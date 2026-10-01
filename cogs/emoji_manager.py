"""
EmojiManagerCog: カスタム絵文字→言語マッピングの管理コマンド

サーバー管理者向けスラッシュコマンド群。ギルド単位で設定を管理する。
"""

import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.emoji_config import (
    LANGUAGE_PRESETS,
    add_custom_mapping,
    get_guild_config,
    get_merged_map,
    load_config,
    remove_custom_mapping,
    set_disable_default_flags,
    sync_from_firestore,
)

logger = logging.getLogger(__name__)


class EmojiManagerCog(commands.Cog):
    """カスタム絵文字→言語マッピングの管理コグ。"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 起動時に設定ファイルを読み込む
        load_config()

    @commands.Cog.listener()
    async def on_ready(self):
        """ボット起動時に Firestore から最新絵文字設定を同期する"""
        if self.bot.user:
            await asyncio.to_thread(sync_from_firestore, self.bot.user.id)

    # ── グループ定義 ──────────────────────────────────────────────────────
    emoji_group = app_commands.Group(
        name="emoji",
        description="翻訳リアクションの絵文字マッピングを管理します",
    )

    # ── /emoji add ────────────────────────────────────────────────────────
    @emoji_group.command(name="add", description="絵文字→言語マッピングを追加します")
    @app_commands.describe(
        emoji="翻訳トリガーにする絵文字（国旗でもカスタムでもOK）",
        language="翻訳先の言語（プリセットから選択）",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def emoji_add(
        self,
        interaction: discord.Interaction,
        emoji: str,
        language: str,
    ):
        if language not in LANGUAGE_PRESETS:
            await interaction.response.send_message(
                f"❌ 不明な言語: `{language}`\n"
                f"`/emoji add` の language 欄でプリセットから選択してください。",
                ephemeral=True,
            )
            return

        preset = LANGUAGE_PRESETS[language]
        add_custom_mapping(
            guild_id=interaction.guild_id,
            emoji=emoji,
            deepl=preset["deepl"],
            mymemory=preset["mymemory"],
            label=preset["label"],
        )
        await interaction.response.send_message(
            f"✅ マッピングを追加しました: {emoji} → **{preset['label']}**",
            ephemeral=True,
        )

    @emoji_add.autocomplete("language")
    async def _language_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """言語プリセットの autocomplete。"""
        choices = [
            app_commands.Choice(name=name, value=name)
            for name in LANGUAGE_PRESETS
            if current.lower() in name.lower()
        ]
        return choices[:25]  # Discord の上限は 25

    # ── /emoji remove ─────────────────────────────────────────────────────
    @emoji_group.command(name="remove", description="カスタム絵文字マッピングを削除します")
    @app_commands.describe(emoji="削除する絵文字")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def emoji_remove(
        self,
        interaction: discord.Interaction,
        emoji: str,
    ):
        removed = remove_custom_mapping(interaction.guild_id, emoji)
        if removed:
            await interaction.response.send_message(
                f"✅ カスタムマッピングを削除しました: {emoji}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"⚠️ カスタムマッピングが見つかりません: {emoji}\n"
                "（デフォルト国旗マッピングは `/emoji defaults` で無効化できます）",
                ephemeral=True,
            )

    # ── /emoji list ───────────────────────────────────────────────────────
    @emoji_group.command(name="list", description="現在有効な絵文字マッピングを一覧表示します")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def emoji_list(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        guild_cfg = get_guild_config(guild_id)
        merged = get_merged_map(guild_id)
        custom_emojis = set(guild_cfg.get("custom_mappings", {}).keys())
        defaults_disabled = guild_cfg.get("disable_default_flags", False)

        # ヘッダー
        lines: list[str] = []
        lines.append("## 📋 絵文字→言語マッピング一覧\n")
        if defaults_disabled:
            lines.append("⚠️ **デフォルト国旗マッピング: 無効**\n")
        else:
            lines.append("✅ **デフォルト国旗マッピング: 有効**\n")

        # カスタムマッピング
        if custom_emojis:
            lines.append("### 🔧 カスタムマッピング")
            for emoji_key in sorted(custom_emojis):
                info = merged.get(emoji_key)
                if info:
                    lines.append(f"  {emoji_key} → {info['label']}")
            lines.append("")

        # デフォルトマッピング（有効な場合のみ、簡潔に）
        if not defaults_disabled:
            default_count = sum(1 for e in merged if e not in custom_emojis)
            lines.append(f"### 🏳️ デフォルト国旗マッピング ({default_count} 件)")
            # 全部表示すると長すぎるので代表的なもののみ
            sample_flags = ["🇯🇵", "🇺🇸", "🇬🇧", "🇨🇳", "🇹🇼", "🇰🇷", "🇫🇷", "🇩🇪", "🇪🇸"]
            shown = []
            for flag in sample_flags:
                if flag in merged and flag not in custom_emojis:
                    shown.append(f"  {flag} → {merged[flag]['label']}")
            if shown:
                lines.extend(shown)
                remaining = default_count - len(shown)
                if remaining > 0:
                    lines.append(f"  … 他 {remaining} 件")

        content = "\n".join(lines)
        # Discord メッセージ上限チェック
        if len(content) > 2000:
            content = content[:1990] + "\n…（省略）"

        await interaction.response.send_message(content, ephemeral=True)

    # ── /emoji defaults ───────────────────────────────────────────────────
    @emoji_group.command(
        name="defaults",
        description="デフォルト国旗マッピングの有効/無効を切り替えます",
    )
    @app_commands.describe(action="enable: 有効化 / disable: 無効化")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="enable", value="enable"),
            app_commands.Choice(name="disable", value="disable"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def emoji_defaults(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
    ):
        disabled = action.value == "disable"
        set_disable_default_flags(interaction.guild_id, disabled)

        if disabled:
            msg = (
                "🚫 デフォルト国旗マッピングを **無効化** しました。\n"
                "国旗リアクションでは翻訳されなくなります。\n"
                "カスタムマッピングのみが有効です。"
            )
        else:
            msg = (
                "✅ デフォルト国旗マッピングを **有効化** しました。\n"
                "国旗リアクションで翻訳が行われます。"
            )

        await interaction.response.send_message(msg, ephemeral=True)

    # ── エラーハンドラ ────────────────────────────────────────────────────
    @emoji_add.error
    @emoji_remove.error
    @emoji_list.error
    @emoji_defaults.error
    async def _on_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ このコマンドを実行するには「サーバーを管理」権限が必要です。",
                ephemeral=True,
            )
        else:
            logger.error("emoji コマンドエラー: %s", error, exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ エラーが発生しました: {error}",
                    ephemeral=True,
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiManagerCog(bot))
