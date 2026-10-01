import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file
load_dotenv()

# ── Core bot config ────────────────────────────────────────────────────────────
API_ID = int(getenv("API_ID", ))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_ID = int(getenv("OWNER_ID", ))
OWNER_USERNAME = getenv("OWNER_USERNAME", "")
BOT_USERNAME = getenv("BOT_USERNAME", "")
BOT_NAME = getenv("BOT_NAME", "˹")
ASSUSERNAME = getenv("ASSUSERNAME", "")

# ── Database & logging ─────────────────────────────────────────────────────────
MONGO_DB_URI = getenv("MONGO_DB_URI")
LOGGER_ID = int(getenv("LOGGER_ID", -1004470010154))

# ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "1200"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "1800"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "157286400"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1288490189"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "30"))

# 🔥 Added User Play Limit (Default = 10)
MAX_USER_PLAY_LIMIT = int(getenv("MAX_USER_PLAY_LIMIT", 30))

# ── External APIs ──────────────────────────────────────────────────────────────
COOKIE_URL = getenv("COOKIE_URL")  # required (paste link)
API_URL = getenv("API_URL")        # optional
API_KEY = getenv("API_KEY")        # optional
DEEP_API = getenv("DEEP_API")      # optional

# ── Hosting / deployment ───────────────────────────────────────────────────────
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# ── Git / updates ──────────────────────────────────────────────────────────────
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/SPRDEVELOPER/STRABERRYBOT.git")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = getenv("GIT_TOKEN")  # needed if repo is private

# ── Support links ──────────────────────────────────────────────────────────────
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/StraberryBots")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/StraberryBotSupport")

# ── Assistant auto-leave ───────────────────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "3600"))

# ── Debug ──────────────────────────────────────────────────────────────────────
DEBUG_IGNORE_LOG = True

# ── Spotify (optional) ─────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ── Session strings (optional) ─────────────────────────────────────────────────
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# ── Media assets ───────────────────────────────────────────────────────────────
START_VIDS = [
    "https://telegra.ph/file/9b7e1b820c72a14d90be7.mp4",
    "https://telegra.ph/file/72f349b1386d6d9374a38.mp4",
    "https://telegra.ph/file/a4d90b0cb759b67d68644.mp4",
]
STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ",
]
HELP_IMG_URL = "https://files.catbox.moe/om6jc7.jpg"
START_IMG_URL = "https://files.catbox.moe/d932vr.jpg"
PING_VID_URL = "BAACAgEAAyEFAASv1rtRAALNJmo9Fig8i2ZXcFXJDnkN0ItiseRdAAKfBwACqpQ4RbVDAZS2rD3MHgQ"
PLAYLIST_IMG_URL = "https://files.catbox.moe/8bj070.jpg"
STATS_VID_URL = "https://telegra.ph/file/e2ab6106ace2e95862372.mp4"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/5lljz5.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/welf9g.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/gpa5ms.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/gpa5ms.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/xzmsy0.jpg"
SPOTIFY_ARTIST_IMG_URL = SPOTIFY_ALBUM_IMG_URL = SPOTIFY_PLAYLIST_IMG_URL = YOUTUBE_IMG_URL

# ── Helpers ────────────────────────────────────────────────────────────────────
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Bot Introduction Messages ───── #
AYU = [
    "ꜰɪɴᴅɪɴɢ ʏᴏᴜʀ ᴛᴜɴᴇ, ʙᴀʙʏ... 💞",
    "ѕᴏɴɢ ʟᴏᴀᴅɪɴɢ ғᴏʀ ᴍʏ ʙᴀʙʏ 💋",
    "ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴠɪʙᴇ ɪs ʟᴏᴀᴅɪɴɢ… 🎧",
    "💞 ғɪɴᴅɪɴɢ ʏᴏᴜʀ ᴀɴɴɪᴇᴍᴜsɪᴄ ᴛᴜɴᴇ... 🎧",
]

