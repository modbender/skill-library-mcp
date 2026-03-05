#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import struct
import sys
import uuid
from pathlib import Path
from urllib import error, request

API_URL = "https://api.remove.bg/v1.0/removebg"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_BYTES = 25 * 1024 * 1024
MAX_DIMENSION = 12000


def _workspace_root() -> Path:
    env_root = os.getenv("OPENCLAW_WORKSPACE")
    return Path(env_root).resolve() if env_root else Path.cwd().resolve()


def _ensure_within(path: Path, root: Path, label: str) -> None:
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError(f"{label} must be inside workspace: {root}")


def _detect_image_format(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def _jpeg_dimensions(data: bytes) -> tuple[int, int]:
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2

        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue

        if i + 2 > len(data):
            break
        seg_len = struct.unpack(">H", data[i : i + 2])[0]
        if seg_len < 2 or i + seg_len > len(data):
            break

        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if i + 7 > len(data):
                break
            height = struct.unpack(">H", data[i + 3 : i + 5])[0]
            width = struct.unpack(">H", data[i + 5 : i + 7])[0]
            return width, height

        i += seg_len

    raise ValueError("Could not parse JPEG dimensions")


def _image_dimensions(fmt: str, data: bytes) -> tuple[int, int]:
    if fmt == "png":
        if len(data) < 24:
            raise ValueError("Invalid PNG")
        width = struct.unpack(">I", data[16:20])[0]
        height = struct.unpack(">I", data[20:24])[0]
        return width, height

    if fmt == "jpeg":
        return _jpeg_dimensions(data)

    if fmt == "webp":
        if len(data) < 30:
            raise ValueError("Invalid WEBP")
        chunk = data[12:16]
        if chunk == b"VP8X":
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if chunk == b"VP8 ":
            start = data.find(b"\x9d\x01\x2a", 20)
            if start == -1 or start + 7 > len(data):
                raise ValueError("Invalid WEBP VP8")
            width = struct.unpack("<H", data[start + 3 : start + 5])[0] & 0x3FFF
            height = struct.unpack("<H", data[start + 5 : start + 7])[0] & 0x3FFF
            return width, height
        if chunk == b"VP8L":
            if len(data) < 25 or data[20] != 0x2F:
                raise ValueError("Invalid WEBP VP8L")
            b0, b1, b2, b3 = data[21], data[22], data[23], data[24]
            width = 1 + (((b1 & 0x3F) << 8) | b0)
            height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
            return width, height
        raise ValueError("Unsupported WEBP chunk")

    raise ValueError(f"Unsupported format: {fmt}")


def _validate_input_image(path: Path) -> bytes:
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Input extension not allowed. Allowed: {allowed}")

    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError("Input too large (>25MB)")

    data = path.read_bytes()
    fmt = _detect_image_format(data)
    if fmt is None:
        raise ValueError("Input is not a supported image (png/jpg/jpeg/webp)")

    # Ensure extension and content don't conflict.
    ext = path.suffix.lower()
    if ext in {".jpg", ".jpeg"} and fmt != "jpeg":
        raise ValueError("File extension/content mismatch")
    if ext == ".png" and fmt != "png":
        raise ValueError("File extension/content mismatch")
    if ext == ".webp" and fmt != "webp":
        raise ValueError("File extension/content mismatch")

    width, height = _image_dimensions(fmt, data)
    if width <= 0 or height <= 0:
        raise ValueError("Invalid image dimensions")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(f"Image dimensions too large (>{MAX_DIMENSION}px)")

    return data


def build_multipart(fields: dict[str, str], file_field: str, file_path: Path, file_data: bytes):
    boundary = f"----OpenClaw{uuid.uuid4().hex}"
    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.extend(str(v).encode())
        body.extend(b"\r\n")

    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return boundary, bytes(body)


def main() -> int:
    p = argparse.ArgumentParser(description="Remove background via remove.bg API")
    p.add_argument("--input", "-i", required=True)
    p.add_argument("--output", "-o", required=True)
    p.add_argument("--size", default="auto", choices=["auto", "preview", "full", "4k"])
    p.add_argument("--format", default="png", choices=["png", "jpg", "zip"])
    args = p.parse_args()

    key = os.getenv("REMOVE_BG_API_KEY")
    if not key:
        print("Missing REMOVE_BG_API_KEY", file=sys.stderr)
        return 2

    workspace = _workspace_root()
    safe_output_root = workspace / "outputs" / "removebg-api"

    try:
        in_path = Path(args.input).expanduser().resolve(strict=True)
    except FileNotFoundError:
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2

    if not in_path.is_file():
        print(f"Input is not a file: {in_path}", file=sys.stderr)
        return 2

    out_path = Path(args.output).expanduser()
    if not out_path.is_absolute():
        out_path = workspace / out_path
    out_path = out_path.resolve()

    try:
        _ensure_within(in_path, workspace, "input path")
        _ensure_within(out_path, safe_output_root, "output path")
        image_bytes = _validate_input_image(in_path)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        print(f"Input must be an allowed image inside {workspace}.", file=sys.stderr)
        print(f"Output must be under {safe_output_root}.", file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fields = {"size": args.size, "format": args.format}
    boundary, payload = build_multipart(fields, "image_file", in_path, image_bytes)

    req = request.Request(API_URL, method="POST", data=payload)
    req.add_header("X-Api-Key", key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with request.urlopen(req, timeout=90) as resp:
            content = resp.read()
            out_path.write_bytes(content)
            print(f"Saved: {out_path}")
            try:
                rel = out_path.relative_to(Path.cwd())
                print(f"MEDIA: ./{rel}")
            except ValueError:
                print(f"MEDIA: {out_path}")
            return 0
    except error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        try:
            parsed = json.loads(body)
            print(json.dumps(parsed, indent=2), file=sys.stderr)
        except Exception:
            print(body, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
