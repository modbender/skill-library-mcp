#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://geizhals.at"
SCHEMA_VERSION = "1.0"
CACHE_TTL_SECONDS = 900

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "de-AT,de;q=0.9,en;q=0.8",
    "Referer": "https://geizhals.at/",
}

ACS_HEADERS = {
    **BASE_HEADERS,
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://geizhals.at",
    "X-Requested-With": "XMLHttpRequest",
}


class FetchError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def _cache_path(cache_dir: Path, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}.txt"


def _is_retryable_status(status: int | None) -> bool:
    return status in {403, 408, 409, 425, 429, 500, 502, 503, 504}


def fetch_text(
    url: str,
    timeout: int = 15,
    extra_headers: dict[str, str] | None = None,
    retries: int = 3,
    backoff_base: float = 0.6,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int = CACHE_TTL_SECONDS,
    debug: bool = False,
) -> str:
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cp = _cache_path(cache_dir, url)
        if cp.exists() and (time.time() - cp.stat().st_mtime) < cache_ttl_seconds:
            if debug:
                print(f"[debug] cache hit {url}", file=sys.stderr)
            return cp.read_text(encoding="utf-8")

    headers = dict(BASE_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)

    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", "ignore")
                if cache_dir is not None:
                    _cache_path(cache_dir, url).write_text(body, encoding="utf-8")
                return body
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode("utf-8", "ignore")
            if debug:
                print(f"[debug] http {status} attempt={attempt} url={url}", file=sys.stderr)
            if _is_retryable_status(status) and attempt < retries:
                time.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            if body:
                raise FetchError(f"HTTP {status} for {url} ({len(body)} bytes body)", status=status)
            raise FetchError(f"HTTP {status} for {url}", status=status)
        except Exception as e:
            last_err = e
            if debug:
                print(f"[debug] network error attempt={attempt} url={url}: {e}", file=sys.stderr)
            if attempt < retries:
                time.sleep(backoff_base * (2 ** (attempt - 1)))
                continue
            break

    raise FetchError(f"Failed to fetch {url}: {last_err}")


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def parse_price_from_title(title_text: str) -> float | None:
    t = html.unescape(title_text)
    m = re.search(r"ab\s*€\s*([0-9][0-9\.,]*)", t, re.IGNORECASE)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_price_from_meta(page_html: str) -> float | None:
    # e.g. <meta property="product:price:amount" content="599.00">
    m = re.search(
        r'<meta[^>]+property=["\']product:price:amount["\'][^>]+content=["\']([0-9]+(?:\.[0-9]+)?)["\']',
        page_html,
        re.IGNORECASE,
    )
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def parse_offer_count(page_html: str) -> int | None:
    m = re.search(r"\b([0-9]{1,5})\s+Angebote\b", page_html, re.IGNORECASE)
    return int(m.group(1)) if m else None


def parse_cheapest_shop(page_html: str) -> tuple[float | None, str | None]:
    patterns = [
        r'"tracking_merchant"\s*:\s*"([^\"]+)".{1,2000}?"raw_price"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        r'"raw_price"\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*"[^\"]*".{0,400}?"tracking_merchant"\s*:\s*"([^\"]+)"',
        r'"merchant"\s*:\s*"([^\"]+)".{1,2000}?"price"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
    ]

    best_price: float | None = None
    best_shop: str | None = None

    for pat in patterns:
        for m in re.findall(pat, page_html, flags=re.IGNORECASE | re.DOTALL):
            if len(m) != 2:
                continue

            if pat.startswith('"raw_price"'):
                p_str, shop_str = m
            else:
                shop_str, p_str = m

            try:
                p = float(p_str)
            except ValueError:
                continue

            if best_price is None or p < best_price:
                best_price = p
                best_shop = html.unescape(shop_str)

    return best_price, best_shop


