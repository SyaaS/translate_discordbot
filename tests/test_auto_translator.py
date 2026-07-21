import json
import os
import unittest
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

        info_unknown = get_lang_info_by_code("xyz_unknown_lang")
        self.assertIsNone(info_unknown)


if __name__ == "__main__":
    unittest.main()
