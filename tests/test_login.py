import allure
from playwright.sync_api import expect, Page
from pages.login_page import LoginPage
from utils import config
from pages.salesforce_home_page import SalesforceHomePage


def verify_Home_page(sf_home: SalesforceHomePage):
    sf_home.assert_on_home()
