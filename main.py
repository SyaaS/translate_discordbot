"""
Discord 翻訳ボット エントリポイント

国旗絵文字リアクションをトリガーに、メッセージを翻訳してスレッドに投稿する。
"""

import asyncio
import logging
import os

import discord
from aiohttp import web
from discord.ext import commands
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Intents
intents = discord.Intents.default()
intents.message_content = True   # メッセージ本文の読み取り
intents.reactions = True          # リアクションの検知
intents.guild_messages = True     # ギルドのメッセージ

bot = commands.Bot(command_prefix="!", intents=intents)


# ── ヘルスチェック HTTP サーバー（Cloud Run 用） ──────────────────────────
async def _health(_request: web.Request) -> web.Response:
    """Cloud Run / ロードバランサ向けヘルスチェック"""
    return web.Response(text="ok")


async def _start_health_server() -> None:
    """バックグラウンドでヘルスチェック用 HTTP サーバーを起動する。"""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/health", _health)
    app.router.add_get("/", _health)          # Cloud Run デフォルト
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("ヘルスチェックサーバー起動: 0.0.0.0:%d", port)


@bot.event
async def on_ready():
    logger.info("ボット起動完了: %s (ID: %s)", bot.user, bot.user.id)
    logger.info("接続サーバー数: %d", len(bot.guilds))


async def main():
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise ValueError("環境変数 DISCORD_TOKEN が設定されていません。.env ファイルを確認してください。")

    # ヘルスチェック用 HTTP サーバーを起動（Cloud Run / GCP 用）
    await _start_health_server()

    async with bot:
        await bot.load_extension("cogs.translator")
        logger.info("コグ cogs.translator を読み込みました")
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
