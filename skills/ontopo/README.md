# Ontopo restaurant search - find available tables across date ranges in one query

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-purple)

> **[Agent Skills](https://agentskills.io) format** - works with OpenClaw, Claude, Cursor, Codex, and other compatible clients

Search Israeli restaurants, check table availability across date ranges, view menus, and get direct booking links via Ontopo.

## The problem

Ontopo makes you browse availability one day at a time, clicking through calendars for each restaurant. Want to find any open table next Wednesday through Saturday at 19:00? That's 4 days x however many restaurants you're considering. Each one is a separate manual search.

This tool searches across date ranges, multiple restaurants, and patterns like "every Friday evening" in a single query - then gives you a direct booking link.

## Installation

```bash
npx skills add alexpolonsky/agent-skill-ontopo
```

<details>
<summary>Manual install (any agent skills client)</summary>

```bash
# OpenClaw
git clone https://github.com/alexpolonsky/agent-skill-ontopo ~/.openclaw/skills/ontopo

# Claude
git clone https://github.com/alexpolonsky/agent-skill-ontopo ~/.claude/skills/ontopo

# Cursor
git clone https://github.com/alexpolonsky/agent-skill-ontopo ~/.cursor/skills/ontopo
```

</details>

<details>
<summary>Standalone CLI</summary>

```bash
git clone https://github.com/alexpolonsky/agent-skill-ontopo
cd agent-skill-ontopo
pip install httpx
python3 scripts/ontopo-cli.py search "taizu"
```

Requires Python 3.9+ and httpx (`pip install httpx`).

</details>

## What you can ask

> "What restaurants are available for 4 people in Tel Aviv this Saturday at 8pm?"

- "Is Mashya available any night this weekend for 2?"
- "Which Tel Aviv restaurants have tables for 6 available this Friday or Saturday?"
- "What's available in Herzliya this Thursday evening for 2?"
- "Check if Taizu has anything available this month on a weekday"

Or use the CLI directly:
```bash
python3 scripts/ontopo-cli.py available friday 19:00 --city tel-aviv
```

## Automation examples

Ask your AI agent to set up recurring checks:

- "Every Sunday morning, check if there are any available tables for 2 in Tel Aviv on the coming Friday or Saturday and let me know what you find"
- "Check every day and alert me if a table opens up at Mashya this month for 2 people"
- "Before each weekend, check availability at a few good restaurants in Tel Aviv for Friday or Saturday evening and send me a summary"

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search venues by name |
| `available <date> <time>` | Find venues with availability |
| `check <venue> <date> [time]` | Check specific venue availability |
| `range <venue> <start> <end>` | Check availability over date range |
| `menu <venue>` | View venue menu |
| `info <venue>` | Get venue details |
| `url <venue>` | Get booking URL |
| `cities` | List supported cities |
| `categories` | List venue categories |

<details>
<summary>Options</summary>

| Option | Commands | Description |
|--------|----------|-------------|
| `--json` | all | Output in JSON format |
| `--locale en\|he` | search, info, url | Language (English or Hebrew) |
| `--city` | available, search | City filter |
| `--party-size` | available, check, range | Number of guests (default: 2) |

</details>

<details>
<summary>Date/time formats</summary>

- **Dates**: `YYYY-MM-DD`, `today`, `tomorrow`, `+N` (days from now)
- **Times**: `HH:MM`, `HHMM`, `7pm`, `19:30`

</details>

<details>
<summary>Supported cities</summary>

tel-aviv, jerusalem, haifa, herzliya, raanana, ramat-gan, netanya, ashdod, ashkelon, beer-sheva, eilat, modiin, rehovot, rishon-lezion, petah-tikva, holon, kfar-saba, hod-hasharon, caesarea

</details>

<details>
<summary>Output example</summary>

```bash
$ python3 scripts/ontopo-cli.py search "taizu"
taizu-tel-aviv-jaffa
  Taizu - Asian Fusion
  Tel Aviv - $$$$

$ python3 scripts/ontopo-cli.py check taizu tomorrow 19:00
Checking taizu-tel-aviv-jaffa for 2025-02-01...
19:00 - Available
19:15 - Available
19:30 - Available
20:00 - Not available
```

</details>

<details>
<summary>Testing</summary>

```bash
cd tests/
./test_commands.sh        # Integration tests
./test_edge_cases.sh      # Error handling tests
./test_skill_selection.sh # Trigger word tests
```

</details>

## How it works

Queries the same endpoints that power Ontopo's website.

## Limitations

- Does not place reservations - generates booking links for manual confirmation
- Availability data may be delayed or inaccurate
- Requires internet connection

## Legal

Independent open-source tool. Not affiliated with or endorsed by Ontopo. Availability data comes from the same APIs that power the website and may not reflect actual availability. This tool generates booking links - it does not place reservations. Provided "as is" without warranty of any kind.

## Author

[Alex Polonsky](https://alexpolonsky.com) - [GitHub](https://github.com/alexpolonsky) - [LinkedIn](https://www.linkedin.com/in/alexpolonsky/) - [Twitter/X](https://x.com/alexpo)

Part of [Agent Skills](https://github.com/alexpolonsky/agent-skills) - [Specification](https://agentskills.io/specification)
