from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel, PeerUser
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, OWNER_ID, SUPPORT_ID
from config import BOT
import time
import re
import html
import logging

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# MongoDB initialization
mongo_BOT = MongoClient(MONGO_URI)
db = mongo_BOT[DB_NAME]
users_collection = db['users']
active_groups_collection = db['active_groups']
sudo_users_collection = db['sudo_users']
authorized_users_collection = db['authorized_users']


# Define a list to store sudo user IDs
SUDO_ID = [6257927828]
sudo_users = SUDO_ID.copy()  # Copy initial SUDO_ID list
sudo_users.append(OWNER_ID)  # Add owner to sudo users list initially


# Track groups where the bot is active
@BOT.on(events.NewMessage(func=lambda e: e.is_group))
async def track_groups(event):
    chat = await event.get_chat()
    group_data = {"group_id": chat.id, "group_name": chat.title, "invite_link": "ɴᴏ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴀᴠᴀɪʟᴀʙʟᴇ"}

    if not active_groups_collection.find_one({"group_id": chat.id}):
        active_groups_collection.insert_one(group_data)

# Check for edited messages
@BOT.on(events.MessageEdited)
async def check_edit(event):
    chat = await event.get_chat()
    user = await event.get_sender()
    user_id = user.id
    user_first_name = html.escape(user.first_name)
    user_mention = f"<a href='tg://user?id={user_id}'>{user_first_name}</a>"

    # Check if user is owner, sudo, or authorized in this group
    is_owner = user_id == OWNER_ID
    is_sudo = user_id in sudo_users
    is_authorized = authorized_users_collection.find_one({"user_id": user_id, "group_id": chat.id})

    if is_owner or is_sudo or is_authorized:
        await BOT.send_message(
            SUPPORT_ID,
            f"<blockquote>Aᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ {user_mention} ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇssᴀɢᴇ ɪɴ ᴄʜᴀᴛ <code>{chat.id}</code>.</blockquote>\n"
            "<blockquote><b>Nᴏ ᴀᴄᴛɪᴏɴ ᴡᴀs ᴛᴀᴋᴇɴ.</b></blockquote>",
            parse_mode='html'
        )
        return

    # Try to check if the user is an admin
    try:
        chat_member = await BOT.get_permissions(chat, user)

        if chat_member.is_admin or chat_member.is_creator:
            await BOT.send_message(
                SUPPORT_ID,
                f"<blockquote>Usᴇʀ {user_mention} is an <b>{chat_member.status}</b> ɪɴ ᴄʜᴀᴛ <code>{chat.id}</code>.</blockquote>\n"
                "<blockquote><b>Nᴏ ᴅᴇʟᴇᴛɪᴏɴ ᴡᴀs ᴘᴇʀғᴏʀᴍᴇᴅ.</b></blockquote>",
                parse_mode='html'
            )
            return

    except Exception as e:
        await BOT.send_message(
            SUPPORT_ID,
            f"<blockquote>Bᴏᴛ ɴᴇᴇᴅs ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɪɴ ᴄʜᴀᴛ <code>{chat.id}</code>.</blockquote>\n"
            f"<blockquote><b>Cᴀɴɴᴏᴛ ᴄʜᴇᴄᴋ/ᴅᴇʟ ᴇᴅɪᴛs ғʀᴏᴍ {user_mention}.<b></blockquote>",
            parse_mode='html'
        )
        return

    # Delete the unauthorized user's edited message
    try:
        await event.delete()

        await BOT.send_message(
            chat.id,
            f"<blockquote><b>{user_mention} Jᴜsᴛ ᴇᴅɪᴛᴇᴅ ᴀ ᴍᴇssᴀɢᴇ.<b></blockquote>"
            "<blockquote><b>ɪ ʜᴀᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ɪᴛ.<b></blockquote>",
            parse_mode='html'
        )

        await BOT.send_message(
            SUPPORT_ID,
            f"<blockquote><b>Dᴇʟᴇᴛᴇᴅ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ {user_mention}<b></blockquote>"
            f"<blockquote><b>ɪɴ ᴄʜᴀᴛ <code>{chat.id}</code>.<b></blockquote>",
            parse_mode='html'
        )

    except Exception as e:
        await BOT.send_message(
            SUPPORT_ID,
            f"<blockquote><b>Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ! Mᴀᴋᴇ sᴜʀᴇ ʙᴏᴛ ʜᴀs ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ ᴀɴᴅ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ʀɪɢʜᴛs.<b></blockquote>\n"
            f"<blockquote><b>Mᴇssᴀɢᴇ ID: <code>{event.id}</code> ɪɴ ᴄʜᴀᴛ <code>{chat.id}</code>.<b></blockquote>\n"
            f"<blockquote><b><code>{e}</code><b></blockquote>",
            parse_mode='html'
        )

