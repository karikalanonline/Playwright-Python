from playwright.sync_api import expect, Page
from utils.logger import logger
from base.base_page import BasePage
import types, inspect, inspect as _inspect
from pages.immigration_record_page import ImmigrationRecordPage


class ImmigrationHomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.immigration_name = "th[data-label='Immigration Name']"

    # def click_immigration_record(
    #     self, record_id: str = "I-23357", timeout: int = 30_000
    # ):
    #     link = self.page.locator(f"role=link[name='{record_id}']").first
    #     expect(link).to_be_visible(timeout=timeout)
    #     with self.page.expect_navigation():
    #         link.click()
    #     return ImmigrationRecordPage(self.page)

    def click_immigration_record(self):
        single = self.page.locator(self.immigration_name).first
        expect(single).to_be_visible(timeout=5000)
        single.click()
        return ImmigrationRecordPage(self.page)
