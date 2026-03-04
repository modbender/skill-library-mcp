#!/usr/bin/env python3
"""IServ (grabbe-dt.de) minimal HTTP client.

Goal: provide read access to common IServ modules via official-ish web endpoints.

Currently implemented (should work on many IServ instances):
- login via /iserv/auth/login (form fields _username/_password)
- unread mail count (IServ API)
- mail list metadata (IServ API)
- mail read / last mails (IMAP)
- mail send / reply (SMTP)
- calendar upcoming events
- file list (root)

Design:
- no browser automation required
- credentials only via env vars
- supports multi-profile env var prefixes

Env (single profile):
  ISERV_BASE_URL=https://grabbe-dt.de
  ISERV_USER=...
  ISERV_PASS=...

Env (multi profile):
  ISERV_PROFILE=cdg
  ISERV_CDG_BASE_URL=...
  ISERV_CDG_USER=...
  ISERV_CDG_PASS=...

Usage:
  ./iserv.py mail-unread
  ./iserv.py mail-list --limit 20
  ./iserv.py mail-last --n 3
  ./iserv.py mail-send --to finn.busse@grabbe-dt.de --subject "Hi" --body "..."
  ./iserv.py mail-reply --uid 370 --body "..."
  ./iserv.py calendar-upcoming
  ./iserv.py files-list --path "/"
  ./iserv.py files-download --path "/Dokumente/foo.pdf" --out-dir ./downloads
  ./iserv.py files-upload --file ./foo.pdf --dest-dir "/Dokumente"
  ./iserv.py files-mkdir --path "/Dokumente/Neu"
  ./iserv.py files-rename --src "/Dokumente/A.txt" --dest "/Dokumente/B.txt"
  ./iserv.py files-delete --path "/Dokumente/B.txt"
  ./iserv.py messenger-chats
  ./iserv.py messenger-messages --chat-id <ID>
  ./iserv.py messenger-send --chat-id <ID> --text "Hello"

"""

from __future__ import annotations

import argparse
import os
import sys
import ssl
import imaplib
import email
import re
import html as _html
import uuid
from pathlib import Path
from email.header import decode_header
from email.message import Message
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin, quote
from html.parser import HTMLParser

import requests

import smtplib
from email.message import EmailMessage


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


def _profile_env(profile: str | None, key: str) -> str:
    if profile:
        p = profile.upper().replace("-", "_")
        v = os.environ.get(f"ISERV_{p}_{key}")
        if v:
            return v
    return _env(f"ISERV_{key}")


def _host_from_base_url(base_url: str) -> str:
    u = urlparse(base_url)
    return u.hostname or base_url.replace('https://', '').replace('http://', '').split('/')[0]


def _decode_mime_header(value: str) -> str:
    parts = []
    for chunk, enc in decode_header(value):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(enc or 'utf-8', errors='replace'))
        else:
            parts.append(chunk)
    return ''.join(parts).strip()


def _extract_text(msg: Message, max_chars: int = 1200) -> str:
    # prefer text/plain
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = (part.get('Content-Disposition') or '').lower()
            if ctype == 'text/plain' and 'attachment' not in disp:
                payload = part.get_payload(decode=True) or b''
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='replace').strip()[:max_chars]
        # fallback: first text/*
        for part in msg.walk():
            if part.get_content_maintype() == 'text':
                payload = part.get_payload(decode=True) or b''
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='replace').strip()[:max_chars]
        return ''
    else:
        payload = msg.get_payload(decode=True) or b''
        charset = msg.get_content_charset() or 'utf-8'
        return payload.decode(charset, errors='replace').strip()[:max_chars]


_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(s: str) -> str:
    return _TAG_RE.sub("", s or "")


def _find_csrf_token(html_text: str) -> str | None:
    # Symfony default
    m = re.search(r'name=["\"]_token["\"]\s+value=["\"]([^"\"]+)["\"]', html_text)
    if m:
        return _html.unescape(m.group(1))
    # meta tag
    m = re.search(r'<meta\s+name=["\"]csrf-token["\"]\s+content=["\"]([^"\"]+)["\"]', html_text, re.I)
    if m:
        return _html.unescape(m.group(1))
    return None


class _FormParser(HTMLParser):
    """Very small HTML form parser (dependency-free).

    Captures <form> blocks with their inputs/textareas/selects. Not a full HTML DOM.
    """

    def __init__(self):
        super().__init__()
        self.forms: list[dict] = []
        self._cur: dict | None = None
        self._in_textarea: dict | None = None
        self._textarea_buf: list[str] = []
        self._in_select: dict | None = None
        self._cur_option: dict | None = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "form":
            self._cur = {
                "action": a.get("action", ""),
                "method": (a.get("method") or "get").lower(),
                "enctype": (a.get("enctype") or "").lower(),
                "inputs": [],
                "textareas": [],
                "selects": [],
            }
            return

        if not self._cur:
            return

        if tag.lower() == "input":
            itype = (a.get("type") or "text").lower()
            self._cur["inputs"].append({
                "type": itype,
                "name": a.get("name", ""),
                "value": a.get("value", ""),
            })
        elif tag.lower() == "textarea":
            self._in_textarea = {"name": a.get("name", ""), "value": ""}
            self._textarea_buf = []
        elif tag.lower() == "select":
            self._in_select = {"name": a.get("name", ""), "options": [], "value": ""}
        elif tag.lower() == "option" and self._in_select is not None:
            self._cur_option = {"value": a.get("value", ""), "selected": "selected" in a or a.get("selected") != ""}

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "form" and self._cur is not None:
            self.forms.append(self._cur)
            self._cur = None
        elif tag == "textarea" and self._cur is not None and self._in_textarea is not None:
            self._in_textarea["value"] = "".join(self._textarea_buf)
            self._cur["textareas"].append(self._in_textarea)
            self._in_textarea = None
            self._textarea_buf = []
        elif tag == "select" and self._cur is not None and self._in_select is not None:
            # choose selected option if present
            sel = ""
            for opt in self._in_select["options"]:
                if opt.get("selected"):
                    sel = opt.get("value") or ""
                    break
            self._in_select["value"] = sel
            self._cur["selects"].append(self._in_select)
            self._in_select = None
        elif tag == "option" and self._in_select is not None:
            if self._cur_option is not None:
                self._in_select["options"].append(self._cur_option)
            self._cur_option = None

    def handle_data(self, data):
        if self._in_textarea is not None:
            self._textarea_buf.append(data)


def _parse_forms(html_text: str) -> list[dict]:
    p = _FormParser()
    p.feed(html_text)
    return p.forms


