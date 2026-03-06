from typing import Optional, Tuple

from scrapling.fetchers import Fetcher


def fetch(url: str, timeout: float = 15.0, verify_ssl: bool = True, headers: Optional[dict] = None) -> Tuple[str, str, int, dict]:
    page = Fetcher.get(
        url,
        timeout=timeout,
        verify=verify_ssl,
        headers=headers or {},
    )
    final_url = str(getattr(page, "url", url))
    html = getattr(page, "html", None) or str(page)
    status = int(getattr(page, "status", 200) or 200)
    meta = getattr(page, "meta", {}) or {}
    return final_url, html, status, meta
