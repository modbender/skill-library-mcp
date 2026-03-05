# How to run clawd-migrate

This guide covers every way to run **clawd-migrate**: via npm (recommended), with Python only, and all commands and options.

---

## What you need

- **Node.js** 14 or newer (for the npm command)
- **Python** 3.x (the migration tool runs on Python)

Works on **Windows**, **macOS** (Terminal or iTerm2), and **Linux**. Make sure both are installed and on your PATH:

```bash
node --version   # v14+
python --version # 3.x (Windows)
python3 --version # 3.x (macOS/Linux)
```

---

## Option 1: Run with npm (recommended)

No clone required. Run directly from the npm registry:

```bash
npx clawd-migrate
```

That starts the **interactive menu** (lobster + guided steps). To run a single command:

```bash
npx clawd-migrate discover
npx clawd-migrate backup
npx clawd-migrate migrate
```

### Install globally (optional)

If you want a short command everywhere:

```bash
npm install -g clawd-migrate
clawd-migrate
```

### Install in a project

```bash
npm install clawd-migrate
npx clawd-migrate
# or from package.json scripts: "migrate": "clawd-migrate"
```

---

## Option 2: Run with Python only

If you cloned the repo or have the Python package locally:

### From the repo (development)

From the **parent** of the `clawd_migrate` folder (so Python can find the package):

```bash
cd path/to/parent
PYTHONPATH=. python -m clawd_migrate
```

Or with a specific command:

```bash
PYTHONPATH=. python -m clawd_migrate discover --root path/to/your/bot
PYTHONPATH=. python -m clawd_migrate backup --root path/to/your/bot
PYTHONPATH=. python -m clawd_migrate migrate --root path/to/your/bot
```

### If you installed via pip (e.g. from PyPI)

```bash
python -m clawd_migrate
python -m clawd_migrate discover
python -m clawd_migrate migrate
```

---

## Interactive mode (default)

When you run `clawd-migrate` with no arguments, you get:

1. A **lobster** and welcome message  
2. A prompt to choose the **working directory** (default: current directory)  
3. A **menu**:
   - **1** – Discover assets (list config, memory, clawdbook)
   - **2** – Create backup only
   - **3** – Full migration (backup first, then migrate)
   - **4** – Migrate without backup (not recommended)
   - **5** – Change working directory
   - **q** – Quit

Use this when you want to explore and migrate step by step.

---

## CLI reference

All commands can be run from the terminal with optional flags.

### Discover

List what would be migrated (no changes made):

```bash
clawd-migrate discover [--root PATH]
```

- `--root` – Directory to scan (default: current directory).

### Backup

Create a timestamped backup only (no migration):

```bash
clawd-migrate backup [--root PATH] [--backup-dir PATH]
```

- `--root` – Source directory (default: current directory).  
- `--backup-dir` – Where to put the backup folder (default: `root/backups`).

### Migrate

Migrate your files into the openclaw layout (optionally create a backup first). Migration **does not** install openclaw; it only copies your assets into `memory/`, `.config/openclaw/`, `.config/clawdbook/`, and `projects/`. After migration you can install openclaw and run `openclaw onboard` in that directory so openclaw is set up with your files in place.

```bash
clawd-migrate migrate [--root PATH] [--no-backup] [--output PATH] [--setup-openclaw]
```

- `--root` – Source directory (default: current directory).  
- `--no-backup` – Skip backup (not recommended).  
- `--output` – Where to write openclaw layout (default: same as `--root`).  
- `--setup-openclaw` – After migration, run `npm i -g openclaw` and `openclaw onboard` in the output directory.

In the **interactive menu**, after a successful migration you’ll be prompted: “Install openclaw and run openclaw onboard in this directory? [Y/n]”. If you say yes, the tool runs `npm i -g openclaw` and then `openclaw onboard` in the migrated directory so your existing files and openclaw’s new structure are combined.

---

## Examples

**Discover what’s in the current directory:**

```bash
npx clawd-migrate discover
```

**Backup a bot that lives in `~/my-bot`:**

```bash
npx clawd-migrate backup --root ~/my-bot
```

**Full migration with backup (recommended):**

```bash
npx clawd-migrate migrate --root ~/my-bot
```

**Migrate into a different directory:**

```bash
npx clawd-migrate migrate --root ~/my-bot --output ~/openclaw-bot
```

**Migrate and then install openclaw and run onboard in the same directory:**

```bash
npx clawd-migrate migrate --root ~/my-bot --setup-openclaw
```

That runs migration, then `npm i -g openclaw` and `openclaw onboard` in the migrated directory so openclaw is set up with your files in place.

---

## What gets migrated

- **Memory/identity:** SOUL.md, USER.md, TOOLS.md, IDENTITY.md, AGENTS.md, MEMORY.md  
- **Config:** `.config/moltbook/`, `.config/moltbot/` (credentials, API keys)  
- **Clawdbook/Moltbook:** Stored under `.config/clawdbook` in the openclaw layout  
- **Extra:** `projects/` (if present)

Backups go under `backups/` (or your `--backup-dir`) with the prefix `openclaw_migrate_backup_`.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `Python not found` | Install Python 3 and add it to your PATH. The npm package needs Python to run. |
| `clawd-migrate: command not found` | Use `npx clawd-migrate` instead of `clawd-migrate`, or install globally with `npm install -g clawd-migrate`. |
| Nothing discovered | Run from (or set `--root` to) the directory that contains your bot’s SOUL.md, USER.md, or .config. |
| Permission errors | Run from a directory you can write to; avoid system-protected folders. |

For more detail, see [README.md](README.md) and the [Documentation](Documentation/) folder.
