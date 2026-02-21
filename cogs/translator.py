"""
TranslatorCog: 国旗リアクション → 翻訳 → スレッド投稿
"""

import logging

import discord
from discord.ext import commands

from utils.flag_map import FLAG_TO_LANG, is_flag_emoji
from utils.translator import translate

logger = logging.getLogger(__name__)

# スレッド名のプレフィックス（翻訳スレッドであることを識別するため）
TRANSLATION_THREAD_PREFIX = "💬 Translations"

# ボットが投稿した翻訳メッセージの識別マーカー
TRANSLATION_MARKER = "Translation (via"


class TranslatorCog(commands.Cog):
    """国旗リアクションで翻訳するコグ。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member | discord.User):
        """リアクション追加時のイベントハンドラ。"""

        # ボット自身のリアクションは無視
        if user.bot:
            return

        emoji = str(reaction.emoji)

        # 国旗絵文字でない場合は無視
        if not is_flag_emoji(emoji):
            return

        # 未対応の国旗の場合は無視
        lang_info = FLAG_TO_LANG.get(emoji)
        if lang_info is None:
            return

        message: discord.Message = reaction.message

        # ボット自身のメッセージは翻訳しない
        if message.author == self.bot.user:
            return

        # テキストが空のメッセージ（画像のみ等）はスキップ
        content = message.content.strip()
        if not content:
            logger.debug("テキストが空のため翻訳スキップ: message_id=%s", message.id)
            return

        deepl_lang = lang_info["deepl"]
        google_lang = lang_info["google"]
        lang_label = lang_info["label"]

        # --- スレッドの取得または作成 ---
        thread = await self._get_or_create_thread(message)
        if thread is None:
            logger.error("スレッドの取得・作成に失敗: message_id=%s", message.id)
            return

        # --- 重複チェック ---
        if await self._already_translated(thread, lang_label):
            logger.debug("翻訳済みのためスキップ: lang=%s, message_id=%s", lang_label, message.id)
            return

        # --- 翻訳実行 ---
        logger.info("翻訳開始: emoji=%s lang=%s message_id=%s", emoji, lang_label, message.id)
        translated_text, engine = translate(content, deepl_lang, google_lang)

        if translated_text is None:
            logger.error("翻訳失敗: message_id=%s", message.id)
            await thread.send(f"{emoji} **{lang_label} Translation failed.** (すべての翻訳エンジンが利用できませんでした)")
            return

        # --- スレッドに投稿 ---
        post = (
            f"{emoji} **{lang_label} Translation (via {engine}):**\n"
            f"{translated_text}"
        )
        await thread.send(post)
        logger.info("翻訳投稿完了: engine=%s lang=%s message_id=%s", engine, lang_label, message.id)

    async def _get_or_create_thread(self, message: discord.Message) -> discord.Thread | None:
        """
        メッセージに紐付くスレッドを返す。
        既存スレッドがあればそれを、なければ新規作成する。
        """
        # チャンネルがスレッドをサポートしているか確認
        if not isinstance(message.channel, (discord.TextChannel, discord.Thread)):
            return None

        # 既にスレッドの中のメッセージの場合はそのスレッドをそのまま使う
        if isinstance(message.channel, discord.Thread):
            return message.channel

        # メッセージに紐付くスレッドを探す
        try:
            # fetch_message でスレッドが添付されているか確認
            fetched = await message.channel.fetch_message(message.id)
            if fetched.thread:
                return fetched.thread
        except discord.NotFound:
            return None

        # スレッドがない場合は新規作成
        try:
            thread = await message.create_thread(name=TRANSLATION_THREAD_PREFIX)
            return thread
        except discord.Forbidden:
            logger.error(
                "スレッド作成権限がありません: channel=%s", message.channel.id
            )
            return None
        except discord.HTTPException as e:
            logger.error("スレッド作成失敗: %s", e)
            return None

    async def _already_translated(self, thread: discord.Thread, lang_label: str) -> bool:
        """
        同じ言語への翻訳が既にスレッドに投稿されているか確認する。
        """
        marker = f"**{lang_label} {TRANSLATION_MARKER}"
        try:
            async for msg in thread.history(limit=50):
                if msg.author == self.bot.user and marker in msg.content:
                    return True
        except discord.Forbidden:
            logger.warning("スレッド履歴の読み取り権限がありません: thread=%s", thread.id)
        except discord.HTTPException as e:
            logger.warning("スレッド履歴取得エラー: %s", e)
        return False


async def setup(bot: commands.Bot):
    await bot.add_cog(TranslatorCog(bot))
