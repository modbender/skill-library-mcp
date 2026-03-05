#!/usr/bin/env python3
"""Minimal Cloudflare DNS helper for this skill.

Auth:
  - Uses CLOUDFLARE_API_TOKEN env var (recommended).

Permissions (least privilege):
  - Zone:Zone:Read
  - Zone:DNS:Edit

Usage examples:
  ./cf_dns.py zone-id example.com
  ./cf_dns.py dns list --zone example.com --name openclaw.example.com
  ./cf_dns.py dns delete --zone example.com --record-id <id>
  ./cf_dns.py dns upsert --zone example.com --type CNAME --name openclaw --content <uuid>.cfargotunnel.com --proxied true
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"


def _token() -> str:
    t = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not t:
        raise SystemExit("Missing CLOUDFLARE_API_TOKEN env var")
    return t


def _req(method: str, path: str, *, params: dict | None = None, body: dict | None = None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

    data = None
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise SystemExit(f"Cloudflare API request failed: {e}")

    if not payload.get("success"):
        errs = payload.get("errors") or payload
        raise SystemExit(f"Cloudflare API error: {json.dumps(errs, indent=2)}")
    return payload.get("result")


def zone_id(zone: str) -> str:
    # zone can be zone name or zone id
    if zone and len(zone) == 32 and all(c in "0123456789abcdef" for c in zone.lower()):
        return zone
    res = _req("GET", "/zones", params={"name": zone, "status": "active", "per_page": 50})
    if not res:
        raise SystemExit(f"Zone not found/active: {zone}")
    return res[0]["id"]


def dns_list(zone: str, *, name: str | None = None, rtype: str | None = None):
    zid = zone_id(zone)
    params = {"per_page": 100, "name": name, "type": rtype}
    return _req("GET", f"/zones/{zid}/dns_records", params=params)


def dns_upsert(zone: str, *, rtype: str, name: str, content: str, proxied: bool | None, ttl: int | None):
    zid = zone_id(zone)

    # Accept relative name (e.g. "openclaw") or FQDN.
    # Cloudflare API accepts both; we pass as-is.
    existing = dns_list(zone, name=name, rtype=rtype) or []

    body = {"type": rtype, "name": name, "content": content}
    if proxied is not None:
        body["proxied"] = proxied
    if ttl is not None:
        body["ttl"] = ttl

    if existing:
        rec_id = existing[0]["id"]
        return _req("PUT", f"/zones/{zid}/dns_records/{rec_id}", body=body)
    return _req("POST", f"/zones/{zid}/dns_records", body=body)


def dns_delete(zone: str, *, record_id: str):
    zid = zone_id(zone)
    _req("DELETE", f"/zones/{zid}/dns_records/{record_id}")
    return "OK"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    zid = sub.add_parser("zone-id")
    zid.add_argument("zone")

    dns = sub.add_parser("dns")
    dns_sub = dns.add_subparsers(dest="dns_cmd", required=True)

    lst = dns_sub.add_parser("list")
    lst.add_argument("--zone", required=True)
    lst.add_argument("--name")
    lst.add_argument("--type", dest="rtype")

    ups = dns_sub.add_parser("upsert")
    ups.add_argument("--zone", required=True)
    ups.add_argument("--type", dest="rtype", required=True)
    ups.add_argument("--name", required=True)
    ups.add_argument("--content", required=True)
    ups.add_argument("--proxied", choices=["true", "false"])
    ups.add_argument("--ttl", type=int)

    dele = dns_sub.add_parser("delete")
    dele.add_argument("--zone", required=True)
    dele.add_argument("--record-id", required=True)

    args = ap.parse_args(argv)

    if args.cmd == "zone-id":
        print(zone_id(args.zone))
        return 0

    if args.cmd == "dns" and args.dns_cmd == "list":
        print(json.dumps(dns_list(args.zone, name=args.name, rtype=args.rtype), indent=2))
        return 0

    if args.cmd == "dns" and args.dns_cmd == "upsert":
        proxied = None
        if args.proxied is not None:
            proxied = args.proxied == "true"
        print(json.dumps(dns_upsert(args.zone, rtype=args.rtype, name=args.name, content=args.content, proxied=proxied, ttl=args.ttl), indent=2))
        return 0

    if args.cmd == "dns" and args.dns_cmd == "delete":
        print(dns_delete(args.zone, record_id=args.record_id))
        return 0

    raise SystemExit("unreachable")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
