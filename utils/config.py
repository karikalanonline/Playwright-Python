import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("base_url")
USERNAME = os.getenv("sf_user")
PASSWORD = os.getenv("sf_password")
