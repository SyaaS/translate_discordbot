"""
テキストフィルタリング・分類ユーティリティ

Discord上で送信されたメッセージが、翻訳に値する自然言語のテキストを含んでいるかを判定する。
絵文字のみ、GIF/メディアURLのみ、ネットスラング（草、wwwなど）のみ、メンションのみの投稿を除外し、
無駄な翻訳APIリクエストや不要な翻訳スレッドの作成を防止する。
"""

from __future__ import annotations

import re
import unicodedata

# 1. URL パターン（Tenor, Giphy, Discord CDN, 通常URLなど）
URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)

# 2. Discord 固有構文
# カスタム絵文字: <:name:12345> またはアニメーション <a:name:12345>
DISCORD_CUSTOM_EMOJI_PATTERN = re.compile(r"<a?:[a-zA-Z0-9_~]+:\d+>")
# メンション: ユーザー <@123>, <@!123>, ロール <@&123>, チャンネル <#123>, スラッシュコマンド </name:123>, 全体メンション
DISCORD_MENTION_PATTERN = re.compile(r"<@!?\d+>|<@&\d+>|<#\d+>|</[a-zA-Z0-9_-]+:\d+>|@everyone|@here")
# タイムスタンプ: <t:1234567890:R> など
DISCORD_TIMESTAMP_PATTERN = re.compile(r"<t:\d+(:[a-zA-Z])?>")

