#!/usr/bin/env python3
"""
Publish a note to Xiaohongshu using xhs-toolkit.

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_publish.py \
        --title "标题" --content "正文" \
        --images "/path/img1.png,/path/img2.png" \
        --topics "话题1,话题2" \
        [--dry-run]
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def setup_toolkit():
    toolkit_dir = os.environ.get("XHS_TOOLKIT_DIR", os.path.expanduser("~/.openclaw/skills/xhs/xhs-toolkit"))
    sys.path.insert(0, toolkit_dir)
    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )
    os.environ.setdefault("COOKIES_FILE", cookies_file)
    os.environ.setdefault(
        "CHROME_PATH",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    return toolkit_dir, cookies_file


def validate_cookies(cookies_file: str) -> bool:
    if not Path(cookies_file).exists():
        return False
    try:
        data = json.loads(Path(cookies_file).read_text())
        cookies = data.get("cookies", data) if isinstance(data, dict) else data
        return bool(cookies)
    except (json.JSONDecodeError, KeyError):
        return False


def parse_list_arg(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_images(image_paths: list[str]) -> tuple[bool, str]:
    if not image_paths:
        return False, "至少需要提供 1 张图片"
    if len(image_paths) > 9:
        return False, f"最多 9 张图片，当前 {len(image_paths)} 张"
    valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    for p in image_paths:
        path = Path(p)
        if not path.exists():
            return False, f"图片文件不存在: {p}"
        if path.suffix.lower() not in valid_exts:
            return False, f"不支持的图片格式: {path.suffix} ({p})"
    return True, "ok"


async def publish(title: str, content: str, images: list[str], topics: list[str], toolkit_dir: str):
    from src.core.config import XHSConfig
    from src.xiaohongshu.client import XHSClient

    config = XHSConfig()
    client = XHSClient(config)

    from src.xiaohongshu.models import XHSNote

    note = await XHSNote.async_smart_create(
        title=title,
        content=content,
        images=",".join(images),
        topics=",".join(topics) if topics else None,
    )

    result = await client.publish_note(note)
    return result


def main():
    parser = argparse.ArgumentParser(description="Publish a note to Xiaohongshu")
    parser.add_argument("--title", required=True, help="Note title (max 50 chars)")
    parser.add_argument("--content", required=True, help="Note body (max 1000 chars)")
    parser.add_argument("--images", required=True, help="Image paths, comma-separated (1-9 images)")
    parser.add_argument("--topics", default="", help="Topic hashtags, comma-separated (max 10)")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not publish")
    args = parser.parse_args()

    toolkit_dir, cookies_file = setup_toolkit()

    # Validate cookies
    if not validate_cookies(cookies_file):
        print(json.dumps({
            "status": "auth_required",
            "message": "未登录或 Cookie 无效，请先运行 xhs_auth.py 登录。",
        }))
        sys.exit(1)

    # Validate title
    if len(args.title) > 50:
        print(json.dumps({
            "status": "validation_error",
            "message": f"标题过长（{len(args.title)} 字），最多 50 字。",
        }))
        sys.exit(1)

    # Validate content
    if len(args.content) > 1000:
        print(json.dumps({
            "status": "validation_error",
            "message": f"正文过长（{len(args.content)} 字），最多 1000 字。",
        }))
        sys.exit(1)

    # Validate images
    images = parse_list_arg(args.images)
    valid, msg = validate_images(images)
    if not valid:
        print(json.dumps({
            "status": "validation_error",
            "message": msg,
        }))
        sys.exit(1)

    # Validate topics
    topics = parse_list_arg(args.topics)
    if len(topics) > 10:
        print(json.dumps({
            "status": "validation_error",
            "message": f"话题过多（{len(topics)} 个），最多 10 个。",
        }))
        sys.exit(1)

    if args.dry_run:
        print(json.dumps({
            "status": "dry_run",
            "message": "验证通过（dry-run 模式，未实际发布）。",
            "title": args.title,
            "content_length": len(args.content),
            "image_count": len(images),
            "topics": topics,
        }))
        return

    # Publish
    try:
        result = asyncio.run(publish(args.title, args.content, images, topics, toolkit_dir))

        # Log the publish
        data_dir = os.environ.get(
            "XHS_DATA_DIR",
            os.path.expanduser("~/.openclaw/skills/xhs/data"),
        )
        log_dir = Path(data_dir) / "published"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": args.title,
            "content_length": len(args.content),
            "image_count": len(images),
            "topics": topics,
            "result": {
                "success": getattr(result, "success", False),
                "url": getattr(result, "url", None),
                "message": getattr(result, "message", str(result)),
            },
        }
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        if getattr(result, "success", False):
            print(json.dumps({
                "status": "success",
                "message": "笔记发布成功！",
                "url": getattr(result, "url", None),
                "title": args.title,
            }))
        else:
            print(json.dumps({
                "status": "failed",
                "message": f"发布失败: {getattr(result, 'message', str(result))}",
            }))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"发布过程出错: {str(e)}",
            "error": str(e),
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
