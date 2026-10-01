
from datetime import datetime, timezone, timedelta

from pyrogram import filters, enums
from pyrogram.types import (
    ChatJoinRequest,
    CallbackQuery,
    Message,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ForceReply,
)
from pyrogram.errors import UserIsBlocked, PeerIdInvalid, RPCError

import config
from STRABERRY import app
from STRABERRY.logging import LOGGER
from STRABERRY.mongo import joinreq_db as db

IST = timezone(timedelta(hours=5, minutes=30))

CARD_TEMPLATE = """🔔 **New Join Request**

**Group :** {chat_title} (`{chat_id}`)
**User :** {first_name} (@{username})
**ID :** `{user_id}`
**Bio :** {bio}
**Requested at:** {requested_at}

Admins: use the buttons below to decide."""

_ADMIN_STATUSES = (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER)
_MUTE_PERMS = ChatPermissions()

_pending_reason: dict[int, tuple[int, int]] = {}


def _fmt_time(dt: datetime) -> str:
    return dt.astimezone(IST).strftime("%Y-%m-%d %I:%M:%S %p IST")


def _buttons(chat_id: int, user_id: int, disabled_label: str = None) -> InlineKeyboardMarkup:
    if disabled_label:
        return InlineKeyboardMarkup([[InlineKeyboardButton(disabled_label, callback_data="jr_noop", style=enums.ButtonStyle.PRIMARY)]])
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🍏 Approve", callback_data=f"jr_ok_{chat_id}_{user_id}", style=enums.ButtonStyle.SUCCESS),
                InlineKeyboardButton("🍎 Dismiss", callback_data=f"jr_ds_{chat_id}_{user_id}", style=enums.ButtonStyle.DANGER),
            ],
            [
                InlineKeyboardButton("🤐 Mute", callback_data=f"jr_mt_{chat_id}_{user_id}", style=enums.ButtonStyle.PRIMARY),
                InlineKeyboardButton("🔨 Ban", callback_data=f"jr_bn_{chat_id}_{user_id}", style=enums.ButtonStyle.DANGER),
            ],
            [
                InlineKeyboardButton("🔻 Dismiss With Reason 🔻", callback_data=f"jr_dr_{chat_id}_{user_id}", style=enums.ButtonStyle.DANGER),
            ],
        ]
    )


async def _is_group_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in _ADMIN_STATUSES
    except RPCError:
        return False


async def _sync_cards(client, req: dict, final_text: str, disabled_label: str) -> None:
    for card in req.get("cards", []):
        try:
            await client.edit_message_text(
                card["chat_id"],
                card["msg_id"],
                final_text,
                reply_markup=_buttons(req["chat_id"], req["user_id"], disabled_label=disabled_label),
            )
        except RPCError:
            pass


