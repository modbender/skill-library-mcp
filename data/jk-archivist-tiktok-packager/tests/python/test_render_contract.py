import json
import tempfile
import unittest
from pathlib import Path

from src.python.render_slides_pillow import load_spec


class RenderContractTests(unittest.TestCase):
    def test_load_spec_accepts_exactly_six_slides(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "spec.json"
            slides = [f"slide {idx}" for idx in range(6)]
            path.write_text(json.dumps({"slides": slides}), encoding="utf-8")

            loaded = load_spec(path)
            self.assertEqual(loaded, slides)


if __name__ == "__main__":
    unittest.main()