# Add sudo user
@BOT.on(events.NewMessage(pattern='/addsudo'))
async def add_sudo(event):
    user = await event.get_sender()
    chat = await event.get_chat()

    # Check if the user is the owner
    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ  sᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Check if a username or user ID is provided
    if not event.pattern_match.group(1):
        await event.reply("Usᴀɢᴇ: /addsudo <ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ᴜsᴇʀ Iᴅ>")
        return

    sudo_user = event.pattern_match.group(1).strip()

    # Resolve the user ID from username if provided
    try:
        if sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))

        # Add sudo user ID to the database if not already present
        if sudo_users_collection.find_one({"user_id": sudo_user_id}):
            await event.reply(f"{user_entity.first_name} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ.")
            return

        # Add sudo user to the database
        sudo_users_collection.insert_one({
            "user_id": sudo_user_id,
            "username": user_entity.username,
            "first_name": user_entity.first_name
        })
        await event.reply(f"ᴀᴅᴅᴇᴅ {user_entity.first_name} ᴀs ᴀ sᴜᴅᴏ ᴜsᴇʀ.")
    except Exception as e:
        await event.reply(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ sᴜᴘᴇʀ ᴜsᴇʀ: {e}")

# Remove sudo user
@BOT.on(events.NewMessage(pattern='/rmsudo'))
async def rmsudo(event):
    user = await event.get_sender()
    chat = await event.get_chat()

    # Check if the user is the owner
    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ  sᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Check if a username or user ID is provided
    if not event.pattern_match.group(1):
        await event.reply("Usᴀɢᴇ: /rmsudo <ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ᴜsᴇʀ ɪᴅ>")
        return

    sudo_user = event.pattern_match.group(1).strip()

    try:
        if sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))

        # Remove sudo user from the database
        result = sudo_users_collection.delete_one({"user_id": sudo_user_id})
        if result.deleted_count > 0:
            await event.reply(f"Rᴇᴍᴏᴠᴇᴅ {user_entity.first_name} ᴀs ᴀ sᴜᴅᴏ ᴜsᴇʀ.")
        else:
            await event.reply(f"{user_entity.first_name} ɪs ɴᴏᴛ ᴀ sᴜᴅᴏ ᴜsᴇʀ.")
    except Exception as e:
        await event.reply(f"Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ ᴜsᴇʀ: {e}")

# List sudo users
@BOT.on(events.NewMessage(pattern='/sudolist'))
async def sudo_list(event):
    user = await event.get_sender()

    # Check if the user is the owner
    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Fetch sudo users from MongoDB
    sudo_users_cursor = sudo_users_collection.find({})
    text = "ʟɪsᴛ ᴏғ sᴜᴅᴏ ᴜsᴇʀs:\n"
    count = 1

    for user_data in sudo_users_cursor:
        try:
            user_mention = f"[{user_data['first_name']}](tg://user?id={user_data['user_id']})"
            text += f"{count}. {user_mention}\n"
            count += 1
        except Exception as e:
            await event.reply(f"Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ sᴜᴘᴇʀ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs: {e}")
            return

    if not text.strip():
        await event.reply("Nᴏ sᴜᴘᴇʀ ᴜsᴇʀs ғᴏᴜɴᴅ.")
    else:
        await event.reply(text, parse_mode='markdown')

