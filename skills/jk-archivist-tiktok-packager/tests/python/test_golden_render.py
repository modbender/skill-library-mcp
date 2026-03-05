import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SLIDES = [
    "A deterministic golden test slide one.",
    "A deterministic golden test slide two.",
    "A deterministic golden test slide three.",
    "A deterministic golden test slide four.",
    "A deterministic golden test slide five.",
    "A deterministic golden test slide six.",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GoldenRenderTests(unittest.TestCase):
    def test_render_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = tmp_path / "spec.json"
            out_a = tmp_path / "a"
            out_b = tmp_path / "b"
            styles = ["default", "clean", "high-contrast"]
            for style in styles:
                spec.write_text(
                    json.dumps({"slides": SLIDES, "style": {"preset": style}}), encoding="utf-8"
                )

                font = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
                if not font.exists():
                    self.skipTest("System font not available for golden render test.")

                cmd = [
                    "python3",
                    "scripts/render_slides_pillow.py",
                    "--spec",
                    str(spec),
                    "--out",
                    str(out_a),
                    "--font",
                    str(font),
                ]
                subprocess.run(cmd, check=True)
                cmd[5] = str(out_b)
                subprocess.run(cmd, check=True)

                for idx in range(1, 7):
                    file_name = f"slide_{idx:02d}.png"
                    hash_a = sha256(out_a / file_name)
                    hash_b = sha256(out_b / file_name)
                    self.assertEqual(hash_a, hash_b, msg=f"mismatch for {style} {file_name}")


if __name__ == "__main__":
    unittest.main()
