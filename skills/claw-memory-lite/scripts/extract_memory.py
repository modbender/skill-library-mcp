#!/usr/bin/env python3
"""
extract_memory.py - Auto-extract daily memory files to long-term database

This script scans the memory/ directory for unprocessed daily memory files,
extracts key information using heuristic analysis, and stores them in a
SQLite database for fast querying.

Usage:
    python3 extract_memory.py [--review] [--force]

Arguments:
    --review    Preview mode - show what would be extracted without writing
    --force     Re-process already processed files

Features:
    - Automatic category detection (System/Environment/Skill/Project/Comm/Security)
    - L0/L1/L2 hierarchy extraction
    - Keyword generation for fast search
    - Idempotent (won't re-process same files)
"""

import sqlite3
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# ============== Configuration ==============
WORKSPACE = Path(os.environ.get("CLAW_MEMORY_WORKSPACE", "/home/node/.openclaw/workspace"))
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_MD = WORKSPACE / "MEMORY.md"
DB_PATH = os.environ.get(
    "CLAW_MEMORY_DB_PATH",
    "/home/node/.openclaw/database/insight.db"
)

# Category keywords for heuristic classification
CATEGORY_KEYWORDS = {
    "Skill": ["skill", "工具", "配置", "api", "token", "oauth", "model", "installed", "command"],
    "Project": ["项目", "project", "策略", "strategy", "backtest", "portfolio", "stock"],
    "System": ["system", "配置", "config", "model", "alias", "session", "openclaw"],
    "Environment": ["env", "路径", "backup", "workspace", "uv", "python", "path", "directory"],
    "Comm": ["discord", "telegram", "频道", "channel", "bot", "notification", "message"],
    "Security": ["security", "凭证", "api key", "密码", "permission", "access", "auth"]
}

# Extraction keywords (lines containing these are likely important)
EXTRACTION_KEYWORDS = [
    "完成", "配置", "添加", "修复", "停用", "决策", "note", "fix", "add", 
    "config", "install", "create", "update", "delete", "error", "success"
]


# ============== Database Operations ==============
def init_db():
    """Initialize database schema."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            keywords TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for fast queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_category ON long_term_memory(category)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_keywords ON long_term_memory(keywords)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at ON long_term_memory(created_at)
    """)
    
    conn.commit()
    conn.close()


def save_to_db(category, content, keywords="", source_file=""):
    """Save a memory record to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO long_term_memory (category, content, keywords, source_file)
        VALUES (?, ?, ?, ?)
    """, (category, content, keywords, source_file))
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    
    return last_id


# ============== File Operations ==============
def get_processed_files():
    """Get list of already processed files from MEMORY.md."""
    processed = set()
    
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        # Parse extraction log table
        for match in re.finditer(r'\| (\d{4}-\d{2}-\d{2}) \| `memory/([^`]+)`', content):
            processed.add(match.group(2))
    
    return processed


def get_unprocessed_files(force=False):
    """Get list of unprocessed daily memory files."""
    if not MEMORY_DIR.exists():
        return []
    
    processed = set() if force else get_processed_files()
    
    unprocessed = []
    for f in sorted(MEMORY_DIR.glob("*.md")):
        if f.name not in processed and f.name != "heartbeat-state.json":
            unprocessed.append(f)
    
    return unprocessed


def extract_content_from_file(file_path):
    """Extract plain text content from markdown file."""
    content = file_path.read_text()
    # Remove markdown headers
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    return content.strip()


# ============== Extraction Logic ==============
def detect_category(content):
    """Detect category using keyword matching."""
    content_lower = content.lower()
    max_score = 0
    detected_category = "System"  # Default
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > max_score:
            max_score = score
            detected_category = category
    
    return detected_category


def extract_facts(content):
    """Extract important facts from content."""
    lines = content.split('\n')
    facts = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 20 and not line.startswith('#'):
            # Extract lines containing key verbs/nouns
            if any(kw in line.lower() for kw in EXTRACTION_KEYWORDS):
                facts.append(line[:200])  # Limit length
    
    return facts


