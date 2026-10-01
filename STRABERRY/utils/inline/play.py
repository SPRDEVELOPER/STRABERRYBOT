import time
from pyrogram.types import InlineKeyboardButton
from STRABERRY.utils.formatters import time_to_seconds
from STRABERRY.core.mongo import mongodb
from STRABERRY.utils.colour import styled_button

LAST_UPDATE_TIME = {}

# ===== AUTOPLAY DB =====
autoplay_db = mongodb.autoplay


# 🔥 SAFE GET (NO ERROR)
async def get_autoplay(chat_id):
    try:
        data = await autoplay_db.find_one({"chat_id": chat_id})
        return data["status"] if data else False
    except:
        return False


# 🔥 SAFE TIME CONVERTER
def safe_time_to_seconds(t):
    try:
        return time_to_seconds(t)
    except:
        return 0


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]


def should_update_progress(chat_id):
    now = time.time()
    last = LAST_UPDATE_TIME.get(chat_id, 0)
    if now - last >= 6:
        LAST_UPDATE_TIME[chat_id] = now
        return True
    return False


# 🔥 PROGRESS BAR - HEART WAVE STYLE
def generate_progress_bar(played_sec, duration_sec):
    if duration_sec <= 0:
        return "〜♡〜"

    percentage = min((played_sec / duration_sec) * 100, 100)

    # Button width ke hisab se dynamic length
    if duration_sec >= 3600:       # 1 hour+
        bar_length = 1
    elif duration_sec >= 1800:     # 30 min+
        bar_length = 3
    else:
        bar_length = 8

    filled = int(bar_length * percentage / 100)
    empty = bar_length - filled

    return "〜" * filled + "♡" + "〜" * empty


# 🔥 ORIGINAL CONTROL BUTTONS (for pyrogram InlineKeyboardMarkup)
def control_buttons_sync(_, chat_id):
    return [
        [
            InlineKeyboardButton("▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton("II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton("↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton("‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton("▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton("« 20s", callback_data=f"ADMIN 5|{chat_id}"),
            InlineKeyboardButton("⚙️", callback_data="open_settings"),
            InlineKeyboardButton("20s »", callback_data=f"ADMIN 6|{chat_id}"),
        ]
    ]


# 🔥 COLOURED CONTROL BUTTONS (for Bot API HTTP - colour support)
def control_buttons_colored(chat_id):
    return [
        [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="success"),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="success"),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="success"),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="success"),
        ],
        [
            styled_button("« 20s", callback_data=f"ADMIN 5|{chat_id}", style="primary"),
            styled_button("⚙️", callback_data="open_settings", style="primary"),
            styled_button("20s »", callback_data=f"ADMIN 6|{chat_id}", style="primary"),
        ]
    ]


# 🔥 COLOURED TIMER UI
def stream_markup_timer_colored(chat_id, played, dur):
    if not should_update_progress(chat_id):
        return control_buttons_colored(chat_id)

    played_sec = safe_time_to_seconds(played)
    duration_sec = safe_time_to_seconds(dur)

    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[styled_button(f"{played} {bar} {dur}", callback_data="GetTimer", style="primary")]]
        + control_buttons_colored(chat_id)
        + [[styled_button("✘ ᴄʟᴏꜱᴇ ✘", callback_data="close", style="danger")]]
    )


# 🔥 COLOURED MAIN PLAYER
def stream_markup_colored(chat_id):
    return (
        control_buttons_colored(chat_id)
        + [[styled_button("✘ ᴄʟᴏꜱᴇ ✘", callback_data="close", style="danger")]]
    )


# ═══════════════════════════════════════════════════════════
# BELOW: ORIGINAL PYROGRAM FUNCTIONS (fallback / non-colored)
# ═══════════════════════════════════════════════════════════

# 🔥 TIMER UI (pyrogram fallback)
def stream_markup_timer(_, chat_id, played, dur):
    if not should_update_progress(chat_id):
        return control_buttons_sync(_, chat_id)

    played_sec = safe_time_to_seconds(played)
    duration_sec = safe_time_to_seconds(dur)

    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")]]
        + control_buttons_sync(_, chat_id)
        + [[InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]]
    )


# 🔥 MAIN PLAYER (pyrogram fallback)
def stream_markup(_, chat_id):
    return (
        control_buttons_sync(_, chat_id)
        + [[InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]]
    )


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"StraberryPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"StraberryPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    short_query = query[:20]
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {short_query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
