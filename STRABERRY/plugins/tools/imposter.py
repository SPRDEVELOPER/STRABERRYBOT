from pyrogram import filters
from pyrogram.types import Message
from STRABERRY import app
from STRABERRY.mongo.pretenderdb import (
    impo_off, impo_on, check_pretender,
    add_userdata, get_userdata, usr_data
)
from STRABERRY.utils.admin_filters import admin_filter

# --------------------------------------------------------------------------
# ✔ FIXED: Pretender detection → group=1 
# (ताकि यह commands को block न करे)
# --------------------------------------------------------------------------
@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=1)
async def chk_usr(_, message: Message):

    if message.sender_chat or not await check_pretender(message.chat.id):
        return

    if not await usr_data(message.from_user.id):
        return await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

    usernamebefore, first_name, lastname_before = await get_userdata(message.from_user.id)
    msg = ""

    if (
        usernamebefore != message.from_user.username
        or first_name != message.from_user.first_name
        or lastname_before != message.from_user.last_name
    ):
        msg += f"""
**🔓 ᴘʀᴇᴛᴇɴᴅᴇʀ ᴅᴇᴛᴇᴄᴛᴇᴅ 🔓**
━━━━━━━━━━━━━━━  
**🍊 ɴᴀᴍᴇ** : {message.from_user.mention}
**🍅 ᴜsᴇʀ ɪᴅ** : {message.from_user.id}
━━━━━━━━━━━━━━━  
"""

    # USERNAME CHANGE
    if usernamebefore != message.from_user.username:
        usernamebefore = f"@{usernamebefore}" if usernamebefore else "NO USERNAME"
        usernameafter = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "NO USERNAME"
        )

        msg += f"""
**🐻‍❄️ ᴄʜᴀɴɢᴇᴅ ᴜsᴇʀɴᴀᴍᴇ 🐻‍❄️**
━━━━━━━━━━━━━━━  
**🎭 ғʀᴏᴍ** : {usernamebefore}
**🍜 ᴛᴏ** : {usernameafter}
━━━━━━━━━━━━━━━  
"""

        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

    # FIRST NAME CHANGE
    if first_name != message.from_user.first_name:
        msg += f"""
**🪧 ᴄʜᴀɴɢᴇᴅ ғɪʀsᴛ ɴᴀᴍᴇ 🪧**
━━━━━━━━━━━━━━━  
**🔐 ғʀᴏᴍ** : {first_name}
**🍓 ᴛᴏ** : {message.from_user.first_name}
━━━━━━━━━━━━━━━  
"""

        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

    # LAST NAME CHANGE
    if lastname_before != message.from_user.last_name:
        lastname_before = lastname_before or "NO LAST NAME"
        lastname_after = message.from_user.last_name or "NO LAST NAME"

        msg += f"""
**🪧 ᴄʜᴀɴɢᴇᴅ ʟᴀsᴛ ɴᴀᴍᴇ 🪧**
━━━━━━━━━━━━━━━  
**🚏 ғʀᴏᴍ** : {lastname_before}
**🍕 ᴛᴏ** : {lastname_after}
━━━━━━━━━━━━━━━  
"""

        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )

    if msg != "":
        await message.reply_photo(
            "https://telegra.ph/file/58afe55fee5ae99d6901b.jpg",
            caption=msg
        )


# --------------------------------------------------------------------------
# ✔ FIXED: Imposter admin command → group=0 
# (ताकि यह हमेशा पहले reply करे)
# --------------------------------------------------------------------------
@app.on_message(filters.group & filters.command("imposter") & ~filters.bot & ~filters.via_bot & admin_filter, group=0)
async def set_mataa(_, message: Message):

    if len(message.command) == 1:
        return await message.reply(
            "ᴅᴇᴛᴇᴄᴛ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴜsᴇʀs **ᴜsᴀɢᴇ:** `/imposter enable|disable`"
        )

    cmd = message.command[1].lower()

    # ENABLE
    if cmd == "enable":
        cekset = await impo_on(message.chat.id)
        if cekset:
            return await message.reply("**ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
        return await message.reply(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ғᴏʀ** {message.chat.title}")

    # DISABLE
    elif cmd == "disable":
        cekset = await impo_off(message.chat.id)
        if not cekset:
            return await message.reply("**ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")
        return await message.reply(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴅɪsᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ғᴏʀ** {message.chat.title}")

    else:
        return await message.reply("**ᴏɴʟʏ: /imposter enable OR disable**")
