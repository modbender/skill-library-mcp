#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from urllib.parse import quote, urlparse

DEFAULT_BASE_URL = os.environ.get("CLIPROXY_BASE_URL", "")
DEFAULT_MGMT_KEY = os.environ.get("CLIPROXY_MANAGEMENT_KEY", "")
DEFAULT_AUTH_FILES_ENDPOINT = os.environ.get("CLIPROXY_AUTH_FILES_ENDPOINT", "/v0/management/auth-files")
DEFAULT_API_CALL_ENDPOINT = os.environ.get("CLIPROXY_API_CALL_ENDPOINT", "/v0/management/api-call")
DEFAULT_AUTH_DELETE_ENDPOINT = os.environ.get("CLIPROXY_AUTH_DELETE_ENDPOINT", "/v0/management/auth-files")
DEFAULT_PROBE_URL = os.environ.get("CODEX_PROBE_URL", "https://chatgpt.com/backend-api/codex/responses")
DEFAULT_ALLOWED_PROBE_HOSTS = os.environ.get("CLIPROXY_ALLOWED_PROBE_HOSTS", "chatgpt.com")
DEFAULT_WORKERS = int(os.environ.get("SCAN_WORKERS", "80"))


@dataclass
class AuthEntry:
    name: str
    provider: str
    auth_index: str
    status_message: str
    unavailable: bool


@dataclass
class CheckResult:
    name: str
    auth_index: str
    status_code: int | None
    unauthorized_401: bool
    weekly_quota_zero: bool
    error: str
    response_preview: str


def _json_request(url: str, method: str, headers: dict[str, str], body_obj: dict | None, timeout: int, insecure: bool) -> tuple[int, dict | str]:
    data = None
    if body_obj is not None:
        data = json.dumps(body_obj, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, headers=headers, data=data, method=method.upper())
    ctx = ssl._create_unverified_context() if insecure else ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            code = r.getcode()
            text = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        code = e.code
        text = e.read().decode("utf-8", "replace")
    if not text:
        return code, ""
    try:
        return code, json.loads(text)
    except Exception:
        return code, text


def _is_weekly_quota_zero(status_code: int | None, text: str) -> bool:
    t = (text or "").lower()
    markers = ["weekly", "week", "per week", "weekly quota", "weekly limit", "week limit", "本周", "周限额", "周额度"]
    qwords = ["quota", "limit", "exceeded", "reached", "用尽", "耗尽", "超出"]
    if status_code == 429 and any(m in t for m in markers) and any(q in t for q in qwords):
        return True
    return any(m in t for m in markers) and any(q in t for q in qwords)


def _probe_payload() -> dict:
    return {
        "model": "gpt-5",
        "instructions": "ping",
        "store": False,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": "ping"}]}],
        "max_output_tokens": 1,
    }


def _list_codex_auths(base_url: str, key: str, endpoint: str, insecure: bool) -> list[AuthEntry]:
    url = base_url.rstrip("/") + endpoint
    code, resp = _json_request(
        url,
        "GET",
        {"Authorization": f"Bearer {key}", "Accept": "application/json"},
        None,
        timeout=30,
        insecure=insecure,
    )
    if code >= 400:
        raise RuntimeError(f"list auth-files failed: {code} {resp}")
    files = resp.get("files") if isinstance(resp, dict) else []
    out: list[AuthEntry] = []
    for f in files or []:
        if not isinstance(f, dict):
            continue
        name = str(f.get("name") or "").strip()
        provider = str(f.get("provider") or f.get("type") or "").strip().lower()
        auth_index = str(f.get("auth_index") or "").strip()
        if not name or not auth_index:
            continue
        if provider == "codex" or "codex" in name.lower():
            out.append(
                AuthEntry(
                    name=name,
                    provider=provider or "codex",
                    auth_index=auth_index,
                    status_message=str(f.get("status_message") or ""),
                    unavailable=bool(f.get("unavailable") or False),
                )
            )
    return out


def _probe_via_management_api_call(base_url: str, key: str, api_call_endpoint: str, probe_url: str, auth: AuthEntry, insecure: bool) -> CheckResult:
    url = base_url.rstrip("/") + api_call_endpoint
    token_magic = "$" + "TOKEN$"
    body = {
        "auth_index": auth.auth_index,
        "method": "POST",
        "url": probe_url,
        "header": {
            "Authorization": "Bearer " + token_magic,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "codex_cli_rs/0.98.0 (cliproxy-api-call-sweep)",
        },
        "data": json.dumps(_probe_payload(), ensure_ascii=False),
    }
    try:
        code, resp = _json_request(
            url,
            "POST",
            {"Authorization": f"Bearer {key}", "Accept": "application/json", "Content-Type": "application/json"},
            body,
            timeout=60,
            insecure=insecure,
        )
    except Exception as e:  # noqa: BLE001
        return CheckResult(auth.name, auth.auth_index, None, False, False, f"api_call error: {e}", "")

    if code >= 400:
        return CheckResult(auth.name, auth.auth_index, None, False, False, f"management api_call failed: {code}", str(resp)[:220])

    if not isinstance(resp, dict):
        return CheckResult(auth.name, auth.auth_index, None, False, False, "invalid api_call response", str(resp)[:220])

    status_code = resp.get("status_code")
    body_text = resp.get("body") if isinstance(resp.get("body"), str) else json.dumps(resp.get("body"), ensure_ascii=False)
    low = (body_text or "").lower()

    unauthorized = (status_code == 401) or ("invalid auth" in low) or ("revoked" in low)
    weekly_zero = _is_weekly_quota_zero(status_code, body_text or "")
    return CheckResult(auth.name, auth.auth_index, status_code, unauthorized, weekly_zero, "", (body_text or "")[:220])


