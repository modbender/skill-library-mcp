import os
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from core.util.secrets import get_secret


OURA_API = "https://api.ouraring.com"


def _http_get_json(url: str, headers: Dict[str, str], timeout: int = 10) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - network blocked in tests
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _http_post_form_json(url: str, form: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
    headers = headers or {}
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - network blocked in tests
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _http_error_details(he: Exception, max_chars: int = 400) -> Dict[str, Any]:
    # Best-effort to capture status + small response snippet (never includes auth headers).
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


def _get_oura_tokens() -> Dict[str, Optional[str]]:
    return {
        "access_token": (
            get_secret("OpenClaw Oura", "token")
            or get_secret("OpenClaw Oura", "credential")
            or os.getenv("OURA_PERSONAL_ACCESS_TOKEN")
        ),
        "refresh_token": get_secret("OpenClaw Oura", "refresh_token") or os.getenv("OURA_REFRESH_TOKEN"),
        "client_id": get_secret("OpenClaw Oura", "client_id") or os.getenv("OURA_CLIENT_ID"),
        "client_secret": get_secret("OpenClaw Oura", "client_secret") or os.getenv("OURA_CLIENT_SECRET"),
    }


def _oura_refresh_access_token(refresh_token: str, client_id: str, client_secret: str) -> Dict[str, Any]:
    """Refresh Oura access token.

    Per Oura docs, client_id/client_secret can be supplied either as body params OR via HTTP Basic Auth.
    We prefer Basic Auth because it is the most widely compatible OAuth2 pattern.
    """

    url = f"{OURA_API}/oauth/token"
    try:
        # Basic auth: base64(client_id:client_secret)
        import base64

        b = f"{client_id}:{client_secret}".encode("utf-8")
        basic = base64.b64encode(b).decode("ascii")
        headers = {"Authorization": f"Basic {basic}"}

        resp = _http_post_form_json(
            url,
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers=headers,
        )
        return {"ok": True, "access_token": resp.get("access_token"), "refresh_token": resp.get("refresh_token")}
    except urllib.error.HTTPError as he:  # type: ignore[attr-defined]
        return {"ok": False, "error": "refresh_http_error", **_http_error_details(he)}
    except Exception as e:
        return {"ok": False, "error": f"refresh_failed: {type(e).__name__}"}


def _parse_daily_sleep(obj: Dict[str, Any]) -> Dict[str, Any]:
    d = {
        "total_seconds": None,
        "score": None,
        "respiratory_rate": None,
        "resting_hr": None,
        "hrv_rmssd": None,
        "spo2": None,
    }
    if not obj:
        return d
    # Seconds
    for k in ["total_sleep_duration", "total_sleep_time", "duration"]:
        if isinstance(obj.get(k), (int, float)):
            d["total_seconds"] = int(obj[k])
            break
    # Score
    if isinstance(obj.get("score"), (int, float)):
        d["score"] = obj["score"]
    # Respiratory rate
    for k in ["average_breathing_rate", "avg_breathing_rate", "breath_average"]:
        v = obj.get(k)
        if isinstance(v, (int, float)):
            d["respiratory_rate"] = float(v)
            break
    # Resting HR
    for k in ["resting_heart_rate", "lowest_heart_rate", "average_heart_rate"]:
        v = obj.get(k)
        if isinstance(v, (int, float)):
            d["resting_hr"] = int(v)
            break
    # HRV RMSSD (ms)
    for k in ["average_rmssd", "rmssd", "hrv_rmssd_millis", "rmssd_millis", "average_hrv"]:
        v = obj.get(k)
        if isinstance(v, (int, float)):
            d["hrv_rmssd"] = float(v)
            break
    return d


def _safe_int(v: Any) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except Exception:
        return None


def fetch(date_str: str, live: bool = False) -> Dict[str, Any]:
    tokens = _get_oura_tokens()
    access_token = tokens.get("access_token")

    payload: Dict[str, Any] = {
        "source": "oura",
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
        # No credentials available. Do NOT fabricate sample values.
        payload["has_token"] = False
        payload["error"] = {
            "message": "missing_token",
            "hint": "Set OURA_PERSONAL_ACCESS_TOKEN (or configure 1Password item 'OpenClaw Oura').",
        }
        return payload

    if os.getenv("OPENCLAW_FORCE_SAMPLE") == "1":
        return payload

    try:
        _ = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        payload["error"] = {"message": "invalid_date", "detail": "Expected YYYY-MM-DD"}
        return payload

    def _attempt(access_tok: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_tok}"}
        try:
            base = f"{OURA_API}/v2/usercollection"
            q = urllib.parse.urlencode({"start_date": date_str, "end_date": date_str})

            js_sleep = _http_get_json(f"{base}/daily_sleep?{q}", headers)
            sleep_list = js_sleep.get("data") or []
            sleep_obj = sleep_list[0] if sleep_list else {}
            sleep_parsed = _parse_daily_sleep(sleep_obj)
            payload["sleep"] = {"total_seconds": sleep_parsed["total_seconds"], "score": sleep_parsed["score"]}
            if sleep_parsed.get("resting_hr") is not None:
                payload["resting_hr"] = _safe_int(sleep_parsed["resting_hr"])
            if sleep_parsed.get("hrv_rmssd") is not None:
                payload["hrv_rmssd"] = sleep_parsed["hrv_rmssd"]
            if sleep_parsed.get("respiratory_rate") is not None:
                payload["respiratory_rate"] = sleep_parsed["respiratory_rate"]

            js_ready = _http_get_json(f"{base}/daily_readiness?{q}", headers)
            r_list = js_ready.get("data") or []
            r_obj = r_list[0] if r_list else {}
            r_score = r_obj.get("score") if isinstance(r_obj.get("score"), (int, float)) else None
            payload["readiness"] = {"score": r_score}

            js_act = _http_get_json(f"{base}/daily_activity?{q}", headers)
            a_list = js_act.get("data") or []
            a_obj = a_list[0] if a_list else {}
            steps = _safe_int(a_obj.get("steps"))

            calories = None
            for k in ["calories", "total_calories", "calories_burned", "active_calories"]:
                v = a_obj.get(k)
                if isinstance(v, (int, float)):
                    calories = int(v)
                    break

            minutes = None
            for k in ["equivalent_min", "active_time", "moderate_activity_time", "high_activity_time"]:
                v = a_obj.get(k)
                if isinstance(v, (int, float)):
                    minutes = int(v / 60) if v and v > 1000 else int(v)
                    break

            payload["activity"] = {"steps": steps, "calories": calories, "minutes": minutes}
            return payload

        except urllib.error.HTTPError as he:  # type: ignore[attr-defined]
            details = _http_error_details(he)
            return {"http_error": details.get("status", 0), "message": "http_error", **details}
        except Exception as e:
            return {"error": f"fetch_failed: {type(e).__name__}"}

    res = _attempt(access_token)  # type: ignore[arg-type]

    if isinstance(res, dict) and res.get("http_error") == 401:
        rt, cid, cs = tokens.get("refresh_token"), tokens.get("client_id"), tokens.get("client_secret")
        if rt and cid and cs:
            ref = _oura_refresh_access_token(rt, cid, cs)
            if ref.get("ok") and ref.get("access_token"):
                new_access = ref.get("access_token")
                res2 = _attempt(new_access)  # type: ignore[arg-type]
                if isinstance(res2, dict) and "http_error" not in res2 and "error" not in res2:
                    new_rt = ref.get("refresh_token")
                    if new_rt and new_rt != rt:
                        payload["note"] = "Oura refresh_token rotated. Update your 1Password item."
                    return payload
                else:
                    payload["error"] = {
                        "message": "fetch_failed_after_refresh",
                        "detail": {k: res2.get(k) for k in ["http_error", "status", "body_snippet", "message", "error"] if isinstance(res2, dict)},
                    }
                    return payload
            else:
                payload["error"] = {"message": "refresh_failed", "detail": {k: ref.get(k) for k in ["status", "body_snippet", "error"]}}
                return payload
        else:
            payload["error"] = {"message": "unauthorized", "detail": "Token expired; missing refresh credentials."}
            return payload

    if isinstance(res, dict) and ("http_error" in res or "error" in res):
        payload["error"] = {"message": res.get("message", "fetch_failed"), "detail": {k: res.get(k) for k in ["http_error", "status", "body_snippet", "error"]}}
        return payload

    return payload


def cli(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Oura connector")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--live", action="store_true", help="DEPRECATED: live is default when credentials are present")
    args = parser.parse_args(argv)

    datetime.strptime(args.date, "%Y-%m-%d")
    payload = fetch(args.date, live=args.live)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    cli()
