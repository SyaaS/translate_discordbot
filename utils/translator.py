"""
翻訳処理モジュール

DeepL API Free をメインとし、失敗時は deep-translator (Google Translate) にフォールバック。
"""

import logging
import os

logger = logging.getLogger(__name__)


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


def translate_deepl(text: str, target_lang_deepl: str) -> str | None:
    """
    DeepL API で翻訳する。
    成功時は翻訳文字列、失敗時は None を返す。
    """
    translator = _get_deepl_translator()
    if translator is None:
        return None
    try:
        result = translator.translate_text(text, target_lang=target_lang_deepl)
        return result.text
    except Exception as e:
        logger.warning("DeepL 翻訳失敗 (target=%s): %s", target_lang_deepl, e)
        return None


def translate_google(text: str, target_lang_google: str) -> str | None:
    """
    deep-translator (Google Translate) で翻訳する。
    成功時は翻訳文字列、失敗時は None を返す。
    """
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target=target_lang_google).translate(text)
        return translated
    except Exception as e:
        logger.warning("Google Translate フォールバック失敗 (target=%s): %s", target_lang_google, e)
        return None


def translate(text: str, deepl_lang: str, google_lang: str) -> tuple[str | None, str]:
    """
    テキストを翻訳する。

    Returns:
        (translated_text, engine_name)
        翻訳失敗時は (None, "")
    """
    if not text or not text.strip():
        return None, ""

    # 1. DeepL で試みる
    result = translate_deepl(text, deepl_lang)
    if result:
        return result, "DeepL"

    # 2. Google Translate にフォールバック
    result = translate_google(text, google_lang)
    if result:
        return result, "Google Translate"

    return None, ""
