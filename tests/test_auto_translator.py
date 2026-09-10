import unittest
from cogs.auto_translator import extract_source_message_id, parse_env_pairs
from utils.flag_map import get_lang_info_by_code


class DummyEmbedField:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class DummyEmbed:
    def __init__(self, description="", fields=None):
        self.description = description
        self.fields = fields or []


class TestAutoTranslator(unittest.TestCase):

    def test_get_lang_info_by_code(self):
        info_en = get_lang_info_by_code("en")
        self.assertIsNotNone(info_en)
        self.assertEqual(info_en["mymemory"], "en")
        self.assertEqual(info_en["deepl"], "EN-US")

        info_ja = get_lang_info_by_code("japanese")
        self.assertIsNotNone(info_ja)
        self.assertEqual(info_ja["mymemory"], "ja")

    def test_parse_env_pairs_with_mode(self):
        env_str = "333333333333333333:222222222222222222:en:trigger, 12345:67890:ja:all"
        configs = parse_env_pairs(env_str)

        self.assertIn("333333333333333333", configs)
        self.assertEqual(len(configs["333333333333333333"]), 1)
        self.assertEqual(configs["333333333333333333"][0]["target_channel_id"], 222222222222222222)
        self.assertEqual(configs["333333333333333333"][0]["target_lang_code"], "en")
        self.assertEqual(configs["333333333333333333"][0]["mode"], "trigger")

        self.assertIn("12345", configs)
        self.assertEqual(configs["12345"][0]["mode"], "all")

    def test_extract_source_message_id(self):
        embed = DummyEmbed(
            fields=[
                DummyEmbedField(
                    name="Original Message",
                    value="[Jump to Message](https://discord.com/channels/12345/67890/987654321098765432)"
                )
            ]
        )
        msg_id = extract_source_message_id(embed)
        self.assertEqual(msg_id, 987654321098765432)


if __name__ == "__main__":
    unittest.main()
