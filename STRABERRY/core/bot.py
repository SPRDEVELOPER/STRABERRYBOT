import sys
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from ..logging import LOGGER


class RAJ(Client):
    def __init__(self):
        super().__init__(
            name="StraberryTunesBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            workers=48,
            max_concurrent_transmissions=7,
        )
        LOGGER(__name__).info("Bot client initialized.")

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username, self.id = me.username, me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.mention = me.mention

        try:
            await self.send_message(
                config.LOGGER_ID,
                f"» {self.name} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ\n\nɪᴅ : {self.id}\nɴᴀᴍᴇ : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except Exception:
            LOGGER(__name__).warning("⚠️ Could not send start msg to log group, continuing anyway...")

        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).warning("⚠️ Bot is not admin in log group.")
        except Exception:
            pass

        LOGGER(__name__).info(f"✅ Music Bot started as {self.name} (@{self.username})")
