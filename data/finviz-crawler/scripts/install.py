#!/usr/bin/env python3
"""
Cross-platform install script for finviz-crawler.
Works on macOS, Linux, and Windows (Python 3.10+).
"""
import subprocess
import sys
import shutil
import os
import json
import sqlite3
from datetime import datetime, timezone


DEFAULT_TICKERS = {
    "QQQ": ["qqq", "nasdaq"],
    "AMZN": ["amazon", "amzn", "aws"],
    "GOOGL": ["google", "googl", "alphabet"],
    "TSLA": ["tesla", "tsla", "elon musk"],
    "META": ["meta", "facebook", "zuckerberg"],
    "NVDA": ["nvidia", "nvda", "jensen"],
}


def run(cmd, check=True):
    print(f"  → {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def pip_install(packages):
    """Install packages using pip, preferring --user on non-venv systems."""
    pip_cmd = [sys.executable, "-m", "pip", "install"]
    if not (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)):
        pip_cmd.append("--user")
    pip_cmd.extend(packages)
    result = run(pip_cmd, check=False)
    if result.returncode != 0:
        print("  ⚠️  pip install failed, retrying without --user...")
        run([sys.executable, "-m", "pip", "install"] + packages)


def setup_tickers_db(settings_dir):
    """Create tickers SQLite DB with default tickers."""
    os.makedirs(settings_dir, exist_ok=True)
    db_path = os.path.join(settings_dir, "finviz.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS tickers (
        symbol TEXT PRIMARY KEY,
        keywords TEXT NOT NULL DEFAULT '[]',
        added_at TEXT NOT NULL
    )""")
    now = datetime.now(timezone.utc).isoformat()
    added = []
    for sym, kw in DEFAULT_TICKERS.items():
        cur = conn.execute("SELECT 1 FROM tickers WHERE symbol = ?", (sym,))
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO tickers (symbol, keywords, added_at) VALUES (?, ?, ?)",
                (sym, json.dumps(kw), now),
            )
            added.append(sym)
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM tickers").fetchone()[0]
    conn.close()
    if added:
        print(f"  Added default tickers: {', '.join(added)}")
    print(f"  📊 Tickers DB: {db_path} ({total} tickers)")
    return db_path


def setup_systemd_service(script_dir, python_exe):
    """Create and enable systemd user service (Linux only)."""
    service_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(service_dir, exist_ok=True)
    crawler_path = os.path.join(script_dir, "finviz_crawler.py")

    service_content = f"""[Unit]
Description=Finviz Financial News Crawler
After=network-online.target

[Service]
Type=simple
ExecStart={python_exe} {crawler_path} --expiry-days 30
Restart=on-failure
RestartSec=30
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""
    service_path = os.path.join(service_dir, "finviz-crawler.service")
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"  📝 Service file: {service_path}")

    run(["systemctl", "--user", "daemon-reload"], check=False)
    run(["systemctl", "--user", "enable", "finviz-crawler.service"], check=False)
    print("  ✅ Service enabled (will start on login)")
    print("  Start now with: systemctl --user start finviz-crawler.service")


def setup_launchd_plist(script_dir, python_exe):
    """Create launchd plist (macOS only)."""
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(plist_dir, exist_ok=True)
    crawler_path = os.path.join(script_dir, "finviz_crawler.py")
    log_path = os.path.expanduser("~/Library/Logs/finviz-crawler.log")

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.finviz.crawler</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{crawler_path}</string>
        <string>--expiry-days</string>
        <string>30</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>{log_path}</string>
    <key>StandardErrorPath</key><string>{log_path}</string>
</dict>
</plist>"""
    plist_path = os.path.join(plist_dir, "com.finviz.crawler.plist")
    with open(plist_path, "w") as f:
        f.write(plist_content)
    print(f"  📝 Plist file: {plist_path}")
    print("  Start now with: launchctl load ~/Library/LaunchAgents/com.finviz.crawler.plist")


def main():
    print("🔧 Installing finviz-crawler...\n")

    # 1. Check Python version
    v = sys.version_info
    print(f"Python: {v.major}.{v.minor}.{v.micro}")
    if v < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    print(f"  ✅ Python {v.major}.{v.minor}\n")

    # 2. Install Python packages
    print("Installing Python packages...")
    pip_install(["crawl4ai", "feedparser"])

    # 3. Install Playwright browsers (required by crawl4ai)
    print("\nInstalling Playwright browsers (used by crawl4ai)...")
    result = run([sys.executable, "-m", "crawl4ai.install"], check=False)
    if result.returncode != 0:
        crawl4ai_setup = shutil.which("crawl4ai-setup")
        if crawl4ai_setup:
            run([crawl4ai_setup], check=False)
        else:
            print("  Falling back to playwright install...")
            run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)

    # 4. Create data directories
    data_dir = os.path.expanduser("~/Downloads/Finviz")
    articles_dir = os.path.join(data_dir, "articles")
    os.makedirs(articles_dir, exist_ok=True)
    print(f"\n  📁 Data directory: {data_dir}")
    print(f"  📁 Articles directory: {articles_dir}")

    # 5. Create tickers DB with defaults
    print("\nSetting up tickers database...")
    settings_dir = os.path.expanduser("~/Downloads/Finviz")
    setup_tickers_db(settings_dir)

    # 6. Set up service (platform-specific)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable
    platform = sys.platform

    print("\nSetting up background service...")
    if platform == "linux":
        setup_systemd_service(script_dir, python_exe)
    elif platform == "darwin":
        setup_launchd_plist(script_dir, python_exe)
    else:
        print("  ⚠️  Auto-service not supported on this platform.")
        print(f"  Run manually: {python_exe} {os.path.join(script_dir, 'finviz_crawler.py')}")

    # 7. Verify
    print("\n🔍 Verifying installation...")
    errors = []

    try:
        import crawl4ai  # noqa: F401
        print("  ✅ crawl4ai")
    except ImportError:
        errors.append("crawl4ai")
        print("  ❌ crawl4ai")

    try:
        import feedparser  # noqa: F401
        print("  ✅ feedparser")
    except ImportError:
        errors.append("feedparser")
        print("  ❌ feedparser")

    try:
        from zoneinfo import ZoneInfo  # noqa: F401
        print("  ✅ zoneinfo")
    except ImportError:
        errors.append("zoneinfo (Python 3.9+ required)")
        print("  ❌ zoneinfo")

    query_script = os.path.join(script_dir, "finviz_query.py")
    if os.path.exists(query_script):
        result = run([sys.executable, query_script, "--list-tickers"], check=False)
        if result.returncode == 0:
            print("  ✅ query script")
        else:
            print("  ⚠️  query script (check errors above)")

    if errors:
        print(f"\n❌ Missing: {', '.join(errors)}")
        print("   Try: pip install " + " ".join(errors))
        sys.exit(1)
    else:
        print("\n✅ Installation complete!")
        print("\nManage tickers:")
        print(f"  python3 {query_script} --list-tickers")
        print(f"  python3 {query_script} --add-ticker NVDA:nvidia,jensen")
        print(f"  python3 {query_script} --remove-ticker MSFT")
        print("\nQuery articles:")
        print(f"  python3 {query_script} --hours 24 --titles-only")


if __name__ == "__main__":
    main()
