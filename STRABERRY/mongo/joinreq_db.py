
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from STRABERRY.core.mongo import mongodb

_col = mongodb["join_requests"]

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_MUTED = "approved_muted"
STATUS_BANNED = "banned"

FINAL_STATUSES = (STATUS_APPROVED, STATUS_REJECTED, STATUS_MUTED, STATUS_BANNED)


def _key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}_{user_id}"


async def has_pending(chat_id: int, user_id: int) -> bool:
    doc = await _col.find_one(
        {"_id": _key(chat_id, user_id), "status": STATUS_PENDING}, {"_id": 1}
    )
    return doc is not None


async def create_request(
    chat_id: int,
    user_id: int,
    chat_title: str,
    username: Optional[str],
    first_name: str,
    bio: Optional[str],
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc = {
        "_id": _key(chat_id, user_id),
        "chat_id": chat_id,
        "chat_title": chat_title,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "bio": bio or "-",
        "status": STATUS_PENDING,
        "requested_at": now,
        "decided_at": None,
        "decided_by": None,
        "reason": None,
        "cards": [],
    }
    await _col.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
    return doc


async def get_request(chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    return await _col.find_one({"_id": _key(chat_id, user_id)})


async def add_card_ref(chat_id: int, user_id: int, card_chat_id: int, card_msg_id: int) -> None:
    await _col.update_one(
        {"_id": _key(chat_id, user_id)},
        {"$push": {"cards": {"chat_id": card_chat_id, "msg_id": card_msg_id}}},
    )


async def set_decision(chat_id: int, user_id: int, status: str, admin_id: int, reason: Optional[str] = None) -> bool:
    if status not in FINAL_STATUSES:
        raise ValueError(f"status must be one of {FINAL_STATUSES}")
    result = await _col.update_one(
        {"_id": _key(chat_id, user_id), "status": STATUS_PENDING},
        {
            "$set": {
                "status": status,
                "decided_at": datetime.now(timezone.utc),
                "decided_by": admin_id,
                "reason": reason,
            }
        },
    )
    return result.modified_count == 1


async def list_pending(chat_id: int) -> List[Dict[str, Any]]:
    cursor = _col.find({"chat_id": chat_id, "status": STATUS_PENDING}).sort("requested_at", 1)
    return await cursor.to_list(length=None)


async def count_by_status(chat_id: int, status: str) -> int:
    return await _col.count_documents({"chat_id": chat_id, "status": status})
