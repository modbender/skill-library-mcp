"""Shared fixtures for detect-file-type tests."""

from __future__ import annotations

import struct
import zipfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def create_fixtures():
    """Generate small, license-clean test fixture files."""
    FIXTURES_DIR.mkdir(exist_ok=True)

    # tiny.txt — short UTF-8 text
    (FIXTURES_DIR / "tiny.txt").write_text(
        "The quick brown fox jumps over the lazy dog.\n" * 5, encoding="utf-8"
    )

    # sample.png — minimal valid 1x1 white PNG
    png = _minimal_png()
    (FIXTURES_DIR / "sample.png").write_bytes(png)

    # sample.zip — zip containing tiny.txt
    # Keep stable local git state: only create if missing.
    zip_path = FIXTURES_DIR / "sample.zip"
    if not zip_path.exists():
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("tiny.txt", "The quick brown fox jumps over the lazy dog.\n")

    # empty.bin — 0-byte file
    (FIXTURES_DIR / "empty.bin").write_bytes(b"")

    # misleading.txt.png — text content with .png extension
    (FIXTURES_DIR / "misleading.txt.png").write_text(
        "This is actually a plain text file, not a PNG image.\n" * 5, encoding="utf-8"
    )


def _minimal_png() -> bytes:
    """Generate a minimal valid 1x1 white PNG file."""
    import zlib

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    signature = b"\x89PNG\r\n\x1a\n"
    # IHDR: 1x1, 8-bit RGB
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    # IDAT: single row, filter byte 0, white pixel (255, 255, 255)
    raw_data = b"\x00\xff\xff\xff"
    compressed = zlib.compress(raw_data)
    idat = _chunk(b"IDAT", compressed)
    # IEND
    iend = _chunk(b"IEND", b"")
    return signature + ihdr + idat + iend
