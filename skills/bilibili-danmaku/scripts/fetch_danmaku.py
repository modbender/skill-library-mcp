#!/usr/bin/env python3
"""
抓取 B 站视频弹幕（XML）并导出为 CSV/JSON/TXT。
仅使用 Python 标准库，避免 requests 依赖。
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
import gzip
from typing import Any, Dict, List, Optional

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def http_get_json(url: str, timeout: int = 20) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
    return json.loads(raw)


def http_get_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        enc = (resp.headers.get("Content-Encoding") or "").lower()

    if "deflate" in enc:
        try:
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        except Exception:
            try:
                raw = zlib.decompress(raw)
            except Exception:
                pass
    elif "gzip" in enc:
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass

    return raw.decode("utf-8", errors="ignore")


def parse_bvid_from_url(url: str) -> Optional[str]:
    m = re.search(r"/(BV[0-9A-Za-z]+)", url)
    return m.group(1) if m else None


def parse_page_from_url(url: str) -> Optional[int]:
    try:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if "p" in query and query["p"]:
            p = int(query["p"][0])
            return p if p >= 1 else None
    except Exception:
        return None
    return None


def iso_from_ts(ts: int) -> str:
    try:
        return dt.datetime.fromtimestamp(ts).isoformat()
    except Exception:
        return ""


def choose_page(video_data: Dict[str, Any], page_num: int, force_cid: Optional[int]) -> Dict[str, Any]:
    if force_cid:
        return {
            "page": page_num,
            "part": "(forced by --cid)",
            "cid": force_cid,
        }

    pages = video_data.get("pages") or []
    if not pages:
        raise RuntimeError("视频信息缺少 pages，无法定位 cid")
    if page_num < 1 or page_num > len(pages):
        raise RuntimeError(f"页码超出范围：p={page_num}, 该视频总P数={len(pages)}")

    selected = pages[page_num - 1]
    return {
        "page": selected.get("page", page_num),
        "part": selected.get("part", ""),
        "cid": int(selected["cid"]),
    }


def parse_danmaku_xml(xml_text: str) -> List[Dict[str, Any]]:
    root = ET.fromstring(xml_text)
    out: List[Dict[str, Any]] = []

    for node in root.findall("d"):
        p = (node.attrib.get("p") or "").split(",")
        if len(p) < 8:
            continue

        text = (node.text or "").strip()
        try:
            item = {
                "appear_sec": float(p[0]),
                "mode": int(p[1]),
                "font_size": int(p[2]),
                "color": int(p[3]),
                "color_hex": f"#{int(p[3]):06X}",
                "send_ts": int(p[4]),
                "send_time": iso_from_ts(int(p[4])),
                "pool": int(p[5]),
                "user_hash": p[6],
                "danmaku_id": p[7],
                "text": text,
            }
            out.append(item)
        except Exception:
            continue
    return out


def safe_name(s: str) -> str:
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "", s)
    return s[:80] if s else "video"


def save_outputs(records: List[Dict[str, Any]], meta: Dict[str, Any], outdir: str, prefix: str) -> Dict[str, str]:
    os.makedirs(outdir, exist_ok=True)

    csv_path = os.path.join(outdir, f"{prefix}_danmaku.csv")
    json_path = os.path.join(outdir, f"{prefix}_danmaku.json")
    txt_path = os.path.join(outdir, f"{prefix}_corpus.txt")
    meta_path = os.path.join(outdir, f"{prefix}_meta.json")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "appear_sec",
                "mode",
                "font_size",
                "color",
                "color_hex",
                "send_ts",
                "send_time",
                "pool",
                "user_hash",
                "danmaku_id",
                "text",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        for r in records:
            t = (r.get("text") or "").strip()
            if t:
                f.write(t + "\n")

    meta = dict(meta)
    meta["danmaku_count"] = len(records)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return {
        "csv": csv_path,
        "json": json_path,
        "txt": txt_path,
        "meta": meta_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="抓取 B 站视频弹幕并导出")
    parser.add_argument("--url", help="B站视频URL，例如 https://www.bilibili.com/video/BVxxxx")
    parser.add_argument("--bvid", help="BV号，例如 BV1xx411c7mD")
    parser.add_argument("--cid", type=int, help="直接指定 cid（可跳过视频信息接口）")
    parser.add_argument("--page", type=int, default=1, help="分P页码，默认 1")
    parser.add_argument("--outdir", default="./output", help="输出目录")
    parser.add_argument("--prefix", default="", help="输出文件前缀（默认自动生成）")
    args = parser.parse_args()

    bvid = args.bvid
    page_num = args.page

    if args.url:
        bvid = bvid or parse_bvid_from_url(args.url)
        url_p = parse_page_from_url(args.url)
        if url_p and args.page == 1:
            page_num = url_p

    if not bvid and not args.cid:
        print("[error] 需要提供 --url / --bvid / --cid 之一", file=sys.stderr)
        return 2

    video_meta: Dict[str, Any] = {}
    if args.cid:
        page_info = {"cid": args.cid, "page": page_num, "part": ""}
        if bvid:
            video_meta["bvid"] = bvid
    else:
        api = f"https://api.bilibili.com/x/web-interface/view?bvid={urllib.parse.quote(bvid)}"
        view = http_get_json(api)
        if view.get("code") != 0:
            print(f"[error] 获取视频信息失败: {view}", file=sys.stderr)
            return 3
        data = view.get("data") or {}
        page_info = choose_page(data, page_num, None)
        video_meta = {
            "bvid": data.get("bvid") or bvid,
            "aid": data.get("aid"),
            "title": data.get("title") or "",
            "owner": (data.get("owner") or {}).get("name"),
            "pubdate": data.get("pubdate"),
            "duration": data.get("duration"),
        }

    cid = int(page_info["cid"])
    xml_url = f"https://comment.bilibili.com/{cid}.xml"
    xml_text = http_get_text(xml_url)
    records = parse_danmaku_xml(xml_text)

    if not records:
        print("[warn] 未抓到弹幕，可能视频关闭弹幕或区域限制")

    title_safe = safe_name(video_meta.get("title") or "video")
    default_prefix = f"{video_meta.get('bvid', 'cid'+str(cid))}_p{page_info.get('page', 1)}_{cid}_{title_safe}"
    prefix = args.prefix.strip() or default_prefix

    meta = {
        "source": {
            "url": args.url,
            "bvid": video_meta.get("bvid") or bvid,
            "cid": cid,
            "page": page_info.get("page"),
            "part": page_info.get("part"),
            "xml_url": xml_url,
        },
        "video": video_meta,
    }

    paths = save_outputs(records, meta, args.outdir, prefix)

    print("[ok] 弹幕抓取完成")
    print(f"[ok] count: {len(records)}")
    for k, v in paths.items():
        print(f"[ok] {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
