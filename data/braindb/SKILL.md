---
name: braindb
version: 0.5.0
description: Persistent, semantic memory for AI agents. Gives your AI long-term recall that survives compaction and session resets — 98% accuracy, 20ms latency.
homepage: https://github.com/Chair4ce/braindb
license: MIT
author: Oaiken LLC
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "requires": {
        "bins": ["docker", "node"],
        "env": [],
        "configPaths": ["~/.openclaw/openclaw.json"]
      },
      "permissions": {
        "configWrite": true,
        "workspaceRead": true,
        "networkOptional": "Migration with --swarm sends file contents to Google Gemini API. Default migration is fully local."
      },
      "install": [
        {
          "id": "release-download",
          "kind": "download",
          "url": "https://github.com/Chair4ce/braindb/releases/download/v0.5.0/braindb-v0.5.0.zip",
          "archive": "zip",
          "extract": true,
          "stripComponents": 1,
          "targetDir": "~/.openclaw/plugins/braindb",
          "label": "Download BrainDB v0.5.0",
          "postInstall": "cd ~/.openclaw/plugins/braindb && bash install.sh"
        }
      ],
      "uninstall": "cd ~/.openclaw/plugins/braindb && bash uninstall.sh"
    }
  }
---

# BrainDB

Persistent, semantic memory for AI agents. Built for [OpenClaw](https://github.com/openclaw/openclaw).

---

## What It Does

Your AI forgets everything between sessions. BrainDB fixes that.

It gives your assistant a memory system that automatically captures important context from conversations and recalls it when relevant — who you are, what you're working on, what you've told it before. Memories persist across compaction, session resets, and restarts.

**How it works:**
```
You say something → OpenClaw captures important facts → BrainDB stores them
You ask something → OpenClaw recalls relevant memories → AI has context
```

No commands. No manual saving. It just works.

---

## Install

Requires Docker and ~4 GB RAM.

```bash
openclaw plugin install braindb
```

Or manually:
```bash
git clone https://github.com/Chair4ce/braindb.git ~/.openclaw/plugins/braindb
cd ~/.openclaw/plugins/braindb
bash install.sh
```

First run: 3–5 minutes (downloads embedding model). After that: ~10 seconds.

**What the installer does:**
1. Backs up your existing memory files to `~/.openclaw/braindb-backup/`
2. Builds and starts 3 Docker containers (Neo4j, embedder, gateway)
3. Patches your OpenClaw config (`~/.openclaw/openclaw.json`) to enable the plugin
4. Optionally offers to migrate existing workspace files into BrainDB

Review `install.sh` before running if you want to understand each step.

---

## What You Get

- **768-dim semantic search** — finds conceptually related memories, not just keyword matches
- **4 memory types** — episodic (events), semantic (facts), procedural (skills), association (links)
- **Tiered ranking** — semantic similarity always beats keyword match
- **Auto-dedup** — won't store near-duplicate memories
- **Hebbian reinforcement** — memories strengthen with use, decay without it
- **Query expansion** — understands colloquial phrases
- **98% recall accuracy** on a 50-test benchmark suite
- **12–20 ms** average query latency

---

## Security & Privacy

**Core operation is fully local:**
- Gateway binds to **localhost only** — not exposed to your network
- Neo4j and embedder are **not accessible** from the host (isolated Docker network)
- Neo4j password is **auto-generated** (24-char random)
- Optional **API key authentication** via `BRAINDB_API_KEY`
- Containers run as **non-root** users
- All embedding, search, and storage runs locally — no external API calls during normal operation

**What the installer reads/writes:**
- Reads your OpenClaw config (`~/.openclaw/openclaw.json`) to add the plugin entry
- Reads workspace files during optional migration (preview with `--scan` first)
- Writes `.env` with generated Neo4j credentials
- Creates Docker volumes for persistent storage

**Migration privacy notice:**
- **Default migration (`--no-swarm`):** Fully local. File contents never leave your machine.
- **Migration with swarm:** Sends file contents to Google's Gemini API for intelligent fact extraction. This is **opt-in only** — you must have swarm installed and explicitly allow it. Use `--no-swarm` to guarantee local-only processing.
- Always run `node migrate.cjs --scan` or `--dry-run` first to see exactly what would be processed.

---

## Migrating Existing Memories

Already have `MEMORY.md`, daily notes, or other workspace files? Import them:

```bash
node migrate.cjs --scan /path/to/workspace   # Preview files (no data sent anywhere)
node migrate.cjs --dry-run /path/to/workspace # Extract facts locally, don't encode
node migrate.cjs --no-swarm /path/to/workspace # Import, fully local
node migrate.cjs /path/to/workspace           # Import (uses swarm if available)
```

Your files are never modified. BrainDB copies facts from them — it doesn't replace anything.

---

## Failover

BrainDB fails gracefully:

1. **Gateway down:** OpenClaw works normally — the memory block is simply absent from prompts. Your AI still has `MEMORY.md` and workspace files.
2. **Neo4j down:** Gateway returns empty results. No errors, just no memories.
3. **Embedder down:** Falls back to text-only search (less accurate but functional).

Your workspace files are the safety net. BrainDB is additive — remove it and you're back to defaults with zero data loss.

---

## Uninstall

```bash
openclaw plugin remove braindb
```

The uninstaller exports all memories (JSON + readable markdown), stops containers, removes the plugin config from OpenClaw, and leaves your workspace files untouched. Docker volumes are preserved until you explicitly delete them.

---

## Performance

| Metric | Value |
|--------|-------|
| Recall accuracy | 98% (50-test suite) |
| Avg latency | 12–20 ms |
| Cold query | ~60 ms |
| Capacity | 10K+ memories |
| Storage | ~3 GB |
| RAM | ~2.5 GB |

---

## Links

- [Documentation](https://github.com/Chair4ce/braindb#readme)
- [OpenClaw](https://github.com/openclaw/openclaw)

---

MIT — [Oaiken LLC](https://oaiken.com)
