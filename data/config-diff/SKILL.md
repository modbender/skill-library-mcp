---
name: config-diff
description: Compare config files semantically, highlight differences, and
  suggest merge strategies.
---


# Config Diff

Semantically compare and merge configuration files (YAML, JSON, TOML, INI, .env).

## Instructions

1. **Detect format** from file extension or content
2. **Semantic diff** — parse structure, don't just compare text:
   ```bash
   # JSON: normalize and diff
   jq -S . a.json > /tmp/a.json && jq -S . b.json > /tmp/b.json
   diff --unified /tmp/a.json /tmp/b.json

   # YAML: convert to sorted JSON first
   yq -o=json -S '.' a.yml | diff - <(yq -o=json -S '.' b.yml)

   # .env files
   diff <(sort a.env) <(sort b.env)
   ```
3. **Classify changes**:
   - 🟢 **Added**: New keys in target
   - 🔴 **Removed**: Keys missing from target
   - 🟡 **Changed**: Same key, different value
   - ⚪ **Unchanged**: Same key and value
4. **Report format**:
   ```
   📋 Config Diff: config.yml vs config.prod.yml
   | Key Path | Source | Target | Change |
   |----------|--------|--------|--------|
   | db.host  | localhost | db.prod.internal | 🟡 Changed |
   | db.pool  | —      | 20     | 🟢 Added |
   | debug    | true   | —      | 🔴 Removed |
   ```
5. **Merge suggestions**: For conflicts, recommend which value to keep based on environment context

## Security

- Flag sensitive values (passwords, tokens, keys) — never display in full; mask as `****`
- Warn if secrets differ between environments (may indicate misconfiguration)

## Edge Cases

- **Comments**: Text diff preserves comments; semantic diff ignores them — note this
- **Key ordering**: Semantic diff ignores order; flag if order matters (INI sections)
- **Nested objects**: Flatten key paths with dot notation for clear reporting

## Requirements

- `diff` (pre-installed)
- Optional: `jq` (JSON), `yq` (YAML)
- No API keys needed