def _delete_auth_file(base_url: str, key: str, endpoint: str, name: str, insecure: bool) -> bool:
    url = f"{base_url.rstrip('/')}{endpoint}?name={quote(name, safe='')}"
    code, _ = _json_request(
        url,
        "DELETE",
        {"Authorization": f"Bearer {key}", "Accept": "application/json"},
        None,
        timeout=30,
        insecure=insecure,
    )
    return code < 400


def _normalize_hosts_csv(raw: str) -> set[str]:
    return {h.strip().lower() for h in (raw or "").split(",") if h.strip()}


def _assert_probe_url_safe(probe_url: str, allowed_hosts_csv: str, unsafe_allow: bool) -> None:
    parsed = urlparse(probe_url)
    if parsed.scheme != "https":
        raise SystemExit("Security check failed: --probe-url must use https")
    host = (parsed.hostname or "").lower()
    allowed = _normalize_hosts_csv(allowed_hosts_csv)
    if not host:
        raise SystemExit("Security check failed: --probe-url host is empty")
    if host not in allowed:
        if unsafe_allow:
            return
        raise SystemExit(
            f"Security check failed: probe host '{host}' not in allowlist {sorted(allowed)}. "
            "Use --allow-unsafe-probe-host only if you fully trust this host."
        )


def main() -> int:
    p = argparse.ArgumentParser(description="Scan Codex auth via CLI Proxy management api-call (supports runtime refresh/quota view)")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--management-key", default=DEFAULT_MGMT_KEY)
    p.add_argument("--auth-files-endpoint", default=DEFAULT_AUTH_FILES_ENDPOINT)
    p.add_argument("--api-call-endpoint", default=DEFAULT_API_CALL_ENDPOINT)
    p.add_argument("--auth-delete-endpoint", default=DEFAULT_AUTH_DELETE_ENDPOINT)
    p.add_argument("--probe-url", default=DEFAULT_PROBE_URL)
    p.add_argument("--allowed-probe-hosts", default=DEFAULT_ALLOWED_PROBE_HOSTS, help="Comma-separated allowlist for probe host, default: chatgpt.com")
    p.add_argument("--allow-unsafe-probe-host", action="store_true", help="Allow probe host outside allowlist (DANGEROUS)")
    p.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    p.add_argument("--delete-401", action="store_true")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification (DANGEROUS)")
    p.add_argument("--allow-insecure-tls", action="store_true", help="Second confirmation for --insecure")
    p.add_argument("--output-json", action="store_true")
    args = p.parse_args()

    if not args.base_url or not args.management_key:
        raise SystemExit("Missing required params: --base-url and --management-key")
    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    if args.insecure and not args.allow_insecure_tls:
        raise SystemExit("Security check failed: --insecure requires explicit --allow-insecure-tls")
    _assert_probe_url_safe(args.probe_url, args.allowed_probe_hosts, args.allow_unsafe_probe_host)

    auths = _list_codex_auths(args.base_url, args.management_key, args.auth_files_endpoint, args.insecure)

    results: list[CheckResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(_probe_via_management_api_call, args.base_url, args.management_key, args.api_call_endpoint, args.probe_url, a, args.insecure) for a in auths]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())

    to_delete = [r.name for r in results if r.unauthorized_401]
    deleted = 0
    if args.delete_401 and args.yes and to_delete:
        for name in to_delete:
            if _delete_auth_file(args.base_url, args.management_key, args.auth_delete_endpoint, name, args.insecure):
                deleted += 1

    management_quota_exhausted = sum(
        1
        for a in auths
        if a.unavailable and (("quota" in a.status_message.lower()) or ("限额" in a.status_message) or ("额度" in a.status_message))
    )

    status_buckets: dict[str, int] = {}
    for r in results:
        k = str(r.status_code) if r.status_code is not None else "none"
        status_buckets[k] = status_buckets.get(k, 0) + 1

    payload = {
        "summary": {
            "total": len(results),
            "unauthorized_401": sum(1 for r in results if r.unauthorized_401),
            "weekly_quota_zero": sum(1 for r in results if r.weekly_quota_zero),
            "ok": sum(1 for r in results if r.status_code is not None and 200 <= r.status_code < 300),
            "errors": sum(1 for r in results if r.error),
            "management_quota_exhausted": management_quota_exhausted,
            "status_code_buckets": status_buckets,
        },
        "deletion": {
            "requested": bool(args.delete_401),
            "target_count": len(to_delete),
            "confirmed": bool(args.delete_401 and args.yes),
            "deleted_count": deleted,
        },
        "results": [asdict(r) for r in results],
    }

    if args.output_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        s = payload["summary"]
        print(f"total={s['total']} invalid={s['unauthorized_401']} weekly_zero={s['weekly_quota_zero']} ok={s['ok']} errors={s['errors']} mgmt_quota_exhausted={s['management_quota_exhausted']}")
        print(f"status_code_buckets={json.dumps(s['status_code_buckets'], ensure_ascii=False)}")

    return 1 if payload["summary"]["unauthorized_401"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
