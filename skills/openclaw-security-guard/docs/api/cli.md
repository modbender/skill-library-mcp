# 📋 CLI Reference

Complete reference for all CLI commands.

---

## Global Options

These options work with all commands:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--version` | `-V` | Show version number | - |
| `--config <path>` | `-c` | Path to config file | Auto-detect |
| `--lang <lang>` | `-l` | Language (en\|fr\|ar) | `en` |
| `--verbose` | `-v` | Verbose output | `false` |
| `--quiet` | `-q` | No banner | `false` |
| `--help` | `-h` | Show help | - |

---

## Commands

### `audit`

Run a complete security audit.

```bash
openclaw-guard audit [options]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--deep` | Deep scan (slower but thorough) | `false` |
| `--quick` | Quick scan (faster) | `false` |
| `-o, --output <path>` | Output file path | - |
| `-f, --format <format>` | Output format: text\|json\|html\|md | `text` |
| `--ci` | CI mode (exit 1 on critical) | `false` |

#### Examples

```bash
# Basic audit
openclaw-guard audit

# Deep audit
openclaw-guard audit --deep

# Quick audit
openclaw-guard audit --quick

# Save as HTML report
openclaw-guard audit -o report.html -f html

# Save as JSON
openclaw-guard audit -o audit.json -f json

# CI/CD mode
openclaw-guard audit --ci

# Verbose output
openclaw-guard audit -v

# French language
openclaw-guard audit -l fr
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Critical issues found (with `--ci`) |

---

### `dashboard`

Start the real-time security dashboard.

```bash
openclaw-guard dashboard [options]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-p, --port <port>` | Dashboard port | `18790` |
| `-g, --gateway <url>` | OpenClaw Gateway URL | `ws://127.0.0.1:18789` |
| `--no-browser` | Don't open browser | `false` |

#### Examples

```bash
# Start dashboard
openclaw-guard dashboard

# Custom port
openclaw-guard dashboard -p 3000

# Don't open browser
openclaw-guard dashboard --no-browser

# Custom gateway
openclaw-guard dashboard -g ws://192.168.1.100:18789
```

#### First Run

On first run, you'll be prompted to create a password.

---

### `fix`

Fix security issues automatically.

```bash
openclaw-guard fix [options]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--auto` | Auto-fix without prompts | `false` |
| `--interactive` | Interactive mode | `true` |
| `--backup` | Create backup before changes | `true` |
| `--dry-run` | Preview changes only | `false` |

#### Examples

```bash
# Interactive fix
openclaw-guard fix

# Automatic fix
openclaw-guard fix --auto

# Preview only (no changes)
openclaw-guard fix --dry-run

# No backup
openclaw-guard fix --auto --no-backup
```

---

### `scan`

Run individual scanners.

```bash
openclaw-guard scan <scanner> [options]
```

#### Scanners

| Scanner | Description |
|---------|-------------|
| `secrets` | Scan for exposed secrets |
| `config` | Audit OpenClaw configuration |
| `prompts` | Detect prompt injection patterns |

#### Options (secrets)

| Option | Description |
|--------|-------------|
| `--quick` | Quick scan mode |

#### Options (config)

| Option | Description |
|--------|-------------|
| `--strict` | Strict mode |

#### Options (prompts)

| Option | Description |
|--------|-------------|
| `-s, --sensitivity <level>` | low\|medium\|high |

#### Examples

```bash
# Scan for secrets
openclaw-guard scan secrets

# Quick secrets scan
openclaw-guard scan secrets --quick

# Audit config
openclaw-guard scan config

# Strict config audit
openclaw-guard scan config --strict

# Detect injections
openclaw-guard scan prompts

# High sensitivity
openclaw-guard scan prompts -s high
```

---

### `report`

Generate security reports.

```bash
openclaw-guard report [options]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-f, --format <format>` | html\|json\|md | `html` |
| `-o, --output <path>` | Output path | `./security-report` |

#### Examples

```bash
# HTML report
openclaw-guard report

# JSON report
openclaw-guard report -f json -o audit.json

# Markdown report
openclaw-guard report -f md -o SECURITY.md

# Custom path
openclaw-guard report -o /var/reports/security.html
```

---

### `hooks`

Manage git pre-commit hooks.

```bash
openclaw-guard hooks <action>
```

#### Actions

| Action | Description |
|--------|-------------|
| `install` | Install pre-commit hook |
| `uninstall` | Remove pre-commit hook |
| `status` | Check if hook is installed |

#### Examples

```bash
# Install hook
openclaw-guard hooks install

# Check status
openclaw-guard hooks status

# Remove hook
openclaw-guard hooks uninstall
```

---

### `about`

Show information about the tool.

```bash
openclaw-guard about
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENCLAW_HOME` | OpenClaw directory | `~/.openclaw` |
| `OPENCLAW_GUARD_CONFIG` | Config file path | Auto-detect |
| `NO_COLOR` | Disable colors | - |

---

## Configuration File

Create `.openclaw-guard.json` in project or home directory:

```json
{
  "scanners": {
    "secrets": { "enabled": true },
    "config": { "enabled": true, "strict": false },
    "prompts": { "enabled": true, "sensitivity": "medium" }
  },
  "dashboard": {
    "port": 18790
  }
}
```

---

<div align="center">

**[Back to Documentation](../en/README.md)**

</div>
