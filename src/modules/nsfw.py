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

@BOT.on(events.NewMessage(func=lambda e: e.is_group and (e.photo or e.video or e.sticker or e.gif or e.document)))
async def media_handler(event):
    try:
        # Determine the type of media
        if event.photo:
            media_type = "photo"
            media = event.photo
        elif event.video:
            media_type = "video"
            media = event.video
        elif event.sticker:
            media_type = "sticker"
            media = event.sticker
        elif event.gif:
            media_type = "gif"
            media = event.gif
        elif event.document:
            media_type = "document"
            media = event.document
        else:
            return

        print(f"Downloading {media_type} with file id: {media.id}")

        file_path = await event.download_media()
        print(f"{media_type.capitalize()} downloaded to: {file_path}")

        # Skip NSFW check for non-image files
        if media_type in ["photo", "sticker"]:
            # Convert .webp stickers to .png for processing
            if media_type == "sticker" and file_path.endswith(".webp"):
                converted_path = file_path.replace(".webp", ".png")
                with Image.open(file_path) as img:
                    img.save(converted_path, "PNG")
                os.remove(file_path)  # Remove the original .webp file
                file_path = converted_path

            nsfw = await check_nsfw_image(file_path)  # NSFW check for images
        else:
            nsfw = False  # Skip NSFW check for videos, GIFs, and documents

        if nsfw:
            name = event.sender.first_name
            await event.delete()
            
            await event.respond(
                f"**⚠️ WARNING** (NSFW detected)\n**{name}** sent NSFW {media_type}."
            )

            if SPOILER:  
                await event.respond(
                    file=file_path,
                    message=f"**⚠️ WARNING** (NSFW detected)\n**{name}** sent NSFW {media_type}.",
                    spoiler=True
                )
        
        # Clean up downloaded files
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        print(f"Error processing {media_type}: {e}")

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
