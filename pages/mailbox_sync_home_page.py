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
        self.picklist_icon = (
            "button[title ='Select a List View: Immigration Mailbox Sync']"
        )
        self.search_box = "input[role ='combobox']"
        self.img_request_number = "th[data-label='IMG Request Number']"
        # self.record_type_value = "div.slds-form-element:has(span.test-id__field-label:has-text('Record Type')) div.recordTypeName span"
        self.record_type = (
            "div div div span[class='test-id__field-label']:has-text('Record Type')"
        )

    def select_ixt_record(self, inquiry_number: str):
        inquiry_number = self.page.locator(f"a[title='{inquiry_number}'")
        with self.page.expect_navigation():
            self.click_element(inquiry_number)
        return MailboxSyncRecordPage(self.page)

    def go_to_list_view(self, list_view_name: str):
        self.click_element(self.picklist_icon)
        self.click_element(self.search_box)
        # self.fill(self.search_box, list_view_name)
        self.type(self.search_box, list_view_name)
        list_view = self.page.locator(
            f"div.slds-listbox lightning-base-combobox-formatted-text:has-text('{list_view_name}')"
        )
        self.click_element(list_view)

    def assert_list_view_loaded(self, list_view_name: str, timeout: int = 10_000):
        header = self.page.locator(
            f"span.slds-page-header__title:has-text('{list_view_name}')"
        )
        expect(header).to_be_visible(timeout=timeout)

    def open_ixt_record_business(self, record_id: str, timeout: int = 30_000):
        # 1) Open global search
        # self.page.wait_for_timeout(3000)
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

    def open_first_n_records(self, n=2):
        records = self.page.locator(self.img_request_number)
        count = records.count()
        print(f"Total record count is {count}")
        record_types = []

        for i in range(min(n, count)):
            record_link = records.nth(i)
            record_link.click()
            self.page.wait_for_load_state("networkidle")
            self.page.locator(self.record_type).scroll_into_view_if_needed()
            value = self.get_field_value("Record Type")
            print(f"The field value is {value}")
            record_types.append(value)
            self.page.go_back()
            self.page.wait_for_load_state("networkidle")
        return record_types
