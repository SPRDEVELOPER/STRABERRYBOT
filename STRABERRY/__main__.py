import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from STRABERRY import LOGGER, app, userbot
from STRABERRY.core.call import RAJ
from STRABERRY.misc import sudo
from STRABERRY.plugins import ALL_MODULES
from STRABERRY.utils.database import get_banned_users, get_gbanned
from STRABERRY.utils.cookie_handler import fetch_and_store_cookies
from config import BANNED_USERS

#from STRABERRY.plugins.tools.vclogger import initialize_vc_logger


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ sᴇssɪᴏɴ ɴᴏᴛ ғɪʟʟᴇᴅ, ᴘʟᴇᴀsᴇ ғɪʟʟ ᴀ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ...")
        exit()

    # Try to fetch cookies at startup
    try:
        await fetch_and_store_cookies()
        LOGGER("STRABERRY").info(
            "ʏᴏᴜᴛᴜʙᴇ ᴄᴏᴏᴋɪᴇs ʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅"
        )
    except Exception as e:
        LOGGER("STRABERRY").warning(f"⚠️ᴄᴏᴏᴋɪᴇ ᴇʀʀᴏʀ: {e}")

    # ❌ VC LOGGER AUTO RESTORE DISABLED
    # await initialize_vc_logger()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()

    # Set bot menu commands
    try:
        from pyrogram.raw.types import BotCommand
        commands = []
        for cmd, desc in [
            ("start", "sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
            ("help", "ɢᴇᴛ ʜᴇʟᴘ ᴍᴇɴᴜ"),
            ("play", "ᴘʟᴀʏ ᴀ ꜱᴏɴɢ ɪɴ ᴠᴄ"),
            ("vplay", "ᴘʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴄ"),
            ("stop", "ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍɪɴɢ"),
            ("pause", "ᴘᴀᴜꜱᴇ ᴛʜᴇ ꜱᴛʀᴇᴀᴍ"),
            ("resume", "ʀᴇꜱᴜᴍᴇ ᴛʜᴇ ꜱᴛʀᴇᴀᴍ"),
            ("skip", "ꜱᴋɪᴘ ᴛᴏ ɴᴇxᴛ ꜱᴏɴɢ"),
            ("queue", "ꜱʜᴏᴡ ǫᴜᴇᴜᴇ ʟɪꜱᴛ"),
            ("loop", "ʟᴏᴏᴘ ᴄᴜʀʀᴇɴᴛ ꜱᴏɴɢ"),
            ("shuffle", "ꜱʜᴜꜰꜰʟᴇ ᴛʜᴇ ǫᴜᴇᴜᴇ"),
            ("seek", "ꜱᴇᴇᴋ ɪɴ ᴄᴜʀʀᴇɴᴛ ꜱᴏɴɢ"),
            ("speed", "ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ ꜱᴘᴇᴇᴅ"),
            ("song", "ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴏɴɢ"),
            ("lock", "ʟᴏᴄᴋ ᴀ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇ"),
            ("unlock", "ᴜɴʟᴏᴄᴋ ᴀ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇ"),
            ("lockhelp", "ʟᴏᴄᴋ ꜱʏꜱᴛᴇᴍ ʜᴇʟᴘ"),
            ("filter", "ᴀᴅᴅ ᴀ ꜰɪʟᴛᴇʀ"),
            ("filters", "ʟɪꜱᴛ ᴀʟʟ ꜰɪʟᴛᴇʀꜱ"),
            ("warn", "ᴡᴀʀɴ ᴀ ᴜꜱᴇʀ"),
            ("ban", "ʙᴀɴ ᴀ ᴜꜱᴇʀ"),
            ("mute", "ᴍᴜᴛᴇ ᴀ ᴜꜱᴇʀ"),
            ("kick", "ᴋɪᴄᴋ ᴀ ᴜꜱᴇʀ"),
            ("promote", "ᴘʀᴏᴍᴏᴛᴇ ᴀ ᴜꜱᴇʀ"),
            ("settings", "ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ ᴘᴀɴᴇʟ"),
            ("reload", "ʀᴇꜰʀᴇꜱʜ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ"),
            ("ping", "ᴄʜᴇᴄᴋ ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ"),
            ("bwhelp", "ʙʟᴀᴄᴋʟɪꜱᴛ ᴡᴏʀᴅ ʜᴇʟᴘ"),
        ]:
            commands.append(BotCommand(command=cmd, description=desc))
        from pyrogram.raw.functions.bots import SetBotCommands
        from pyrogram.raw.types import BotCommandScopeDefault
        await app.invoke(SetBotCommands(scope=BotCommandScopeDefault(), lang_code="", commands=commands))
    except Exception:
        pass

    for all_module in ALL_MODULES:
        importlib.import_module("STRABERRY.plugins" + all_module)

    LOGGER("STRABERRY.plugins").info("ᴀɴɴɪᴇ's ᴍᴏᴅᴜʟᴇs ʟᴏᴀᴅᴇᴅ...")

    await userbot.start()
    await RAJ.start()

    try:
        await RAJ.stream_call("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")
    except NoActiveGroupCall:
        LOGGER("STRABERRY").error(
            "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\nᴀɴɴɪᴇ ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ..."
        )
        exit()
    except:
        pass

    await RAJ.decorators()
    LOGGER("STRABERRY").info(
        "\x41\x6e\x6e\x69\x65\x20\x4d\x75\x73\x69\x63\x20\x52\x6f\x62\x6f\x74\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x2e\x2e"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("STRABERRY").info("sᴛᴏᴘᴘɪɴɢ ᴀɴɴɪᴇ ᴍᴜsɪᴄ ʙᴏᴛ ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
