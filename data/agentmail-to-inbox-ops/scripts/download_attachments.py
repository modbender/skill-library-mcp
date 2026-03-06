import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import httpx

DEFAULT_MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024
DEFAULT_DOWNLOAD_TIMEOUT_SECONDS = 60.0
_FILENAME_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._ -]+")


def sanitize_attachment_filename(filename: str | None, attachment_id: str) -> str:
    raw = (filename or "").strip().replace("\\", "/")
    basename = Path(raw).name.strip().strip(". ")
    if not basename or basename in {".", ".."}:
        return f"{attachment_id}.bin"

    safe = _FILENAME_SAFE_CHARS.sub("_", basename)
    safe = re.sub(r"\s+", " ", safe).strip().strip(". ")
    if not safe or safe in {".", ".."}:
        return f"{attachment_id}.bin"

    suffix = Path(safe).suffix
    stem = Path(safe).stem or attachment_id
    max_len = 120
    if len(safe) > max_len:
        reserve = len(suffix)
        if reserve >= max_len - 1:
            suffix = ""
            reserve = 0
        stem = stem[: max_len - reserve].rstrip(" ._") or attachment_id
        safe = f"{stem}{suffix}"

    return safe


def secure_output_path(out_dir: Path, stored_name: str) -> Path:
    out_dir_resolved = out_dir.resolve()
    candidate = (out_dir_resolved / stored_name).resolve()
    if not candidate.is_relative_to(out_dir_resolved):
        raise ValueError(f"Refusing to write outside output directory: {stored_name}")
    return candidate


def dedupe_path(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    for i in range(1, 10_000):
        candidate = target.with_name(f"{stem}-{i}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Unable to choose unique filename for {target.name}")


def validate_download_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError("Attachment download URL must use HTTPS")
    if not parsed.netloc:
        raise ValueError("Attachment download URL is missing a host")


def _parse_content_length(response: httpx.Response) -> int | None:
    raw = response.headers.get("content-length")
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


def stream_download_to_file(
    url: str,
    target: Path,
    *,
    max_bytes: int,
    timeout_seconds: float,
) -> int:
    validate_download_url(url)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = None
    bytes_written = 0

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, dir=target.parent, prefix=f".{target.name}.", suffix=".part"
        ) as tmp_file:
            tmp_name = tmp_file.name
            try:
                os.chmod(tmp_name, 0o600)
            except OSError:
                pass

            with httpx.stream("GET", url, timeout=timeout_seconds, follow_redirects=True) as response:
                response.raise_for_status()
                if response.url.scheme.lower() != "https":
                    raise ValueError("Attachment download redirected to a non-HTTPS URL")

                content_length = _parse_content_length(response)
                if content_length is not None and content_length > max_bytes:
                    raise ValueError(
                        f"Attachment size {content_length} exceeds configured limit {max_bytes}"
                    )

                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    bytes_written += len(chunk)
                    if bytes_written > max_bytes:
                        raise ValueError(
                            f"Attachment size exceeds configured limit {max_bytes}"
                        )
                    tmp_file.write(chunk)

                tmp_file.flush()

                if content_length is not None and bytes_written != content_length:
                    raise ValueError(
                        f"Downloaded byte count mismatch (expected {content_length}, got {bytes_written})"
                    )

        Path(tmp_name).replace(target)
        return bytes_written
    except Exception:
        if tmp_name:
            try:
                Path(tmp_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise


def main() -> None:
    from common import build_parser, emit, get_client_and_inbox, log_action

    p = build_parser("Download message attachments")
    p.add_argument("message_id")
    p.add_argument("--out-dir", default="./downloads")
    p.add_argument("--attachment-id", default=None)
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_ATTACHMENT_BYTES)
    p.add_argument("--timeout-seconds", type=float, default=DEFAULT_DOWNLOAD_TIMEOUT_SECONDS)
    args = p.parse_args()
    if args.max_bytes <= 0:
        raise SystemExit("--max-bytes must be > 0")
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be > 0")

    client, inbox = get_client_and_inbox(args)
    log_action(
        "download_attachments.start",
        inbox=inbox,
        message_id=args.message_id,
        out_dir=args.out_dir,
        attachment_id=args.attachment_id,
        max_bytes=args.max_bytes,
    )
    msg = client.inboxes.messages.get(inbox_id=inbox, message_id=args.message_id)
    attachments = msg.attachments or []

    if args.attachment_id:
        attachments = [a for a in attachments if a.attachment_id == args.attachment_id]

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    downloaded = []
    failed = []
    for a in attachments:
        original_filename = a.filename or f"{a.attachment_id}.bin"
        try:
            meta = client.inboxes.messages.get_attachment(
                inbox_id=inbox, message_id=args.message_id, attachment_id=a.attachment_id
            )
            stored_name = sanitize_attachment_filename(original_filename, a.attachment_id)
            target = dedupe_path(secure_output_path(out_dir, stored_name))
            byte_count = stream_download_to_file(
                meta.download_url,
                target,
                max_bytes=args.max_bytes,
                timeout_seconds=args.timeout_seconds,
            )

            downloaded.append(
                {
                    "attachment_id": a.attachment_id,
                    "filename": original_filename,
                    "stored_filename": target.name,
                    "path": str(target.resolve()),
                    "bytes": byte_count,
                    "content_type": a.content_type,
                }
            )
        except Exception as exc:
            failed.append(
                {
                    "attachment_id": a.attachment_id,
                    "filename": original_filename,
                    "error": str(exc),
                }
            )
            log_action(
                "download_attachments.error",
                inbox=inbox,
                message_id=args.message_id,
                attachment_id=a.attachment_id,
                error=str(exc),
            )

    log_action(
        "download_attachments.done",
        inbox=inbox,
        message_id=args.message_id,
        downloaded_count=len(downloaded),
        failed_count=len(failed),
    )
    emit({"inbox": inbox, "message_id": args.message_id, "downloaded": downloaded, "failed": failed})


if __name__ == "__main__":
    main()
