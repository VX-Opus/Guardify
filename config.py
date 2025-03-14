import os
import logging
from telethon import TelegramClient
from os import getenv
from strings.helpers import DEV
from dotenv import load_dotenv

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

BOT_TOKEN = getenv("BOT_TOKEN", default=None)
API_ID = 18136872
API_HASH = "312d861b78efcd1b02183b2ab52a83a4"
SUDO_USERS.append(OWNER_ID)
SPOILER_MODE = os.environ.get("SPOILER_MODE", "True").lower() == "true"
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = ""
SUDO_ID = [6257927828]
LOGGER = False
BOT_NAME = "Guardify"
SUPPORT_ID = -1002064111110
SUDO_USERS = list(map(lambda x: int(x), getenv("SUDO_USERS", default="6257927828").split()))
for x in DEV:
    SUDO_USERS.append(x)
OWNER_ID = int(getenv("OWNER_ID", default="6257927828"))
BOT = TelegramClient('ꜱ ᴛ ᴏ ʀ ᴍ', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
