---
name: exo-installer Skill
description: Install, update, and monitor all E.x.O. tools with a single command.
---

# exo-installer Skill

**E.x.O. Ecosystem Manager**

Install, update, and monitor all E.x.O. tools with a single command.

## When to Use

- User wants to install E.x.O. tools (jasper-recall, hopeIDS, context-compactor)
- User asks about the E.x.O. ecosystem
- User needs to set up OpenClaw plugins
- User wants to check health of installed tools

## Quick Start

```bash
# Install all public E.x.O. packages
npx exo-installer install --all

# Or install specific tools
exo install jasper-recall
exo install hopeIDS
exo install jasper-context-compactor

# Health check
exo doctor
exo doctor --json  # For automation
```

## Commands

| Command | Description |
|---------|-------------|
| `exo install --all` | Install all public packages |
| `exo install <pkg>` | Install specific package |
| `exo update` | Update all installed packages |
| `exo doctor` | Health check all components |
| `exo doctor --json` | Health check with JSON output |
| `exo list` | List available packages |
| `exo internal clone` | Clone private repos (needs GitHub access) |

## Available Packages

### Public (npm)

| Package | Description |
|---------|-------------|
| `jasper-recall` | Local RAG system for agent memory |
| `hopeIDS` | Behavioral anomaly detection |
| `jasper-context-compactor` | Token management for local models |
| `jasper-configguard` | Safe config changes with rollback |

### Internal (GitHub)

| Repo | Description |
|------|-------------|
| `hopeClaw` | Meta-cognitive inference engine |
| `moraClaw` | Temporal orchestration agent |
| `task-dashboard` | Project management system |
| `exo-distiller` | Agent distillation pipeline |

Internal packages require GitHub org access:
```bash
exo internal clone
```

## Health Check

```bash
$ exo doctor
🔍 E.x.O. Health Check

jasper-recall ................. ✅ v0.4.2
  ChromaDB: ✅ connected
  Embeddings: ✅ loaded
  Documents: 847

hopeIDS ...................... ✅ v1.3.3
  Analyzer: ✅ ready
  Models: 3 loaded

jasper-context-compactor ...... ✅ v0.2.2

Overall: 3/3 healthy
```

## Integration

After installing, tools auto-register with OpenClaw:

```json
{
  "extensions": {
    "jasper-recall": { "enabled": true },
    "hopeIDS": { "enabled": true },
    "jasper-context-compactor": { "enabled": true }
  }
}
```

## Links

- GitHub: https://github.com/E-x-O-Entertainment-Studios-Inc/exo-installer
- Docs: https://exohaven.com/products
- Discord: https://discord.com/invite/clawd
