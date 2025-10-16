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

    def get_field_value(self, label: str, timeout: int = 10_000) -> str:
        """
        Given a visible field label (e.g. 'Record Type'), return the displayed value text.
        Works for:
          - standard static fields inside span.test-id__field-value
          - record type rendered inside div.recordTypeName > span
          - fields rendered inside slots/other nested LWC components

        Raises:
          TimeoutError if label not found within timeout or value cannot be located.
        """
        # 1) locate the label (anchor)
        label_locator = self.page.locator(
            "span.test-id__field-label", has_text=label
        ).first
        try:
            label_locator.wait_for(state="visible", timeout=timeout)
        except TimeoutError:
            raise TimeoutError(
                f"Label '{label}' not found or not visible within {timeout}ms"
            )

        # 2) get the nearest slds-form-element (ancestor) container
        # use xpath to climb up to the form element
        container = label_locator.locator(
            "xpath=ancestor::div[contains(@class,'slds-form-element')]"
        ).first

        # 3) Try multiple candidate locators for the value (order matters)
        candidates = [
            "span.test-id__field-value",  # normal static value
            "div.recordTypeName span",  # Record Type special renderer
            ".//slot[@name='outputField']//div//span",  # nested inside slot -> records-record-type -> div -> span
            ".//span[contains(@class,'test-id__field-value')]//span",  # nested span inside the value container
            ".//span[normalize-space() and string-length(normalize-space(.))>0]",  # any non-empty span fallback
        ]

        for sel in candidates:
            # if selector starts with xpath-like prefix, pass as xpath by using locator("xpath=...")
            if sel.startswith(".//") or sel.startswith("//"):
                value_loc = container.locator(f"xpath={sel}")
            else:
                # prefer css selector
                value_loc = container.locator(sel)

            try:
                # wait short time for the candidate to appear - some components render slower
                value_loc.wait_for(state="attached", timeout=1200)
            except Exception:
                # candidate not attached quickly — continue to next
                continue

            # get first non-empty match
            count = value_loc.count()
            if count == 0:
                continue

            # iterate matches and return first non-empty inner_text
            for i in range(count):
                text = value_loc.nth(i).inner_text().strip()
                if text:
                    # self._log(
                    #     f"Found value for '{label}' using selector '{sel}': {text}"
                    # )
                    return text

        # if we reach here, none of the candidates returned text
        raise Exception(f"Unable to find value for label '{label}' — DOM may differ.")
