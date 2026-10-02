"""
TranslatorCog: リアクション → 翻訳 → スレッド投稿 → スレッドクローズ

国旗絵文字またはカスタム絵文字のリアクションをトリガーに翻訳する。
対応する絵文字はギルド単位の設定（emoji_config）で管理される。
"""

from __future__ import annotations

import logging


import discord
from discord.ext import commands

from utils.emoji_config import get_lang_info
from utils.translator import translate

logger = logging.getLogger(__name__)

TRANSLATION_THREAD_PREFIX = "💬 Translations"
TRANSLATION_MARKER = "Translation (via"


class TranslatorCog(commands.Cog):
    """リアクションで翻訳するコグ（国旗・カスタム絵文字対応）。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """リアクション追加時のイベントハンドラ（キャッシュにない古いメッセージにも対応）。"""

        # ボット自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            return

        emoji = str(payload.emoji)

        # DM（ギルド外）でのリアクションは無視
        if payload.guild_id is None:
            return

        # ギルド単位のマッピングから言語情報を取得
        lang_info = get_lang_info(payload.guild_id, emoji)
        if lang_info is None:
            return

        # チャンネルの取得
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return

        # メッセージの取得
        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            logger.error("メッセージの取得に失敗: message_id=%s", payload.message_id)
            return

        # ボットへのメッセージへのリアクションは無視
        if message.author == self.bot.user:
            return

        # ユーザー情報の取得（member が None の場合は fetch する）
        user = payload.member
        if user is None:
            try:
                user = await self.bot.fetch_user(payload.user_id)
            except discord.HTTPException:
                return

        if user.bot:
            return

        content = message.content.strip()
        if not content:
            logger.debug("テキストが空のため翻訳スキップ: message_id=%s", message.id)
            return

        deepl_lang    = lang_info["deepl"]      # None = DeepL非対応
        mymemory_lang = lang_info["mymemory"]
        lang_label    = lang_info["label"]

        # --- 翻訳実行（スレッド作成前に行い、同言語ならスキップ） ---
        logger.info("翻訳開始: emoji=%s lang=%s message_id=%s", emoji, lang_label, message.id)
        translated_text, engine = translate(content, deepl_lang, mymemory_lang)

        # ソース言語とターゲット言語が同じ場合、または非言語テキストの場合は何もしない
        if engine in ("same_language", "non_translatable"):
            logger.info("翻訳不要のためスキップ: engine=%s, lang=%s, message_id=%s", engine, lang_label, message.id)
            return

        # --- スレッドの取得または作成 ---
        thread, was_archived = await self._get_or_create_thread(message)
        if thread is None:
            logger.error("スレッドの取得・作成に失敗: message_id=%s", message.id)
            return

        # --- 重複チェック ---
        if await self._already_translated(thread, lang_label):
            logger.debug("翻訳済みのためスキップ: lang=%s, message_id=%s", lang_label, message.id)
            # アーカイブを元に戻す（元々閉じていた場合）
            if was_archived:
                await self._archive_thread(thread)
            return

        if translated_text is None:
            logger.error("翻訳失敗: message_id=%s", message.id)
            await thread.send(
                f"{emoji} **{lang_label} Translation failed.**\n"
                "（すべての翻訳エンジンが利用できませんでした）"
            )
        else:
            post = (
                f"{emoji} **{lang_label} Translation (via {engine}):**\n"
                f"{translated_text}"
            )
            await thread.send(post)
            logger.info("翻訳投稿完了: engine=%s lang=%s message_id=%s", engine, lang_label, message.id)

        # --- スレッドをクローズ（アーカイブ）---
        await self._archive_thread(thread)

    # ─────────────────────────────────────────────────────────────────────

    async def _get_or_create_thread(
        self, message: discord.Message
    ) -> tuple[discord.Thread | None, bool]:
        """
        メッセージに紐付くスレッドを返す。
        既存スレッドがあればそれを（アーカイブ済みなら解除して）、
        なければ新規作成する。

        Returns:
            (thread, was_archived)
            was_archived: 元々アーカイブ済みだったかどうか
        """
        if not isinstance(message.channel, (discord.TextChannel, discord.Thread)):
            return None, False

        # 既にスレッド内のメッセージの場合はそのスレッドを使う
        if isinstance(message.channel, discord.Thread):
            return message.channel, False

        # メッセージに紐付く既存スレッドを探す
        try:
            fetched = await message.channel.fetch_message(message.id)
            if fetched.thread:
                thread = fetched.thread
                was_archived = thread.archived
                if was_archived:
                    # アーカイブされていた場合は一時的に開く
                    try:
                        await thread.edit(archived=False)
                    except (discord.Forbidden, discord.HTTPException) as e:
                        logger.warning("スレッドのアーカイブ解除失敗: %s", e)
                return thread, was_archived
        except discord.NotFound:
            return None, False

        # スレッドがない場合は新規作成
        try:
            thread = await message.create_thread(name=TRANSLATION_THREAD_PREFIX)
            return thread, False
        except discord.Forbidden:
            logger.error("スレッド作成権限がありません: channel=%s", message.channel.id)
            return None, False
        except discord.HTTPException as e:
            logger.error("スレッド作成失敗: %s", e)
            return None, False

    async def _archive_thread(self, thread: discord.Thread) -> None:
        """スレッドをアーカイブ（クローズ）する。"""
        try:
            await thread.edit(archived=True)
            logger.info("スレッドをクローズしました: thread_id=%s", thread.id)
        except discord.Forbidden:
            logger.warning("スレッドのアーカイブ権限がありません: thread_id=%s", thread.id)
        except discord.HTTPException as e:
            logger.warning("スレッドのアーカイブ失敗: %s", e)

    async def _already_translated(self, thread: discord.Thread, lang_label: str) -> bool:
        """同じ言語への翻訳が既にスレッドに投稿されているか確認する。"""
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
