import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
ADMINS = [
    int(admin_chat_id) for admin_chat_id in str(os.getenv("ADMINS")).split(",")
]
SQLALCHEMY_DATABASE_URL = str(os.getenv("DATABASE_URL"))

PAYMENTS_PROVIDER_TOKEN = str(os.getenv("PAYMENTS_PROVIDER_TOKEN"))
PAYMENTS_IMAGE_URL = "https://img.freepik.com/premium-vector/online-payment-concept_118813-2685.jpg"

MAX_FREE_CHANNELS = 3

I18N_DOMAIN = "easypostbot"
BASE_DIR = Path(__file__).parent.parent
LOCALES_DIR = BASE_DIR / "locales"

DEFAULT_LANGUAGE_CODE = "en"
DEFAULT_TIMEZONE = "Europe/Kiev"
