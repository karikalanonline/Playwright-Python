from base.base_page import BasePage
from utils.logger import logger
from pages.salesforce_home_page import SalesforceHomePage
from playwright.async_api import Page


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.user_name_input = "#username"
        self.password_input = "#password"
        self.login_button = "#Login"

    def login(self, username, password):
        logger.info("Login to the application with valid username and password")
        self.fill(self.user_name_input, username)
        self.fill(self.password_input, password)
        with self.page.expect_navigation():
            self.click_element(self.login_button)
        # self.page.wait_for_load_state("load")
        return SalesforceHomePage(self.page)
