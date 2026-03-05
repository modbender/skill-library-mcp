import unittest
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add scripts directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from obsidian_utils import extract_wikilinks, find_note_path, extract_links_recursive

class TestObsidianUtils(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for zettelkasten
        self.test_dir = tempfile.mkdtemp()
        self.zettel_dir = Path(self.test_dir)

        # Create some dummy notes
        (self.zettel_dir / "Note A.md").write_text("Links to [[Note B]] and [[Note C]]", encoding='utf-8')
        (self.zettel_dir / "Note B.md").write_text("Links to [[Note A]]", encoding='utf-8')
        (self.zettel_dir / "Note C.md").write_text("No links here", encoding='utf-8')
        (self.zettel_dir / "isolated.md").write_text("Just text", encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_extract_wikilinks(self):
        content = "This has a [[Link]] and [[Another Link]] and a [[Link|Alias]]."
        links = extract_wikilinks(content)
        # Regex in obsidian_utils might capture 'Link|Alias' as is or just 'Link'.
        # The current regex is r'\[\[([^\]]+)\]\]', so it captures everything inside [[ ]].
        self.assertIn("Link", links)
        self.assertIn("Another Link", links)
        self.assertIn("Link|Alias", links)
        self.assertEqual(len(links), 3)

    def test_find_note_path_exact(self):
        path = find_note_path("Note A", self.zettel_dir)
        self.assertIsNotNone(path)
        self.assertEqual(path.name, "Note A.md")

    def test_find_note_path_case_insensitive(self):
        path = find_note_path("note a", self.zettel_dir)
        self.assertIsNotNone(path)
        self.assertEqual(path.name, "Note A.md")

    def test_find_note_path_nonexistent(self):
        path = find_note_path("NonExistent", self.zettel_dir)
        self.assertIsNone(path)

    def test_extract_links_recursive(self):
        seed_path = self.zettel_dir / "Note A.md"
        # Depth 1: Should get Note A, Note B, Note C
        results = extract_links_recursive(seed_path, self.zettel_dir, max_depth=1, max_links=10)

        self.assertIn(seed_path, results)

        note_b_path = self.zettel_dir / "Note B.md"
        note_c_path = self.zettel_dir / "Note C.md"

        self.assertIn(note_b_path, results)
        self.assertIn(note_c_path, results)

        # Check levels
        self.assertEqual(results[seed_path]['level'], 0)
        self.assertEqual(results[note_b_path]['level'], 1)
        self.assertEqual(results[note_c_path]['level'], 1)

    def test_extract_links_limit(self):
        seed_path = self.zettel_dir / "Note A.md"
        # Max links 2: Should get Note A and one other
        results = extract_links_recursive(seed_path, self.zettel_dir, max_depth=2, max_links=2)
        self.assertEqual(len(results), 2)

if __name__ == '__main__':
    unittest.main()
