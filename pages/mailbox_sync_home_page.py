from playwright.sync_api import Page, expect
from base.base_page import BasePage
from pages.mailbox_sync_record_page import MailboxSyncRecordPage


class MailboxSyncHomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.global_search_button = "button[aria-label='Search']"
        self.global_search_input = (
            "input.slds-input[placeholder='Search...'][type='search']"
        )
        self.list_search = "input.slds-input[placeholder='Search...'][type='search']"

    def select_ixt_record(self, inquiry_number: str):
        inquiry_number = self.page.locator(f"a[title='{inquiry_number}'")
        with self.page.expect_navigation():
            self.click_element(inquiry_number)
        return MailboxSyncRecordPage(self.page)

    # def open_ixt_record_business(self, record_id: str, timeout=30_000):
    #     expect(self.page.locator(self.global_search_button)).to_be_visible()
    #     self.page.locator(self.global_search_button).click()
    #     global_search = self.page.locator(self.global_search_button).first
    #     global_search.type(record_id, delay=90)
    #     self.page.locator(f"mark[class='data-match']:has-text('{record_id}')").click()
    #     return MailboxSyncRecordPage(self.page)

    def open_ixt_record_business(self, record_id: str, timeout: int = 30_000):
        # 1) Open global search
        btn = self.page.locator(self.global_search_button)
        expect(btn).to_be_visible()
        btn.click()

        # 2) Focus the global search input
        box = self.page.locator(self.global_search_input).first
        expect(box).to_be_visible()
        box.click()
        box.fill("")  # clear any residue
        box.type(record_id, delay=60)
        with self.page.expect_navigation():
            self.page.locator(
                f"mark[class='data-match']:has-text('{record_id}')"
            ).click()
        self.page.wait_for_timeout(5000)
        return MailboxSyncRecordPage(self.page)
