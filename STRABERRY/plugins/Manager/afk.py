from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message
from STRABERRY import app
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB Setup
MONGO_URL = os.getenv("MONGO_DB_URI")
if not MONGO_URL:
    raise RuntimeError("MONGO_DB_URI is not set. Please provide it in the environment or .env file.")

mongo = AsyncIOMotorClient(MONGO_URL)
db = mongo["STRABERRY"]
afk_collection = db["afk_users"]

def build_afk_set_message(user_name, reason):
    return f"<b>😴 {user_name} ɪs ɴᴏᴡ ᴀꜰᴋ!</b>\n\n<i>🕒 ʀᴇᴀꜱᴏɴ:</i> <code>{reason}</code>\n<i>💤 ɪ'ʟʟ ʟᴇᴛ ᴏᴛʜᴇʀꜱ ᴋɴᴏᴡ ʏᴏᴜ'ʀᴇ ᴀᴡᴀʏ.</i>"


def build_afk_mention_message(name, time_afk, reason):
    return f"<b>💤 {name} ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴀꜰᴋ.</b>\n<i>🕒 ꜱɪɴᴄᴇ:</i> <code>{time_afk} ᴀɢᴏ</code>\n<i>📄 ʀᴇᴀꜱᴏɴ:</i> <code>{reason}</code>"


def build_afk_back_message(name, time_afk, reason):
    return f"<b>✅ ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ {name}!</b>\n<i>🕒 ʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ ꜰᴏʀ:</i> <code>{time_afk}</code>\n<i>📄 ʀᴇᴀꜱᴏɴ:</i> <code>{reason}</code>"


@app.on_message(filters.command(["afk", "afk@straberryxrobot"]) & ~filters.bot)
async def set_afk(_, message: Message):
    user = message.from_user
    if not user:
        return

    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "ɴᴏ ʀᴇᴀꜱᴏɴ"
    await afk_collection.update_one(
        {"user_id": user.id},
        {"$set": {"reason": reason, "time": datetime.utcnow(), "name": user.first_name}},
        upsert=True
    )

    text = build_afk_set_message(user.first_name, reason)
    await message.reply_text(text)


@app.on_message(filters.text & ~filters.bot, group=5)
async def mention_afk(_, message: Message):
    mentioned_ids = set()

    if message.reply_to_message and message.reply_to_message.from_user:
        mentioned_ids.add(message.reply_to_message.from_user.id)

    if message.entities:
        for entity in message.entities:
            if entity.type.name == "MENTION":
                username = message.text[entity.offset + 1 : entity.offset + entity.length]
                try:
                    user = await app.get_users(username)
                    mentioned_ids.add(user.id)
                except Exception:
                    pass
            elif entity.type.name == "TEXT_MENTION" and entity.user:
                mentioned_ids.add(entity.user.id)

    for user_id in mentioned_ids:
        afk_user = await afk_collection.find_one({"user_id": user_id})
        if afk_user:
            since = datetime.utcnow() - afk_user["time"]
            time_afk = str(timedelta(seconds=int(since.total_seconds())))
            try:
                text = build_afk_mention_message(afk_user['name'], time_afk, afk_user['reason'])
                await message.reply_text(text)
            except Exception:
                pass


@app.on_message(~filters.bot & ~filters.command(["afk", "afk@straberryxrobot"]), group=6)
async def remove_afk(_, message: Message):
    user = message.from_user
    if not user:
        return

    afk_user = await afk_collection.find_one({"user_id": user.id})
    if afk_user:
        since = datetime.utcnow() - afk_user["time"]
        time_afk = str(timedelta(seconds=int(since.total_seconds())))
        await afk_collection.delete_one({"user_id": user.id})

        text = build_afk_back_message(afk_user['name'], time_afk, afk_user['reason'])
        await message.reply_text(text)
