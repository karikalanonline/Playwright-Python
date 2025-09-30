import json
import pytest
from pages.mailbox_sync_home_page import MailboxSyncHomePage

with open("data/common_data.json") as f:
    common_data = json.load(f)


@pytest.mark.parametrize(
    "select_list_view", ["US Outbound - Open cases"], indirect=True
)
def test_select_us_outbound(select_list_view):
    mailbox_sync_home_page = select_list_view
    mailbox_sync_home_page


def test_select_us_outbound(select_list_view, common_data):
    page = select_list_view("US Outbound - Open cases")
    page.assert_list_view_loaded(
        common_data["list_view_name"]["US Outbound - Open cases"]
    )


# @pytest.mark.parametrize("Key_or_value", ["All", "US Outbound - Open cases"])
# def test_list_view_all(select_list_view_factory, Key_or_value):
#     select_list_view_factory(Key_or_value)
