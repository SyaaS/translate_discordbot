"""
国旗絵文字 → 言語コードのマッピング

DeepL code: DeepL APIで使用する言語コード (大文字)
Google code: deep-translator (Google Translate) で使用する言語コード
label: 人が読める言語名
"""

# 国旗絵文字 → {"deepl": "...", "google": "...", "label": "..."}
FLAG_TO_LANG: dict[str, dict[str, str]] = {
    # アジア
    "🇯🇵": {"deepl": "JA",    "google": "ja",    "label": "Japanese"},
    "🇨🇳": {"deepl": "ZH",    "google": "zh-CN", "label": "Chinese (Simplified)"},
    "🇹🇼": {"deepl": "ZH",    "google": "zh-TW", "label": "Chinese (Traditional)"},
    "🇰🇷": {"deepl": "KO",    "google": "ko",    "label": "Korean"},
    "🇻🇳": {"deepl": "VI",    "google": "vi",    "label": "Vietnamese"},
    "🇹🇭": {"deepl": "TH",    "google": "th",    "label": "Thai"},
    "🇮🇩": {"deepl": "ID",    "google": "id",    "label": "Indonesian"},
    "🇲🇾": {"deepl": "MS",    "google": "ms",    "label": "Malay"},
    "🇵🇭": {"deepl": "EN-US", "google": "fil",   "label": "Filipino"},
    "🇮🇳": {"deepl": "HI",    "google": "hi",    "label": "Hindi"},
    "🇧🇩": {"deepl": "BN",    "google": "bn",    "label": "Bengali"},
    "🇵🇰": {"deepl": "UR",    "google": "ur",    "label": "Urdu"},
    "🇦🇿": {"deepl": "AZ",    "google": "az",    "label": "Azerbaijani"},
    "🇰🇿": {"deepl": "KK",    "google": "kk",    "label": "Kazakh"},
    "🇬🇪": {"deepl": "KA",    "google": "ka",    "label": "Georgian"},
    "🇦🇲": {"deepl": "HY",    "google": "hy",    "label": "Armenian"},

    # 中東
    "🇸🇦": {"deepl": "AR",    "google": "ar",    "label": "Arabic"},
    "🇦🇪": {"deepl": "AR",    "google": "ar",    "label": "Arabic"},
    "🇮🇱": {"deepl": "HE",    "google": "iw",    "label": "Hebrew"},
    "🇮🇷": {"deepl": "FA",    "google": "fa",    "label": "Persian"},
    "🇹🇷": {"deepl": "TR",    "google": "tr",    "label": "Turkish"},

    # ヨーロッパ
    "🇺🇸": {"deepl": "EN-US", "google": "en",    "label": "English (US)"},
    "🇬🇧": {"deepl": "EN-GB", "google": "en",    "label": "English (UK)"},
    "🇫🇷": {"deepl": "FR",    "google": "fr",    "label": "French"},
    "🇩🇪": {"deepl": "DE",    "google": "de",    "label": "German"},
    "🇪🇸": {"deepl": "ES",    "google": "es",    "label": "Spanish"},
    "🇵🇹": {"deepl": "PT-PT", "google": "pt",    "label": "Portuguese (Portugal)"},
    "🇧🇷": {"deepl": "PT-BR", "google": "pt",    "label": "Portuguese (Brazil)"},
    "🇮🇹": {"deepl": "IT",    "google": "it",    "label": "Italian"},
    "🇳🇱": {"deepl": "NL",    "google": "nl",    "label": "Dutch"},
    "🇵🇱": {"deepl": "PL",    "google": "pl",    "label": "Polish"},
    "🇷🇺": {"deepl": "RU",    "google": "ru",    "label": "Russian"},
    "🇺🇦": {"deepl": "UK",    "google": "uk",    "label": "Ukrainian"},
    "🇸🇪": {"deepl": "SV",    "google": "sv",    "label": "Swedish"},
    "🇳🇴": {"deepl": "NB",    "google": "no",    "label": "Norwegian"},
    "🇩🇰": {"deepl": "DA",    "google": "da",    "label": "Danish"},
    "🇫🇮": {"deepl": "FI",    "google": "fi",    "label": "Finnish"},
    "🇨🇿": {"deepl": "CS",    "google": "cs",    "label": "Czech"},
    "🇸🇰": {"deepl": "SK",    "google": "sk",    "label": "Slovak"},
    "🇭🇺": {"deepl": "HU",    "google": "hu",    "label": "Hungarian"},
    "🇷🇴": {"deepl": "RO",    "google": "ro",    "label": "Romanian"},
    "🇧🇬": {"deepl": "BG",    "google": "bg",    "label": "Bulgarian"},
    "🇬🇷": {"deepl": "EL",    "google": "el",    "label": "Greek"},
    "🇭🇷": {"deepl": "HR",    "google": "hr",    "label": "Croatian"},
    "🇷🇸": {"deepl": "SR",    "google": "sr",    "label": "Serbian"},
    "🇸🇮": {"deepl": "SL",    "google": "sl",    "label": "Slovenian"},
    "🇱🇹": {"deepl": "LT",    "google": "lt",    "label": "Lithuanian"},
    "🇱🇻": {"deepl": "LV",    "google": "lv",    "label": "Latvian"},
    "🇪🇪": {"deepl": "ET",    "google": "et",    "label": "Estonian"},

    # アフリカ
    "🇿🇦": {"deepl": "EN-US", "google": "af",    "label": "Afrikaans"},
    "🇳🇬": {"deepl": "EN-US", "google": "yo",    "label": "Yoruba"},
    "🇰🇪": {"deepl": "EN-US", "google": "sw",    "label": "Swahili"},

    # アメリカ大陸
    "🇲🇽": {"deepl": "ES",    "google": "es",    "label": "Spanish (Mexico)"},
    "🇦🇷": {"deepl": "ES",    "google": "es",    "label": "Spanish (Argentina)"},
    "🇨🇦": {"deepl": "EN-US", "google": "en",    "label": "English (Canada)"},

    # オセアニア
    "🇦🇺": {"deepl": "EN-US", "google": "en",    "label": "English (Australia)"},
    "🇳🇿": {"deepl": "EN-US", "google": "en",    "label": "English (New Zealand)"},
}


def get_lang_info(emoji: str) -> dict[str, str] | None:
    """国旗絵文字から言語情報を返す。未対応の場合は None を返す。"""
    return FLAG_TO_LANG.get(emoji)


def is_flag_emoji(emoji: str) -> bool:
    """絵文字が国旗（地域指示子2文字）かどうかを判定する。"""
    # 地域指示子は U+1F1E6–U+1F1FF の2文字で構成される
    if len(emoji) != 2:
        return False
    return all(0x1F1E6 <= ord(c) <= 0x1F1FF for c in emoji)
