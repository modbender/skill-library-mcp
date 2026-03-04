---
name: firm-i18n-audit-pack
version: 1.0.0
description: >
  Internationalization audit pack.
  Locale file scanning and missing translation key detection. 1 i18n tool.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - i18n
  - localization
  - audit
  - translations
  - locale
---

# firm-i18n-audit-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Scans locale files to detect missing translation keys, inconsistent key structures
across languages, and untranslated strings. Supports JSON and YAML locale formats.

## Tools (1)

| Tool | Description |
|------|-------------|
| `openclaw_i18n_audit` | Locale file scanning + missing key detection |

## Usage

```yaml
skills:
  - firm-i18n-audit-pack

# Audit translations:
openclaw_i18n_audit config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
