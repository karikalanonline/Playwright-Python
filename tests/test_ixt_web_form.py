import json
import pytest
from pages.mailbox_sync_record_page import MailboxSyncRecordPage
from pages.custom_email_II_page import CustomEmailPage

with open("data/case_details.json") as f:
    case_details = json.load(f)


# 1st Test case
@pytest.mark.dependency(name="submit form")
def test_submit_webform(inquiry_number):
    assert inquiry_number is not None


@pytest.mark.dependency(depends=["submit form"])
@pytest.mark.parametrize("expected", [case_details["TC-5788780"]])
def test_verify_case_details(
    mailbox_record_page_business: MailboxSyncRecordPage, expected
):
    mailbox_record_page_business.assert_case_details(expected)
    custom_email_page = mailbox_record_page_business.click_email_link()
    custom_email_page.assert_email_status(expected="Sent")
