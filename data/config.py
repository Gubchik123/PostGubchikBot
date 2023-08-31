import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
ADMINS = [
    int(admin_chat_id) for admin_chat_id in str(os.getenv("ADMINS")).split(",")
]
SQLALCHEMY_DATABASE_URL = str(os.getenv("DATABASE_URL"))

I18N_DOMAIN = "easypostbot"
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locales"

DEFAULT_LANGUAGE_CODE = "en"
DEFAULT_TIMEZONE = "Europe/Kiev"

PAYMENT_SITE_URL = "https://example.com/transfer/quickpay/"
