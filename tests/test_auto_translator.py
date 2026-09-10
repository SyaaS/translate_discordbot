import unittest
from cogs.auto_translator import parse_env_pairs
from utils.flag_map import get_lang_info_by_code


class TestAutoTranslator(unittest.TestCase):

    def test_get_lang_info_by_code(self):
        info_en = get_lang_info_by_code("en")
        self.assertIsNotNone(info_en)
        self.assertEqual(info_en["mymemory"], "en")
        self.assertEqual(info_en["deepl"], "EN-US")

        info_ja = get_lang_info_by_code("japanese")
        self.assertIsNotNone(info_ja)
        self.assertEqual(info_ja["mymemory"], "ja")

    def test_parse_env_pairs(self):
        env_str = "333333333333333333:222222222222222222:en, 12345:67890:ja"
        configs = parse_env_pairs(env_str)

        self.assertIn("333333333333333333", configs)
        self.assertEqual(len(configs["333333333333333333"]), 1)
        self.assertEqual(configs["333333333333333333"][0]["target_channel_id"], 222222222222222222)
        self.assertEqual(configs["333333333333333333"][0]["target_lang_code"], "en")

        self.assertIn("12345", configs)
        self.assertEqual(configs["12345"][0]["target_channel_id"], 67890)
        self.assertEqual(configs["12345"][0]["target_lang_code"], "ja")

    def test_parse_env_pairs_invalid(self):
        env_str = "invalid_format, 123:not_an_int:ja, 123:456:unknown_lang_xyz"
        configs = parse_env_pairs(env_str)
        self.assertEqual(len(configs), 0)


if __name__ == "__main__":
    unittest.main()
