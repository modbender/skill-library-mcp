#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


def split_items(text: str):
    parts = re.split(r"\n###\s+", "\n" + text)
    out = []
    for p in parts[1:]:
        out.append("### " + p)
    return out


def find_summary(item_text: str):
    for ln in item_text.splitlines():
        low = ln.lower()
        if "summary" in low:
            if "：" in ln:
                return ln.split("：", 1)[1].strip()
            if ":" in ln:
                return ln.split(":", 1)[1].strip()
    return ""


def find_comment_lines(item_text: str):
    lines = []
    for ln in item_text.splitlines():
        s = ln.strip()
        if (
            s.startswith("- @")
            or s.startswith("-  @")
            or s.startswith("- insufficient comments")
        ):
            lines.append(s)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--language", default="zh")
    ap.add_argument("--zh-summary-min", type=int, default=300)
    ap.add_argument("--zh-comment-min", type=int, default=80)
    ap.add_argument("--short-marker", default="source is short / info limited")
    args = ap.parse_args()

    txt = Path(args.report).read_text(encoding="utf-8")
    items = split_items(txt)
    if not items:
        print("FAIL: no items found")
        sys.exit(2)

    errors = []
    short_markers = [m for m in [args.short_marker] if m]

    if args.language.startswith("zh"):
        for idx, it in enumerate(items, 1):
            summary = find_summary(it)
            if not summary:
                errors.append(f"item {idx}: missing summary")
            elif len(summary) < args.zh_summary_min and not any(m in summary for m in short_markers):
                errors.append(f"item {idx}: summary too short ({len(summary)}<{args.zh_summary_min})")

            c_lines = find_comment_lines(it)
            for j, c in enumerate(c_lines, 1):
                if c.startswith("- insufficient comments"):
                    continue
                body = c.split("：", 1)[1].strip() if "：" in c else c
                if len(body) < args.zh_comment_min and not any(m in body for m in short_markers):
                    errors.append(
                        f"item {idx} comment {j}: too short ({len(body)}<{args.zh_comment_min})"
                    )

    if errors:
        print("FAIL")
        for e in errors:
            print("-", e)
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
