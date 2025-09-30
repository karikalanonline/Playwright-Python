import time, logging
from playwright.sync_api import Page, expect, Locator
from utils.logger import logger
from datetime import date, datetime

# from pages.login_page import LoginPage


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.app_launcher_icon = "button[title='App Launcher']"

    def retry_action(self, action_Fn, retries=1, delay=1):
        for attempt in range(retries + 1):
            try:
                return action_Fn()
            except Exception as e:
                logger.warning(
                    f"Retry failed after {attempt +1} attempts. Error{str(e)}"
                )
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise

    def navigate_to(self, url: str):
        logger.info(f"Navigate to the {url}")
        self.page.goto(url)
        # self.page.set_viewport_size({"width": 1920, "height": 1080})
        ##return LoginPage(self.page)

    def click_element(self, target, *, timeout: int = 30_000):
        if isinstance(target, str):
            locator = self.page.locator(target).first

        elif isinstance(target, Locator):
            locator = target.first

        else:
            raise TypeError(
                f"click_element expected str or Locator, got {type(target)}"
            )
        expect(locator).to_be_visible()
        self.retry_action(lambda: locator.click())

    # def fill(self, selector: str, value):
    #     if isinstance(value, (date, datetime)):
    #         value = value.strftime("%Y-%m-%d")
    #     self.page.fill(selector, str(value))

    def fill(self, selector: str, value):
        if isinstance(value, (date, datetime)):
            value = value.strftime("%Y-%m-%d")
        self.retry_action(lambda: self.page.locator(selector).fill(value))

    def type(self, selector: str, value):
        if isinstance(value, (date, datetime)):
            value.strftime("%Y-%m-%d")
        self.retry_action(lambda: self.page.locator(selector).type(value, delay=200))

    def get_text(self, selector: str) -> str:
        logger.info(f"Getting the text from the element: {selector}")
        return self.page.text_content(selector)

    def wait_for_element(self, selector: str, timeout: int = 5000):
        logger.info(f"Waiting for the element: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)

    def assert_element_visible(self, selector: str) -> bool:
        logger.info(f"Asserting the visibility of the element: {selector}")
        element = self.page.locator(selector)
        expect(element).to_be_visible()

    def assert_text_content(self, selector: str, expected_string: str) -> bool:
        logger.info(f"Asserting the text content of the element: {selector}")
        element = self.page.locator(selector)
        expect(element).to_be_equal(expected_string)

    def click_and_wait_navi(self, selector: str, *, timeout=30_000):
        locator = self.page.locator(selector).first
        with self.page.expect_navigation(timeout=timeout):
            locator.click()

    def click_app_launcher(self):
        logger.info("Clicking the app launcher icon")
        expect(self.page.locator(self.app_launcher_icon)).to_be_visible(timeout=8000)
        self.page.locator(self.app_launcher_icon).click()

    # def click_app_launcher(self):
    #     # debug print is optional but helpful during verification
    #     try:
    #         print(
    #             "DEBUG: clicking app launcher on page id",
    #             id(self.page),
    #             "url",
    #             self.page.url,
    #         )
    #     except Exception:
    #         pass

    #     # use the exact selector your app needs
    #     self.page.locator(
    #         "button[aria-label='App Launcher'], button[title='App Launcher']"
    #     ).click()

    # optionally wait for the launcher modal / grid to appear
    # self.page.locator("div[role='dialog'] >> text=All Apps").wait_for(state="visible", timeout=8000)
