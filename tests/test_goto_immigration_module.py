from playwright.sync_api import expect, Page
from pages.login_page import LoginPage
from utils import config
from data import test_data
import re


def test_goto_immigration_module(page: Page):
    loginPage = LoginPage(page)
    loginPage.navigate_to(config.BASE_URL)
    salesforce_home_page = loginPage.login(config.USERNAME, config.PASSWORD)
    salesforce_home_page.switch_to_lightning()
    salesforce_home_page.click_app_launcher()
    salesforce_home_page.search_immigration()
    salesforce_home_page.click_immigration()
    expected_url = test_data.immigration_home_url
    expect(page).to_have_url(re.compile(rf"^{re.escape(expected_url)}"))
