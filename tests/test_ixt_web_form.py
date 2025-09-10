# import pytest, json
# from pages.salesforce_home_page import SalesforceHomePage
# from pages.mailbox_sync_home_page import MailboxSyncRecordPage
# from pages.custom_email_II_page import CustomEmailPage

# with open("data/case_details.json") as f:
#     case_details = json.load(f)


# # 1st Test case
# # @pytest.mark.submitForm
# # def test_submit_webform(inquiry_number):
# #     # Form is filled inside fixture (fill_form is called there)
# #     # Test stays clear about the purpose
# #     assert inquiry_number is not None


# # @pytest.mark.verifyEmail
# # def test_verify_case_details(ixt_mailbox_business: MailboxSyncRecordPage):
# #     ixt_mailbox_business.assert_case_details()


# @pytest.mark.parametrize("expected", [case_details["TC-5788780"]])
# def test_verify_case_details(
#     mailbox_record_page_business: MailboxSyncRecordPage, expected
# ):
#     mailbox_record_page_business.assert_case_details(expected)
#     custom_email_page = mailbox_record_page_business.click_email_link()
#     custom_email_page.assert_email_status(expected="Sent")

# tests/test_ixt_web_form.py
import json
import pytest
from pages.mailbox_sync_record_page import MailboxSyncRecordPage
from pages.custom_email_II_page import CustomEmailPage

with open("data/case_details.json") as f:
    case_details = json.load(f)


@pytest.mark.parametrize("expected", [case_details["TC-5788780"]])
def test_verify_case_details(
    mailbox_record_page_business: MailboxSyncRecordPage, expected
):
    mailbox_record_page_business.assert_case_details(expected)
    custom_email_page = mailbox_record_page_business.click_email_link()
    custom_email_page.assert_email_status(expected="Sent")
