import aiohttp
import aiofiles
import urllib.parse
import os
import time
import random
import re
import asyncio
from STRABERRY import app
from pyrogram import filters
from pyrogram.types import Message
from PIL import Image
import io
import json

# ---------------- CONFIG ----------------
POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY", "sk_XQP8gHCbIt4MwvQUCY1qQ1A5hZDzWval"
)
HF_API_KEY = os.getenv("HF_API_KEY", "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")
# ----------------------------------------

def to_small_caps(text: str) -> str:
    """Convert text to small caps style."""
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ',
        'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ',
        'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵'
    }
    return ''.join(mapping.get(c, c) for c in text)

# Adult content blocked words list
ADULT_WORDS = [
    "naked", "nude", "sex", "porn", "fuck", "xxx", "adult", "erotic", 
    "boobs", "breast", "vagina", "penis", "orgasm", "masturbate", 
    "intercourse", "blowjob", "anal", "dildo", "bdsm", "fetish",
    "stripping", "nudity", "explicit", "nsfw", "onlyfans", "pussy",
    "cock", "dick", "asshole", "tits", "horny", "cum", "sperm",
    "नग्न", "सेक्स", "बोब्स", "चूत", "लंड", "गांड", "हस्तमैथुन",
    "बलात्कार", "अश्लील", "कामुक", "bobs and vegana", "sex video", 
    "porn video", "adult video", "18+", "nsfw", "women boobs"
]

NSFW_PATTERNS = [
    r"(naked|nude|sex|porn|xxx|adult|erotic)",
    r"(boobs|breast|vagina|penis|orgasm)",
    r"(masturbat|intercourse|blowjob|anal|dildo|bdsm)",
    r"(nudity|explicit|nsfw|onlyfans)",
    r"(pussy|cock|dick|asshole|tits|horny|cum|sperm)",
    r"(नग्न|सेक्स|बोब्स|चूत|लंड|गांड|हस्तमैथुन)",
    r"(बलात्कार|अश्लील|कामुक)",
]

def is_adult_content(prompt: str) -> bool:
    """Check if prompt contains adult content."""
    prompt_lower = prompt.lower()
    
    for word in ADULT_WORDS:
        if word in prompt_lower:
            return True
    
    for pattern in NSFW_PATTERNS:
        if re.search(pattern, prompt_lower):
            return True
    
    return False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


async def is_valid_image(data: bytes) -> bool:
    """Check if bytes are a valid image."""
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        return True
    except Exception:
        return False


async def generate_from_pollinations(prompt: str, width: int, height: int) -> bytes | None:
    """Generate image using Pollinations API with API key."""
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://gen.pollinations.ai/image/{encoded}"
        f"?model=flux&width={width}&height={height}&nologo=true"
    )
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
    }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=180)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if await is_valid_image(data):
                        return data
    except Exception:
        pass
    return None


async def generate_from_hf(prompt: str) -> bytes | None:
    """Generate image using Hugging Face Inference API."""
    models = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "stabilityai/stable-diffusion-3.5-large-turbo",
        "runwayml/stable-diffusion-v1-5",
        "prompthero/openjourney-v4",
    ]
    headers = {
        **HEADERS,
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
    }
    for model in models:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            payload = json.dumps({"inputs": prompt, "parameters": {"negative_prompt": "nsfw, nude, naked, sex, porn, adult content"}})
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(
                    url, data=payload, timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        if await is_valid_image(data):
                            return data
        except Exception:
            continue
    return None


async def generate_from_pollinations_free(prompt: str, width: int, height: int) -> bytes | None:
    """Try Pollinations old endpoint without key."""
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 999999)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true"
    )
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if await is_valid_image(data):
                        return data
    except Exception:
        pass
    return None


