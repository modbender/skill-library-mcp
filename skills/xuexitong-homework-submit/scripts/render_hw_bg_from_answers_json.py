#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Render handwritten-style PNG pages from an answers-text JSON.

Input JSON format (list):
[
  {
    "questionId": "406128479",
    "title": "第1题 ...",
    "answer": "...multiline text..."
  },
  ...
]

Outputs PNG files named:
  <outdir>/qid_<questionId>_p1.png, p2...

NOTE: This script is meant to be executed with the HandWrite project's venv
(HandWrite/.venv/bin/python) because it depends on handright + Pillow.
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageFont
from handright import Template, handwrite


def make_template(*, rate: int, w: int, h: int, font_path: str, font_size: int,
                  line_spacing: int, margins: tuple[int, int, int, int], word_spacing: int,
                  bg_image_path: str,
                  line_spacing_sigma: float, font_size_sigma: float, word_spacing_sigma: float,
                  perturb_x_sigma: float, perturb_y_sigma: float, perturb_theta_sigma: float,
                  fill=(20, 20, 20, 255)) -> Template:
    W, H = w * rate, h * rate

    bg = Image.open(bg_image_path).convert("RGBA")
    bg = bg.resize((W, H), Image.Resampling.LANCZOS)

    left, top, right, bottom = margins

    return Template(
        background=bg,
        font=ImageFont.truetype(font_path, size=font_size * rate),
        line_spacing=line_spacing * rate,
        fill=fill,
        left_margin=left * rate,
        top_margin=top * rate,
        right_margin=right * rate,
        bottom_margin=bottom * rate,
        word_spacing=word_spacing * rate,
        line_spacing_sigma=line_spacing_sigma * rate,
        font_size_sigma=font_size_sigma * rate,
        word_spacing_sigma=word_spacing_sigma * rate,
        start_chars="“（[<",
        end_chars="，。",
        perturb_x_sigma=perturb_x_sigma,
        perturb_y_sigma=perturb_y_sigma,
        perturb_theta_sigma=perturb_theta_sigma,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers-json", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--font", required=True)
    ap.add_argument("--bg", required=True)
    ap.add_argument("--rate", type=int, default=4)
    ap.add_argument("--w", type=int, default=850)
    ap.add_argument("--h", type=int, default=1200)
    ap.add_argument("--font-size", type=int, default=28)
    ap.add_argument("--line-spacing", type=int, default=62)
    ap.add_argument("--margins", default="55,40,55,40")
    ap.add_argument("--word-spacing", type=int, default=2)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    margins = tuple(int(x.strip()) for x in args.margins.split(","))
    if len(margins) != 4:
        raise SystemExit("--margins must be like '55,40,55,40'")

    template = make_template(
        rate=args.rate,
        w=args.w,
        h=args.h,
        font_path=args.font,
        font_size=args.font_size,
        line_spacing=args.line_spacing,
        margins=margins,  # type: ignore
        word_spacing=args.word_spacing,
        bg_image_path=args.bg,
        line_spacing_sigma=2,
        font_size_sigma=1,
        word_spacing_sigma=1,
        perturb_x_sigma=0.6,
        perturb_y_sigma=0.6,
        perturb_theta_sigma=0.02,
    )

    items = json.load(open(args.answers_json, encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("answers json must be a list")

    written = []
    for item in items:
        qid = str(item.get("questionId") or "").strip()
        title = str(item.get("title") or "").strip()
        answer = str(item.get("answer") or "").strip()
        if not qid:
            continue
        text = (title + "\n\n" + answer).strip()
        pages = list(handwrite(text, template, outdir.as_posix()))
        for i, im in enumerate(pages, start=1):
            p = outdir / f"qid_{qid}_p{i}.png"
            im.save(p)
            written.append(str(p))

    print(json.dumps({"outdir": str(outdir.resolve()), "count": len(written), "files": written}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
