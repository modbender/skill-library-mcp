# Config Schema Reference

Config file is loaded from (first found):
1. Path passed via `--config`
2. `~/.openclaw/outgoing-filter-config.yaml`
3. `~/.openclaw/outgoing-filter-config.yml`
4. `~/.openclaw/outgoing-filter-config.json`

If absent, built-in defaults apply (mode=mask, all built-in patterns enabled).

---

## Top-Level Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `mask\|block\|warn` | `mask` | Global default action when a pattern matches |
| `mask_char` | string | `*` | Character(s) used to replace masked content |
| `show_prefix` | int | `3` | Reveal first N chars of masked value (0 = hide all) |
| `show_suffix` | int | `0` | Reveal last N chars of masked value (0 = hide all) |
| `log_detections` | bool | `false` | Write detection events to `log_path` (JSONL) |
| `log_path` | string | `~/.openclaw/outgoing-filter.jsonl` | Where to write detection logs |
| `allow_channels` | list[string] | `[]` | Channel IDs exempt from all filtering |
| `allow_patterns` | list[string] | `[]` | Regex patterns; matching messages pass through unfiltered |
| `patterns` | list[PatternDef] | `[]` | User-defined patterns (merged with / override built-ins) |

---

## PatternDef Object

```yaml
patterns:
  - name: my_pattern          # Required. Unique name. Must match built-in name to override it.
    regex: "PATTERN_REGEX"    # Required. Python re-compatible regex string.
    action: mask              # Optional. mask | block | warn. Overrides global mode.
    capture_group: 1          # Optional. Only mask/redact this group (not full match).
    description: "..."        # Optional. Human-readable label shown in detections output.
    disabled: false           # Optional. Set true to disable a built-in by name.
```

### action values

- **`mask`** — Replace matched value (or capture group) with masked version. Message is still sent.
- **`block`** — Do NOT send the message. Exit code 1. Caller must handle the block.
- **`warn`** — Allow the message but include a warning in `result.warnings`. Useful for IP addresses or semi-sensitive data.

---

## Example Config

```yaml
# ~/.openclaw/outgoing-filter-config.yaml

mode: mask
mask_char: "▓"
show_prefix: 4
show_suffix: 0
log_detections: true
log_path: ~/.openclaw/filter-log.jsonl

allow_channels:
  - "C_PRIVATE_VAULT"

allow_patterns:
  - "(?i)^(test|mock|example)"   # Pass through obvious test messages

patterns:
  # Override a built-in to make private IPs block instead of warn
  - name: private_ip_range
    regex: '\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})\b'
    action: block
    description: "Private IP address (escalated to block)"

  # Disable a built-in entirely
  - name: env_file_line
    regex: "PLACEHOLDER"
    disabled: true

  # Add a custom pattern (internal project tokens)
  - name: acme_deploy_token
    regex: '\bACME-[A-Z0-9]{32}\b'
    action: block
    description: "ACME Corp deployment token"
```

---

## Output JSON

```json
{
  "blocked": false,
  "message": "Filtered text (or original if blocked)",
  "detections": [
    {
      "name": "generic_api_key",
      "action": "mask",
      "snippet": "sk-ant…",
      "description": "Generic API key / secret"
    }
  ],
  "warnings": ["⚠️  Sensitive pattern detected (private_ip_range): Private IP address (RFC1918)"]
}
```

**Exit codes:** `0` = OK/masked (send `result.message`), `1` = blocked (abort send), `2` = usage error.
