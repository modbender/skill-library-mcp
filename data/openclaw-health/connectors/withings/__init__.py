import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from core.util.secrets import get_secret, set_secret
from core.util.local_secrets import get_local_secret, set_local_secret

WITHINGS_API = "https://wbsapi.withings.net"


def _http_get_json(url: str, headers: Dict[str, str], timeout: int = 10) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _http_post_form_json(url: str, form: Dict[str, str], headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Dict[str, Any]:
    headers = headers or {}
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def _read_withings_secrets() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    # Prefer 1Password
    cid = get_secret("OpenClaw Withings", "client_id")
    csec = get_secret("OpenClaw Withings", "client_secret")
    rtok = get_local_secret("withings", "refresh_token") or get_secret("OpenClaw Withings", "refresh_token")
    uid = get_secret("OpenClaw Withings", "user_id")
    # Fallback env
    cid = cid or os.getenv("WITHINGS_CLIENT_ID")
    csec = csec or os.getenv("WITHINGS_CLIENT_SECRET")
    rtok = rtok or os.getenv("WITHINGS_REFRESH_TOKEN")
    uid = uid or os.getenv("WITHINGS_USER_ID")
    return cid, csec, rtok, uid


def _withings_refresh_access_token(cid: str, csec: str, rtok: str) -> Dict[str, Any]:
    url = f"{WITHINGS_API}/v2/oauth2"
    try:
        resp = _http_post_form_json(
            url,
            {
                "action": "requesttoken",
                "grant_type": "refresh_token",
                "client_id": cid,
                "client_secret": csec,
                "refresh_token": rtok,
            },
        )
        # Withings returns {status: 0, body: {...}}
        if isinstance(resp, dict) and resp.get("status") == 0:
            body = resp.get("body", {})
            return {
                "ok": True,
                "access_token": body.get("access_token"),
                "refresh_token": body.get("refresh_token"),
                "expires_in": body.get("expires_in"),
            }
        return {"ok": False, "error": f"status_{resp.get('status')}"}
    except Exception as e:
        return {"ok": False, "error": f"refresh_failed: {type(e).__name__}"}


def _epoch_range_for_day(date_str: str) -> Tuple[int, int]:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    start = int(time.mktime(dt.timetuple()))
    end = int(time.mktime((dt + timedelta(days=1)).timetuple()))
    return start, end


def fetch(date_str: str, live: bool = False) -> Dict[str, Any]:
    cid, csec, rtok, uid = _read_withings_secrets()
    has_creds = bool(cid and csec and rtok)

    payload: Dict[str, Any] = {
        "source": "withings",
        "date": date_str,
        "has_token": has_creds,
        "sleep": {"total_seconds": None, "score": None},
        "readiness": {"score": None},
        "activity": {"steps": None, "calories": None, "minutes": None},
        "resting_hr": None,
        "hrv_rmssd": None,
        "respiratory_rate": None,
        "spo2": None,
        "weight_kg": None,
        "body_fat_percent": None,
    }

    # If we don't have refresh creds, do NOT fabricate sample values.
    if not has_creds:
        payload["has_token"] = False
        payload["error"] = {
            "message": "missing_creds",
            "hint": "Set WITHINGS_CLIENT_ID/WITHINGS_CLIENT_SECRET/WITHINGS_REFRESH_TOKEN (or configure 1Password item 'OpenClaw Withings').",
        }
        return payload

    if os.getenv("OPENCLAW_FORCE_SAMPLE") == "1":
        return payload

    # Refresh to get an access token (Withings typically requires it)
    ref = _withings_refresh_access_token(cid or "", csec or "", rtok or "")
    if not ref.get("ok") or not ref.get("access_token"):
        payload["error"] = {"message": "refresh_failed", "hint": "Ensure client_id, client_secret, refresh_token are valid."}
        return payload
    access_token = ref.get("access_token")
    rotated_note = None
    new_rtok = ref.get("refresh_token")
    if new_rtok and rtok and new_rtok != rtok:
        local_ok = False
        try:
            local_ok = set_local_secret("withings", "refresh_token", str(new_rtok))
        except Exception:
            local_ok = False

        wrote_1p = False
        try:
            wrote_1p = set_secret("OpenClaw Withings", "refresh_token", str(new_rtok))
        except Exception:
            wrote_1p = False

        rotated_note = "Withings refresh_token rotated. "
        rotated_note += "Saved locally." if local_ok else "Local save failed; update stored token."
        if wrote_1p:
            rotated_note += " (Also updated 1Password.)"

    headers = {"Authorization": f"Bearer {access_token}"}

    # Sleep summary
    try:
        q = urllib.parse.urlencode({"action": "getsummary", "startdateymd": date_str, "enddateymd": date_str})
        js = _http_get_json(f"{WITHINGS_API}/v2/sleep?{q}", headers)
        if js.get("status") == 0:
            series = js.get("body", {}).get("series", [])
            entry = series[0] if series else {}
            data = entry.get("data", {})
            # total sleep duration may be in seconds under different keys
            total = None
            for k in ["totalsleepduration", "duration", "total_timeinbed"]:
                v = data.get(k)
                if isinstance(v, (int, float)):
                    total = int(v)
                    break
            score = data.get("score") if isinstance(data.get("score"), (int, float)) else None
            payload["sleep"] = {"total_seconds": total, "score": score}
    except Exception:
        pass

    # Activity (daily)
    try:
        q = urllib.parse.urlencode({"action": "getactivity", "startdateymd": date_str, "enddateymd": date_str})
        js = _http_get_json(f"{WITHINGS_API}/v2/measure?{q}", headers)
        if js.get("status") == 0:
            acts = js.get("body", {}).get("activities", [])
            a = acts[0] if acts else {}
            steps = a.get("steps") if isinstance(a.get("steps"), (int, float)) else None
            cals = a.get("calories") if isinstance(a.get("calories"), (int, float)) else None
            minutes = None
            for k in ["active", "duration", "totalactive"]:
                v = a.get(k)
                if isinstance(v, (int, float)):
                    minutes = int(v / 60) if v and v > 1000 else int(v)
                    break
            payload["activity"] = {"steps": steps, "calories": cals, "minutes": minutes}
    except Exception:
        pass

    # Weight, body fat %, BP
    try:
        start, end = _epoch_range_for_day(date_str)
        q = urllib.parse.urlencode({
            "action": "getmeas",
            "meastypes": ",".join(["1", "6", "10", "11"]),
            "startdate": str(start),
            "enddate": str(end),
        })
        js = _http_get_json(f"{WITHINGS_API}/measure?{q}", headers)
        if js.get("status") == 0:
            grps = js.get("body", {}).get("measuregrps", [])
            latest_by_type: Dict[int, Tuple[int, float]] = {}
            for g in grps:
                ts = g.get("date") or 0
                for m in g.get("measures", []) or []:
                    mtype = m.get("type")
                    val = m.get("value")
                    unit = m.get("unit")
                    if isinstance(mtype, int) and isinstance(val, (int, float)) and isinstance(unit, int):
                        value = float(val) * (10 ** unit)
                        prev = latest_by_type.get(mtype)
                        if prev is None or ts > prev[0]:
                            latest_by_type[mtype] = (ts, value)
            # Map types
            if 1 in latest_by_type:  # Weight kg
                payload["weight_kg"] = round(latest_by_type[1][1], 2)
            if 6 in latest_by_type:  # Fat ratio %
                payload["body_fat_percent"] = round(latest_by_type[6][1], 2)
            bp = {}
            if 10 in latest_by_type:
                bp["systolic"] = round(latest_by_type[10][1], 0)
            if 11 in latest_by_type:
                bp["diastolic"] = round(latest_by_type[11][1], 0)
            if bp:
                payload.setdefault("withings_extra", {})["bp"] = bp
    except Exception:
        pass

    if rotated_note:
        payload["note"] = rotated_note

    return payload


def cli(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Withings connector")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--live", action="store_true", help="DEPRECATED: live is default when credentials are present")
    args = parser.parse_args(argv)

    datetime.strptime(args.date, "%Y-%m-%d")
    payload = fetch(args.date, live=args.live)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    cli()