# 3. コードブロック (```...```) または インラインコード (`...`)
CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```|`[^`\n]+`")

# 4. 単独で投稿されがちな非言語スラング・笑い表現（正規表現）
# 例: w, ww, www..., 草, 草草..., 8888 (拍手), lol, lool, lmao, hahaha, kkk...
LAUGHTER_PATTERNS = [
    re.compile(r"^[wWｗＷ]+$"),
    re.compile(r"^[草]+$"),
    re.compile(r"^[8８]+$"),  # 8888 (パチパチ)
    re.compile(r"^(l+o+l+|l+m+a+o+|r+o+f+l+|k{2,}|(ha)+h?|(he)+h?|(ja)+j?|h+a+h+a+|h+e+h+e+)$", re.IGNORECASE),
]

# 単独で投稿される非翻訳単語セット（完全一致小文字判定用）
NON_TRANSLATABLE_STANDALONE = {
    "w", "ww", "www", "草", "大草", "笑", "ワラ", "わら",
    "lol", "lmao", "rofl", "omg", "gg", "ggwp", "glhf",
    "ok", "okay", "ng", "yes", "no", "hi", "hey", "hello",
    "thx", "thanks", "ty", "np", "bye",
    "うん", "ううん", "はい", "いいえ", "おめ", "あり", "りょ", "おつ",
}


def clean_text_for_classification(text: str) -> str:
    """
    URL、Discordカスタム絵文字、メンション、タイムスタンプ、コードブロックを除去し、
    テキスト分類・言語判定のためのプレーンテキストを抽出する。
    """
    if not text:
        return ""

    # コードブロックを除去
    cleaned = CODE_BLOCK_PATTERN.sub(" ", text)
    # URLを除去
    cleaned = URL_PATTERN.sub(" ", cleaned)
    # カスタム絵文字を除去
    cleaned = DISCORD_CUSTOM_EMOJI_PATTERN.sub(" ", cleaned)
    # メンションを除去
    cleaned = DISCORD_MENTION_PATTERN.sub(" ", cleaned)
    # タイムスタンプを除去
    cleaned = DISCORD_TIMESTAMP_PATTERN.sub(" ", cleaned)

    return cleaned.strip()


def is_translatable_text(text: str) -> tuple[bool, str]:
    """
    メッセージが翻訳対象の自然言語テキストを含むかを判定する。

    Returns:
        (is_translatable, reason)
        - is_translatable: True なら翻訳対象、False ならスキップすべき非言語テキスト
        - reason: 判定の理由 ("valid", "empty", "url_only", "emoji_only", "laughter_only", "too_short" など)
    """
    if not text or not text.strip():
        return False, "empty"

    raw_stripped = text.strip()

    # 1. プレーンテキストの抽出（URLやDiscord特殊構文の除去）
    cleaned = clean_text_for_classification(raw_stripped)
    if not cleaned:
        # クリーニング後に空になった場合、元がURLのみか絵文字/メンションのみ
        if URL_PATTERN.search(raw_stripped):
            return False, "url_only"
        if DISCORD_CUSTOM_EMOJI_PATTERN.search(raw_stripped):
            return False, "custom_emoji_only"
        if DISCORD_MENTION_PATTERN.search(raw_stripped):
            return False, "mention_only"
        if CODE_BLOCK_PATTERN.search(raw_stripped):
            return False, "code_only"
        return False, "symbols_only"

    # 2. 単独スラング・相槌チェック
    cleaned_lower = cleaned.lower()
    if cleaned_lower in NON_TRANSLATABLE_STANDALONE:
        return False, "standalone_slang"

    for pattern in LAUGHTER_PATTERNS:
        if pattern.match(cleaned):
            return False, "laughter_only"

    # 3. Unicode文字種別のカウント
    # L* (Letter): 漢字、ひらがな、カタカナ、アルファベット、ハングル、キリルなど
    # N* (Number): 数字
    # S* (Symbol), P* (Punctuation), Z* (Separator), C* (Other)
    letters = []
    cjk_count = 0
    latin_count = 0
    other_letter_count = 0

    for ch in cleaned:
        cat = unicodedata.category(ch)
        if cat.startswith("L"):  # Letter
            letters.append(ch)
            # CJK（漢字・ひらがな・カタカナ・ハングルなど）の判定
            # U+3000-U+9FFF, U+AC00-U+D7AF
            code = ord(ch)
            if (
                0x3040 <= code <= 0x30FF or  # ひらがな・カタカナ
                0x4E00 <= code <= 0x9FFF or  # CJK統合漢字
                0x3400 <= code <= 0x4DBF or  # CJK統合漢字拡張A
                0xAC00 <= code <= 0xD7AF      # ハングル音節
            ):
                cjk_count += 1
            elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):  # Basic Latin A-Z, a-z
                latin_count += 1
            else:
                other_letter_count += 1

    total_letters = len(letters)

    # 有効な文字が一切ない（Unicode絵文字 😀 や記号 !?@#$%^&* のみの場合など）
    if total_letters == 0:
        return False, "emoji_or_symbols_only"

    # 4. 言語ごとの長さ・単語数閾値判定
    # (a) CJK文字が含まれている場合
    if cjk_count > 0:
        # CJKが2文字以上あれば自然言語の単語/文章として成立（例: 「了解」「行く」「待って」）
        # 1文字の場合（「草」「あ」「w」など）は非言語扱い
        if cjk_count >= 2:
            return True, "valid_cjk"
        # CJKが1文字でも他のアルファベットや文字と組み合わさっている場合（例: 「B組」「A棟」）
        if total_letters >= 3:
            return True, "valid_mixed"
        return False, "cjk_too_short"

    # (b) ラテン文字（英単語など）の場合
    if latin_count > 0:
        words = [w for w in re.split(r"\s+", cleaned) if any(c.isalpha() for c in w)]
        # 単語数が2語以上あれば文またはフレーズ（例: "see you", "good morning"）
        if len(words) >= 2:
            return True, "valid_latin_phrase"
        # 1単語の場合: 単語長が4文字以上かつネットスラング等でなければ翻訳対象
        # 例: "hello", "tomorrow", "awesome"
        # 短すぎる単語（"abc", "idk", "thx"等）はスキップ
        if latin_count >= 5:
            return True, "valid_latin_word"
        return False, "latin_too_short"

    # (c) その他の文字（ロシア語、タイ語、アラビア語等）
    if other_letter_count >= 2:
        return True, "valid_other"

    return False, "too_short"