def _find_form_for_exercise_submission(html_text: str) -> dict | None:
    """Pick the most likely submission form.

    Heuristics:
    - Prefer forms that contain an <input type="file">.
    - Otherwise pick the one whose action contains '/iserv/exercise/attachment'.
    """
    forms = _parse_forms(html_text)
    best = None
    for f in forms:
        action = f.get("action") or ""
        has_file = any((i.get("type") == "file" and (i.get("name") or "")) for i in f.get("inputs", []))
        if has_file:
            return f
        if "/iserv/exercise/attachment" in action:
            best = f
    return best


@dataclass
class IServClient:
    base_url: str
    user: str
    password: str
    timeout: int = 25

    def __post_init__(self):
        self.base_url = self.base_url.rstrip("/")
        self.host = _host_from_base_url(self.base_url)
        self.s = requests.Session()
        self._routes: dict[str, str] | None = None
        self._messenger_api_base: str | None = None
        self._messenger_chats_path: str | None = None

    def login(self, start_path: str = "/iserv/"):
        """Log in and preserve the correct _target_path redirect chain.

        Some IServ apps (e.g. messenger under /iserv/app/...) require starting from the
        target page so the auth flow sets the right cookies / session.
        """
        start_url = f"{self.base_url}{start_path}" if start_path.startswith("/") else start_path

        # Step 1: hit a protected page; follow redirects until we land on /iserv/auth/login?..._target_path=...
        r0 = self.s.get(start_url, allow_redirects=True, timeout=self.timeout)
        login_url = r0.url
        if "/iserv/auth/login" not in login_url:
            # fallback to plain login
            login_url = f"{self.base_url}/iserv/auth/login"
            self.s.get(login_url, timeout=self.timeout)

        # Step 2: post credentials to the *current* login URL (keeps query like _target_path)
        r = self.s.post(
            login_url,
            data={"_username": self.user, "_password": self.password, "_remember_me": "on"},
            allow_redirects=True,
            timeout=self.timeout,
        )
        r.raise_for_status()

        # Basic check: some IServ cookies appear after successful login
        if not any(k.lower().startswith("iserv") for k in self.s.cookies.get_dict().keys()):
            raise RuntimeError("Login failed (no IServ cookies set)")
        return True

    def mail_unread(self) -> int:
        r = self.s.get(f"{self.base_url}/iserv/mail/api/unread/inbox", timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return int(data.get("count", 0))

    def mail_list(self, folder: str = "INBOX", limit: int = 20, offset: int = 0):
        """List mail metadata via IServ mail API."""
        # Endpoint expects order as JSON string: {"column":"date","dir":"desc"}
        order = '{"column":"date","dir":"desc"}'
        params = {
            'folder': folder,
            'order': order,
            'offset': int(offset),
            'limit': int(limit),
            'filter': '{}',
        }
        r = self.s.get(f"{self.base_url}/iserv/mail/api/message/list", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _imap(self):
        ctx = ssl.create_default_context()
        M = imaplib.IMAP4_SSL(self.host, 993, ssl_context=ctx)
        M.login(self.user, self.password)
        return M

    def mail_last(self, n: int = 3):
        """Return last n mails via IMAP (headers + short text excerpt)."""
        M = self._imap()
        M.select('INBOX')
        typ, ids = M.search(None, 'ALL')
        if typ != 'OK':
            M.logout()
            raise RuntimeError('IMAP search failed')
        all_ids = ids[0].split()
        last_ids = all_ids[-n:]
        results = []
        for mid in last_ids[::-1]:
            typ, msg_data = M.fetch(mid, '(RFC822)')
            if typ != 'OK':
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            results.append({
                'from': _decode_mime_header(msg.get('From','')),
                'subject': _decode_mime_header(msg.get('Subject','')),
                'date': _decode_mime_header(msg.get('Date','')),
                'excerpt': _extract_text(msg, max_chars=1200),
            })
        M.logout()
        return results

    def mail_read_uid(self, uid: int, folder: str = 'INBOX'):
        M = self._imap()
        M.select(folder)
        typ, msg_data = M.uid('fetch', str(uid), '(RFC822)')
        if typ != 'OK' or not msg_data or not msg_data[0]:
            M.logout()
            raise RuntimeError('IMAP uid fetch failed')
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        out = {
            'from': _decode_mime_header(msg.get('From','')),
            'to': _decode_mime_header(msg.get('To','')),
            'subject': _decode_mime_header(msg.get('Subject','')),
            'date': _decode_mime_header(msg.get('Date','')),
            'message_id': _decode_mime_header(msg.get('Message-Id','')),
            'references': _decode_mime_header(msg.get('References','')),
            'excerpt': _extract_text(msg, max_chars=6000),
        }
        M.logout()
        return out

    def mail_send(self, to_addr: str, subject: str, body: str):
        msg = EmailMessage()
        msg['From'] = f"{self.user}@{self.host}"
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.set_content(body)

        ctx = ssl.create_default_context()
        with smtplib.SMTP(self.host, 587, timeout=self.timeout) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
            s.login(self.user, self.password)
            s.send_message(msg)
        return True

    def mail_reply(self, uid: int, body: str, folder: str = 'INBOX'):
        orig = self.mail_read_uid(uid=uid, folder=folder)
        # basic reply: to original sender
        to_addr = orig['from']
        subj = orig['subject']
        if not subj.lower().startswith('re:'):
            subj = 'Re: ' + subj

        msg = EmailMessage()
        msg['From'] = f"{self.user}@{self.host}"
        msg['To'] = to_addr
        msg['Subject'] = subj
        if orig.get('message_id'):
            msg['In-Reply-To'] = orig['message_id']
            refs = (orig.get('references') or '').strip()
            msg['References'] = (refs + ' ' + orig['message_id']).strip() if refs else orig['message_id']
        msg.set_content(body)

        ctx = ssl.create_default_context()
        with smtplib.SMTP(self.host, 587, timeout=self.timeout) as s:
            s.ehlo(); s.starttls(context=ctx); s.ehlo()
            s.login(self.user, self.password)
            s.send_message(msg)
        return True

    def calendar_upcoming(self):
        r = self.s.get(f"{self.base_url}/iserv/calendar/api/upcoming", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _discover_routes(self) -> dict[str, str]:
        """Best-effort discovery of Symfony FOS JS routes.

        IServ commonly exposes the route table via:
          /iserv/js/fos_js_routes.js

        That file is JS, but it embeds a JSON object passed to:
          Routing.setRoutingData({...});

        We parse it and reconstruct a simple path template for each route by
        concatenating the token list (text + variable placeholders).
        """
        if self._routes is not None:
            return self._routes

        js_candidates = [
            f"{self.base_url}/iserv/js/fos_js_routes.js",
            f"{self.base_url}/iserv/js/assets/fos_js_routes.js",
        ]

        routes: dict[str, str] = {}
        for url in js_candidates:
            try:
                r = self.s.get(url, timeout=self.timeout)
                if r.status_code >= 400:
                    continue
                t = r.text or ""
                # Extract JSON object inside Routing.setRoutingData(...)
                m = re.search(r"Routing\.setRoutingData\((\{.*\})\);", t, re.S)
                if not m:
                    continue
                import json

                data = json.loads(m.group(1))
                base_url = (data.get("base_url") or "")
                if isinstance(base_url, str) and base_url:
                    base_url = base_url.rstrip("/")

                rts = data.get("routes") if isinstance(data, dict) else None
                if not isinstance(rts, dict):
                    continue

                for name, spec in rts.items():
                    if not isinstance(spec, dict):
                        continue
                    toks = spec.get("tokens")
                    if not isinstance(toks, list):
                        continue
                    parts: list[str] = []
                    for tok in toks:
                        if not isinstance(tok, list) or not tok:
                            continue
                        kind = tok[0]
                        if kind == "text" and len(tok) >= 2:
                            parts.append(str(tok[1]))
                        elif kind == "variable" and len(tok) >= 4:
                            # tok: ["variable", <separator>, <regex>, <name>, <optional?>]
                            sep = str(tok[1])
                            varname = str(tok[3])
                            parts.append(sep + "{" + varname + "}")
                    path_tpl = "".join(parts)
                    # include base_url prefix if present
                    if base_url and path_tpl.startswith("/"):
                        path_tpl = base_url + path_tpl
                    routes[str(name)] = path_tpl

                if routes:
                    break
            except Exception:
                continue

        self._routes = routes
        return routes

    def files_list(self, path: str = ""):
        """List files/folders for a directory (JSON).

        IServ has at least two variants in the wild:
        - /iserv/file/api/list/<path>
        - /iserv/file/api/list?path=<path>

        We try the route-based variant first (as exposed in FOS routes on grabbe-dt.de),
        then fall back to the query variant.

        Args:
            path: remote directory path. Examples: "", "/", "/Files", "/Files/Sub".

        Returns:
            Parsed JSON (usually dict with entries/data).
        """
        if path is None:
            path = ""
        p = (path or "").strip()
        if p in ("/", ""):
            p = ""
        if p.startswith("/"):
            p = p[1:]

        # Candidate 1: route-based list
        routes = self._discover_routes()
        if "file_list_json" in routes:
            tpl = routes["file_list_json"]
            # If the template contains a {path} placeholder, fill it.
            if "{path}" in tpl:
                filled = tpl.replace("{path}", quote(p, safe=""))
                # Normalize potential double slashes when p is empty
                filled = filled.replace("//", "/")
                url = f"{self.base_url}{filled}" if filled.startswith("/") else f"{self.base_url}/{filled}"
            else:
                base_path = tpl.rstrip("/")
                url = f"{self.base_url}{base_path}"
                if p:
                    url = url + "/" + quote(p, safe="")
            r = self.s.get(url, timeout=self.timeout)
            if r.status_code < 400 and self._is_json_response(r):
                return r.json()

        # Candidate 2: common API path with query param
        url = f"{self.base_url}/iserv/file/api/list"
        r = self.s.get(url, params={"path": p}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _files_entries(self, list_json: object) -> list[dict]:
        """Normalize various list responses to a list of entry dicts (best-effort)."""
        if isinstance(list_json, dict):
            for k in ("entries", "data", "items", "children"):
                v = list_json.get(k)
                if isinstance(v, list):
                    return [x for x in v if isinstance(x, dict)]
            # Some instances return dict with numeric keys
            if all(isinstance(v, dict) for v in list_json.values()):
                return list(list_json.values())
        if isinstance(list_json, list):
            return [x for x in list_json if isinstance(x, dict)]
        return []

    def files_search(self, query: str, start_dir: str = "/Files", max_results: int = 50, max_depth: int = 6) -> list[dict]:
        """Recursive file/folder search by substring in name (best-effort).

        Returns list of matches with at least: name, path (when inferable), type.
        """
        q = (query or "").strip().lower()
        if not q:
            return []

        if not start_dir.startswith("/"):
            start_dir = "/" + start_dir
        start_dir = start_dir.rstrip("/") or "/"

        results: list[dict] = []
        queue: list[tuple[str, int]] = [(start_dir, 0)]
        seen: set[str] = set()

        while queue and len(results) < max_results:
            cur, depth = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            if depth > max_depth:
                continue

            j = self.files_list(cur)
            for e in self._files_entries(j):
                name = str(e.get("name") or e.get("filename") or e.get("title") or "").strip()
                etype = (e.get("type") or e.get("kind") or "").lower()
                is_dir = bool(e.get("isDir") or e.get("is_dir") or e.get("directory")) or etype in ("dir", "folder", "directory")

                # Try to infer full path
                ep = e.get("path") or e.get("fullPath") or e.get("full_path")
                if isinstance(ep, str) and ep.startswith("/"):
                    full_path = ep
                else:
                    full_path = (cur.rstrip("/") + "/" + name) if name else None

                if name and q in name.lower():
                    results.append({
                        "name": name,
                        "path": full_path,
                        "type": "dir" if is_dir else "file",
                        "raw": e,
                    })
                    if len(results) >= max_results:
                        break

                if is_dir and name:
                    queue.append((cur.rstrip("/") + "/" + name, depth + 1))

        return results

    def _download_stream_to_path(self, r: requests.Response, out_dir: str, fallback_name: str) -> Path:
        out_dir_p = Path(out_dir)
        out_dir_p.mkdir(parents=True, exist_ok=True)

        # filename from Content-Disposition; fallback to provided name
        fname = None
        cd = r.headers.get("Content-Disposition") or ""
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd)
        if m:
            fname = _html.unescape(m.group(1))
        if not fname:
            m = re.search(r"filename=\"?([^\";]+)\"?", cd)
            if m:
                fname = _html.unescape(m.group(1))
        if not fname:
            fname = fallback_name or "download.bin"

        out_path = out_dir_p / fname
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)
        return out_path

    def _fs_prepare_download(self, source: str, paths: list[str]) -> str | None:
        """Ask the FS API to prepare a download and return an identifier (best-effort)."""
        routes = self._discover_routes()
        # /fs/api/actions/<source>/<path>
        action_route = routes.get("filesystem_api_actions")
        if not action_route:
            return None

        # Some installations expose actions as either:
        #   POST /iserv/fs/api/actions/<source>
        # or
        #   POST /iserv/fs/api/actions/<source>/<path>
        # We'll try a few variants.
        bases = [
            f"{self.base_url}/iserv/fs/api/actions/{quote(source, safe='')}",
            f"{self.base_url}/iserv/fs/api/actions/{quote(source, safe='')}/",
        ]
        # Also try with a directory context (use first path's parent)
        try:
            parent = "/" + str(Path(paths[0]).parent).lstrip("/")
            if parent in ("/", "."):
                parent = ""
            if parent:
                bases.append(f"{self.base_url}/iserv/fs/api/actions/{quote(source, safe='')}/{quote(parent.lstrip('/'), safe='')}")
        except Exception:
            pass

        payload_candidates = [
            {"action": "prepareDownload", "paths": paths},
            {"action": "download", "paths": paths},
            {"action": "prepare_download", "paths": paths},
            {"action": "preparedDownload", "paths": paths},
        ]

        for base in bases:
            for pl in payload_candidates:
                try:
                    r = self.s.post(base, json=pl, timeout=self.timeout)
                    if r.status_code >= 400:
                        continue
                    if not self._is_json_response(r):
                        continue
                    j = r.json()
                    # Common keys we have seen across Symfony apps
                    for k in ("identifier", "id", "token", "download", "prepared", "preparedDownload"):
                        v = j.get(k) if isinstance(j, dict) else None
                        if isinstance(v, str) and v:
                            return v
                    # Sometimes nested
                    if isinstance(j, dict):
                        for kk in ("data", "result"):
                            v2 = j.get(kk)
                            if isinstance(v2, dict):
                                for k in ("identifier", "id", "token"):
                                    v = v2.get(k)
                                    if isinstance(v, str) and v:
                                        return v
                except Exception:
                    continue
        return None

    def files_download(self, path: str, out_dir: str = ".") -> Path:
        """Download a file by remote path (best-effort across IServ versions).

        Strategy:
          1) Try legacy direct download endpoints with ?path=...
          2) Try /iserv/file_pass/<path> (legacy)
          3) Use FS "prepare download" + /iserv/file/prepared/download/<identifier> (newer)
        """
        if not path.startswith("/"):
            path = "/" + path
        fallback_name = Path(path).name or "download.bin"

        # 1) Known direct endpoints (older installations)
        direct_candidates = [
            f"{self.base_url}/iserv/file/api/download",
            f"{self.base_url}/iserv/fs/api/download",
            f"{self.base_url}/iserv/fs/api/file/download",
        ]
        routes = self._discover_routes()
        for rn in ("iserv_file_api_download", "iserv_fs_api_download", "iserv_fs_download"):
            if rn in routes:
                direct_candidates.insert(0, f"{self.base_url}{routes[rn]}")

        for url in direct_candidates:
            try:
                r = self.s.get(url, params={"path": path}, stream=True, timeout=self.timeout)
                if r.status_code >= 400:
                    continue
                return self._download_stream_to_path(r, out_dir=out_dir, fallback_name=fallback_name)
            except Exception:
                pass

        # 2) Legacy file_pass route (may or may not be enabled)
        try:
            url = f"{self.base_url}/iserv/file_pass/{quote(path.lstrip('/'), safe='') }"
            r = self.s.get(url, stream=True, timeout=self.timeout)
            if r.status_code < 400:
                return self._download_stream_to_path(r, out_dir=out_dir, fallback_name=fallback_name)
        except Exception:
            pass

        # 3) FS prepared download
        identifier = self._fs_prepare_download(source="file", paths=[path])
        if identifier:
            url = f"{self.base_url}/iserv/file/prepared/download/{quote(identifier, safe='')}"
            r = self.s.get(url, stream=True, timeout=self.timeout)
            r.raise_for_status()
            return self._download_stream_to_path(r, out_dir=out_dir, fallback_name=fallback_name)

        raise RuntimeError(f"Could not download path={path}. No working download strategy succeeded.")

    def files_upload(self, local_file: str, dest_dir: str = "/Files", chunk_size: int | None = None) -> dict:
        """Upload a local file into a destination directory.

        Newer IServ installations (including grabbe-dt.de) use a Dropzone-style
        chunked upload against the FS API:
          POST /iserv/fs/api/upload/<source>
        with form fields like dzuuid/dzchunkindex/... and a multipart "file" part.

        This implementation:
          1) tries the FS chunked upload (preferred)
          2) falls back to legacy /iserv/file/upload form POST if FS upload fails

        Returns a small debug dict.
        """
        fp = Path(local_file)
        if not fp.exists():
            raise FileNotFoundError(str(fp))

        # Normalize destination dir to something like "Files/Sub"
        d = (dest_dir or "/Files").strip()
        if d in ("", "/"):
            d = "/Files"
        if not d.startswith("/"):
            d = "/" + d
        d = d.rstrip("/")

        # Preferred: FS (dropzone/chunked)
        try:
            return self._files_upload_fs_chunked(fp=fp, dest_dir=d, chunk_size=chunk_size)
        except Exception as e_fs:
            # Fallback: legacy form upload (some instances still use it)
            try:
                return self._files_upload_legacy_form(fp=fp, dest_dir=d, err_hint=str(e_fs))
            except Exception:
                raise

    def _files_upload_fs_chunked(self, fp: Path, dest_dir: str, chunk_size: int | None = None) -> dict:
        routes = self._discover_routes()

        # Pick upload URL; routes expose filesystem_universal_upload: /fs/api/upload/<source>
        upload_url = None
        if "filesystem_universal_upload" in routes:
            # We don't reconstruct placeholder routes fully; build manually
            upload_url = f"{self.base_url}/iserv/fs/api/upload/file"
        else:
            upload_url = f"{self.base_url}/iserv/fs/api/upload/file"

        # Ask connectivity endpoint for hints (best-effort)
        if chunk_size is None:
            try:
                r = self.s.get(f"{self.base_url}/iserv/file/upload/connectivity", timeout=self.timeout)
                if r.status_code < 400 and self._is_json_response(r):
                    j = r.json()
                    # heuristic keys
                    for k in ("chunkSize", "chunk_size", "maxChunkSize", "max_chunk_size"):
                        v = j.get(k) if isinstance(j, dict) else None
                        if isinstance(v, int) and v > 0:
                            chunk_size = int(v)
                            break
            except Exception:
                pass
        if chunk_size is None:
            chunk_size = 8 * 1024 * 1024  # 8 MiB default

        total_size = fp.stat().st_size
        total_chunks = max(1, (total_size + chunk_size - 1) // chunk_size)
        dzu = str(uuid.uuid4())

        # CSRF token (optional but some instances require it)
        csrf = None
        try:
            page = self.s.get(f"{self.base_url}/iserv/file/-/{quote(dest_dir.lstrip('/'), safe='')}", timeout=self.timeout)
            if page.status_code < 400:
                csrf = _find_csrf_token(page.text)
        except Exception:
            pass

        last_json = None
        with open(fp, "rb") as f:
            for idx in range(total_chunks):
                offset = idx * chunk_size
                f.seek(offset)
                data_bytes = f.read(chunk_size)
                if not data_bytes:
                    break

                form = {
                    # Dropzone chunk metadata
                    "dzuuid": dzu,
                    "dzchunkindex": str(idx),
                    "dztotalchunkcount": str(total_chunks),
                    "dzchunksize": str(chunk_size),
                    "dztotalfilesize": str(total_size),
                    "dzchunkbyteoffset": str(offset),
                    # Destination
                    "path": dest_dir,
                    "upload[path]": dest_dir.lstrip("/"),
                }
                headers = {"X-Requested-With": "XMLHttpRequest"}
                if csrf:
                    headers["X-CSRF-Token"] = csrf

                files = {"file": (fp.name, data_bytes)}
                r = self.s.post(upload_url, data=form, files=files, headers=headers, timeout=self.timeout)
                if r.status_code >= 400:
                    raise RuntimeError(f"FS chunk upload failed at chunk {idx+1}/{total_chunks}: HTTP {r.status_code} {r.text[:400]}")
                if self._is_json_response(r):
                    last_json = r.json()

        return {
            "ok": True,
            "method": "fs_chunked",
            "upload_url": upload_url,
            "dest_dir": dest_dir,
            "filename": fp.name,
            "size": total_size,
            "chunk_size": chunk_size,
            "chunks": total_chunks,
            "last_json": last_json,
        }

    def _files_upload_legacy_form(self, fp: Path, dest_dir: str, err_hint: str | None = None) -> dict:
        # Normalize destination path like "/Files" -> "Files"
        d = dest_dir.lstrip("/").strip("/")
        if not d:
            d = "Files"

        # Fetch token from file page HTML
        page = self.s.get(f"{self.base_url}/iserv/file/-/{quote(d, safe='')}", timeout=self.timeout)
        page.raise_for_status()
        tok_m = re.search(r'id="upload__token"[^>]*value="([^"]+)"', page.text)
        token = tok_m.group(1) if tok_m else ""

        upload_url = f"{self.base_url}/iserv/file/upload"
        with open(fp, "rb") as f:
            r = self.s.post(
                upload_url,
                files={"file": (fp.name, f)},
                data={"upload[path]": d, "upload[_token]": token},
                timeout=self.timeout,
                allow_redirects=True,
            )
        r.raise_for_status()
        return {
            "ok": True,
            "method": "legacy_form",
            "upload_url": upload_url,
            "dest_dir": dest_dir,
            "filename": fp.name,
            "size": fp.stat().st_size,
            "err_hint": err_hint,
            "status": r.status_code,
            "final_url": str(r.url),
            "content_type": r.headers.get("content-type"),
            "text_head": (r.text or "")[:800],
        }

    def files_mkdir(self, path: str) -> dict:
        """Create a folder (best-effort)."""
        if not path.startswith("/"):
            path = "/" + path
        routes = self._discover_routes()
        candidates = []
        for rn in ("iserv_fs_api_mkdir", "iserv_fs_api_folder_create", "iserv_fs_mkdir"):
            if rn in routes:
                candidates.append(f"{self.base_url}{routes[rn]}")
        candidates += [
            f"{self.base_url}/iserv/fs/api/mkdir",
            f"{self.base_url}/iserv/fs/api/folder/create",
            f"{self.base_url}/iserv/file/api/folder/create",
        ]
        last = None
        for url in candidates:
            try:
                r = self.s.post(url, json={"path": path}, timeout=self.timeout)
                if r.status_code >= 400:
                    continue
                return r.json() if self._is_json_response(r) else {"status": r.status_code, "text": (r.text or "")[:2000]}
            except Exception as e:
                last = e
        raise RuntimeError(f"mkdir failed for {path}. Last error: {last}")

    def files_rename(self, src_path: str, dest_path: str) -> dict:
        """Rename/move a file or folder (best-effort)."""
        if not src_path.startswith("/"):
            src_path = "/" + src_path
        if not dest_path.startswith("/"):
            dest_path = "/" + dest_path

        routes = self._discover_routes()
        candidates = []
        for rn in ("iserv_fs_api_rename", "iserv_fs_api_move", "iserv_file_api_rename"):
            if rn in routes:
                candidates.append(f"{self.base_url}{routes[rn]}")
        candidates += [
            f"{self.base_url}/iserv/fs/api/rename",
            f"{self.base_url}/iserv/fs/api/move",
            f"{self.base_url}/iserv/file/api/rename",
        ]

        last = None
        for url in candidates:
            try:
                r = self.s.post(url, json={"source": src_path, "src": src_path, "from": src_path, "destination": dest_path, "dest": dest_path, "to": dest_path}, timeout=self.timeout)
                if r.status_code >= 400:
                    continue
                return r.json() if self._is_json_response(r) else {"status": r.status_code, "text": (r.text or "")[:2000]}
            except Exception as e:
                last = e
        raise RuntimeError(f"rename/move failed {src_path} -> {dest_path}. Last error: {last}")

    def files_delete(self, path: str) -> dict:
        """Delete a file or folder (best-effort; use with care)."""
        if not path.startswith("/"):
            path = "/" + path
        routes = self._discover_routes()
        candidates = []
        for rn in ("iserv_fs_api_delete", "iserv_file_api_delete"):
            if rn in routes:
                candidates.append(f"{self.base_url}{routes[rn]}")
        candidates += [
            f"{self.base_url}/iserv/fs/api/delete",
            f"{self.base_url}/iserv/file/api/delete",
        ]

        last = None
        for url in candidates:
            for method in ("post", "delete"):
                try:
                    r = self.s.request(method.upper(), url, json={"path": path}, timeout=self.timeout)
                    if r.status_code >= 400:
                        continue
                    return r.json() if self._is_json_response(r) else {"status": r.status_code, "text": (r.text or "")[:2000]}
                except Exception as e:
                    last = e
        raise RuntimeError(f"delete failed for {path}. Last error: {last}")

    # --------------------
    # Messenger (IServ app)
    # --------------------

    def _is_json_response(self, r: requests.Response) -> bool:
        ct = (r.headers.get('content-type') or '').lower()
        return 'application/json' in ct or ct.startswith('application/json')

    def _messenger_discover(self) -> tuple[str, str]:
        """Discover a working messenger API base + chats list path.

        Many IServ instances mount the messenger API under:
          /iserv/app/messenger/api/...

        This method tries a set of known bases and chats endpoints and caches
        the first combination that returns JSON.
        """
        if self._messenger_api_base and self._messenger_chats_path:
            return self._messenger_api_base, self._messenger_chats_path

        base_candidates = [
            f"{self.base_url}/iserv/app/messenger/api",
            f"{self.base_url}/iserv/messenger/api",
        ]
        chats_paths = [
            "/chat/list",
            "/chats",
            "/conversation/list",
            "/conversations",
            "/room/list",
            "/rooms",
        ]

        last_err: Exception | None = None
        for b in base_candidates:
            for p in chats_paths:
                url = b + p
                try:
                    r = self.s.get(url, allow_redirects=False, timeout=self.timeout)
                    # Not logged in usually yields 302 to /iserv/auth/auth.
                    if r.status_code in (301, 302, 303, 307, 308):
                        continue
                    if r.status_code >= 400:
                        continue
                    if not self._is_json_response(r):
                        # Some endpoints return HTML.
                        continue
                    _ = r.json()  # ensure valid JSON
                    self._messenger_api_base = b
                    self._messenger_chats_path = p
                    return b, p
                except Exception as e:
                    last_err = e
                    continue

        raise RuntimeError(
            "Could not discover messenger API endpoints. "
            "Are you logged in and does this IServ instance have Messenger enabled?"
            + (f" Last error: {last_err}" if last_err else "")
        )

    def messenger_chats(self):
        """List messenger chats/conversations."""
        b, p = self._messenger_discover()
        r = self.s.get(b + p, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def messenger_messages(self, chat_id: str, limit: int = 50, offset: int = 0):
        """Fetch messages for a given chat/conversation id."""
        b, _ = self._messenger_discover()
        # Try a few common message listing endpoints.
        candidates = [
            ("GET", f"/chat/{chat_id}/message/list", {"params": {"limit": limit, "offset": offset}}),
            ("GET", f"/chat/{chat_id}/messages", {"params": {"limit": limit, "offset": offset}}),
            ("GET", f"/conversation/{chat_id}/message/list", {"params": {"limit": limit, "offset": offset}}),
            ("GET", f"/conversation/{chat_id}/messages", {"params": {"limit": limit, "offset": offset}}),
            ("GET", "/message/list", {"params": {"chatId": chat_id, "limit": limit, "offset": offset}}),
            ("GET", "/messages", {"params": {"chatId": chat_id, "limit": limit, "offset": offset}}),
        ]
        last: Exception | None = None
        for method, path, kw in candidates:
            try:
                r = self.s.request(method, b + path, timeout=self.timeout, **kw)
                if r.status_code >= 400:
                    continue
                if not self._is_json_response(r):
                    continue
                return r.json()
            except Exception as e:
                last = e
                continue
        raise RuntimeError(f"Could not fetch messages for chat_id={chat_id}. Last error: {last}")

    def messenger_send(self, chat_id: str, text: str):
        """Send a text message to a chat/conversation id."""
        b, _ = self._messenger_discover()
        # Try a few common send endpoints/payloads.
        candidates = [
            ("POST", f"/chat/{chat_id}/message/send", {"json": {"text": text}}),
            ("POST", f"/chat/{chat_id}/message/send", {"json": {"message": text}}),
            ("POST", f"/chat/{chat_id}/messages", {"json": {"text": text}}),
            ("POST", f"/conversation/{chat_id}/message/send", {"json": {"text": text}}),
            ("POST", "/message/send", {"json": {"chatId": chat_id, "text": text}}),
            ("POST", "/messages", {"json": {"chatId": chat_id, "text": text}}),
        ]
        last: Exception | None = None
        for method, path, kw in candidates:
            try:
                r = self.s.request(method, b + path, timeout=self.timeout, **kw)
                if r.status_code >= 400:
                    continue
                # Some instances return empty 204, some JSON.
                if r.status_code == 204:
                    return {"ok": True, "status": 204, "endpoint": b + path}
                if self._is_json_response(r):
                    return r.json()
                return {"ok": True, "status": r.status_code, "endpoint": b + path, "body": (r.text or '')[:2000]}
            except Exception as e:
                last = e
                continue
        raise RuntimeError(f"Could not send message to chat_id={chat_id}. Last error: {last}")

    # ----------------------
    # Exercises (Aufgaben)
    # ----------------------

    def exercise_list(self, limit: int = 50) -> list[dict]:
        """Best-effort exercise list by scraping the /iserv/exercise HTML page.

        Many IServ instances have an internal API, but it's not stable across versions.
        This implementation avoids hardcoding API routes.
        """
        r = self.s.get(f"{self.base_url}/iserv/exercise", timeout=self.timeout)
        r.raise_for_status()
        t = r.text

        # Discover exercise IDs from links like /iserv/exercise/show/123
        items: list[dict] = []
        seen: set[str] = set()
        for m in re.finditer(r"/iserv/exercise/show/(\d+)", t):
            ex_id = m.group(1)
            if ex_id in seen:
                continue
            seen.add(ex_id)

            # Try to infer a title from nearby anchor tag
            start = max(0, m.start() - 250)
            end = min(len(t), m.end() + 250)
            snippet = t[start:end]
            title = None
            am = re.search(r"<a[^>]+href=[\"'][^\"']*/iserv/exercise/show/%s[^\"']*[\"'][^>]*>(.*?)</a>" % re.escape(ex_id), snippet, re.I | re.S)
            if am:
                title = _strip_tags(am.group(1)).strip()
            if not title:
                title = f"Exercise {ex_id}"

            items.append({"id": int(ex_id), "title": _html.unescape(title)})
            if len(items) >= limit:
                break

        return items

    def exercise_detail(self, exercise_id: int) -> dict:
        r = self.s.get(f"{self.base_url}/iserv/exercise/show/{int(exercise_id)}", timeout=self.timeout)
        r.raise_for_status()
        t = r.text

        # Title
        title = None
        m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.I | re.S)
        if m:
            title = _strip_tags(m.group(1)).strip()
        if not title:
            m = re.search(r"<title>(.*?)</title>", t, re.I | re.S)
            title = _strip_tags(m.group(1)).strip() if m else f"Exercise {exercise_id}"

        # Attachments (best-effort)
        attachments: list[dict] = []
        for href, text in re.findall(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", t, re.I | re.S):
            if "/iserv/exercise/attachment" not in href:
                continue
            url = urljoin(self.base_url + "/", href)
            att_id = None
            mid = re.search(r"/(\d+)(?:\?|$)", href)
            if mid:
                att_id = int(mid.group(1))
            fname = _strip_tags(text).strip() or None
            attachments.append({"id": att_id, "name": fname, "url": url})

        return {
            "id": int(exercise_id),
            "title": _html.unescape(title or ""),
            "csrf": _find_csrf_token(t),
            "attachments": attachments,
            "html": t,
        }

    def exercise_download_attachment(self, url_or_id: str | int, out_dir: str = ".") -> Path:
        """Download an attachment by direct URL or numeric ID (best-effort)."""
        if isinstance(url_or_id, int) or (isinstance(url_or_id, str) and str(url_or_id).isdigit()):
            # try common download route (may differ by IServ version)
            url = f"{self.base_url}/iserv/exercise/attachment/download/{int(url_or_id)}"
        else:
            url = str(url_or_id)
        out_dir_p = Path(out_dir)
        out_dir_p.mkdir(parents=True, exist_ok=True)

        r = self.s.get(url, stream=True, timeout=self.timeout)
        r.raise_for_status()

        # filename from Content-Disposition
        fname = None
        cd = r.headers.get("Content-Disposition") or ""
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd)
        if m:
            fname = _html.unescape(m.group(1))
        if not fname:
            m = re.search(r"filename=\"?([^\";]+)\"?", cd)
            if m:
                fname = _html.unescape(m.group(1))
        if not fname:
            fname = "attachment.bin"

        out_path = out_dir_p / fname
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)
        return out_path

    def exercise_submit(self, exercise_id: int, file_path: str, comment: str | None = None) -> dict:
        """Submit a solution file (HTML-form driven, best-effort).

        Approach:
          1) GET exercise detail page
          2) parse the most likely submission <form> (prefer the one containing a file input)
          3) POST multipart/form-data directly to the form action (no separate fs upload)

        This is significantly more robust across IServ versions than guessing an internal API.
        Returns a dict with request/response debug information.
        """
        detail = self.exercise_detail(exercise_id)
        html_text = detail["html"]

        form = _find_form_for_exercise_submission(html_text)
        if not form:
            raise RuntimeError("Could not find a submission form on the exercise detail page")

        action = (form.get("action") or "").strip() or f"/iserv/exercise/show/{int(exercise_id)}"
        method = (form.get("method") or "post").lower()
        enctype = (form.get("enctype") or "").lower()

        # Build payload from discovered controls
        payload: dict[str, str] = {}
        file_field_name: str | None = None

        for inp in form.get("inputs", []):
            name = (inp.get("name") or "").strip()
            if not name:
                continue
            itype = (inp.get("type") or "text").lower()
            if itype == "file":
                file_field_name = name
                continue
            # Ignore unchecked checkboxes/radios (we can't reliably know checked state)
            if itype in ("checkbox", "radio"):
                continue
            payload.setdefault(name, inp.get("value") or "")

        for ta in form.get("textareas", []):
            name = (ta.get("name") or "").strip()
            if not name:
                continue
            payload.setdefault(name, (ta.get("value") or "").strip())

        for sel in form.get("selects", []):
            name = (sel.get("name") or "").strip()
            if not name:
                continue
            payload.setdefault(name, sel.get("value") or "")

        # CSRF token: if present but empty, fill from page-level token
        if "_token" in payload and not payload.get("_token"):
            payload["_token"] = detail.get("csrf") or ""

        # Add comment if we can locate a suitable field; else, include a generic one.
        if comment:
            # prefer any field that looks like a comment/message
            preferred = None
            for k in payload.keys():
                if re.search(r"comment|message|bemerk|notiz", k, re.I):
                    preferred = k
                    break
            if preferred:
                payload[preferred] = comment
            else:
                payload.setdefault("comment", comment)

        fp = Path(file_path)
        if not fp.exists():
            raise FileNotFoundError(str(fp))

        submit_url = urljoin(self.base_url + "/", action)

        # Decide between multipart or urlencoded
        files = None
        if file_field_name:
            files = {file_field_name: (fp.name, open(fp, "rb"))}
        elif "multipart/form-data" in enctype:
            # enctype suggests a file is expected but we didn't parse the field name
            # still try common field names
            for candidate in ("file", "attachment", "exercise_attachment[file]", "exercise[file]"):
                file_field_name = candidate
                files = {file_field_name: (fp.name, open(fp, "rb"))}
                break

        try:
            if method != "post":
                raise RuntimeError(f"Unsupported form method: {method}")

            if files is not None:
                sub_r = self.s.post(submit_url, data=payload, files=files, timeout=self.timeout, allow_redirects=True)
            else:
                sub_r = self.s.post(submit_url, data=payload, timeout=self.timeout, allow_redirects=True)
            sub_r.raise_for_status()
        finally:
            if files:
                for _, fobj in files.values():
                    try:
                        fobj.close()
                    except Exception:
                        pass

        return {
            "exercise_id": int(exercise_id),
            "form_action": submit_url,
            "form_method": method,
            "form_enctype": enctype,
            "file_field": file_field_name,
            "form_payload_keys": sorted(payload.keys()),
            "submit_status": sub_r.status_code,
            "submit_url_final": str(sub_r.url),
            "submit_text_head": sub_r.text[:5000],
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=os.environ.get("ISERV_PROFILE"))

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mail-unread")
    p_list = sub.add_parser("mail-list")
    p_list.add_argument("--folder", default="INBOX")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--offset", type=int, default=0)

    p_last = sub.add_parser("mail-last")
    p_last.add_argument("--n", type=int, default=3)

    p_send = sub.add_parser("mail-send")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body", required=True)

    p_reply = sub.add_parser("mail-reply")
    p_reply.add_argument("--uid", type=int, required=True)
    p_reply.add_argument("--body", required=True)

    sub.add_parser("calendar-upcoming")
    p_files = sub.add_parser("files-list")
    p_files.add_argument("--path", default="")

    p_fd = sub.add_parser("files-download")
    p_fd.add_argument("--path", required=True, help="Remote file path")
    p_fd.add_argument("--out-dir", default="./downloads")

    p_fs = sub.add_parser("files-search")
    p_fs.add_argument("--query", required=True, help="Substring to search for (case-insensitive)")
    p_fs.add_argument("--start-dir", default="/Files")
    p_fs.add_argument("--max-results", type=int, default=50)
    p_fs.add_argument("--max-depth", type=int, default=6)

    p_fu = sub.add_parser("files-upload")
    p_fu.add_argument("--file", required=True, help="Local file path")
    p_fu.add_argument("--dest-dir", default="/Files", help="Remote destination directory")
    p_fu.add_argument("--chunk-size", type=int, default=None, help="Chunk size bytes for FS chunked upload")

    p_mkdir = sub.add_parser("files-mkdir")
    p_mkdir.add_argument("--path", required=True, help="Remote folder path to create")

    p_ren = sub.add_parser("files-rename")
    p_ren.add_argument("--src", required=True, help="Remote source path")
    p_ren.add_argument("--dest", required=True, help="Remote destination path")

    p_del = sub.add_parser("files-delete")
    p_del.add_argument("--path", required=True, help="Remote path to delete")

    # Messenger
    sub.add_parser("messenger-chats")
    p_mm = sub.add_parser("messenger-messages")
    p_mm.add_argument("--chat-id", required=True)
    p_mm.add_argument("--limit", type=int, default=50)
    p_mm.add_argument("--offset", type=int, default=0)

    p_ms = sub.add_parser("messenger-send")
    p_ms.add_argument("--chat-id", required=True)
    p_ms.add_argument("--text", required=True)

    # exercises
    p_ex_list = sub.add_parser("exercise-list")
    p_ex_list.add_argument("--limit", type=int, default=50)

    p_ex_det = sub.add_parser("exercise-detail")
    p_ex_det.add_argument("--id", type=int, required=True)
    p_ex_det.add_argument("--download-dir", default=None, help="If set, download all discovered attachments to this directory")

    p_ex_sub = sub.add_parser("exercise-submit")
    p_ex_sub.add_argument("--id", type=int, required=True)
    p_ex_sub.add_argument("--file", required=True)
    p_ex_sub.add_argument("--comment", default="")

    args = ap.parse_args()

    profile = (args.profile or "").strip() or None
    base_url = _profile_env(profile, "BASE_URL")
    user = _profile_env(profile, "USER")
    password = _profile_env(profile, "PASS")

    c = IServClient(base_url=base_url, user=user, password=password)
    # If a command targets a specific app, start login there so auth flow sets correct redirect chain
    start_path = "/iserv/"
    if args.cmd.startswith("messenger-"):
        start_path = "/iserv/messenger/"
    elif args.cmd.startswith("exercise-"):
        start_path = "/iserv/exercise"
    elif args.cmd.startswith("files-"):
        start_path = "/iserv/file/-/"
    c.login(start_path=start_path)

    if args.cmd == "mail-unread":
        print(c.mail_unread())
    elif args.cmd == "mail-list":
        data = c.mail_list(folder=args.folder, limit=args.limit, offset=args.offset)
        for i, m in enumerate(data.get('data', [])[: args.limit], 1):
            frm = (m.get('from') or {}).get('name') or ''
            subj = m.get('subject') or ''
            date = m.get('date') or ''
            uid = m.get('uid')
            print(f"{i}. [{uid}] {date} | {frm} | {subj}")
    elif args.cmd == "mail-last":
        items = c.mail_last(n=args.n)
        for i, m in enumerate(items, 1):
            print(f"\n#{i}")
            print(f"From: {m['from']}")
            print(f"Date: {m['date']}")
            print(f"Subject: {m['subject']}")
            ex = (m['excerpt'] or '').strip()
            if ex:
                print(f"\n{ex}\n")
    elif args.cmd == "mail-send":
        c.mail_send(to_addr=args.to, subject=args.subject, body=args.body)
        print("sent")
    elif args.cmd == "mail-reply":
        c.mail_reply(uid=args.uid, body=args.body)
        print("sent")
    elif args.cmd == "calendar-upcoming":
        print(c.calendar_upcoming())
    elif args.cmd == "files-list":
        print(c.files_list(path=args.path))
    elif args.cmd == "files-download":
        outp = c.files_download(path=args.path, out_dir=args.out_dir)
        print(str(outp))
    elif args.cmd == "files-search":
        res = c.files_search(query=args.query, start_dir=args.start_dir, max_results=args.max_results, max_depth=args.max_depth)
        for i, m in enumerate(res, 1):
            print(f"{i}. [{m.get('type')}] {m.get('path') or ''} ({m.get('name')})")
    elif args.cmd == "files-upload":
        print(c.files_upload(local_file=args.file, dest_dir=args.dest_dir, chunk_size=args.chunk_size))
    elif args.cmd == "files-mkdir":
        print(c.files_mkdir(path=args.path))
    elif args.cmd == "files-rename":
        print(c.files_rename(src_path=args.src, dest_path=args.dest))
    elif args.cmd == "files-delete":
        print(c.files_delete(path=args.path))
    elif args.cmd == "messenger-chats":
        data = c.messenger_chats()
        # best-effort pretty output
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
            items = data['data']
        elif isinstance(data, list):
            items = data
        else:
            items = None
        if items is None:
            print(data)
        else:
            for i, ch in enumerate(items, 1):
                cid = ch.get('id') or ch.get('uuid') or ch.get('chatId')
                title = ch.get('title') or ch.get('name') or ch.get('subject') or ''
                last = ch.get('lastMessage') or ch.get('last_message') or {}
                last_txt = last.get('text') if isinstance(last, dict) else ''
                print(f"{i}. [{cid}] {title} {('- ' + last_txt) if last_txt else ''}")
    elif args.cmd == "messenger-messages":
        data = c.messenger_messages(chat_id=args.chat_id, limit=args.limit, offset=args.offset)
        # Print most useful subset if response looks like a list
        items = None
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
            items = data['data']
        elif isinstance(data, list):
            items = data
        if items is None:
            print(data)
        else:
            for m in items:
                mid = m.get('id') or m.get('uuid')
                author = (m.get('author') or {}).get('name') if isinstance(m.get('author'), dict) else (m.get('author') or '')
                ts = m.get('createdAt') or m.get('created_at') or m.get('date') or ''
                text = m.get('text') or m.get('message') or ''
                print(f"[{ts}] {author}: {text} ({mid})")
    elif args.cmd == "messenger-send":
        res = c.messenger_send(chat_id=args.chat_id, text=args.text)
        print(res)
    elif args.cmd == "exercise-list":
        items = c.exercise_list(limit=args.limit)
        for i, ex in enumerate(items, 1):
            print(f"{i}. [{ex['id']}] {ex.get('title','')}")
    elif args.cmd == "exercise-detail":
        d = c.exercise_detail(exercise_id=args.id)
        print(f"[{d['id']}] {d.get('title','')}")
        if d.get('attachments'):
            print("Attachments:")
            for a in d['attachments']:
                aid = a.get('id')
                nm = a.get('name') or ''
                url = a.get('url') or ''
                print(f"- {aid if aid is not None else '?'} | {nm} | {url}")
        else:
            print("Attachments: (none found)")

        if args.download_dir:
            for a in d.get('attachments', []):
                try:
                    outp = c.exercise_download_attachment(a.get('url') or a.get('id'), out_dir=args.download_dir)
                    print(f"downloaded: {outp}")
                except Exception as e:
                    print(f"download failed for {a}: {e}", file=sys.stderr)
    elif args.cmd == "exercise-submit":
        res = c.exercise_submit(exercise_id=args.id, file_path=args.file, comment=(args.comment or None))
        # Print a short, useful summary
        print(f"upload_status={res.get('upload_status')} submit_status={res.get('submit_status')}")
        print(f"submit_url_final={res.get('submit_url_final')}")
        if res.get('upload_json') is not None:
            print(f"upload_json={res['upload_json']}")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
