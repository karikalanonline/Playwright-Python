import pytest
from playwright.sync_api import expect, Page

# from conftest import immigration_record_data
from utils import config
from data import test_data
from data import test_data
from utils import report_helper
from pages.immi_home_page import ImmigrationHomePage


# @pytest.mark.e2e
# def test_end_to_end_flow(page: Page):
#     loginPage = LoginPage(page)
#     loginPage.navigate_to(config.BASE_URL)
#     salesforce_home_page = loginPage.login(config.USERNAME, config.PASSWORD)
#     salesforce_home_page.switch_to_lightning()
#     salesforce_home_page.click_app_launcher()
#     salesforce_home_page.search_immigration()
#     immigration_home_page = salesforce_home_page.click_immigration()
#     expected_url = test_data.immigration_home_url
#     expect(page).to_have_url(re.compile(rf"^{re.escape(expected_url)}"))

#     with page.expect_navigation():
#         immigration_record_page = immigration_home_page.click_immigration_record(
#             test_data.immigration_record_id
#         )
#     _ = immigration_record_page.get_cap_nominee_value()
#     immigration_record_page.verify_cap_nominee_field()


# @pytest.mark.e2e
def test_e2e_flow(immigration_home: ImmigrationHomePage, immigration_record_data):
    with immigration_home.page.expect_navigation():
        immi_record_page = immigration_home.click_immigration_record(
            immigration_record_data["immigration_record_id"]
        )
        actual_cap_value = immi_record_page.get_cap_nominee_value()
        expected_cap_value = immigration_record_data["immigration_cap_nominee_value"]
        assert (
            actual_cap_value.lower() == expected_cap_value.lower()
        ), f"Expected {expected_cap_value}, got {actual_cap_value}"
