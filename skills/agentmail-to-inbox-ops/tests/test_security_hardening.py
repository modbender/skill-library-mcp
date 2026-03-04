import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_attachment  # noqa: E402
import download_attachments  # noqa: E402


class DownloadAttachmentHardeningTests(unittest.TestCase):
    def test_sanitize_attachment_filename_strips_path_traversal(self) -> None:
        name = download_attachments.sanitize_attachment_filename("../../etc/passwd", "att_1")
        self.assertEqual(name, "passwd")

    def test_sanitize_attachment_filename_normalizes_windows_paths(self) -> None:
        name = download_attachments.sanitize_attachment_filename(r"C:\temp\bad?.pdf", "att_1")
        self.assertEqual(name, "bad_.pdf")

    def test_sanitize_attachment_filename_falls_back_when_empty(self) -> None:
        name = download_attachments.sanitize_attachment_filename("..", "att_1")
        self.assertEqual(name, "att_1.bin")

    def test_secure_output_path_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            with self.assertRaises(ValueError):
                download_attachments.secure_output_path(out_dir, "../oops.txt")

    def test_dedupe_path_adds_numeric_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "report.txt"
            base.write_text("x", encoding="utf-8")
            candidate = download_attachments.dedupe_path(base)
            self.assertEqual(candidate.name, "report-1.txt")

    def test_validate_download_url_requires_https(self) -> None:
        with self.assertRaises(ValueError):
            download_attachments.validate_download_url("http://example.com/file")


class AnalyzeAttachmentHardeningTests(unittest.TestCase):
    def test_text_file_is_truncated_by_max_chars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("a" * 50, encoding="utf-8")
            result = analyze_attachment.analyze_file(
                path,
                extract_text=False,
                max_bytes=1024,
                max_chars=20,
                max_pages=5,
                max_paragraphs=10,
                parse_timeout_seconds=1.0,
            )
            self.assertEqual(result["mode"], "plain")
            self.assertEqual(result["chars_extracted"], 20)
            self.assertTrue(result["truncated"])
            self.assertIsNone(result["parse_error"])

    def test_pdf_parsing_is_disabled_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pdf"
            path.write_bytes(b"not a real pdf")
            result = analyze_attachment.analyze_file(
                path,
                extract_text=False,
                max_bytes=1024,
                max_chars=100,
                max_pages=5,
                max_paragraphs=10,
                parse_timeout_seconds=1.0,
            )
            self.assertEqual(result["mode"], "pdf")
            self.assertEqual(result["chars_extracted"], 0)
            self.assertIn("--extract-text", result["parse_skipped_reason"])
            self.assertIsNone(result["parse_error"])

    def test_oversized_file_skips_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("x" * 200, encoding="utf-8")
            result = analyze_attachment.analyze_file(
                path,
                extract_text=False,
                max_bytes=50,
                max_chars=100,
                max_pages=5,
                max_paragraphs=10,
                parse_timeout_seconds=1.0,
            )
            self.assertEqual(result["chars_extracted"], 0)
            self.assertIn("exceeds max-bytes", result["parse_skipped_reason"])

    def test_worker_errors_are_returned_structured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pdf"
            path.write_bytes(b"not a real pdf")
            with mock.patch.object(
                analyze_attachment,
                "run_parse_worker",
                return_value={"ok": False, "error": {"type": "Boom", "message": "bad parse"}},
            ):
                result = analyze_attachment.analyze_file(
                    path,
                    extract_text=True,
                    max_bytes=1024,
                    max_chars=100,
                    max_pages=5,
                    max_paragraphs=10,
                    parse_timeout_seconds=1.0,
                )
            self.assertEqual(result["mode"], "pdf")
            self.assertEqual(result["parse_error"]["type"], "Boom")
            self.assertIsNone(result["summary"])

    def test_run_parse_worker_timeout_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pdf"
            path.write_bytes(b"content")
            with mock.patch.object(
                analyze_attachment.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired(cmd=["python"], timeout=0.1),
            ):
                result = analyze_attachment.run_parse_worker(
                    path,
                    max_chars=100,
                    max_pages=5,
                    max_paragraphs=10,
                    timeout_seconds=0.1,
                )
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["type"], "TimeoutExpired")


if __name__ == "__main__":
    unittest.main()
