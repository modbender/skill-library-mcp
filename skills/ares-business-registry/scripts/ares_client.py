#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import socket
import urllib.error
import urllib.request

DEFAULT_BASE = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest"
CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 20
RETRYABLE_HTTP_CODES = {429, 502, 503, 504}
RETRY_BACKOFF_SECONDS = (1, 2, 4)
CACHE_TTL_SECONDS = 24 * 60 * 60
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
DEFAULT_SORT = "+obchodniJmeno"

CURATED_PRAVNI_FORMA_OVERRIDES = {
    112: "s.r.o.",
    121: "a.s.",
    141: "z.s.",
    701: "OSVČ",
    301: "s.p.",
    331: "p.o.",
}

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_ARES_NON_OK = 2
EXIT_NETWORK = 3


class ValidationError(Exception):
    pass


class AresError(Exception):
    def __init__(self, message: str, *, status: int | None = None, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.details = details or {}


class NetworkError(Exception):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


_PRAVNI_FORMA_MEMORY_CACHE: dict[int, str] | None = None
_PRAVNI_FORMA_MEMORY_TS: int | None = None


def eprint(*parts: Any) -> None:
    print(*parts, file=sys.stderr)


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def cache_file() -> Path:
    return root_dir() / ".cache" / "pravni_forma.json"


def safe_int(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def http_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call ARES and return parsed JSON object.

    Uses only Python stdlib (urllib) to keep the skill dependency-free.
    """

    delays = list(RETRY_BACKOFF_SECONDS)
    attempts = 1 + len(delays)

    body: bytes | None = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    timeout_seconds = max(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS)

    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url=url, data=body, method=method.upper(), headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                status = int(getattr(resp, "status", 200))
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                if status != 200:
                    raise urllib.error.HTTPError(url, status, "HTTP error", resp.headers, None)

        except urllib.error.HTTPError as err:
            status = int(getattr(err, "code", 0) or 0)
            retry_after = None
            if hasattr(err, "headers") and err.headers is not None:
                retry_after = err.headers.get("Retry-After")

            if status in RETRYABLE_HTTP_CODES and attempt < len(delays):
                sleep_seconds = delays[attempt]
                if retry_after and str(retry_after).isdigit():
                    sleep_seconds = max(sleep_seconds, int(retry_after))
                time.sleep(sleep_seconds)
                continue

            excerpt = ""
            try:
                if hasattr(err, "read"):
                    excerpt = (err.read() or b"")[:400].decode("utf-8", errors="replace")
            except Exception:
                excerpt = ""

            raise AresError(
                f"ARES HTTP {status}" if status else "ARES HTTP error",
                status=status or None,
                details={"url": url, "response_excerpt": excerpt},
            ) from err

        except (urllib.error.URLError, socket.timeout) as err:
            if attempt < len(delays):
                time.sleep(delays[attempt])
                continue
            raise NetworkError(
                f"Network/timeout while calling ARES: {url}",
                details={"url": url, "error": str(err)},
            ) from err

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as err:
            raise AresError(
                f"ARES returned invalid JSON for {url}",
                status=200,
                details={"url": url},
            ) from err

        if not isinstance(parsed, dict):
            raise AresError(
                "ARES payload is not a JSON object",
                status=200,
                details={"url": url},
            )
        return parsed

    raise NetworkError(f"Failed after retries: {url}", details={"url": url})


def pick_first(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = d.get(key)
        if value not in (None, ""):
            return value
    return None


def _str_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def normalize_address(subject: dict[str, Any]) -> dict[str, Any]:
    addr = pick_first(subject, "sidlo", "adresa", "adresaSidla")
    if not isinstance(addr, dict):
        return {"text": None, "city": None, "psc": None}
    text = pick_first(addr, "textovaAdresa", "text", "adresaText")
    city = pick_first(addr, "nazevObce", "obec", "mesto", "castObce")
    psc = pick_first(addr, "psc", "pscTxt", "zip")
    return {"text": _str_or_none(text), "city": _str_or_none(city), "psc": _str_or_none(psc)}


def extract_pravni_forma_code(subject: dict[str, Any]) -> int | None:
    value = subject.get("pravniForma")
    if isinstance(value, dict):
        return safe_int(pick_first(value, "kod", "code", "id"))
    return safe_int(value)


def normalize_subject(subject: dict[str, Any], pravni_forma_map: dict[int, str]) -> dict[str, Any]:
    code = extract_pravni_forma_code(subject)
    return {
        "name": _str_or_none(pick_first(subject, "obchodniJmeno", "nazev", "jmeno")),
        "ico": _str_or_none(pick_first(subject, "ico", "IC", "ic")),
        "dic": _str_or_none(pick_first(subject, "dic", "DIC")),
        "datumVzniku": _str_or_none(pick_first(subject, "datumVzniku", "datumVznikuSubjektu", "vznik")),
        "address": normalize_address(subject),
        "codes": {"pravniForma": _str_or_none(code)},
        "decoded": {"pravniForma": pravni_forma_map.get(code) if code is not None else None},
    }


def parse_total(response: dict[str, Any], fallback_count: int) -> int:
    for key in ("pocetCelkem", "total", "celkem", "count"):
        value = safe_int(response.get(key))
        if value is not None:
            return value
    return fallback_count


def parse_search_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("ekonomickeSubjekty", "subjekty", "items", "vysledky"):
        value = response.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def extract_codelist_pairs(node: Any, out: dict[int, str]) -> None:
    if isinstance(node, dict):
        code = safe_int(pick_first(node, "kod", "code", "id", "kodPolozkyCiselniku", "hodnota"))
        name = pick_first(node, "nazev", "name", "text", "nazevPolozky", "hodnotaPopis")
        if code is not None and name not in (None, ""):
            out[code] = str(name)
        for value in node.values():
            extract_codelist_pairs(value, out)
        return
    if isinstance(node, list):
        for item in node:
            extract_codelist_pairs(item, out)


def _load_cache_payload() -> tuple[dict[str, Any] | None, dict[int, str] | None]:
    path = cache_file()
    if not path.exists():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None

    fetched_at = safe_int(data.get("fetched_at"))
    items = data.get("items")
    if fetched_at is None or not isinstance(items, dict):
        return None, None

    mapping: dict[int, str] = {}
    for key, value in items.items():
        k = safe_int(key)
        if k is not None and isinstance(value, str):
            mapping[k] = value
    if not mapping:
        return None, None

    age = int(time.time()) - fetched_at
    if age <= CACHE_TTL_SECONDS:
        return mapping, mapping
    return None, mapping


def _memory_cache_is_fresh() -> bool:
    if _PRAVNI_FORMA_MEMORY_CACHE is None or _PRAVNI_FORMA_MEMORY_TS is None:
        return False
    return int(time.time()) - _PRAVNI_FORMA_MEMORY_TS <= CACHE_TTL_SECONDS


def save_cached_pravni_forma(mapping: dict[int, str]) -> None:
    path = cache_file()
    payload = {
        "fetched_at": int(time.time()),
        "items": {str(k): v for k, v in sorted(mapping.items())},
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return


def fetch_pravni_forma_from_ares(base: str) -> dict[int, str]:
    url = f"{base.rstrip('/')}/ciselniky-nazevniky/vyhledat"
    payload = http_json("POST", url, payload={"kodCiselniku": "PravniForma"})
    mapping: dict[int, str] = {}
    extract_codelist_pairs(payload, mapping)
    if mapping:
        return mapping
    raise AresError("Failed to decode codelist PravniForma", status=200, details={"url": url})


def get_pravni_forma_map(base: str) -> dict[int, str]:
    global _PRAVNI_FORMA_MEMORY_CACHE
    global _PRAVNI_FORMA_MEMORY_TS

    if _memory_cache_is_fresh():
        merged = dict(_PRAVNI_FORMA_MEMORY_CACHE or {})
        merged.update(CURATED_PRAVNI_FORMA_OVERRIDES)
        return merged

    fresh_cache, stale_cache = _load_cache_payload()
    if fresh_cache:
        _PRAVNI_FORMA_MEMORY_CACHE = dict(fresh_cache)
        _PRAVNI_FORMA_MEMORY_TS = int(time.time())
        merged = dict(fresh_cache)
        merged.update(CURATED_PRAVNI_FORMA_OVERRIDES)
        return merged

    try:
        fetched = fetch_pravni_forma_from_ares(base)
        _PRAVNI_FORMA_MEMORY_CACHE = dict(fetched)
        _PRAVNI_FORMA_MEMORY_TS = int(time.time())
        save_cached_pravni_forma(fetched)
        merged = dict(fetched)
        merged.update(CURATED_PRAVNI_FORMA_OVERRIDES)
        return merged
    except (AresError, NetworkError):
        if _PRAVNI_FORMA_MEMORY_CACHE:
            merged = dict(_PRAVNI_FORMA_MEMORY_CACHE)
        elif stale_cache:
            merged = dict(stale_cache)
        else:
            merged = {}
        merged.update(CURATED_PRAVNI_FORMA_OVERRIDES)
        return merged


def validate_ico(value: str) -> str:
    ico = value.strip()
    if not re.fullmatch(r"\d{8}", ico):
        raise ValidationError("ico must be exactly 8 digits")
    digits = [int(ch) for ch in ico]
    weighted = sum(digits[idx] * (8 - idx) for idx in range(7))
    mod = weighted % 11
    check = 11 - mod
    if check == 10:
        check = 0
    elif check == 11:
        check = 1
    if digits[7] != check:
        raise ValidationError("ico checksum failed (mod11)")
    return ico


def validate_name(value: str) -> str:
    name = value.strip()
    if len(name) < 3:
        raise ValidationError("search --name must have length >= 3")
    return name


def validate_limit(value: int) -> int:
    if value < 1:
        raise ValidationError("limit must be >= 1")
    return min(value, MAX_LIMIT)


def validate_offset(value: int) -> int:
    if value < 0:
        raise ValidationError("offset must be >= 0")
    return value


def validate_pick(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 1:
        raise ValidationError("pick must be >= 1")
    return value


def fetch_ico(base: str, ico: str) -> dict[str, Any]:
    return http_json("GET", f"{base.rstrip('/')}/ekonomicke-subjekty/{ico}")


def validate_nace(values: list[str]) -> list[str]:
    """Validate CZ-NACE codes: exactly 5 digits (e.g. '47710', '46420')."""
    validated = []
    for v in values:
        code = v.strip()
        if not re.fullmatch(r"\d{5}", code):
            raise ValidationError(f"NACE code must be exactly 5 digits (CZ-NACE format), got: {code!r}")
        validated.append(code)
    return validated


def fetch_search(
    base: str,
    name: str | None,
    city: str | None,
    nace: list[str] | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "pocet": limit,
        "start": offset,
        "razeni": [DEFAULT_SORT],
    }
    if name:
        body["obchodniJmeno"] = name
    if city:
        body["sidlo"] = {"nazevObce": city}
    if nace:
        body["czNace"] = nace
    if not name and not nace:
        raise ValidationError("search requires at least --name or --nace")
    return http_json("POST", f"{base.rstrip('/')}/ekonomicke-subjekty/vyhledat", payload=body)


def subject_card(item: dict[str, Any]) -> str:
    address = item.get("address") if isinstance(item.get("address"), dict) else {}
    legal = item.get("decoded", {}).get("pravniForma") if isinstance(item.get("decoded"), dict) else None
    return (
        f"{item.get('name') or '-'} | IČO {item.get('ico') or '-'} | DIČ {item.get('dic') or '-'} | "
        f"{address.get('city') or '-'} | právní forma {legal or '-'}"
    )


def print_human_ico(item: dict[str, Any]) -> None:
    print(subject_card(item))


def print_human_search(result: dict[str, Any]) -> None:
    query = result.get("query", {})
    city = query.get("city") if isinstance(query, dict) else None
    nace = query.get("nace") if isinstance(query, dict) else None
    parts = [
        f"name={query.get('name')!r}",
        f"city={city!r}",
    ]
    if nace:
        parts.append(f"nace={nace!r}")
    parts.append(f"limit={query.get('limit')}")
    parts.append(f"offset={query.get('offset')}")
    print(f"Query {', '.join(parts)} | total={result.get('total')}")

    items = result.get("items")
    if not isinstance(items, list) or not items:
        print("No items found.")
        return

    for idx, item in enumerate(items, start=1):
        if isinstance(item, dict):
            print(f"{idx}. {subject_card(item)}")

    picked = result.get("picked")
    if isinstance(picked, dict):
        subject = picked.get("subject")
        if isinstance(subject, dict):
            print(f"Picked: {subject_card(subject)}")


def json_error(
    message: str,
    code: str,
    *,
    status: int | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    return json.dumps(
        {
            "error": {
                "code": code,
                "message": message,
                "status": status,
                "details": details or {},
            }
        },
        ensure_ascii=False,
    )


def cmd_ico(args: argparse.Namespace) -> int:
    ico = validate_ico(args.ico)
    pravni_map = get_pravni_forma_map(args.base)
    payload = fetch_ico(args.base, ico)
    normalized_subject = normalize_subject(payload, pravni_map)
    normalized = {"subject": normalized_subject}

    if args.raw:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.json_mode:
        print(json.dumps(normalized, ensure_ascii=False, indent=2))
    else:
        print_human_ico(normalized_subject)
    return EXIT_OK


def cmd_search(args: argparse.Namespace) -> int:
    name: str | None = None
    if args.name:
        name = validate_name(args.name)
    nace: list[str] | None = None
    if args.nace:
        nace = validate_nace(args.nace)
    city = args.city.strip() if args.city else None
    limit = validate_limit(args.limit)
    offset = validate_offset(args.offset)
    pick = validate_pick(args.pick)

    pravni_map = get_pravni_forma_map(args.base)
    payload = fetch_search(args.base, name, city, nace, limit, offset)

    raw_items = parse_search_items(payload)
    items = [normalize_subject(item, pravni_map) for item in raw_items]
    result: dict[str, Any] = {
        "query": {"name": name, "city": city, "nace": nace, "limit": limit, "offset": offset},
        "total": parse_total(payload, len(items)),
        "items": items,
    }

    if pick is not None:
        if pick > len(items):
            raise ValidationError(f"pick {pick} is out of range for {len(items)} item(s)")
        picked_item = items[pick - 1]
        result["picked"] = {"index": pick - 1, "ico": picked_item.get("ico"), "subject": picked_item}

    if args.raw:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.json_mode:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human_search(result)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ares_client.py", description="ARES business registry client")
    parser.add_argument("--base", default=DEFAULT_BASE, help=f"ARES base URL (default: {DEFAULT_BASE})")

    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    mode = common.add_mutually_exclusive_group()
    mode.add_argument("--json", action="store_true", dest="json_mode", help="Output normalized JSON")
    mode.add_argument("--raw", action="store_true", help="Output raw ARES payload")

    p_ico = sub.add_parser("ico", parents=[common], help="Lookup by ICO")
    p_ico.add_argument("ico")
    p_ico.set_defaults(func=cmd_ico)

    p_search = sub.add_parser("search", parents=[common], help="Search by name and/or NACE code")
    p_search.add_argument("--name")
    p_search.add_argument("--nace", nargs="+", metavar="CODE", help="CZ-NACE code(s) to filter by (e.g. 4771 4719)")
    p_search.add_argument("--city")
    p_search.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p_search.add_argument("--offset", type=int, default=0)
    p_search.add_argument("--pick", type=int)
    p_search.set_defaults(func=cmd_search)

    # Friendly alias: `ares name "Foo"` instead of `ares search --name "Foo"`
    p_name = sub.add_parser("name", parents=[common], help="Search by name")
    p_name.add_argument("name")
    p_name.add_argument("--nace", nargs="+", metavar="CODE", help="CZ-NACE code(s) to filter by (e.g. 4771 4719)")
    p_name.add_argument("--city")
    p_name.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p_name.add_argument("--offset", type=int, default=0)
    p_name.add_argument("--pick", type=int)
    p_name.set_defaults(func=cmd_search)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except ValidationError as err:
        if getattr(args, "json_mode", False):
            print(json_error(str(err), "validation_error"))
        else:
            eprint(f"VALIDATION: {err}")
        return EXIT_VALIDATION
    except AresError as err:
        if getattr(args, "json_mode", False):
            print(json_error(str(err), "ares_error", status=err.status, details=err.details))
        else:
            status = f" (HTTP {err.status})" if err.status is not None else ""
            eprint(f"ARES_ERROR{status}: {err}")
        return EXIT_ARES_NON_OK
    except NetworkError as err:
        if getattr(args, "json_mode", False):
            print(json_error(str(err), "network_error", details=err.details))
        else:
            eprint(f"NETWORK: {err}")
        return EXIT_NETWORK


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
