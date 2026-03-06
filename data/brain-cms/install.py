#!/usr/bin/env python3
"""
Brain CMS Installer
Sets up the full Continuum Memory System in your OpenClaw workspace.
Run once to bootstrap the architecture.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent
WORKSPACE = Path.home() / ".openclaw" / "workspace"

# ─── Templates ────────────────────────────────────────────────────────────────
INDEX_TEMPLATE = """# Memory Index — Hippocampus
_Last updated: {date}_

> **This file is the router. Check it before loading any schema.**
> It tells you what to load, what's connected, and why it matters.
> Add new schemas here immediately when you create them.

---

## Schema Registry

<!-- Add your schemas here. Example:

### [ProjectName]
- **Files:** `memory/project.md`
- **Triggers:** keyword1, keyword2, keyword3
- **Priority:** HIGH / MEDIUM / LOW
- **Cross-links:** → **OtherDomain** (reason)
- **Status:** Active / Complete
- **Why it matters:** One sentence on why this schema exists.

-->

---

## Cross-Link Map
```
(Add cross-links between domains as they emerge)
```

---

## Permanent Anchors
Check `memory/ANCHORS.md` when:
- A CRITICAL domain is triggered
- User mentions a past milestone or commitment
- Something feels inconsistent with known history

---

## Vector Store
Location: `memory_brain/vectorstore/` (LanceDB)
Re-index after schema changes: `memory_brain/.venv/bin/python3 memory_brain/index_memory.py`
Query: `memory_brain/.venv/bin/python3 memory_brain/query_memory.py "text" --sources-only`

---

## Auto-Schema Protocol
New significant project/domain → create `memory/<topic>.md` → add entry above → note cross-links → re-index.
"""

ANCHORS_TEMPLATE = """# Memory Anchors — Permanent High-Significance Events
_Last updated: {date}_

> These are strong memory anchors. Never prune. Update in place if superseded.
> Tag new anchors in daily logs with [ANCHOR] — NREM promotes them here automatically.

---

## Format
`Date | Domain | Event | Why it matters | Status`

---

## Active Anchors

### {date} | Setup | Brain CMS installed
Continuum Memory System installed and configured.
Status: Active foundation.

---

## Anchor Promotion Protocol
NREM scans daily logs for [ANCHOR] tags → appends here → removes tag from log.
REM reviews anchors → updates Status if superseded → never deletes (marks [ARCHIVED]).
"""

# ─── Brain scripts to copy ─────────────────────────────────────────────────────
BRAIN_SCRIPTS = ["index_memory.py", "query_memory.py", "nrem.py", "rem.py"]

# ─── Install ───────────────────────────────────────────────────────────────────
def run(cmd: str, check=True) -> bool:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  [WARN] {result.stderr[:100]}")
        return False
    return True

def main():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    print("\n🧠 Brain CMS Installer")
    print("=" * 50)

    # 1. Create memory directories
    memory_dir = WORKSPACE / "memory"
    brain_dir = WORKSPACE / "memory_brain"
    memory_dir.mkdir(parents=True, exist_ok=True)
    brain_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")

    # 2. Create INDEX.md if not exists
    index_path = memory_dir / "INDEX.md"
    if not index_path.exists():
        index_path.write_text(INDEX_TEMPLATE.format(date=today))
        print("✅ INDEX.md (hippocampus) created")
    else:
        print("⏭️  INDEX.md already exists — skipping")

    # 3. Create ANCHORS.md if not exists
    anchors_path = memory_dir / "ANCHORS.md"
    if not anchors_path.exists():
        anchors_path.write_text(ANCHORS_TEMPLATE.format(date=today))
        print("✅ ANCHORS.md created")
    else:
        print("⏭️  ANCHORS.md already exists — skipping")

    # 4. Copy brain scripts
    copied = 0
    for script in BRAIN_SCRIPTS:
        src = SKILL_DIR / "brain_scripts" / script
        dst = brain_dir / script
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
        elif dst.exists():
            pass  # Already there
        else:
            print(f"  [WARN] Script not found: {src}")
    if copied:
        print(f"✅ Copied {copied} brain scripts")

    # 5. Set up Python venv + deps
    venv_path = brain_dir / ".venv"
    if not venv_path.exists():
        print("📦 Creating Python venv...")
        run(f"python3 -m venv {venv_path}")
        pip = venv_path / "bin" / "pip"
        print("📦 Installing dependencies...")
        run(f"{pip} install lancedb numpy pyarrow requests --quiet")
        print("✅ Dependencies installed")
    else:
        print("⏭️  Venv already exists — skipping")

    # 6. Create requirements.txt
    req_path = brain_dir / "requirements.txt"
    if not req_path.exists():
        req_path.write_text("lancedb>=0.29.0\nnumpy>=1.24.0\npyarrow>=12.0.0\nrequests>=2.28.0\n")

    # 7. Add AGENTS.md instructions (append if file exists)
    agents_path = WORKSPACE / "AGENTS.md"
    cms_note = """
## 🧠 Brain CMS — Memory Architecture

This workspace uses the Continuum Memory System. Full instructions in `memory/INDEX.md`.

**Boot:** Load MEMORY.md + today's daily log. Nothing else.
**On topic:** Read INDEX.md → load relevant schemas → check ANCHORS.md if CRITICAL.
**Semantic search:** `memory_brain/.venv/bin/python3 memory_brain/query_memory.py "text" --sources-only`
**Sleep:** NREM on shutdown → `memory_brain/.venv/bin/python3 memory_brain/nrem.py`
**Weekly:** REM on Sunday → `memory_brain/.venv/bin/python3 memory_brain/rem.py`
"""
    if agents_path.exists():
        content = agents_path.read_text()
        if "Brain CMS" not in content:
            agents_path.write_text(content + cms_note)
            print("✅ AGENTS.md updated with CMS instructions")
    else:
        agents_path.write_text(f"# AGENTS.md\n{cms_note}")
        print("✅ AGENTS.md created")

    print("\n" + "=" * 50)
    print("✅ Brain CMS installed successfully!")
    print("\nNext steps:")
    print("  1. Index your schemas:")
    print(f"     cd {brain_dir} && .venv/bin/python3 index_memory.py")
    print("  2. Test retrieval:")
    print(f"     .venv/bin/python3 query_memory.py 'your topic' --sources-only")
    print("  3. Read INDEX.md and add your first schema")
    print("\n🧠 Your agent now has a proper brain.\n")

if __name__ == "__main__":
    main()
