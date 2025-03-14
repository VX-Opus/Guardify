from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import asyncio
import config import BOT


delay_times = {}


# Command to set the delay time
@BOT.on(events.NewMessage(pattern='/setdelay'))
async def set_delay(event):
    try:
        # Extract the delay time from the command
        delay = int(event.message.text.split(' ')[1])
        if delay < 1:
            await event.reply("Delay time must be at least 1 minute.")
            return

        # Store the delay time for the chat
        chat_id = event.chat_id
        delay_times[chat_id] = delay
        await event.reply(f"Auto-deletion delay set to {delay} minutes.")

    except (IndexError, ValueError):
        await event.reply("Usage: /setdelay <time_in_minutes>")

# Handler for media messages
@BOT.on(events.NewMessage(func=lambda e: e.is_group and e.media))
async def handle_media(event):
    chat_id = event.chat_id

    # Check if a delay time is set for this chat
    if chat_id in delay_times:
        delay = delay_times[chat_id]
        await asyncio.sleep(delay * 60)  # Wait for the specified delay

        try:
            # Delete the media message
            await event.delete()
            print(f"Deleted media in chat {chat_id} after {delay} minutes.")
        except Exception as e:
            print(f"Failed to delete media: {e}")
