import os
from dotenv import load_dotenv

load_dotenv()

# Salesforce
BASE_URL = os.getenv("base_url")
USERNAME = os.getenv("sf_user")
PASSWORD = os.getenv("sf_password")

# Gmail
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_ADDRESS = os.getenv("TO_ADDRESS")
