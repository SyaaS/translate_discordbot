"""
国旗絵文字 → 言語コードのマッピング

deepl:     DeepL API の言語コード。None の場合 DeepL は非対応 → MyMemory に直行。
mymemory:  MyMemory API の言語コード（ISO 639-1 ベース）。
label:     人が読める言語名。
"""

FLAG_TO_LANG: dict[str, dict] = {
    # アジア
    "🇯🇵": {"deepl": "JA",    "mymemory": "ja",    "label": "Japanese"},
    "🇨🇳": {"deepl": "ZH",    "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "🇹🇼": {"deepl": "ZH",    "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "🇰🇷": {"deepl": "KO",    "mymemory": "ko",    "label": "Korean"},
    "🇻🇳": {"deepl": "VI",    "mymemory": "vi",    "label": "Vietnamese"},
    "🇹🇭": {"deepl": "TH",    "mymemory": "th",    "label": "Thai"},
    "🇮🇩": {"deepl": "ID",    "mymemory": "id",    "label": "Indonesian"},
    "🇲🇾": {"deepl": "MS",    "mymemory": "ms",    "label": "Malay"},
    "🇵🇭": {"deepl": None,    "mymemory": "tl",    "label": "Filipino"},   # DeepL 非対応
    "🇮🇳": {"deepl": "HI",    "mymemory": "hi",    "label": "Hindi"},
    "🇧🇩": {"deepl": "BN",    "mymemory": "bn",    "label": "Bengali"},
    "🇵🇰": {"deepl": "UR",    "mymemory": "ur",    "label": "Urdu"},
    "🇦🇿": {"deepl": "AZ",    "mymemory": "az",    "label": "Azerbaijani"},
    "🇰🇿": {"deepl": "KK",    "mymemory": "kk",    "label": "Kazakh"},
    "🇬🇪": {"deepl": "KA",    "mymemory": "ka",    "label": "Georgian"},
    "🇦🇲": {"deepl": "HY",    "mymemory": "hy",    "label": "Armenian"},

    # 中東
    "🇸🇦": {"deepl": "AR",    "mymemory": "ar",    "label": "Arabic"},
    "🇦🇪": {"deepl": "AR",    "mymemory": "ar",    "label": "Arabic"},
    "🇮🇱": {"deepl": "HE",    "mymemory": "he",    "label": "Hebrew"},
    "🇮🇷": {"deepl": "FA",    "mymemory": "fa",    "label": "Persian"},
    "🇹🇷": {"deepl": "TR",    "mymemory": "tr",    "label": "Turkish"},

    # ヨーロッパ
    "🇺🇸": {"deepl": "EN-US", "mymemory": "en",    "label": "English (US)"},
    "🇬🇧": {"deepl": "EN-GB", "mymemory": "en",    "label": "English (UK)"},
    "🇫🇷": {"deepl": "FR",    "mymemory": "fr",    "label": "French"},
    "🇩🇪": {"deepl": "DE",    "mymemory": "de",    "label": "German"},
    "🇪🇸": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish"},
    "🇵🇹": {"deepl": "PT-PT", "mymemory": "pt",    "label": "Portuguese (Portugal)"},
    "🇧🇷": {"deepl": "PT-BR", "mymemory": "pt",    "label": "Portuguese (Brazil)"},
    "🇮🇹": {"deepl": "IT",    "mymemory": "it",    "label": "Italian"},
    "🇳🇱": {"deepl": "NL",    "mymemory": "nl",    "label": "Dutch"},
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
    "🇷🇴": {"deepl": "RO",    "mymemory": "ro",    "label": "Romanian"},
    "🇧🇬": {"deepl": "BG",    "mymemory": "bg",    "label": "Bulgarian"},
    "🇬🇷": {"deepl": "EL",    "mymemory": "el",    "label": "Greek"},
    "🇭🇷": {"deepl": "HR",    "mymemory": "hr",    "label": "Croatian"},
    "🇷🇸": {"deepl": "SR",    "mymemory": "sr",    "label": "Serbian"},
    "🇸🇮": {"deepl": "SL",    "mymemory": "sl",    "label": "Slovenian"},
    "🇱🇹": {"deepl": "LT",    "mymemory": "lt",    "label": "Lithuanian"},
    "🇱🇻": {"deepl": "LV",    "mymemory": "lv",    "label": "Latvian"},
    "🇪🇪": {"deepl": "ET",    "mymemory": "et",    "label": "Estonian"},

    # アフリカ
    "🇿🇦": {"deepl": None,    "mymemory": "af",    "label": "Afrikaans"},   # DeepL 非対応
    "🇳🇬": {"deepl": None,    "mymemory": "yo",    "label": "Yoruba"},      # DeepL 非対応
    "🇰🇪": {"deepl": None,    "mymemory": "sw",    "label": "Swahili"},     # DeepL 非対応

    # アメリカ大陸
    "🇲🇽": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Mexico)"},
    "🇦🇷": {"deepl": "ES",    "mymemory": "es",    "label": "Spanish (Argentina)"},
    "🇨🇦": {"deepl": "EN-US", "mymemory": "en",    "label": "English (Canada)"},

    # オセアニア
    "🇦🇺": {"deepl": "EN-US", "mymemory": "en",    "label": "English (Australia)"},
    "🇳🇿": {"deepl": "EN-US", "mymemory": "en",    "label": "English (New Zealand)"},
}


def get_lang_info(emoji: str) -> dict | None:
    """国旗絵文字から言語情報を返す。未対応の場合は None を返す。"""
    return FLAG_TO_LANG.get(emoji)


def is_flag_emoji(emoji: str) -> bool:
    """絵文字が国旗（地域指示子2文字）かどうかを判定する。"""
    if len(emoji) != 2:
        return False
    return all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in emoji)