def extract_title_tag(page_html: str) -> str | None:
    m = re.search(r"<title>(.*?)</title>", page_html, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    return html.unescape(m.group(1)).strip()


def acs_search(query: str, debug: bool = False) -> list[list[Any]]:
    url = f"{BASE}/acs?lang=de&loc=at&o=json&k={urllib.parse.quote(query)}"
    raw = fetch_text(url, extra_headers=ACS_HEADERS, retries=3, backoff_base=0.5, debug=debug)
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    return data


def candidate_to_url(candidate: list[Any]) -> str | None:
    if not candidate:
        return None
    first = candidate[0] if len(candidate) > 0 else None
    if isinstance(first, str) and first:
        if first.startswith("http"):
            return first
        if first.startswith("/"):
            return BASE + first
        return f"{BASE}/{first}"
    return None


def enrich_item(page: str) -> dict[str, Any]:
    title = extract_title_tag(page) or ""
    offer_count = parse_offer_count(page)

    best_price, best_shop = parse_cheapest_shop(page)
    if best_price is not None:
        return {
            "min_price_eur": best_price,
            "shop": best_shop,
            "price_confidence": "high",
            "price_source": "embedded_offer_raw_price",
            "offer_count": offer_count,
            "page_title": title,
        }

    meta_price = parse_price_from_meta(page)
    if meta_price is not None:
        return {
            "min_price_eur": meta_price,
            "shop": best_shop,
            "price_confidence": "medium",
            "price_source": "meta_product_price",
            "offer_count": offer_count,
            "page_title": title,
        }

    title_price = parse_price_from_title(title)
    if title_price is not None:
        return {
            "min_price_eur": title_price,
            "shop": best_shop,
            "price_confidence": "low",
            "price_source": "title_ab_price",
            "offer_count": offer_count,
            "page_title": title,
        }

    return {
        "min_price_eur": None,
        "shop": best_shop,
        "price_confidence": "unknown",
        "price_source": "none",
        "offer_count": offer_count,
        "page_title": title,
    }


def search(query: str, limit: int, debug: bool = False, cache_dir: Path | None = None) -> list[dict[str, Any]]:
    rows = acs_search(query, debug=debug)
    out: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, list) or len(row) < 2:
            continue

        name_html = row[1] if len(row) > 1 else ""
        name = html.unescape(strip_tags(name_html)).strip()
        if not name:
            continue

        detail_url = candidate_to_url(row)
        if not detail_url:
            continue

        item: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "name": name,
            "detail_url": detail_url,
            "min_price_eur": None,
            "offer_count": None,
            "shop": None,
            "price_confidence": "unknown",
            "price_source": "none",
            "error": None,
        }

        try:
            page = fetch_text(
                detail_url,
                extra_headers={"Accept": "text/html,*/*"},
                retries=3,
                backoff_base=0.6,
                cache_dir=cache_dir,
                debug=debug,
            )
            item.update(enrich_item(page))
        except Exception as e:
            item["error"] = str(e)

        out.append(item)
        if len(out) >= limit:
            break

        time.sleep(0.2)

    return out


def print_table(items: list[dict[str, Any]]) -> None:
    if not items:
        print("No results")
        return
    for i, it in enumerate(items, 1):
        price = it.get("min_price_eur")
        price_s = f"€{price:.2f}" if isinstance(price, (int, float)) else "n/a"
        offers = it.get("offer_count")
        offers_s = str(offers) if isinstance(offers, int) else "n/a"
        shop = it.get("shop") or "n/a"
        conf = it.get("price_confidence") or "unknown"
        source = it.get("price_source") or "none"
        print(f"{i}. {it.get('name','-')}")
        print(f"   Price: {price_s} | Shop: {shop} | Offers: {offers_s}")
        print(f"   Confidence: {conf} ({source})")
        print(f"   URL: {it.get('detail_url','-')}")
        if it.get("error"):
            print(f"   Error: {it['error']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="geizhals skill prototype")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="Search Geizhals")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=5)
    p_search.add_argument("--json", action="store_true", dest="as_json")
    p_search.add_argument("--debug", action="store_true")
    p_search.add_argument(
        "--cache-dir",
        default=os.path.expanduser("~/.cache/geizhals-skill"),
        help="Cache directory for detail pages (default: ~/.cache/geizhals-skill)",
    )

    args = parser.parse_args()

    if args.cmd == "search":
        items = search(
            args.query,
            max(1, min(args.limit, 15)),
            debug=args.debug,
            cache_dir=Path(args.cache_dir),
        )
        if args.as_json:
            print(json.dumps(items, ensure_ascii=False, indent=2))
        else:
            print_table(items)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
