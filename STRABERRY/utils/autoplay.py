import asyncio
import random
import re
import time
import aiohttp

from STRABERRY import app
from STRABERRY.core.mongo import mongodb
from STRABERRY.misc import db
from py_yt import VideosSearch

autoplay_db = mongodb.autoplay

RECENT = {}
AUTO_PLAYING = {}
USER_LAST_PLAY = {}


def set_user_play(chat_id, title):
    USER_LAST_PLAY[chat_id] = title


ARTIST_DB = {
    "arijit singh": ["arijit", "arijit singh"],
    "atif aslam": ["atif", "atif aslam"],
    "jubin nautiyal": ["jubin", "jubin nautiyal"],
    "neha kakkar": ["neha kakkar", "neha"],
    "shreya ghoshal": ["shreya", "shreya ghoshal"],
    "badshah": ["badshah"],
    "yo yo honey singh": ["honey singh", "yo yo"],
    "sidhu moosewala": ["sidhu", "sidhu moosewala"],
    "diljit dosanjh": ["diljit", "diljit dosanjh"],
    "karan aujla": ["karan aujla"],
    "ap dhillon": ["ap dhillon", "dhillon"],
    "guru randhawa": ["guru randhawa"],
    "darshan raval": ["darshan raval", "darshan"],
    "armaan malik": ["armaan malik", "armaan"],
    "sonu nigam": ["sonu nigam"],
    "kumar sanu": ["kumar sanu"],
    "kishore kumar": ["kishore kumar", "kishore"],
    "lata mangeshkar": ["lata mangeshkar", "lata"],
    "udit narayan": ["udit narayan", "udit"],
    "pawan singh": ["pawan singh"],
    "khesari lal": ["khesari lal", "khesari"],
    "ammy virk": ["ammy virk"],
    "b praak": ["b praak"],
    "hardy sandhu": ["hardy sandhu"],
    "shubh": ["shubh"],
}

SIMILAR_ARTISTS = {
    "arijit singh": ["jubin nautiyal", "atif aslam", "armaan malik", "darshan raval"],
    "jubin nautiyal": ["arijit singh", "armaan malik", "darshan raval"],
    "sidhu moosewala": ["karan aujla", "ap dhillon", "diljit dosanjh", "shubh"],
    "diljit dosanjh": ["sidhu moosewala", "karan aujla", "ammy virk"],
    "karan aujla": ["sidhu moosewala", "ap dhillon", "shubh"],
    "ap dhillon": ["karan aujla", "shubh", "diljit dosanjh"],
    "neha kakkar": ["badshah", "guru randhawa", "shreya ghoshal"],
    "badshah": ["yo yo honey singh", "neha kakkar", "guru randhawa"],
}


def extract_artist(title):
    if not title:
        return ""
    t = title.lower()
    for artist, keys in ARTIST_DB.items():
        if any(x in t for x in keys):
            return artist
    for sep in [" - ", " | ", " — "]:
        if sep in title:
            parts = title.split(sep)
            for part in parts[1:]:
                p = part.strip().lower()
                if 2 < len(p) < 40:
                    if any(w in p for w in ["records", "films", "official", "video", "music"]):
                        continue
                    for artist, keys in ARTIST_DB.items():
                        if any(x in p for x in keys):
                            return artist
            break
    return ""


def normalize_title(title):
    if not title:
        return ""
    t = title.lower().strip()
    for sep in [" - ", " | ", " — "]:
        if sep in t:
            t = t.split(sep)[0].strip()
            break
    t = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", "", t)
    noise = ["official", "video", "music", "audio", "lyrics", "lyrical", "full", "hd", "hq", "4k", "song", "new", "latest"]
    for w in noise:
        t = re.sub(rf"\b{w}\b", "", t)
    return re.sub(r"\s+", " ", t).strip()


