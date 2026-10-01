from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from pyrogram.enums import ChatMemberStatus

from STRABERRY import app
from STRABERRY.core.mongo import mongodb

thumbdb = mongodb.thumbnail_settings


# ===== GET / SET =====
async def get_thumb_status(chat_id: int) -> bool:
    """Returns True if thumbnail is enabled (default), False if disabled."""
    data = await thumbdb.find_one({"chat_id": chat_id})
    if data is None:
        return True  # Default: enabled
    return data.get("status", True)


async def set_thumb_status(chat_id: int, status: bool):
    await thumbdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": status}},
        upsert=True,
    )


# ===== ADMIN CHECK =====
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ]
    except:
        return False


# ===== BUTTONS =====
def thumb_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ᴇɴᴀʙʟᴇ", callback_data="thumb_enable"),
                InlineKeyboardButton("ᴅɪꜱᴀʙʟᴇ", callback_data="thumb_disable"),
            ],
            [
                InlineKeyboardButton("ᴄʟᴏꜱᴇ ☒", callback_data="thumb_close")
            ],
        ]
    )


THUMB_TEXT_ON = """
🌀 <b>ᴛʜᴜᴍʙɴᴀɪʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>

<b>ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: ᴇɴᴀʙʟᴇᴅ ✅</b>

ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴛʜᴜᴍʙɴᴀɪʟꜱ.
"""

THUMB_TEXT_OFF = """
🌀 <b>ᴛʜᴜᴍʙɴᴀɪʟ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>

<b>ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ: ᴅɪꜱᴀʙʟᴇᴅ ❌</b>

ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛʀᴏʟ ᴛʜᴜᴍʙɴᴀɪʟꜱ.
"""


# ===== /thumb COMMAND =====
@app.on_message(filters.command("thumb") & filters.group)
async def thumb_cmd(_, message: Message):
    chat_id = message.chat.id
    status = await get_thumb_status(chat_id)
    text = THUMB_TEXT_ON if status else THUMB_TEXT_OFF

    await message.reply_text(
        text,
        reply_markup=thumb_buttons(),
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("thumb") & filters.private)
async def thumb_private(_, message: Message):
    await message.reply_text("⚠️ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜꜱᴇᴅ ɪɴ ɢʀᴏᴜᴘꜱ.")


# ===== CALLBACKS =====
@app.on_callback_query(filters.regex("^thumb_enable$"))
async def thumb_enable_cb(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if not await is_admin(chat_id, user_id):
        return await query.answer("⚠️ ᴀᴅᴍɪɴ ᴏɴʟʏ", show_alert=True)

    await set_thumb_status(chat_id, True)

    try:
        await query.message.edit_text(
            THUMB_TEXT_ON,
            reply_markup=thumb_buttons(),
        )
    except:
        pass

    await query.answer("✅ ᴛʜᴜᴍʙɴᴀɪʟ ᴇɴᴀʙʟᴇᴅ", show_alert=True)


@app.on_callback_query(filters.regex("^thumb_disable$"))
async def thumb_disable_cb(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if not await is_admin(chat_id, user_id):
        return await query.answer("⚠️ ᴀᴅᴍɪɴ ᴏɴʟʏ", show_alert=True)

    await set_thumb_status(chat_id, False)

    try:
        await query.message.edit_text(
            THUMB_TEXT_OFF,
            reply_markup=thumb_buttons(),
        )
    except:
        pass

    await query.answer("❌ ᴛʜᴜᴍʙɴᴀɪʟ ᴅɪꜱᴀʙʟᴇᴅ", show_alert=True)


@app.on_callback_query(filters.regex("^thumb_close$"))
async def thumb_close_cb(_, query: CallbackQuery):
    try:
        await query.answer()
        await query.message.delete()
    except:
        pass
