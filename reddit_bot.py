from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import cohere
import os
from datetime import datetime

class RedditBot:
    def __init__(self):
        options = UiAutomator2Options()
        options.platform_name = 'Android'
        options.device_name = '7d3f31f1'
        options.app_package = 'com.reddit.frontpage'
        options.app_activity = 'com.reddit.launch.main.MainActivity'
        options.automation_name = 'uiautomator2'
        options.no_reset = True

        self.driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        self.wait = WebDriverWait(self.driver, 30)
        self.co = cohere.Client('2AQBVeglB3wITOLph3fRjIrkpkkHpZBlo2lT6Xjw')
        
        self.debug_dir = 'debug_logs'
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)

    def take_screenshot(self, name):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.debug_dir}/{name}_{timestamp}.png"
            self.driver.get_screenshot_as_file(filename)
            print(f"Screenshot saved: {filename}")
        except Exception as e:
            print(f"Failed to take screenshot: {e}")

    def save_page_source(self, name):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.debug_dir}/{name}_{timestamp}.xml"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"Page source saved: {filename}")
        except Exception as e:
            print(f"Failed to save page source: {e}")

    def wait_for_element(self, locator, timeout=30, retries=3):
        for i in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
            except Exception as e:
                if i == retries - 1:
                    print(f"Element not found after {retries} attempts: {e}")
                    self.take_screenshot('element_not_found')
                    return None
                time.sleep(2)

    def safe_click(self, element, retries=3):
        for i in range(retries):
            try:
                if element and element.is_displayed() and element.is_enabled():
                    element.click()
                    time.sleep(2)
                    return True
            except:
                if i == retries - 1:
                    self.take_screenshot('click_failed')
                    return False
                time.sleep(2)
        return False

    def scroll_down(self):
        try:
            screen_size = self.driver.get_window_size()
            start_y = screen_size['height'] * 0.8
            end_y = screen_size['height'] * 0.2
            start_x = screen_size['width'] * 0.5
            
            self.driver.swipe(start_x, start_y, start_x, end_y, 1000)
            time.sleep(2)
        except Exception as e:
            print(f"Scroll failed: {e}")

    def upvote_post(self):
        try:
            time.sleep(5)
            upvote_button = self.wait_for_element(
                (AppiumBy.XPATH, '//android.view.View[@resource-id="post_footer"]/android.view.View[1]')
            )
            if self.safe_click(upvote_button):
                print("Successfully upvoted the post")
                time.sleep(2)
        except Exception as e:
            print(f"Error while upvoting: {e}")
            self.take_screenshot('upvote_error')

    def comment_on_post(self):
        try:
            time.sleep(5)
            print("Starting comment process...")
            
            # Click comment button with retries
            comment_locators = [
                (AppiumBy.XPATH, '//android.view.View[@resource-id="comment_button"]/android.view.View/android.widget.Button'),
                (AppiumBy.XPATH, '//android.widget.LinearLayout[@resource-id="com.reddit.frontpage:id/reply"]/android.view.ViewGroup'),
                (AppiumBy.XPATH, '//android.view.View[contains(@content-desc, "Comment")]'),
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Comment")')
            ]
            
            comment_button = None
            for locator in comment_locators:
                print(f"Trying to find comment button with: {locator}")
                comment_button = self.wait_for_element(locator)
                if comment_button:
                    print(f"Found comment button using: {locator}")
                    break

            if self.safe_click(comment_button):
                print("Clicked comment button")
                time.sleep(5)
                
                # Find reply field with multiple attempts
                reply_locators = [
                    (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.reddit.frontpage:id/reply_text"]'),
                    (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="text_message_input"]'),
                    (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="comment_field"]'),
                    (AppiumBy.XPATH, '//android.widget.ScrollView/android.widget.LinearLayout/android.widget.EditText'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")'),
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Add a comment")')
                ]

                reply_field = None
                for locator in reply_locators:
                    print(f"Trying to find reply field with: {locator}")
                    reply_field = self.wait_for_element(locator)
                    if reply_field:
                        print(f"Found reply field using: {locator}")
                        break
                        
                if not reply_field:
                    print("Reply field not found, attempting to scroll...")
                    self.scroll_down()
                    time.sleep(2)
                    
                    for locator in reply_locators:
                        reply_field = self.wait_for_element(locator)
                        if reply_field:
                            print(f"Found reply field after scrolling using: {locator}")
                            break

                if reply_field:
                    if self.safe_click(reply_field):
                        time.sleep(2)
                        # Re-locate element before sending keys
                        reply_field = self.wait_for_element(
                            (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.reddit.frontpage:id/reply_text"]')
                        )
                        if reply_field:
                            reply_field.send_keys("This is an interesting post!")
                            print("Entered comment text")
                            time.sleep(2)

                            # Updated post button locators and handling
                            post_locators = [
                                (AppiumBy.XPATH, '//android.widget.Button[@resource-id="com.reddit.frontpage:id/menu_item_text"]'),
                                (AppiumBy.XPATH, '//android.widget.Button[contains(@text, "Post")]'),
                                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Post")'),
                                (AppiumBy.XPATH, '//android.widget.Button[@text="Post"]'),
                                (AppiumBy.XPATH, '//android.widget.Button[contains(@resource-id, "post_button")]')
                            ]

                            # Try multiple times to find and click post button
                            for _ in range(3):
                                for locator in post_locators:
                                    try:
                                        print(f"Trying to find post button with: {locator}")
                                        post_button = self.wait.until(EC.element_to_be_clickable(locator))
                                        if post_button and post_button.is_displayed():
                                            post_button.click()
                                            print("Successfully clicked post button")
                                            return
                                    except:
                                        continue
                                time.sleep(2)
                            
                            print("Failed to find clickable post button")
                            self.take_screenshot('post_button_not_found')
                        else:
                            print("Failed to re-locate reply field")
                    else:
                        print("Failed to click reply field")
                else:
                    print("Reply field not found even after scrolling")
            else:
                print("Failed to click comment button")
                
        except Exception as e:
            print(f"Error posting comment: {e}")
            self.take_screenshot('comment_error')
            self.save_page_source('comment_error')

def main():
    bot = None
    try:
        bot = RedditBot()
        bot.upvote_post()
        time.sleep(5)
        bot.comment_on_post()
    except Exception as e:
        print(f"Main error occurred: {e}")
    finally:
        if bot:
            bot.driver.quit()

if __name__ == "__main__":
    main()
