from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatType, MessageEntityType
from STRABERRY import app
from STRABERRY.utils.decorators.language import language
import asyncio
import json
import os
import re
import atexit
from datetime import datetime

# ------------------------------
# 🔒 ʙᴀꜱɪᴄ ᴄᴏɴꜰɪɢ
# ------------------------------

LOCK_DATA_FILE = "lock_data.json"

# ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ʟᴏᴄᴋ ᴛʏᴘᴇꜱ (rose bot official + extras)
LOCKABLES = [
    "all", "album", "anonchannel", "audio", "bot", "button", "cashtag", "checklist",
    "cjk", "command", "comment", "contact", "cyrillic", "document", "email", "emoji",
    "emojicustom", "emojigame", "emojionly", "externalreply", "forward", "forwarduser",
    "forwardbot", "forwardchannel", "forwardstory", "game", "gif", "guestbot", "inline",
    "invitelink", "botlink", "location", "media", "outsidereaction", "phone", "photo",
    "pin", "poll", "reaction", "rtl", "spoiler", "sticker", "stickeranimated",
    "stickerpremium", "text", "url", "username", "video", "videonote", "voice", "zalgo"
]

# ꜱᴛʏʟɪꜱʜ ᴇᴍᴏᴊɪ ꜰᴏʀ ᴇᴀᴄʜ ʟᴏᴄᴋ ᴛʏᴘᴇ
EMOJI = {
    "all": "🔐", "audio": "🎵", "bot": "🤖", "button": "🔘", "contact": "📇",
    "document": "📄", "egame": "🎮", "forward": "🔄", "game": "🕹️",
    "gif": "🎞️", "info": "ℹ️", "inline": "⚡", "invitelink": "🔗",
    "location": "📍", "media": "📺", "messages": "💬", "other": "🧩",
    "photo": "🖼️", "pin": "📌", "poll": "📊", "previews": "🔍",
    "rtl": "↩️", "sticker": "✨", "url": "🔗", "username": "👤",
    "video": "🎥", "voice": "🎙️", "text": "📝",
    # Rose Bot extras
    "album": "🖼️", "anonchannel": "👤", "cashtag": "💰", "checklist": "✅",
    "cjk": "🇨🇳", "command": "⚙️", "comment": "💬", "cyrillic": "🇷🇺",
    "email": "📧", "emoji": "😀", "emojicustom": "🌟", "emojigame": "🎲",
    "emojionly": "😊", "externalreply": "↩️", "forwarduser": "👤", "forwardbot": "🤖",
    "forwardchannel": "📢", "forwardstory": "📱", "guestbot": "👾", "invitelink": "🔗",
    "botlink": "🤖", "outsidereaction": "🫥", "phone": "📞", "reaction": "👍",
    "spoiler": "🚫", "stickeranimated": "🎬", "stickerpremium": "💎", "videonote": "🎥",
    "zalgo": "⚠️"
}

BOT_OWNER_ID = 7844545002

# ------------------------------
# 💾 ᴅᴀᴛᴀ ʟᴏᴀᴅ / ꜱᴀᴠᴇ
# ------------------------------

