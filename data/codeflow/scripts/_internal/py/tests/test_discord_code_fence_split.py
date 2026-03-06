import os
import sys
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SCRIPT_DIR)

from message_split import split_markdown_code_fence_safe


def _chunk_fences_balanced(text: str) -> bool:
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
    return not in_code


def _strip_fence_lines(text: str) -> str:
    out = []
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            continue
        out.append(line)
    return "".join(out)


class DiscordCodeFenceSplitTests(unittest.TestCase):
    def test_plain_text_split_has_no_loss(self):
        msg = "A\n" + ("b" * 500) + "\nC\n"
        chunks = split_markdown_code_fence_safe(msg, limit=120)
        self.assertGreater(len(chunks), 1)
        self.assertEqual("".join(chunks), msg)
        self.assertTrue(all(len(c) <= 120 for c in chunks))

    def test_code_fence_chunks_are_self_contained(self):
        code = "".join(f"line {i}\n" for i in range(120))
        msg = "Header\n```python\n" + code + "```\nTail\n"
        chunks = split_markdown_code_fence_safe(msg, limit=120)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(c) <= 120 for c in chunks))
        self.assertTrue(all(_chunk_fences_balanced(c) for c in chunks))

        joined = "".join(chunks)
        self.assertEqual(_strip_fence_lines(joined), _strip_fence_lines(msg))


if __name__ == "__main__":
    unittest.main()

