from telethon import events
from telethon.tl.custom import Button
from config import BOT

START_OP = [
    [Button.url("ᴀᴅᴅ ᴍᴇ ↗️", "https://t.me/vxguardian_bot?startgroup=true&admin=delete_messages")],
    [Button.url("ꜱᴜᴘᴘᴏʀᴛ", "https://t.me/STORM_CORE"), Button.url("ᴄʜᴀɴɴᴇʟ", "https://t.me/STORM_TECHH")]
]

@BOT.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.is_private:
        KEX = await event.client.get_me()
        bot_name = KEX.first_name
        TEXT = f"""
<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴠx ɢᴜᴀʀᴅɪᴀɴ ʙᴏᴛ ⚡️</b>
<b><u>ɪ'ᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘ’ꜱ ꜱʜɪᴇʟᴅ ᴀɢᴀɪɴꜱᴛ ꜱᴘᴀᴍ, ᴜɴᴡᴀɴᴛᴇᴅ ᴍᴇᴅɪᴀ, ᴀɴᴅ ꜱɴᴇᴀᴋʏ ᴇᴅɪᴛꜱ.</u></b>
<blockquote><b>• ᴍᴇᴅɪᴀ ɢᴜᴀʀᴅ</b>
<b>• ᴄᴏɴᴛᴇɴᴛ ꜰɪʟᴛᴇʀ</b>
<b>• ᴇᴅɪᴛ ᴡᴀᴛᴄʜ</b>
<b>• ᴀᴜᴛᴏ ᴍᴇᴅɪᴀ ᴅᴇʟᴇᴛɪᴏɴ</b></blockquote>
<blockquote><b>✅ ᴀᴅᴅ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ.</b>
<b>/help ꜰᴏʀ ᴄᴏᴍᴍᴀɴᴅꜱ</b></blockquote>
"""
        await event.respond(TEXT, buttons=START_OP, parse_mode='html')
