import json
import pytest
from pages.mailbox_sync_home_page import MailboxSyncHomePage

with open("data/common_data.json") as f:
    common_data = json.load(f)


@pytest.mark.parametrize(
    "select_list_view", ["US Outbound - Open cases"], indirect=True
)
def test_select_us_outbound(select_list_view: MailboxSyncHomePage):
    mailbox_sync_home_page = select_list_view
    mailbox_sync_home_page.assert_list_view_loaded()
