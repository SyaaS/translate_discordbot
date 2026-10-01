"""
国旗絵文字 → 言語コードのマッピング

deepl:     DeepL API の言語コード。None の場合 DeepL は非対応 → MyMemory に直行。
mymemory:  MyMemory API の言語コード（ISO 639-1 ベース）。
label:     人が読める言語名。
"""

from __future__ import annotations


FLAG_TO_LANG: dict[str, dict] = {
    # アジア
    "🇯🇵": {"deepl": "JA",    "mymemory": "ja",    "label": "Japanese"},
    "🇨🇳": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "🇭🇰": {"deepl": "ZH-HANT", "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "🇹🇼": {"deepl": "ZH-HANT", "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "🇲🇴": {"deepl": "ZH-HANT", "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "🇰🇷": {"deepl": "KO",    "mymemory": "ko",    "label": "Korean"},
    "🇻🇳": {"deepl": "VI",    "mymemory": "vi",    "label": "Vietnamese"},
    "🇹🇭": {"deepl": "TH",    "mymemory": "th",    "label": "Thai"},
    "🇮🇩": {"deepl": "ID",    "mymemory": "id",    "label": "Indonesian"},
    "🇲🇾": {"deepl": "MS",    "mymemory": "ms",    "label": "Malay"},
    "🇸🇬": {"deepl": "EN-US", "mymemory": "en",    "label": "English (Singapore)"},
    "🇵🇭": {"deepl": None,    "mymemory": "tl",    "label": "Filipino"},
    "🇮🇳": {"deepl": "HI",    "mymemory": "hi",    "label": "Hindi"},
    "🇧🇩": {"deepl": "BN",    "mymemory": "bn",    "label": "Bengali"},
    "🇵🇰": {"deepl": "UR",    "mymemory": "ur",    "label": "Urdu"},

    # 中東
    "🇸🇦": {"deepl": "AR",    "mymemory": "ar",    "label": "Arabic"},
    "🇦🇪": {"deepl": "AR",    "mymemory": "ar",    "label": "Arabic"},
    "🇶🇦": {"deepl": "AR",    "mymemory": "ar",    "label": "Arabic"},
    "🇮🇱": {"deepl": "HE",    "mymemory": "he",    "label": "Hebrew"},
    "🇮🇷": {"deepl": "FA",    "mymemory": "fa",    "label": "Persian"},
    "🇹🇷": {"deepl": "TR",    "mymemory": "tr",    "label": "Turkish"},

    # ヨーロッパ
    "🇺🇸": {"deepl": "EN-US", "mymemory": "en",    "label": "English (US)"},
    "🇺🇲": {"deepl": "EN-US", "mymemory": "en",    "label": "English (US) - UM"},
    "🇬🇧": {"deepl": "EN-GB", "mymemory": "en",    "label": "English (UK)"},
    "🇮🇪": {"deepl": "EN-GB", "mymemory": "en",    "label": "English (Ireland)"},
    "🇫🇷": {"deepl": "FR",    "mymemory": "fr",    "label": "French"},
    "🇲🇨": {"deepl": "FR",    "mymemory": "fr",    "label": "French (Monaco)"},
    "🇩🇪": {"deepl": "DE",    "mymemory": "de",    "label": "German"},
    "🇦🇹": {"deepl": "DE",    "mymemory": "de",    "label": "German (Austria)"},
    "🇨🇭": {"deepl": "DE",    "mymemory": "de",    "label": "German (Swiss)"},
    "🇪🇸": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish"},
    "🇵🇹": {"deepl": "PT-PT", "mymemory": "pt",    "label": "Portuguese (Portugal)"},
    "🇧🇷": {"deepl": "PT-BR", "mymemory": "pt",    "label": "Portuguese (Brazil)"},
    "🇮🇹": {"deepl": "IT",    "mymemory": "it",    "label": "Italian"},
    "🇳🇱": {"deepl": "NL",    "mymemory": "nl",    "label": "Dutch"},
    "🇧🇪": {"deepl": "NL",    "mymemory": "nl",    "label": "Dutch (Belgium)"},
    "🇵🇱": {"deepl": "PL",    "mymemory": "pl",    "label": "Polish"},
    "🇷🇺": {"deepl": "RU",    "mymemory": "ru",    "label": "Russian"},
    "🇺🇦": {"deepl": "UK",    "mymemory": "uk",    "label": "Ukrainian"},
    "🇸🇪": {"deepl": "SV",    "mymemory": "sv",    "label": "Swedish"},
    "🇳🇴": {"deepl": "NB",    "mymemory": "no",    "label": "Norwegian"},
    "🇩🇰": {"deepl": "DA",    "mymemory": "da",    "label": "Danish"},
    "🇫🇮": {"deepl": "FI",    "mymemory": "fi",    "label": "Finnish"},
    "🇨🇿": {"deepl": "CS",    "mymemory": "cs",    "label": "Czech"},
    "🇸🇰": {"deepl": "SK",    "mymemory": "sk",    "label": "Slovak"},
    "🇭🇺": {"deepl": "HU",    "mymemory": "hu",    "label": "Hungarian"},
    "🇬🇷": {"deepl": "EL",    "mymemory": "el",    "label": "Greek"},

    # アフリカ
    "🇿🇦": {"deepl": None,    "mymemory": "af",    "label": "Afrikaans"},
    "🇳🇬": {"deepl": None,    "mymemory": "yo",    "label": "Yoruba"},
    "🇰🇪": {"deepl": None,    "mymemory": "sw",    "label": "Swahili"},

    # アメリカ大陸
    "🇲🇽": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Mexico)"},
    "🇦🇷": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Argentina)"},
    "🇨🇱": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Chile)"},
    "🇨🇴": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Colombia)"},
    "🇵🇪": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Peru)"},
    "🇨🇦": {"deepl": "EN-US", "mymemory": "en",    "label": "English (Canada)"},

    # オセアニア
    "🇦🇺": {"deepl": "EN-US", "mymemory": "en",    "label": "English (Australia)"},
    "🇳🇿": {"deepl": "EN-US", "mymemory": "en",    "label": "English (New Zealand)"},
}


