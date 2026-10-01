import os
import aiofiles
import aiohttp

from PIL import (
    Image,
    ImageEnhance,
)

from config import YOUTUBE_IMG_URL
from STRABERRY.core.dir import CACHE_DIR


# =========================================================
# SIMPLE FULL ORIGINAL THUMBNAIL
# =========================================================

async def get_thumb(
    videoid: str,
) -> str:

    cache_path = os.path.join(
        CACHE_DIR,
        f"{videoid}_original.jpg",
    )

    # =====================================================
    # CACHE CHECK
    # =====================================================

    if os.path.exists(cache_path):
        return cache_path

    # =====================================================
    # BEST QUALITY THUMBNAIL URLS
    # =====================================================

    thumbnail_urls = [

        # MAX QUALITY WEBP
        f"https://i.ytimg.com/vi_webp/{videoid}/maxresdefault.webp",

        # MAX QUALITY JPG
        f"https://i.ytimg.com/vi/{videoid}/maxresdefault.jpg",

        # FALLBACKS
        f"https://i.ytimg.com/vi/{videoid}/sddefault.jpg",

        f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",

        f"https://i.ytimg.com/vi/{videoid}/mqdefault.jpg",
    ]

    thumb_path = os.path.join(
        CACHE_DIR,
        f"thumb_{videoid}.jpg",
    )

    downloaded = False

    # =====================================================
    # DOWNLOAD THUMBNAIL
    # =====================================================

    async with aiohttp.ClientSession() as session:

        for url in thumbnail_urls:

            try:

                async with session.get(url) as resp:

                    if resp.status == 200:

                        data = await resp.read()

                        # INVALID FILE CHECK
                        if len(data) < 1000:
                            continue

                        async with aiofiles.open(
                            thumb_path,
                            "wb",
                        ) as f:

                            await f.write(data)

                        downloaded = True
                        break

            except Exception:
                continue

    # =====================================================
    # DOWNLOAD FAILED
    # =====================================================

    if not downloaded:
        return YOUTUBE_IMG_URL

    # =====================================================
    # OPEN ORIGINAL IMAGE
    # =====================================================

    img = Image.open(
        thumb_path
    ).convert("RGB")

    # =====================================================
    # LIGHT QUALITY ENHANCEMENT
    # =====================================================

    img = ImageEnhance.Sharpness(
        img
    ).enhance(1.4)

    img = ImageEnhance.Contrast(
        img
    ).enhance(1.03)

    img = ImageEnhance.Color(
        img
    ).enhance(1.02)

    # =====================================================
    # SAVE ORIGINAL FULL THUMBNAIL
    # =====================================================

    img.save(

        cache_path,

        format="JPEG",

        quality=95,

        optimize=True,

        progressive=True,
    )

    # =====================================================
    # CLEANUP
    # =====================================================

    try:
        os.remove(thumb_path)

    except Exception:
        pass

    # =====================================================
    # RETURN FINAL IMAGE
    # =====================================================

    return cache_path


# =========================================================
# EXAMPLE
# =========================================================

# VIDEO:
# https://youtube.com/watch?v=T4crrkAmNoE

# VIDEO ID:
# T4crrkAmNoE

# USAGE:
#
# result = await get_thumb(
#     "T4crrkAmNoE"
# )
#
# print(result)

# OUTPUT:
# cache/T4crrkAmNoE_original.jpg
