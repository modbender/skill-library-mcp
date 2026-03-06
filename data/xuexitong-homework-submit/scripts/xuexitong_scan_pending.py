#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scan Chaoxing Xuexitong homework list and report likely-unsubmitted items.

Goal
- Find assignments that are likely *not submitted* (未交卷) and still writable.
- Heuristic-based: Chaoxing pages vary; we combine URL params + HTML signals.

What it does
1) scripts/xuexitong_submit.py list -> task URLs
2) resolve each task URL -> doHomeWork URL
3) For each doHomeWork:
   - Fetch index=0 page
   - Determine whether it looks submitted (已交/得分/已批阅)
   - Iterate questions and check if answer<qid> hidden inputs are all empty

Output
- JSON list of candidates.

Notes
- "New + unwritten" is defined as: has questions AND all answers empty AND page contains submit/交卷 keywords.
- resolve failures are recorded.
"""

import argparse
import json
import os
import re
import subprocess
from urllib.parse import parse_qs, urlparse

from xuexitong_submit import read_cookie, session, fetch_index, parse_question

try:
    from update_check import maybe_check_for_update
except Exception:
    def maybe_check_for_update():
        return


RE_SUBMITTED = re.compile(r"(已\s*(交|提交)|已交卷|交卷成功|已批阅|得分|分数)")
RE_CAN_SUBMIT = re.compile(r"(交卷|提交)")


def run_submit_py(args: list[str]) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    py = os.path.join(here, "xuexitong_submit.py")
    vpy = os.path.join(os.path.dirname(here), ".venv", "bin", "python")
    cmd = [vpy, py] + args

    # Avoid repeated GitHub checks for each subprocess call in scan flow.
    env = dict(os.environ)
    env["XUEXITONG_SKIP_UPDATE_CHECK"] = "1"

    return subprocess.check_output(cmd, env=env).decode("utf-8")


def main():
    maybe_check_for_update()

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cookie",
        default=os.path.expanduser("~/.openclaw/credentials/xuexitong_cookie.txt"),
        help="cookie file path",
    )
    ap.add_argument("--limit", type=int, default=50, help="max tasks to scan")
    ap.add_argument("--max-index", type=int, default=20, help="max question pages to scan per work")
    ap.add_argument("--save-resolve-failures", default="", help="optional path to save resolve-failure task urls")
    ap.add_argument("--out", default="", help="optional output json file")
    args = ap.parse_args()

    tasks = json.loads(run_submit_py(["list"]))["tasks"]
    tasks = tasks[: args.limit]

    resolved = []
    resolve_failures = []
    seen = set()
    for t in tasks:
        try:
            do = run_submit_py(["resolve", "--task-url", t]).strip()
        except Exception:
            resolve_failures.append(t)
            continue
        q = parse_qs(urlparse(do).query)
        work_id = q.get("workId", [None])[0]
        if not work_id or work_id in seen:
            continue
        seen.add(work_id)
        resolved.append({"workId": work_id, "dohomeworkUrl": do, "taskUrl": t})

    if args.save_resolve_failures:
        open(args.save_resolve_failures, "w", encoding="utf-8").write(
            "\n".join(resolve_failures) + "\n"
        )

    s = session(read_cookie(args.cookie))

    candidates = []
    for item in resolved:
        do = item["dohomeworkUrl"]
        try:
            r = s.get(do, timeout=25)
            r.raise_for_status()
            html0 = r.text
        except Exception:
            continue

        submitted = bool(RE_SUBMITTED.search(html0))
        can_submit = bool(RE_CAN_SUBMIT.search(html0))
        if submitted:
            continue

        total = 0
        filled = 0
        seen_q = set()
        dup = 0
        for idx in range(args.max_index):
            html = fetch_index(s, do, idx)
            q = parse_question(html)
            qid = q.get("questionId")
            if not qid:
                break
            if qid in seen_q:
                dup += 1
                if dup >= 2:
                    break
                continue
            dup = 0
            seen_q.add(qid)
            total += 1

            # hidden input answer<qid> value
            m = re.search(rf'name="answer{qid}"\s+value="([^"]*)"', html)
            val = m.group(1) if m else ""
            if val and val.strip():
                filled += 1

        if total > 0 and filled == 0 and can_submit:
            candidates.append({
                "workId": item["workId"],
                "questions": total,
                "filled": filled,
                "dohomeworkUrl": do,
                "taskUrl": item["taskUrl"],
            })

    out = {
        "count": len(candidates),
        "candidates": candidates,
        "resolveFailures": resolve_failures,
        "scanned": len(resolved),
        "taskLimit": args.limit,
    }

    if args.out:
        open(args.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
