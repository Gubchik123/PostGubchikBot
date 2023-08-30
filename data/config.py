import os

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
ADMINS = [
    int(admin_chat_id) for admin_chat_id in str(os.getenv("ADMINS")).split(",")
]
SQLALCHEMY_DATABASE_URL = str(os.getenv("DATABASE_URL"))
