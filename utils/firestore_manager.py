"""
FirestoreManager: Firebase / Google Cloud Firestore を用いた設定永続化マネージャー

Discord Bot の設定（自動翻訳チャンネルペア、トリガーユーザー・スタンプ、カスタム絵文字設定等）を
Firestore に自動保存・自動復元する。

ドキュメントIDは Bot の Discord ID (Snowflake) で管理され、
複数 Bot や複数サーバーの設定が互いに干渉することなく安全に保存される。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Firestore コレクション名
COLLECTION_NAME = "bot_configs"


class FirestoreManager:
    """Firestore への設定保存・読み込みを行うシングルトンクラス"""

    _instance: Optional[FirestoreManager] = None

    def __new__(cls) -> FirestoreManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.client = None
        self.enabled = False
        self.project_id = (
            os.getenv("FIREBASE_PROJECT_ID")
            or os.getenv("GCP_PROJECT_ID")
            or os.getenv("PROJECT_ID")
        )

        if not self.project_id:
            logger.info("FIREBASE_PROJECT_ID が未設定のため、ローカル設定ファイルモードで動作します")
            return

        self._init_client()

    def _init_client(self) -> None:
        """Firestore クライアントの初期化を試行する"""
        try:
            from google.cloud import firestore
            from google.oauth2 import service_account

            creds = None
            cred_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")

            if cred_json_str:
                try:
                    cred_info = json.loads(cred_json_str)
                    creds = service_account.Credentials.from_service_account_info(cred_info)
                    logger.info("FIREBASE_CREDENTIALS_JSON からサービスアカウント認証情報を読み込みました")
                except Exception as e:
                    logger.error("FIREBASE_CREDENTIALS_JSON のパースに失敗しました: %s", e)

            if creds:
                self.client = firestore.Client(project=self.project_id, credentials=creds)
            else:
                # ADC (Application Default Credentials, 例: GCP Cloud Run 上での自動認証)
                self.client = firestore.Client(project=self.project_id)

            self.enabled = True
            logger.info("Firestore クライアントを初期化しました (Project: %s)", self.project_id)
        except ImportError:
            logger.warning(
                "google-cloud-firestore がインストールされていないため、Firestore 永続化は無効です"
            )
            self.enabled = False
        except Exception as e:
            logger.error("Firestore クライアントの初期化に失敗しました: %s", e)
            self.enabled = False

    def is_enabled(self) -> bool:
        """Firestore 永続化が有効かどうかを返す"""
        return self.enabled and self.client is not None

    def _doc_ref(self, bot_id: str | int):
        """指定した Bot ID のドキュメント参照を取得する"""
        if not self.is_enabled():
            return None
        return self.client.collection(COLLECTION_NAME).document(str(bot_id))

    def load_bot_config(self, bot_id: str | int) -> Optional[dict[str, Any]]:
        """Bot ID の全設定ドキュメントを同期取得する"""
        if not self.is_enabled():
            return None

        try:
            doc = self._doc_ref(bot_id).get()
            if doc.exists:
                data = doc.to_dict()
                logger.info("Firestore から Bot (%s) の設定を読み込みました", bot_id)
                return data
            logger.info("Firestore に Bot (%s) の設定ドキュメントはまだ存在しません", bot_id)
            return None
        except Exception as e:
            logger.error("Firestore からの Bot (%s) 設定読み込みに失敗しました: %s", bot_id, e)
            return None

    def save_bot_config(self, bot_id: str | int, data: dict[str, Any], merge: bool = True) -> bool:
        """Bot ID の設定ドキュメントを同期保存する"""
        if not self.is_enabled():
            return False

        try:
            payload = dict(data)
            payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._doc_ref(bot_id).set(payload, merge=merge)
            logger.info("Firestore に Bot (%s) の設定を保存しました", bot_id)
            return True
        except Exception as e:
            logger.error("Firestore への Bot (%s) 設定保存に失敗しました: %s", bot_id, e)
            return False

    def load_auto_translator_data(self, bot_id: str | int) -> Optional[dict[str, Any]]:
        """自動翻訳関連の設定（channels, trigger_users, trigger_emojis）を読み込む"""
        doc_data = self.load_bot_config(bot_id)
        if not doc_data:
            return None

        auto_data = doc_data.get("auto_translator")
        if isinstance(auto_data, dict):
            return auto_data
        return None

    def save_auto_translator_data(
        self,
        bot_id: str | int,
        channels: dict[str, list[dict]],
        trigger_users: list[str],
        trigger_emojis: list[str],
    ) -> bool:
        """自動翻訳関連の設定を保存する"""
        auto_data = {
            "channels": channels,
            "trigger_users": trigger_users,
            "trigger_emojis": trigger_emojis,
        }
        return self.save_bot_config(bot_id, {"auto_translator": auto_data}, merge=True)

    async def async_save_auto_translator_data(
        self,
        bot_id: str | int,
        channels: dict[str, list[dict]],
        trigger_users: list[str],
        trigger_emojis: list[str],
    ) -> bool:
        """非同期（別スレッド）で自動翻訳設定を保存する（Discord イベントループをブロックしない）"""
        if not self.is_enabled():
            return False
        return await asyncio.to_thread(
            self.save_auto_translator_data,
            bot_id,
            channels,
            trigger_users,
            trigger_emojis,
        )

    def load_guild_emoji_config(self, bot_id: str | int) -> Optional[dict[str, Any]]:
        """カスタム絵文字設定（ギルド単位）を読み込む"""
        doc_data = self.load_bot_config(bot_id)
        if not doc_data:
            return None

        emoji_data = doc_data.get("guild_emoji_config")
        if isinstance(emoji_data, dict):
            return emoji_data
        return None

    def save_guild_emoji_config(self, bot_id: str | int, emoji_config: dict[str, Any]) -> bool:
        """カスタム絵文字設定を保存する"""
        return self.save_bot_config(bot_id, {"guild_emoji_config": emoji_config}, merge=True)

    async def async_save_guild_emoji_config(
        self, bot_id: str | int, emoji_config: dict[str, Any]
    ) -> bool:
        """非同期でカスタム絵文字設定を保存する"""
        if not self.is_enabled():
            return False
        return await asyncio.to_thread(self.save_guild_emoji_config, bot_id, emoji_config)


# グローバル共有インスタンス
firestore_manager = FirestoreManager()
