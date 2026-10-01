"""
ギルド単位の絵文字→言語マッピング設定管理

guild_emoji_config.json にギルドごとのカスタムマッピングと
デフォルト国旗の有効/無効設定を保存する。
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

from utils.flag_map import FLAG_TO_LANG, LETTER_TO_LANG

logger = logging.getLogger(__name__)

# 設定ファイルのパス（プロジェクトルート直下）
_CONFIG_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = _CONFIG_DIR / "guild_emoji_config.json"

# 言語プリセット: `/emoji add` の autocomplete で選択肢として使う
LANGUAGE_PRESETS: dict[str, dict[str, Any]] = {
    "Japanese":               {"deepl": "JA",      "mymemory": "ja",    "label": "Japanese"},
    "English (US)":           {"deepl": "EN-US",   "mymemory": "en",    "label": "English (US)"},
    "English (UK)":           {"deepl": "EN-GB",   "mymemory": "en",    "label": "English (UK)"},
    "Chinese (Simplified)":   {"deepl": "ZH-HANS", "mymemory": "zh-CN", "label": "Chinese (Simplified)"},
    "Chinese (Traditional)":  {"deepl": "ZH-HANT", "mymemory": "zh-TW", "label": "Chinese (Traditional)"},
    "Korean":                 {"deepl": "KO",      "mymemory": "ko",    "label": "Korean"},
    "Vietnamese":             {"deepl": "VI",      "mymemory": "vi",    "label": "Vietnamese"},
    "Thai":                   {"deepl": "TH",      "mymemory": "th",    "label": "Thai"},
    "Indonesian":             {"deepl": "ID",      "mymemory": "id",    "label": "Indonesian"},
    "Malay":                  {"deepl": "MS",      "mymemory": "ms",    "label": "Malay"},
    "Filipino":               {"deepl": None,      "mymemory": "tl",    "label": "Filipino"},
    "Hindi":                  {"deepl": "HI",      "mymemory": "hi",    "label": "Hindi"},
    "Bengali":                {"deepl": "BN",      "mymemory": "bn",    "label": "Bengali"},
    "Urdu":                   {"deepl": "UR",      "mymemory": "ur",    "label": "Urdu"},
    "Arabic":                 {"deepl": "AR",      "mymemory": "ar",    "label": "Arabic"},
    "Hebrew":                 {"deepl": "HE",      "mymemory": "he",    "label": "Hebrew"},
    "Persian":                {"deepl": "FA",      "mymemory": "fa",    "label": "Persian"},
    "Turkish":                {"deepl": "TR",      "mymemory": "tr",    "label": "Turkish"},
    "French":                 {"deepl": "FR",      "mymemory": "fr",    "label": "French"},
    "German":                 {"deepl": "DE",      "mymemory": "de",    "label": "German"},
    "Spanish":                {"deepl": "ES",      "mymemory": "es",    "label": "Spanish"},
    "Portuguese (Portugal)":  {"deepl": "PT-PT",   "mymemory": "pt",    "label": "Portuguese (Portugal)"},
    "Portuguese (Brazil)":    {"deepl": "PT-BR",   "mymemory": "pt",    "label": "Portuguese (Brazil)"},
    "Italian":                {"deepl": "IT",      "mymemory": "it",    "label": "Italian"},
    "Dutch":                  {"deepl": "NL",      "mymemory": "nl",    "label": "Dutch"},
    "Polish":                 {"deepl": "PL",      "mymemory": "pl",    "label": "Polish"},
    "Russian":                {"deepl": "RU",      "mymemory": "ru",    "label": "Russian"},
    "Ukrainian":              {"deepl": "UK",      "mymemory": "uk",    "label": "Ukrainian"},
    "Swedish":                {"deepl": "SV",      "mymemory": "sv",    "label": "Swedish"},
    "Norwegian":              {"deepl": "NB",      "mymemory": "no",    "label": "Norwegian"},
    "Danish":                 {"deepl": "DA",      "mymemory": "da",    "label": "Danish"},
    "Finnish":                {"deepl": "FI",      "mymemory": "fi",    "label": "Finnish"},
    "Czech":                  {"deepl": "CS",      "mymemory": "cs",    "label": "Czech"},
    "Slovak":                 {"deepl": "SK",      "mymemory": "sk",    "label": "Slovak"},
    "Hungarian":              {"deepl": "HU",      "mymemory": "hu",    "label": "Hungarian"},
    "Greek":                  {"deepl": "EL",      "mymemory": "el",    "label": "Greek"},
    "Afrikaans":              {"deepl": None,      "mymemory": "af",    "label": "Afrikaans"},
    "Swahili":                {"deepl": None,      "mymemory": "sw",    "label": "Swahili"},
}


# ── 内部データ ──────────────────────────────────────────────────────────────

_config: dict[str, Any] | None = None  # メモリ上のキャッシュ


def _default_guild_config() -> dict[str, Any]:
    """ギルドのデフォルト設定を返す。"""
    return {
        "custom_mappings": {},
        "disable_default_flags": False,
    }


def _default_config() -> dict[str, Any]:
    """設定ファイル全体のデフォルト構造を返す。"""
    return {"guilds": {}}


# ── 読み書き ────────────────────────────────────────────────────────────────

def load_config() -> dict[str, Any]:
    """設定ファイルを読み込む。なければデフォルトを返す。"""
    global _config
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _config = json.load(f)
                logger.info("設定ファイルを読み込みました: %s", CONFIG_PATH)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("設定ファイルの読み込みに失敗、デフォルトを使用: %s", e)
            _config = _default_config()
    else:
        _config = _default_config()
        logger.info("設定ファイルが存在しないためデフォルトを使用")
    return _config


def save_config() -> None:
    """現在のメモリ上の設定をファイルに書き出す。"""
    global _config
    if _config is None:
        return
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_config, f, ensure_ascii=False, indent=2)
        logger.info("設定ファイルを保存しました: %s", CONFIG_PATH)
    except OSError as e:
        logger.error("設定ファイルの保存に失敗: %s", e)


def _ensure_loaded() -> dict[str, Any]:
    """設定がメモリに読み込まれていなければ読み込む。"""
    global _config
    if _config is None:
        load_config()
    return _config  # type: ignore[return-value]


# ── ギルド設定の取得・操作 ──────────────────────────────────────────────────

def get_guild_config(guild_id: int) -> dict[str, Any]:
    """指定ギルドの設定を取得する（なければデフォルトを作成）。"""
    config = _ensure_loaded()
    gid = str(guild_id)
    if gid not in config["guilds"]:
        config["guilds"][gid] = _default_guild_config()
    return config["guilds"][gid]


def get_merged_map(guild_id: int) -> dict[str, dict]:
    """
    デフォルト国旗マッピングとカスタムマッピングをマージして返す。
    カスタム側が優先される（同じ絵文字ならカスタムで上書き）。
    disable_default_flags が True ならデフォルトは含めない。
    """
    guild_cfg = get_guild_config(guild_id)
    merged: dict[str, dict] = {}

    # 1. デフォルト国旗および文字マッピング（無効でなければ）
    if not guild_cfg.get("disable_default_flags", False):
        merged.update(FLAG_TO_LANG)
        merged.update(LETTER_TO_LANG)

    # 2. カスタムマッピング（上書き優先）
    merged.update(guild_cfg.get("custom_mappings", {}))

    return merged


def get_lang_info(guild_id: int, emoji: str) -> dict | None:
    """マージ済みマップから指定絵文字の言語情報を返す。未対応なら None。"""
    merged = get_merged_map(guild_id)
    res = merged.get(emoji)
    if res:
        return res
    clean = emoji.strip(":").lower()
    return merged.get(clean)


def add_custom_mapping(
    guild_id: int,
    emoji: str,
    deepl: str | None,
    mymemory: str,
    label: str,
) -> None:
    """カスタムマッピングを追加して保存する。"""
    guild_cfg = get_guild_config(guild_id)
    guild_cfg["custom_mappings"][emoji] = {
        "deepl": deepl,
        "mymemory": mymemory,
        "label": label,
    }
    save_config()
    logger.info("カスタムマッピング追加: guild=%s emoji=%s → %s", guild_id, emoji, label)


def remove_custom_mapping(guild_id: int, emoji: str) -> bool:
    """
    カスタムマッピングを削除して保存する。
    Returns: 削除できた場合 True、存在しなかった場合 False。
    """
    guild_cfg = get_guild_config(guild_id)
    if emoji in guild_cfg["custom_mappings"]:
        del guild_cfg["custom_mappings"][emoji]
        save_config()
        logger.info("カスタムマッピング削除: guild=%s emoji=%s", guild_id, emoji)
        return True
    return False


def set_disable_default_flags(guild_id: int, disabled: bool) -> None:
    """デフォルト国旗マッピングの有効/無効を切り替えて保存する。"""
    guild_cfg = get_guild_config(guild_id)
    guild_cfg["disable_default_flags"] = disabled
    save_config()
    state = "無効" if disabled else "有効"
    logger.info("デフォルト国旗マッピングを%sに変更: guild=%s", state, guild_id)