# Authorize a user in a specific group
@BOT.on(events.NewMessage(pattern='/auth'))
async def auth(event):
    user = await event.get_sender()
    chat = await event.get_chat()

    # Check if the user is the owner or a sudo user
    if user.id != OWNER_ID and user.id not in sudo_users:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Check if a username or user ID is provided
    if not event.pattern_match.group(1):
        await event.reply("Usᴀɢᴇ: /auth <@ᴜsᴇʀɴᴀᴍᴇ> ᴏʀ ʀᴇᴘʟʏ  ᴏ ʜɪs/ʜᴇʀ ᴍᴇssᴀɢᴇ.")
        return

    sudo_user = event.pattern_match.group(1).strip()

    try:
        if sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))

        # Check if the user is already authorized in this group
        if authorized_users_collection.find_one({"user_id": sudo_user_id, "group_id": chat.id}):
            await event.reply(f"{user_entity.first_name} ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
            return

        # Add to the database
        authorized_users_collection.insert_one({
            "user_id": sudo_user_id,
            "username": user_entity.username,
            "first_name": user_entity.first_name,
            "group_id": chat.id
        })
        await event.reply(f"{user_entity.first_name} ʜᴀs ʙᴇᴇɴ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
    except Exception as e:
        await event.reply(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇ ᴜsᴇʀ: {e}")

# Unauthorize a user in a specific group
@BOT.on(events.NewMessage(pattern='/unauth'))
async def unauth(event):
    user = await event.get_sender()
    chat = await event.get_chat()

    # Check if the user is the owner or a sudo user
    if user.id != OWNER_ID and user.id not in sudo_users:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    # Check if a username or user ID is provided
    if not event.pattern_match.group(1):
        await event.reply("Usᴀɢᴇ: /unauth <@ᴜsᴇʀɴᴀᴍᴇ> ᴏʀ ʀᴇᴘʟʏ  ᴏ ʜɪs/ʜᴇʀ ᴍᴇssᴀɢᴇ.")
        return

    sudo_user = event.pattern_match.group(1).strip()

    try:
        if sudo_user.startswith('@'):
            user_entity = await BOT.get_entity(sudo_user)
            sudo_user_id = user_entity.id
        else:
            sudo_user_id = int(sudo_user)
            user_entity = await BOT.get_entity(PeerUser(sudo_user_id))

        # Check if the user is authorized in this group
        if not authorized_users_collection.find_one({"user_id": sudo_user_id, "group_id": chat.id}):
            await event.reply(f"{user_entity.first_name} ɪs ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
            return

        # Remove from the database
        authorized_users_collection.delete_one({"user_id": sudo_user_id, "group_id": chat.id})
        await event.reply(f"{user_entity.first_name} ʜᴀs ʙᴇᴇɴ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
    except Exception as e:
        await event.reply(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ ᴜsᴇʀ: {e}")

# Send bot statistics
@BOT.on(events.NewMessage(pattern='/stats'))
async def send_stats(event):
    user = await event.get_sender()

    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ  ᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    try:
        users_count = users_collection.count_documents({})
        chat_count = active_groups_collection.count_documents({})  # Use correct collection

        stats_msg = f"Tᴏᴛᴀʟ Usᴇʀs: {users_count}\nTᴏᴛᴀʟ Gʀᴏᴜᴘs: {chat_count}\n"
        await event.reply(stats_msg)
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ɪɴ send_stats ғᴜɴᴄᴛɪᴏɴ: {e}")
        await event.reply("Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ sᴛᴀs.")

# List active groups
@BOT.on(events.NewMessage(pattern='/activegroups'))
async def list_active_groups(event):
    user = await event.get_sender()

    if user.id != OWNER_ID:
        await event.reply("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    active_groups_from_db = fetch_active_groups_from_db()

    if not active_groups_from_db:
        await event.reply("Tʜᴇ ʙɪʟʟᴀ ᴇɢ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ ɪɴ ᴀɴʏ ɢʀᴏᴜᴘs ᴏʀ ғᴀɪʟᴇᴅ ᴛᴏ ᴄᴏᴍɴᴇᴄᴛ ᴛᴏ MᴏɴɢᴏDB.")
        return

    group_list_msg = "Aᴄᴛɪᴠᴇ ɢʀᴏᴜᴘs ᴡʜᴇʀᴇ ᴛʜᴇ ʙɪʟʟᴀ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ:\n"
    for group in active_groups_from_db:
        group_name = group.get("group_name", "Unknown Group")
        invite_link = group.get("invite_link", "Nᴏ ɪɴᴠɪᴛᴀᴛɪᴏɴ ᴀᴠᴀɪʟᴀʙʟᴅ")

        if invite_link != "ɪɴᴠɪᴛᴀᴛᴀᴛɪᴏɴ ᴀᴠᴀɪʟᴀʙʟᴇ":
            group_list_msg += f"- <a href='{invite_link}'>[{group_name}]</a>\n"
        else:
            group_list_msg += f"- {group_name}\n"

    await event.reply(group_list_msg, parse_mode='html')

# Fetch active groups from MongoDB
def fetch_active_groups_from_db():
    try:
        active_groups = list(active_groups_collection.find({}, {"group_id": 1, "group_name": 1, "invite_link": 1, "_id": 0}))
        return active_groups
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ MᴏɴɢᴏDB: {e}")
        return None
