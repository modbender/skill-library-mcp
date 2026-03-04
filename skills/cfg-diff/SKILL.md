---
description: Compare configuration files, highlight differences, and suggest merge strategies for YAML, JSON, TOML, and INI formats.
---

# Config Diff

Compare and merge configuration files.

## Capabilities

- **Diff**: Side-by-side or unified diff of config files
- **Semantic Diff**: Understand structure (not just text) for YAML/JSON/TOML
- **Merge Suggestions**: Propose how to merge conflicting configs
- **Format Support**: YAML, JSON, TOML, INI, env files

## Usage

Ask the agent to:
- "Compare config.yml and config.production.yml"
- "What changed between these two JSON configs?"
- "Help me merge these two TOML files"
- "Show differences between .env.local and .env.production"

## How It Works

Uses `diff`, `jq`, `yq`, and text analysis:

```bash
diff --unified config-a.yml config-b.yml
jq -S . a.json > /tmp/a.json && jq -S . b.json > /tmp/b.json && diff /tmp/a.json /tmp/b.json
```

## Requirements

- `diff` (pre-installed)
- Optional: `jq` for JSON, `yq` for YAML
- No API keys needed
