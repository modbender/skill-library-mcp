# openclaw-crm

[![Tests](https://img.shields.io/badge/tests-10%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> Local-first CRM for tracking leads, deals, and follow-ups.

A lightweight, SQLite-powered CRM built for agents and humans alike. Manage contacts, track deals through pipeline stages, log activities, schedule follow-ups, tag everything, and generate pipeline reports — all from the command line.

## Features

- **Contact management** — add, edit, list, and search contacts with company/email/phone
- **Deal pipeline** — track deals through customizable stages with values
- **Activities & notes** — log calls, emails, meetings, and notes against deals
- **Follow-ups** — schedule and track due follow-ups with overdue detection
- **Tagging** — tag deals for flexible categorization and filtering
- **Full-text search** — search across contacts and deals
- **Pipeline reports** — summary of deals by stage with total values
- **Interchange output** — publish CRM state as `.md` files
- **Backup & restore** — full database backup and recovery

## Quick Start

```bash
cd skills/crm
npm install

# Add a contact and create a deal
node src/cli.js lead add "Jane Smith" -c "Acme Corp" -e jane@acme.com
node src/cli.js deal add "Acme Enterprise License" -c <contact-id> -v 50000 --stage proposal

# Schedule a follow-up
node src/cli.js followup add <deal-id> -d 2026-03-01 -n "Send revised proposal"

# Check what's due
node src/cli.js followup due --days 7

# Pipeline overview
node src/cli.js report pipeline
```

## CLI Reference

### Contacts

```bash
crm lead add <name> [-c company] [-e email] [-p phone] [-n notes]
crm lead list [-s search-query]
crm lead edit <id> [-c company] [-e email] [-p phone] [-n notes]
```

### Deals

```bash
crm deal add <title> [-c contact-id] [-v value] [-s source] [--stage stage]
crm deal list [--stage stage] [--tag tag]
crm deal stage <id> <new-stage>
crm deal note <id> <content> [-t type]
crm deal tag <id> <tag-name>
```

### Follow-ups

```bash
crm followup add <deal-id> -d <YYYY-MM-DD> [-n note]
crm followup due [--days <n>]
crm followup complete <id>
```

### Reports & Search

```bash
crm report pipeline          # Pipeline summary by stage
crm search <query>           # Search contacts and deals
```

### Utilities

```bash
crm refresh                  # Regenerate interchange .md files
crm backup [-o path]
crm restore <backup-file>
```

## Architecture

SQLite database (`data/crm.db`) with tables for contacts, deals, activities, follow-ups, and tags. Deal stages flow through a customizable pipeline (e.g., `prospect → qualified → proposal → negotiation → closed-won`). All queries are local — no external services required.

## .md Interchange

Running `crm refresh` generates `.md` files summarizing pipeline state, due follow-ups, and contact information. Other agents can read these files via `@openclaw/interchange` to stay informed about deal status without direct DB access.

## Testing

```bash
npm test
```

10 tests covering contact CRUD, deal lifecycle, follow-up scheduling, tagging, search, and pipeline reports.

## Part of the OpenClaw Ecosystem

CRM publishes deal and pipeline data via `@openclaw/interchange`. The `monitoring` skill can track CRM task outcomes, and `orchestration` can queue follow-up actions based on pipeline changes.

## License

MIT
