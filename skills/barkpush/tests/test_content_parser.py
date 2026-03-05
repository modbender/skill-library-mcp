import unittest

from bark_push.content_parser import ContentParser, ContentType


class TestContentParser(unittest.TestCase):
    def setUp(self) -> None:
        self.p = ContentParser()

    def test_image_only(self) -> None:
        parsed = self.p.parse("https://example.com/a.png")
        self.assertEqual(parsed.content_type, ContentType.IMAGE_ONLY)
        self.assertEqual(parsed.images, ["https://example.com/a.png"])

    def test_url_only(self) -> None:
        parsed = self.p.parse("https://example.com/a")
        self.assertEqual(parsed.content_type, ContentType.URL_ONLY)
        self.assertEqual(parsed.urls, ["https://example.com/a"])

    def test_text_only(self) -> None:
        parsed = self.p.parse("hello world")
        self.assertEqual(parsed.content_type, ContentType.TEXT_ONLY)
        self.assertEqual(parsed.text, "hello world")

    def test_mixed(self) -> None:
        parsed = self.p.parse("hello https://example.com/a.png https://example.com/b")
        self.assertEqual(parsed.content_type, ContentType.MIXED)
        self.assertTrue(parsed.markdown)


if __name__ == "__main__":
    unittest.main()
