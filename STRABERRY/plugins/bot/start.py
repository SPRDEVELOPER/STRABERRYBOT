import time
import asyncio
import random
import requests
import re
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from STRABERRY import app
from STRABERRY.misc import _boot_
from STRABERRY.plugins.sudo.sudoers import sudoers_list
from STRABERRY.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from STRABERRY.utils.decorators.language import LanguageStart
from STRABERRY.utils.formatters import get_readable_time
from STRABERRY.utils.inline.help import first_page
from STRABERRY.utils.inline.start import private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

REACTIONS = ["❤️", "🔥", "🥰", "😍", "😘", "👌", "👏", "🎉", "✨", "⭐️", "🌈", "🎵", "🎶", "💝", "💖", "💗", "💓", "💞", "💕", "💋"]

# 💖 ONLY WORKING HEART EFFECT IDs
HEART_EFFECTS = [
    "5159385139981059251"
]

FALLBACK_EFFECTS = ["💖", "❤️", "💗", "💓", "💞", "💕", "💝"]

async def delete_message_after_delay(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

async def send_heart_effect_private(chat_id: int, retries: int = 5):
    """Sirf Private chat ke liye heart effect"""
    for attempt in range(retries):
        try:
            effect_id = random.choice(HEART_EFFECTS)
            emoji = random.choice(FALLBACK_EFFECTS)
            
            response = requests.post(
                f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": emoji,
                    "message_effect_id": effect_id,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    message_id = data.get("result", {}).get("message_id")
                    if message_id:
                        asyncio.create_task(delete_effect_message(chat_id, message_id))
                        return True
            await asyncio.sleep(0.5)
        except Exception as e:
            await asyncio.sleep(0.5)
    
    # Fallback: Sirf emoji bhejo
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "💖",
            },
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                message_id = data.get("result", {}).get("message_id")
                if message_id:
                    asyncio.create_task(delete_effect_message(chat_id, message_id))
    except:
        pass
    return False

async def send_heart_effect_group(chat_id: int):
    """Group ke liye sirf emoji bhejo (effect allowed nahi hai)"""
    try:
        emoji = random.choice(FALLBACK_EFFECTS)
        response = requests.post(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": emoji,
            },
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                message_id = data.get("result", {}).get("message_id")
                if message_id:
                    asyncio.create_task(delete_effect_message(chat_id, message_id))
                    return True
    except Exception as e:
        pass
    return False

async def delete_effect_message(chat_id: int, message_id: int):
    await asyncio.sleep(2)
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteMessage",
            json={
                "chat_id": chat_id,
                "message_id": message_id
            },
            timeout=5,
        )
    except Exception as e:
        pass

