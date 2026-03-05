#!/usr/bin/env python3
import argparse
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
from difflib import SequenceMatcher

CORP_CACHE = os.path.expanduser("~/.cache/opendart/corpcode.json")


def eprint(*args):
    print(*args, file=sys.stderr)


def get_api_key(cli_key: str | None) -> str:
    key = cli_key or os.getenv("OPENDART_API_KEY")
    if not key:
        raise SystemExit("Missing API key. Use --api-key or set OPENDART_API_KEY")
    return key


def http_get(url: str, params: dict) -> bytes:
    q = urllib.parse.urlencode(params)
    full = f"{url}?{q}"
    with urllib.request.urlopen(full, timeout=30) as r:
        return r.read()


def load_corp_list(api_key: str, force_refresh: bool = False) -> list[dict]:
    if (not force_refresh) and os.path.exists(CORP_CACHE):
        with open(CORP_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)

    raw = http_get("https://opendart.fss.or.kr/api/corpCode.xml", {"crtfc_key": api_key})
    zf = zipfile.ZipFile(io.BytesIO(raw))
    names = zf.namelist()
    if not names:
        raise SystemExit("corpCode response zip is empty")

    xml_data = zf.read(names[0])
    root = ET.fromstring(xml_data)

    corps = []
    for item in root.findall("list"):
        corp_code = (item.findtext("corp_code") or "").strip()
        corp_name = (item.findtext("corp_name") or "").strip()
        stock_code = (item.findtext("stock_code") or "").strip()
        modify_date = (item.findtext("modify_date") or "").strip()
        if corp_code and corp_name:
            corps.append(
                {
                    "corp_code": corp_code,
                    "corp_name": corp_name,
                    "stock_code": stock_code,
                    "modify_date": modify_date,
                }
            )

    os.makedirs(os.path.dirname(CORP_CACHE), exist_ok=True)
    with open(CORP_CACHE, "w", encoding="utf-8") as f:
        json.dump(corps, f, ensure_ascii=False)

    return corps


def normalize(s: str) -> str:
    return re.sub(r"\s+", "", s).lower()


def rank_corps(corps: list[dict], name: str, limit: int) -> list[dict]:
    n = normalize(name)
    scored = []
    for c in corps:
        cn = normalize(c["corp_name"])
        score = SequenceMatcher(None, n, cn).ratio()
        if n in cn:
            score += 0.4
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, c in scored[:limit]:
        obj = dict(c)
        obj["score"] = round(score, 4)
        out.append(obj)
    return out


def cmd_search_corp(args):
    api_key = get_api_key(args.api_key)
    corps = load_corp_list(api_key, force_refresh=args.refresh)
    matches = rank_corps(corps, args.name, args.limit)
    print(json.dumps({"query": args.name, "results": matches}, ensure_ascii=False, indent=2))


def _fetch_recent(api_key: str, corp_code: str, from_date: str, to_date: str, limit: int, pblntf_ty: str | None, last_reprt_at: str | None):
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": from_date,
        "end_de": to_date,
        "page_no": 1,
        "page_count": min(max(limit, 1), 100),
    }
    if pblntf_ty:
        params["pblntf_ty"] = pblntf_ty
    if last_reprt_at:
        params["last_reprt_at"] = last_reprt_at

    raw = http_get("https://opendart.fss.or.kr/api/list.json", params)
    data = json.loads(raw.decode("utf-8", errors="replace"))

    status = data.get("status")
    if status != "000":
        msg = data.get("message", "Unknown OpenDART error")
        raise SystemExit(f"OpenDART error {status}: {msg}")

    items = data.get("list", [])
    items.sort(key=lambda x: (x.get("rcept_dt", ""), x.get("rcept_no", "")), reverse=True)
    items = items[:limit]

    out = []
    for x in items:
        rcept_no = x.get("rcept_no", "")
        out.append(
            {
                "corp_name": x.get("corp_name", ""),
                "corp_code": x.get("corp_code", ""),
                "report_name": x.get("report_nm", ""),
                "receipt_no": rcept_no,
                "receipt_date": x.get("rcept_dt", ""),
                "flr_name": x.get("flr_nm", ""),
                "link": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
            }
        )
    return out


