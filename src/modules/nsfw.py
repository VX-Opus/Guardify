from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat
import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import os
import re
import asyncio
import config
from config import BOT

SPOILER = config.SPOILER_MODE
slangf = 'slang_words.txt'

with open(slangf, 'r') as f:
    slang_words = set(line.strip().lower() for line in f)

model_name = "AdamCodd/vit-base-nsfw-detector"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

def process_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            return torch.argmax(logits, dim=-1).item() == 1
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ɪᴍᴀɢᴇ: {e}")
        return False

async def check_nsfw_media(file_path):
    return await asyncio.to_thread(process_image, file_path)

@BOT.on(events.NewMessage(func=lambda e: e.is_group and (e.photo)))
async def media_handler(event):
    try:
        file_path = await event.download_media()
        nsfw = await check_nsfw_media(file_path)
        
        if nsfw:
            name = event.sender.first_name
            await event.delete()
            warning_msg = f"**⚠️ ɴꜱꜰᴡ ᴅᴇᴛᴇᴄᴛᴇᴅ**\n{name},ʏᴏᴜʀ ᴍᴇᴅɪᴀ ᴡᴀꜱ ʀᴇᴍᴏᴠᴇᴅ."
            await event.respond(warning_msg)
            
            if SPOILER:
                await event.respond(file=file_path, message=warning_msg, spoiler=True)
        
        os.remove(file_path)
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴍᴇᴅɪᴀ: {e}")

slang_pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in slang_words) + r')\b', re.IGNORECASE)

@BOT.on(events.NewMessage(func=lambda e: e.is_group and e.text))
async def slang_filter(event):
    sender = await BOT.get_permissions(event.chat_id, event.sender_id)
    if sender.is_admin:
        return
    
    sentence = event.text
    censored_sentence = slang_pattern.sub(lambda m: f'||{m.group()}||', sentence)
    
    if sentence != censored_sentence:
        await event.delete()
        name = event.sender.first_name
        msgtxt = f"{name}, ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡᴀꜱ ᴅᴇʟᴇᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ɪɴᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʟᴀɴɢᴜᴀɢᴇ. ʜᴇʀᴇ ɪꜱ ᴀ ᴄᴇɴꜱᴏʀᴇᴅ ᴠᴇʀꜱɪᴏɴ:\n\n{censored_sentence}"
        if SPOILER:
            await event.respond(msgtxt)
