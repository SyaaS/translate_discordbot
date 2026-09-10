"""
AutoTranslatorCog: チャンネル間自動翻訳転送機能（全自動/トリガー別モード・重複防止・本人認証対応）
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Optional

import discord
from discord.ext import commands

from utils.flag_map import get_lang_info_by_code
from utils.translator import translate

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join("data", "channel_config.json")
JUMP_URL_PATTERN = re.compile(r"https://discord\.com/channels/\d+/\d+/(\d+)")


def extract_source_message_id(embed: discord.Embed) -> Optional[int]:
    """
    転送先 Embed の内容（Jump to Message リンク）から、元メッセージのIDを抽出する。
    """
    for field in embed.fields:
        if field.name == "Original Message" and field.value:
            match = JUMP_URL_PATTERN.search(field.value)
            if match:
                return int(match.group(1))

    if embed.description:
        match = JUMP_URL_PATTERN.search(embed.description)
        if match:
            return int(match.group(1))

    return None


def parse_env_pairs(env_str: str) -> dict[str, list[dict]]:
    """
    環境変数 AUTO_TRANSLATE_PAIRS 文字列をパースする。
    フォーマット: "ソースID:ターゲットID:言語コード[:モード][:絵文字][:ユーザー1;ユーザー2],..."
    例: "333333333333333333:222222222222222222:en:trigger:🇺🇸:user1"
    """
    configs: dict[str, list[dict]] = {}
    if not env_str or not env_str.strip():
        return configs

    raw_items = env_str.split(",")
    for item in raw_items:
        item = item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) < 3:
            logger.warning("環境変数 AUTO_TRANSLATE_PAIRS のパース失敗 (形式不正): %s", item)
            continue

        source_id_str = parts[0].strip()
        target_id_str = parts[1].strip()
        lang_code = parts[2].strip()
        mode = parts[3].strip().lower() if len(parts) >= 4 and parts[3].strip() else "all"
        emoji = parts[4].strip() if len(parts) >= 5 and parts[4].strip() else None
        users_str = parts[5].strip() if len(parts) >= 6 and parts[5].strip() else None
        target_users = [u.strip() for u in users_str.split(";") if u.strip()] if users_str else None

        try:
            target_id = int(target_id_str)
        except ValueError:
            logger.warning("環境変数 AUTO_TRANSLATE_PAIRS のターゲットID不正: %s", target_id_str)
            continue

        lang_info = get_lang_info_by_code(lang_code)
        if not lang_info:
            logger.warning("環境変数 AUTO_TRANSLATE_PAIRS の言語コード不正: %s", lang_code)
            continue

        pair_data = {
            "target_channel_id": target_id,
            "target_lang_code": lang_code.lower(),
            "deepl_lang": lang_info.get("deepl"),
            "mymemory_lang": lang_info.get("mymemory"),
            "lang_label": lang_info.get("label"),
            "mode": mode,
            "emoji": emoji,
            "target_users": target_users,
            "is_from_env": True
        }

        if source_id_str not in configs:
            configs[source_id_str] = []

        if not any(
            p["target_channel_id"] == target_id 
            and p.get("mode", "all") == mode 
            and p.get("emoji") == emoji
            and p.get("target_users") == target_users
            for p in configs[source_id_str]
        ):
            configs[source_id_str].append(pair_data)

    return configs


class AutoTranslatorCog(commands.Cog):
    """指定したチャンネルの投稿を自動で翻訳して別チャンネルへ転送するコグ。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.configs: dict = self._load_configs()

    def _load_configs(self) -> dict:
        """設定ファイルおよび環境変数から設定を読み込んで構造化する。"""
        data = {
            "trigger_users": ["user1"],
            "trigger_emojis": ["🌐"],
            "channels": {}
        }

        # 1. ローカル JSON ファイルからの読み込み
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        # 旧形式データ（channel_id のみがルートキー）の判定と移行
                        if "channels" in loaded:
                            data["channels"] = loaded.get("channels", {})
                            data["trigger_users"] = loaded.get("trigger_users", ["user1"])
                            data["trigger_emojis"] = loaded.get("trigger_emojis", ["🌐"])
                        else:
                            data["channels"] = loaded
            except Exception as e:
                logger.error("設定ファイルの読み込みに失敗しました: %s", e)

        # 2. 環境変数 TRIGGER_USERS / TRIGGER_EMOJIS の上書き・マージ
        env_users = os.getenv("TRIGGER_USERS", "").strip()
        if env_users:
            data["trigger_users"] = [u.strip() for u in env_users.split(",") if u.strip()]

        env_emojis = os.getenv("TRIGGER_EMOJIS", "").strip()
        if env_emojis:
            data["trigger_emojis"] = [e.strip() for e in env_emojis.split(",") if e.strip()]

        # 3. 環境変数 AUTO_TRANSLATE_PAIRS からのペア自動マージ
        env_str = os.getenv("AUTO_TRANSLATE_PAIRS", "").strip()
        if env_str:
            env_channels = parse_env_pairs(env_str)
            for s_id, pairs in env_channels.items():
                if s_id not in data["channels"]:
                    data["channels"][s_id] = []
                for env_pair in pairs:
                    if not any(
                        p["target_channel_id"] == env_pair["target_channel_id"]
                        and p.get("mode", "all") == env_pair.get("mode", "all")
                        and p.get("emoji") == env_pair.get("emoji")
                        and p.get("target_users") == env_pair.get("target_users")
                        for p in data["channels"][s_id]
                    ):
                        data["channels"][s_id].append(env_pair)

        return data

    def _save_configs(self) -> None:
        """現在の設定構造をファイルに保存する。"""
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.configs, f, indent=2, ensure_ascii=False)
            logger.info("自動翻訳設定を保存しました")
        except Exception as e:
            logger.error("設定ファイルの保存に失敗しました: %s", e)

    async def _get_already_translated_source_ids(
        self,
        target_channel: discord.TextChannel,
        scan_limit: int = 500
    ) -> set[int]:
        """転送先チャンネルの過去ログから、既に転送済みの元メッセージID集合を取得する。"""
        translated_source_ids: set[int] = set()
        try:
            async for msg in target_channel.history(limit=scan_limit):
                if msg.author == self.bot.user and msg.embeds:
                    for embed in msg.embeds:
                        source_id = extract_source_message_id(embed)
                        if source_id:
                            translated_source_ids.add(source_id)
        except (discord.Forbidden, discord.HTTPException) as e:
            logger.warning("既転送メッセージのスキャンに失敗しました: %s", e)

        return translated_source_ids

    async def _send_translated_embed(
        self,
        message: discord.Message,
        target_channel: discord.abc.Messageable,
        deepl_lang: Optional[str],
        mymemory_lang: str,
        lang_label: str
    ) -> bool:
        """メッセージを翻訳し、指定のターゲットチャンネルに Embed で送信する共通ヘルパー。"""
        content = message.content.strip()
        if not content:
            return False

        translated_text, engine = translate(content, deepl_lang, mymemory_lang)

        if engine == "same_language" or not translated_text:
            return False

        embed = discord.Embed(
            description=translated_text,
            color=discord.Color.blue(),
            timestamp=message.created_at
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url
        )
        embed.set_footer(
            text=f"Translated to {lang_label} via {engine} | Source: #{message.channel.name if hasattr(message.channel, 'name') else 'channel'}"
        )
        embed.add_field(
            name="Original Message",
            value=f"[Jump to Message]({message.jump_url})",
            inline=False
        )

        try:
            await target_channel.send(embed=embed)
            return True
        except (discord.Forbidden, discord.HTTPException) as e:
            logger.error("自動翻訳メッセージ送信失敗: %s", e)
            return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """メッセージ投稿時に全自動翻訳 (mode == 'all') を行うリスナー。"""

        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        source_channel_id = str(message.channel.id)
        channels_config = self.configs.get("channels", {})
        if source_channel_id not in channels_config:
            return

        # mode == 'all' のペアのみを全自動翻訳対象とする
        all_pairs = [p for p in channels_config[source_channel_id] if p.get("mode", "all") == "all"]
        for pair in all_pairs:
            # 特定ユーザー限定フィルタが設定されている場合の検証
            target_users = pair.get("target_users")
            if target_users:
                author_match = (
                    str(message.author.id) in target_users
                    or message.author.name.lower() in [u.lower() for u in target_users]
                    or message.author.display_name.lower() in [u.lower() for u in target_users]
                )
                if not author_match:
                    continue

            target_channel_id = pair["target_channel_id"]
            deepl_lang = pair.get("deepl_lang")
            mymemory_lang = pair.get("mymemory_lang")
            lang_label = pair.get("lang_label", "Unknown")

            target_channel = self.bot.get_channel(target_channel_id)
            if target_channel is None:
                try:
                    target_channel = await self.bot.fetch_channel(target_channel_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                    logger.error("ターゲットチャンネル (%s) の取得失敗: %s", target_channel_id, e)
                    continue

            await self._send_translated_embed(
                message=message,
                target_channel=target_channel,
                deepl_lang=deepl_lang,
                mymemory_lang=mymemory_lang,
                lang_label=lang_label
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        リアクション追加時に特定ユーザー＆特定スタンプでトリガー翻訳 (mode == 'trigger') を行うリスナー。
        【解決策A】発言者本人かつリアクション実行者が対象ユーザーに含まれること。
        """

        if payload.user_id == self.bot.user.id:
            return

        emoji_str = str(payload.emoji)
        source_channel_id = str(payload.channel_id)
        channels_config = self.configs.get("channels", {})
        if source_channel_id not in channels_config:
            return

        all_trigger_pairs = [p for p in channels_config[source_channel_id] if p.get("mode") == "trigger"]
        if not all_trigger_pairs:
            return

        # 押された絵文字がペア個別設定または全体トリガー設定とマッチするペアのみ抽出
        global_trigger_emojis = self.configs.get("trigger_emojis", ["🌐"])
        matching_pairs = []
        for pair in all_trigger_pairs:
            pair_emoji = pair.get("emoji")
            if pair_emoji:
                is_match = (
                    emoji_str == pair_emoji
                    or (payload.emoji.id and str(payload.emoji.id) in pair_emoji)
                    or (payload.emoji.name and payload.emoji.name == pair_emoji)
                )
                if is_match:
                    matching_pairs.append(pair)
            else:
                if emoji_str in global_trigger_emojis:
                    matching_pairs.append(pair)

        if not matching_pairs:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                return

        try:
            message = await channel.fetch_message(payload.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return

        if message.author.bot:
            return

        reactor = payload.member
        if reactor is None:
            try:
                reactor = await self.bot.fetch_user(payload.user_id)
            except discord.HTTPException:
                return

        global_trigger_users = self.configs.get("trigger_users", ["user1"])

        # 該当する各ペアについて、発言者＆実行者検証を行って翻訳投稿
        for pair in matching_pairs:
            pair_users = pair.get("target_users") or global_trigger_users

            # 1. メッセージ発言者の検証
            author_match = (
                str(message.author.id) in pair_users
                or message.author.name.lower() in [u.lower() for u in pair_users]
                or message.author.display_name.lower() in [u.lower() for u in pair_users]
            )
            if not author_match:
                continue

            # 2. リアクション実行者の検証 (解決策A: 押した人自身も対象ユーザーであること)
            reactor_match = (
                str(reactor.id) in pair_users
                or reactor.name.lower() in [u.lower() for u in pair_users]
                or (hasattr(reactor, "display_name") and reactor.display_name.lower() in [u.lower() for u in pair_users])
            )
            if not reactor_match:
                logger.debug("リアクション実行者 (%s) がトリガー対象外ユーザーのためスキップ", reactor)
                continue

            # 3. 転送先へ翻訳投稿
            target_channel_id = pair["target_channel_id"]
            deepl_lang = pair.get("deepl_lang")
            mymemory_lang = pair.get("mymemory_lang")
            lang_label = pair.get("lang_label", "Unknown")

            target_channel = self.bot.get_channel(target_channel_id)
            if target_channel is None:
                try:
                    target_channel = await self.bot.fetch_channel(target_channel_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    continue

            # 二重投稿の自動判定
            already_ids = await self._get_already_translated_source_ids(target_channel, scan_limit=200)
            if message.id in already_ids:
                logger.debug("既に転送先に存在するメッセージのためスキップ: msg_id=%s", message.id)
                continue

            await self._send_translated_embed(
                message=message,
                target_channel=target_channel,
                deepl_lang=deepl_lang,
                mymemory_lang=mymemory_lang,
                lang_label=lang_label
            )

    @commands.group(name="auto_translate", aliases=["at"], invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def auto_translate(self, ctx: commands.Context):
        """チャンネル自動翻訳コマンドのルートグループ。"""
        await ctx.send_help(ctx.command)

    def _add_pair_internal(
        self,
        source_channel: discord.TextChannel,
        target_channel: discord.TextChannel,
        lang_info: dict,
        lang_code: str,
        mode: str,
        emoji: Optional[str] = None,
        target_users: Optional[list[str]] = None
    ):
        source_id = str(source_channel.id)
        new_pair = {
            "target_channel_id": target_channel.id,
            "target_lang_code": lang_code.lower(),
            "deepl_lang": lang_info.get("deepl"),
            "mymemory_lang": lang_info.get("mymemory"),
            "lang_label": lang_info.get("label"),
            "mode": mode,
            "emoji": emoji,
            "target_users": target_users
        }

        if "channels" not in self.configs:
            self.configs["channels"] = {}

        if source_id not in self.configs["channels"]:
            self.configs["channels"][source_id] = []

        updated = False
        for i, pair in enumerate(self.configs["channels"][source_id]):
            if (
                pair["target_channel_id"] == target_channel.id 
                and pair.get("mode", "all") == mode
                and pair.get("emoji") == emoji
                and pair.get("target_users") == target_users
            ):
                self.configs["channels"][source_id][i] = new_pair
                updated = True
                break

        if not updated:
            self.configs["channels"][source_id].append(new_pair)

        self._save_configs()

    @auto_translate.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def add_pair(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: discord.TextChannel,
        lang_code: str,
        target_user: Optional[str] = None
    ):
        """全自動翻訳ペアを追加します。（[target_user] 指定時は特定ユーザーのみ自動翻訳）"""
        lang_info = get_lang_info_by_code(lang_code)
        if not lang_info:
            await ctx.send(f"❌ 指定された言語コード `{lang_code}` が見つかりません。")
            return

        target_users = [target_user] if target_user else None
        self._add_pair_internal(
            source_channel, target_channel, lang_info, lang_code, mode="all", target_users=target_users
        )
        user_info = f"\n• 対象ユーザー: **{target_user}** 限定" if target_user else " (全ユーザー対象)"
        await ctx.send(
            f"✅ **全自動翻訳ペア**を設定しました！\n"
            f"• 転送元: {source_channel.mention}\n"
            f"• 転送先: {target_channel.mention}\n"
            f"• 言語: **{lang_info['label']}** (`{lang_code}`)\n"
            f"• モード: **全自動翻訳**{user_info}"
        )

    @auto_translate.command(name="add_trigger")
    @commands.has_permissions(manage_channels=True)
    async def add_trigger_pair(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: discord.TextChannel,
        lang_code: str,
        emoji: Optional[str] = None,
        target_user: Optional[str] = None
    ):
        """特定スタンプ・特定ユーザー指定のトリガー翻訳ペアを追加します。"""
        lang_info = get_lang_info_by_code(lang_code)
        if not lang_info:
            await ctx.send(f"❌ 指定された言語コード `{lang_code}` が見つかりません。")
            return

        target_users = [target_user] if target_user else None
        self._add_pair_internal(
            source_channel, target_channel, lang_info, lang_code, mode="trigger", emoji=emoji, target_users=target_users
        )
        
        global_users = ", ".join(self.configs.get("trigger_users", ["user1"]))
        global_emojis = " ".join(self.configs.get("trigger_emojis", ["🌐"]))

        emoji_str = emoji if emoji else f"{global_emojis} (全体設定)"
        user_str = target_user if target_user else f"{global_users} (全体設定)"

        await ctx.send(
            f"✅ **トリガー限定翻訳ペア**を設定しました！\n"
            f"• 転送元: {source_channel.mention}\n"
            f"• 転送先: {target_channel.mention}\n"
            f"• 言語: **{lang_info['label']}** (`{lang_code}`)\n"
            f"• トリガースタンプ: {emoji_str}\n"
            f"• 対象ユーザー: **{user_str}**\n"
            f"💡 対象ユーザーが発言し、指定スタンプが押された時のみ翻訳転送されます。"
        )

    # ── トリガーユーザー管理グループ ──
    @auto_translate.group(name="trigger_user", invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def trigger_user_group(self, ctx: commands.Context):
        """トリガー対象ユーザー管理コマンド。"""
        await ctx.send_help(ctx.command)

    @trigger_user_group.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def add_trigger_user(self, ctx: commands.Context, username_or_id: str):
        """トリガー対象ユーザーを追加します。"""
        users = self.configs.get("trigger_users", ["user1"])
        if username_or_id not in users:
            users.append(username_or_id)
            self.configs["trigger_users"] = users
            self._save_configs()
            await ctx.send(f"✅ トリガー対象ユーザーに `{username_or_id}` を追加しました。")
        else:
            await ctx.send(f"ℹ️ `{username_or_id}` は既にトリガー対象に登録されています。")

    @trigger_user_group.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def remove_trigger_user(self, ctx: commands.Context, username_or_id: str):
        """トリガー対象ユーザーを削除します。"""
        users = self.configs.get("trigger_users", ["user1"])
        if username_or_id in users:
            users.remove(username_or_id)
            self.configs["trigger_users"] = users
            self._save_configs()
            await ctx.send(f"✅ トリガー対象ユーザーから `{username_or_id}` を削除しました。")
        else:
            await ctx.send(f"⚠️ `{username_or_id}` はトリガー対象に登録されていません。")

    @trigger_user_group.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def list_trigger_users(self, ctx: commands.Context):
        """トリガー対象ユーザー一覧を表示します。"""
        users = self.configs.get("trigger_users", ["user1"])
        await ctx.send(f"👤 **現在のトリガー対象ユーザー**: {', '.join(users) if users else 'なし'}")

    # ── トリガースタンプ管理グループ ──
    @auto_translate.group(name="trigger_emoji", invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def trigger_emoji_group(self, ctx: commands.Context):
        """トリガースタンプ（絵文字）管理コマンド。"""
        await ctx.send_help(ctx.command)

    @trigger_emoji_group.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def add_trigger_emoji(self, ctx: commands.Context, emoji: str):
        """トリガースタンプ（絵文字）を追加します。"""
        emojis = self.configs.get("trigger_emojis", ["🌐"])
        if emoji not in emojis:
            emojis.append(emoji)
            self.configs["trigger_emojis"] = emojis
            self._save_configs()
            await ctx.send(f"✅ トリガースタンプに {emoji} を追加しました。")
        else:
            await ctx.send(f"ℹ️ {emoji} は既に登録されています。")

    @trigger_emoji_group.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def remove_trigger_emoji(self, ctx: commands.Context, emoji: str):
        """トリガースタンプ（絵文字）を削除します。"""
        emojis = self.configs.get("trigger_emojis", ["🌐"])
        if emoji in emojis:
            emojis.remove(emoji)
            self.configs["trigger_emojis"] = emojis
            self._save_configs()
            await ctx.send(f"✅ トリガースタンプから {emoji} を削除しました。")
        else:
            await ctx.send(f"⚠️ {emoji} は登録されていません。")

    @trigger_emoji_group.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def list_trigger_emojis(self, ctx: commands.Context):
        """トリガースタンプ一覧を表示します。"""
        emojis = self.configs.get("trigger_emojis", ["🌐"])
        await ctx.send(f"🎨 **現在のトリガースタンプ**: {' '.join(emojis) if emojis else 'なし'}")

    @auto_translate.command(name="trigger_info")
    @commands.has_permissions(manage_channels=True)
    async def trigger_info(self, ctx: commands.Context):
        """トリガー翻訳設定の総合情報を表示します。"""
        users = ", ".join(self.configs.get("trigger_users", ["user1"]))
        emojis = " ".join(self.configs.get("trigger_emojis", ["🌐"]))

        embed = discord.Embed(
            title="⚙️ トリガー自動翻訳 設定情報",
            color=discord.Color.gold()
        )
        embed.add_field(name="👤 対象ユーザー", value=users or "なし", inline=False)
        embed.add_field(name="🎨 トリガースタンプ", value=emojis or "なし", inline=False)

        channels_config = self.configs.get("channels", {})
        count = 0
        for s_id, pairs in channels_config.items():
            s_chan = self.bot.get_channel(int(s_id))
            s_name = s_chan.mention if s_chan else f"ID: {s_id}"

            for pair in pairs:
                if pair.get("mode") == "trigger":
                    t_chan = self.bot.get_channel(pair["target_channel_id"])
                    t_name = t_chan.mention if t_chan else f"ID: {pair['target_channel_id']}"
                    embed.add_field(
                        name=f"Trigger Pair #{count + 1}",
                        value=f"• **転送元**: {s_name}\n• **転送先**: {t_name}\n• **言語**: {pair.get('lang_label')}",
                        inline=False
                    )
                    count += 1

        if count == 0:
            embed.add_field(name="🌐 トリガーペア", value="登録されているトリガー限定ペアはありません。", inline=False)

        await ctx.send(embed=embed)

    @auto_translate.command(name="backfill")
    @commands.has_permissions(manage_channels=True)
    async def backfill_messages(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: discord.TextChannel,
        lang_code: str,
        limit: int = 100,
        after_message_id: Optional[int] = None
    ):
        """過去ログを古い順から一括で翻訳・転送します（重複自動スキップ機能付き）。"""
        lang_info = get_lang_info_by_code(lang_code)
        if not lang_info:
            await ctx.send(f"❌ 指定された言語コード `{lang_code}` が見つかりません。")
            return

        if limit < 1 or limit > 1000:
            await ctx.send("⚠️ 取得件数は 1〜1000 件の間で指定してください。")
            return

        after_msg = None
        if after_message_id is not None:
            try:
                after_msg = await source_channel.fetch_message(after_message_id)
            except discord.NotFound:
                await ctx.send(f"❌ 指定された開始メッセージID `{after_message_id}` が見つかりませんでした。")
                return
            except (discord.Forbidden, discord.HTTPException) as e:
                await ctx.send(f"❌ メッセージの取得に失敗しました: {e}")
                return

        status_msg = await ctx.send("🔄 転送先チャンネルの既存ログをスキャン中...")

        already_translated_ids = await self._get_already_translated_source_ids(target_channel)

        after_info = f" (メッセージID: `{after_message_id}` の直後から)" if after_message_id else ""
        await status_msg.edit(
            content=(
                f"🔄 {source_channel.mention} の過去メッセージ（最大 {limit} 件）を古い順から翻訳中{after_info}...\n"
                f"転送先: {target_channel.mention} | 言語: **{lang_info['label']}** (検出済み転送済み: {len(already_translated_ids)} 件スキップ可能)"
            )
        )

        deepl_lang = lang_info.get("deepl")
        mymemory_lang = lang_info.get("mymemory")
        lang_label = lang_info.get("label", "Unknown")

        processed_count = 0
        translated_count = 0
        skipped_duplicate_count = 0

        history_kwargs = {
            "limit": limit,
            "oldest_first": True,
        }
        if after_msg:
            history_kwargs["after"] = after_msg

        async for message in source_channel.history(**history_kwargs):
            if message.author.bot or not message.content.strip():
                continue

            msg_ctx = await self.bot.get_context(message)
            if msg_ctx.valid:
                continue

            if message.id in already_translated_ids:
                skipped_duplicate_count += 1
                continue

            processed_count += 1
            success = await self._send_translated_embed(
                message=message,
                target_channel=target_channel,
                deepl_lang=deepl_lang,
                mymemory_lang=mymemory_lang,
                lang_label=lang_label
            )

            if success:
                translated_count += 1
                await asyncio.sleep(1.2)

        await status_msg.edit(
            content=(
                f"✅ **バックフィル完了！**\n"
                f"• 転送元: {source_channel.mention}\n"
                f"• 転送先: {target_channel.mention}\n"
                f"• 処理メッセージ数: **{translated_count} 件** を新規翻訳転送しました。\n"
                f"• スキップ件数: 既転送済み重複 `{skipped_duplicate_count}` 件 / 対象外 `{processed_count - translated_count}` 件"
            )
        )

    @auto_translate.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def remove_pair(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: Optional[discord.TextChannel] = None
    ):
        """自動翻訳ペアを削除します。"""
        source_id = str(source_channel.id)
        channels_config = self.configs.get("channels", {})
        if source_id not in channels_config or not channels_config[source_id]:
            await ctx.send(f"⚠️ {source_channel.mention} には自動翻訳設定がありません。")
            return

        if target_channel is None:
            del channels_config[source_id]
            self._save_configs()
            await ctx.send(f"✅ {source_channel.mention} からの自動翻訳設定をすべて削除しました。")
        else:
            original_len = len(channels_config[source_id])
            channels_config[source_id] = [
                p for p in channels_config[source_id] if p["target_channel_id"] != target_channel.id
            ]
            if len(channels_config[source_id]) == 0:
                del channels_config[source_id]

            if len(channels_config.get(source_id, [])) < original_len:
                self._save_configs()
                await ctx.send(
                    f"✅ {source_channel.mention} → {target_channel.mention} の自動翻訳設定を削除しました。"
                )
            else:
                await ctx.send(
                    f"⚠️ {source_channel.mention} から {target_channel.mention} への自動翻訳設定は見つかりませんでした。"
                )

    @auto_translate.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def list_pairs(self, ctx: commands.Context):
        """設定中の自動翻訳ペア一覧を表示します。"""
        channels_config = self.configs.get("channels", {})
        if not channels_config:
            await ctx.send("ℹ️ 現在設定されている自動翻訳ペアはありません。")
            return

        embed = discord.Embed(
            title="🌐 チャンネル自動翻訳 一覧",
            color=discord.Color.green()
        )

        count = 0
        for source_id, pairs in channels_config.items():
            source_chan = self.bot.get_channel(int(source_id))
            source_name = source_chan.mention if source_chan else f"ID: {source_id}"

            for pair in pairs:
                target_chan = self.bot.get_channel(pair["target_channel_id"])
                target_name = target_chan.mention if target_chan else f"ID: {pair['target_channel_id']}"
                lang_label = pair.get("lang_label", "Unknown")
                mode_str = " (トリガー限定)" if pair.get("mode") == "trigger" else " (全自動)"
                from_env = " [環境変数]" if pair.get("is_from_env") else ""

                pair_details = [
                    f"• **転送元**: {source_name}",
                    f"• **転送先**: {target_name}",
                    f"• **言語**: {lang_label}"
                ]
                if pair.get("emoji"):
                    pair_details.append(f"• **トリガースタンプ**: {pair['emoji']}")

                pair_users = pair.get("target_users")
                if pair_users:
                    pair_details.append(f"• **対象ユーザー**: {', '.join(pair_users)} 限定")

                embed.add_field(
                    name=f"Pair #{count + 1}{mode_str}{from_env}",
                    value="\n".join(pair_details),
                    inline=False
                )
                count += 1

        if count == 0:
            await ctx.send("ℹ️ 現在設定されている自動翻訳ペアはありません。")
        else:
            await ctx.send(embed=embed)

    @auto_translate.command(name="env_export")
    @commands.has_permissions(manage_channels=True)
    async def env_export(self, ctx: commands.Context):
        """現在の全ペア設定およびトリガー設定を環境変数用のテキスト形式で出力します。"""
        channels_config = self.configs.get("channels", {})
        export_items = []
        for source_id, pairs in channels_config.items():
            for pair in pairs:
                target_id = pair["target_channel_id"]
                lang_code = pair.get("target_lang_code", "en")
                mode = pair.get("mode", "all")
                emoji = pair.get("emoji") or ""
                users_list = pair.get("target_users")
                users_str = ";".join(users_list) if users_list else ""
                export_items.append(f"{source_id}:{target_id}:{lang_code}:{mode}:{emoji}:{users_str}")

        env_pairs_val = ",".join(export_items)
        users_val = ",".join(self.configs.get("trigger_users", ["user1"]))
        emojis_val = ",".join(self.configs.get("trigger_emojis", ["🌐"]))

        out_msg = (
            f"📋 **環境変数設定用テキスト**:\n"
            f"```env\n"
            f"AUTO_TRANSLATE_PAIRS=\"{env_pairs_val}\"\n"
            f"TRIGGER_USERS=\"{users_val}\"\n"
            f"TRIGGER_EMOJIS=\"{emojis_val}\"\n"
            f"```\n"
            f"💡 上記を GCP Secret Manager に登録しておくと、コンテナ再起動後も永久に設定が維持されます。"
        )
        await ctx.send(out_msg)

    @add_pair.error
    @add_trigger_pair.error
    @backfill_messages.error
    @remove_pair.error
    @auto_translate.error
    @env_export.error
    @trigger_info.error
    async def auto_translate_cmd_error(self, ctx: commands.Context, error: commands.CommandError):
        """自動翻訳コマンド群のエラーハンドラ"""
        logger.info("自動翻訳コマンドエラー発生: user=%s, command=%s, error=%s", ctx.author, ctx.command, error)

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 **権限エラー**: このコマンドを実行するには「チャンネルの管理 (Manage Channels)」権限が必要です。")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(
                f"❌ チャンネル `{error.argument}` が見つかりませんでした。\n"
                f"💡 **指定方法のヒント**:\n"
                f"• `#` を入力してメニューから選択する **チャンネルメンション**（例: `#チャンネル名`）を指定してください。\n"
                f"• または、18桁のチャンネルIDを直接入力してください。"
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ 入力されたパラメータの形式が正しくありません。使用例を確認してください。")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ パラメータが足りません: `{error.param.name}`")
        else:
            await ctx.send(f"❌ コマンド実行中にエラーが発生しました: `{error}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoTranslatorCog(bot))