async def is_repeat(chat_id, vidid, title=""):
    if chat_id not in RECENT:
        RECENT[chat_id] = []
    now = time.time()
    # Keep history for 4 hours (longer to avoid repeats)
    RECENT[chat_id] = [(v, t, ti) for v, t, ti in RECENT[chat_id] if now - t < 14400]
    
    # Check exact video ID
    for sv, _, st in RECENT[chat_id]:
        if sv == vidid:
            return True
    
    # Check normalized title match
    if title:
        norm = normalize_title(title)
        if norm and len(norm) >= 4:
            for _, _, st in RECENT[chat_id]:
                if not st:
                    continue
                snorm = normalize_title(st)
                if not snorm:
                    continue
                # Exact normalized match
                if snorm == norm:
                    return True
                # Partial match - if one title contains the other (catches remixes, versions)
                if len(norm) >= 6 and len(snorm) >= 6:
                    if norm in snorm or snorm in norm:
                        return True
                    # Word overlap - if 70%+ words match, it's likely same song
                    words1 = set(norm.split())
                    words2 = set(snorm.split())
                    if len(words1) >= 2 and len(words2) >= 2:
                        common = words1 & words2
                        smaller = min(len(words1), len(words2))
                        if smaller > 0 and len(common) / smaller >= 0.7:
                            return True
    return False


async def add_recent(chat_id, vidid, title=""):
    if chat_id not in RECENT:
        RECENT[chat_id] = []
    RECENT[chat_id].append((vidid, time.time(), title))
    if len(RECENT[chat_id]) > 50:
        RECENT[chat_id] = RECENT[chat_id][-50:]


async def yt_search(query, limit=10):
    try:
        data = await VideosSearch(query, limit=limit).next()
        return data.get("result", [])
    except:
        return []


def build_queries(user_query, artist, last_title):
    queries = []
    if artist:
        # Always search for DIFFERENT songs from this artist
        suffixes = [
            "all songs", "hit songs 2024", "best songs 2023", "new songs 2025",
            "latest songs", "top songs", "romantic songs", "sad songs",
            "popular songs", "old songs", "superhit", "top 10",
            "unplugged", "acoustic", "live performance",
        ]
        random.shuffle(suffixes)
        queries = [f"{artist} {s}" for s in suffixes[:5]]
        
        # Also try similar artists for variety
        if artist in SIMILAR_ARTISTS:
            sim = random.choice(SIMILAR_ARTISTS[artist])
            queries.append(f"{sim} hit songs")
            queries.append(f"{sim} latest songs")
    elif user_query:
        suffixes = ["songs", "more songs like", "similar to", "hit songs", "best songs", "top tracks"]
        random.shuffle(suffixes)
        queries = [f"{user_query} {s}" for s in suffixes[:3]]
        queries.append(user_query)
    
    if last_title and last_title != user_query:
        # Use last song title to find similar but DIFFERENT songs
        norm_last = normalize_title(last_title)
        if norm_last:
            queries.append(f"{norm_last} similar songs")
    
    random.shuffle(queries)
    return queries[:7]


async def get_thumbnail(vid_id):
    urls = [
        f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
    ]
    async with aiohttp.ClientSession() as s:
        for url in urls:
            try:
                async with s.get(url) as r:
                    if r.status == 200:
                        return url
            except:
                pass
    return urls[-1]


BAD_WORDS = [
    "slowed", "reverb", "8d", "lofi", "jukebox", "nonstop", "mashup",
    "compilation", "full album", "full movie", "podcast", "interview",
    "cover", "karaoke", "instrumental", "live concert", "reaction",
]