def load_lock_data():
    try:
        if os.path.exists(LOCK_DATA_FILE):
            with open(LOCK_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except:
        return {}


def save_lock_data():
    try:
        with open(LOCK_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(lock_status, f, indent=4, ensure_ascii=False)
    except:
        pass


lock_status = load_lock_data()
atexit.register(save_lock_data)

# ------------------------------
# 🛡 ᴘᴇʀᴍɪꜱꜱɪᴏɴ ʜᴇʟᴘᴇʀꜱ
# ------------------------------

async def check_admin_permission(message: Message) -> bool:
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # ᴀʟᴡᴀʏꜱ ᴛʀᴇᴀᴛ ʙᴏᴛ ᴏᴡɴᴇʀ ᴀꜱ ᴀᴅᴍɪɴ
        if user_id == BOT_OWNER_ID:
            return True

        # ᴅɪʀᴇᴄᴛʟʏ ɢᴇᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ ᴀɴᴅ ᴄʜᴇᴄᴋ ꜱᴛᴀᴛᴜꜱ
        try:
            member = await app.get_chat_member(chat_id, user_id)
            status = member.status
            
            if status in [member.status.ADMINISTRATOR, member.status.OWNER]:
                return True
            return False
            
        except Exception as e:
            print(f"ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ: {e}")
            return False

    except Exception as e:
        print(f"ᴀᴅᴍɪɴ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴇʀʀᴏʀ: {e}")
        return False

async def check_owner_or_creator(message: Message) -> bool:
    try:
        # ᴄʜᴇᴄᴋ ɪꜰ ᴍᴇꜱꜱᴀɢᴇ.ꜰʀᴏᴍ_ᴜꜱᴇʀ ᴇxɪꜱᴛꜱ
        if not message.from_user:
            return False
            
        user = message.from_user
        chat = message.chat

        # ʙᴏᴛ ᴏᴡɴᴇʀ ʙʏᴘᴀꜱꜱ
        if user.id == BOT_OWNER_ID:
            return True

        # ᴄʜᴇᴄᴋ ᴀᴄᴛᴜᴀʟ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ ꜱᴛᴀᴛᴜꜱ
        m = await app.get_chat_member(chat.id, user.id)
        return m.status == m.status.OWNER

    except Exception as e:
        print("ᴏᴡɴᴇʀ ᴄʜᴇᴄᴋ ᴇʀʀᴏʀ:", e)
        return False

def set_metadata(chat_id: str, message: Message):
    try:
        lock_status.setdefault(chat_id, {})["_updated_by"] = (
            message.from_user.username
            or message.from_user.first_name
            or str(message.from_user.id)
        )
        lock_status.setdefault(chat_id, {})["_updated_at"] = datetime.utcnow().isoformat()
    except:
        pass

# ------------------------------
# 🔒 ʟᴏᴄᴋ ᴄᴏᴍᴍᴀɴᴅ
# ------------------------------

@app.on_message(filters.command(["lock", "lock@straberryxrobot"]) & filters.group)
@language
async def lock_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ!")
    except:
        return await message.reply_text("⛔ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ!")

    try:
        chat_id = str(message.chat.id)
        parts = message.text.split(maxsplit=1)

        if len(parts) < 2:
            return await message.reply_text("<i>❌ ᴜꜱᴇ:</i> <code>/lock &lt;ᴛʏᴘᴇ&gt;</code>")

        ltype = parts[1].lower()

        if ltype not in LOCKABLES:
            return await message.reply_text("<i>❌ ɪɴᴠᴀʟɪᴅ ʟᴏᴄᴋ ᴛʏᴘᴇ!</i>")

        # 🔥 ꜰᴜʟʟ ɢʀᴏᴜᴘ ʟᴏᴄᴋ
        if ltype == "all":
            for t in LOCKABLES:
                if t != "all":
                    lock_status.setdefault(chat_id, {})[t] = True

            set_metadata(chat_id, message)
            save_lock_data()

            try:
                await app.set_chat_permissions(
                    message.chat.id,
                    ChatPermissions()
                )
            except:
                pass

            return await message.reply_text("<b>🔐 ᴀʟʟ ʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")

        # 📸 ᴍᴇᴅɪᴀ ʟᴏᴄᴋ
        if ltype == "media":
            for t in [
                "photo", "video", "audio", "voice",
                "document", "sticker", "gif", "media"
            ]:
                lock_status.setdefault(chat_id, {})[t] = True

            set_metadata(chat_id, message)
            save_lock_data()

            return await message.reply_text("<b>🔒 ᴍᴇᴅɪᴀ ʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")

        # ꜱɪɴɢʟᴇ ᴛʏᴘᴇ ʟᴏᴄᴋ
        lock_status.setdefault(chat_id, {})[ltype] = True
        set_metadata(chat_id, message)
        # Ensure data is saved immediately
        save_lock_data()

        emoji = EMOJI.get(ltype, "🔒")
        return await message.reply_text(f"<b>{emoji} {ltype.title()} ʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")

    except Exception as e:
        print("ʟᴏᴄᴋ ᴇʀʀᴏʀ:", e)
        return await message.reply_text("<i>❌ ᴇʀʀᴏʀ!</i>")


# ------------------------------
# 🔓 ᴜɴʟᴏᴄᴋ ᴄᴏᴍᴍᴀɴᴅ
# ------------------------------

@app.on_message(filters.command(["unlock", "unlock@straberryxrobot"]) & filters.group)
@language
async def unlock_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")
    except:
        return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")

    try:
        chat_id = str(message.chat.id)
        parts = message.text.split(maxsplit=1)

        if len(parts) < 2:
            return await message.reply_text("<i>❌ ᴜꜱᴇ:</i> <code>/unlock &lt;ᴛʏᴘᴇ&gt;</code>")

        ltype = parts[1].lower()

        # ꜰᴜʟʟ ɢʀᴏᴜᴘ ᴜɴʟᴏᴄᴋ
        if ltype == "all":
            # ꜱᴀᴠᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ ᴀɴᴅ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ ʙᴇꜰᴏʀᴇ ᴄʟᴇᴀʀɪɴɢ
            lockadmin_status = lock_status.get(chat_id, {}).get("_lockadmin", False)
            silent_status = lock_status.get(chat_id, {}).get("_silent", False)
            
            # ꜱᴀᴠᴇ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ ɪꜰ ʟᴏᴄᴋᴀᴅᴍɪɴ ɪꜱ ᴏɴ
            media_locks = {}
            if lockadmin_status:
                media_types = ["photo", "video", "audio", "voice", "document", "sticker", "gif", "media"]
                for media_type in media_types:
                    if lock_status.get(chat_id, {}).get(media_type):
                        media_locks[media_type] = True
            
            # ᴄʟᴇᴀʀ ᴀʟʟ ʟᴏᴄᴋꜱ
            lock_status.pop(chat_id, None)
            
            # ʀᴇꜱᴛᴏʀᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ, ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ, ᴀɴᴅ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ
            if lockadmin_status:
                lock_status.setdefault(chat_id, {})["_lockadmin"] = lockadmin_status
                for media_type, status in media_locks.items():
                    lock_status.setdefault(chat_id, {})[media_type] = status
                    
            if silent_status:
                lock_status.setdefault(chat_id, {})["_silent"] = silent_status
                
            save_lock_data()

            try:
                await app.set_chat_permissions(
                    message.chat.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
            except:
                pass

            return await message.reply_text("<b>🔓 ᴀʟʟ ᴜɴʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")

        # ᴍᴇᴅɪᴀ ᴜɴʟᴏᴄᴋ
        if ltype == "media":
            for t in [
                "photo", "video", "audio", "voice",
                "document", "sticker", "gif", "media"
            ]:
                if chat_id in lock_status:
                    lock_status[chat_id].pop(t, None)

            set_metadata(chat_id, message)
            save_lock_data()

            return await message.reply_text("<b>🔓 ᴍᴇᴅɪᴀ ᴜɴʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")

        # ꜱɪɴɢʟᴇ ᴛʏᴘᴇ ᴜɴʟᴏᴄᴋ
        if chat_id in lock_status and ltype in lock_status[chat_id]:
            lock_status[chat_id].pop(ltype, None)
            # Also remove metadata if no locks remain
            if not any(k for k in lock_status[chat_id].keys() if not str(k).startswith("_")):
                lock_status.pop(chat_id, None)
            set_metadata(chat_id, message)
            save_lock_data()

            emoji = EMOJI.get(ltype, "🔓")
            return await message.reply_text(f"<b>{emoji} {ltype.title()} ᴜɴʟᴏᴄᴋᴇᴅ!</b>")

        return await message.reply_text("<i>ℹ️ ɴᴏᴛ ʟᴏᴄᴋᴇᴅ!</i>")

    except Exception as e:
        print("ᴜɴʟᴏᴄᴋ ᴇʀʀᴏʀ:", e)
        return await message.reply_text("<i>❌ ᴇʀʀᴏʀ!</i>")


# ------------------------------
# 🔓 ᴜɴʟᴏᴄᴋ ᴀʟʟ
# ------------------------------

@app.on_message(filters.command(["unlockall", "unlockall@straberryxrobot"]) & filters.group)
@language
async def unlockall_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")
    except:
        return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")

    chat_id = str(message.chat.id)
    
    # ꜱᴀᴠᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ ꜱᴛᴀᴛᴜꜱ ᴀɴᴅ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ ʙᴇꜰᴏʀᴇ ᴄʟᴇᴀʀɪɴɢ
    lockadmin_status = lock_status.get(chat_id, {}).get("_lockadmin", False)
    silent_status = lock_status.get(chat_id, {}).get("_silent", False)
    
    # ꜱᴀᴠᴇ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ ɪꜰ ʟᴏᴄᴋᴀᴅᴍɪɴ ɪꜱ ᴏɴ
    media_locks = {}
    if lockadmin_status:
        media_types = ["photo", "video", "audio", "voice", "document", "sticker", "gif", "media"]
        for media_type in media_types:
            if lock_status.get(chat_id, {}).get(media_type):
                media_locks[media_type] = True
    
    # ᴄʟᴇᴀʀ ᴀʟʟ ʟᴏᴄᴋꜱ
    lock_status.pop(chat_id, None)
    
    # ʀᴇꜱᴛᴏʀᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ, ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ, ᴀɴᴅ ᴍᴇᴅɪᴀ ʟᴏᴄᴋꜱ
    if lockadmin_status:
        lock_status.setdefault(chat_id, {})["_lockadmin"] = lockadmin_status
        for media_type, status in media_locks.items():
            lock_status.setdefault(chat_id, {})[media_type] = status
            
    if silent_status:
        lock_status.setdefault(chat_id, {})["_silent"] = silent_status
        
    save_lock_data()

    try:
        await app.set_chat_permissions(
            message.chat.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
    except:
        pass

    return await message.reply_text("<b>🔓 ᴀʟʟ ᴜɴʟᴏᴄᴋᴇᴅ!</b>")

@app.on_message(filters.command(["locktypes", "locktypes@straberryxrobot"]) & filters.group)
async def locktypes_cmd(client, message):

    text = "🔐 ᴀᴠᴀɪʟᴀʙʟᴇ ʟᴏᴄᴋ ᴛʏᴘᴇꜱ:\n\n"

    for t in LOCKABLES:
        emoji = EMOJI.get(t, "🔸")
        text += f"{emoji} {t}\n"

    await message.reply_text(text)


# ------------------------------
# 📊 ᴀᴄᴛɪᴠᴇ ʟᴏᴄᴋꜱ
# ------------------------------

@app.on_message(filters.command(["locks", "locks@straberryxrobot"]) & filters.group)
@language
async def locks_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ!")
    except:
        return await message.reply_text("⛔ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ!")

    chat_id = str(message.chat.id)
    data = lock_status.get(chat_id, {})

    active = [k for k, v in data.items() if v and not str(k).startswith("_")]

    if not active:
        return await message.reply_text("✨ ɴᴏ ᴀᴄᴛɪᴠᴇ ʟᴏᴄᴋꜱ!")

    text = "🔐 ᴀᴄᴛɪᴠᴇ ʟᴏᴄᴋꜱ:\n\n"
    for key in active:
        emoji = EMOJI.get(key, "🔸")
        text += f"{emoji} {key}\n"

    await message.reply_text(text)


# ------------------------------
# 📌 ꜰᴜʟʟ ʟᴏᴄᴋ ꜱᴛᴀᴛᴜꜱ
# ------------------------------

@app.on_message(filters.command(["lockstatus", "lockstatus@straberryxrobot"]) & filters.group)
@language
async def lockstatus_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")
    except:
        return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")

    chat_id = str(message.chat.id)
    data = lock_status.get(chat_id, {})

    result = "🔐 ꜱᴛʏʟɪꜱʜ ʟᴏᴄᴋ ꜱᴛᴀᴛᴜꜱ:\n\n"

    for key in LOCKABLES:
        if key == "all":
            continue

        emoji = EMOJI.get(key, "🔸")
        status = "🔒" if data.get(key) else "🔓"
        result += f"{emoji} {key} — {status}\n"

    return await message.reply_text(result)


# ------------------------------
# 🔕 ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ
# ------------------------------

@app.on_message(filters.command(["locksilent", "locksilent@straberryxrobot"]) & filters.group)
@language
async def locksilent_cmd(client, message: Message, _):
    
    # ꜱɪᴍᴘʟᴇ ᴀᴅᴍɪɴ ᴄʜᴇᴄᴋ
    try:
        user = await app.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [user.status.ADMINISTRATOR, user.status.OWNER]:
            if message.from_user.id != BOT_OWNER_ID:
                return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")
    except:
        return await message.reply_text("⛔ ᴀᴅᴍɪɴ ᴏɴʟʏ!")

    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        mode = lock_status.get(chat_id, {})["_silent"] if chat_id in lock_status and "_silent" in lock_status[chat_id] else False
        return await message.reply_text(
            f"🔕 ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ: {'ᴏɴ' if mode else 'ᴏꜰꜰ'}"
        )

    mode = args[1].lower()

    if mode in ["on", "enable", "yes"]:
        lock_status.setdefault(chat_id, {})["_silent"] = True
        save_lock_data()
        return await message.reply_text("🔕✨ ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!")

    elif mode in ["off", "disable", "no"]:
        lock_status.setdefault(chat_id, {})["_silent"] = False
        save_lock_data()
        return await message.reply_text("🔔✨ ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ!")

    else:
        return await message.reply_text("❌ ᴜꜱᴇ: /locksilent ᴏɴ/ᴏꜰꜰ")


# ------------------------------
# 👀 ᴡᴀᴛᴄʜᴇʀ — ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ʟᴏᴄᴋᴇᴅ ᴄᴏɴᴛᴇɴᴛ (ᴄᴏᴍᴘʟᴇᴛᴇ ꜰɪx)
# ------------------------------

def _get_message_entities(message: Message):
    entities = getattr(message, "entities", None) or getattr(message, "caption_entities", None) or []
    return entities or []


def _contains_username_reference(message: Message) -> bool:
    text = (message.text or "" if message.text else "") or (message.caption or "" if message.caption else "")
    if not text:
        return False

    # First check: entities (mention type)
    for entity in _get_message_entities(message):
        entity_type = getattr(entity, "type", None)
        if entity_type in {MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION}:
            return True

    # Second check: regex for @username pattern (more robust)
    # Handles: @username, @username123, @user_name, etc.
    # Excludes: .@username (start with punctuation)
    username_pattern = r"(?<![a-zA-Z0-9_@])@([a-zA-Z0-9_]{1,32})\b"
    if re.search(username_pattern, text):
        return True

    return False


@app.on_message(filters.group, group=69)
async def lock_watcher(client, message: Message):
    try:
        # ꜱᴋɪᴘ ɪꜰ ɴᴏ ᴜꜱᴇʀ ᴏʀ ʙᴏᴛ
        if not message.from_user or message.from_user.is_bot:
            return

        chat_id = str(message.chat.id)
        data = lock_status.get(chat_id, {})
        
        # ꜱᴋɪᴘ ɪꜰ ɴᴏ ʟᴏᴄᴋꜱ ᴀᴄᴛɪᴠᴇ
        if not data:
            return

        # ɢᴇᴛ ᴜꜱᴇʀ ᴍᴇᴍʙᴇʀ ɪɴꜰᴏ
        try:
            user_member = await app.get_chat_member(message.chat.id, message.from_user.id)
            user_status = user_member.status
            user_id = message.from_user.id
        except Exception as e:
            return

        # ᴄʜᴇᴄᴋ ɪꜰ ʟᴏᴄᴋᴀᴅᴍɪɴ ɪꜱ ᴇɴᴀʙʟᴇᴅ
        lockadmin_on = data.get("_lockadmin", False)
        silent_mode = data.get("_silent", False)

        # ᴅᴇᴛᴇʀᴍɪɴᴇ ᴘʀɪᴠɪʟᴇɢᴇ
        is_privileged = False
        
        # ʙᴏᴛ ᴏᴡɴᴇʀ ᴀʟᴡᴀʏꜱ ᴘʀɪᴠɪʟᴇɢᴇᴅ (ɴᴇᴠᴇʀ ᴅᴇʟᴇᴛᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴍᴇꜱꜱᴀɢᴇꜱ)
        if user_id == BOT_OWNER_ID:
            is_privileged = True
        # ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ᴀʟᴡᴀʏꜱ ᴘʀɪᴠɪʟᴇɢᴇᴅ
        elif user_status == user_member.status.OWNER:
            is_privileged = True
        # ꜰᴏʀ ᴀᴅᴍɪɴꜱ - ᴄʜᴇᴄᴋ ʟᴏᴄᴋᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢ
        elif user_status == user_member.status.ADMINISTRATOR:
            if lockadmin_on:
                # ʟᴏᴄᴋᴀᴅᴍɪɴ ᴏɴ - ᴀᴅᴍɪɴꜱ ᴀʀᴇ ɴᴏᴛ ᴘʀɪᴠɪʟᴇɢᴇᴅ
                is_privileged = False
            else:
                # ʟᴏᴄᴋᴀᴅᴍɪɴ ᴏꜰꜰ - ᴀᴅᴍɪɴꜱ ᴀʀᴇ ᴘʀɪᴠɪʟᴇɢᴇᴅ
                is_privileged = True
        else:
            # ɴᴏʀᴍᴀʟ ᴜꜱᴇʀꜱ ᴀʀᴇ ɴᴇᴠᴇʀ ᴘʀɪᴠɪʟᴇɢᴇᴅ
            is_privileged = False

        # ɪꜰ ᴜꜱᴇʀ ɪꜱ ᴘʀɪᴠɪʟᴇɢᴇᴅ, ꜱᴋɪᴘ ᴀʟʟ ᴄʜᴇᴄᴋꜱ (ɴᴇᴠᴇʀ ᴅᴇʟᴇᴛᴇ)
        if is_privileged:
            return

        # ᴄʜᴇᴄᴋ ʟᴏᴄᴋꜱ - ᴏɴʟʏ ꜰᴏʀ ɴᴏɴ-ᴘʀɪᴠɪʟᴇɢᴇᴅ ᴜꜱᴇʀꜱ
        delete_it = False

        # ꜰᴜʟʟ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ
        if data.get("all"):
            delete_it = True

        # ɪɴᴅɪᴠɪᴅᴜᴀʟ ʟᴏᴄᴋ ᴄʜᴇᴄᴋꜱ - ᴄᴏᴍᴘʟᴇᴛᴇ ʟɪꜱᴛ
        elif message.text and data.get("text"):
            delete_it = True
        
        elif message.photo and data.get("photo"):
            delete_it = True
        
        elif message.video and data.get("video"):
            delete_it = True
        
        elif message.audio and data.get("audio"):
            delete_it = True
        
        elif message.voice and data.get("voice"):
            delete_it = True
        
        elif message.document and data.get("document"):
            delete_it = True
        
        elif message.sticker and data.get("sticker"):
            delete_it = True
        
        elif getattr(message, "animation", None) and data.get("gif"):
            delete_it = True
        
        elif message.poll and data.get("poll"):
            delete_it = True
        
        elif message.contact and data.get("contact"):
            delete_it = True
        
        elif message.location and data.get("location"):
            delete_it = True
        
        elif message.forward_date and data.get("forward"):
            delete_it = True
        
        # ᴘɪɴ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ᴘɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ
        elif message.pinned_message and data.get("pin"):
            delete_it = True

        # ᴜʀʟ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ꜰᴏʀ ʜᴛᴛᴘ/ʜᴛᴛᴘs/ᴡᴡᴡ ʟɪɴᴋꜱ
        elif data.get("url"):
            text_to_check = (message.text or "") if message.text else (message.caption or "")
            if text_to_check:
                # Check for URLs using regex (more reliable than entities)
                url_pattern = r"(?i)\b((?:https?://|www\.)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(/[a-zA-Z0-9+&@#/%?=~_|!:,.;-]*)?)"
                if re.search(url_pattern, text_to_check):
                    delete_it = True
                else:
                    # Fallback: check entities if regex fails
                    entities = message.entities or message.caption_entities
                    if entities:
                        for e in entities:
                            if getattr(e, "type", None) == MessageEntityType.URL:
                                delete_it = True
                                break

        # ᴜꜱᴇʀɴᴀᴍᴇ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ꜰᴏʀ @ᴍᴇɴᴛɪᴏɴꜱ ᴀɴᴅ ᴜꜱᴇʀɴᴀᴍᴇ ᴛᴀɢꜱ (INDEPENDENT CHECK - not elif)
        if not delete_it and data.get("username"):
            # Check both text and caption for username mentions
            has_username = False
            text_to_check = ""
            
            if message.text:
                text_to_check = message.text
                # Check entities for text
                for entity in getattr(message, "entities", []) or []:
                    if getattr(entity, "type", None) in {MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION}:
                        has_username = True
                        break
            
            if not has_username and message.caption:
                text_to_check = message.caption
                # Check caption entities
                for entity in getattr(message, "caption_entities", []) or []:
                    if getattr(entity, "type", None) in {MessageEntityType.MENTION, MessageEntityType.TEXT_MENTION}:
                        has_username = True
                        break
            
            # If no entity found, use regex fallback
            if not has_username and text_to_check:
                if re.search(r"(?<![a-zA-Z0-9_@])@([a-zA-Z0-9_]{1,32})\b", text_to_check):
                    has_username = True
            
            if has_username:
                delete_it = True

        # ʙᴏᴛꜱ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ᴘʀᴇᴠᴇɴᴛ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ
        elif message.text and data.get("bots"):
            # Check for bot commands starting with / or !
            if message.text.startswith("/") or message.text.startswith("!"):
                delete_it = True
            else:
                # Also check for inline bot queries (e.g., @bot username)
                # Check if message contains @username followed by a space (inline query format)
                if re.search(r"(?<!\w)@[a-zA-Z][a-zA-Z0-9_]{3,31}\s", message.text):
                    delete_it = True

        # ʙᴜᴛᴛᴏɴ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴꜱ (ʀᴇᴘʟʏ_ᴍᴀʀᴋᴜᴘ ɪɴᴄʟᴜᴅᴇꜱ ɪɴʟɪɴᴇᴋᴇʏʙᴏᴀʀᴅ)
        elif data.get("button"):
            if message.reply_markup:
                # Check if reply_markup has inline buttons
                for row in getattr(message.reply_markup, "inline_keyboard", []) or []:
                    if row:
                        delete_it = True
                        break

        # ɪɴᴠɪᴛᴇ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ᴛᴇʟᴇɢʀᴀᴍ ɪɴᴠɪᴛᴇ ʟɪɴᴋꜱ
        elif data.get("invite"):
            text_to_check = (message.text or "") if message.text else (message.caption or "")
            if text_to_check:
                # Check for Telegram invite links using regex
                invite_pattern = r"(?i)\b(t\.me/joinchat/|telegram\.me/joinchat/|t\.me/[a-zA-Z0-9_]+\?[a-zA-Z0-9_]+)"
                if re.search(invite_pattern, text_to_check):
                    delete_it = True
        
        # ᴘʀᴇᴠɪᴇᴡꜱ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ - ꜰᴏʀ ʟɪɴᴋ ᴘʀᴇᴠɪᴇᴡꜱ (ꜰɪʟᴇꜱ ᴡɪᴛʜ ᴜʀʟ)
        elif data.get("previews"):
            if (message.text or message.caption):
                url_pattern = r"(?i)\b((?:https?://|www\.)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+)"
                if re.search(url_pattern, (message.text or message.caption)):
                    delete_it = True

        # ɢᴀᴍᴇ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ
        elif data.get("game"):
            if getattr(message, "game", None):
                delete_it = True
            # Check for egame (emoji game) - check for game entities
            elif getattr(message, "entities", None):
                for e in message.entities:
                    if getattr(e, "type", None) == MessageEntityType.TEXT_MENTION:
                        # Could be an inline game mention
                        delete_it = True
                        break

        # ʟᴏᴄᴀᴛɪᴏɴ ʟᴏᴄᴋ ᴄʜᴇᴄᴋ
        elif message.location and data.get("location"):
            delete_it = True
        
        # ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ʟᴏᴄᴋ
        elif data.get("phone"):
            if (message.text or message.caption):
                phone_pattern = r"\b\+?[0-9]{1,4}[-.\s]?\(?\d{1,5}\)?[-.\s]?\d{1,5}[-.\s]?\d{1,6}\b"
                if re.search(phone_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴇᴍᴀɪʟ ʟᴏᴄᴋ
        elif data.get("email"):
            if (message.text or message.caption):
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                if re.search(email_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴄᴀsʜʟᴀɢ ʟᴏᴄᴋ ($TOKEN)
        elif data.get("cashtag"):
            if (message.text or message.caption):
                cashtag_pattern = r"\$[A-Za-z]{3,}\b"
                if re.search(cashtag_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴄᴊᴋ ʟᴏᴄᴋ (ᴄʜɪɴᴇꜱᴇ/ᴊᴀᴘᴀɴᴇꜱᴇ/ᴋᴏʀᴇᴀɴ)
        elif data.get("cjk"):
            if (message.text or message.caption):
                cjk_pattern = r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]"
                if re.search(cjk_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴄʏʀɪʟʟɪᴄ ʟᴏᴄᴋ (ʀᴜꜱꜱɪᴀɴ, ᴜᴋʀᴀɪɴɪᴀɴ, ᴇᴛᴄ)
        elif data.get("cyrillic"):
            if (message.text or message.caption):
                cyrillic_pattern = r"[а-яА-ЯёЁ]"
                if re.search(cyrillic_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ʀᴛʟ ʟᴏᴄᴋ (ᴀʀᴀʙɪᴄ, ʜᴇʙʀᴇᴡ)
        elif data.get("rtl"):
            if (message.text or message.caption):
                rtl_pattern = r"[\u0600-\u06FF\u0590-\u05FF]"
                if re.search(rtl_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴢᴀʟɢᴏ ʟᴏᴄᴋ (ᴛᴇxᴛ ᴡɪᴛʜ ᴇxᴛʀᴀ ꜰᴏʀᴍᴀᴛᴛɪɴɢ)
        elif data.get("zalgo"):
            if (message.text or message.caption):
                zalgo_pattern = r"[\u0300-\u036F\u0489]"
                if re.search(zalgo_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ꜱᴘᴏɪʟᴇʀ ʟᴏᴄᴋ
        elif data.get("spoiler"):
            if getattr(message, "has_media_spoiler", False):
                delete_it = True
            elif message.caption:
                if "tg-spoiler" in message.caption or "||" in message.caption:
                    delete_it = True
            elif message.text:
                if "tg-spoiler" in message.text or "||" in message.text:
                    delete_it = True
        
        # ᴇᴍᴏᴊɪ ʟᴏᴄᴋ (ᴀɴʏ ᴇᴍᴏᴊɪ)
        elif data.get("emoji"):
            if (message.text or message.caption or message.sticker):
                # Check for any emoji in text
                emoji_pattern = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002600-\U000026FF]"
                if re.search(emoji_pattern, (message.text or message.caption)):
                    delete_it = True
                elif message.sticker:
                    delete_it = True
        
        # ᴇᴍᴏᴊɪᴏɴʟʏ ʟᴏᴄᴋ (ᴏɴʟʏ ᴇᴍᴏᴊɪ, ɴᴏ ᴛᴇxᴛ)
        elif data.get("emojionly"):
            if message.text:
                # Check if message is ONLY emoji
                emoji_only_pattern = r"^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002600-\U000026FF]+$"
                if re.search(emoji_only_pattern, message.text):
                    delete_it = True
        
        # ᴇᴍᴏᴊɪɢᴀᴍᴇ ʟᴏᴄᴋ (ᴅɪᴄᴇ, ꜰᴏᴏᴛʙᴀʟʟ, ᴇᴛᴄ)
        elif data.get("emojigame"):
            if getattr(message, "dice", None):
                delete_it = True
        
        # ꜱᴛɪᴄᴋᴇʀᴀɴɪᴍᴀᴛᴇᴅ ʟᴏᴄᴋ
        elif data.get("stickeranimated"):
            if message.sticker and getattr(message.sticker, "is_animated", False):
                delete_it = True
        
        # ꜱᴛɪᴄᴋᴇʀᴘʀᴇᴍɪᴜᴍ ʟᴏᴄᴋ
        elif data.get("stickerpremium"):
            if message.sticker and getattr(message.sticker, "is_video", False):
                delete_it = True
        
        # ᴠɪᴅᴇᴏɴᴏᴛᴇ ʟᴏᴄᴋ
        elif data.get("videonote"):
            if getattr(message, "video_note", None):
                delete_it = True
        
        # ɢᴜᴇꜱᴛʙᴏᴛ ʟᴏᴄᴋ
        elif data.get("guestbot"):
            if getattr(message, "is_automatic_forward", False):
                delete_it = True
        
        # ᴇxᴛᴇʀɴᴀʟʀᴇᴘʟʏ ʟᴏᴄᴋ
        elif data.get("externalreply"):
            if getattr(message, "reply_to_message", None) and getattr(message.reply_to_message, "chat", None):
                if message.reply_to_message.chat.id != message.chat.id:
                    delete_it = True
        
        # ɪɴʟɪɴᴇ ʙᴏᴛ ʟᴏᴄᴋ
        elif data.get("inline"):
            if (message.text or message.caption):
                inline_pattern = r"(?<!\w)@[a-zA-Z][a-zA-Z0-9_]{3,31}\s"
                if re.search(inline_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ɪɴᴠɪᴛᴇʟɪɴᴋ ʟᴏᴄᴋ (ʀᴏꜱᴇ ʙᴏᴛ ꜰᴏʀᴍᴀᴛ)
        elif data.get("invitelink"):
            if (message.text or message.caption):
                invite_pattern = r"(?i)\b(t\.me/joinchat/|telegram\.me/joinchat/|t\.me/[a-zA-Z0-9_]+\?[a-zA-Z0-9_]+)"
                if re.search(invite_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ʙᴏᴛʟɪɴᴋ ʟᴏᴄᴋ
        elif data.get("botlink"):
            if (message.text or message.caption):
                botlink_pattern = r"(?i)\b(t\.me/[a-zA-Z0-9_]+bot|telegram\.me/[a-zA-Z0-9_]+bot)"
                if re.search(botlink_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ɢʀᴏᴜᴘ ʙᴏᴛ ʟᴏᴄᴋ (ʀᴏꜱᴇ ʙᴏᴛ: bot lock)
        elif data.get("bot"):
            if getattr(message, "new_chat_members", None) or getattr(message, "left_chat_member", None):
                if message.new_chat_members:
                    for user in message.new_chat_members:
                        if user.is_bot:
                            delete_it = True
                            break
                if message.left_chat_member and message.left_chat_member.is_bot:
                    delete_it = True
        
        # ғᴏʀᴡᴀʀᴅᴜsᴇʀ ʟᴏᴄᴋ
        elif data.get("forwarduser"):
            if message.forward_from:
                delete_it = True
        
        # ғᴏʀᴡᴀʀᴅʙᴏᴛ ʟᴏᴄᴋ
        elif data.get("forwardbot"):
            if message.forward_from and message.forward_from.is_bot:
                delete_it = True
        
        # ғᴏʀᴡᴀʀᴅᴄʜᴀɴɴᴇʟ ʟᴏᴄᴋ
        elif data.get("forwardchannel"):
            if message.forward_from_chat and message.forward_from_chat.type in ["channel", "supergroup"]:
                delete_it = True
        
        # ғᴏʀᴡᴀʀᴅsᴛᴏʀy ʟᴏᴄᴋ
        elif data.get("forwardstory"):
            if getattr(message, "forward_from_story", None):
                delete_it = True
        
        # ғᴏʀᴡᴀʀᴅ ʟᴏᴄᴋ (ꜰᴜʟʟ)
        elif data.get("forward"):
            if message.forward_date:
                delete_it = True
        
        # ᴀɴᴏɴᴄʜᴀɴɴᴇʟ ʟᴏᴄᴋ
        elif data.get("anonchannel"):
            if getattr(message, "sender_chat", None):
                delete_it = True
        
        # ʀᴇᴀᴄᴛɪᴏɴ ʟᴏᴄᴋ
        elif data.get("reaction"):
            if getattr(message, "reaction", None):
                delete_it = True
        
        # ᴏᴜᴛsɪᴅᴇʀᴇᴀᴄᴛɪᴏɴ ʟᴏᴄᴋ
        elif data.get("outsidereaction"):
            # Check if reactions exist but sender is not group member
            if getattr(message, "reactions", None):
                delete_it = True
        
        # ᴄʜᴇᴄᴋʟɪsᴛ ʟᴏᴄᴋ
        elif data.get("checklist"):
            if getattr(message, "service", None) and "checklist" in str(getattr(message, "text", "")).lower():
                delete_it = True
        
        # ᴄᴏᴍᴍᴇɴᴛ ʟᴏᴄᴋ (ᴏᴜᴛꜱɪᴅᴇʀ ᴄᴏᴍᴍᴇɴᴛꜱ)
        elif data.get("comment"):
            # Comment lock - if message is from linked channel and user is not group member
            if getattr(message, "is_automatic_forward", False):
                delete_it = True
        
        # ᴇᴍᴏᴊɪᴄᴜsᴛᴏᴍ ʟᴏᴄᴋ
        elif data.get("emojicustom"):
            if message.sticker and getattr(message.sticker, "emoji", None) is None:
                # Custom emoji has no emoji field
                delete_it = True
            elif (message.text or message.caption):
                custom_emoji_pattern = r"(<emoji id=\"[^\"]+\">)"
                if re.search(custom_emoji_pattern, (message.text or message.caption)):
                    delete_it = True
        
        # ᴍᴇᴅɪᴀ ʟᴏᴄᴋ (ᴄᴏᴍʙɪɴᴇᴅ ᴄʜᴇᴄᴋ)
        elif data.get("media"):
            if any([getattr(message, mt, None) for mt in ["photo", "video", "audio", "voice", "sticker", "document", "gif"]]):
                delete_it = True

        # ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇ ɪꜰ ʟᴏᴄᴋᴇᴅ
        if delete_it:
            try:
                await message.delete()

                # ꜱᴇɴᴅ ᴡᴀʀɴɪɴɢ ɪꜰ ɴᴏᴛ ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ
                if not silent_mode:
                    warn_msg = f"⛔ {message.from_user.mention} ᴛʜɪꜱ ᴄᴏɴᴛᴇɴᴛ ɪꜱ ʟᴏᴄᴋᴇᴅ!"
                    sent_msg = await message.reply_text(warn_msg)
                    await asyncio.sleep(3)
                    await sent_msg.delete()

            except Exception as delete_error:
                print(f"ᴅᴇʟᴇᴛᴇ ᴇʀʀᴏʀ: {delete_error}")

    except Exception as e:
        if "'Message' object has no attribute 'te'" in str(e):
            pass
        else:
            print(f"ᴡᴀᴛᴄʜᴇʀ ᴇʀʀᴏʀ: {e}")


# ------------------------------
# 🔐 ʟᴏᴄᴋᴀᴅᴍɪɴ
# ------------------------------

@app.on_message(filters.command(["lockadmin", "lockadmin@straberryxrobot"]) & filters.group)
@language
async def lockadmin_cmd(client, message: Message, _):

    if not message.from_user:
        return await message.reply_text("❌ ᴜɴᴀʙʟᴇ ᴛᴏ ɪᴅᴇɴᴛɪꜰʏ ᴜꜱᴇʀ!")

    if not await check_owner_or_creator(message):
        return await message.reply_text(
            "👑 ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴀɴᴅ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!"
        )

    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        current = lock_status.get(chat_id, {}).get("_lockadmin", False)
        return await message.reply_text(
            f"🔑 ʟᴏᴄᴋᴀᴅᴍɪɴ: {'ᴏɴ' if current else 'ᴏꜰꜰ'}"
        )

    mode = args[1].lower()

    if mode in ["on", "enable", "yes"]:
        # ᴀᴜᴛᴏ ʟᴏᴄᴋ ᴀʟʟ ᴍᴇᴅɪᴀ ᴛʏᴘᴇꜱ ᴡʜᴇɴ ʟᴏᴄᴋᴀᴅᴍɪɴ ɪꜱ ᴇɴᴀʙʟᴇᴅ
        media_types = ["photo", "video", "audio", "voice", "document", "sticker", "gif", "media"]
        for media_type in media_types:
            lock_status.setdefault(chat_id, {})[media_type] = True
        
        # ᴇɴᴀʙʟᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ
        lock_status.setdefault(chat_id, {})["_lockadmin"] = True
        set_metadata(chat_id, message)
        save_lock_data()
        
        return await message.reply_text("🔑✨ ʟᴏᴄᴋᴀᴅᴍɪɴ ᴇɴᴀʙʟᴇᴅ + ᴀʟʟ ᴍᴇᴅɪᴀ ʟᴏᴄᴋᴇᴅ!")

    elif mode in ["off", "disable", "no"]:
        # ᴅɪꜱᴀʙʟᴇ ʟᴏᴄᴋᴀᴅᴍɪɴ ʙᴜᴛ ᴅᴏɴ'ᴛ ᴜɴʟᴏᴄᴋ ᴍᴇᴅɪᴀ
        lock_status.setdefault(chat_id, {})["_lockadmin"] = False
        set_metadata(chat_id, message)
        save_lock_data()
        
        return await message.reply_text("🔑✨ ʟᴏᴄᴋᴀᴅᴍɪɴ ᴅɪꜱᴀʙʟᴇᴅ!")

    else:
        return await message.reply_text("❌ ᴜꜱᴇ: /lockadmin ᴏɴ/ᴏꜰꜰ")


# ------------------------------
# ❓ ʟᴏᴄᴋ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅ
# ------------------------------

@app.on_message(filters.command(["lockhelp", "lockhelp@straberryxrobot"]) & filters.group)
@language
async def lock_help(client, message: Message, _):

    text = """
🔐 ʟᴏᴄᴋ ꜱʏꜱᴛᴇᴍ ʜᴇʟᴘ (Rose Bot Compatible)

✨ ʙᴀꜱɪᴄ ʟᴏᴄᴋꜱ
/lock text - 📝 ʟᴏᴄᴋ ᴛᴇxᴛ ᴍᴇꜱꜱᴀɢᴇꜱ
/lock media - 📺 ʟᴏᴄᴋ ᴍᴇᴅɪᴀ (ᴘʜᴏᴛᴏ/ᴠɪᴅᴇᴏ/ꜱᴛɪᴄᴋᴇʀ/ɢɪꜰ/ᴅᴏᴄᴜᴍᴇɴᴛ)
/lock audio - 🎵 ʟᴏᴄᴋ ᴀᴜᴅɪᴏ
/lock voice - 🎙 ʟᴏᴄᴋ ᴠᴏɪᴄᴇ
/lock photo - 🖼 ʟᴏᴄᴋ ᴘʜᴏᴛᴏꜱ
/lock video - 🎥 ʟᴏᴄᴋ ᴠɪᴅᴇᴏꜱ
/lock sticker - ✨ ʟᴏᴄᴋ ꜱᴛɪᴄᴋᴇʀꜱ
/lock gif - 🎞 ʟᴏᴄᴋ ɢɪꜰꜱ
/lock document - 📄 ʟᴏᴄᴋ ꜰɪʟᴇꜱ
/lock url - 🔗 ʟᴏᴄᴋ ᴇxᴛᴇʀɴᴀʟ ʟɪɴᴋꜱ
/lock username - 👤 ʟᴏᴄᴋ ᴜꜱᴇʀɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴꜱ (@ᴜꜱᴇʀɴᴀᴍᴇ)
/lock forward - 🔄 ʟᴏᴄᴋ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ
/lock contact - 📇 ʟᴏᴄᴋ ᴄᴏɴᴛᴀᴄᴛꜱ
/lock location - 📍 ʟᴏᴄᴋ ʟᴏᴄᴀᴛɪᴏɴꜱ
/lock poll - 📊 ʟᴏᴄᴋ ᴘᴏʟʟꜱ
/lock bots - 🤖 ʟᴏᴄᴋ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ
/lock button - 🔘 ʟᴏᴄᴋ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴꜱ
/lock invite - 🔗 ʟᴏᴄᴋ ɪɴᴠɪᴛᴇ ʟɪɴᴋꜱ
/lock all - 🔐 ᴄᴏᴍᴘʟᴇᴛᴇʟʏ ʟᴏᴄᴋ ɢʀᴏᴜᴘ

✨ ʀᴏꜱᴇ ʙᴏᴛ ʟᴏᴄᴋꜱ (ɴᴇᴡ)
/lock album - 🖼 ʟᴏᴄᴋ ᴍᴇᴅɪᴀ ᴀʟʙᴜᴍꜱ
/lock anonchannel - 👤 ʟᴏᴄᴋ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴄʜᴀɴɴᴇʟ ᴍᴇꜱꜱᴀɢᴇꜱ
/lock audio - 🎵 ʟᴏᴄᴋ ᴀᴜᴅɪᴏ
/lock bot - 🤖 ʟᴏᴄᴋ ʙᴏᴛ ᴀᴅᴅɪᴛɪᴏɴ
/lock cashtag - 💰 ʟᴏᴄᴋ $TOKEN ʟɪᴋᴇ ᴄᴀsʜ
/lock checklist - ✅ ʟᴏᴄᴋ ᴄʜᴇᴄᴋʟɪꜱᴛꜱ
/lock cjk - 🇨🇳 ʟᴏᴄᴋ ᴄʜɪɴᴇꜱᴇ/ᴊᴀᴘᴀɴᴇꜱᴇ/ᴋᴏʀᴇᴀɴ
/lock command - ⚙️ ʟᴏᴄᴋ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ (/)
/lock comment - 💬 ʟᴏᴄᴋ ᴄʜᴀɴɴᴇʟ ᴄᴏᴍᴍᴇɴᴛꜱ
/lock cyrillic - 🇷🇺 ʟᴏᴄᴋ ʀᴜꜱꜱɪᴀɴ/ᴜᴋʀᴀɪɴɪᴀɴ
/lock email - 📧 ʟᴏᴄᴋ ᴇᴍᴀɪʟ ᴀᴅᴅʀᴇꜱꜱᴇꜱ
/lock emoji - 😀 ʟᴏᴄᴋ ᴀɴʏ ᴇᴍᴏᴊɪ
/lock emojicustom - 🌟 ʟᴏᴄᴋ ᴄᴜꜱᴛᴏᴍ ᴇᴍᴏᴊɪ
/lock emojigame - 🎲 ʟᴏᴄᴋ ᴅɪᴄᴇ/ɢᴀᴍᴇ ᴇᴍᴏᴊɪ
/lock emojionly - 😊 ʟᴏᴄᴋ ᴇᴍᴏᴊɪ-ᴏɴʟʏ ᴍᴇꜱꜱᴀɢᴇꜱ
/lock externalreply - ↩️ ʟᴏᴄᴋ ᴏᴜᴛꜱɪᴅᴇ ʀᴇᴘʟɪᴇꜱ
/lock forwarduser - 👤 ʟᴏᴄᴋ ꜰʀᴏᴍ ᴜꜱᴇʀꜱ
/lock forwardbot - 🤖 ʟᴏᴄᴋ ꜰʀᴏᴍ ʙᴏᴛꜱ
/lock forwardchannel - 📢 ʟᴏᴄᴋ ꜰʀᴏᴍ ᴄʜᴀɴɴᴇʟꜱ
/lock forwardstory - 📱 ʟᴏᴄᴋ ꜰʀᴏᴍ ꜱᴛᴏʀɪᴇꜱ
/lock game - 🕹️ ʟᴏᴄᴋ ᴛᴇʟᴇɢʀᴀᴍ ɢᴀᴍᴇꜱ
/lock guestbot - 👾 ʟᴏᴄᴋ ɢᴜᴇꜱᴛ ʙᴏᴛꜱ
/lock inline - ⚡ ʟᴏᴄᴋ ɪɴʟɪɴᴇ ʙᴏᴛꜱ
/lock invitelink - 🔗 ʟᴏᴄᴋ ᴛᴇʟᴇɢʀᴀᴍ ɪɴᴠɪᴛᴇꜱ
/lock botlink - 🤖 ʟᴏᴄᴋ ʙᴏᴛ ʟɪɴᴋꜱ
/lock outsidereaction - 🫥 ʟᴏᴄᴋ ᴏᴜᴛꜱɪᴅᴇʀ ʀᴇᴀᴄᴛɪᴏɴꜱ
/lock phone - 📞 ʟᴏᴄᴋ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀꜱ
/lock pin - 📌 ʟᴏᴄᴋ ᴘɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ
/lock reaction - 👍 ʟᴏᴄᴋ ʀᴇᴀᴄᴛɪᴏɴꜱ
/lock rtl - ↩️ ʟᴏᴄᴋ ᴀʀᴀʙɪᴄ/ʜᴇʙʀᴇᴡ
/lock spoiler - 🚫 ʟᴏᴄᴋ ꜱᴘᴏɪʟᴇʀꜱ
/lock stickeranimated - 🎬 ʟᴏᴄᴋ ᴀɴɪᴍᴀᴛᴇᴅ ꜱᴛɪᴄᴋᴇʀꜱ
/lock stickerpremium - 💎 ʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ ꜱᴛɪᴄᴋᴇʀꜱ
/lock videonote - 🎥 ʟᴏᴄᴋ ᴠɪᴅᴇᴏ ɴᴏᴛᴇꜱ
/lock zalgo - ⚠️ ʟᴏᴄᴋ ᴢᴀʟɢᴏ ᴛᴇxᴛ

✨ ꜱᴘᴇᴄɪᴀʟ ʟᴏᴄᴋꜱ
/lockall - 🔐 ᴄᴏᴍᴘʟᴇᴛᴇ ɢʀᴏᴜᴘ ʟᴏᴄᴋ

✨ ᴜɴʟᴏᴄᴋ ᴄᴏᴍᴍᴀɴᴅꜱ
/unlock <type> - 🔓 ᴜɴʟᴏᴄᴋ ꜱᴘᴇᴄɪꜰɪᴄ ᴛʏᴘᴇ
/unlock media - 🔓 ᴜɴʟᴏᴄᴋ ᴀʟʟ ᴍᴇᴅɪᴀ
/unlockall - 🔓 ꜰᴜʟʟʏ ᴜɴʟᴏᴄᴋ ɢʀᴏᴜᴘ

✨ ʟᴏᴄᴋ ɪɴꜰᴏ
/locks - 📌 ꜱᴇᴇ ᴀᴄᴛɪᴠᴇ ʟᴏᴄᴋꜱ
/lockstatus - 📊 ꜰᴜʟʟ ʟᴏᴄᴋ ꜱᴛᴀᴛᴜꜱ
/locktypes - 📋 ꜱᴇᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʟᴏᴄᴋꜱ

✨ ꜱɪʟᴇɴᴛ ᴍᴏᴅᴇ
/locksilent on - 🔕 ɴᴏ ᴡᴀʀɴɪɴɢꜱ (ᴏɴʟʏ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ)
/locksilent off - 🔔 ꜱʜᴏᴡ ᴡᴀʀɴɪɴɢ

✨ ᴀᴅᴍɪɴ-ᴏɴʟʏ ᴄᴏɴᴛʀᴏʟ
/lockadmin on - 🔑 ᴀᴜᴛᴏ ʟᴏᴄᴋ ᴀʟʟ ᴍᴇᴅɪᴀ + ᴀᴅᴍɪɴꜱ ᴀʟꜱᴏ ʟᴏᴄᴋᴇᴅ
/lockadmin off - 🔓 ᴏɴʟʏ ᴍᴇᴍʙᴇʀꜱ ᴀꜰꜰᴇᴄᴛᴇᴅ

👑 ʙᴏᴛ ᴏᴡɴᴇʀ & ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ: ɴᴇᴠᴇʀ ᴅᴇʟᴇᴛᴇᴅ
👥 ᴀᴅᴍɪɴꜱ: ʀᴇꜱᴘᴇᴄᴛ ʟᴏᴄᴋᴀᴅᴍɪɴ ꜱᴇᴛᴛɪɴɢ
👤 ᴍᴇᴍʙᴇʀꜱ: ᴀʟᴡᴀʏꜱ ᴀꜰꜰᴇᴄᴛᴇᴅ ʙʏ ʟᴏᴄᴋꜱ
"""

    await message.reply_text(text)
