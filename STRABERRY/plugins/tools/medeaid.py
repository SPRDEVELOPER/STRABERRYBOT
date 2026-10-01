from pyrogram import filters
from pyrogram.types import Message

from STRABERRY import app


@app.on_message(filters.command(["mediaid", "fileid"]))
async def media_id(_, message: Message):

    if not message.reply_to_message:
        return await message.reply_text(
            "⦿ ᴍᴇᴅɪᴀ ɪᴅ ғɪɴᴅᴇʀ\n\n"
            "⦿ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, ᴀᴜᴅɪᴏ,\n"
            "   ᴠᴏɪᴄᴇ, ɢɪꜰ, sᴛɪᴄᴋᴇʀ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ.\n\n"
            "⦿ ᴇxᴀᴍᴘʟᴇ :\n"
            "1. ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ\n"
            "2. sᴇɴᴅ /mediaid"
        )

    replied = message.reply_to_message

    if replied.photo:
        return await message.reply_text(
            f"⦿ ᴘʜᴏᴛᴏ ɪᴅ\n\n<code>{replied.photo.file_id}</code>"
        )

    if replied.video:
        return await message.reply_text(
            f"⦿ ᴠɪᴅᴇᴏ ɪᴅ\n\n<code>{replied.video.file_id}</code>"
        )

    if replied.audio:
        return await message.reply_text(
            f"⦿ ᴀᴜᴅɪᴏ ɪᴅ\n\n<code>{replied.audio.file_id}</code>"
        )

    if replied.voice:
        return await message.reply_text(
            f"⦿ ᴠᴏɪᴄᴇ ɪᴅ\n\n<code>{replied.voice.file_id}</code>"
        )

    if replied.document:
        return await message.reply_text(
            f"⦿ ᴅᴏᴄᴜᴍᴇɴᴛ ɪᴅ\n\n<code>{replied.document.file_id}</code>"
        )

    if replied.animation:
        return await message.reply_text(
            f"⦿ ɢɪꜰ ɪᴅ\n\n<code>{replied.animation.file_id}</code>"
        )

    if replied.sticker:
        return await message.reply_text(
            f"⦿ sᴛɪᴄᴋᴇʀ ɪᴅ\n\n<code>{replied.sticker.file_id}</code>"
        )

    return await message.reply_text(
        "⦿ ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ."
    )
