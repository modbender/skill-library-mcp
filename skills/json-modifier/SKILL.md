---
name: json-modifier
description: Safely apply structured JSON patches (RFC 6902) to files. Use this skill when you need to update configuration files, package.json, or memory JSONs without rewriting the whole file or using brittle regex.
---

# JSON Modifier

A utility for modifying JSON files using [RFC 6902 JSON Patch](https://jsonpatch.com/) format.
Supports precise additions, removals, replacements, moves, copies, and tests.

## Usage

```bash
# Modify a file in place
node skills/json-modifier/index.js --file path/to/config.json --patch '[{"op": "replace", "path": "/key", "value": "new_value"}]'

# Modify and save to a new file
node skills/json-modifier/index.js --file input.json --patch '[...]' --out output.json

# Use a patch file
node skills/json-modifier/index.js --file input.json --patch-file patches/update.json
```

## Patch Format (RFC 6902)

The patch must be a JSON array of operation objects.

### Examples

**Replace a value:**
```json
[
  { "op": "replace", "path": "/version", "value": "2.0.0" }
]
```

**Add a new key:**
```json
[
  { "op": "add", "path": "/features/new_feature", "value": true }
]
```

**Remove a key:**
```json
[
  { "op": "remove", "path": "/deprecated_key" }
]
```

**Append to an array:**
```json
[
  { "op": "add", "path": "/list/-", "value": "item" }
]
```

## Safety

- Validates patch against document before applying.
- Atomic write (writes to temporary file, then renames).
- Preserves indentation (default: 2 spaces).
