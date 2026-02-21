"""
翻訳処理モジュール

優先順位:
  1. DeepL API Free（deepl_lang が None の言語はスキップ）
  2. MyMemory API（公式・無料・クレカ不要）
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"


# ── DeepL ──────────────────────────────────────────────────────────────────

def _get_deepl_translator():
    """deepl.Translator インスタンスを返す。APIキー未設定時は None。"""
    api_key = os.getenv("DEEPL_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        import deepl
        return deepl.Translator(api_key)
    except Exception as e:
        logger.warning("DeepL の初期化に失敗しました: %s", e)
        return None


def translate_deepl(text: str, target_lang: str) -> str | None:
    """
    DeepL API で翻訳する。
    成功時は翻訳文字列、失敗時は None を返す。
    """
    translator = _get_deepl_translator()
    if translator is None:
        return None
    try:
        result = translator.translate_text(text, target_lang=target_lang)
        return result.text
    except Exception as e:
        logger.warning("DeepL 翻訳失敗 (target=%s): %s", target_lang, e)
        return None


# ── MyMemory ───────────────────────────────────────────────────────────────

def _detect_language(text: str) -> str:
    """
    テキストのソース言語を検出する（langdetect 使用・オフライン・無料）。
    検出失敗時は "en" をデフォルトとして返す。
    """
    try:
        from langdetect import detect
        lang = detect(text)
        # langdetect は "zh-cn", "zh-tw" 等を返す場合がある
        return lang.lower()
    except Exception:
        return "en"


def translate_mymemory(text: str, target_lang: str) -> str | None:
    """
    MyMemory API で翻訳する（公式 REST API、クレカ不要）。

    無料枠:
      - 登録なし: 5,000 文字/日
      - メール登録 (MYMEMORY_EMAIL): 50,000 文字/日

    MyMemory は "auto" をソース言語として受け付けないため、
    langdetect でソース言語を自動検出して使用する。
    成功時は翻訳文字列、失敗時は None を返す。
    """
    email = os.getenv("MYMEMORY_EMAIL", "").strip()
    source_lang = _detect_language(text)

    # ソース言語とターゲット言語が同じ場合は翻訳不要
    if source_lang == target_lang:
        return None

    params: dict = {
        "q": text,
        "langpair": f"{source_lang}|{target_lang}",
    }
    if email:
        params["de"] = email

    try:
        resp = requests.get(MYMEMORY_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"]
        logger.warning("MyMemory API エラー: %s", data.get("responseDetails"))
        return None
    except Exception as e:
        logger.warning("MyMemory 翻訳失敗 (target=%s): %s", target_lang, e)
        return None


# ── 統合エントリポイント ────────────────────────────────────────────────────

def translate(
    text: str,
    deepl_lang: str | None,
    mymemory_lang: str,
) -> tuple[str | None, str]:
    """
    テキストを翻訳する。

    Args:
        text:          翻訳対象テキスト
        deepl_lang:    DeepL 言語コード。None の場合は DeepL をスキップ。
        mymemory_lang: MyMemory 言語コード（フォールバック用）

    Returns:
        (translated_text, engine_name)
        翻訳不要時は (None, "same_language")
        翻訳失敗時は (None, "")
    """
    if not text or not text.strip():
        return None, ""

    # 0. ソース言語を検出し、ターゲットと同じならAPI呼び出しをスキップ
    detected = _detect_language(text)
    # DeepL コードは "EN-US", "PT-BR" 等なのでプレフィックスで比較
    deepl_prefix = deepl_lang.split("-")[0].lower() if deepl_lang else None
    if detected == mymemory_lang or (deepl_prefix and detected == deepl_prefix):
        logger.info(
            "ソース言語(%s)とターゲット言語が同一のため翻訳スキップ", detected
        )
        return None, "same_language"

    # 1. DeepL が対応している言語のみ試みる
    if deepl_lang is not None:
        result = translate_deepl(text, deepl_lang)
        if result:
            return result, "DeepL"
        logger.info("DeepL 失敗 → MyMemory にフォールバック")

    # 2. MyMemory（公式フォールバック）
    result = translate_mymemory(text, mymemory_lang)
    if result:
        return result, "MyMemory"

    return None, ""

