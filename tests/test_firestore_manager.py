import os
import unittest
from unittest.mock import MagicMock, patch

from utils.firestore_manager import FirestoreManager


class TestFirestoreManager(unittest.TestCase):

    def setUp(self):
        # シングルトンの状態をテスト用にリセット
        FirestoreManager._instance = None

    def tearDown(self):
        FirestoreManager._instance = None

    def test_disabled_when_no_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            manager = FirestoreManager()
            self.assertFalse(manager.is_enabled())
            self.assertIsNone(manager.load_bot_config("123456789"))
            self.assertFalse(manager.save_bot_config("123456789", {"test": 1}))

    def test_mocked_firestore_save_and_load(self):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "auto_translator": {
                "channels": {"111": [{"target_channel_id": 222, "mode": "1", "lang": "ja"}]},
                "trigger_users": ["user1"],
                "trigger_emojis": ["🌐"],
            },
            "guild_emoji_config": {"guilds": {"999": {"disable_default_flags": False}}},
        }

        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc

        mock_client = MagicMock()
        mock_client.collection.return_value.document.return_value = mock_doc_ref

        mock_cloud = MagicMock()
        mock_cloud.firestore.Client.return_value = mock_client

        with patch.dict(os.environ, {"FIREBASE_PROJECT_ID": "test-project"}):
            with patch.dict("sys.modules", {
                "google": MagicMock(),
                "google.cloud": mock_cloud,
                "google.cloud.firestore": mock_cloud.firestore,
                "google.oauth2": MagicMock(),
                "google.oauth2.service_account": MagicMock(),
            }):
                manager = FirestoreManager()
                self.assertTrue(manager.is_enabled())

                # load_bot_config
                config = manager.load_bot_config("12345")
                self.assertIsNotNone(config)
                self.assertIn("auto_translator", config)

                # load_auto_translator_data
                auto_data = manager.load_auto_translator_data("12345")
                self.assertIsNotNone(auto_data)
                self.assertIn("111", auto_data["channels"])
                self.assertEqual(auto_data["trigger_users"], ["user1"])

                # load_guild_emoji_config
                emoji_data = manager.load_guild_emoji_config("12345")
                self.assertIsNotNone(emoji_data)
                self.assertIn("999", emoji_data["guilds"])

                # save_auto_translator_data
                saved = manager.save_auto_translator_data(
                    "12345",
                    {"111": [{"target_channel_id": 222}]},
                    ["user2"],
                    ["🇯🇵"],
                )
                self.assertTrue(saved)
                mock_doc_ref.set.assert_called()

    def test_load_nonexistent_doc(self):
        mock_doc = MagicMock()
        mock_doc.exists = False

        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc

        mock_client = MagicMock()
        mock_client.collection.return_value.document.return_value = mock_doc_ref

        mock_cloud = MagicMock()
        mock_cloud.firestore.Client.return_value = mock_client

        with patch.dict(os.environ, {"FIREBASE_PROJECT_ID": "test-project"}):
            with patch.dict("sys.modules", {
                "google": MagicMock(),
                "google.cloud": mock_cloud,
                "google.cloud.firestore": mock_cloud.firestore,
                "google.oauth2": MagicMock(),
                "google.oauth2.service_account": MagicMock(),
            }):
                manager = FirestoreManager()
                config = manager.load_bot_config("99999")
                self.assertIsNone(config)


if __name__ == "__main__":
    unittest.main()