@app.on_chat_join_request(filters.all, group=1)
async def on_join_request(client, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user

    if await db.has_pending(chat.id, user.id):
        return

    doc = await db.create_request(
        chat_id=chat.id,
        user_id=user.id,
        chat_title=chat.title,
        username=user.username,
        first_name=user.first_name or "Unknown",
        bio=getattr(request, "bio", None),
    )

    text = CARD_TEMPLATE.format(
        chat_title=doc["chat_title"],
        chat_id=doc["chat_id"],
        first_name=doc["first_name"],
        username=doc["username"] or "-",
        user_id=doc["user_id"],
        bio=doc["bio"],
        requested_at=_fmt_time(doc["requested_at"]),
    )
    markup = _buttons(chat.id, user.id)

    try:
        sent = await client.send_message(chat.id, text, reply_markup=markup)
        await db.add_card_ref(chat.id, user.id, sent.chat.id, sent.id)
    except RPCError as e:
        LOGGER(__name__).warning(
            f"⚠️ join-request: could not post approval card into group "
            f"{chat.id} ({chat.title}): {e}. Make sure the bot is an admin "
            f"there with permission to post messages."
        )

    if config.LOGGER_ID:
        try:
            sent2 = await client.send_message(config.LOGGER_ID, text, reply_markup=markup)
            await db.add_card_ref(chat.id, user.id, sent2.chat.id, sent2.id)
        except RPCError:
            pass


@app.on_callback_query(filters.regex(r"^jr_(ok|ds|mt|bn|dr)_(-?\d+)_(\d+)$"))
async def on_join_decision(client, cq: CallbackQuery):
    action, chat_id, user_id = cq.matches[0].groups()
    chat_id, user_id = int(chat_id), int(user_id)

    if not await _is_group_admin(client, chat_id, cq.from_user.id):
        await cq.answer("⛔ Only admins of this group can use these buttons.", show_alert=True)
        return

    req = await db.get_request(chat_id, user_id)
    if not req or req["status"] != db.STATUS_PENDING:
        await cq.answer("This request was already handled.", show_alert=True)
        return

    if action == "dr":
        prompt = await cq.message.reply_text(
            f"✍️ Reply to **this message** with the reason for declining "
            f"{req['first_name']}'s join request.",
            reply_markup=ForceReply(selective=True),
        )
        _pending_reason[prompt.id] = (chat_id, user_id)
        await cq.answer("Reply with the reason.")
        return

    label_map = {
        "ok": ("✅ Approved", db.STATUS_APPROVED),
        "ds": ("🍎 Dismissed", db.STATUS_REJECTED),
        "mt": ("🤐 Approved (Muted)", db.STATUS_MUTED),
        "bn": ("🔨 Banned", db.STATUS_BANNED),
    }
    label, status = label_map[action]

    try:
        if action == "ok":
            await client.approve_chat_join_request(chat_id, user_id)
        elif action == "ds":
            await client.decline_chat_join_request(chat_id, user_id)
        elif action == "mt":
            await client.approve_chat_join_request(chat_id, user_id)
            await client.restrict_chat_member(chat_id, user_id, _MUTE_PERMS)
        elif action == "bn":
            await client.ban_chat_member(chat_id, user_id)
    except RPCError as e:
        await cq.answer(f"Telegram error: {e.MESSAGE if hasattr(e, 'MESSAGE') else e}", show_alert=True)
        return

    await _finalize(client, req, status, cq.from_user, label)
    await cq.answer(label)


@app.on_message(filters.reply & filters.group & ~filters.via_bot, group=2)
async def on_reason_reply(client, message: Message):
    replied = message.reply_to_message
    if not replied or replied.id not in _pending_reason:
        return

    chat_id, user_id = _pending_reason.pop(replied.id)

    if not await _is_group_admin(client, chat_id, message.from_user.id):
        return

    req = await db.get_request(chat_id, user_id)
    if not req or req["status"] != db.STATUS_PENDING:
        try:
            await message.reply_text("This request was already handled.")
        except RPCError:
            pass
        return

    reason = message.text or "-"
    try:
        await client.decline_chat_join_request(chat_id, user_id)
    except RPCError as e:
        await message.reply_text(f"Telegram error: {e.MESSAGE if hasattr(e, 'MESSAGE') else e}")
        return

    await _finalize(client, req, db.STATUS_REJECTED, message.from_user, "🍎 Dismissed (with reason)", reason=reason)
    try:
        await replied.delete()
        await message.delete()
    except RPCError:
        pass


async def _finalize(client, req: dict, status: str, admin, label: str, reason: str = None) -> None:
    updated = await db.set_decision(req["chat_id"], req["user_id"], status, admin.id, reason=reason)
    if not updated:
        return

    extra = f"\n**Reason:** {reason}" if reason else ""
    final_text = CARD_TEMPLATE.format(
        chat_title=req["chat_title"],
        chat_id=req["chat_id"],
        first_name=req["first_name"],
        username=req["username"] or "-",
        user_id=req["user_id"],
        bio=req["bio"],
        requested_at=_fmt_time(req["requested_at"]),
    ) + f"\n\n**Status:** {label} by {admin.mention}" + extra

    req = await db.get_request(req["chat_id"], req["user_id"])
    await _sync_cards(client, req, final_text, disabled_label=label)

    if status == db.STATUS_APPROVED:
        dm_text = f"🎉 Your request to join **{req['chat_title']}** was approved! Welcome aboard."
    elif status == db.STATUS_MUTED:
        dm_text = (
            f"🎉 Your request to join **{req['chat_title']}** was approved, "
            f"but you've been muted until an admin lifts it."
        )
    elif status == db.STATUS_BANNED:
        dm_text = f"🚫 Your request to join **{req['chat_title']}** was declined and you were banned."
    else:
        dm_text = f"😔 Your request to join **{req['chat_title']}** was declined by the admins."
        if reason:
            dm_text += f"\n\n**Reason:** {reason}"

    try:
        await client.send_message(req["user_id"], dm_text)
    except (UserIsBlocked, PeerIdInvalid, RPCError):
        pass
