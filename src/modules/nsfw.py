from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat
import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from PIL import Image
import os
import re
import config
from config import BOT

SPOILER = config.SPOILER_MODE
slangf = 'slang_words.txt'

with open(slangf, 'r') as f:
    slang_words = set(line.strip().lower() for line in f)

model_name = "AdamCodd/vit-base-nsfw-detector"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

# NSFW detection function
async def check_nsfw_image(image_path):
    try:
        image = Image.open(image_path)
        inputs = feature_extractor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()

        return predicted_class == 1 
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ɪᴍᴀɢᴇ: {e}")
        return False

@BOT.on(events.NewMessage(func=lambda e: e.is_group and e.photo))
async def image(event):
    sender = await BOT.get_permissions(event.chat_id, event.sender_id)
    isadmin = sender.is_admin

    if not isadmin:
        try:
            photo = event.photo
            print(f"ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ ᴡɪᴛʜ ꜰɪʟᴇ ɪᴅ: {photo.id}")

            file_path = await event.download_media()
            print(f"ɪᴍᴀɢᴇ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ᴛᴏ: {file_path}")

            nsfw = await check_nsfw_image(file_path)

            if nsfw:
                name = event.sender.first_name
                await event.delete()
                
                await event.respond(
                    f"**⚠️ ᴡᴀʀɴɪɴɢ** (ɴꜱꜰᴡ ᴅᴇᴛᴇᴄᴛᴇᴅ)\n**{name}** ꜱᴇɴᴛ ɴꜱꜰᴡ ɪᴍᴀɢᴇ."
                )

                if SPOILER:  
                    await event.respond(
                        file=file_path,
                        message=f"**⚠️ ᴡᴀʀɴɪɴɢ** (ɴꜱꜰᴡ ᴅᴇᴛᴇᴄᴛᴇᴅ)\n**{name}** ꜱᴇɴᴛ ɴꜱꜰᴡ ɪᴍᴀɢᴇ.",
                        spoiler=True
                    )
            os.remove(file_path)

        except Exception as e:
            print(f"ᴇʀʀᴏʀ pʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ: {e}")

@BOT.on(events.NewMessage(func=lambda e: e.is_group and e.text))
async def slang(event):
    sender = await BOT.get_permissions(event.chat_id, event.sender_id)
    isadmin = sender.is_admin
    if not isadmin:
        sentence = event.text
        sent = re.sub(r'\W+', ' ', sentence)
        isslang = False
        for word in sent.split():
            if word.lower() in slang_words:
                isslang = True
                await event.delete()
                sentence = sentence.replace(word, f'||{word}||')
        
        if isslang:
            name = event.sender.first_name
            msgtxt = f"""{name} ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴛʜᴇ ᴘʀᴇꜱᴇɴᴄᴇ ᴏꜰ ɪɴᴀᴘᴘʀᴏᴘɪᴀᴛᴇ ʟᴀɴɢᴜᴀɢᴇ[ɢᴀᴀʟɪ/ꜱʟᴀɴɢꜰᴜʟ ᴡᴏʀᴅꜱ]. ʜᴇʀᴇ ɪꜱ ᴀ ᴄᴇɴꜱᴏʀᴇᴅ ᴠᴇʀꜱɪᴏɴ ᴏꜰ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ:

{sentence}
            """

            if SPOILER:
                await event.respond(msgtxt)
