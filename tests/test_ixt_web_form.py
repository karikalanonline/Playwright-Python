import pytest, json
from playwright.sync_api import expect
from utils import config
from data import test_data
from utils import report_helper
from pages.salesforce_home_page import SalesforceHomePage
from pages.mailbox_sync_home_page import MailboxSyncRecordPage

with open("data/case_details.json") as f:
    case_details = json.load(f)


# 1st Test case
# @pytest.mark.submitForm
# def test_submit_webform(inquiry_number):
#     # Form is filled inside fixture (fill_form is called there)
#     # Test stays clear about the purpose
#     assert inquiry_number is not None


# @pytest.mark.verifyEmail
# def test_verify_case_details(ixt_mailbox_business: MailboxSyncRecordPage):
#     ixt_mailbox_business.assert_case_details()


@pytest.mark.parametrize("expected", [case_details["TC-5788780"]])
def test_verify_case_details(ixt_mailbox_business: MailboxSyncRecordPage, expected):
    ixt_mailbox_business.assert_case_details(expected)
