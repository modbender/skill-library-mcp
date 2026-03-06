import os
import sys
import unittest
import io
from contextlib import redirect_stderr


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SCRIPT_DIR)

import py_compat


class PyCompatTests(unittest.TestCase):
    def test_is_python_supported(self):
        self.assertFalse(py_compat.is_python_supported((3, 9, 9)))
        self.assertTrue(py_compat.is_python_supported((3, 10, 0)))
        self.assertTrue(py_compat.is_python_supported((3, 11, 0)))

    def test_require_python310_raises_on_old_python(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                py_compat.require_python310(prog="codeflow", version_info=(3, 9, 0))
        self.assertEqual(ctx.exception.code, 2)

    def test_require_python310_allows_supported(self):
        py_compat.require_python310(prog="codeflow", version_info=(3, 10, 0))


if __name__ == "__main__":
    unittest.main()
