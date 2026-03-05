# OpenClaw Doctor Pro - CLI Tools

Professional-grade diagnostic and management tools for OpenClaw AI Gateway.

## Scripts Overview

### 1. error-fixer.py (163 lines)
Error diagnosis and auto-fix CLI for OpenClaw.

**Usage:**
```bash
# Analyze log file
./error-fixer.py --input /path/to/openclaw.log

# Direct error code lookup
./error-fixer.py --error NOT_LINKED

# Read from stdin
tail -100 openclaw.log | ./error-fixer.py

# Auto-fix safe errors
./error-fixer.py --input openclaw.log --auto-fix

# Dry-run mode
./error-fixer.py --input openclaw.log --auto-fix --dry-run

# List errors by category
./error-fixer.py --category network

# JSON output
./error-fixer.py --error HTTP_500 --json
```

**Features:**
- Multi-layer error matching (exact code, regex, semantic)
- Auto-fix execution for safe recipes
- Rich panel output with severity badges
- Category filtering
- JSON output mode

---

### 2. skill-recommender.py (150 lines)
Smart ClawHub skill recommendations.

**Usage:**
```bash
# Auto-detect from config
./skill-recommender.py --auto-detect

# Filter by channel
./skill-recommender.py --channel whatsapp

# Search by use case
./skill-recommender.py --use-case calendar

# Combined search
./skill-recommender.py --channel telegram --use-case image

# Check for updates
./skill-recommender.py --check-updates

# Limit results
./skill-recommender.py --channel discord --top 5

# JSON output
./skill-recommender.py --auto-detect --json
```

**Features:**
- Channel-skill affinity scoring
- Use case keyword matching
- Verification and popularity scoring
- Update checker for installed skills
- Cache freshness indicators

---

### 3. self-updater.py (140 lines)
Self-update checker and executor.

**Usage:**
```bash
# Check status (default)
./self-updater.py

# Check with explicit flag
./self-updater.py --check

# Update everything
./self-updater.py --update

# Update docs only
./self-updater.py --update --docs-only

# Update skill cache only
./self-updater.py --update --skills-only

# JSON output
./self-updater.py --check --json
```

**Features:**
- OpenClaw version checking (npm)
- ClawHub CLI availability check
- Documentation reachability test
- Skill cache refresh
- Error pattern updates from docs

---

### 4. enhanced-doctor.py (182 lines)
Extended diagnostics CLI for OpenClaw.

**Usage:**
```bash
# Basic diagnostics
./enhanced-doctor.py

# Deep diagnostics with log analysis
./enhanced-doctor.py --deep

# JSON output
./enhanced-doctor.py --json

# Generate markdown report
./enhanced-doctor.py --report

# Combined
./enhanced-doctor.py --deep --json
```

**Checks:**
- System requirements (Node.js, pnpm, openclaw, git, docker)
- Network connectivity (Anthropic, OpenAI APIs)
- Gateway status (port 18789)
- Configuration validation
- Channel credentials
- Disk space (~/.openclaw)
- Recent errors (deep mode)

---

### 5. setup-wizard.py (176 lines)
Interactive onboarding wizard.

**Usage:**
```bash
# Interactive mode
./setup-wizard.py

# Check prerequisites only
./setup-wizard.py --check-only

# Non-interactive with pre-selection
./setup-wizard.py --non-interactive --provider anthropic --channel telegram --channel discord

# Pre-select provider
./setup-wizard.py --provider openai

# Pre-select channels
./setup-wizard.py --channel whatsapp --channel slack
```

**Features:**
- Prerequisite checking
- Automatic component installation
- Interactive channel selection
- AI provider configuration
- Config generation with backup
- Integration with openclaw doctor

**Supported Channels:**
whatsapp, telegram, discord, slack, signal, imessage, teams, matrix, google-chat, zalo, bluebubbles

**Supported Providers:**
anthropic, openai, gemini

---

## Library Modules

All scripts use shared modules from `scripts/lib/`:

- `clawhub_client.py` - ClawHub CLI wrapper with caching
- `config_analyzer.py` - Configuration validation
- `doc_fetcher.py` - Documentation fetcher
- `error_database.py` - Error pattern matching engine
- `error_parser.py` - Log and error text parser
- `fix_engine.py` - Auto-fix execution engine
- `recommendation_engine.py` - Skill recommendation system
- `setup_helpers.py` - Setup wizard helpers
- `system_checks.py` - System and environment checks
- `utils.py` - Shared utilities

---

## Installation

All scripts are executable and use the project's Python interpreter:

```bash
chmod +x scripts/*.py
```

---

## Requirements

- Python 3.10+
- Rich library (for CLI output)
- Click library (for CLI parsing)

Install dependencies:
```bash
pip install rich click
```

---

## File Organization

```
scripts/
├── error-fixer.py           # Error diagnosis & auto-fix
├── skill-recommender.py     # ClawHub skill recommendations
├── self-updater.py          # Self-update management
├── enhanced-doctor.py       # Extended diagnostics
├── setup-wizard.py          # Interactive setup
└── lib/
    ├── __init__.py
    ├── clawhub_client.py    # ClawHub API client
    ├── config_analyzer.py   # Config validation
    ├── doc_fetcher.py       # Docs fetcher
    ├── error_database.py    # Error patterns
    ├── error_parser.py      # Log parser
    ├── fix_engine.py        # Auto-fix engine
    ├── recommendation_engine.py
    ├── setup_helpers.py     # Setup utilities
    ├── system_checks.py     # System checks
    └── utils.py             # Shared utilities
```

---

## Data Files

Required data files in `data/`:

- `error-patterns.json` - Error code definitions
- `fix-recipes.json` - Auto-fix recipes
- `clawhub-cache.json` - Skill cache (auto-generated)

---

## Notes

- All scripts follow YAGNI, KISS, DRY principles
- Each script is under 200 lines
- Kebab-case filenames with descriptive names
- Proper error handling and user feedback
- Rich output for better UX
- JSON output mode for automation
