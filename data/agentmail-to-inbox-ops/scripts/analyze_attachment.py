import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log"}
PARSEABLE_BINARY_EXTENSIONS = {".pdf", ".docx"}

DEFAULT_MAX_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_CHARS = 20000
DEFAULT_MAX_PDF_PAGES = 25
DEFAULT_MAX_DOCX_PARAGRAPHS = 500
DEFAULT_PARSE_TIMEOUT_SECONDS = 8.0


def summarize(text: str, max_chars: int = 1200) -> str:
    clean = " ".join(text.split())
    return clean[:max_chars]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _append_limited_text(parts: list[str], chunk: str, *, max_chars: int) -> bool:
    current = sum(len(p) for p in parts)
    remaining = max_chars - current
    if remaining <= 0:
        return True
    if len(chunk) > remaining:
        parts.append(chunk[:remaining])
        return True
    parts.append(chunk)
    return False


def read_text_file(path: Path, *, max_chars: int) -> tuple[str, bool]:
    text = path.read_text(errors="ignore")
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def read_pdf_text(path: Path, *, max_pages: int, max_chars: int) -> tuple[str, bool]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    truncated = False
    for index, page in enumerate(reader.pages):
        if index >= max_pages:
            truncated = True
            break
        extracted = page.extract_text() or ""
        if _append_limited_text(parts, extracted + "\n", max_chars=max_chars):
            truncated = True
            break
    return "".join(parts), truncated


def read_docx_text(path: Path, *, max_paragraphs: int, max_chars: int) -> tuple[str, bool]:
    from docx import Document

    doc = Document(str(path))
    parts: list[str] = []
    truncated = False
    for index, para in enumerate(doc.paragraphs):
        if index >= max_paragraphs:
            truncated = True
            break
        if _append_limited_text(parts, para.text + "\n", max_chars=max_chars):
            truncated = True
            break
    return "".join(parts), truncated


def read_text_limited(
    path: Path,
    *,
    max_chars: int,
    max_pages: int,
    max_paragraphs: int,
) -> tuple[str, str, bool]:
    ext = path.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        text, truncated = read_text_file(path, max_chars=max_chars)
        return text, "plain", truncated
    if ext == ".pdf":
        text, truncated = read_pdf_text(path, max_pages=max_pages, max_chars=max_chars)
        return text, "pdf", truncated
    if ext == ".docx":
        text, truncated = read_docx_text(
            path, max_paragraphs=max_paragraphs, max_chars=max_chars
        )
        return text, "docx", truncated
    return "", "binary", False


def _apply_worker_limits(timeout_seconds: float) -> None:
    try:
        import resource
    except Exception:
        return

    try:
        cpu_limit = max(1, int(timeout_seconds) + 1)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
    except Exception:
        pass
    try:
        max_file = 64 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (max_file, max_file))
    except Exception:
        pass
    try:
        max_mem = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))
    except Exception:
        pass


def worker_main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--_worker-read-text")
    p.add_argument("--_worker-max-chars", type=int, required=True)
    p.add_argument("--_worker-max-pages", type=int, required=True)
    p.add_argument("--_worker-max-paragraphs", type=int, required=True)
    p.add_argument("--_worker-timeout-seconds", type=float, required=True)
    args = p.parse_args(argv)

    path = Path(args._worker_read_text)
    _apply_worker_limits(args._worker_timeout_seconds)

    try:
        text, mode, truncated = read_text_limited(
            path,
            max_chars=args._worker_max_chars,
            max_pages=args._worker_max_pages,
            max_paragraphs=args._worker_max_paragraphs,
        )
        payload = {
            "ok": True,
            "text": text,
            "mode": mode,
            "truncated": truncated,
        }
    except Exception as exc:
        payload = {
            "ok": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

    sys.stdout.write(json.dumps(payload))
    return 0


def run_parse_worker(
    path: Path,
    *,
    max_chars: int,
    max_pages: int,
    max_paragraphs: int,
    timeout_seconds: float,
) -> dict:
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_worker-read-text",
        str(path),
        "--_worker-max-chars",
        str(max_chars),
        "--_worker-max-pages",
        str(max_pages),
        "--_worker-max-paragraphs",
        str(max_paragraphs),
        "--_worker-timeout-seconds",
        str(timeout_seconds),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": {
                "type": "TimeoutExpired",
                "message": f"Parsing exceeded timeout ({timeout_seconds}s)",
            },
        }

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": {
                "type": "WorkerExit",
                "message": f"Parser worker exited with code {proc.returncode}",
                "stderr": proc.stderr.strip() or None,
            },
        }

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": {
                "type": "WorkerProtocolError",
                "message": f"Invalid worker JSON: {exc}",
                "stderr": proc.stderr.strip() or None,
            },
        }


