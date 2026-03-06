#!/usr/bin/env python3
"""XHS (Xiaohongshu) sentiment crawler - search keywords and collect notes + comments.
Usage: python3 xhs_crawler.py --keywords "关键词1,关键词2" --output ./data
Requires: MediaCrawler installed at MEDIA_CRAWLER_PATH env var or ../media-crawler/
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_media_crawler():
    """Locate MediaCrawler installation."""
    env_path = os.environ.get("MEDIA_CRAWLER_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    # Check common locations
    candidates = [
        Path(__file__).parent.parent.parent / "media-crawler",
        Path.home() / ".openclaw" / "workspace" / "skills" / "media-crawler",
    ]
    for p in candidates:
        if (p / "main.py").exists():
            return p
    return None


def update_config(crawler_path: Path, keywords: str):
    """Update MediaCrawler config with search keywords."""
    config_file = crawler_path / "config" / "base_config.py"
    if not config_file.exists():
        print(f"ERROR: Config not found at {config_file}")
        sys.exit(1)

    content = config_file.read_text()
    # Update KEYWORDS
    import re
    content = re.sub(
        r'KEYWORDS\s*=\s*"[^"]*"',
        f'KEYWORDS = "{keywords}"',
        content
    )
    # Ensure JSON save mode
    content = re.sub(
        r'SAVE_DATA_OPTION\s*=\s*"[^"]*"',
        'SAVE_DATA_OPTION = "json"',
        content
    )
    # Ensure XHS platform
    content = re.sub(
        r'PLATFORM\s*=\s*"[^"]*"',
        'PLATFORM = "xhs"',
        content
    )
    config_file.write_text(content)
    print(f"Updated config: keywords={keywords}")


def run_crawler(crawler_path: Path):
    """Run MediaCrawler."""
    venv_python = crawler_path / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print("ERROR: MediaCrawler venv not found. Run 'uv sync' in media-crawler/ first.")
        sys.exit(1)

    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    if "/usr/sbin" not in env.get("PATH", ""):
        env["PATH"] = f"/usr/sbin:{env['PATH']}"

    print("Starting XHS crawler (CDP mode)...")
    print("If login required, scan QR code on your phone.")
    result = subprocess.run(
        [str(venv_python), "main.py", "--platform", "xhs", "--lt", "qrcode"],
        cwd=str(crawler_path),
        env=env,
        timeout=600,
    )
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="XHS Sentiment Crawler")
    parser.add_argument("--keywords", required=True, help="Comma-separated search keywords")
    parser.add_argument("--output", default="./data", help="Output directory")
    parser.add_argument("--crawl-only", action="store_true", help="Only crawl, skip analysis")
    args = parser.parse_args()

    crawler_path = find_media_crawler()
    if not crawler_path:
        print("ERROR: MediaCrawler not found. Install it first:")
        print("  git clone https://github.com/NanmiCoder/MediaCrawler ~/.openclaw/workspace/skills/media-crawler")
        print("  cd ~/.openclaw/workspace/skills/media-crawler && uv sync")
        sys.exit(1)

    update_config(crawler_path, args.keywords)
    exit_code = run_crawler(crawler_path)

    if exit_code != 0:
        print(f"Crawler exited with code {exit_code}")
        sys.exit(exit_code)

    # Copy data to output
    data_dir = crawler_path / "data" / "xhs" / "json"
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    import glob
    for f in data_dir.glob("*.json"):
        dest = output_dir / f.name
        shutil.copy2(f, dest)
        print(f"Copied {f.name} -> {dest}")

    print(f"\nCrawl complete. Data saved to {output_dir}")


if __name__ == "__main__":
    main()
