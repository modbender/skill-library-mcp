#!/usr/bin/env python3
"""
Split a long podcast script into 4~6 TTS-ready text files.
"""

import argparse
import re
from pathlib import Path


def normalize(text: str) -> str:
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_by_paragraphs(text: str, target_parts: int = 5):
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    total = sum(len(p) for p in paras)
    if total == 0:
        return []
    chunk_size = max(1200, total // target_parts)

    parts, cur, cur_len = [], [], 0
    for p in paras:
        if cur_len + len(p) > chunk_size and cur:
            parts.append('\n\n'.join(cur))
            cur, cur_len = [p], len(p)
        else:
            cur.append(p)
            cur_len += len(p)
    if cur:
        parts.append('\n\n'.join(cur))

    while len(parts) > 6:
        parts[-2] = parts[-2] + '\n\n' + parts[-1]
        parts.pop()
    while len(parts) < 4 and len(parts) > 1:
        half = parts.pop()
        mid = len(parts[-1]) // 2
        parts[-1], first = parts[-1][:mid], parts[-1][mid:]
        parts.append(first + '\n\n' + half)

    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, help='script markdown/txt path')
    ap.add_argument('--outdir', required=True, help='output dir')
    ap.add_argument('--parts', type=int, default=5, help='target split count (default 5)')
    args = ap.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    text = normalize(inp.read_text(encoding='utf-8', errors='ignore'))
    parts = split_by_paragraphs(text, target_parts=args.parts)

    for i, part in enumerate(parts, 1):
        (outdir / f'tts_part_{i}.txt').write_text(part, encoding='utf-8')

    print(f'PARTS={len(parts)}')
    print(f'OUTDIR={outdir.resolve()}')


if __name__ == '__main__':
    main()
