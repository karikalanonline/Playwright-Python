from base.base_page import BasePage
from playwright.sync_api import Page, expect, TimeoutError as PWTimeoutError
from utils.logger import logger
from pages.immi_home_page import ImmigrationHomePage
from pages.salesforce_admin_page import SalesforceAdminPage
from pages.mailbox_sync_home_page import MailboxSyncHomePage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pages.ixt_mailbox_home_page import IxtMailboxApp


class SalesforceHomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.spinner = ".slds-spinner:not([hidden])"
        self.home_tab = "a[title='Home']"
        self.accountTab = "a[href='/lightning/o/Account/home'] span.slds-truncate:has_text('Accounts')"
        self.switch_to_lightning_link = (
            "div.navLinks div.linkElements a.switch-to-lightning"
        )
        self.immigration = ":text-is('Immigration')"
        self.ixt_mailbox_app = "p[class='slds-truncate']:has-text('IXT Mailbox App')"
        self.gear_icon = "div.setupGear"
        self.setup_option = "#related_setup_app_home"

    def switch_to_lightning(self):
        logger.info("Attempting to switch to Lightning...")

        try:
            link = self.page.locator(self.switch_to_lightning_link).first
            link.wait_for(state="visible", timeout=5000)
            print("Found the lightning link, clicking")
            with self.page.expect_navigation():
                link.click()
        except PWTimeoutError:
            logger.info("Already in Lightning")

    def search_immigration(self):
        logger.info("Searching for the immigration module")
        self.page.get_by_label("Search apps and items...").fill("Immigration")
        self.page.wait_for_selector(self.immigration)

    def search_and_select_ixt_mailbox_app(self):
        logger.info("Searching the IXT Mailbox APP via app launcher")
        self.page.get_by_label("Search apps and items...").fill("IXT Mailbox App")
        self.page.wait_for_selector(self.ixt_mailbox_app)
        self.click_and_wait_navi(self.ixt_mailbox_app)
        from pages.ixt_mailbox_home_page import IxtMailboxApp

        return IxtMailboxApp(self.page)

    def click_immigration(self):
        logger.info("Selecting the immigration module")
        self.click_element(self.immigration)
        self.page.wait_for_load_state("domcontentloaded")
        return ImmigrationHomePage(self.page)

    def assert_on_home(self):
        expect(self.page.locator(self.home_tab)).to_be_visible()

    def go_to_admin_page(self):
        self.click_element(self.gear_icon)
        with self.page.context.expect_page() as new_page_info:
            self.click_element(self.setup_option)
        setup_page = new_page_info.value
        return SalesforceAdminPage(setup_page)
