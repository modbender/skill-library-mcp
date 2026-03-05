"""
Image Provider API client (Internal).

This client handles image generation API calls.
The underlying provider details are abstracted away from user-facing code.
"""

from __future__ import annotations

import base64
import ipaddress
import logging
import mimetypes
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse

import requests

from .http_retry import request_with_retry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageJobResult:
    job_id: str
    status: str
    result_url: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class ImageProviderClient:
    def __init__(
        self,
        api_key: str,
        generate_url: Optional[str] = None,
        jobs_base_url: Optional[str] = None,
        timeout_seconds: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("API key is required")

        base_url = (os.getenv("SOCICLAW_IMAGE_API_BASE_URL") or "").strip().rstrip("/")
        default_generate_url = (
            f"{base_url}/api/v1?path=generate"
            if base_url
            else ""
        )
        default_jobs_base_url = (
            f"{base_url}/api/v1/jobs/"
            if base_url
            else ""
        )

        self.api_key = api_key.strip()
        self.generate_url = (generate_url or default_generate_url).strip()
        self.jobs_base_url = (jobs_base_url or default_jobs_base_url).strip().rstrip("/")
        if not self.generate_url or not self.jobs_base_url:
            raise ValueError(
                "Image API URLs are required. Set SOCICLAW_IMAGE_API_BASE_URL or pass generate_url/jobs_base_url."
            )
        self.jobs_base_url += "/"
        self.timeout_seconds = int(timeout_seconds)
        self.max_retries = int(os.getenv("SOCICLAW_HTTP_MAX_RETRIES", "3"))
        self.backoff_base_seconds = float(os.getenv("SOCICLAW_HTTP_BACKOFF_SECONDS", "0.5"))
        self.max_payload_bytes = int(os.getenv("SOCICLAW_IMAGE_INPUT_MAX_BYTES", str(10 * 1024 * 1024)))
        self.allow_remote_url = (
            os.getenv("SOCICLAW_ALLOW_IMAGE_URL_INPUT", "false").strip().lower()
            in {"1", "true", "yes", "on"}
        )
        self.allowed_input_roots = self._resolve_allowed_roots()
        self.allowed_url_hosts = self._resolve_allowed_url_hosts()
        self.max_remote_redirects = int(os.getenv("SOCICLAW_IMAGE_URL_MAX_REDIRECTS", "3"))
        self.session = session or requests.Session()

    def create_job(
        self,
        *,
        prompt: str,
        model: str,
        image_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        user_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        base_payload: Dict[str, Any] = {
            "prompt": prompt,
            "model": model,
        }
        if image_url:
            base_payload["image_url"] = image_url
        if webhook_url:
            base_payload["webhook_url"] = webhook_url
        if user_id:
            base_payload["user_id"] = user_id
        if extra:
            base_payload.update(extra)

        payload_candidates = [base_payload]
        if image_url:
            image_data_url = self._resolve_image_data_url(image_url)
            if image_data_url:
                payload_with_data_url = dict(base_payload)
                payload_with_data_url["image_data_url"] = image_data_url
                payload_candidates.append(payload_with_data_url)

                payload_data_only = dict(base_payload)
                payload_data_only.pop("image_url", None)
                payload_data_only["image_data_url"] = image_data_url
                payload_candidates.append(payload_data_only)

        last_response: Optional[requests.Response] = None
        for idx, payload in enumerate(payload_candidates):
            resp = request_with_retry(
                session=self.session,
                method="POST",
                url=self.generate_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout_seconds,
                max_retries=self.max_retries,
                backoff_base_seconds=self.backoff_base_seconds,
            )
            if resp.ok:
                return resp.json()

            last_response = resp
            has_fallback = idx < (len(payload_candidates) - 1)
            if has_fallback and self._should_retry_with_alternate_payload(resp):
                logger.warning(
                    "Generate request failed (%s). Retrying with alternate image payload format.",
                    resp.status_code,
                )
                continue

            resp.raise_for_status()

        if last_response is not None:
            last_response.raise_for_status()
        raise RuntimeError("Image API create_job failed without response")

    def _should_retry_with_alternate_payload(self, response: requests.Response) -> bool:
        if response.status_code not in {400, 422}:
            return False
        body = (response.text or "").lower()
        return any(
            token in body
            for token in (
                "image input",
                "image_url",
                "image_data_url",
                "missing image",
                "requires an image",
            )
        )

    def _resolve_image_data_url(self, image_url: str) -> Optional[str]:
        clean = str(image_url or "").strip()
        if not clean:
            return None
        if clean.startswith("data:image/"):
            return clean

        local_path = self._resolve_local_path(clean)
        if local_path and local_path.is_file():
            try:
                data = local_path.read_bytes()
            except OSError:
                return None
            content_type = self._guess_image_content_type(data, source_hint=str(local_path))
            if not content_type:
                logger.warning("Blocked non-image local file for image generation: %s", local_path)
                return None
            return self._build_image_data_url(data, source_hint=str(local_path), content_type_hint=content_type)

        if not self.allow_remote_url:
            return None

        disable = (os.getenv("SOCICLAW_DISABLE_IMAGE_DATA_URL_FALLBACK") or "").strip().lower()
        if disable in {"1", "true", "yes", "on"}:
            return None

        if not self._is_allowed_remote_image_url(clean):
            return None

        data, content_type, final_url = self._fetch_remote_image_bytes(clean)
        if not data:
            return None

        ct = (content_type or "").strip().lower()
        if not ct.startswith("image/"):
            ct = self._guess_image_content_type(data, source_hint=final_url or clean, header_hint=ct) or ct
            if not ct:
                return None

        return self._build_image_data_url(data, source_hint=final_url or clean, content_type_hint=ct)

    def _resolve_local_path(self, image_input: str) -> Optional[Path]:
        value = str(image_input or "").strip()
        if not value:
            return None

        if value.lower().startswith("file://"):
            parsed = urlparse(value)
            if parsed.scheme != "file":
                return None
            file_path = unquote(parsed.path or "")
            if os.name == "nt" and file_path.startswith("/"):
                file_path = file_path[1:]
            return self._normalize_local_path(file_path)

        try:
            candidate = Path(value)
        except (TypeError, ValueError):
            return None
        return self._normalize_local_path(candidate)

    def _normalize_local_path(self, path: str | Path) -> Optional[Path]:
        try:
            candidate = Path(path).expanduser()
            if not candidate.is_absolute():
                candidate = (Path.cwd() / candidate).resolve()
            else:
                candidate = candidate.resolve()
        except (OSError, RuntimeError):
            return None

        try:
            if not candidate.is_file():
                return None
        except OSError:
            return None

        if not self._is_allowed_path(candidate):
            logger.warning("Blocked local image path outside allowed roots: %s", candidate)
            return None
        return candidate

    def _resolve_allowed_roots(self) -> list[Path]:
        configured = os.getenv("SOCICLAW_ALLOWED_IMAGE_INPUT_DIRS")
        base = Path.cwd().resolve()
        candidate_roots: list[Path] = [base / ".sociclaw", base / ".tmp"]
        allow_absolute = (
            os.getenv("SOCICLAW_ALLOW_ABSOLUTE_IMAGE_INPUT_DIRS", "false").strip().lower()
            in {"1", "true", "yes", "on"}
        )
        if configured:
            candidate_roots = []
            for item in configured.split(","):
                value = item.strip()
                if not value:
                    continue

                p = Path(value).expanduser()
                if p.is_absolute():
                    if not allow_absolute:
                        logger.warning(
                            "Ignoring absolute SOCICLAW_ALLOWED_IMAGE_INPUT_DIRS entry (set SOCICLAW_ALLOW_ABSOLUTE_IMAGE_INPUT_DIRS=true to allow): %s",
                            p,
                        )
                        continue
                    candidate = p
                else:
                    candidate = (base / p)

                try:
                    resolved = candidate.resolve()
                except OSError:
                    resolved = candidate

                # Never allow filesystem roots (e.g. C:\ or /).
                if resolved.parent == resolved:
                    logger.warning("Ignoring root directory in SOCICLAW_ALLOWED_IMAGE_INPUT_DIRS: %s", resolved)
                    continue

                candidate_roots.append(resolved)
            if not candidate_roots:
                candidate_roots = [base / ".sociclaw", base / ".tmp"]
        resolved: list[Path] = []
        for root in candidate_roots:
            try:
                resolved.append(root.resolve())
            except OSError:
                resolved.append(Path(root).expanduser())
        unique: list[Path] = []
        for root in resolved:
            if root not in unique:
                unique.append(root)
        return unique

    def _resolve_allowed_url_hosts(self) -> list[str]:
        raw = (os.getenv("SOCICLAW_ALLOWED_IMAGE_URL_HOSTS") or "").strip()
        if not raw:
            return []
        items = []
        for item in raw.split(","):
            v = item.strip().lower().rstrip(".")
            if not v:
                continue
            items.append(v)
        unique: list[str] = []
        for v in items:
            if v not in unique:
                unique.append(v)
        return unique

    def _host_matches_allowlist(self, host: str) -> bool:
        normalized = (host or "").strip().lower().rstrip(".")
        if not normalized or not self.allowed_url_hosts:
            return False
        for pattern in self.allowed_url_hosts:
            if pattern == "*":
                return True
            if pattern.startswith("*."):
                base = pattern[2:]
                if normalized == base or normalized.endswith("." + base):
                    return True
                continue
            if normalized == pattern:
                return True
        return False

    def _is_allowed_remote_image_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
        except Exception:
            return False

        scheme = (parsed.scheme or "").lower()
        if scheme != "https":
            return False

        host = (parsed.hostname or "").strip().lower().rstrip(".")
        if not host:
            return False
        if host in {"localhost", "0.0.0.0"} or host.endswith(".local"):
            return False

        # If host is an IP literal, block private/link-local/etc.
        try:
            ip = ipaddress.ip_address(host)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                return False
        except ValueError:
            pass

        # Remote URL fetch is an explicit opt-in AND requires an explicit host allowlist.
        if not self._host_matches_allowlist(host):
            logger.warning("Blocked remote image URL host not in allowlist: %s", host)
            return False

        return True

    def _fetch_remote_image_bytes(self, url: str) -> tuple[bytes, Optional[str], Optional[str]]:
        try:
            with self.session.get(
                url,
                timeout=self.timeout_seconds,
                stream=True,
                allow_redirects=True,
                headers={"Accept": "image/*"},
            ) as resp:
                if not resp.ok:
                    return b"", None, None

                if resp.history and len(resp.history) > self.max_remote_redirects:
                    logger.warning("Blocked remote image URL with too many redirects (%s)", len(resp.history))
                    return b"", None, None

                final_url = resp.url or url
                if final_url != url and not self._is_allowed_remote_image_url(final_url):
                    logger.warning("Blocked remote image URL after redirect to disallowed host")
                    return b"", None, None

                content_type = (resp.headers.get("Content-Type", "") or "").split(";", 1)[0].strip().lower() or None

                total = 0
                chunks: list[bytes] = []
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > self.max_payload_bytes:
                        logger.warning("Remote image too large for data URL fallback (%s bytes)", total)
                        return b"", None, None
                    chunks.append(chunk)

                data = b"".join(chunks)
                return data, content_type, final_url
        except requests.RequestException:
            return b"", None, None

    def _is_allowed_path(self, candidate: Path) -> bool:
        for root in self.allowed_input_roots:
            try:
                candidate.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _guess_image_content_type(
        self,
        data: bytes,
        *,
        source_hint: str,
        header_hint: str | None = None,
    ) -> Optional[str]:
        if header_hint and header_hint.startswith("image/"):
            return header_hint
        kind = self._sniff_image_type(data)
        if kind:
            return f"image/{kind}"

        guessed, _ = mimetypes.guess_type(source_hint)
        if guessed and guessed.startswith("image/"):
            return guessed

        return None

    @staticmethod
    def _sniff_image_type(data: bytes) -> Optional[str]:
        if not data:
            return None

        png = data[:8]
        if png.startswith(b"\x89PNG\r\n\x1a\n"):
            return "png"
        if data[:3] == b"\xff\xd8\xff":
            return "jpeg"
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return "gif"
        if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return "webp"
        if len(data) >= 2 and data[:2] in (b"BM",):
            return "bmp"
        if len(data) >= 4 and data[:4] in (b"MM\x00*", b"II*\x00"):
            return "tiff"
        return None

    def _build_image_data_url(
        self,
        data: bytes,
        *,
        source_hint: str,
        content_type_hint: Optional[str],
    ) -> Optional[str]:
        if not data:
            return None
        if len(data) > self.max_payload_bytes:
            logger.warning("Input image too large for data URL fallback (%s bytes)", len(data))
            return None

        content_type = (content_type_hint or "").split(";")[0].strip().lower()
        if not content_type.startswith("image/"):
            return None

        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{content_type};base64,{encoded}"

    def get_job(self, job_id: str) -> Dict[str, Any]:
        url = f"{self.jobs_base_url}{job_id}"
        resp = request_with_retry(
            session=self.session,
            method="GET",
            url=url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=max(self.timeout_seconds, 60),
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )
        resp.raise_for_status()
        return resp.json()

    def wait_for_job(
        self,
        job_id: str,
        *,
        timeout_seconds: int = 180,
        poll_interval_seconds: int = 5,
    ) -> ImageJobResult:
        deadline = time.time() + int(timeout_seconds)
        last: Optional[Dict[str, Any]] = None

        while time.time() < deadline:
            last = self.get_job(job_id)
            status = str(last.get("status", "")).lower().strip()

            if status == "completed":
                return ImageJobResult(
                    job_id=job_id,
                    status=status,
                    result_url=last.get("result_url") or last.get("url"),
                    raw=last,
                )

            if status in {"failed", "error", "canceled", "cancelled"}:
                raise RuntimeError(f"Image job {job_id} failed: {last}")

            time.sleep(int(poll_interval_seconds))

        raise TimeoutError(f"Image job {job_id} did not complete within {timeout_seconds}s: {last}")

    def generate_image(
        self,
        *,
        prompt: str,
        model: str,
        image_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        user_id: Optional[str] = None,
        timeout_seconds: int = 180,
        poll_interval_seconds: int = 5,
    ) -> str:
        created = self.create_job(
            prompt=prompt,
            model=model,
            image_url=image_url,
            webhook_url=webhook_url,
            user_id=user_id,
        )

        job_id = created.get("job_id") or created.get("id")
        if not job_id:
            raise RuntimeError(f"create_job did not return job_id: {created}")

        result = self.wait_for_job(
            str(job_id),
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )

        if not result.result_url:
            raise RuntimeError(f"Image job completed but no result_url: {result.raw}")

        return str(result.result_url)
