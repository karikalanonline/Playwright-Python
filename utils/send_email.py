# # utils/send_email.py
# import os, uuid, smtplib
# from email.message import EmailMessage
# from dotenv import load_dotenv

# load_dotenv()
# GMAIL_USER = os.getenv("GMAIL_USER")
# GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# TO_ADDRESS = os.getenv("TO_ADDRESS")


# def send_email_to_salesforce() -> str:
#     """Sends an email to Email-to-Case and returns a unique token placed in the subject/body."""
#     assert GMAIL_USER and GMAIL_APP_PASSWORD and TO_ADDRESS, "Set .env values"

#     token = str(uuid.uuid4())[:8]  # short unique id
#     subject = f"[Test] Email-to-Case trigger ({token})"
#     body = f"""Hello Support,

# This is an automated test email.
# Token: {token}

# Thanks,
# QA Automation
# """

#     msg = EmailMessage()
#     msg["From"] = f"Practitioner <{GMAIL_USER}>"
#     msg["To"] = TO_ADDRESS
#     msg["Subject"] = subject
#     msg.set_content(body)

#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#         smtp.starttls()
#         smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
#         smtp.send_message(msg)

#     return token


# if __name__ == "__main__":
#     t = send_email_to_salesforce()
#     print("Sent. Token:", t)

# send_email_smtp_ssl.py
import os, uuid, smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_ADDRESS = os.getenv("TO_ADDRESS")


def send_email_to_salesforce() -> str:
    assert GMAIL_USER and GMAIL_APP_PASSWORD and TO_ADDRESS, "Set .env values"

    token = str(uuid.uuid4())[:8]
    subject = f"[Test] Email-to-Case trigger ({token})"
    body = f"Token: {token}\nThis is test email."

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = TO_ADDRESS
    msg["Subject"] = subject
    msg.set_content(body)

    # SMTP_SSL — no starttls()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    return token
