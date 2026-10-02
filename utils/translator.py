"""
翻訳処理モジュール

優先順位:
  1. DeepL API Free（deepl_lang が None の言語はスキップ）
  2. MyMemory API（公式・無料・クレカ不要）
"""

from __future__ import annotations

import logging

import os
import re

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

# 言語判定用の正規表現パターン
HANGUL_RE = re.compile(r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]")
KANA_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")
KANJI_RE = re.compile(r"[\u4E00-\u9FFF]")

# 簡体字・繁体字および中国語特有の機能語・代名詞・表記
CHINESE_SPECIFIC_CHARS = set(
    "你您们么吗吧呢这那谁什没很还说话请问谢欢"
    "点让着跟比别快要真太买卖做吃喝读写东西"
    "个为对样现动经长关门题进节车气东"
    "汉语简体中文中国网电脑软件见岁"
)


def detect_language(text: str) -> str:
    """
    テキストのソース言語を検出する。
    1. ハングルが含まれていれば韓国語 ("ko") と確定。
    2. ひらがな・カタカナが1文字でも含まれていれば日本語 ("ja") と確定。
    3. 漢字が含まれている場合、中国語特有文字の有無や長さ・langdetect結果から "zh-cn" または "ja" を判定。
    4. それ以外（英字・キリル等）は langdetect で検出。
    """
    try:
        from utils.text_filter import clean_text_for_classification
        cleaned = clean_text_for_classification(text)
        if not cleaned:
            cleaned = text.strip() if text else ""
        if not cleaned:
            return "en"

        # 1. ハングル（韓国語確定）
        if HANGUL_RE.search(cleaned):
            return "ko"

        # 2. ひらがな・カタカナ（日本語確定）
        if KANA_RE.search(cleaned):
            return "ja"

        # 3. 漢字が含まれている場合（かな・ハングルがない）
        kanji_matches = KANJI_RE.findall(cleaned)
        if kanji_matches:
            # 中国語特有の文字・語彙が含まれている場合は中国語
            if any(c in CHINESE_SPECIFIC_CHARS for c in kanji_matches):
                return "zh-cn"

            # 4文字以下の短い漢字単語（了解、完了、確認、感謝、乾杯など）は日本語環境での相槌・報告として日本語扱い
            if len(kanji_matches) <= 4:
                return "ja"

            # 5文字以上の場合は langdetect による判定を試みる（ハングルはないため 'ko' は除外）
            try:
                from langdetect import detect_langs
                langs = detect_langs(cleaned)
                no_ko = [l for l in langs if l.lang != "ko"]
                if no_ko and no_ko[0].lang in ("zh-cn", "zh-tw") and no_ko[0].prob > 0.8:
                    return no_ko[0].lang
            except Exception:
                pass

            return "ja"

        # 4. 上記以外（英数字、キリル文字、タイ文字など）
        from langdetect import detect
        lang = detect(cleaned)
        return lang.lower()
    except Exception:
        return "en"


_detect_language = detect_language


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
    source_lang_limit: str | None = None
) -> tuple[str | None, str]:
    """
    テキストを翻訳する。

    Args:
        text:               翻訳対象テキスト
        deepl_lang:         DeepL 言語コード。None の場合は DeepL をスキップ。
        mymemory_lang:      MyMemory 言語コード（フォールバック用）
        source_lang_limit:  指定された元言語コード（例: 'ja'）。指定時はこの言語の発言のみ翻訳。

    Returns:
        (translated_text, engine_name)
        翻訳不要時は (None, "same_language") や (None, "source_lang_mismatch")
        翻訳失敗時は (None, "")
    """
    if not text or not text.strip():
        return None, ""

    # 自然言語テキストが含まれていない場合は翻訳不要
    from utils.text_filter import is_translatable_text
    translatable, reason = is_translatable_text(text)
    if not translatable:
        logger.info("非言語テキストのため翻訳スキップ (reason=%s): %s", reason, text[:50])
        return None, "non_translatable"

    # 0. ソース言語を検出
    detected = _detect_language(text)

    # 元言語制限が指定されている場合、一致しなければスキップ
    if source_lang_limit:
        clean_limit = source_lang_limit.strip().lower()
        if not detected.startswith(clean_limit):
            logger.info("ソース言語(%s)が指定された元言語制限(%s)と一致しないため翻訳スキップ", detected, clean_limit)
            return None, "source_lang_mismatch"

    # ターゲットと同じならAPI呼び出しをスキップ
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