async def auto_play_next(client, chat_id, last_title="", last_vidid="", forceplay=False):
    from STRABERRY.utils.database import get_lang
    from STRABERRY.utils.stream.stream import stream
    from STRABERRY.core.call import RAJ
    from strings import get_string

    if AUTO_PLAYING.get(chat_id):
        return
    AUTO_PLAYING[chat_id] = True

    try:
        data = await autoplay_db.find_one({"chat_id": chat_id})
        if not data or not data.get("status"):
            AUTO_PLAYING[chat_id] = False
            return

        msg = await client.send_message(chat_id, "✨ ᴀɴɴɪᴇ → ꜰɪɴᴅɪɴɢ ɴᴇxᴛ ꜱᴏɴɢ ʙᴀʙʏ 💞")

        # Mark current song as played
        if last_vidid:
            await add_recent(chat_id, last_vidid, last_title)

        # Get search context
        user_query = USER_LAST_PLAY.get(chat_id, "")
        if not user_query:
            if last_title:
                user_query = last_title
            else:
                queue = db.get(chat_id)
                if queue and len(queue) > 0:
                    user_query = queue[0].get("title", "hindi songs 2025")
                else:
                    user_query = "hindi songs 2025"

        artist = extract_artist(user_query) or extract_artist(last_title)
        queries = build_queries(user_query, artist, last_title)

        vidid = None
        details = None

        # Search through queries
        for query in queries:
            try:
                results = await yt_search(query, limit=10)
                if not results:
                    continue

                random.shuffle(results)

                for r in results:
                    vid = r.get("id", "")
                    title = r.get("title", "")
                    dur = r.get("duration", "0:00")

                    if not vid or not title:
                        continue
                    if vid == last_vidid:
                        continue

                    tl = title.lower()
                    if any(b in tl for b in BAD_WORDS):
                        continue

                    # Duration 1-10 min
                    if not dur or ":" not in str(dur):
                        continue
                    parts = str(dur).split(":")
                    if len(parts) == 3:
                        continue
                    try:
                        total = int(parts[0]) * 60 + int(parts[1])
                        if total < 60 or total > 600:
                            continue
                    except:
                        continue

                    if await is_repeat(chat_id, vid, title):
                        continue

                    # Found valid song
                    thumbs = r.get("thumbnails", [])
                    thumb = thumbs[-1].get("url", "") if thumbs else ""
                    vidid = vid
                    details = {
                        "title": title,
                        "duration_min": dur,
                        "vidid": vid,
                        "thumb": thumb,
                        "link": f"https://youtube.com/watch?v={vid}",
                    }
                    break

                if vidid:
                    break
            except:
                continue
            await asyncio.sleep(0.2)

        # Fallback - just search generic if nothing found
        if not vidid:
            fallbacks = [
                f"{user_query}",
                "bollywood songs 2025",
                "latest hindi songs",
                "trending songs india",
            ]
            for fb in fallbacks:
                try:
                    results = await yt_search(fb, limit=5)
                    if not results:
                        continue
                    random.shuffle(results)
                    for r in results:
                        vid = r.get("id", "")
                        title = r.get("title", "")
                        dur = r.get("duration", "0:00")
                        if not vid or not title or vid == last_vidid:
                            continue
                        if any(b in title.lower() for b in BAD_WORDS):
                            continue
                        if not dur or ":" not in str(dur):
                            continue
                        parts = str(dur).split(":")
                        if len(parts) == 3:
                            continue
                        try:
                            total = int(parts[0]) * 60 + int(parts[1])
                            if total < 60 or total > 600:
                                continue
                        except:
                            continue
                        if await is_repeat(chat_id, vid, title):
                            continue
                        thumbs = r.get("thumbnails", [])
                        thumb = thumbs[-1].get("url", "") if thumbs else ""
                        vidid = vid
                        details = {
                            "title": title,
                            "duration_min": dur,
                            "vidid": vid,
                            "thumb": thumb,
                            "link": f"https://youtube.com/watch?v={vid}",
                        }
                        break
                    if vidid:
                        break
                except:
                    continue

        if not vidid:
            try:
                await msg.edit_text("❌ ɴᴏ ꜱᴏɴɢ ꜰᴏᴜɴᴅ, ʟᴇᴀᴠɪɴɢ ᴠᴄ...")
                await asyncio.sleep(2)
            except:
                pass
            # Song not found — leave VC
            try:
                await RAJ.stop_stream(chat_id)
            except:
                pass
            AUTO_PLAYING[chat_id] = False
            return

        await add_recent(chat_id, vidid, details.get("title", ""))

        link = details.get("link", f"https://youtube.com/watch?v={vidid}")
        song_title = details.get("title", "Autoplay")
        song_duration = details.get("duration_min", "00:00")

        try:
            thumb = details.get("thumb", "")
            if not thumb or not thumb.startswith("http"):
                thumb = await get_thumbnail(vidid)
        except:
            thumb = await get_thumbnail(vidid)

        language = await get_lang(chat_id)
        _ = get_string(language)

        await stream(
            _, client, 0,
            {
                "link": link,
                "vidid": vidid,
                "title": song_title,
                "duration_min": song_duration,
                "thumb": thumb,
            },
            chat_id,
            "ᴀɴɴɪᴇ ᴀᴜᴛᴏᴘʟᴀʏ",
            chat_id,
            video=False,
            streamtype="youtube",
            is_autoplay=True,
            forceplay=forceplay,
        )

    except Exception as e:
        print(f"Autoplay Error: {e}")
        # Song download fail — leave VC
        try:
            await RAJ.stop_stream(chat_id)
        except:
            pass
    finally:
        # Always delete "finding next song" message
        try:
            await msg.delete()
        except:
            pass
        AUTO_PLAYING.pop(chat_id, None)
