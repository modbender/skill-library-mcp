#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""End-to-end pipeline for Chaoxing Xuexitong homework:

- fetch questions from doHomeWork URL
- generate editable answers template (with stems)
- (after user edits) render handwritten PNGs on grid background
- upload PNGs to Chaoxing cldisk (uploadNoticeFile)
- write HTML <img> answers.json
- temp-save (暂存) to homework

Design goals:
- safe by default: only temp-save, never final submit unless user runs xuexitong_submit.py submit separately
- decouple the "user edit" step by writing a JSON file on disk

Files produced:
- work.json (questions)
- answers_text.json (list with title/stem/answer)
- outputs_hw_bg_auto/ (rendered PNGs)
- uploads.json (png->url)
- answers_html.json (qid->html)

Usage (recommended):
1) init:
   .venv/bin/python scripts/xuexitong_hw_pipeline.py init --dohomework-url "..." --outdir run1
2) edit run1/answers_text.json (fill in each item.answer)
3) run:
   .venv/bin/python scripts/xuexitong_hw_pipeline.py run --dohomework-url "..." --rundir run1
"""

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

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
    raise SystemExit(msg)


def read_cookie(path: str) -> dict:
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
    if len(d) < 2:
        die("cookie parsed too short")
    return d


def make_session(cookies: dict) -> requests.Session:
    s = requests.Session()
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    s.headers.update(
        {
            "User-Agent": DEFAULT_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://mooc1-api.chaoxing.com/work/stu-work",
            # Some endpoints behave differently if cookies are not also present as a raw header
            "Cookie": cookie_header,
        }
    )
    # populate cookie jar (best-effort)
    for k, v in cookies.items():
        s.cookies.set(k, v, domain=".chaoxing.com")
    return s


def fetch_index(s: requests.Session, base_url: str, idx: int) -> str:
    # Reuse logic from xuexitong_submit.py without importing to keep this file standalone.
    from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

    u = urlparse(base_url)
    q = parse_qs(u.query)
    q["index"] = [str(idx)]
    if "knowledgeid" not in q and "knowledgeId" not in q:
        q["knowledgeid"] = ["0"]
    new_q = urlencode({k: v[0] for k, v in q.items()}, doseq=False)
    u2 = u._replace(query=new_q)
    url = urlunparse(u2)

    r = s.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def extract_hidden_fields(html: str) -> dict:
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


def fetch_work(s: requests.Session, dohomework_url: str, max_index: int = 40) -> dict:
    questions = []
    seen = set()
    base_fields = None
    dup_streak = 0

    for idx in range(max_index):
        html = fetch_index(s, dohomework_url, idx)
        if base_fields is None:
            base_fields = extract_hidden_fields(html)
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

    return {
        "dohomeworkUrl": dohomework_url,
        "questions": questions,
        "baseFields": base_fields or {},
        "fetchedAt": int(time.time()),
    }


def make_answers_text(work: dict) -> list:
    out = []
    for i, q in enumerate(work.get("questions", []), start=1):
        qid = str(q.get("questionId") or "")
        stem = str(q.get("stem") or "")
        title = f"第{i}题"
        if stem:
            title += " " + stem
        out.append(
            {
                "questionId": qid,
                "title": title,
                "stem": stem,
                "answer": "",  # user fills
            }
        )
    return out


def render_handwrite(*, answers_text_path: Path, outdir: Path):
    ws = Path(__file__).resolve().parents[3]  # workspace
    hw_dir = ws / "HandWrite"
    hw_py = hw_dir / ".venv" / "bin" / "python"
    render_script = Path(__file__).resolve().parent / "render_hw_bg_from_answers_json.py"

    font_path = hw_dir / "ttf_library" / "未知手写体_1.ttf"
    bg_path = hw_dir / "assets" / "grid.jpg"

    if not hw_py.exists():
        die(f"HandWrite venv python not found: {hw_py}")
    if not render_script.exists():
        die(f"render script not found: {render_script}")
    if not font_path.exists():
        die(f"font not found: {font_path}")
    if not bg_path.exists():
        die(f"bg image not found: {bg_path}")

    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(hw_py),
        str(render_script),
        "--answers-json",
        str(answers_text_path),
        "--outdir",
        str(outdir),
        "--font",
        str(font_path),
        "--bg",
        str(bg_path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr or p.stdout)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"raw": p.stdout}


def upload_notice_file(s: requests.Session, file_path: Path) -> dict:
    url = "http://notice.chaoxing.com/pc/files/uploadNoticeFile"
    with open(file_path, "rb") as f:
        files = {"attrFile": (f"{int(time.time()*1000)}{file_path.suffix}", f)}
        r = s.post(url, files=files, timeout=30)
    r.raise_for_status()
    j = r.json()
    if not j.get("status"):
        return {"ok": False, "resp": j}
    # stable url without query
    u = (j.get("url") or "").split("?")[0]
    return {"ok": True, "url": u, "raw": j}


def build_answers_html(work: dict, uploads: dict) -> dict:
    """Return mapping: questionId -> html string with <img> tags.

    uploads keys: filename -> url
    expected rendered filenames: qid_<qid>_pN.png
    """

    by_qid = {}
    for fname, u in uploads.items():
        m = re.match(r"qid_(\d+)_p(\d+)\.png$", fname)
        if not m:
            continue
        qid = m.group(1)
        page = int(m.group(2))
        by_qid.setdefault(qid, []).append((page, u))

    out = {}
    for q in work.get("questions", []):
        qid = str(q.get("questionId") or "")
        pages = sorted(by_qid.get(qid, []), key=lambda t: t[0])
        if not pages:
            out[qid] = ""
            continue
        html = "答案见图片：<br/>" + "<br/>".join(
            [f'<img src="{u}" style="max-width:100%;height:auto;" />' for _, u in pages]
        )
        out[qid] = html
    return out


def temp_save_homework(*, dohomework_url: str, work_json_path: Path, answers_html_path: Path, out_result: Path):
    # call existing submit script to ensure per-question hidden fields are handled
    skill_dir = Path(__file__).resolve().parents[1]
    submit_py = skill_dir / "scripts" / "xuexitong_submit.py"
    venv_py = skill_dir / ".venv" / "bin" / "python"

    cmd = [
        str(venv_py),
        str(submit_py),
        "save",
        "--dohomework-url",
        dohomework_url,
        "--answers",
        str(answers_html_path),
        "--work-json",
        str(work_json_path),
        "--out",
        str(out_result),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr or p.stdout)
    return p.stdout


def cmd_init(args):
    cookies = read_cookie(args.cookie)
    s = make_session(cookies)

    rundir = Path(args.outdir)
    rundir.mkdir(parents=True, exist_ok=True)

    work = fetch_work(s, args.dohomework_url)
    work_path = rundir / "work.json"
    work_path.write_text(json.dumps(work, ensure_ascii=False, indent=2), encoding="utf-8")

    answers_text = make_answers_text(work)
    answers_text_path = rundir / "answers_text.json"
    answers_text_path.write_text(json.dumps(answers_text, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "rundir": str(rundir.resolve()),
        "work": str(work_path),
        "answers_text": str(answers_text_path),
        "questionCount": len(work.get("questions", [])),
        "next": "Edit answers_text.json (fill item.answer), then run: cmd run --rundir <dir>"
    }, ensure_ascii=False, indent=2))


def cmd_run(args):
    cookies = read_cookie(args.cookie)
    s = make_session(cookies)

    rundir = Path(args.rundir)
    work_path = rundir / "work.json"
    answers_text_path = rundir / "answers_text.json"
    if not work_path.exists() or not answers_text_path.exists():
        die("rundir missing work.json or answers_text.json; run init first")

    work = json.loads(work_path.read_text(encoding="utf-8"))

    # render
    render_outdir = rundir / "outputs_hw_bg_auto"
    render_info = render_handwrite(answers_text_path=answers_text_path, outdir=render_outdir)

    # upload all rendered pngs
    uploads = {}
    for p in sorted(render_outdir.glob("qid_*_p*.png")):
        up = upload_notice_file(s, p)
        if not up.get("ok"):
            die(f"upload failed: {p.name} {up}")
        uploads[p.name] = up["url"]

    uploads_path = rundir / "uploads.json"
    uploads_path.write_text(json.dumps(uploads, ensure_ascii=False, indent=2), encoding="utf-8")

    # build answers html
    answers_html = build_answers_html(work, uploads)
    answers_html_path = rundir / "answers_html.json"
    answers_html_path.write_text(json.dumps(answers_html, ensure_ascii=False, indent=2), encoding="utf-8")

    # temp-save
    result_path = rundir / "save_result.json"
    out_text = temp_save_homework(
        dohomework_url=args.dohomework_url,
        work_json_path=work_path,
        answers_html_path=answers_html_path,
        out_result=result_path,
    )

    print(json.dumps({
        "rundir": str(rundir.resolve()),
        "render": render_info,
        "uploads": str(uploads_path),
        "answers_html": str(answers_html_path),
        "save_result": str(result_path),
        "save_stdout": out_text.strip(),
        "note": "Temp-saved only. Review in Xuexitong. Final submit still requires xuexitong_submit.py submit --confirm"
    }, ensure_ascii=False, indent=2))


def main():
    maybe_check_for_update()

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cookie",
        default=os.path.expanduser("~/.openclaw/credentials/xuexitong_cookie.txt"),
        help="cookie file path",
    )

    sub = ap.add_subparsers(dest="cmd")

    sp = sub.add_parser("init", help="fetch questions and create editable answers_text.json")
    sp.add_argument("--dohomework-url", required=True)
    sp.add_argument("--outdir", required=True, help="rundir path")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("run", help="render->upload->temp-save using answers_text.json in rundir")
    sp.add_argument("--dohomework-url", required=True)
    sp.add_argument("--rundir", required=True)
    sp.set_defaults(func=cmd_run)

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