def generate_keywords(content, category, date_str):
    """Generate keywords for search optimization."""
    # Extract English words (4+ chars)
    all_words = list(set(re.findall(r'\b[A-Za-z]{4,}\b', content)))
    # Extract Chinese keywords (2+ chars)
    chinese_words = list(set(re.findall(r'[\u4e00-\u9fa5]{2,}', content)))
    
    # Combine and limit
    keywords = f"{category} {date_str} " + " ".join(all_words[:10] + chinese_words[:5])
    return keywords


def simple_extract(content, filename):
    """
    Simple extraction logic (no external LLM dependency).
    Uses heuristic analysis based on keywords and structure.
    """
    # Detect category
    category = detect_category(content)
    
    # Extract facts
    facts = extract_facts(content)
    
    # Generate L0 summary
    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    date_str = date_match.group(1) if date_match else "unknown"
    
    if facts:
        l0 = f"[{date_str}] {category}: {facts[0][:80]}..."
    else:
        l0 = f"[{date_str}] {category} update"
    
    # Generate keywords
    keywords = generate_keywords(content, category, date_str)
    
    return {
        "l0": l0,
        "l1_category": category,
        "l1_summary": f"{category} memory update with {len(facts)} key record(s)",
        "l2_facts": facts[:5],  # Limit to top 5 facts
        "keywords": keywords,
        "source_file": filename,
        "raw_content": content
    }


def process_file(file_path, review_only=False):
    """Process a single memory file."""
    content = extract_content_from_file(file_path)
    result = simple_extract(content, file_path.name)
    
    if not review_only:
        # Save to database
        for fact in result["l2_facts"]:
            save_to_db(
                category=result["l1_category"],
                content=fact,
                keywords=result["keywords"],
                source_file=file_path.name
            )
        
        # Update MEMORY.md
        update_memory_md(file_path.name, result)
    
    return result


def update_memory_md(filename, result):
    """Update MEMORY.md extraction log."""
    if not MEMORY_MD.exists():
        return
    
    content = MEMORY_MD.read_text()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create new table row
    summary = result["l2_facts"][0][:50] if result["l2_facts"] else "No facts extracted"
    new_row = f"| {today} | `memory/{filename}` | {result['l1_category']}: {summary}... |\n"
    
    # Find table and insert new row
    table_marker = "## 📅 Recent extraction records"
    if table_marker in content:
        parts = content.split(table_marker)
        if len(parts) > 1:
            table_start = parts[1].find('|')
            if table_start > 0:
                lines = parts[1][table_start:].split('\n')
                insert_pos = 1  # After header
                while insert_pos < len(lines) and lines[insert_pos].startswith('|'):
                    insert_pos += 1
                lines.insert(insert_pos, new_row.strip())
                parts[1] = '\n'.join(lines)
                content = table_marker + parts[1]
    
    # Update last updated timestamp
    content = re.sub(
        r'\*Last Updated：[^*]+\*',
        f'*Last updated: {today} | Next auto-extraction: during heartbeat check*',
        content
    )
    
    MEMORY_MD.write_text(content)


# ============== Main ==============
def main():
    review_only = "--review" in sys.argv
    force = "--force" in sys.argv
    
    print("🔍 Scanning for unprocessed daily memory files...\n")
    
    # Initialize database
    init_db()
    
    # Get unprocessed files
    unprocessed = get_unprocessed_files(force)
    
    if not unprocessed:
        print("✅ All daily memory files have been processed.")
        return
    
    print(f"Found {len(unprocessed)} file(s) to process:\n")
    
    total_facts = 0
    for file_path in unprocessed:
        print(f"📄 Processing: {file_path.name}")
        result = process_file(file_path, review_only)
        
        print(f"   L0: {result['l0']}")
        print(f"   L1 Category: {result['l1_category']}")
        print(f"   L2 Facts: {len(result['l2_facts'])} extracted")
        
        for fact in result['l2_facts'][:3]:
            print(f"      - {fact[:60]}...")
        
        total_facts += len(result['l2_facts'])
        print()
    
    mode = "Preview mode (no writes)" if review_only else "Written to database"
    print(f"\n✅ Complete - {mode}")
    print(f"   Total facts extracted: {total_facts}")
    
    if review_only:
        print("   Run without --review to save to database")


if __name__ == "__main__":
    main()
