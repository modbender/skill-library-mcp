# Libby book monitor - get notified when books arrive in your library's catalog

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-purple)

> **[Agent Skills](https://agentskills.io) format** - works with OpenClaw, Claude, Cursor, Codex, and other compatible clients

Track book availability on [Libby/OverDrive](https://www.overdrive.com/) libraries. Search catalogs, manage a watchlist, and get notified when books are added to your library's collection.

## The problem

Libby notifies you when a hold becomes available. It does not notify you when a book is *added* to your library. If you're waiting for a new release that isn't in the catalog yet, your only option is to keep checking manually - and if you forget, someone else places a hold first and you're waiting months.

This tool watches for books that aren't in your library yet and tells you the moment they appear - before there's a waitlist.

## Installation

```bash
npx skills add alexpolonsky/agent-skill-libby-book-monitor
```

<details>
<summary>Manual install (any agent skills client)</summary>

```bash
# OpenClaw
git clone https://github.com/alexpolonsky/agent-skill-libby-book-monitor ~/.openclaw/skills/libby-book-monitor

# Claude
git clone https://github.com/alexpolonsky/agent-skill-libby-book-monitor ~/.claude/skills/libby-book-monitor

# Cursor
git clone https://github.com/alexpolonsky/agent-skill-libby-book-monitor ~/.cursor/skills/libby-book-monitor
```

</details>

<details>
<summary>Standalone CLI</summary>

```bash
git clone https://github.com/alexpolonsky/agent-skill-libby-book-monitor
cd agent-skill-libby-book-monitor
python3 scripts/libby-book-monitor.py search nypl "The Travelling Cat Chronicles"
```

Requires Python 3.9+ with no external dependencies.

</details>

## What you can ask

> "Is 'The Travelling Cat Chronicles' by Hiro Arikawa available at my library yet?"

- "Add 'Tomorrow, and Tomorrow, and Tomorrow' to my Libby watchlist"
- "Which books on my watchlist are now available?"
- "Check if any book on my list has shown up in the catalog this week"
- "Search for anything by Kazuo Ishiguro at my library"

Or use the CLI directly:
```bash
python3 scripts/libby-book-monitor.py search nypl "The Travelling Cat Chronicles"
python3 scripts/libby-book-monitor.py watch "The Travelling Cat Chronicles" --author "Hiro Arikawa"
```

## Automation examples

Ask your AI agent to set up recurring checks:

- "Every morning, check my Libby watchlist and tell me if anything new has appeared in the catalog"
- "Let me know the moment 'The Travelling Cat Chronicles' becomes available at my library"
- "Check my watchlist once a day and send me a notification if any book is newly available so I can place a hold before the waitlist builds up"

## Commands

| Command | Description |
|---------|-------------|
| `search <library> <query>` | Search a library catalog by title or author |
| `watch <title>` | Add a book to the watchlist |
| `unwatch <title>` | Remove a book from the watchlist |
| `list` | Show the watchlist with current status |
| `check` | Check all watchlist books against the API |

<details>
<summary>Options</summary>

| Option | Commands | Description |
|--------|----------|-------------|
| `--profile <name>` | all | Separate watchlist per user |
| `--author <name>` | watch | Specify book author |
| `--library <code>` | watch | Library code (default: from config) |
| `--notify` | check | Only print newly found books (for cron/automation) |
| `--data-dir <path>` | all | Custom data directory |

</details>

## Finding your library code

Your library's OverDrive code is the subdomain from its OverDrive site:

| Library | Code |
|---------|------|
| New York Public Library | `nypl` |
| Israel Digital | `telaviv` |
| Toronto Public Library | `toronto` |
| LA Public Library | `lapl` |

<details>
<summary>More libraries</summary>

| Library | URL | Code |
|---------|-----|------|
| Brooklyn Public Library | brooklyn.overdrive.com | `brooklyn` |
| Seattle Public Library | spl.overdrive.com | `spl` |
| Chicago Public Library | chipublib.overdrive.com | `chipublib` |
| The Libraries Consortium (UK) | tlc.overdrive.com | `tlc` |
| Minuteman Library Network | minuteman.overdrive.com | `minuteman` |

Not sure about your library? Search for it on [overdrive.com/libraries](https://www.overdrive.com/libraries).

</details>

## Automation

Use `--notify` to only get output when something new appears - perfect for scheduled checks:

```bash
# crontab -e
0 9 * * * /usr/bin/python3 /path/to/scripts/libby-book-monitor.py check --notify
```

Pair with any notification tool (email, ntfy, pushover, etc.):

```bash
0 9 * * * /usr/bin/python3 /path/to/scripts/libby-book-monitor.py check --notify | \
  ifne mail -s "New on Libby" you@example.com
```

With [OpenClaw](https://github.com/openclaw/openclaw), you can manage your watchlist conversationally - just message your agent "add Dune to my Libby watchlist" or "check if any new books appeared on Libby". OpenClaw can also run daily checks automatically and notify you when something new shows up.

<details>
<summary>Profiles</summary>

Use `--profile` to maintain separate watchlists for different people:

```bash
python3 scripts/libby-book-monitor.py --profile jane watch "Dune"
python3 scripts/libby-book-monitor.py --profile bob watch "Tomorrow, and Tomorrow, and Tomorrow"

python3 scripts/libby-book-monitor.py --profile jane check
python3 scripts/libby-book-monitor.py --profile bob list
```

</details>

<details>
<summary>Configuration</summary>

Data is stored in `~/.libby-book-monitor/` by default. Override with `--data-dir` or `LIBBY_BOOK_MONITOR_DATA` env var.

A config file is created on first run at `~/.libby-book-monitor/config.json`:

```json
{
  "default_library": "telaviv",
  "libraries": {
    "telaviv": "Israel Digital"
  }
}
```

Edit `default_library` to set your preferred library.

</details>

<details>
<summary>Output example</summary>

```bash
$ python3 scripts/libby-book-monitor.py search telaviv "Project Hail Mary"
Searching "Project Hail Mary" in telaviv...

  1. Project Hail Mary - Andy Weir
     In catalogue | Copies: 8 | Available: No

3 result(s) total

$ python3 scripts/libby-book-monitor.py list
Watchlist (2 books):

    1. Kafka on the Shore
       Author: Haruki Murakami
       Library: nypl | Status: not_found | Checked: 2026-02-13T09:00:05

  * 2. Project Hail Mary
       Author: Andy Weir
       Library: telaviv | Status: found | Checked: 2026-02-13T09:00:07
       Found on: 2026-02-13
```

</details>

## How it works

Uses the [OverDrive Thunder API](https://thunder.api.overdrive.com/v2/) - the same API that powers the Libby web app's catalog search. No authentication required for searching (read-only access to public catalog data). A book is considered "in the catalog" when the API returns it with `isOwned: true`.

## Limitations

- Title matching uses substring comparison - very short or common titles may false-match
- The Thunder API is unofficial (used internally by Libby) but has been stable for years
- Cannot borrow books or place holds (those require authentication)

## Legal

Independent open-source tool. Not affiliated with or endorsed by OverDrive/Libby. Catalog data comes from the same APIs that power the Libby web app and may not reflect real-time availability. This tool searches catalogs only - it does not borrow books or place holds. Provided "as is" without warranty of any kind.

## Author

[Alex Polonsky](https://alexpolonsky.com) - [GitHub](https://github.com/alexpolonsky) - [LinkedIn](https://www.linkedin.com/in/alexpolonsky/) - [Twitter/X](https://x.com/alexpo)

Part of [Agent Skills](https://github.com/alexpolonsky/agent-skills) - [Specification](https://agentskills.io/specification)