# アルファベット（Regional Indicator記号・文字絵文字）→ 言語コードマッピング
LETTER_TO_LANG: dict[str, dict] = {
    # J: Japanese
    "\U0001F1EF": {"deepl": "JA", "mymemory": "ja", "label": "Japanese"},
    "j": {"deepl": "JA", "mymemory": "ja", "label": "Japanese"},
    "J": {"deepl": "JA", "mymemory": "ja", "label": "Japanese"},

    # E: English
    "\U0001F1EA": {"deepl": "EN-US", "mymemory": "en", "label": "English"},
    "e": {"deepl": "EN-US", "mymemory": "en", "label": "English"},
    "E": {"deepl": "EN-US", "mymemory": "en", "label": "English"},

    # C: Chinese (Simplified)
    "\U0001F1E8": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "c": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "C": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},

    # K: Korean
    "\U0001F1F0": {"deepl": "KO", "mymemory": "ko", "label": "Korean"},
    "k": {"deepl": "KO", "mymemory": "ko", "label": "Korean"},
    "K": {"deepl": "KO", "mymemory": "ko", "label": "Korean"},

    # F: French
    "\U0001F1EB": {"deepl": "FR", "mymemory": "fr", "label": "French"},
    "f": {"deepl": "FR", "mymemory": "fr", "label": "French"},
    "F": {"deepl": "FR", "mymemory": "fr", "label": "French"},

    # D: German
    "\U0001F1E9": {"deepl": "DE", "mymemory": "de", "label": "German"},
    "d": {"deepl": "DE", "mymemory": "de", "label": "German"},
    "D": {"deepl": "DE", "mymemory": "de", "label": "German"},

    # S: Spanish
    "\U0001F1F8": {"deepl": "ES", "mymemory": "es", "label": "Spanish"},
    "s": {"deepl": "ES", "mymemory": "es", "label": "Spanish"},
    "S": {"deepl": "ES", "mymemory": "es", "label": "Spanish"},
}


def get_lang_info(emoji: str) -> dict | None:
    """国旗絵文字またはアルファベット記号から言語情報を返す。未対応の場合は None を返す。"""
    res = FLAG_TO_LANG.get(emoji)
    if res:
        return res
    res = LETTER_TO_LANG.get(emoji)
    if res:
        return res
    clean = emoji.strip(":").lower()
    return LETTER_TO_LANG.get(clean)


def is_flag_emoji(emoji: str) -> bool:
    """絵文字が国旗（地域指示子2文字）かどうかを判定する。"""
    if len(emoji) != 2:
        return False
    return all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in emoji)


CODE_TO_LANG: dict[str, dict] = {
    "ja": {"deepl": "JA", "mymemory": "ja", "label": "Japanese"},
    "japanese": {"deepl": "JA", "mymemory": "ja", "label": "Japanese"},
    "en": {"deepl": "EN-US", "mymemory": "en", "label": "English"},
    "english": {"deepl": "EN-US", "mymemory": "en", "label": "English"},
    "zh": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "chinese": {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "zh-tw": {"deepl": "ZH-HANT", "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "ko": {"deepl": "KO", "mymemory": "ko", "label": "Korean"},
    "korean": {"deepl": "KO", "mymemory": "ko", "label": "Korean"},
    "fr": {"deepl": "FR", "mymemory": "fr", "label": "French"},
    "french": {"deepl": "FR", "mymemory": "fr", "label": "French"},
    "de": {"deepl": "DE", "mymemory": "de", "label": "German"},
    "german": {"deepl": "DE", "mymemory": "de", "label": "German"},
    "es": {"deepl": "ES", "mymemory": "es", "label": "Spanish"},
    "spanish": {"deepl": "ES", "mymemory": "es", "label": "Spanish"},
    "pt": {"deepl": "PT-PT", "mymemory": "pt", "label": "Portuguese"},
    "portuguese": {"deepl": "PT-PT", "mymemory": "pt", "label": "Portuguese"},
    "it": {"deepl": "IT", "mymemory": "it", "label": "Italian"},
    "italian": {"deepl": "IT", "mymemory": "it", "label": "Italian"},
    "ru": {"deepl": "RU", "mymemory": "ru", "label": "Russian"},
    "russian": {"deepl": "RU", "mymemory": "ru", "label": "Russian"},
    "vi": {"deepl": "VI", "mymemory": "vi", "label": "Vietnamese"},
    "th": {"deepl": "TH", "mymemory": "th", "label": "Thai"},
    "id": {"deepl": "ID", "mymemory": "id", "label": "Indonesian"},
}


def get_lang_info_by_code(code: str) -> dict | None:
    """
    言語コード（例: 'en', 'ja', 'zh', 'french' 等）から言語情報を返す。
    見つからない場合は mymemory / deepl と一致するものが FLAG_TO_LANG 内にあればそれを動的に返す。
    """
    key = code.strip().lower()
    if key in CODE_TO_LANG:
        return CODE_TO_LANG[key]

    # FLAG_TO_LANG 内を検索
    for item in FLAG_TO_LANG.values():
        if item["mymemory"].lower() == key:
            return item
        if item.get("deepl") and item["deepl"].lower() == key:
            return item
        if item["label"].lower() == key:
            return item

    return None

