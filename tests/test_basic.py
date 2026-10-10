"""Test super ringan, stdlib only. Jalanin: python -m unittest discover -s tests -v"""

import unittest

from grabin import platforms, utils
from grabin.downloader import quality_to_format


class TestPlatforms(unittest.TestCase):
    def test_facebook_detected(self):
        self.assertEqual(platforms.platform_key("https://www.facebook.com/reel/123"), "facebook")

    def test_tiktok_detected(self):
        self.assertEqual(platforms.platform_key("https://vt.tiktok.com/abc/"), "tiktok")

    def test_unknown_falls_back_to_generic(self):
        self.assertEqual(platforms.platform_key("https://situs-random.example/v/1"), "generic")


class TestUtils(unittest.TestCase):
    def test_sanitize_removes_illegal_chars(self):
        self.assertNotIn("/", utils.sanitize_filename("a/b:c"))

    def test_quality_mapping(self):
        self.assertIn("bestaudio", quality_to_format("audio"))
        self.assertIn("720", quality_to_format("720"))


if __name__ == "__main__":
    unittest.main()
