#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

import requests

try:
    from update_check import maybe_check_for_update
except Exception:
    def maybe_check_for_update():
        return

SKIP_COOKIE_KEYS = {
    "path",
    "domain",
    "expires",
    "max-age",
    "samesite",
    "secure",
    "httponly",
    "version",
    "priority",
}

DEFAULT_UA = (
    "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36"
)


def die(msg: str, code: int = 2):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def read_cookie(path: str) -> str:
    if not os.path.exists(path):
        die(f"cookie file not found: {path}")
    raw = open(path, "r", encoding="utf-8").read().strip()
    if not raw:
        die("cookie file is empty")

    parts = re.split(r"[;\n]", raw)
    d = {}
    for p in parts:
        p = p.strip()
        if not p or "=" not in p:
            continue
        k, v = p.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k.lower() in SKIP_COOKIE_KEYS:
            continue
        d[k] = v

    cookie = "; ".join([f"{k}={v}" for k, v in d.items()])
    if len(cookie) < 10:
        die("cookie header too short; likely parsing failed")
    return cookie


def session(cookie_header: str, ua: str = DEFAULT_UA) -> requests.Session:
    """Create a session that sends cookies as a CookieJar (more reliable than raw Cookie header)."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://mooc1-api.chaoxing.com/work/stu-work",
            # Many Chaoxing endpoints behave differently depending on whether cookies are sent
            # as a raw header vs cookie jar. We set BOTH for maximum compatibility.
            "Cookie": cookie_header,
        }
    )

    # Populate cookie jar
    for kv in cookie_header.split(";"):
        kv = kv.strip()
        if not kv or "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        s.cookies.set(k, v, domain=".chaoxing.com")

    return s


def cmd_list(args):
    s = session(read_cookie(args.cookie))
    url = "https://mooc1-api.chaoxing.com/work/stu-work"
    r = s.get(url, timeout=30)
    r.raise_for_status()
    html = r.text
    if args.save_html:
        open(args.save_html, "w", encoding="utf-8").write(html)

    links = re.findall(r"https?://[^\"\'<>\s]+", html)
    # keep task links
    task_links = [
        l
        for l in links
        if "mooc1-api.chaoxing.com/android/mtaskmsgspecial" in l
        and "type=work" in l
        and "taskrefId=" in l
    ]
    # de-dupe keep order
    seen = set()
    out = []
    for l in task_links:
        if l in seen:
            continue
        seen.add(l)
        out.append(l)

    print(json.dumps({"count": len(out), "tasks": out}, ensure_ascii=False, indent=2))


def resolve_mtask_to_dohomework(s: requests.Session, task_url: str, sleep_ms: int = 0) -> str:
    if sleep_ms:
        time.sleep(sleep_ms / 1000)

    r = s.get(task_url, timeout=30)
    r.raise_for_status()
    html = r.text

    # Find doHomeWork URL inside the page
    # pattern in our earlier page: '/work/phone/doHomeWork?courseId=...&workId=...'
    m = re.search(r"/work/phone/doHomeWork\?[^\"\']+", html)
    if not m:
        # some pages use full origin + _CP_ concatenation; try looser regex
        m = re.search(r"doHomeWork\?courseId=\d+[^\"\']+", html)
    if not m:
        # dump hint
        die("could not find doHomeWork URL in task page; save HTML and inspect")

    path_qs = m.group(0)
    if not path_qs.startswith("/mooc-ans"):
        # task page uses _CP_='/mooc-ans'
        if path_qs.startswith("/work/"):
            path_qs = "/mooc-ans" + path_qs
        elif path_qs.startswith("doHomeWork"):
            path_qs = "/mooc-ans/work/phone/" + path_qs

    do_url = "https://mooc1-api.chaoxing.com" + path_qs
    return do_url


def cmd_resolve(args):
    s = session(read_cookie(args.cookie))
    do_url = resolve_mtask_to_dohomework(s, args.task_url, sleep_ms=args.sleep_ms)
    print(do_url)


def fetch_index(s: requests.Session, base_url: str, idx: int, sleep_ms: int = 0) -> str:
    if sleep_ms:
        time.sleep(sleep_ms / 1000)

    u = urlparse(base_url)
    q = parse_qs(u.query)
    q["index"] = [str(idx)]
    # some pages require explicit knowledgeid
    if "knowledgeid" not in q and "knowledgeId" not in q:
        q["knowledgeid"] = ["0"]
    new_q = urlencode({k: v[0] for k, v in q.items()}, doseq=False)
    u2 = u._replace(query=new_q)
    url = urlunparse(u2)

    r = s.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def extract_form_fields(html: str) -> dict:
    fields = {}
    for m in re.finditer(r"<input[^>]+type=\"hidden\"[^>]+>", html):
        tag = m.group(0)
        nm = re.search(r"name=\"([^\"]+)\"", tag)
        if not nm:
            continue
        name = nm.group(1)
        val = re.search(r"value=\"([^\"]*)\"", tag)
        fields[name] = val.group(1) if val else ""
    return fields


def parse_question(html: str) -> dict:
    qid_m = re.search(r"id=\"questionId\"[^>]+value=\"(\d+)\"", html)
    qid = qid_m.group(1) if qid_m else None

    stem = ""
    stem_m = re.search(r"<div class=\"ans-cc timuStyle[\s\S]*?<p>([\s\S]*?)</p>", html)
    if stem_m:
        stem = re.sub(r"<[^>]+>", "", stem_m.group(1)).strip()

    qtype = None
    score = None
    if qid:
        m = re.search(rf"name=\"type{qid}\" value=\"(\d+)\"", html)
        if m:
            qtype = m.group(1)
        m = re.search(rf"name=\"score{qid}\" value=\"([^\"]+)\"", html)
        if m:
            score = m.group(1)

    return {"questionId": qid, "type": qtype, "score": score, "stem": stem}


def cmd_fetch(args):
    s = session(read_cookie(args.cookie))

    questions = []
    seen = set()
    base_fields = None

    dup_streak = 0
    for idx in range(0, args.max_index):
        html = fetch_index(s, args.dohomework_url, idx, sleep_ms=args.sleep_ms)
        if base_fields is None:
            base_fields = extract_form_fields(html)
        q = parse_question(html)
        qid = q.get("questionId")
        if not qid:
            break
        if qid in seen:
            dup_streak += 1
            if dup_streak >= 2:
                break
            continue
        dup_streak = 0
        seen.add(qid)
        questions.append(q)

    out = {
        "dohomeworkUrl": args.dohomework_url,
        "questions": questions,
        "baseFields": base_fields or {},
        "fetchedAt": int(time.time()),
    }
    open(args.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"saved {args.out} ({len(questions)} questions)")


def cmd_template(args):
    data = json.load(open(args.work_json, encoding="utf-8"))
    tmpl = {q["questionId"]: "" for q in data.get("questions", []) if q.get("questionId")}
    open(args.out, "w", encoding="utf-8").write(json.dumps(tmpl, ensure_ascii=False, indent=2))
    print(f"wrote {args.out} ({len(tmpl)} items)")


def submit_payload(s: requests.Session, payload: dict, temp_save: bool, sleep_ms: int = 0) -> dict:
    if sleep_ms:
        time.sleep(sleep_ms / 1000)

    url = (
        "https://mooc1-api.chaoxing.com/mooc-ans/work/phone/doNormalHomeWorkSubmit"
        + f"?tempSave={'true' if temp_save else 'false'}"
    )
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json,*/*",
    }
    r = s.post(url, data=payload, headers=headers, timeout=30)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"raw": r.text}


def cmd_save_or_submit(args, temp_save: bool):
    if (not temp_save) and (not args.confirm):
        die("refusing to submit without --confirm")

    work = json.load(open(args.work_json, encoding="utf-8")) if args.work_json else None

    s = session(read_cookie(args.cookie))

    answers = json.load(open(args.answers, encoding="utf-8"))
    want_qids = [str(k) for k in answers.keys()]

    # IMPORTANT: Chaoxing embeds per-question hidden fields (type/score/etc.) on each index page.
    # Using only index=0 fields will cause later questions to submit as blank.
    qid_fields: dict[str, dict] = {}

    if work and work.get("questions"):
        # Assume work.json questions order matches index=0..N traversal.
        for idx, q in enumerate(work.get("questions", [])):
            qid = str(q.get("questionId") or "")
            if not qid or qid not in want_qids:
                continue
            html = fetch_index(s, args.dohomework_url, idx, sleep_ms=args.sleep_ms)
            qid_fields[qid] = extract_form_fields(html)

    # Fallback: brute-force fetch indices until all qids are found.
    if len(qid_fields) < len(want_qids):
        seen = set(qid_fields.keys())
        for idx in range(0, 30):
            html = fetch_index(s, args.dohomework_url, idx, sleep_ms=args.sleep_ms)
            q = parse_question(html)
            qid = str(q.get("questionId") or "")
            if not qid or qid in seen or qid not in want_qids:
                continue
            qid_fields[qid] = extract_form_fields(html)
            seen.add(qid)
            if len(seen) >= len(want_qids):
                break

    missing = [q for q in want_qids if q not in qid_fields]
    if missing:
        die(f"could not fetch per-question hidden fields for qids: {missing}")

    results = {}
    for qid, ans in answers.items():
        qid = str(qid)
        ans = ans or ""
        payload = dict(qid_fields[qid])
        payload["tempSave"] = "true" if temp_save else "false"
        payload[f"answer{qid}"] = ans
        resp = submit_payload(s, payload, temp_save=temp_save, sleep_ms=args.sleep_ms)
        results[qid] = resp
        ok = resp.get("status") is True
        print(f"{('SAVE' if temp_save else 'SUBMIT')} qid={qid} status={ok} msg={resp.get('msg')}")

    if args.out:
        open(args.out, "w", encoding="utf-8").write(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"wrote {args.out}")


def main():
    maybe_check_for_update()

    p = argparse.ArgumentParser()
    p.set_defaults(func=None)

    p.add_argument(
        "--cookie",
        default=os.path.expanduser("~/.openclaw/credentials/xuexitong_cookie.txt"),
        help="cookie file path",
    )

    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("list", help="list homework task entries from stu-work")
    sp.add_argument("--save-html", default="", help="optional path to save stu-work html")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("resolve", help="resolve mtaskmsgspecial URL to doHomeWork URL")
    sp.add_argument("--task-url", required=True)
    sp.add_argument("--sleep-ms", type=int, default=0)
    sp.set_defaults(func=cmd_resolve)

    sp = sub.add_parser("fetch", help="fetch questions by iterating index=0..")
    sp.add_argument("--dohomework-url", required=True)
    sp.add_argument("--out", default="work.json")
    sp.add_argument("--max-index", type=int, default=20)
    sp.add_argument("--sleep-ms", type=int, default=0)
    sp.set_defaults(func=cmd_fetch)

    sp = sub.add_parser("template", help="generate answers template JSON from work.json")
    sp.add_argument("--work-json", required=True)
    sp.add_argument("--out", default="answers.json")
    sp.set_defaults(func=cmd_template)

    for name, temp in [("save", True), ("submit", False)]:
        sp = sub.add_parser(name, help=("temp save" if temp else "final submit"))
        sp.add_argument("--dohomework-url", required=True)
        sp.add_argument("--answers", required=True)
        sp.add_argument("--work-json", default="", help="optional; use baseFields from this file")
        sp.add_argument("--out", default="", help="optional output json results")
        sp.add_argument("--sleep-ms", type=int, default=0)
        sp.add_argument("--confirm", action="store_true", help="required for submit")
        sp.set_defaults(func=(lambda a, t=temp: cmd_save_or_submit(a, t)))

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