async def get_video_info(video_id: str):
    """Fetch video info with proper title handling"""
    try:
        query = f"https://www.youtube.com/watch?v={video_id}"
        results = VideosSearch(query, limit=1)
        result = (await results.next())["result"][0]
        
        # Get title - agar URL hai toh fix karo
        title = result.get("title", "Unknown Title")
        
        # Agar title mein "http" hai toh actual title fetch karo
        if title.startswith("http"):
            # Dobara search karo with different query
            new_results = VideosSearch(video_id, limit=1)
            new_result = (await new_results.next())["result"][0]
            title = new_result.get("title", "Unknown Title")
            
            # Agar phir bhi URL hai toh video ID se title fetch karo
            if title.startswith("http"):
                # YouTube video page se title extract karo
                try:
                    response = requests.get(f"https://www.youtube.com/watch?v={video_id}", timeout=10)
                    html = response.text
                    title_match = re.search(r'<title>(.*?)</title>', html)
                    if title_match:
                        title = title_match.group(1).replace(" - YouTube", "")
                except:
                    title = "Unknown Title"
        
        duration = result.get("duration", "Unknown")
        views = result.get("viewCount", {}).get("short", "0")
        thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
        channellink = result["channel"].get("link", "https://youtube.com")
        channel = result["channel"].get("name", "YouTube Channel")
        link = result.get("link", f"https://youtu.be/{video_id}")
        published = result.get("publishedTime", "Unknown")
        
        return {
            "title": title,
            "duration": duration,
            "views": views,
            "thumbnail": thumbnail,
            "channellink": channellink,
            "channel": channel,
            "link": link,
            "published": published
        }
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return None

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await add_served_user(message.from_user.id)
    except:
        pass
    
    # Reaction
    try:
        await message.react(random.choice(REACTIONS))
    except:
        pass
    
    # 💖 PRIVATE - Heart effect with bubbles
    await send_heart_effect_private(message.chat.id)
    
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = first_page(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴜsᴇᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            video_id = (str(name)).replace("info_", "", 1)
            
            # Fetch video info with proper title
            info = await get_video_info(video_id)
            
            if not info:
                await m.edit_text("❌ Failed to fetch video information. Please try again.")
                return
            
            # 🔥 en.yml se caption aayega
            searched_text = _["start_6"].format(
                info['title'],           # {0} - TITLE
                info['duration'],        # {1} - DURATION
                info['views'],           # {2} - VIEWS
                info['published'],       # {3} - PUBLISHED ON
                info['channellink'],     # {4} - CHANNEL LINK (href)
                info['channel'],         # {5} - CHANNEL NAME
                app.mention              # {6} - BOT NAME
            )
            
            # 🔥 Buttons bhi en.yml se aayenge
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_6"], url=info['link']),
                        InlineKeyboardButton(text=_["S_B_4"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=info['thumbnail'],
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴜsᴇᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
    else:
        try:
            # ========== WELCOME ANIMATION (Sirf Private) ==========
            welcome_msgs = [
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. ⚣",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. 🥳",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. 💥",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. 🤩",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. 💌",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁ᴀʙʏ ꨄ {}.. 💞",
            ]
            lol = await message.reply_text(welcome_msgs[0].format(message.from_user.mention))
            for msg in welcome_msgs[1:]:
                await asyncio.sleep(0.3)
                await lol.edit_text(msg.format(message.from_user.mention))
            await asyncio.sleep(1.5)
            await lol.delete()
            
            # ========== STARTING ANIMATION (Sirf Private) ==========
            start_msgs = [
                "**⚡️ѕ**",
                "⚡ѕт",
                "**⚡ѕтα**",
                "**⚡ѕтαя**",
                "**⚡ѕтαят**",
                "**⚡ѕтαятι**",
                "**⚡ѕтαятιи**",
                "**⚡ѕтαятιиg**",
                "**⚡ѕтαятιиg.**",
                "**⚡ѕтαятιиg....**",
                "**⚡ѕтαятιиg.**",
                "**⚡ѕтαятιиg....**",
            ]
            lols = await message.reply_text(start_msgs[0])
            for msg in start_msgs[1:]:
                await asyncio.sleep(0.2)
                await lols.edit_text(msg)
            await asyncio.sleep(1.5)
            await lols.delete()
            # ===================================================
            
            if message.from_user.photo:
                userss_photo = await app.download_media(message.from_user.photo.big_file_id)
            else:
                userss_photo = "assets/nodp.png"
        except:
            userss_photo = "assets/nodp.png"
            
        chat_photo = userss_photo if userss_photo != "assets/nodp.png" else config.START_IMG_URL
        out = private_panel(_)
        
        await message.reply_photo(
            photo=chat_photo,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        
        if await is_on_off(2):
            username = f"@{message.from_user.username}" if message.from_user.username else "None"
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴜsᴇᴅ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    # Reaction for group
    try:
        await message.react(random.choice(REACTIONS))
    except:
        pass
    
    # 💖 GROUP - Sirf emoji
    await send_heart_effect_group(message.chat.id)
    
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    try:
        if message.from_user and message.from_user.photo:
            userss_photo = await app.download_media(message.from_user.photo.big_file_id)
        else:
            userss_photo = "assets/nodp.png"
    except:
        userss_photo = "assets/nodp.png"
    
    chat_photo = userss_photo if userss_photo != "assets/nodp.png" else config.START_IMG_URL
    
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    
    await message.reply_photo(
        photo=chat_photo,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
                    
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                # 💖 WELCOME - Sirf emoji
                await send_heart_effect_group(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except:
            pass
