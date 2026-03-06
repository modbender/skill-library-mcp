import os
import subprocess
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BIN_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "bin"))
LIB = os.path.join(BIN_DIR, "lib.sh")


def _run_parse(line: str):
    proc = subprocess.run(
        ["bash", "-c", f'source "{LIB}"; codeflow_parse_task_line "$1"', "--", line],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


class ParallelTasksParseTests(unittest.TestCase):
    def test_skips_blank_and_comments(self):
        rc, out = _run_parse("   ")
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")

        rc, out = _run_parse("# comment")
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")

        rc, out = _run_parse("   # comment with leading space")
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")

    def test_rejects_invalid_lines(self):
        rc, out = _run_parse("no delimiter here")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")

        rc, out = _run_parse("dir only |   ")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")

    def test_parses_and_trims(self):
        rc, out = _run_parse("  ~/projects/api   |  Build user auth  ")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "~/projects/api\tBuild user auth")

    def test_preserves_hash_in_prompt(self):
        rc, out = _run_parse("~/p | do # not a comment")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "~/p\tdo # not a comment")

    def test_supports_quoted_fields(self):
        rc, out = _run_parse('"~/my dir" | "do thing"')
        self.assertEqual(rc, 0)
        self.assertEqual(out, "~/my dir\tdo thing")

        rc, out = _run_parse("'~/my dir' | 'do thing'")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "~/my dir\tdo thing")


if __name__ == "__main__":
    unittest.main()
