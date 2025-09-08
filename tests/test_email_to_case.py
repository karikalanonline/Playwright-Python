# tests/test_email_to_case.py
from utils.send_email import send_email_to_salesforce
from utils.gmail_inbox import wait_for_email_with_token
import re


def test_email_to_case_reply():
    token = send_email_to_salesforce()
    reply = wait_for_email_with_token(token, timeout_sec=300, poll_sec=10)

    print("Reply Subject:", reply["subject"])
    print("Reply Body (first 300 chars):", reply["body"][:300])

    # Example assertion: make sure the inquiry/case id shows up (adjust regex to your format)
    # Your screenshot shows like IXT-00000444
    assert re.search(
        r"\bIXT-\d{8}\b", reply["subject"] + " " + reply["body"]
    ), "Inquiry/Case ID not found in the reply"
