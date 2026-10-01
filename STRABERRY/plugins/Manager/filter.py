import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from STRABERRY import app
from STRABERRY.core.mongo import mongodb

filtersdb = mongodb["filters"]
warndb = mongodb["warns"]

# ---------------- STYLE (FIXED FONTS) ---------------- #
MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)

def sc(t: str):
    return t.lower().translate(MAP)

# ---------------- ADMIN CHECK ---------------- #
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
        return False
    except:
        return False

# ---------------- BOT PERMISSION CHECK ---------------- #
async def check_bot_permission(client, chat_id, action="ban"):
    try:
        bot = await client.get_chat_member(chat_id, (await client.get_me()).id)
        
        if bot.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return False, f"❌ {sc('bot is not admin')}\n\n{sc('please make me admin with all permissions')}"
        
        if action == "ban":
            if not bot.privileges.can_restrict_members:
                return False, f"❌ {sc('bot needs permission')}: {sc('ban members')}"
        
        return True, "ok"
    except:
        return False, f"❌ {sc('bot is not admin')}"

# ---------------- ADD FILTER ---------------- #
@app.on_message(filters.command("filter") & (filters.group | filters.private))
async def add_filter(client, m: Message):

    try:
        if m.chat.type == "private":
            return await m.reply_text(f"❌ {sc('this command only works in groups')}")

        if not await is_admin(client, m.chat.id, m.from_user.id):
            return await m.reply_text(f"❌ {sc('only admin can use this')}")

        if len(m.command) < 2:
            return await m.reply_text(f"⚠️ {sc('give filter name')}")

        key = m.command[1].lower()
        data = {"key": key}

        # reply system
        if m.reply_to_message:
            r = m.reply_to_message

            # Get text from text or caption
            msg_text = r.text or r.caption or ""
            
            if msg_text:
                # 🔥 Check for custom/premium emoji in entities
                entities = r.entities or r.caption_entities or []
                has_custom_emoji = False
                
                for entity in entities:
                    if hasattr(entity, "custom_emoji_id") and entity.custom_emoji_id:
                        has_custom_emoji = True
                        break
                
                if has_custom_emoji:
                    # 🔥 Store original message reference directly
                    # Don't copy/forward - it strips premium emoji for non-premium bots
                    data["text"] = msg_text
                    data["has_premium_emoji"] = True
                    data["premium_msg_chat"] = r.chat.id
                    data["premium_msg_id"] = r.id
                else:
                    data["text"] = msg_text

            # 🔥 ALL MEDIA SUPPORT (photo with caption = save both file + text)
            if r.photo:
                data["file"] = r.photo.file_id
                if r.caption and "text" not in data:
                    data["text"] = r.caption
            elif r.video:
                data["file"] = r.video.file_id
                if r.caption and "text" not in data:
                    data["text"] = r.caption
            elif r.document:
                data["file"] = r.document.file_id
            elif r.sticker:
                data["file"] = r.sticker.file_id
            elif r.audio:
                data["file"] = r.audio.file_id
            elif r.voice:
                data["file"] = r.voice.file_id
            elif r.animation:
                data["file"] = r.animation.file_id

        # inline system
        elif len(m.command) > 2:
            text = " ".join(m.command[2:])
            
            # Check if the original message has premium/custom emoji entities
            entities = m.entities or []
            has_custom_emoji = False
            for entity in entities:
                if hasattr(entity, "custom_emoji_id") and entity.custom_emoji_id:
                    has_custom_emoji = True
                    break
            
            if has_custom_emoji:
                # Store original message reference (preserves premium emoji)
                data["text"] = text
                data["has_premium_emoji"] = True
                data["premium_msg_chat"] = m.chat.id
                data["premium_msg_id"] = m.id
            else:
                data["text"] = text

        else:
            return await m.reply_text(f"⚠️ {sc('reply or use')} /filter key text")

        await filtersdb.update_one(
            {"chat_id": m.chat.id, "key": key},
            {"$set": {"key": key, **data}},
            upsert=True
        )

        emoji_note = " (Premium emoji enabled ✨)" if data.get("has_premium_emoji") else ""
        await m.reply_text(f"✅ {sc('filter')} `{key}` {sc('saved')}{emoji_note}")

    except Exception as e:
        await m.reply_text(f"❌ {sc('error')}: `{str(e)}`")


