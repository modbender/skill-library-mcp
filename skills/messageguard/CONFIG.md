# CONFIGURATION.md

This document explains the configuration options available for the Outgoing Message Filter Skill.

---

## Overview
Configuration files are loaded from the following (first match):
1. Explicit `--config` argument during invocation.
2. Default file paths:
   - `~/.openclaw/outgoing-filter-config.yaml`
   - `~/.openclaw/outgoing-filter-config.json`

If none is found, built-in defaults are applied.

---

### Global Settings

| Field         | Type              | Default                          | Description                     |
|---------------|-------------------|----------------------------------|---------------------------------|
| `mode`        | `mask|block|warn` | `mask`                          | Default action for detections.  |
| `mask_char`   | string            | `*`                              | Character used for masking.     |
| `log_detections` | bool           | `false`                         | Log detection events if true.   |
| `log_path`    | string            | `~/.openclaw/filter-log.jsonl`   | Path to detection log file.     |

### Pattern Configuration

Each pattern can override the global settings with a `PatternDef` object:

```yaml
patterns:
  - name: my_custom_pattern
    regex: "CUSTOM_REGEX"
    action: block  # Override global mode: mask, block, warn
    description: "Human-readable purpose"
    capture_group: 1  # Nth regex group.
```

---

### Example Configurations

#### Minimal Setup
```yaml
mode: warn
patterns:
  - name: jwt_tokens
    regex: "eyJ[^"]*"
```

#### Full Sample
```yaml
mode: mask
mask_char: ""+
log_detections: true
log_path: "~/.openclaw/custom-log.jsonl"
patterns:
  - name: private_key_block
    action: block
  - name: custom_regex_example
    regex: "Test-Pattern"
```
