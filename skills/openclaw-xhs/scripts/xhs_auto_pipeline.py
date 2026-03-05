#!/usr/bin/env python3
"""
Full automation pipeline: trending → generate → preview/publish.

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_auto_pipeline.py --mode preview
    uv run --project $XHS_TOOLKIT_DIR xhs_auto_pipeline.py --mode auto --category "科技"
    uv run --project $XHS_TOOLKIT_DIR xhs_auto_pipeline.py --config  (show/edit config)
    uv run --project $XHS_TOOLKIT_DIR xhs_auto_pipeline.py --set-mode auto|preview
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_data_dir() -> Path:
    return Path(os.environ.get(
        "XHS_DATA_DIR",
        os.path.expanduser("~/.openclaw/skills/xhs/data"),
    ))


def get_config_path() -> Path:
    return get_data_dir() / "config.json"


def load_config() -> dict:
    config_path = get_config_path()
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "mode": "preview",
        "category": "综合",
        "style": "干货分享",
        "image_count": 4,
        "skip_published_topics": True,
        "max_daily_posts": 3,
        "cron": {
            "trending_scan": "0 9,15,21 * * *",
            "auto_publish": "0 10,14,20 * * *",
        },
    }


def save_config(config: dict):
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))


def get_published_topics() -> set[str]:
    """Get set of topics already published to avoid duplicates."""
    published_dir = get_data_dir() / "published"
    topics = set()
    if not published_dir.exists():
        return topics
    for f in published_dir.glob("*.jsonl"):
        try:
            for line in f.read_text().splitlines():
                entry = json.loads(line)
                if entry.get("title"):
                    topics.add(entry["title"])
        except Exception:
            continue
    return topics


def find_latest_trending() -> Path | None:
    """Find the most recent trending data file."""
    trending_dir = get_data_dir() / "trending"
    if not trending_dir.exists():
        return None
    files = sorted(trending_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0] if files else None


def select_topic_from_trending(trending_file: Path, published_topics: set[str]) -> str | None:
    """Select an unpublished topic from trending data."""
    data = json.loads(trending_file.read_text())

    # Try weighted keywords first
    analysis = data.get("analysis", {})
    weighted_keywords = analysis.get("top_weighted_keywords", [])
    for kw in weighted_keywords:
        word = kw.get("word", "") if isinstance(kw, dict) else kw[0]
        if word and word not in published_topics and len(word) >= 2:
            return word

    # Fallback to note titles
    notes = data.get("notes", [])
    for note in notes:
        title = note.get("title", "")
        if title and title not in published_topics:
            return title[:20]

    # Fallback to regular keywords
    top_keywords = analysis.get("top_keywords", [])
    for kw in top_keywords:
        word = kw.get("word", "") if isinstance(kw, dict) else kw[0]
        if word and word not in published_topics and len(word) >= 2:
            return word

    return None


def run_script(script_name: str, args: list[str]) -> dict:
    """Run a sibling script and parse its JSON output."""
    toolkit_dir = os.environ.get("XHS_TOOLKIT_DIR", os.path.expanduser("~/.openclaw/skills/xhs/xhs-toolkit"))
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name

    cmd = ["uv", "run", "--project", toolkit_dir, str(script_path)] + args

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        env=os.environ.copy(),
    )

    # Parse the last JSON line from output
    output_lines = result.stdout.strip().split("\n")
    for line in reversed(output_lines):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    return {
        "status": "error",
        "message": f"Script {script_name} failed",
        "stdout": result.stdout[-500:] if result.stdout else "",
        "stderr": result.stderr[-500:] if result.stderr else "",
        "returncode": result.returncode,
    }


def count_today_posts() -> int:
    """Count how many posts were published today."""
    published_dir = get_data_dir() / "published"
    today_file = published_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    if not today_file.exists():
        return 0
    return sum(1 for line in today_file.read_text().splitlines() if line.strip())


def main():
    parser = argparse.ArgumentParser(description="XHS Auto Pipeline")
    parser.add_argument("--mode", choices=["auto", "preview"], default="",
                        help="Pipeline mode: auto (publish directly) or preview (generate only)")
    parser.add_argument("--category", default="", help="Trending category to scan")
    parser.add_argument("--keyword", default="", help="Search keyword for trending")
    parser.add_argument("--skip-trending", action="store_true",
                        help="Skip trending scrape, use latest data")
    parser.add_argument("--config", action="store_true", help="Show current config")
    parser.add_argument("--set-mode", choices=["auto", "preview"], default="",
                        help="Set pipeline mode")
    args = parser.parse_args()

    config = load_config()

    # Config management
    if args.set_mode:
        config["mode"] = args.set_mode
        save_config(config)
        print(json.dumps({
            "status": "success",
            "message": f"模式已切换为: {args.set_mode}",
            "config": config,
        }, ensure_ascii=False))
        return

    if args.config:
        print(json.dumps({
            "status": "info",
            "message": "当前配置",
            "config": config,
            "today_posts": count_today_posts(),
        }, ensure_ascii=False))
        return

    mode = args.mode or config.get("mode", "preview")
    category = args.category or config.get("category", "综合")
    style = config.get("style", "干货分享")
    image_count = config.get("image_count", 4)
    max_daily = config.get("max_daily_posts", 3)

    # Check daily limit
    today_count = count_today_posts()
    if today_count >= max_daily:
        print(json.dumps({
            "status": "limit_reached",
            "message": f"今日已发布 {today_count} 篇，达到每日上限 {max_daily} 篇。",
        }))
        return

    print(json.dumps({
        "status": "starting",
        "message": f"开始自动流水线 (模式: {mode}, 分类: {category})",
        "mode": mode,
    }))
    sys.stdout.flush()

    # Step 1: Check login status
    status_result = run_script("xhs_status.py", [])
    if not status_result.get("logged_in"):
        print(json.dumps({
            "status": "auth_required",
            "message": "未登录小红书，请先运行登录。",
        }))
        sys.exit(1)

    # Step 2: Scrape trending (unless skipped)
    trending_file = None
    if not args.skip_trending:
        print(json.dumps({
            "step": "trending",
            "status": "scraping",
            "message": f"正在爬取热点 ({category})...",
        }))
        sys.stdout.flush()

        trending_args = ["--category", category, "--limit", "20"]
        if args.keyword:
            trending_args = ["--keyword", args.keyword, "--limit", "20"]

        trending_result = run_script("xhs_trending.py", trending_args)
        if trending_result.get("status") == "success" and trending_result.get("output_file"):
            trending_file = Path(trending_result["output_file"])
        else:
            print(json.dumps({
                "step": "trending",
                "status": "warning",
                "message": f"热点爬取失败: {trending_result.get('message', 'unknown error')}，尝试使用已有数据。",
            }))
            sys.stdout.flush()

    if not trending_file:
        trending_file = find_latest_trending()

    # Step 3: Select topic
    published_topics = get_published_topics() if config.get("skip_published_topics", True) else set()

    topic = None
    if trending_file and trending_file.exists():
        topic = select_topic_from_trending(trending_file, published_topics)

    if not topic:
        topic = category if category != "综合" else "生活分享"
        print(json.dumps({
            "step": "topic_selection",
            "status": "fallback",
            "message": f"没有找到未发布的热门话题，使用默认话题: {topic}",
        }))
        sys.stdout.flush()
    else:
        print(json.dumps({
            "step": "topic_selection",
            "status": "selected",
            "message": f"选择话题: {topic}",
        }))
        sys.stdout.flush()

    # Step 4: Generate content
    print(json.dumps({
        "step": "generation",
        "status": "generating",
        "message": f"正在生成内容 (话题: {topic}, 风格: {style})...",
    }))
    sys.stdout.flush()

    gen_args = ["--topic", topic, "--style", style, "--image-count", str(image_count)]
    if trending_file and trending_file.exists():
        gen_args.extend(["--trending-file", str(trending_file)])

    gen_result = run_script("xhs_generate_content.py", gen_args)

    if gen_result.get("status") != "success":
        print(json.dumps({
            "status": "error",
            "message": f"内容生成失败: {gen_result.get('message', 'unknown error')}",
        }))
        sys.exit(1)

    package = gen_result.get("package", {})

    # Step 5: Preview or Publish
    if mode == "preview":
        result = {
            "status": "preview",
            "message": "内容已生成，等待确认。回复「发吧」发布，或修改意见。",
            "title": package.get("title", ""),
            "content": package.get("content", ""),
            "topics": package.get("topics", []),
            "images": package.get("images", []),
            "output_dir": gen_result.get("output_dir", ""),
        }
        print(json.dumps(result, ensure_ascii=False))
        # MEDIA lines for preview
        for img_path in package.get("images", []):
            print(f"MEDIA: {img_path}")
        return

    # Auto mode: publish directly
    images = package.get("images", [])
    if not images:
        print(json.dumps({
            "status": "error",
            "message": "没有可用的图片，无法发布。降级为预览模式。",
            "title": package.get("title", ""),
            "content": package.get("content", ""),
            "topics": package.get("topics", []),
        }))
        sys.exit(1)

    print(json.dumps({
        "step": "publishing",
        "status": "publishing",
        "message": f"正在发布笔记: {package.get('title', '')}",
    }))
    sys.stdout.flush()

    publish_args = [
        "--title", package.get("title", ""),
        "--content", package.get("content", ""),
        "--images", ",".join(images),
    ]
    if package.get("topics"):
        publish_args.extend(["--topics", ",".join(package["topics"])])

    publish_result = run_script("xhs_publish.py", publish_args)

    if publish_result.get("status") == "success":
        print(json.dumps({
            "status": "success",
            "message": f"全自动发布成功！标题: {package.get('title', '')}",
            "url": publish_result.get("url", ""),
            "title": package.get("title", ""),
            "today_posts": today_count + 1,
        }, ensure_ascii=False))
    else:
        print(json.dumps({
            "status": "publish_failed",
            "message": f"发布失败: {publish_result.get('message', 'unknown error')}",
            "title": package.get("title", ""),
            "content": package.get("content", ""),
            "images": images,
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
