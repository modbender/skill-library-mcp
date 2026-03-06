"""
Module for generating images.

Provides:
- Exponential backoff retries
- Local image backup (downloads the generated image URL)
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

from .image_provider_client import ImageProviderClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImageResult:
    """
    Result of an image generation request.

    Attributes:
        url: URL of the generated image
        local_path: Local path where the image was saved
    """

    url: str
    local_path: Optional[Path] = None


class ImageGenerator:
    """
    Generate images with optional credit checks and retries.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        generate_url: Optional[str] = None,
        jobs_base_url: Optional[str] = None,
        image_url: Optional[str] = None,
        webhook_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        poll_interval_seconds: Optional[int] = None,
        provider_client: Optional[ImageProviderClient] = None,
        # Shared
        output_dir: Optional[Path] = None,
        max_retries: int = 3,
        backoff_base: float = 1.5,
    ) -> None:
        self.max_retries = int(max_retries)
        self.backoff_base = float(backoff_base)

        if output_dir is None:
            repo_root = Path(__file__).resolve().parents[2]
            output_dir = repo_root / ".sociclaw" / "generated_images"
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Image Provider Config
        self.provider_client = None
        self.model = (
            model
            or os.getenv("SOCICLAW_IMAGE_MODEL")
            or "nano-banana"
        )
        self.image_url = (
            image_url
            or os.getenv("SOCICLAW_IMAGE_URL")
        )
        self.webhook_url = (
            webhook_url
            or os.getenv("SOCICLAW_WEBHOOK_URL")
        )
        self.timeout_seconds = int(timeout_seconds or os.getenv("SOCICLAW_IMAGE_TIMEOUT_SECONDS") or 120)
        self.poll_interval_seconds = int(poll_interval_seconds or os.getenv("SOCICLAW_IMAGE_POLL_INTERVAL_SECONDS") or 2)

        _api_key = (
            api_key
            or os.getenv("SOCICLAW_IMAGE_API_KEY")
        )
        if not _api_key and provider_client is None:
            raise ValueError(
                "Missing image API key. Set SOCICLAW_IMAGE_API_KEY."
            )

        _generate_url = (
            generate_url
            or os.getenv("SOCICLAW_IMAGE_GENERATE_URL")
        )
        _jobs_base_url = (
            jobs_base_url
            or os.getenv("SOCICLAW_IMAGE_JOBS_URL")
        )

        self.provider_client = provider_client or ImageProviderClient(
            api_key=_api_key,
            generate_url=_generate_url,
            jobs_base_url=_jobs_base_url,
        )

        logger.info("ImageGenerator initialized")

    def generate_image(self, prompt: str, user_address: str) -> ImageResult:
        """
        Generate an image from a prompt.
        """
        last_error: Optional[Exception] = None
        delay = 1.0

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Generating image (attempt {attempt}/{self.max_retries})")

                url = self.provider_client.generate_image(
                    prompt=prompt,
                    model=self.model,
                    image_url=self.image_url,
                    webhook_url=self.webhook_url,
                    user_id=user_address,
                    timeout_seconds=self.timeout_seconds,
                    poll_interval_seconds=self.poll_interval_seconds,
                )

                local_path = self._save_image(url)

                return ImageResult(url=str(url), local_path=local_path)

            except Exception as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                logger.warning(f"Image generation failed: {exc}. Retrying in {delay:.1f}s")
                time.sleep(delay)
                delay *= self.backoff_base

        raise RuntimeError(f"Image generation failed after retries: {last_error}")

    def _save_image(self, url: str) -> Path:
        """
        Download and save the image locally.
        """
        filename = f"sociclaw_{int(time.time())}.png"
        file_path = self.output_dir / filename

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        file_path.write_bytes(response.content)
        logger.info(f"Saved image to {file_path}")
        return file_path
