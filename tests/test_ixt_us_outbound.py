import json
import pytest
from pages.mailbox_sync_record_page import MailboxSyncRecordPage
from pages.custom_email_II_page import CustomEmailPage

with open("data/web_form_values.json") as f:
    case_details = json.load(f)


# @pytest.mark.dependency(name="submit form")
# def test_submit_webform(get_inquiry_number):
#     assert get_inquiry_number is not None


# @pytest.mark.dependency(depends=["submit form"])
# @pytest.mark.parametrize("expected", [case_details["TC-5788780"]])
# def test_verify_case_details(
#     mailbox_record_page_business: MailboxSyncRecordPage, expected
# ):
#     mailbox_record_page_business.assert_case_details(expected)
#     custom_email_page = mailbox_record_page_business.click_email_link()
#     custom_email_page.assert_email_status(expected="Sent")


def test_default_user_login(proxy_user_login):
    proxy_user_login.click_app_launcher()


###################################
@pytest.mark.parametrize(
    (
        "proxy_user_login",
        "select_list_view",
    ),
    [("non_us_outbound_team_member", "Master Case List")],
    indirect=[
        "proxy_user_login",
        "select_list_view",
    ],
)
def test_tc06_us1(select_list_view):
    print("Test")


###################################################
@pytest.mark.parametrize(
    ("proxy_user_login", "select_list_view"),
    [("IXT Business Test User 1", "General Inquiries")],
    indirect=["proxy_user_login", "select_list_view"],
)
def test_tc01_us4(select_list_view):
    print("Test")
