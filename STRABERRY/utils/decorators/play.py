import asyncio
import re  # Added for security check

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteHashExpired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist, MAX_USER_PLAY_LIMIT
from strings import get_string
from STRABERRY import YouTube, app
from STRABERRY.misc import SUDOERS, db
from STRABERRY.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from STRABERRY.utils.inline import botplaylist_markup

# Security function to validate YouTube URLs
def is_safe_youtube_url(url: str) -> bool:
    if not url:
        return True
    if any(x in url for x in [";", "&", "|", "$", "`"]):
        return False
    pattern = r"^https:\/\/(www\.)?(youtube\.com|youtu\.be)\/"
    return bool(re.match(pattern, url))

# Cache for invite links per chat
links = {}

# NEW: User-wise queue limit storage
USER_QUEUE = {}   # USER_QUEUE[chat_id][user_id] = count


def PlayWrapper(command):
    async def wrapper(client, message):

        chat_id = message.chat.id
        user_id = message.from_user.id
        language = await get_lang(chat_id)
        _ = get_string(language)

        # ------------------ AUTO DELETE ALWAYS FIRST ------------------
        try:
            await message.delete()
        except Exception:
            pass
        # --------------------------------------------------------------

        # ---------- INIT USER QUEUE STRUCTURE ----------
        if chat_id not in USER_QUEUE:
            USER_QUEUE[chat_id] = {}

        if user_id not in USER_QUEUE[chat_id]:
            USER_QUEUE[chat_id][user_id] = 0
        # -------------------------------------------------

        # -------- AUTO RESET WHEN QUEUE IS EMPTY --------
        queue = db.get(chat_id)
        if not queue:
            USER_QUEUE[chat_id] = {}
            USER_QUEUE[chat_id][user_id] = 0
        # -------------------------------------------------

        # ------------ LIMIT CHECK FOR NON-SUDO -----------
        if user_id not in SUDOERS:
            if USER_QUEUE[chat_id][user_id] >= MAX_USER_PLAY_LIMIT:
                return await message.reply_text(
                    "ʏᴏᴜ ᴄᴀɴ'ᴛ ᴀᴅᴅ ᴍᴏʀᴇ ᴛʜᴀɴ 𝟣𝟢 ꜱᴏɴɢꜱ ᴛᴏ ᴛʜᴇ ǫᴜᴇᴜᴇ, ʙᴀʙʏ 💞"
                )
        # -------------------------------------------------

        # -------------------- ORIGINAL CODE ----------------------
        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if await is_maintenance() is False:
            if user_id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a>",
                    disable_web_page_preview=True,
                )

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message else None
        )
        url = await YouTube.url(message)

        # 🔒 SECURITY CHECK - Validate YouTube URL
        if url and not is_safe_youtube_url(url):
            return await message.reply_text(
                "🚨 ꜱᴇᴄᴜʀɪᴛʏ ᴀʟᴇʀᴛ 💔\n\n"
                "⚠️ ꜱᴜꜱᴘɪᴄɪᴏᴜꜱ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ...\n"
                "❌ ᴛʜɪꜱ ᴛʏᴘᴇ ᴏꜰ ʟɪɴᴋ ɪꜱ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ\n\n"
                "🎧 ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴏɴʟʏ ᴠᴀʟɪᴅ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋꜱ, ʙᴀʙʏ 💞"
            )

        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL, caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )

        # -------------------- CHANNEL PLAY ---------------------
        if message.command[0][0] == "c":
            c_id = await get_cmode(chat_id)
            if c_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat_info = await app.get_chat(c_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])
            channel = chat_info.title
            chat_for_play = c_id
        else:
            channel = None
            chat_for_play = chat_id
        # --------------------------------------------------------

        # ---------------- ADMIN-ONLY PLAY -----------------------
        playmode = await get_playmode(chat_id)
        playty = await get_playtype(chat_id)
        if playty != "Everyone":
            if user_id not in SUDOERS:
                admins = adminlist.get(chat_id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                elif user_id not in admins:
                    return await message.reply_text(_["play_4"])
        # --------------------------------------------------------

        # ⭐⭐⭐ 100% FIXED VIDEO DETECTION ⭐⭐⭐
        cmd = message.command[0].lower()

        if cmd.startswith("v") or "-v" in message.text:
            video = True
        else:
            video = None
        # --------------------------------------------------------

        # --------------- FORCE PLAY ---------------------
        fplay = True if message.command[0].endswith("e") else None
        # ------------------------------------------------

        # --------------- CHECK ASSISTANT IN VC ----------
        if not await is_active_chat(chat_for_play):
            userbot = await get_assistant(chat_for_play)
            try:
                try:
                    member = await app.get_chat_member(chat_for_play, userbot.id)
                except ChatAdminRequired:
                    return await message.reply_text(_["call_1"])

                if member.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):
                    return await message.reply_text(
                        _["call_2"].format(app.mention, userbot.id, userbot.name, userbot.username)
                    )
            except UserNotParticipant:

                if chat_for_play in links:
                    invitelink = links[chat_for_play]
                else:
                    if message.chat.username:
                        invitelink = message.chat.username
                        try: await userbot.resolve_peer(invitelink)
                        except Exception: pass
                    else:
                        try:
                            invitelink = await app.export_chat_invite_link(chat_for_play)
                        except Exception as e:
                            return await message.reply_text(
                                _["call_3"].format(app.mention, type(e).__name__)
                            )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")

                msg2 = await message.reply_text(_["call_4"].format(app.mention))

                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)

                except InviteHashExpired:

                    if chat_for_play in links:
                        del links[chat_for_play]

                    try:
                        invitelink = await app.export_chat_invite_link(chat_for_play)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )

                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")

                    links[chat_for_play] = invitelink
                    await userbot.join_chat(invitelink)

                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_for_play, userbot.id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    await asyncio.sleep(3)
                    await msg2.edit(_["call_5"].format(app.mention))

                except UserAlreadyParticipant:
                    pass

        # ---------------- ADD USER QUEUE COUNT -------------------
        if user_id not in SUDOERS:

            # 💯 KeyError FIX
            if chat_id not in USER_QUEUE:
                USER_QUEUE[chat_id] = {}

            if user_id not in USER_QUEUE[chat_id]:
                USER_QUEUE[chat_id][user_id] = 0

            USER_QUEUE[chat_id][user_id] += 1
        # ---------------------------------------------------------

        return await command(
            client,
            message,
            _,
            chat_for_play,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
