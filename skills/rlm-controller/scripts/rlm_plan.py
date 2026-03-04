#!/usr/bin/env python3
"""Suggest a minimal RLM action plan.
Heuristic: extract keywords from goal, search ctx for them, then propose slices.
Outputs JSON with proposed slices.
"""
import argparse, json, os, re, sys
from collections import Counter
from rlm_path import validate_path as _validate_path

def read_text(path):
    rp = _validate_path(path)
    with open(rp, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def keywords(goal):
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", goal.lower())
    stop = set(["the","and","for","with","from","this","that","have","will","should","can","into","about","where","when","what","your","you","are","use","using","into","over","under","goal","task"])
    words = [w for w in words if w not in stop]
    return [w for w,_ in Counter(words).most_common(8)]

def find_spans(text, kw, max_hits=50):
    spans = []
    for m in re.finditer(re.escape(kw), text, flags=re.IGNORECASE):
        spans.append((m.start(), m.end()))
        if len(spans) >= max_hits: break
    return spans

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ctx', required=True)
    p.add_argument('--goal', required=True)
    p.add_argument('--window', type=int, default=2000)
    args = p.parse_args()

    text = read_text(args.ctx)
    kws = keywords(args.goal)
    slices = []
    for kw in kws:
        for (s,e) in find_spans(text, kw):
            start = max(0, s - args.window)
            end = min(len(text), e + args.window)
            slices.append({"start": start, "end": end, "kw": kw})
    # de-dup similar slices
    dedup = []
    for sl in sorted(slices, key=lambda x: x["start"]):
        if not dedup or sl["start"] > dedup[-1]["end"]:
            dedup.append(sl)
        else:
            dedup[-1]["end"] = max(dedup[-1]["end"], sl["end"])
    print(json.dumps({"keywords": kws, "slices": dedup}, indent=2))

if __name__ == '__main__':
    main()
