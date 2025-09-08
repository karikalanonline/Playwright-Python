import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("base_url")
USERNAME = os.getenv("user")
PASSWORD = os.getenv("password")
