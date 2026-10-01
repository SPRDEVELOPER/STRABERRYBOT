import os
from typing import List

import yaml

languages = {}
languages_present = {}

# --- PREMIUM EMOJI REPLACEMENT ---
# Maps normal emojis to premium custom emoji HTML tags
PREMIUM_EMOJI_MAP = {
    "🎄": '<tg-emoji emoji-id="6122790473917537632">🎄</tg-emoji>',
    "🥀": '<tg-emoji emoji-id="6129415619885407680">🥀</tg-emoji>',
    "🦋": '<tg-emoji emoji-id="5956031393623445676">🦋</tg-emoji>',
    "🫧": '<tg-emoji emoji-id="5956031393623445676">🫧</tg-emoji>',
    "🪽": '<tg-emoji emoji-id="5956031393623445676">🪽</tg-emoji>',
    "⚡": '<tg-emoji emoji-id="6129639980387015660">⚡</tg-emoji>',
    "🏓": '<tg-emoji emoji-id="6129639980387015660">🏓</tg-emoji>',
    "📌": '<tg-emoji emoji-id="5859588916604047101">📌</tg-emoji>',
    "⏳": '<tg-emoji emoji-id="5854847234054558104">⏳</tg-emoji>',
    "⏰": '<tg-emoji emoji-id="5854847234054558104">⏰</tg-emoji>',
    "👀": '<tg-emoji emoji-id="6129639980387015660">👀</tg-emoji>',
    "📎": '<tg-emoji emoji-id="5859588916604047101">📎</tg-emoji>',
    "🔗": '<tg-emoji emoji-id="5859588916604047101">🔗</tg-emoji>',
    "🕚": '<tg-emoji emoji-id="5854847234054558104">🕚</tg-emoji>',
    "🎧": '<tg-emoji emoji-id="5859588916604047101">🎧</tg-emoji>',
    "😲": '<tg-emoji emoji-id="6122790473917537632">😲</tg-emoji>',
    "✨": '<tg-emoji emoji-id="5956031393623445676">✨</tg-emoji>',
    "🌸": '<tg-emoji emoji-id="5956031393623445676">🌸</tg-emoji>',
    "🌟": '<tg-emoji emoji-id="5956031393623445676">🌟</tg-emoji>',
    "🔥": '<tg-emoji emoji-id="6129639980387015660">🔥</tg-emoji>',
    "❤️": '<tg-emoji emoji-id="6122790473917537632">❤️</tg-emoji>',
    "🤍": '<tg-emoji emoji-id="6122790473917537632">🤍</tg-emoji>',
    "💗": '<tg-emoji emoji-id="6122790473917537632">💗</tg-emoji>',
    "🎶": '<tg-emoji emoji-id="5859588916604047101">🎶</tg-emoji>',
    "🎵": '<tg-emoji emoji-id="5859588916604047101">🎵</tg-emoji>',
    "🌈": '<tg-emoji emoji-id="5956031393623445676">🌈</tg-emoji>',
    "🌺": '<tg-emoji emoji-id="5956031393623445676">🌺</tg-emoji>',
    "🌞": '<tg-emoji emoji-id="6129639980387015660">🌞</tg-emoji>',
    "🤝": '<tg-emoji emoji-id="6122790473917537632">🤝</tg-emoji>',
}

def apply_premium_emojis(text):
    """Replace normal emojis with premium custom emoji tags in a string."""
    if not isinstance(text, str):
        return text
    for emoji, replacement in PREMIUM_EMOJI_MAP.items():
        text = text.replace(emoji, replacement)
    return text

def apply_premium_to_dict(lang_dict):
    """Apply premium emojis to all string values in a language dict."""
    for key in lang_dict:
        if isinstance(lang_dict[key], str):
            lang_dict[key] = apply_premium_emojis(lang_dict[key])
    return lang_dict


def get_string(lang: str):
    return languages[lang]


for filename in os.listdir(r"./strings/langs/"):
    if "en" not in languages:
        languages["en"] = yaml.safe_load(
            open(r"./strings/langs/en.yml", encoding="utf8")
        )
        languages_present["en"] = languages["en"]["name"]
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        if language_name == "en":
            continue
        languages[language_name] = yaml.safe_load(
            open(r"./strings/langs/" + filename, encoding="utf8")
        )
        for item in languages["en"]:
            if item not in languages[language_name]:
                languages[language_name][item] = languages["en"][item]
    try:
        languages_present[language_name] = languages[language_name]["name"]
    except:
        print("There is some issue with the language file inside bot.")
        exit()

# Apply premium emojis to all loaded languages
for lang in languages:
    languages[lang] = apply_premium_to_dict(languages[lang])
