import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from preprocess import extract_tags, find_tag_similar_docs

class TestPreprocess(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for zettelkasten
        self.test_dir = tempfile.mkdtemp()
        self.zettel_dir = Path(self.test_dir)

        # Create notes with tags
        (self.zettel_dir / "Note1.md").write_text("---\ntags: [apple, banana]\n---\nContent", encoding='utf-8')
        (self.zettel_dir / "Note2.md").write_text("Text with #apple tag", encoding='utf-8')
        (self.zettel_dir / "Note3.md").write_text("---\ntags: [cherry]\n---\nNo overlap", encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extract_tags_inline(self):
        content = "This has #tag1 and #tag-2 embedded."
        tags = extract_tags(content)
        self.assertIn("tag1", tags)
        self.assertIn("tag-2", tags)

    def test_extract_tags_frontmatter_list(self):
        content = "---\ntags: [foo, bar]\n---\nContent"
        tags = extract_tags(content)
        self.assertIn("foo", tags)
        self.assertIn("bar", tags)

    def test_extract_tags_frontmatter_comma(self):
        content = "---\ntags: foo, bar\n---\nContent"
        tags = extract_tags(content)
        self.assertIn("foo", tags)
        self.assertIn("bar", tags)

    def test_find_tag_similar_docs(self):
        seed_path = self.zettel_dir / "seed.md"
        seed_path.write_text("Query tag #apple", encoding='utf-8')

        seed_tags = {"apple"}
        similar = find_tag_similar_docs(seed_tags, self.zettel_dir, seed_path)

        # Note1 and Note2 have 'apple', Note3 does not
        # Note1: tags [apple, banana] -> overlap 1
        # Note2: #apple -> overlap 1

        paths = [s['path'] for s in similar]
        self.assertTrue(any("Note1.md" in p for p in paths))
        self.assertTrue(any("Note2.md" in p for p in paths))
        self.assertFalse(any("Note3.md" in p for p in paths))

if __name__ == '__main__':
    unittest.main()
