#!/usr/bin/env python3
import argparse
import html as html_lib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

STORE_PATH = Path.home() / ".openclaw" / "state" / "price-watcher" / "watchers.json"
MAX_BYTES = 2_000_000
TIMEOUT = 12
UA = "Mozilla/5.0 (compatible; OpenClaw-PriceWatcher/1.1)"

PRICE_RE = re.compile(r"(?:\$|CLP\s?|USD\s?)\s*([0-9][0-9\.,\s]{1,20})", re.IGNORECASE)
META_PRICE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\'](?:product:price:amount|og:price:amount|twitter:data1)["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
JSONLD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
DDG_LINK_RE = re.compile(r'<a[^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]+href=["\']([^"\']+)["\']', re.IGNORECASE)

TRUSTED_DOMAINS = [
    "falabella.com",
    "paris.cl",
    "ripley.cl",
    "lider.cl",
    "mercadolibre.cl",
    "abcdin.cl",
    "hites.com",
    "pcfactory.cl",
    "maconline.com",
    "entel.cl",
    "claro.cl",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")


def load_store() -> Dict[str, Any]:
    ensure_store()
    with STORE_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "items" not in data or not isinstance(data["items"], list):
        data = {"items": []}
    return data


def save_store(data: Dict[str, Any]) -> None:
    with STORE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_price(raw: str) -> Optional[float]:
    s = raw.strip().replace(" ", "")
    s = s.replace(".", "").replace(",", ".")
    try:
        value = float(s)
        return value if value > 0 else None
    except ValueError:
        return None


def parse_title(html: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        return "(unknown title)"
    return re.sub(r"\s+", " ", m.group(1)).strip()[:220]


def extract_jsonld_prices(html: str) -> List[float]:
    out: List[float] = []
    for m in JSONLD_RE.finditer(html):
        blob = m.group(1).strip()
        try:
            parsed = json.loads(blob)
        except Exception:
            continue
        stack = [parsed]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if "price" in node and isinstance(node["price"], (str, int, float)):
                    p = normalize_price(str(node["price"]))
                    if p:
                        out.append(p)
                for v in node.values():
                    stack.append(v)
            elif isinstance(node, list):
                stack.extend(node)
    return out


def extract_meta_prices(html: str) -> List[float]:
    prices: List[float] = []
    for m in META_PRICE_RE.finditer(html):
        p = normalize_price(m.group(1))
        if p:
            prices.append(p)
    return prices


def extract_regex_prices(html: str) -> List[float]:
    prices: List[float] = []
    for m in PRICE_RE.finditer(html):
        p = normalize_price(m.group(1))
        if p:
            prices.append(p)
    return prices


def validate_url(url: str) -> None:
    p = urlparse(url)
    if p.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed")
    if not p.netloc:
        raise ValueError("Invalid URL")


def fetch_html(url: str) -> str:
    validate_url(url)
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=TIMEOUT) as r:
        content_type = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            raise ValueError(f"Unsupported content type: {content_type}")
        raw = r.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Response too large")
        return raw.decode("utf-8", errors="replace")


def parse_product(url: str) -> Tuple[str, Optional[float], Dict[str, Any]]:
    html = fetch_html(url)
    title = parse_title(html)

    candidates: List[Tuple[str, float]] = []
    for p in extract_jsonld_prices(html):
        candidates.append(("jsonld", p))
    for p in extract_meta_prices(html):
        candidates.append(("meta", p))
    for p in extract_regex_prices(html):
        candidates.append(("regex", p))

    if not candidates:
        return title, None, {"sources": []}

    source, best = min(candidates, key=lambda x: x[1])
    return title, best, {
        "source": source,
        "candidates": [{"source": s, "price": p} for s, p in candidates[:25]],
    }


def domain_matches(url: str, allowlist: List[str]) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == d or host.endswith("." + d) for d in allowlist)


def parse_ddg_redirect(link: str) -> str:
    # DuckDuckGo often returns /l/?uddg=<encoded-url>
    if "uddg=" not in link:
        return link
    part = link.split("uddg=", 1)[1]
    part = part.split("&", 1)[0]
    return unquote(part)


def discover_product_urls(query: str, trusted_only: bool, max_results: int) -> List[str]:
    q = quote_plus(query)
    search_url = f"https://html.duckduckgo.com/html/?q={q}"
    html = fetch_html(search_url)

    urls: List[str] = []
    seen = set()
    for m in DDG_LINK_RE.finditer(html):
        href = html_lib.unescape(m.group(1))
        href = parse_ddg_redirect(href)
        if not href.startswith("http"):
            continue
        try:
            validate_url(href)
        except ValueError:
            continue
        if trusted_only and not domain_matches(href, TRUSTED_DOMAINS):
            continue
        if href in seen:
            continue
        seen.add(href)
        urls.append(href)
        if len(urls) >= max_results:
            break
    return urls


def add_watch_item(data: Dict[str, Any], url: str, target_price: Optional[float], currency: str, query: Optional[str] = None) -> Dict[str, Any]:
    # prevent exact duplicates
    for it in data["items"]:
        if it.get("url") == url:
            return {"id": it["id"], "url": url, "duplicate": True}

    wid = uuid.uuid4().hex[:10]
    item = {
        "id": wid,
        "url": url,
        "targetPrice": target_price,
        "currency": currency,
        "title": "",
        "currentPrice": None,
        "previousPrice": None,
        "lowestPrice": None,
        "lastCheckedAt": None,
        "history": [],
        "createdAt": now_iso(),
    }
    if query:
        item["query"] = query
    data["items"].append(item)
    return {"id": wid, "url": url, "duplicate": False}


