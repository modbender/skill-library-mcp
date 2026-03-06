---
name: kmoe-manga-download
description: Download manga from Kmoe (kxx.moe / mox.moe) with concurrent downloads, credential management, and automation callbacks.
metadata:
  openclaw:
    emoji: "\U0001F4DA"
    requires:
      bins:
        - kmdr
    install:
      - id: pip-kmdr
        kind: pip
        package: kmoe-manga-downloader
        bins:
          - kmdr
        label: "Install kmoe-manga-downloader via pip (requires Python >= 3.9)"
---

# Kmoe Manga Downloader

Download manga from Kmoe (kxx.moe / mox.moe) as EPUB or MOBI files using the `kmdr` CLI.

> **Prerequisite**: This skill requires the `kmdr` command-line tool. Install it with:
> ```bash
> pip install kmoe-manga-downloader
> ```
> Requires Python >= 3.9.

## When to Use This Skill

Activate when the user:
- Wants to download manga from Kmoe / kxx.moe / mox.moe
- Asks to batch-download manga volumes
- Needs to manage Kmoe account credentials or credential pools
- Wants to automate post-download actions (e.g., move files, send notifications)

## Quick Start

```bash
# 1. Log in to Kmoe
kmdr login -u <username> -p <password>

# 2. Download volumes 1-3 of a manga
kmdr download -l https://kxx.moe/c/50076.htm -v 1-3 -d ~/manga
```

## Commands

### Authentication

```bash
# Log in (password prompted if omitted)
kmdr login -u <username> [-p <password>]

# Check account status and download quota
kmdr status
```

### Download

```bash
kmdr download -l <book-url> -v <volumes> [options]
```

**Required flags:**
- `-l, --book-url` — Manga homepage URL on Kmoe
- `-v, --volume` — Volume selection: `1,2,3` or `1-5,8` or `all`

**Common options:**

| Flag | Description | Default |
|---|---|---|
| `-d, --dest` | Download directory | config or current dir |
| `-t, --vol-type` | Volume type: `vol`, `extra`, `seri`, `all` | `vol` |
| `-f, --format` | Output format: `epub` or `mobi` | `epub` |
| `-r, --retry` | Retry attempts on failure | `3` |
| `-m, --method` | Download method: `1` or `2` | `1` |
| `--num-workers` | Concurrent download workers | `8` |
| `-P, --use-pool` | Use credential pool with failover | off |
| `-p, --proxy` | Proxy server address | none |
| `-c, --callback` | Post-download callback script | none |

### Configuration

```bash
# Set default options
kmdr config --set proxy=http://localhost:7890 dest=~/manga

# List current config
kmdr config -l

# Clear all config
kmdr config -c all

# Switch mirror source
kmdr config -b https://mox.moe
```

### Credential Pool

Manage multiple accounts for failover when one account's quota is exhausted.

```bash
# Add account to pool
kmdr pool add -u <username> [-o <priority>] [-n "note"]

# List pool accounts (with optional quota refresh)
kmdr pool list [-r] [--num-workers 3]

# Switch active account
kmdr pool use <username>

# Update account info
kmdr pool update <username> [-n "note"] [-o <priority>]

# Remove account from pool
kmdr pool remove <username>
```

## Examples

### Download specific volumes

```bash
kmdr download -d ~/manga -l https://kxx.moe/c/50076.htm -v 1-5
```

### Download all extras as MOBI

```bash
kmdr download -l https://kxx.moe/c/50076.htm -t extra -v all -f mobi
```

### Download with callback

Post-download callbacks support template variables:
- `{v.name}` — Volume name
- `{v.page}` — Page count
- `{v.size}` — File size
- `{b.name}` — Book/manga name
- `{b.author}` — Author name

```bash
kmdr download -l https://kxx.moe/c/50076.htm -v 1-3 \
  --callback "echo '{b.name} - {v.name} done!' >> ~/kmdr.log"
```

### Use credential pool for large batch

```bash
kmdr pool add -u user1 -o 1 -n "main account"
kmdr pool add -u user2 -o 2 -n "backup"
kmdr download -l https://kxx.moe/c/50076.htm -v all --use-pool
```

### Download via proxy

```bash
kmdr download -l https://kxx.moe/c/50076.htm -v 1-10 -p http://localhost:7890
```

## Error Handling

| Problem | Solution |
|---|---|
| Not logged in | Run `kmdr login -u <username>` first |
| Download quota exhausted | Use `--use-pool` with multiple accounts, or wait for quota reset |
| Network timeout | Increase `--retry` count, or set a proxy with `-p` |
| Volumes not found | Check `-t` flag — the volume may be under `extra` or `seri` type |
| Mirror unavailable | Switch mirror with `kmdr config -b https://mox.moe` |

## Tips

- **Set defaults once**: Use `kmdr config --set dest=~/manga proxy=http://localhost:7890` to avoid repeating flags
- **Credential pool**: For large downloads, set up multiple accounts with `kmdr pool add` to avoid hitting quota limits
- **Volume types**: Manga on Kmoe may have `vol` (main volumes), `extra` (bonus chapters), and `seri` (serialized chapters) — use `-t all` to get everything
- **Callback automation**: Use callbacks to trigger file organization, notifications, or syncing after each volume downloads