def resolve_dates(args):
    if args.today:
        d = datetime.now().strftime("%Y%m%d")
        return d, d
    if args.days is not None:
        if args.days <= 0:
            raise SystemExit("--days must be >= 1")
        end = datetime.now()
        start = end - timedelta(days=args.days - 1)
        return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
    if args.from_date and args.to_date:
        return args.from_date, args.to_date
    raise SystemExit("Provide --today, --days N, or both --from and --to")


def cmd_recent(args):
    api_key = get_api_key(args.api_key)
    from_date, to_date = resolve_dates(args)
    out = _fetch_recent(api_key, args.corp_code, from_date, to_date, args.limit, args.pblntf_ty, args.last_reprt_at)
    print(
        json.dumps(
            {
                "corp_code": args.corp_code,
                "from": from_date,
                "to": to_date,
                "count": len(out),
                "results": out,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_recent_by_name(args):
    api_key = get_api_key(args.api_key)
    from_date, to_date = resolve_dates(args)
    corps = load_corp_list(api_key, force_refresh=args.refresh)
    matches = rank_corps(corps, args.name, 1)
    if not matches:
        raise SystemExit(f"No company matched: {args.name}")
    best = matches[0]
    out = _fetch_recent(api_key, best["corp_code"], from_date, to_date, args.limit, args.pblntf_ty, args.last_reprt_at)
    print(
        json.dumps(
            {
                "query": args.name,
                "matched": {
                    "corp_name": best["corp_name"],
                    "corp_code": best["corp_code"],
                    "stock_code": best.get("stock_code", ""),
                    "score": best.get("score"),
                },
                "from": from_date,
                "to": to_date,
                "count": len(out),
                "results": out,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def build_parser():
    p = argparse.ArgumentParser(description="OpenDART utility")
    p.add_argument("--api-key", help="OpenDART API key (fallback: OPENDART_API_KEY)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("search-corp", help="Search company candidates by name")
    s1.add_argument("--name", required=True, help="Company name")
    s1.add_argument("--limit", type=int, default=10)
    s1.add_argument("--refresh", action="store_true", help="Refresh corp code cache")
    s1.set_defaults(func=cmd_search_corp)

    s2 = sub.add_parser("recent", help="Get recent disclosures by corp_code")
    s2.add_argument("--corp-code", required=True)
    s2.add_argument("--from", dest="from_date", help="YYYYMMDD")
    s2.add_argument("--to", dest="to_date", help="YYYYMMDD")
    s2.add_argument("--today", action="store_true", help="Shortcut for today only")
    s2.add_argument("--days", type=int, help="Shortcut for last N days")
    s2.add_argument("--limit", type=int, default=10)
    s2.add_argument("--pblntf-ty", help="A/B/C... publication type")
    s2.add_argument("--last-reprt-at", choices=["Y", "N"], help="Only final report")
    s2.set_defaults(func=cmd_recent)

    s3 = sub.add_parser("recent-by-name", help="Resolve company name then get recent disclosures")
    s3.add_argument("--name", required=True, help="Company name")
    s3.add_argument("--from", dest="from_date", help="YYYYMMDD")
    s3.add_argument("--to", dest="to_date", help="YYYYMMDD")
    s3.add_argument("--today", action="store_true", help="Shortcut for today only")
    s3.add_argument("--days", type=int, help="Shortcut for last N days")
    s3.add_argument("--limit", type=int, default=10)
    s3.add_argument("--pblntf-ty", help="A/B/C... publication type")
    s3.add_argument("--last-reprt-at", choices=["Y", "N"], help="Only final report")
    s3.add_argument("--refresh", action="store_true", help="Refresh corp code cache")
    s3.set_defaults(func=cmd_recent_by_name)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
