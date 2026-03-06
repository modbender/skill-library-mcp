# Contributing to self-evolving-agent

Thanks for your interest! This skill runs on personal OpenClaw instances and the more people improve it, the better it gets for everyone.

---

## First-Time Contributors

Welcome! Here's the fastest path to your first contribution:

1. Read this file (you're doing it ✅)
2. Check [`docs/good-first-issues.md`](docs/good-first-issues.md) for curated starter tasks
3. Look for issues labeled [`good first issue`](https://github.com/ramsbaby/self-evolving-agent/labels/good%20first%20issue) on GitHub
4. Open an issue to claim a task before you start (avoids duplicate work)
5. Fork, branch, code, PR

Not sure where to start? Open a [Discussion](https://github.com/ramsbaby/self-evolving-agent/discussions) and ask.

---

## What's Worth Contributing

### 🟢 Easy (Good First Issues)

- Add complaint pattern keywords for languages other than Korean/English
- Improve error messages in scripts
- Fix typos in documentation
- Add examples to `docs/`
- Add a new language to `config.yaml`'s `complaint_patterns`

### 🟡 Medium

- New analysis signal types (e.g., detecting session compaction patterns)
- Support for additional OpenClaw session log formats
- `config.yaml` validation script
- Windows/WSL compatibility fixes
- New delivery platform integration in `deliver.sh`

### 🔴 Hard

- Alternative output targets beyond AGENTS.md (SOUL.md, TOOLS.md)
- Multi-workspace support (analyze across multiple OpenClaw instances)
- Integration with other skill ecosystems (Claude Code, Codex)
- New analysis stage added to the orchestrator pipeline

---

## Development Setup

### Prerequisites

- **bash** 3.2+ (macOS default; bash 4+ on Linux/WSL)
- **python3** 3.8+ (for inline Python in scripts)
- **shellcheck** for linting

```bash
# macOS
brew install shellcheck

# Ubuntu / WSL
sudo apt-get install shellcheck

# Check version
shellcheck --version   # should be 0.8+
```

### Clone and Install

```bash
git clone https://github.com/ramsbaby/self-evolving-agent
cd self-evolving-agent

# Symlink into your OpenClaw skills directory (for live testing)
ln -s "$(pwd)" ~/openclaw/skills/self-evolving-agent

# Or copy directly
cp -r . ~/openclaw/skills/self-evolving-agent
```

### Configure for Local Development

```bash
# Copy and edit the config
cp config.yaml config.yaml.local   # optional — keep local overrides out of git

# Minimum required for dry-run testing:
# analysis.days: 3
# cron.discord_channel: "your-channel-id"
```

---

## Running Tests

```bash
# Lint all shell scripts
make test

# Or run shellcheck directly
shellcheck scripts/*.sh scripts/lib/*.sh scripts/v4/*.sh

# Dry-run the full v4 pipeline (no LLM calls, fast)
DRY_RUN=true VERBOSE=true \
  bash scripts/v4/orchestrator.sh

# Dry-run a single stage
DRY_RUN=true VERBOSE=true \
  bash scripts/v4/collect-logs.sh /tmp/sea-v4/logs.json

# Validate JSON output
cat /tmp/sea-v4/analysis.json | python3 -m json.tool

# Test config loading
bash -c 'source scripts/lib/config-loader.sh && sea_load_config && echo "days=$SEA_DAYS"'
```

> **Edge case tests** you should check manually before a PR:
> - `ANALYSIS_DAYS=1 DRY_RUN=true bash scripts/v4/orchestrator.sh` (single day)
> - Run with an empty agents dir: `AGENTS_DIR=/tmp/empty_test DRY_RUN=true bash scripts/v4/orchestrator.sh`
> - Verify the proposal JSON is valid: `python3 -m json.tool < /tmp/sea-v4/effects.json`

---

## Code Style Guide

This project uses bash as its primary language. All scripts must follow these conventions:

### The Non-Negotiables

```bash
#!/usr/bin/env bash
set -euo pipefail   # Every script starts with this (except register-cron.sh — see below)
```

> **Exception:** `register-cron.sh` explicitly omits `set -euo pipefail` because it runs in cron contexts where error exposure to Discord must be prevented.

### Variable Quoting

Always quote variable expansions. No exceptions.

```bash
# ❌ Wrong
echo $VAR
cat $FILE

# ✅ Correct
echo "$VAR"
cat "$FILE"
```

### File Existence Checks

Check before reading:

```bash
# ❌ Wrong
content=$(cat "$file")

# ✅ Correct
if [[ -f "$file" ]]; then
  content=$(cat "$file")
fi
```

### No Hardcoded Paths

Use config variables or derive from `SCRIPT_DIR`:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
```

### Error Propagation vs Suppression

The orchestrator wraps stage calls in `|| true` to prevent cascade failures. Inside stages, use `set -euo pipefail` normally but wrap external calls defensively:

```bash
# External tools that might not be installed
jq_result=$(echo "$json" | jq -r '.key' 2>/dev/null) || jq_result="fallback"

# Optional operations that should not block progress
find "$dir" -name "*.json" -mtime +30 -delete 2>/dev/null || true
```

### Security Manifest (Required for all scripts)

Every script that reads/writes files or calls APIs must have a security manifest comment at the top:

```bash
# SECURITY MANIFEST:
# Environment variables accessed: VAR1, VAR2
# External endpoints called: none
# Local files read: ~/.openclaw/sessions/* (read-only)
# Local files written: ~/openclaw/skills/self-evolving-agent/data/
# Network: None
```

### Inline Python

When bash can't easily do something (JSON, date math, regex), use a Python heredoc:

```bash
python3 - > "$OUTPUT_FILE" 2>/dev/null <<'PYEOF' || true
import json
# ... your python
PYEOF
```

Rules for inline Python:
- Use `PYEOF` (or similar unique delimiter) — never `EOF` to avoid collisions
- Always redirect to a temp file then move atomically: `> "$file.tmp" && mv "$file.tmp" "$file"`
- Wrap in `|| true` at the call site

### Bash 3.2 Compatibility

The project must work on macOS's default bash (3.2). This means:

```bash
# ❌ bash 4+ only
declare -A my_map
my_map[key]="value"

# ✅ bash 3.2 compatible
MY_MAP_KEY="value"          # individual variables
eval "_var_${key}='${val}'" # dynamic variable naming
```

### Conventional Commits

```
feat: add French complaint pattern keywords
fix: handle missing .learnings/ directory gracefully
docs: add WSL setup guide
chore: update shellcheck CI to v0.10
refactor: extract stage log parsing into lib function
test: add edge case for empty sessions directory
```

---

## How to Add a New Analysis Pattern

Analysis patterns live in `config.yaml` under `analysis.complaint_patterns.ko` and `analysis.complaint_patterns.en`.

### Adding a Keyword Pattern

1. Edit `config.yaml`:
   ```yaml
   complaint_patterns:
     ko:
       - "새로 추가한 패턴"   # Add here
     en:
       - "new pattern here"  # Add here
   ```

2. Add a comment if the pattern is non-obvious or has a false-positive risk:
   ```yaml
     ko:
       - "새로 추가한 패턴"  # 구체적 불만 표현, "다시 해줘" 같은 일반 요청과 구별됨
   ```

3. Test: run a dry analysis and check complaint counts make sense.

### Adding a Structural Violation Pattern

For patterns that detect AGENTS.md rule violations, add to `analysis.violation_patterns`:

```yaml
violation_patterns:
  - pattern: "your regex here"
    rule: "Human-readable rule description"
    severity: "high"   # high | medium | low
    min_hits: 3        # Only flag if seen ≥ N times
```

### Adding a New Signal Type

To add a brand-new type of signal (e.g., detecting session compaction):

1. Add the detection logic to `scripts/v4/semantic-analyze.sh` as a new Python section
2. Add the new field to the `analysis.json` output schema (document in `docs/v4-architecture.md`)
3. Reference the new field in `scripts/v4/synthesize-proposal.sh` to include it in proposals
4. Update `docs/architecture.md` with the new signal type
5. Add a test: verify the JSON field appears in output

---

## How to Add a New Delivery Platform

Delivery platforms are handled by `scripts/v4/deliver.sh`. Discord uses OpenClaw's native cron delivery and bypasses `deliver.sh` entirely.

### Steps

1. **Add config keys to `config.yaml`:**
   ```yaml
   delivery:
     myplatform:
       api_key: ""
       endpoint: ""
   ```

2. **Add environment variable mappings in `scripts/lib/config-loader.sh`:**
   ```bash
   SEA_MYPLATFORM_API_KEY="${config_delivery_myplatform_api_key:-}"
   SEA_MYPLATFORM_ENDPOINT="${config_delivery_myplatform_endpoint:-}"
   ```

3. **Add the delivery case in `scripts/v4/deliver.sh`:**
   ```bash
   "myplatform")
     # SECURITY MANIFEST: External endpoints called: $SEA_MYPLATFORM_ENDPOINT
     curl -sf -X POST "$SEA_MYPLATFORM_ENDPOINT" \
       -H "Authorization: Bearer $SEA_MYPLATFORM_API_KEY" \
       -d "{\"text\": $(jq -Rs . < "$1")}" \
       || log_err "myplatform delivery failed"
     ;;
   ```

4. **Add the platform to `feature_request.yml`'s dropdown** in `.github/ISSUE_TEMPLATE/`

5. **Update `SKILL.md`** under the Delivery section

6. **Update the security manifest** at the top of `deliver.sh`

---

## Issue Labels Explained

| Label | Meaning |
|---|---|
| `bug` | Something isn't working as expected |
| `enhancement` | New feature or improvement |
| `good first issue` | Suitable for first-time contributors — well-scoped, mentor available |
| `help wanted` | Maintainer wants external contribution on this |
| `question` | Needs clarification or is a discussion starter |
| `documentation` | Docs-only change |
| `breaking change` | Requires migration steps |
| `security` | Security-sensitive change — please follow SECURITY.md |
| `wontfix` | Out of scope or intentionally not addressed |
| `platform: windows` | Windows/WSL-specific issue |
| `platform: linux` | Linux-specific issue |

---

## Pull Request Checklist

Before opening a PR:

- [ ] `make test` passes (shellcheck clean on all `.sh` files)
- [ ] Manually ran the pipeline with `DRY_RUN=true` and verified output
- [ ] Security manifests updated for any script that gained new file reads/writes/network calls
- [ ] `SKILL.md` updated if adding/changing user-facing config options or behaviors
- [ ] `README.md` updated if the feature affects the "Quick Start" or examples
- [ ] `CHANGELOG.md` updated with the change under `[Unreleased]`
- [ ] One PR = one concern (split unrelated changes into separate PRs)
- [ ] Issue opened first for non-trivial changes

---

## Project Structure

```
self-evolving-agent/
├── SKILL.md                # OpenClaw skill definition (frontmatter + docs)
├── README.md               # GitHub + ClawHub landing page
├── config.yaml             # User-editable configuration
├── CONTRIBUTING.md         # This file
├── CHANGELOG.md            # Version history
├── LICENSE                 # MIT
│
├── scripts/
│   ├── analyze-behavior.sh     # Legacy v3 analysis engine (kept for compatibility)
│   ├── generate-proposal.sh    # Legacy v3 proposal formatter (kept for compatibility)
│   ├── register-cron.sh        # Cron job management (reads config.yaml, calls orchestrator.sh)
│   └── lib/
│       └── config-loader.sh    # YAML config parser → bash env vars
│
├── scripts/v4/             # v4 multi-stage pipeline
│   ├── orchestrator.sh         # Main entry point (called by cron)
│   ├── collect-logs.sh         # Stage 1: Gather session + cron logs
│   ├── semantic-analyze.sh     # Stage 2: Pattern detection, signal extraction
│   ├── benchmark.sh            # Stage 3: GitHub star count, ClawHub metrics
│   ├── measure-effects.sh      # Stage 4: Past proposal effectiveness
│   ├── synthesize-proposal.sh  # Stage 5: Generate final proposal markdown
│   └── deliver.sh              # Optional: Slack/Telegram/webhook delivery
│
├── templates/
│   └── proposal-template.md    # Output format for proposals
│
├── docs/
│   ├── architecture.md         # System overview
│   ├── v4-architecture.md      # v4 stage specifications
│   ├── migration-v3-to-v4.md   # Upgrade guide for v3 users
│   ├── good-first-issues.md    # Curated starter tasks
│   └── ...
│
├── data/                   # Runtime data (gitignored)
│   ├── proposals/
│   └── rejected-proposals.json
│
└── .github/
    ├── workflows/
    │   └── ci.yml              # shellcheck CI on every PR
    ├── PULL_REQUEST_TEMPLATE.md
    └── ISSUE_TEMPLATE/
        ├── bug_report.yml
        ├── feature_request.yml
        └── good_first_issue.yml
```

---

## Ground Rules

### Code of Conduct

- Be kind. Everyone is learning.
- Critique code, not people.
- If something is broken, open an issue before assuming malice.
- Respect that this is a personal productivity tool — changes that work for you might break others' setups.

### When in Doubt

Open a [GitHub Discussion](https://github.com/ramsbaby/self-evolving-agent/discussions) or file an issue with the `question` label.