# ---------------- STOP FILTER ---------------- #
@app.on_message(filters.command("stop") & (filters.group | filters.private))
async def stop_filter(client, m: Message):

    try:
        if m.chat.type == "private":
            return await m.reply_text(f"❌ {sc('this command only works in groups')}")

        if not await is_admin(client, m.chat.id, m.from_user.id):
            return await m.reply_text(f"❌ {sc('only admin can use this')}")

        if len(m.command) < 2:
            return await m.reply_text(f"⚠️ {sc('give filter name')}")

        key = m.command[1].lower()

        data = await filtersdb.find_one({
            "chat_id": m.chat.id,
            "$or": [{"key": key}, {"keyword": key}]
        })

        if not data:
            return await m.reply_text(f"❌ {sc('filter not found')}")

        await filtersdb.delete_one({"_id": data["_id"]})

        await m.reply_text(f"✅ {sc('filter')} `{key}` {sc('stopped')}")

    except Exception as e:
        await m.reply_text(f"❌ {sc('error')}: `{str(e)}`")


# ---------------- LIST FILTERS ---------------- #
@app.on_message(filters.command("filters") & (filters.group | filters.private))
async def list_filters(_, m: Message):

    try:
        if m.chat.type == "private":
            return await m.reply_text(f"❌ {sc('this command only works in groups')}")

        name = m.chat.title or "private"
        text = f"📋 {sc('list of filters in')} {sc(name)}:\n\n"

        count = 0
        async for f in filtersdb.find({"chat_id": m.chat.id}):
            key = f.get("key") or f.get("keyword")
            if not key:
                continue

            text += f"🔹 `{key}`\n"
            count += 1

        if count == 0:
            return await m.reply_text(f"❌ {sc('no filters found')}")

        await m.reply_text(text)

    except Exception as e:
        await m.reply_text(f"❌ {sc('error')}: `{str(e)}`")


# ---------------- AUTO FILTER ---------------- #
@app.on_message((filters.text | filters.caption) & filters.group, group=50)
async def auto_filter(client, m: Message):

    try:
        txtmsg = (m.text or m.caption or "").lower()
        
        # Skip empty
        if not txtmsg:
            return

        async for f in filtersdb.find({"chat_id": m.chat.id}):
            key = f.get("key") or f.get("keyword")
            if not key:
                continue

            # Detect keyword anywhere in message (like Rose bot)
            if key.startswith("/"):
                matched = re.search(rf"(?<!\w){re.escape(key)}(?!\w)", txtmsg, re.IGNORECASE)
            else:
                # Strip @ for matching (so @rajowner matches rajowner and vice versa)
                clean_key = key.lstrip("@")
                matched = clean_key in txtmsg

            if matched:

                # 🔥 Premium emoji - use userbot to copy (preserves premium emoji, no forward tag)
                if f.get("has_premium_emoji") and f.get("premium_msg_chat") and f.get("premium_msg_id"):
                    sent = False
                    # Try userbot first (premium account preserves custom emoji)
                    try:
                        from STRABERRY.core.call import RAJ
                        userbot = RAJ.userbot1
                        if userbot:
                            await userbot.copy_message(
                                chat_id=m.chat.id,
                                from_chat_id=f["premium_msg_chat"],
                                message_id=f["premium_msg_id"],
                            )
                            sent = True
                    except Exception:
                        pass
                    
                    # Fallback: forward (shows forward tag but preserves emoji)
                    if not sent:
                        try:
                            await client.forward_messages(
                                chat_id=m.chat.id,
                                from_chat_id=f["premium_msg_chat"],
                                message_ids=f["premium_msg_id"],
                            )
                            sent = True
                        except Exception:
                            pass
                    
                    # Last fallback: plain text
                    if not sent and f.get("text"):
                        await m.reply_text(f["text"])
                    return

                # 🔥 SEND MEDIA (with caption if available)
                if f.get("file"):
                    try:
                        caption = f.get("text", "")
                        if caption:
                            return await m.reply_cached_media(f["file"], caption=caption)
                        else:
                            return await m.reply_cached_media(f["file"])
                    except Exception as e:
                        if f.get("text"):
                            return await m.reply_text(f["text"])
                        return

                # 🔥 SEND TEXT
                if f.get("text"):
                    return await m.reply_text(f["text"])

    except Exception as e:
        print(e)

