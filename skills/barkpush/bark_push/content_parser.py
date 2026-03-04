from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .utils import extract_image_urls, extract_urls, is_image_url, is_url, safe_host, strip_urls


class ContentType(str, Enum):
    IMAGE_ONLY = "image_only"
    URL_ONLY = "url_only"
    TEXT_ONLY = "text_only"
    MIXED = "mixed"


@dataclass(frozen=True)
class ParsedContent:
    content_type: ContentType
    text: str
    urls: list[str]
    images: list[str]
    markdown: str | None


class ContentParser:
    def parse(self, raw: str) -> ParsedContent:
        content = (raw or "").strip()
        if not content:
            return ParsedContent(
                content_type=ContentType.TEXT_ONLY,
                text="",
                urls=[],
                images=[],
                markdown=None,
            )

        if is_image_url(content):
            return ParsedContent(
                content_type=ContentType.IMAGE_ONLY,
                text="",
                urls=[],
                images=[content],
                markdown=None,
            )

        if is_url(content):
            return ParsedContent(
                content_type=ContentType.URL_ONLY,
                text="",
                urls=[content],
                images=[],
                markdown=None,
            )

        urls = extract_urls(content)
        images = extract_image_urls(content)
        text = strip_urls(content)

        if images and not text and len(urls) == len(images):
            return ParsedContent(
                content_type=ContentType.IMAGE_ONLY,
                text="",
                urls=[],
                images=images,
                markdown=None,
            )

        if urls and not images and not text:
            return ParsedContent(
                content_type=ContentType.URL_ONLY,
                text="",
                urls=urls,
                images=[],
                markdown=None,
            )

        if not urls and not images:
            return ParsedContent(
                content_type=ContentType.TEXT_ONLY,
                text=text,
                urls=[],
                images=[],
                markdown=None,
            )

        md = self._format_markdown(text=text, urls=urls, images=images)
        return ParsedContent(
            content_type=ContentType.MIXED,
            text=text,
            urls=urls,
            images=images,
            markdown=md,
        )

    def auto_title_subtitle(self, parsed: ParsedContent) -> tuple[str, str]:
        if parsed.content_type == ContentType.IMAGE_ONLY and parsed.images:
            host = safe_host(parsed.images[0])
            return ("图片", host or "")
        if parsed.content_type == ContentType.URL_ONLY and parsed.urls:
            host = safe_host(parsed.urls[0])
            return ("链接", host or "")
        base = (parsed.text or parsed.markdown or "").strip()
        if not base:
            return ("通知", "")
        title = base[:12]
        subtitle = base[12:32].strip()
        return (title, subtitle)

    def _format_markdown(self, text: str, urls: list[str], images: list[str]) -> str:
        parts: list[str] = []
        if text:
            parts.append(text)
        if urls:
            parts.append("")
            parts.append("链接：")
            for u in urls:
                parts.append(f"- {u}")
        if images:
            parts.append("")
            parts.append("图片：")
            for img in images:
                parts.append(f"![]({img})")
        return "\n".join(parts).strip()