def cmd_add(args: argparse.Namespace) -> int:
    data = load_store()
    result = add_watch_item(data, args.url, args.target_price, args.currency)
    save_store(data)
    print(json.dumps({"ok": True, "item": result, "store": str(STORE_PATH)}))
    return 0


def cmd_add_item(args: argparse.Namespace) -> int:
    data = load_store()
    query = args.query.strip()
    if not query:
        print(json.dumps({"ok": False, "error": "query is required"}))
        return 2

    urls = discover_product_urls(query=query, trusted_only=args.trusted_only, max_results=args.max_results)
    if not urls:
        print(json.dumps({"ok": False, "error": "No product URLs discovered for query"}))
        return 2

    created: List[Dict[str, Any]] = []
    for u in urls:
        created.append(add_watch_item(data, u, args.target_price, args.currency, query=query))

    save_store(data)
    print(json.dumps({
        "ok": True,
        "query": query,
        "created": created,
        "count": len(created),
        "trustedOnly": args.trusted_only,
    }, ensure_ascii=False))
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    data = load_store()
    print(json.dumps({"ok": True, "count": len(data["items"]), "items": data["items"]}, ensure_ascii=False))
    return 0


def evaluate_alerts(item: Dict[str, Any], new_price: Optional[float]) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    prev = item.get("currentPrice")
    target = item.get("targetPrice")

    if new_price is None:
        return alerts

    if prev is not None and new_price < prev:
        drop_pct = ((prev - new_price) / prev) * 100 if prev > 0 else 0
        alerts.append({
            "type": "price_drop",
            "oldPrice": prev,
            "newPrice": new_price,
            "dropPercent": round(drop_pct, 2),
        })

    if target is not None and new_price <= target:
        alerts.append({
            "type": "target_hit",
            "targetPrice": target,
            "newPrice": new_price,
        })

    return alerts


def check_one(item: Dict[str, Any]) -> Dict[str, Any]:
    checked_at = now_iso()
    try:
        title, price, debug = parse_product(item["url"])
    except Exception as e:
        return {"id": item["id"], "ok": False, "error": str(e), "checkedAt": checked_at}

    alerts = evaluate_alerts(item, price)
    item["previousPrice"] = item.get("currentPrice")
    item["currentPrice"] = price
    item["title"] = title
    item["lastCheckedAt"] = checked_at

    if price is not None:
        lp = item.get("lowestPrice")
        item["lowestPrice"] = price if lp is None else min(lp, price)

    item.setdefault("history", []).append({
        "at": checked_at,
        "price": price,
        "alerts": alerts,
    })
    item["history"] = item["history"][-120:]

    return {
        "id": item["id"],
        "ok": True,
        "title": title,
        "url": item["url"],
        "price": price,
        "previousPrice": item.get("previousPrice"),
        "currency": item.get("currency"),
        "alerts": alerts,
        "checkedAt": checked_at,
        "debug": debug,
    }


def cmd_check(args: argparse.Namespace) -> int:
    data = load_store()
    items = data["items"]

    if args.all:
        selected = items
    else:
        selected = [x for x in items if x["id"] == args.id]

    if not selected:
        print(json.dumps({"ok": False, "error": "No matching watch items"}))
        return 2

    results = [check_one(x) for x in selected]
    save_store(data)

    alerts = []
    for r in results:
        for a in r.get("alerts", []):
            alerts.append({**a, "id": r.get("id"), "title": r.get("title"), "url": r.get("url")})

    print(json.dumps({"ok": True, "results": results, "alerts": alerts}, ensure_ascii=False))
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    data = load_store()
    before = len(data["items"])
    data["items"] = [x for x in data["items"] if x["id"] != args.id]
    save_store(data)
    print(json.dumps({"ok": True, "removed": before - len(data["items"])}))
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    data = load_store()
    item = next((x for x in data["items"] if x["id"] == args.id), None)
    if not item:
        print(json.dumps({"ok": False, "error": "Not found"}))
        return 2
    print(json.dumps({"ok": True, "id": item["id"], "history": item.get("history", [])}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ecommerce price watcher")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Add one product URL")
    a.add_argument("--url", required=True)
    a.add_argument("--target-price", type=float, default=None)
    a.add_argument("--currency", default="CLP")
    a.set_defaults(func=cmd_add)

    ai = sub.add_parser("add-item", help="Add watches by product query (discovers URLs)")
    ai.add_argument("--query", required=True)
    ai.add_argument("--target-price", type=float, default=None)
    ai.add_argument("--currency", default="CLP")
    ai.add_argument("--max-results", type=int, default=5)
    ai.add_argument("--trusted-only", action="store_true")
    ai.set_defaults(func=cmd_add_item)

    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)

    c = sub.add_parser("check")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--id")
    g.add_argument("--all", action="store_true")
    c.set_defaults(func=cmd_check)

    rm = sub.add_parser("remove")
    rm.add_argument("--id", required=True)
    rm.set_defaults(func=cmd_remove)

    h = sub.add_parser("history")
    h.add_argument("--id", required=True)
    h.set_defaults(func=cmd_history)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
