#!/usr/bin/env python3
"""Convert RSS/Atom feeds to Markdown with safe URL/path handling."""

from __future__ import annotations

import argparse
import html
import ipaddress
import pathlib
import re
import socket
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

TAG_RE = re.compile(r"<[^>]+>")


def normalize_text(value: str) -> str:
    text = html.unescape(value or "")
    text = TAG_RE.sub("", text)
    return " ".join(text.split()).strip()


def validate_public_hostname(hostname: str, label: str) -> None:
    if hostname in {"localhost", "localhost.localdomain"}:
        raise ValueError(f"{label} uses localhost, which is not allowed")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Unable to resolve host: {hostname}") from exc

    for item in addr_info:
        ip_raw = item[4][0]
        ip = ipaddress.ip_address(ip_raw)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError(f"{label} resolves to a non-public IP address")


def validate_feed_url(raw_url: str, label: str = "Feed URL") -> str:
    parsed = urllib.parse.urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"{label} must use http or https")
    if not parsed.hostname:
        raise ValueError(f"{label} must include a hostname")

    hostname = parsed.hostname.strip().lower()
    validate_public_hostname(hostname, f"{label} host")

    return parsed.geturl()


def validate_output_path(raw_path: str) -> pathlib.Path:
    out_path = pathlib.Path(raw_path)
    if out_path.is_absolute():
        raise ValueError("Output path must be relative to the current workspace")
    if ".." in out_path.parts:
        raise ValueError("Output path must not contain '..'")
    if out_path.suffix.lower() != ".md":
        raise ValueError("Output path must end with .md")

    root = pathlib.Path.cwd().resolve()
    target = (root / out_path).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("Output path escapes the current workspace") from exc
    return target


class PublicOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        redirected_url = urllib.parse.urljoin(req.full_url, newurl)
        validate_feed_url(redirected_url, "Redirect URL")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_xml(url: str, timeout: int = 15) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    opener = urllib.request.build_opener(PublicOnlyRedirectHandler())
    with opener.open(request, timeout=timeout) as response:
        final_url = response.geturl()
        validate_feed_url(final_url, "Final URL")
        return response.read()


def namespace(tag: str) -> str | None:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return None


def find_text(elem: ET.Element, path: str, ns: dict[str, str] | None = None) -> str:
    child = elem.find(path, ns or {})
    if child is None or child.text is None:
        return ""
    return normalize_text(child.text)


def parse_rss(root: ET.Element) -> tuple[str, list[dict[str, str]]]:
    content_ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid RSS feed: missing channel")

    feed_title = find_text(channel, "title") or "Feed"
    entries: list[dict[str, str]] = []
    for item in channel.findall("item"):
        title = find_text(item, "title") or "Untitled"
        link = find_text(item, "link")
        summary = find_text(item, "content:encoded", content_ns) or find_text(
            item, "description"
        )
        published = find_text(item, "pubDate")
        entries.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
            }
        )
    return feed_title, entries


def parse_atom(root: ET.Element, atom_ns: str) -> tuple[str, list[dict[str, str]]]:
    ns = {"a": atom_ns}
    feed_title = find_text(root, "a:title", ns) or "Feed"
    entries: list[dict[str, str]] = []

    for entry in root.findall("a:entry", ns):
        title = find_text(entry, "a:title", ns) or "Untitled"
        summary = find_text(entry, "a:summary", ns) or find_text(entry, "a:content", ns)
        published = find_text(entry, "a:updated", ns) or find_text(entry, "a:published", ns)

        link = ""
        for link_elem in entry.findall("a:link", ns):
            href = (link_elem.attrib.get("href") or "").strip()
            rel = (link_elem.attrib.get("rel") or "alternate").strip()
            if not href:
                continue
            if rel == "alternate":
                link = href
                break
            if not link:
                link = href

        entries.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
            }
        )

    return feed_title, entries


def parse_feed(xml_bytes: bytes) -> tuple[str, list[dict[str, str]]]:
    root = ET.fromstring(xml_bytes)
    atom_ns = namespace(root.tag)
    if atom_ns == "http://www.w3.org/2005/Atom":
        return parse_atom(root, atom_ns)
    return parse_rss(root)


def truncate(value: str, max_len: int) -> str:
    if max_len <= 0 or len(value) <= max_len:
        return value
    clipped = value[: max_len - 1].rstrip()
    return f"{clipped}…"


def render_markdown(
    feed_title: str,
    entries: list[dict[str, str]],
    template: str,
    include_summary: bool,
    summary_max_len: int,
) -> str:
    lines: list[str] = [f"# {feed_title}", ""]

    if not entries:
        lines.extend(["No feed items found.", ""])
        return "\n".join(lines).rstrip() + "\n"

    if template == "short":
        for item in entries:
            title = item["title"]
            link = item["link"]
            published = item["published"]
            line = f"- [{title}]({link})" if link else f"- {title}"
            if published:
                line += f" ({published})"
            lines.append(line)
        lines.append("")
        return "\n".join(lines)

    for item in entries:
        title = item["title"]
        link = item["link"]
        summary = truncate(item["summary"], summary_max_len)
        published = item["published"]

        lines.append(f"## [{title}]({link})" if link else f"## {title}")
        if published:
            lines.append(f"- Published: {published}")
        if include_summary and summary:
            lines.append("")
            lines.append(summary)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert RSS/Atom feed URL to Markdown")
    parser.add_argument("url", help="RSS/Atom feed URL")
    parser.add_argument("-o", "--output", help="Write Markdown output to a .md file")
    parser.add_argument("--limit", type=int, default=0, help="Max number of feed items")
    parser.add_argument("--no-summary", action="store_true", help="Exclude summaries")
    parser.add_argument(
        "--summary-max-length",
        type=int,
        default=280,
        help="Max summary length before truncation",
    )
    parser.add_argument(
        "--template",
        choices=("short", "full"),
        default="short",
        help="Output template style",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    try:
        feed_url = validate_feed_url(args.url)
        output_path = validate_output_path(args.output) if args.output else None
        if args.limit < 0:
            raise ValueError("--limit must be >= 0")
        if args.summary_max_length < 0:
            raise ValueError("--summary-max-length must be >= 0")

        xml_bytes = fetch_xml(feed_url)
        feed_title, entries = parse_feed(xml_bytes)
        if args.limit:
            entries = entries[: args.limit]

        include_summary = (not args.no_summary) and args.template == "full"
        markdown = render_markdown(
            feed_title=feed_title,
            entries=entries,
            template=args.template,
            include_summary=include_summary,
            summary_max_len=args.summary_max_length,
        )

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
        else:
            sys.stdout.write(markdown)
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