# ---------------- WARN (FINAL REAL FIX) ---------------- #
@app.on_message(filters.command("warn") & (filters.group | filters.private))
async def warn(client, m: Message):

    try:
        if m.chat.type == "private":
            return await m.reply_text(f"❌ {sc('this command only works in groups')}")

        if not await is_admin(client, m.chat.id, m.from_user.id):
            return await m.reply_text(f"❌ {sc('only admin can use this')}")

        user = None
        by_reply = False

        # ---------------- USER GET ---------------- #
        if m.reply_to_message:
            user = m.reply_to_message.from_user
            by_reply = True
        elif len(m.command) > 1:
            try:
                user = await client.get_users(m.command[1])
            except:
                return await m.reply_text(f"❌ {sc('user not found')}")
        else:
            return await m.reply_text(f"⚠️ {sc('reply or warn user')}")

        if not user:
            return await m.reply_text(f"❌ {sc('user not found')}")

        if user.is_bot:
            return await m.reply_text(f"❌ {sc('cannot warn a bot')}")

        # 🔥 REAL MEMBER CHECK (NO FAKE ERROR)
        try:
            member = await client.get_chat_member(m.chat.id, user.id)

            if member.status == ChatMemberStatus.KICKED:
                return await m.reply_text("🚫 ᴜꜱᴇʀ ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ")

            if member.status == ChatMemberStatus.LEFT:
                return await m.reply_text("❌ ᴜꜱᴇʀ ɴᴏᴛ ɪɴ ɢʀᴏᴜᴘ")

        except Exception:
            # ❗ IMPORTANT FIX:
            # reply case me ignore error (user valid hota hai)
            if not by_reply:
                return await m.reply_text("❌ ᴜꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ")
            # reply case → continue (user valid)

        # admin check
        if await is_admin(client, m.chat.id, user.id):
            return await m.reply_text(f"❌ {sc('cannot warn admin')}")

        # bot permission
        try:
            bot = await client.get_chat_member(m.chat.id, (await client.get_me()).id)
            if bot.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await m.reply_text(f"❌ {sc('bot is not admin')}")
            if not bot.privileges.can_restrict_members:
                return await m.reply_text(f"❌ {sc('bot needs ban permission')}")
        except:
            return await m.reply_text(f"❌ {sc('bot is not admin')}")

        # ---------------- WARN COUNT ---------------- #
        data = await warndb.find_one({"chat": m.chat.id, "user": user.id})
        c = data["c"] + 1 if data else 1

        await warndb.update_one(
            {"chat": m.chat.id, "user": user.id},
            {"$set": {"c": c}},
            upsert=True
        )

        mention = f"[⚡{user.first_name}⚡](tg://user?id={user.id})"

        # ---------------- BAN ---------------- #
        if c >= 3:
            try:
                await m.chat.ban_member(user.id)
                await warndb.delete_one({"chat": m.chat.id, "user": user.id})
                return await m.reply_text(f"🚫 {mention} {sc('banned')}!")
            except Exception as e:
                return await m.reply_text(f"❌ {sc('failed to ban user')}: `{str(e)}`")

        # ---------------- BUTTON ---------------- #
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔘 Remove warn (admin only)", callback_data=f"rw_{user.id}")]
        ])

        await m.reply_text(
            f"⚠️ ᴜꜱᴇʀ {mention} ʜᴀꜱ {c}/3 ᴡᴀʀɴɪɴɢꜱ ʙᴇ ᴄᴀʀᴇꜰᴜʟ!",
            reply_markup=btn,
            disable_web_page_preview=True
        )

    except Exception as e:
        await m.reply_text(f"❌ {sc('error')}: `{str(e)}`")

# ---------------- REMOVE WARN (FIXED FINAL) ---------------- #
@app.on_callback_query(filters.regex("^rw_"))
async def rmwarn(client, q: CallbackQuery):

    try:
        uid = int(q.data.split("_")[1])

        member = await client.get_chat_member(q.message.chat.id, q.from_user.id)

        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await q.answer(f"❌ {sc('admin only')}", show_alert=True)

        data = await warndb.find_one({"chat": q.message.chat.id, "user": uid})

        if not data:
            return await q.answer(f"❌ {sc('no warnings')}", show_alert=True)

        c = data["c"] - 1

        admin_mention = f"[{q.from_user.first_name}](tg://user?id={q.from_user.id})"
        user_mention = f"[user](tg://user?id={uid})"

        if c <= 0:
            await warndb.delete_one({"chat": q.message.chat.id, "user": uid})

            await q.message.edit_text(
                f"✅ {admin_mention} ʜᴀꜱ ʀᴇᴍᴏᴠᴇᴅ {user_mention}'ꜱ ᴡᴀʀɴɪɴɢ."
            )
        else:
            await warndb.update_one(
                {"chat": q.message.chat.id, "user": uid},
                {"$set": {"c": c}}
            )

            await q.message.edit_text(
                f"✅ {admin_mention} ʀᴇᴍᴏᴠᴇᴅ ᴡᴀʀɴ — {c}/3"
            )

        await q.answer("✅ done")

    except:
        await q.answer("❌ error", show_alert=True)
