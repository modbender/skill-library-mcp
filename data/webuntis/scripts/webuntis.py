#!/usr/bin/env python3
"""Minimal WebUntis (Untis) JSON-RPC client.

Designed for read-only timetable access.

Auth is username/password (student account). Prefer a dedicated account if possible.

Usage examples:
  WEBUNTIS_BASE_URL="https://example.webuntis.com" \
  WEBUNTIS_SCHOOL="My School" \
  WEBUNTIS_USER="..." WEBUNTIS_PASS="..." \
  ./webuntis.py today

  ./webuntis.py range 2026-02-10 2026-02-14

Notes:
- WebUntis deployments differ. This script tries common JSON-RPC methods.
- It never writes data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse

import requests


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name, default)
    if v is None or v == "":
        raise SystemExit(f"Missing env var: {name}")
    return v


def _profile_env(profile: str | None, key: str, default: str | None = None) -> str:
    """Read env var either from WEBUNTIS_<KEY> or WEBUNTIS_<PROFILE>_<KEY>.

    Example:
      profile="school1", key="BASE_URL" -> WEBUNTIS_SCHOOL1_BASE_URL
    """
    if profile:
        p = profile.upper().replace("-", "_")
        v = os.environ.get(f"WEBUNTIS_{p}_{key}")
        if v:
            return v
    return _env(f"WEBUNTIS_{key}", default)


class WebUntisClient:
    def __init__(self, base_url: str, school: str, user: str, password: str, timeout: int = 25):
        self.base_url = base_url.rstrip("/")
        self.school = school
        self.user = user
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self._rpc_id = 1
        self.last_auth = None
        self._cache = {}

    @property
    def rpc_url(self) -> str:
        # Common layout: https://<host>/WebUntis/jsonrpc.do?school=<school>
        return f"{self.base_url}/WebUntis/jsonrpc.do?school={urllib.parse.quote(self.school)}"

    def _rpc(self, method: str, params: dict | list | None = None):
        payload = {
            "jsonrpc": "2.0",
            "id": self._rpc_id,
            "method": method,
            "params": params or {},
        }
        self._rpc_id += 1

        r = self.session.post(
            self.rpc_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data and data["error"]:
            raise RuntimeError(f"RPC error for {method}: {data['error']}")
        return data.get("result")

    def authenticate(self):
        # Typical method name is "authenticate".
        # Many deployments return { sessionId, personType, personId, klasseId, ... }.
        result = self._rpc(
            "authenticate",
            {
                "user": self.user,
                "password": self.password,
                "client": "openclaw",
            },
        )
        self.last_auth = result
        return result

    def get_user_data(self):
        # Commonly exists and includes personId + role.
        return self._rpc("getUserData")

    def get_timetable(self, element_type: int, element_id: int, start: dt.date, end: dt.date):
        # getTimetable expects dates as YYYYMMDD integers in many deployments.
        start_i = int(start.strftime("%Y%m%d"))
        end_i = int(end.strftime("%Y%m%d"))
        params = {
            "options": {
                "element": {"id": int(element_id), "type": int(element_type)},
                "startDate": start_i,
                "endDate": end_i,
                "showInfo": True,
                "showSubstText": True,
                "showLsText": True,
            }
        }
        return self._rpc("getTimetable", params)

    def _cached_list(self, method: str):
        if method in self._cache:
            return self._cache[method]
        res = self._rpc(method)
        self._cache[method] = res
        return res

    def get_subjects(self):
        return self._cached_list("getSubjects")

    def get_rooms(self):
        return self._cached_list("getRooms")

    def get_teachers(self):
        return self._cached_list("getTeachers")

    def get_classes(self):
        return self._cached_list("getKlassen")


def _parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def _index_by_id(items, name_keys=("name", "longName", "longname"), formatter=None):
    idx = {}
    if not items:
        return idx
    for it in items:
        if not isinstance(it, dict) or "id" not in it:
            continue
        if formatter is not None:
            try:
                idx[int(it["id"])] = formatter(it)
                continue
            except Exception:
                pass
        name = None
        for k in name_keys:
            if it.get(k):
                name = it.get(k)
                break
        idx[int(it["id"])] = name or str(it.get("id"))
    return idx


def _format_events(events, subj_by_id=None, room_by_id=None, teacher_by_id=None, class_by_id=None):
    if not events:
        return "(keine termine)"

    subj_by_id = subj_by_id or {}
    room_by_id = room_by_id or {}
    teacher_by_id = teacher_by_id or {}
    class_by_id = class_by_id or {}

    def date_s(v):
        v = str(v or "")
        return f"{v[0:4]}-{v[4:6]}-{v[6:8]}" if len(v) == 8 else (v or "?")

    def t(hhmm):
        if hhmm is None:
            return "?"
        hhmm = str(hhmm)
        if len(hhmm) == 3:  # e.g. 905
            hhmm = "0" + hhmm
        return f"{hhmm[:-2]}:{hhmm[-2:]}" if len(hhmm) == 4 else "?"

    lines = []
    for e in events:
        start = t(e.get("startTime"))
        end = t(e.get("endTime"))

        subj = None
        if isinstance(e.get("su"), list) and e["su"] and "id" in e["su"][0]:
            subj = subj_by_id.get(int(e["su"][0]["id"]))

        room = None
        if isinstance(e.get("ro"), list) and e["ro"] and "id" in e["ro"][0]:
            room = room_by_id.get(int(e["ro"][0]["id"]))

        teacher = None
        if isinstance(e.get("te"), list) and e["te"]:
            # pick first teacher id; sometimes orgid is present
            tid = e["te"][0].get("orgid") or e["te"][0].get("id")
            if tid is not None:
                teacher = teacher_by_id.get(int(tid))

        klass = None
        if isinstance(e.get("kl"), list) and e["kl"] and "id" in e["kl"][0]:
            klass = class_by_id.get(int(e["kl"][0]["id"]))

        parts = [f"{date_s(e.get('date'))} {start}-{end}"]
        if subj:
            parts.append(str(subj))
        if klass:
            parts.append(str(klass))
        if room:
            parts.append(f"Raum {room}")
        if teacher:
            parts.append(f"bei {teacher}")

        # substitution / lesson text if present
        st = e.get("substText")
        lt = e.get("lstext")
        extra = []
        if st:
            extra.append(str(st))
        if lt:
            extra.append(str(lt))
        if extra:
            parts.append("/".join(extra))

        lines.append(" · ".join(parts))

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=os.environ.get("WEBUNTIS_PROFILE"), help="Optional profile name (uses WEBUNTIS_<PROFILE>_* env vars)")
    ap.add_argument("--base-url", default=os.environ.get("WEBUNTIS_BASE_URL"))
    ap.add_argument("--school", default=os.environ.get("WEBUNTIS_SCHOOL"))
    ap.add_argument("--user", default=os.environ.get("WEBUNTIS_USER"))
    ap.add_argument("--pass", dest="password", default=os.environ.get("WEBUNTIS_PASS"))
    # element type/id are profile-aware too (optional)
    et_default = os.environ.get("WEBUNTIS_ELEMENT_TYPE", "5")
    if os.environ.get("WEBUNTIS_PROFILE"):
        p = os.environ["WEBUNTIS_PROFILE"].upper().replace("-", "_")
        et_default = os.environ.get(f"WEBUNTIS_{p}_ELEMENT_TYPE", et_default)
    ap.add_argument("--element-type", type=int, default=int(et_default))

    eid_default = os.environ.get("WEBUNTIS_ELEMENT_ID")
    if os.environ.get("WEBUNTIS_PROFILE"):
        p = os.environ["WEBUNTIS_PROFILE"].upper().replace("-", "_")
        eid_default = os.environ.get(f"WEBUNTIS_{p}_ELEMENT_ID", eid_default)
    ap.add_argument("--element-id", type=int, default=eid_default)

    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("today")

    p_range = sub.add_parser("range")
    p_range.add_argument("start")
    p_range.add_argument("end")

    args = ap.parse_args()

    profile = (args.profile or "").strip() or None

    base_url = args.base_url or _profile_env(profile, "BASE_URL")
    school = args.school or _profile_env(profile, "SCHOOL")
    user = args.user or _profile_env(profile, "USER")
    password = args.password or _profile_env(profile, "PASS")

    c = WebUntisClient(base_url=base_url, school=school, user=user, password=password)

    auth = c.authenticate() or {}

    element_type = args.element_type
    element_id = args.element_id

    # Best-effort auto-discovery of element_id:
    # 1) from authenticate() result (common)
    if element_id is None and isinstance(auth, dict) and auth.get("personId"):
        element_id = int(auth["personId"])

    # 2) from getUserData (not available on all deployments)
    if element_id is None:
        try:
            ud = c.get_user_data() or {}
            if isinstance(ud, dict) and ud.get("personId"):
                element_id = int(ud["personId"])
        except Exception:
            pass

    if element_id is None:
        raise SystemExit("Could not determine element-id. Set WEBUNTIS_ELEMENT_ID=<id>.")

    if args.cmd == "today":
        start = end = dt.date.today()
    else:
        start = _parse_date(args.start)
        end = _parse_date(args.end)

    events = c.get_timetable(element_type=element_type, element_id=element_id, start=start, end=end)

    # Resolve ids to names (best-effort; some deployments return names directly)
    try:
        subj_by_id = _index_by_id(c.get_subjects())
    except Exception:
        subj_by_id = {}
    try:
        room_by_id = _index_by_id(c.get_rooms())
    except Exception:
        room_by_id = {}
    def _teacher_fmt(t):
        fn = (t.get("foreName") or "").strip()
        ln = (t.get("longName") or t.get("name") or "").strip()
        full = (fn + " " + ln).strip()
        return full or str(t.get("id"))

    try:
        teacher_by_id = _index_by_id(c.get_teachers(), formatter=_teacher_fmt)
    except Exception:
        teacher_by_id = {}
    try:
        class_by_id = _index_by_id(c.get_classes())
    except Exception:
        class_by_id = {}

    print(_format_events(events, subj_by_id=subj_by_id, room_by_id=room_by_id, teacher_by_id=teacher_by_id, class_by_id=class_by_id))


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