async def generate_from_pollinations_turbo(prompt: str, width: int, height: int) -> bytes | None:
    """Try Pollinations turbo endpoint."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://pollinations.ai/p/{encoded}?width={width}&height={height}&model=turbo"
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if await is_valid_image(data):
                        return data
    except Exception:
        pass
    return None


async def generate_from_lexica(prompt: str) -> bytes | None:
    """Generate image using Lexica API (free)."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://lexica.art/api/v1/search?q={urllib.parse.quote(prompt)}", timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('images') and len(data['images']) > 0:
                        img_url = data['images'][0]['src']
                        async with session.get(img_url, timeout=60) as img_resp:
                            if img_resp.status == 200:
                                img_data = await img_resp.read()
                                if await is_valid_image(img_data):
                                    return img_data
    except Exception:
        pass
    return None


@app.on_message(filters.command(["img", "image"]))
async def generate_image(_, m: Message):
    """Generate high quality AI image from text prompt."""

    if len(m.command) < 2:
        await m.delete()
        msg = await m.reply_text(f"{to_small_caps('❗ please provide a prompt.')}")
        await asyncio.sleep(4)
        await msg.delete()
        return

    prompt = m.text.split(" ", 1)[1]
    
    await m.delete()
    
    # Check for adult content - short message
    if is_adult_content(prompt):
        msg = await m.reply_text(
            f"🚫 {to_small_caps('access denied!')}\n"
            f"{to_small_caps('adult content')}"
        )
        await asyncio.sleep(4)
        await msg.delete()
        return

    msg = await m.reply_text(f"{to_small_caps('🤖 gpt-5 mini vision initializing...')}")

    start_time = time.time()
    img_bytes = None

    # Method 1: Pollinations with API key
    if not img_bytes:
        img_bytes = await generate_from_pollinations(prompt, 1024, 1024)

    # Method 2: Hugging Face free tier
    if not img_bytes:
        await msg.edit(f"{to_small_caps('🤖 gpt-5 mini trying alternative source...')}")
        img_bytes = await generate_from_hf(prompt)

    # Method 3: Pollinations free
    if not img_bytes:
        await msg.edit(f"{to_small_caps('🤖 gpt-5 mini trying pollinations free...')}")
        img_bytes = await generate_from_pollinations_free(prompt, 1024, 1024)

    # Method 4: Pollinations Turbo
    if not img_bytes:
        await msg.edit(f"{to_small_caps('🤖 gpt-5 mini trying turbo mode...')}")
        img_bytes = await generate_from_pollinations_turbo(prompt, 1024, 1024)

    # Method 5: Lexica
    if not img_bytes:
        await msg.edit(f"{to_small_caps('🤖 gpt-5 mini trying lexica...')}")
        img_bytes = await generate_from_lexica(prompt)

    # Method 6: Direct Pollinations with enhanced prompt
    if not img_bytes:
        await msg.edit(f"{to_small_caps('🤖 gpt-5 mini trying final method...')}")
        enhanced_prompt = f"masterpiece, best quality, {prompt}"
        encoded = urllib.parse.quote(enhanced_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}"
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        if await is_valid_image(data):
                            img_bytes = data
        except Exception:
            pass

    # All methods failed
    if not img_bytes:
        await msg.edit(
            f"{to_small_caps('❌ gpt-5 mini error:')}\n\n"
            f"{to_small_caps('⚠️ failed to generate image. please try again.')}"
        )
        await asyncio.sleep(4)
        await msg.delete()
        return

    # Save file
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{m.from_user.id}_generated.jpg"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(img_bytes)

    elapsed = round(time.time() - start_time, 2)

    # Send as PHOTO with stylish small caps (ORIGINAL STYLE)
    await m.reply_photo(
        photo=file_path,
        caption=(
            f"✨ {to_small_caps('gpt-5 mini vision generated image')} ✔\n\n"
            f"📝 {to_small_caps('prompt')}: `{prompt}`\n"
            f"⏱️ {to_small_caps('time')}: `{elapsed}s`\n\n"
            f"⚡ {to_small_caps('powered by straberry music bot')}"
        ),
    )

    await msg.delete()

    # Cleanup
    try:
        os.remove(file_path)
    except Exception:
        pass
