import pytest
from playwright.sync_api import expect, Page

# from conftest import immigration_record_data
from utils import config
from data import test_data
from data import test_data
from utils import report_helper
from pages.immi_home_page import ImmigrationHomePage


# @pytest.mark.e2e
def test_e2e_flow(immigration_home: ImmigrationHomePage, immigration_record_data):
    with immigration_home.page.expect_navigation():
        immi_record_page = immigration_home.click_immigration_record()
        actual_cap_value = immi_record_page.get_cap_nominee_value()
        expected_cap_value = immigration_record_data["immigration_cap_nominee_value"]
        assert (
            actual_cap_value.lower() == expected_cap_value.lower()
        ), f"Expected {expected_cap_value}, got {actual_cap_value}"
