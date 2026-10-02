"""
test_text_filter.py: utils/text_filter.py の単体テスト
"""

import unittest

from utils.text_filter import clean_text_for_classification, is_translatable_text


class TestTextFilter(unittest.TestCase):
    def test_empty_or_whitespace(self):
        self.assertEqual(is_translatable_text(""), (False, "empty"))
        self.assertEqual(is_translatable_text("   \n\t  "), (False, "empty"))

    def test_urls_only(self):
        # Tenor GIF URL
        self.assertFalse(is_translatable_text("https://tenor.com/view/cute-cat-dancing-1234567")[0])
        # Giphy URL
        self.assertFalse(is_translatable_text("https://giphy.com/gifs/funny-cat-abc123xyz")[0])
        # Discord CDN media URL
        self.assertFalse(is_translatable_text("https://cdn.discordapp.com/attachments/123/456/image.png")[0])
        # Multiple URLs
        self.assertFalse(is_translatable_text("https://example.com https://google.com")[0])

    def test_discord_emojis_only(self):
        # Custom emojis
        self.assertFalse(is_translatable_text("<:pepe:123456789>")[0])
        self.assertFalse(is_translatable_text("<a:animated_cat:987654321>")[0])
        self.assertFalse(is_translatable_text("<:emoji1:111> <:emoji2:222>")[0])

    def test_unicode_emojis_and_symbols_only(self):
        self.assertFalse(is_translatable_text("😀 🎉 👍")[0])
        self.assertFalse(is_translatable_text("✨🔥💫")[0])
        self.assertFalse(is_translatable_text("!?!?!?")[0])
        self.assertFalse(is_translatable_text("---")[0])
        self.assertFalse(is_translatable_text("12345")[0])

    def test_mentions_and_timestamps_only(self):
        self.assertFalse(is_translatable_text("<@123456789>")[0])
        self.assertFalse(is_translatable_text("<@&987654321> <#11223344>")[0])
        self.assertFalse(is_translatable_text("@everyone @here")[0])
        self.assertFalse(is_translatable_text("<t:1696000000:R>")[0])

    def test_slang_and_laughter_only(self):
        # Japanese laughter
        self.assertFalse(is_translatable_text("w")[0])
        self.assertFalse(is_translatable_text("ww")[0])
        self.assertFalse(is_translatable_text("wwwwww")[0])
        self.assertFalse(is_translatable_text("ｗｗｗ")[0])
        self.assertFalse(is_translatable_text("草")[0])
        self.assertFalse(is_translatable_text("草草草")[0])
        self.assertFalse(is_translatable_text("大草")[0])
        self.assertFalse(is_translatable_text("笑")[0])
        # Clapping 8888
        self.assertFalse(is_translatable_text("8888")[0])
        self.assertFalse(is_translatable_text("８８８８")[0])
        # English / Global slang
        self.assertFalse(is_translatable_text("lol")[0])
        self.assertFalse(is_translatable_text("lmao")[0])
        self.assertFalse(is_translatable_text("rofl")[0])
        self.assertFalse(is_translatable_text("hahaha")[0])
        self.assertFalse(is_translatable_text("hehe")[0])
        self.assertFalse(is_translatable_text("ok")[0])
        self.assertFalse(is_translatable_text("gg")[0])

    def test_code_blocks_only(self):
        self.assertFalse(is_translatable_text("```python\nprint('hello')\n```")[0])
        self.assertFalse(is_translatable_text("`const x = 1;`")[0])

    def test_valid_japanese_text(self):
        self.assertTrue(is_translatable_text("こんにちは")[0])
        self.assertTrue(is_translatable_text("明日の会議は何時からですか？")[0])
        self.assertTrue(is_translatable_text("了解です！")[0])
        self.assertTrue(is_translatable_text("よろしくお願いします")[0])

    def test_valid_english_text(self):
        self.assertTrue(is_translatable_text("Hello everyone")[0])
        self.assertTrue(is_translatable_text("What time is the meeting tomorrow?")[0])
        self.assertTrue(is_translatable_text("See you soon")[0])
        self.assertTrue(is_translatable_text("Awesome!")[0])
        self.assertTrue(is_translatable_text("Tomorrow")[0])

    def test_text_with_urls_and_emojis(self):
        # Valid text accompanying a GIF or URL
        self.assertTrue(is_translatable_text("この猫めっちゃ可愛い https://tenor.com/view/cat-123")[0])
        self.assertTrue(is_translatable_text("Check this out! https://giphy.com/gifs/abc")[0])
        # Valid text with custom and unicode emojis
        self.assertTrue(is_translatable_text("お疲れ様でした！ <:pepe:123> 🎉")[0])
        self.assertTrue(is_translatable_text("<@123456> 今日の進捗はどうですか？")[0])


if __name__ == "__main__":
    unittest.main()
