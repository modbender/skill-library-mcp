# clawd-migrate

Migrate from **moltbot** or **clawdbot** to **openclaw**. Preserves config, memory, and clawdbook (Moltbook) data. Works on any system.

---

## Quick start

**Requirements:** Node.js 14+ and Python 3.x. Works on **Windows**, **macOS**, and **Linux**.

```bash
npx clawd-migrate
```

That starts the **interactive menu** (lobster + guided steps). For full install options and all commands, see **[HOW_TO_RUN.md](HOW_TO_RUN.md)**.

---

## What it does

- **Discovers** your existing bot assets (memory files, config, clawdbook/Moltbook).
- **Backs up** everything into a timestamped folder before any changes.
- **Migrates** your files into the openclaw layout: `memory/`, `.config/openclaw/`, `.config/clawdbook/`, and preserves `projects/`.
- **Verifies** every source file was copied to its destination (file existence + size match).
- **Reinstalls openclaw** (`npm i -g openclaw`) and runs `openclaw onboard` automatically at the end of migration.

Supports both **moltbot** and **clawdbot** source layouts; no machine-specific paths.

---

## Install and run

| Method | Command |
|--------|--------|
| Run without installing | `npx clawd-migrate` |
| Install globally | `npm install -g clawd-migrate` then `clawd-migrate` |
| Install in a project | `npm install clawd-migrate` then `npx clawd-migrate` |

Full details, CLI options, and Python-only usage: **[HOW_TO_RUN.md](HOW_TO_RUN.md)**.

---

## Commands (CLI)

```bash
clawd-migrate                    # Interactive menu (default)
clawd-migrate discover [--root PATH]
clawd-migrate backup [--root PATH] [--backup-dir PATH]
clawd-migrate migrate [--root PATH] [--no-backup] [--output PATH] [--setup-openclaw] [--skip-verify]
```

`--root` defaults to the current directory. Migration now **automatically verifies** all files and **reinstalls openclaw** at the end. Use `--skip-verify` to skip verification (not recommended).

---

## What gets migrated

- **Memory/identity:** SOUL.md, USER.md, TOOLS.md, IDENTITY.md, AGENTS.md, MEMORY.md  
- **Config:** `.config/moltbook/`, `.config/moltbot/` (credentials and API keys)  
- **Clawdbook/Moltbook:** Kept under `.config/clawdbook` in the openclaw layout  
- **Extra:** `projects/` (if present)

Backups go under `backups/` (or `--backup-dir`) with prefix `openclaw_migrate_backup_`.

---

## Tests

From the repo root:

```bash
npm test
```

Runs Python unit tests for discover, backup, and migrate.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [HOW_TO_RUN.md](HOW_TO_RUN.md) | **How to run** – install, interactive mode, CLI, examples |
| [Documentation/GITHUB.md](Documentation/GITHUB.md) | Publishing this repo to GitHub |
| [Documentation/NPM_PUBLISH.md](Documentation/NPM_PUBLISH.md) | Publishing to npm |
| [Documentation/TESTS.md](Documentation/TESTS.md) | Running and writing tests |
| [Documentation/MIGRATION_SOURCES.md](Documentation/MIGRATION_SOURCES.md) | Moltbot/clawdbot support |
| [Documentation/MIGRATION_TUI.md](Documentation/MIGRATION_TUI.md) | Interactive TUI (lobster + menu) |
| [Documentation/VERIFICATION.md](Documentation/VERIFICATION.md) | Post-migration file verification |

---

## License

MIT
