#!/usr/bin/env python3
"""Sci-Hub PDF 定位器 — 给 DOI，返回 PDF URL。

零依赖，仅使用 Python 标准库。
"""
import json
import re
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

TIMEOUT = 10
MIRRORS = [
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ru",
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def _extract_pdf_url(html: str, mirror: str) -> str:
    for pat in [
        r'<(?:iframe|embed)[^>]+src=["\']([^"\']+)["\']',
        r'["\']((?:https?:)?//[^"\']+?\.pdf[^"\']*)["\']',
    ]:
        for url in re.findall(pat, html, re.IGNORECASE):
            url = url.strip().replace("\\/", "/")
            if url.startswith("//"):
                url = f"https:{url}"
            elif url.startswith("/"):
                url = f"{mirror}{url}"
            elif not url.startswith("http"):
                continue
            if ".pdf" in url.lower() or "/pdf" in url.lower():
                return url
    return ""


def find_pdf(doi: str) -> dict:
    """尝试官方 Sci-Hub 镜像，找到 PDF URL 就返回。"""
    safe_doi = quote(doi.strip(), safe="/:().-_")
    for mirror in MIRRORS:
        try:
            req = Request(f"{mirror}/{safe_doi}", headers={"User-Agent": UA})
            with urlopen(req, timeout=TIMEOUT) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            pdf = _extract_pdf_url(html, mirror)
            if pdf:
                return {"doi": doi, "pdf_url": pdf, "mirror": mirror, "status": "found"}
        except Exception:
            continue
    return {"doi": doi, "pdf_url": "", "mirror": "", "status": "not_found"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scihub.py <DOI>", file=sys.stderr)
        sys.exit(1)
    result = find_pdf(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "found" else 1)
