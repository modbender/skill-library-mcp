#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import requests
except ModuleNotFoundError:
    requests = None


OPENAPI_ENDPOINT = "https://api.aixvc.io/gw"
CHAT_PATH = "/openapi/v2/public/twa/agent/chat"
HOST = "api.aixvc.io"
CHAIN_ID = "base"
AWS_REGION = "aixvc"
AWS_SERVICE = "twa-manager"
TIMEOUT_SECONDS = 60
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def _json_compact(obj: object) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _uri_encode(raw: str, *, encode_slash: bool) -> str:
    out: list[str] = []
    for c in raw:
        if ("A" <= c <= "Z") or ("a" <= c <= "z") or ("0" <= c <= "9") or c in ("_", "-", "~", "."):
            out.append(c)
        elif c == "/" and not encode_slash:
            out.append(c)
        else:
            out.extend(f"%{b:02X}" for b in c.encode("utf-8"))
    return "".join(out)


def _derive_signing_key(secret_key: str, date_yyyymmdd: str, region: str, service: str) -> bytes:
    k_secret = f"AWS4{secret_key}".encode("utf-8")
    k_date = _hmac_sha256(k_secret, date_yyyymmdd)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, service)
    return _hmac_sha256(k_service, "aws4_request")


def _build_sigv4_headers(
    *,
    access_key: str,
    secret_key: str,
    url: str,
    body_bytes: bytes,
    chain_id: str,
    region: str,
    service: str,
) -> dict[str, str]:
    parsed = urlparse(url)
    amz_dt = datetime.now(timezone.utc)
    amz_date = amz_dt.strftime("%Y%m%dT%H%M%SZ")
    short_date = amz_dt.strftime("%Y%m%d")
    payload_hash = _sha256_hex(body_bytes) if body_bytes else EMPTY_SHA256
    canonical_uri = _uri_encode(parsed.path or "/", encode_slash=False)
    canonical_headers = f"host:{HOST}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-date"
    canonical_request = "\n".join(
        ["POST", canonical_uri, "", canonical_headers, signed_headers, payload_hash]
    )
    credential_scope = f"{short_date}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join(
        ["AWS4-HMAC-SHA256", amz_date, credential_scope, _sha256_hex(canonical_request.encode("utf-8"))]
    )
    signing_key = _derive_signing_key(secret_key, short_date, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization = (
        "AWS4-HMAC-SHA256 "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "chain-id": chain_id,
        "Content-Length": str(len(body_bytes)),
        "X-Amz-Date": amz_date,
        "X-Amz-Content-Sha256": payload_hash,
        "Authorization": authorization,
    }


def _http_post_json(*, url: str, body_json: str, headers: dict[str, str]) -> tuple[int, str]:
    if requests is None:
        raise RuntimeError('missing dependency: requests. Install with "python -m pip install requests".')
    try:
        resp = requests.post(url, data=body_json, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise RuntimeError(f"request failed: {exc}") from exc
    resp.encoding = resp.encoding or "utf-8"
    return int(resp.status_code), resp.text


def _extract_reply(data: object) -> str:
    if isinstance(data, dict):
        reply = data.get("reply")
        if isinstance(reply, str) and reply.strip():
            result = reply.strip()
        else:
            intent = data.get("intent")
            if isinstance(intent, dict):
                r2u = intent.get("reply_to_user")
                if isinstance(r2u, str) and r2u.strip():
                    result = r2u.strip()
                else:
                    result = _json_compact(data)
            else:
                result = _json_compact(data)
 
        pending_confirm = data.get("pendingConfirm")
        if isinstance(pending_confirm, dict):
            confirm_key = pending_confirm.get("confirmKey")
            if confirm_key:
                result += f"\n\n**confirmKey**: `{confirm_key}`"
                result += f"\n- Confirm: `yes, please execute {confirm_key}`"
                result += f"\n- Cancel: `no, please cancel {confirm_key}`"
        return result
    if isinstance(data, str):
        return data.strip()
    if data is None:
        return ""
    return _json_compact(data)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="axelrod_chat.py",
        description="Axelrod (AIxVC) OpenAPI chat client (AK/SK signed).",
    )
    parser.add_argument("--message", required=True, help="Natural language instruction to send")
    parser.add_argument("--json", action="store_true", help="Print full JSON response")
    args = parser.parse_args(argv)

    access_key = os.environ.get("AIXVC_ACCESS_KEY", "").strip()
    secret_key = os.environ.get("AIXVC_SECRET_KEY", "").strip()
    if not access_key or not secret_key:
        _eprint("error: missing AK/SK. Set AIXVC_ACCESS_KEY and AIXVC_SECRET_KEY.")
        return 2

    url = f"{OPENAPI_ENDPOINT}{CHAT_PATH}"
    req_body = _json_compact({"message": args.message})
    req_body_bytes = req_body.encode("utf-8")
    req_headers = _build_sigv4_headers(
        access_key=access_key,
        secret_key=secret_key,
        url=url,
        body_bytes=req_body_bytes,
        chain_id=CHAIN_ID,
        region=AWS_REGION,
        service=AWS_SERVICE,
    )

    started = time.time()
    try:
        status, resp_body = _http_post_json(url=url, body_json=req_body, headers=req_headers)
    except RuntimeError as exc:
        _eprint(f"error: {exc}")
        return 3
    elapsed_ms = int((time.time() - started) * 1000)

    try:
        obj = json.loads(resp_body)
    except json.JSONDecodeError:
        _eprint(f"http error: status={status} cost={elapsed_ms}ms")
        if resp_body:
            _eprint(resp_body)
        return 3

    if args.json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))

    if not isinstance(obj, dict):
        if not args.json:
            print(resp_body)
        return 0

    code = obj.get("code")
    if code not in (0, 200, "0", "200"):
        msg = obj.get("message") if isinstance(obj.get("message"), str) else "request failed"
        _eprint(f"api error: http={status} code={code} message={msg} cost={elapsed_ms}ms")
        if not args.json:
            _eprint(resp_body)
        return 4

    if not args.json:
        print(_extract_reply(obj.get("data")))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