AYUV = [
    """ʜᴇʟʟᴏ {0}, 🥀

ɪᴛ'ꜱ ᴍᴇ {1} !

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ꜱᴜᴘᴘᴏʀᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍꜱ : ʏᴏᴜᴛᴜʙᴇ, ꜱᴘᴏᴛɪꜰʏ,
┠ ◆ ʀᴇꜱꜱᴏ, ᴀᴘᴘʟᴇᴍᴜꜱɪᴄ , ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ ᴇᴛᴄ.
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ➥ Uᴘᴛɪᴍᴇ : {2}
┠ ➥ SᴇʀᴠᴇʀSᴛᴏʀᴀɢᴇ : {3}
┠ ➥ CPU Lᴏᴀᴅ : {4}
┠ ➥ RAM Cᴏɴsᴜᴘᴛɪᴏɴ : {5}
┠ ➥ ᴜꜱᴇʀꜱ : {6}
┠ ➥ ᴄʜᴀᴛꜱ : {7}
┗━━━━━━━━━━━━━━━━━⧫

🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🪽 ➪ [»»—— 𝗞 𝝠 𝗟 𝗩 𝝠 𝗡 • ‹𝟹🌷݁˖𓂃 »︎](https://t.me/MR_KALVAN)
""",

    """ʜɪɪ, {0} ~

◆ ɪ'ᴍ ᴀ {1} ᴛᴇʟᴇɢʀᴀᴍ ꜱᴛʀᴇᴀᴍɪɴɢ ʙᴏᴛ ᴡɪᴛʜ ꜱᴏᴍᴇ ᴜꜱᴇꜰᴜʟ
◆ ᴜʟᴛʀᴀ ғᴀsᴛ ᴠᴄ ᴘʟᴀʏᴇʀ ꜰᴇᴀᴛᴜʀᴇꜱ.

✨ ꜰᴇᴀᴛᴜʀᴇꜱ ⚡️
◆ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs.
◆ Sᴜᴘᴇʀғᴀsᴛ ʟᴀɢ Fʀᴇᴇ ᴘʟᴀʏᴇʀ.
◆ ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴍᴜꜱɪᴄ + ᴠɪᴅᴇᴏ.
◆ ʟɪᴠᴇ ꜱᴛʀᴇᴀɴɪɴɢ.
◆ ɴᴏ ᴘʀᴏᴍᴏ.
◆ ʙᴇꜱᴛ ꜱᴏᴜɴᴅ Qᴜᴀʟɪᴛʏ.
◆ 24×7 ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴍᴜꜱɪᴄ.
◆ ᴀᴅᴅ ᴛʜɪꜱ ʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ɪᴛ ᴀᴅᴍɪɴ ᴀɴᴅ ᴇɴᴊᴏʏ ᴍᴜꜱɪᴄ 🎵.

┏━━━━━━━━━━━━━━━━━⧫
┠ ◆ ꜱᴜᴘᴘᴏʀᴛɪɴɢ ᴘʟᴀᴛꜰᴏʀᴍꜱ : ʏᴏᴜᴛᴜʙᴇ, ꜱᴘᴏᴛɪꜰʏ,
┠ ◆ ʀᴇꜱꜱᴏ, ᴀᴘᴘʟᴇᴍᴜꜱɪᴄ , ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ ᴇᴛᴄ.
┗━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━⧫
┠ ➥ Uᴘᴛɪᴍᴇ : {2}
┠ ➥ SᴇʀᴠᴇʀSᴛᴏʀᴀɢᴇ : {3}
┠ ➥ CPU Lᴏᴀᴅ : {4}
┠ ➥ RAM Cᴏɴsᴜᴘᴛɪᴏɴ : {5}
┠ ➥ ᴜꜱᴇʀꜱ : {6}
┠ ➥ ᴄʜᴀᴛꜱ : {7}
┗━━━━━━━━━━━━━━━━━⧫

🫧 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🪽 ➪ [»»—— 𝗞 𝝠 𝗟 𝗩 𝝠 𝗡 • ‹𝟹🌷݁˖𓂃 »︎](https://t.me/MR_KALVAN)
"""
]

# ── Runtime structures ─────────────────────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ── Minimal validation ─────────────────────────────────────────────────────────
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://Tamilchat_TP")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://Tamilchat7s")

if not COOKIE_URL:
    raise SystemExit("[ERROR] - COOKIE_URL is required.")

if not re.match(r"^https://(batbin\.me|pastebin\.com)/[A-Za-z0-9]+$", COOKIE_URL):
    raise SystemExit("[ERROR] - Invalid COOKIE_URL. Use https://batbin.me/<id> or https://pastebin.com/<id>")
