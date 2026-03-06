import os
import json
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, Optional

from core.util.secrets import get_secret, set_secret
from core.util.local_secrets import get_local_secret, set_local_secret

# WHOOP Developer API base URLs
WHOOP_API_V2 = "https://api.prod.whoop.com/developer/v2"
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"


def _http_get_json(url: str, headers: Dict[str, str], timeout: int = 10) -> Dict[str, Any]:
    # Some edge/WAF setups will block requests without a User-Agent.
    base_headers = {
        "Accept": "application/json",
        "User-Agent": "openclaw-health-skills/0.1 (+https://github.com/openclaw/openclaw-health-skills)",
    }
    req = urllib.request.Request(url, headers={**base_headers, **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - network disabled in tests
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _http_post_form_json(url: str, form: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
    headers = headers or {}
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "User-Agent": "openclaw-health-skills/0.1 (+https://github.com/openclaw/openclaw-health-skills)",
            "Content-Type": "application/x-www-form-urlencoded",
            **headers,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - network disabled in tests
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _http_error_details(he: Exception, max_chars: int = 400) -> Dict[str, Any]:
    details: Dict[str, Any] = {}
    code = getattr(he, "code", None)
    if isinstance(code, int):
        details["status"] = code
    try:
        body = getattr(he, "read", None)
        if callable(body):
            raw = body()
            if isinstance(raw, (bytes, bytearray)):
                txt = raw.decode("utf-8", errors="replace")
                details["body_snippet"] = txt[:max_chars]
    except Exception:
        pass
    return details


def _s(v: Optional[str]) -> Optional[str]:
    return v.strip() if isinstance(v, str) else None


def _get_whoop_tokens() -> Dict[str, Optional[str]]:
    # WHOOP access token: use `token` only.
    access = _s(get_secret("OpenClaw Whoop", "token") or os.getenv("WHOOP_ACCESS_TOKEN"))

    refresh = _s(
        # Prefer local persisted refresh token (for automatic rotation without 1Password write access).
        get_local_secret("whoop", "refresh_token")
        or get_secret("OpenClaw Whoop", "refresh_token")
        # Back-compat: an early 1Password item used this label.
        or get_secret("OpenClaw Whoop", "refresh_password")
        or os.getenv("WHOOP_REFRESH_TOKEN")
    )

    return {
        "access_token": access,
        "refresh_token": refresh,
        "client_id": _s(get_secret("OpenClaw Whoop", "client_id") or os.getenv("WHOOP_CLIENT_ID")),
        "client_secret": _s(get_secret("OpenClaw Whoop", "client_secret") or os.getenv("WHOOP_CLIENT_SECRET")),
        "redirect_uri": _s(os.getenv("WHOOP_REDIRECT_URI") or os.getenv("WHOOP_REDIRECT_URL") or "http://127.0.0.1:8787/callback"),
    }


def _whoop_refresh_access_token(refresh_token: str, client_id: str, client_secret: str, redirect_uri: Optional[str]) -> Dict[str, Any]:
    # Refresh token flow.
    # Note: WHOOP can be picky about parameters. In practice, sending redirect_uri on refresh
    # may cause "invalid_request" if it doesn't exactly match what WHOOP expects.
    # So we omit redirect_uri here and keep the payload minimal.
    try:
        form = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        resp = _http_post_form_json(WHOOP_TOKEN_URL, form)
        return {
            "ok": True,
            "access_token": resp.get("access_token"),
            "refresh_token": resp.get("refresh_token"),
            "expires_in": resp.get("expires_in"),
        }
    except urllib.error.HTTPError as he:  # type: ignore[attr-defined]
        return {"ok": False, "error": "refresh_http_error", **_http_error_details(he)}
    except Exception as e:
        return {"ok": False, "error": f"refresh_failed: {type(e).__name__}"}


def _iso_window_for_date(date_str: str) -> Dict[str, str]:
    # WHOOP collection endpoints expect RFC3339 date-time strings.
    return {
        "start": f"{date_str}T00:00:00.000Z",
        "end": f"{date_str}T23:59:59.999Z",
    }


def fetch(date_str: str, live: bool = False, debug_raw: bool = False) -> Dict[str, Any]:
    toks = _get_whoop_tokens()
    access_token = toks.get("access_token")

    payload: Dict[str, Any] = {
        "source": "whoop",
        "date": date_str,
        "has_token": bool(access_token),
        "sleep": {"total_seconds": None, "score": None},
        "readiness": {"score": None},
        "activity": {"steps": None, "calories": None, "minutes": None},
        "resting_hr": None,
        "hrv_rmssd": None,
        "respiratory_rate": None,
        "spo2": None,
    }

    if not access_token:
        # No access token — try to refresh if we have refresh creds.
        rt, cid, cs = toks.get("refresh_token"), toks.get("client_id"), toks.get("client_secret")
        if rt and cid and cs:
            ref = _whoop_refresh_access_token(rt, cid, cs, toks.get("redirect_uri"))
            if ref.get("ok"):
                access_token = ref["access_token"]
                payload["has_token"] = True
                # Persist rotated tokens
                try:
                    from core.util.local_secrets import set_local_secret
                    set_local_secret("whoop", "access_token", access_token)
                    if ref.get("refresh_token"):
                        set_local_secret("whoop", "refresh_token", ref["refresh_token"])
                except Exception:
                    pass
            else:
                payload["has_token"] = False
                payload["error"] = {
                    "message": "refresh_failed",
                    "detail": ref,
                }
                return payload
        else:
            payload["has_token"] = False
            payload["error"] = {
                "message": "missing_token",
                "hint": "Set WHOOP_ACCESS_TOKEN (and optionally refresh creds) or configure 1Password item 'OpenClaw Whoop'.",
            }
            return payload

    if os.getenv("OPENCLAW_FORCE_SAMPLE") == "1":
        return payload

    def _attempt(tok: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {tok}"}

        win = _iso_window_for_date(date_str)
        qs = urllib.parse.urlencode({"start": win["start"], "end": win["end"], "limit": "1"})

        # Cycle (v2)
        cyc = _http_get_json(f"{WHOOP_API_V2}/cycle?{qs}", headers)
        if debug_raw:
            payload.setdefault("debug_raw", {})["cycle_v2"] = cyc
        recs = cyc.get("records") or cyc.get("data") or []
        c0 = recs[0] if recs else {}

        # Activity calories: best-effort from cycle score kilojoules
        try:
            cscore = c0.get("score") or {}
            kj = cscore.get("kilojoule")
            if isinstance(kj, (int, float)):
                payload["activity"]["calories"] = int(float(kj) * 0.239005736)
        except Exception:
            pass

        # Recovery collection (v2)
        rec2 = _http_get_json(f"{WHOOP_API_V2}/recovery?{qs}", headers)
        if debug_raw:
            payload.setdefault("debug_raw", {})["recovery_v2"] = rec2
        items = rec2.get("records") or rec2.get("data") or []
        rec = items[0] if items else None
        if isinstance(rec, dict):
            score_obj = rec.get("score") or rec
            if isinstance(score_obj, dict):
                score = score_obj.get("recovery_score")
                if isinstance(score, (int, float)):
                    payload["readiness"]["score"] = int(score)
                rhr = score_obj.get("resting_heart_rate")
                if isinstance(rhr, (int, float)):
                    payload["resting_hr"] = int(rhr)
                hrv = score_obj.get("hrv_rmssd_milli")
                if isinstance(hrv, (int, float)):
                    payload["hrv_rmssd"] = float(hrv)
                spo2 = score_obj.get("spo2_percentage")
                if isinstance(spo2, (int, float)):
                    payload["spo2"] = float(spo2)

        # Sleep collection (v2)
        sl2 = _http_get_json(f"{WHOOP_API_V2}/activity/sleep?{qs}", headers)
        if debug_raw:
            payload.setdefault("debug_raw", {})["sleep_v2"] = sl2
        items = sl2.get("records") or sl2.get("data") or []
        sl = items[0] if items else None
        if isinstance(sl, dict):
            sc = sl.get("score") or sl.get("scores") or {}
            if isinstance(sc, dict):
                perf = sc.get("sleep_performance_percentage")
                if isinstance(perf, (int, float)):
                    payload["sleep"]["score"] = int(perf)
                resp = sc.get("respiratory_rate")
                if isinstance(resp, (int, float)):
                    payload["respiratory_rate"] = float(resp)
                stage = sc.get("stage_summary") or {}
                if isinstance(stage, dict):
                    tib = stage.get("total_in_bed_time_milli")
                    if isinstance(tib, (int, float)):
                        payload["sleep"]["total_seconds"] = int(tib / 1000)

        return payload

    try:
        return _attempt(access_token)
    except urllib.error.HTTPError as he:  # type: ignore[attr-defined]
        details = _http_error_details(he)
        if details.get("status") == 401:
            rt, cid, cs = toks.get("refresh_token"), toks.get("client_id"), toks.get("client_secret")
            if rt and cid and cs:
                ref = _whoop_refresh_access_token(rt, cid, cs, toks.get("redirect_uri"))
                if ref.get("ok") and ref.get("access_token"):
                    try:
                        res2 = _attempt(ref.get("access_token"))
                    except urllib.error.HTTPError as he2:  # type: ignore[attr-defined]
                        payload["error"] = {"message": "fetch_failed_after_refresh", "detail": {"error": "http_error", **_http_error_details(he2)}}
                        return payload
                    except Exception as e:
                        payload["error"] = {"message": "fetch_failed_after_refresh", "detail": f"{type(e).__name__}"}
                        return payload

                    new_rt = ref.get("refresh_token")
                    if new_rt and new_rt != rt:
                        # Persist rotated refresh token.
                        # 1) Always write to local secrets file (preferred for no-human-intervention).
                        local_ok = False
                        try:
                            local_ok = set_local_secret("whoop", "refresh_token", str(new_rt))
                        except Exception:
                            local_ok = False

                        # 2) Best-effort 1Password writeback (opt-in).
                        wrote_1p = False
                        try:
                            wrote_1p = set_secret("OpenClaw Whoop", "refresh_token", str(new_rt))
                        except Exception:
                            wrote_1p = False

                        if local_ok:
                            payload["note"] = "WHOOP refresh_token rotated. Saved locally."
                        else:
                            payload["note"] = "WHOOP refresh_token rotated. Local save failed; update your stored token."
                        if wrote_1p:
                            payload["note"] += " (Also updated 1Password.)"
                    return res2

                payload["error"] = {"message": "refresh_failed", "detail": {k: ref.get(k) for k in ["status", "body_snippet", "error"]}}
                return payload

            payload["error"] = {"message": "unauthorized", "detail": "WHOOP access token expired. Please re-auth.", **details}
            return payload

        payload["error"] = {"message": "http_error", **details}
        return payload
    except Exception as e:
        return {**payload, "error": {"message": f"fetch_failed: {type(e).__name__}"}}


def cli(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Whoop connector")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--live", action="store_true", help="DEPRECATED: live is default when credentials are present")
    parser.add_argument("--debug-raw", action="store_true", help="Include raw WHOOP API responses (for mapping/debugging)")
    args = parser.parse_args(argv)

    datetime.strptime(args.date, "%Y-%m-%d")

    payload = fetch(args.date, live=args.live, debug_raw=args.debug_raw)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    cli()
