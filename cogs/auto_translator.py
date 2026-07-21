"""
AutoTranslatorCog: チャンネル間自動翻訳転送機能
"""

from __future__ import annotations

import json

import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from utils.flag_map import get_lang_info_by_code
from utils.translator import translate

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join("data", "channel_config.json")


class AutoTranslatorCog(commands.Cog):
    """指定したチャンネルの投稿を自動で翻訳して別チャンネルへ転送するコグ。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.configs: dict[str, list[dict]] = self._load_configs()

    def _load_configs(self) -> dict[str, list[dict]]:
        """設定ファイルからチャンネル自動翻訳設定を読み込む。"""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("設定ファイルの読み込みに失敗しました: %s", e)
            return {}

    def _save_configs(self) -> None:
        """現在のチャンネル自動翻訳設定をファイルに保存する。"""
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.configs, f, indent=2, ensure_ascii=False)
            logger.info("自動翻訳設定を保存しました")
        except Exception as e:
            logger.error("設定ファイルの保存に失敗しました: %s", e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """メッセージ投稿時に自動翻訳・転送を行うリスナー。"""

        # ボット自身の発言や他のボットの発言は無視
        if message.author.bot:
            return

        # コマンド判定（プレフィックスで始まるメッセージは無視）
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        source_channel_id = str(message.channel.id)
        if source_channel_id not in self.configs:
            return

        content = message.content.strip()
        if not content:
            return

        pairs = self.configs[source_channel_id]
        for pair in pairs:
            target_channel_id = pair["target_channel_id"]
            deepl_lang = pair.get("deepl_lang")
            mymemory_lang = pair.get("mymemory_lang")
            lang_label = pair.get("lang_label", "Unknown")

            # ターゲットチャンネルの取得
            target_channel = self.bot.get_channel(target_channel_id)
            if target_channel is None:
                try:
                    target_channel = await self.bot.fetch_channel(target_channel_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                    logger.error("ターゲットチャンネル (%s) の取得失敗: %s", target_channel_id, e)
                    continue

            # 翻訳実行
            translated_text, engine = translate(content, deepl_lang, mymemory_lang)

            # 同一言語の場合はスキップ
            if engine == "same_language" or not translated_text:
                logger.debug(
                    "自動翻訳スキップ (engine=%s): source=%s target=%s",
                    engine, source_channel_id, target_channel_id
                )
                continue

            # Embed メッセージ作成
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
                logger.info(
                    "自動翻訳転送完了: message_id=%s -> target_channel=%s (%s)",
                    message.id, target_channel_id, lang_label
                )
            except (discord.Forbidden, discord.HTTPException) as e:
                logger.error("自動翻訳メッセージ送信失敗 (target=%s): %s", target_channel_id, e)

    @commands.group(name="auto_translate", aliases=["at"], invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def auto_translate(self, ctx: commands.Context):
        """チャンネル自動翻訳コマンドのルートグループ。"""
        await ctx.send_help(ctx.command)

    @auto_translate.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def add_pair(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: discord.TextChannel,
        lang_code: str
    ):
        """
        自動翻訳ペアを追加・更新します。
        使用例: !auto_translate add #japanese-chat #english-chat en
        """
        lang_info = get_lang_info_by_code(lang_code)
        if not lang_info:
            await ctx.send(
                f"❌ 指定された言語コード `{lang_code}` が見つかりません。\n"
                f"例: `en` (英語), `ja` (日本語), `zh` (中国語), `ko` (韓国語), `fr` (フランス語), `es` (スペイン語) など指定してください。"
            )
            return

        source_id = str(source_channel.id)
        new_pair = {
            "target_channel_id": target_channel.id,
            "target_lang_code": lang_code.lower(),
            "deepl_lang": lang_info.get("deepl"),
            "mymemory_lang": lang_info.get("mymemory"),
            "lang_label": lang_info.get("label"),
        }

        if source_id not in self.configs:
            self.configs[source_id] = []

        # 重複チェック（同一ターゲットチャンネルへの設定があれば更新）
        updated = False
        for i, pair in enumerate(self.configs[source_id]):
            if pair["target_channel_id"] == target_channel.id:
                self.configs[source_id][i] = new_pair
                updated = True
                break

        if not updated:
            self.configs[source_id].append(new_pair)

        self._save_configs()

        await ctx.send(
            f"✅ 自動翻訳ペアを設定しました！\n"
            f"• 転送元: {source_channel.mention}\n"
            f"• 転送先: {target_channel.mention}\n"
            f"• 翻訳先言語: **{lang_info['label']}** (`{lang_code}`)"
        )

    @auto_translate.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def remove_pair(
        self,
        ctx: commands.Context,
        source_channel: discord.TextChannel,
        target_channel: Optional[discord.TextChannel] = None
    ):
        """
        自動翻訳ペアを削除します。
        使用例: !auto_translate remove #japanese-chat [#english-chat]
        """
        source_id = str(source_channel.id)
        if source_id not in self.configs or not self.configs[source_id]:
            await ctx.send(f"⚠️ {source_channel.mention} には自動翻訳設定がありません。")
            return

        if target_channel is None:
            # ソースチャンネルの設定を全て削除
            del self.configs[source_id]
            self._save_configs()
            await ctx.send(f"✅ {source_channel.mention} からの自動翻訳設定をすべて削除しました。")
        else:
            # 特定のターゲットチャンネルのみ削除
            original_len = len(self.configs[source_id])
            self.configs[source_id] = [
                p for p in self.configs[source_id] if p["target_channel_id"] != target_channel.id
            ]
            if len(self.configs[source_id]) == 0:
                del self.configs[source_id]

            if len(self.configs.get(source_id, [])) < original_len:
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
        if not self.configs:
            await ctx.send("ℹ️ 現在設定されている自動翻訳ペアはありません。")
            return

        embed = discord.Embed(
            title="🌐 チャンネル自動翻訳 一覧",
            color=discord.Color.green()
        )

        count = 0
        for source_id, pairs in self.configs.items():
            source_chan = self.bot.get_channel(int(source_id))
            source_name = source_chan.mention if source_chan else f"ID: {source_id}"

            for pair in pairs:
                target_chan = self.bot.get_channel(pair["target_channel_id"])
                target_name = target_chan.mention if target_chan else f"ID: {pair['target_channel_id']}"
                lang_label = pair.get("lang_label", "Unknown")

                embed.add_field(
                    name=f"Pair #{count + 1}",
                    value=f"• **転送元**: {source_name}\n• **転送先**: {target_name}\n• **言語**: {lang_label}",
                    inline=False
                )
                count += 1

        if count == 0:
            await ctx.send("ℹ️ 現在設定されている自動翻訳ペアはありません。")
        else:
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoTranslatorCog(bot))
