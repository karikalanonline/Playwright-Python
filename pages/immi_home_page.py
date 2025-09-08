from playwright.sync_api import expect, Page
from utils.logger import logger
from base.base_page import BasePage
import types, inspect, inspect as _inspect
from pages.immigration_record_page import ImmigrationRecordPage


class ImmigrationHomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def click_immigration_record(
        self, record_id: str = "I-23357", timeout: int = 30_000
    ):
        # print("DEBUG page type:", type(self.page))
        # print("DEBUG get_by_role attr:", self.page.get_by_role)
        # print(
        #     "DEBUG is bound method?:",
        #     isinstance(self.page.get_by_role, types.MethodType),
        # )
        # print("DEBUG comes from module:", _inspect.getmodule(self.page.get_by_role))
        link = self.page.locator(f"role=link[name='{record_id}']").first
        expect(link).to_be_visible(timeout=timeout)
        with self.page.expect_navigation():
            link.click()
        return ImmigrationRecordPage(self.page)