def analyze_file(
    path: Path,
    *,
    extract_text: bool,
    max_bytes: int,
    max_chars: int,
    max_pages: int,
    max_paragraphs: int,
    parse_timeout_seconds: float,
) -> dict:
    size = path.stat().st_size
    ext = path.suffix.lower()
    payload = {
        "path": str(path.resolve()),
        "size": size,
        "extension": ext or None,
        "sha256": sha256_file(path),
        "mode": "binary",
        "chars_extracted": 0,
        "summary": None,
        "truncated": False,
        "parse_error": None,
        "parse_skipped_reason": None,
    }

    if size > max_bytes:
        payload["parse_skipped_reason"] = f"file size {size} exceeds max-bytes {max_bytes}"
        return payload

    if ext in TEXT_EXTENSIONS:
        text, mode, truncated = read_text_limited(
            path, max_chars=max_chars, max_pages=max_pages, max_paragraphs=max_paragraphs
        )
        payload["mode"] = mode
        payload["chars_extracted"] = len(text)
        payload["summary"] = summarize(text) if text else None
        payload["truncated"] = truncated
        return payload

    if ext in PARSEABLE_BINARY_EXTENSIONS:
        payload["mode"] = ext.lstrip(".")
        if not extract_text:
            payload["parse_skipped_reason"] = (
                f"text extraction for {ext} is disabled by default; rerun with --extract-text"
            )
            return payload

        worker_result = run_parse_worker(
            path,
            max_chars=max_chars,
            max_pages=max_pages,
            max_paragraphs=max_paragraphs,
            timeout_seconds=parse_timeout_seconds,
        )
        if not worker_result.get("ok"):
            payload["parse_error"] = worker_result.get("error")
            return payload

        text = worker_result.get("text") or ""
        payload["mode"] = worker_result.get("mode") or payload["mode"]
        payload["chars_extracted"] = len(text)
        payload["summary"] = summarize(text) if text else None
        payload["truncated"] = bool(worker_result.get("truncated"))
        return payload

    payload["parse_skipped_reason"] = f"unsupported extension: {ext or '(none)'}"
    return payload


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze local attachment")
    p.add_argument("path")
    p.add_argument(
        "--extract-text",
        action="store_true",
        help="Enable text extraction for PDF/DOCX (disabled by default for safety)",
    )
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    p.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    p.add_argument("--max-pdf-pages", type=int, default=DEFAULT_MAX_PDF_PAGES)
    p.add_argument("--max-docx-paragraphs", type=int, default=DEFAULT_MAX_DOCX_PARAGRAPHS)
    p.add_argument("--parse-timeout-seconds", type=float, default=DEFAULT_PARSE_TIMEOUT_SECONDS)
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--_worker-read-text" in argv:
        return worker_main(argv)

    from common import emit, log_action

    p = _build_parser()
    args = p.parse_args(argv)
    path = Path(args.path)

    if args.max_bytes <= 0 or args.max_chars <= 0:
        raise SystemExit("--max-bytes and --max-chars must be > 0")
    if args.max_pdf_pages <= 0 or args.max_docx_paragraphs <= 0:
        raise SystemExit("--max-pdf-pages and --max-docx-paragraphs must be > 0")
    if args.parse_timeout_seconds <= 0:
        raise SystemExit("--parse-timeout-seconds must be > 0")

    log_action(
        "analyze_attachment.start",
        path=str(path),
        extract_text=args.extract_text,
        max_bytes=args.max_bytes,
        max_chars=args.max_chars,
    )

    if not path.exists():
        payload = {
            "path": str(path),
            "error": {"type": "FileNotFound", "message": f"File not found: {path}"},
        }
        emit(payload)
        log_action("analyze_attachment.error", path=str(path), error="file_not_found")
        return 1

    result = analyze_file(
        path,
        extract_text=args.extract_text,
        max_bytes=args.max_bytes,
        max_chars=args.max_chars,
        max_pages=args.max_pdf_pages,
        max_paragraphs=args.max_docx_paragraphs,
        parse_timeout_seconds=args.parse_timeout_seconds,
    )

    log_action(
        "analyze_attachment.done",
        path=str(path),
        mode=result["mode"],
        chars_extracted=result["chars_extracted"],
        parse_error=bool(result["parse_error"]),
        parse_skipped=bool(result["parse_skipped_reason"]),
    )
    emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
