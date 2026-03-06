#!/usr/bin/env python3
"""
install.py — Cross-platform installer for ArXivKB.

Creates data directories, SQLite DB with categories table,
installs Python dependencies, and sets up a daily cron/service
for paper ingestion.

Works on macOS and Linux. Python 3.10+ required.
"""
import subprocess
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).parent
DEFAULT_DATA_DIR = Path("~/Downloads/ArXivKB").expanduser()

DEFAULT_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.CV": "Computer Vision and Pattern Recognition",
    "cs.RO": "Robotics",
    "stat.ML": "Machine Learning",
}


def run(cmd, check=True):
    print(f"  → {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def pip_install(packages):
    """Install packages using pip."""
    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        pip_cmd.append("--user")
    pip_cmd.extend(packages)
    result = run(pip_cmd, check=False)
    if result.returncode != 0:
        # Retry without --user
        run([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)


def setup_db(data_dir: Path):
    """Create SQLite DB with tables and seed default categories."""
    db_path = data_dir / "arxivkb.db"
    conn = sqlite3.connect(str(db_path))

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS papers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id    TEXT    UNIQUE NOT NULL,
            title       TEXT    NOT NULL,
            abstract    TEXT,
            categories  TEXT,
            published   TEXT,
            status      TEXT    DEFAULT 'new',
            created_at  TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        CREATE TABLE IF NOT EXISTS chunks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id    INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
            section     TEXT,
            chunk_index INTEGER,
            text        TEXT NOT NULL,
            faiss_id    INTEGER,
            created_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        CREATE TABLE IF NOT EXISTS translations (
            paper_id    INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
            language    TEXT NOT NULL,
            abstract    TEXT NOT NULL,
            created_at  TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
            PRIMARY KEY (paper_id, language)
        );
        CREATE TABLE IF NOT EXISTS categories (
            code        TEXT PRIMARY KEY,
            description TEXT,
            group_name  TEXT,
            enabled     INTEGER DEFAULT 0,
            added_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        );
        CREATE INDEX IF NOT EXISTS idx_papers_status    ON papers(status);
        CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published);
        CREATE INDEX IF NOT EXISTS idx_chunks_paper_id  ON chunks(paper_id);
        CREATE INDEX IF NOT EXISTS idx_chunks_faiss_id  ON chunks(faiss_id);
    """)

    # Seed default categories
    now = datetime.now(timezone.utc).isoformat()
    added = []
    for cat, desc in DEFAULT_CATEGORIES.items():
        try:
            conn.execute("INSERT INTO categories (code, description, added_at) VALUES (?, ?, ?)", (cat, desc, now))
            added.append(cat)
        except sqlite3.IntegrityError:
            pass
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    conn.close()

    if added:
        print(f"  Added default categories: {', '.join(added)}")
    print(f"  📊 DB: {db_path} ({total} categories)")
    return db_path


def setup_systemd_timer(script_dir: Path, python_exe: str, data_dir: Path):
    """Create systemd timer for daily crawl (Linux only)."""
    service_dir = Path("~/.config/systemd/user").expanduser()
    service_dir.mkdir(parents=True, exist_ok=True)

    cli_path = script_dir / "cli.py"
    cfg_path = data_dir / "config.json"

    service = f"""[Unit]
Description=ArXivKB daily paper ingest
After=network-online.target

[Service]
Type=oneshot
ExecStart={python_exe} {cli_path} --config {cfg_path} ingest
Environment=PYTHONUNBUFFERED=1
TimeoutStartSec=1800
"""
    timer = """[Unit]
Description=ArXivKB daily ingest timer

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""
    (service_dir / "akb-crawler.service").write_text(service)
    (service_dir / "akb-crawler.timer").write_text(timer)

    run(["systemctl", "--user", "daemon-reload"], check=False)
    run(["systemctl", "--user", "enable", "akb-crawler.timer"], check=False)
    print("  ✅ Timer enabled (daily 3 AM)")
    print("  Start now: systemctl --user start akb-crawler.service")


def setup_launchd_plist(script_dir: Path, python_exe: str, data_dir: Path):
    """Create launchd plist for daily crawl (macOS only)."""
    plist_dir = Path("~/Library/LaunchAgents").expanduser()
    plist_dir.mkdir(parents=True, exist_ok=True)

    cli_path = script_dir / "cli.py"
    cfg_path = data_dir / "config.json"
    log_path = Path("~/Library/Logs/akb-crawler.log").expanduser()

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.arxivkb.crawler</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_exe}</string>
        <string>{cli_path}</string>
        <string>--config</string>
        <string>{cfg_path}</string>
        <string>ingest</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>3</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key><string>{log_path}</string>
    <key>StandardErrorPath</key><string>{log_path}</string>
</dict>
</plist>"""
    plist_path = plist_dir / "com.arxivkb.crawler.plist"
    plist_path.write_text(plist)
    print(f"  📝 Plist: {plist_path}")
    print("  Load: launchctl load ~/Library/LaunchAgents/com.arxivkb.crawler.plist")


def main():
    print("🔧 Installing ArXivKB...\n")

    v = sys.version_info
    if v < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    print(f"  ✅ Python {v.major}.{v.minor}\n")

    # 1. Install deps
    print("Installing Python packages...")
    pip_install(["faiss-cpu", "pdfplumber", "arxiv", "numpy", "requests", "tiktoken"])

    # 2. Create data directories
    print("\n📁 Setting up data directory...")
    DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DEFAULT_DATA_DIR / "pdfs").mkdir(exist_ok=True)
    (DEFAULT_DATA_DIR / "faiss").mkdir(exist_ok=True)
    print(f"  📁 {DEFAULT_DATA_DIR}")

    # 3. Pull embedding model via Ollama
    print("\n🤖 Pulling embedding model (nomic-embed-text)...")
    result = run(["ollama", "pull", "nomic-embed-text"], check=False)
    if result.returncode == 0:
        print("  ✅ nomic-embed-text ready")
    else:
        print("  ⚠️  Ollama not found or pull failed — install Ollama and run: ollama pull nomic-embed-text")

    # 4. Create DB with categories
    print("\n🗄️  Database...")
    setup_db(DEFAULT_DATA_DIR)

    # 5. Set up cron
    print("\n⏰ Setting up daily crawl...")
    if sys.platform == "linux":
        setup_systemd_timer(SCRIPT_DIR, sys.executable, DEFAULT_DATA_DIR)
    elif sys.platform == "darwin":
        setup_launchd_plist(SCRIPT_DIR, sys.executable, DEFAULT_DATA_DIR)
    else:
        print("  ⚠️  Manual cron setup needed on this platform")

    # 6. Verify
    print("\n🔍 Verifying...")
    errors = []
    for mod, label in [("faiss", "faiss-cpu"), ("pdfplumber", "pdfplumber"),
                       ("arxiv", "arxiv"), ("numpy", "numpy"), ("tiktoken", "tiktoken")]:
        try:
            __import__(mod)
            print(f"  ✅ {label}")
        except ImportError:
            errors.append(label)
            print(f"  ❌ {label}")

    if errors:
        print(f"\n❌ Missing: {', '.join(errors)}")
        sys.exit(1)

    print("\n✅ ArXivKB installed!")
    print("\nManage categories:")
    print("  akb categories list")
    print("  akb categories add cs.AI cs.CV")
    print("  akb categories browse")
    print("\nRun first ingest:")
    print("  akb ingest --days 7")


if __name__ == "__main__":
    main()
