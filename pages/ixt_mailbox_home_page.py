from playwright.sync_api import Page, expect
from base.base_page import BasePage
from pages.salesforce_home_page import SalesforceHomePage
from pages.ixt_webform_home_page import IxtWebFormHomePage
from pages.mailbox_sync_home_page import MailboxSyncHomePage
from utils.logger import logger


class IxtMailboxApp(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.sf_home = SalesforceHomePage(page)
        self.ixt_mailbox_webform = (
            "p[class='slds-truncate']:has-text('IXT Mailbox WebForm')"
        )
        #self.mailbox_sync_tab = "a[title='Immigration Mailbox Sync']"

    def search_and_select_ixt_webform(self):
        logger.info("Searching the IXT WebForm via app launcher")
        self.click_app_launcher()
        self.page.get_by_label("Search apps and items...").fill("IXT Mailbox WebForm")
        self.page.wait_for_selector(self.ixt_mailbox_webform)
        self.click_and_wait_navi(self.ixt_mailbox_webform)
        return IxtWebFormHomePage(self.page)

    # def click_mailbox_sync_tab(self):
    #     self.click_element(self.mailbox_sync_tab)
    #     return MailboxSyncHomePage(self.page)
