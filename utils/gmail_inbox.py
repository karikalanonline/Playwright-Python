# utils/gmail_inbox.py
import os, time, imaplib, email, re
from email.header import decode_header, make_header
from dotenv import load_dotenv

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def _decode(s):
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s


def _get_body(msg):
    # prefer text/plain; fall back to text/html (strip tags lightly)
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode(errors="ignore")
                return re.sub("<[^>]+>", " ", html)
        return ""
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")


def wait_for_email_with_token(token: str, timeout_sec: int = 300, poll_sec: int = 10):
    """Poll Gmail INBOX for an email whose Subject or Body contains the token.
    Returns dict(subject=..., body=...) if found, else raises TimeoutError."""
    assert (
        GMAIL_USER and GMAIL_APP_PASSWORD
    ), "Set GMAIL_USER and GMAIL_APP_PASSWORD in .env"

    deadline = time.time() + timeout_sec
    with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
        imap.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        # search only INBOX; if your reply lands elsewhere, change to "[Gmail]/All Mail"
        imap.select("INBOX")

        while time.time() < deadline:
            # Search by SUBJECT token first (fast). If not found, we’ll do a broader search.
            status, ids = imap.search(None, "SUBJECT", f'"{token}"')
            if status == "OK" and ids[0]:
                id_list = ids[0].split()
                latest_id = id_list[-1]
                _, data = imap.fetch(latest_id, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                subject = _decode(msg.get("Subject"))
                body = _get_body(msg)
                return {"subject": subject, "body": body}

            # Fallback: search in all new messages and check body
            status, ids = imap.search(None, "UNSEEN")
            if status == "OK" and ids[0]:
                for mid in ids[0].split():
                    _, data = imap.fetch(mid, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    subject = _decode(msg.get("Subject"))
                    body = _get_body(msg)
                    if token in subject or token in body:
                        return {"subject": subject, "body": body}

            time.sleep(poll_sec)

    raise TimeoutError(f"No email with token '{token}' within {timeout_sec}s")
