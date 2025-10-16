import json
import pytest
from pages.mailbox_sync_home_page import MailboxSyncHomePage
from pages.custom_email_II_page import CustomEmailPage
from pages.immi_home_page import ImmigrationHomePage

with open("data/web_form_values.json") as f:
    case_details = json.load(f)


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
def test_tc06_us1(select_list_view: MailboxSyncHomePage):
    record_types = select_list_view.open_first_n_records(n=2)
    for value in record_types:
        assert value != "GVD - US Outbound"
