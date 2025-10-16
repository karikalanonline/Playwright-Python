import allure
from playwright.sync_api import expect, Page
from pages.login_page import LoginPage
from utils import config
from pages.salesforce_home_page import SalesforceHomePage


def test_verify_Home_page(sf_home_page: SalesforceHomePage):
    sf_home_page.assert_on_home_tab()
