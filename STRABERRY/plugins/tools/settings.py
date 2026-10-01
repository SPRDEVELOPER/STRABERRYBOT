from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from STRABERRY import app
from STRABERRY.core.mongo import mongodb
from STRABERRY.misc import db as music_db
import asyncio

# ===== DATABASE =====
db = mongodb.autoplay


# ===== GET / SET =====
async def get_autoplay(chat_id):
    data = await db.find_one({"chat_id": chat_id})
    return data["status"] if data else False


async def set_autoplay(chat_id, status):
    await db.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": status}},
        upsert=True
    )


# ===== ADMIN CHECK =====
async def is_admin(chat_id, user_id):
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]


# ===== SETTINGS BUTTONS =====
def settings_buttons(status):
    text = "✅ ᴀᴜᴛᴏᴘʟᴀʏ ᴏɴ" if status else "❌ ᴀᴜᴛᴏᴘʟᴀʏ ᴏғғ"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔁 {text}", callback_data="toggle_autoplay")],
        [InlineKeyboardButton("⏭ ᴀᴜᴛᴏᴘʟᴀʏ sᴋɪᴘ", callback_data="autoplay_skip")],
        [InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data="close_settings")]
    ])


# ===== OPEN SETTINGS (NO TEXT CHANGE, ONLY BUTTON UPDATE) =====
@app.on_callback_query(filters.regex("open_settings"))
async def settings_panel(_, query: CallbackQuery):
    chat_id = query.message.chat.id

    status = await get_autoplay(chat_id)

    # 🔥 ONLY BUTTON CHANGE (TEXT SAME रहेगा)
    try:
        await query.message.edit_reply_markup(
            reply_markup=settings_buttons(status)
        )
    except:
        pass
    
    await query.answer(cache_time=0)


# ===== TOGGLE AUTOPLAY (LIVE UPDATE) =====
@app.on_callback_query(filters.regex("toggle_autoplay"))
async def toggle(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if not await is_admin(chat_id, user_id):
        try:
            await query.answer("⚠️ Admin only", show_alert=True, cache_time=0)
        except:
            pass
        return

    status = await get_autoplay(chat_id)
    new_status = not status

    await set_autoplay(chat_id, new_status)

    # 🔥 BUTTON LIVE UPDATE
    try:
        await query.message.edit_reply_markup(
            reply_markup=settings_buttons(new_status)
        )
    except:
        pass

    try:
        await query.answer(
            "✅ Autoplay ON" if new_status else "❌ Autoplay OFF",
            show_alert=True,
            cache_time=0
        )
    except:
        pass


# ===== 🔥 SKIP SONG (DIRECT PLAY FIX) =====
@app.on_callback_query(filters.regex("autoplay_skip"))
async def skip(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if not await is_admin(chat_id, user_id):
        try:
            await query.answer("⚠️ Admin only", show_alert=True, cache_time=0)
        except:
            pass
        return

    from STRABERRY.misc import db
    from STRABERRY.core.call import RAJ
    from STRABERRY.utils.autoplay import auto_play_next

    queue = db.get(chat_id)
    autoplay = await get_autoplay(chat_id)

    try:
        # Try to answer first
        try:
            await query.answer("⏭ Skipping...", cache_time=0)
        except:
            pass
        
        # 🔥 NEXT SONG EXISTS
        if queue and len(queue) > 1:
            queue.pop(0)
            next_song = queue[0]

            await RAJ.skip_stream(chat_id, next_song["file"])
            return

        # 🔥 AUTOPLAY MODE - clear queue, keep VC, play next directly
        if autoplay:
            if queue:
                queue.clear()

            await auto_play_next(app, chat_id, forceplay=True)
            return

        # 🔥 NO AUTOPLAY
        await RAJ.stop_stream(chat_id)

    except Exception as e:
        print("Skip Error:", e)
        
        # Fallback: Try autoplay if enabled
        if autoplay:
            try:
                if queue:
                    queue.clear()
                await auto_play_next(app, chat_id, forceplay=True)
            except:
                pass


# ===== CLOSE =====
@app.on_callback_query(filters.regex("close_settings"))
async def close(_, query: CallbackQuery):
    try:
        await query.answer(cache_time=0)
        await query.message.delete()
    except:
        pass
