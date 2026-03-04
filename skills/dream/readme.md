# Dream — OpenClaw Memory Distillation Skill

> Actively maintains your `MEMORY.md` so OpenClaw truly remembers you.

---

## What problem does it solve

OpenClaw's native memory mechanism has three unhandled issues:

**1. MEMORY.md grows indefinitely and silently truncates**
OpenClaw truncates MEMORY.md at 20,000 characters — no error, no warning. The AI quietly loses the second half of your context. You think it remembers, but it doesn't. Dream triggers compression at 18,000 characters, archiving stale content to the ledger so MEMORY.md always stays within the effective range.

**2. No permanent archive**
Important memories disappear once cleaned up. Dream maintains a `ledger.md` — append-only, never deleted. Anything that has ever reached long-term memory is preserved forever, even after being forgotten, and remains searchable for deep recall.

**3. No Re-emergence detection**
You deliberately clear a memory, but it surfaces again in later conversations — that means it mattered more than you thought. Dream detects this "forgotten then re-emerged" pattern, automatically rewrites the entry into memory, and elevates its priority.

---

## How it works

```
memory/YYYY-MM-DD.md        ← Written automatically by OpenClaw (compaction flush)
         │
         │  Daily at 03:30, Dream reads and distills
         ▼
     MEMORY.md               ← Actively maintained by Dream, hard limit 18,000 chars
         │
         │  Important but expired content
         ▼
     ledger.md               ← Permanent archive, append-only, never deleted
```

**Dream is a distiller, not a capturer.**
Capture is handled by OpenClaw's native compaction flush. Search is handled by the native `openclaw memory search`. Dream only does what the native system doesn't: distillation, compression, archiving, and Re-emergence detection.

---

## File structure

After installation, the following files are created:

```
~/.openclaw/workspace/
└── MEMORY.md                    ← Maintained by Dream (existing file, Dream takes over)

~/Documents/Obsidian/dream-vault/    ← Configured via DREAM_VAULT_PATH
├── ledger.md                    ← Permanent archive
├── ledger-index.json            ← Structured index for archive search
├── meta/
│   ├── active-days.json         ← Active day log
│   ├── last-review.txt          ← Last distillation timestamp
│   ├── dream-state.txt          ← System state
│   ├── removed-entries.json     ← Re-emergence tracking
│   └── review-YYYY-MM.md        ← Monthly distillation log
└── obsidian-index/
    ├── _index.md                ← Main content index
    └── topics/<topic>.md        ← Topic-based content index
```

---

## Installation

### Prerequisites

- OpenClaw (Node ≥ 22, Gateway port 18789)
- `jq` (JSON processing)
- `wc` (character count, built-in)
- `md5sum` or `md5` (hashing, built-in)

```bash
# macOS
brew install jq

# Linux
apt install jq
```

### Steps

```bash
# 1. Clone into OpenClaw skills directory
cd ~/.openclaw/workspace/skills
git clone https://github.com/teman2050/dream-skill dream

# 2. Make the script executable
chmod +x dream/dream-tools.sh

# 3. Set vault path (add to your shell config)
echo 'export DREAM_VAULT_PATH="$HOME/Documents/Obsidian/dream-vault"' >> ~/.zshrc
source ~/.zshrc

# 4. Initialize
./dream/dream-tools.sh --init

# 5. Restart OpenClaw gateway to load the skill
openclaw gateway restart
```

### Configure scheduled distillation

Add the following to the end of your `SOUL.md`:

```markdown
## Dream Schedule
Run dream review --scheduled every day at 03:30
```

---

## Usage

### Automatic (recommended)

No action needed after installation. Dream distills at 03:30 every night, runs silently, and never interrupts you.

### Manual trigger

Say any of the following in an OpenClaw conversation:

| You say | Dream does |
|---------|------------|
| `dream` / `review` | Run distillation immediately |
| `what do you remember about me` | Show current MEMORY.md snapshot |
| `dream status` | Show system status |
| `dream search <keyword>` | Search memory + permanent archive + Obsidian index |
| `dream index <content>` | Save an article or webpage to Obsidian index |
| `dream forget <description>` | Remove from memory (archive is kept) |
| `dream init` | First-time setup guide |

---

## What is `dream-tools.sh`

This is Dream's execution engine. **The AI handles semantic judgment; the script handles precise execution.**

File operations, date calculations, character counting, and atomic writes are delegated to the shell script rather than the AI — because AI miscalculates date arithmetic, atomic file replacement requires shell-level `mv`, and character counting needs `wc`, not estimation.

| Command | Purpose |
|---------|---------|
| `--check-idle` | Check if OpenClaw is idle (5s timeout, defaults to busy) |
| `--check-size` | Return MEMORY.md character count and compression state |
| `--hash` | Generate 8-char short hash for entry ID and dedup |
| `--atomic-write` | Atomically replace a file; validates char limit for MEMORY.md |
| `--ledger-append` | Append a record to the permanent archive |
| `--ledger-search` | Keyword search in the archive index |
| `--ledger-mark-reemergence` | Mark a ledger entry as re-emerged |
| `--record-removed` | Log a removed MEMORY.md entry for Re-emergence tracking |
| `--check-reemergence` | Detect if new content resembles a previously forgotten entry |
| `--record-active-day` | Record today as an active day (deduped) |
| `--active-days-since` | Count active days since a given date |
| `--dedup-index` | Check if a URL already exists in the Obsidian index |
| `--init` | Initialize Dream vault directory structure |
| `--status` | Print system status summary (low IO, meta-only reads) |

---

## MEMORY.md structure

Dream maintains MEMORY.md in four sections:

```markdown
## Current State
Ongoing projects, pending decisions, recent important changes

## Stable Profile
Tech stack, work environment, decision style, core preferences

## Relationships & Context
Important people, ongoing collaborations

## Dream
(Auto-maintained) Last 5 ledger entries as one-line summaries
```

---

## Relationship with other memory skills

Dream **does not conflict** with existing memory skills — it fills the gaps:

- **rosepuppy/memory-complete**: handles real-time capture, writes to `memory/YYYY-MM-DD.md`
  → Dream reads those files for distillation — complementary, can coexist

- **openclaw native memory search**: handles daily search
  → `dream search` calls the native command, does not build its own index

- **Using Dream standalone**: OpenClaw's native compaction flush already writes `memory/YYYY-MM-DD.md`, no additional skill needed

---

## Security

- All file operations are strictly scoped to `DREAM_VAULT_PATH` and the OpenClaw workspace
- `dream-tools.sh` makes no network calls and uses no external APIs
- `dream forget` only clears active memory; the permanent archive is unaffected
- Atomic writes (tmp → mv) prevent file corruption on crash

---

## License

MIT
