---
name: json-repair-kit
description: Repair malformed JSON files by normalizing them through Node.js evaluation. Use this to fix trailing commas, single quotes, unquoted keys, or other common syntax errors in JSON files (e.g. config files, manually edited data).
---

# JSON Repair Kit

A utility to repair broken or "loose" JSON files (like those with trailing commas, single quotes, or unquoted keys) by parsing them as JavaScript objects and re-serializing as valid JSON.

## Usage

```bash
# Repair a file in place (creates .bak backup)
node skills/json-repair-kit/index.js --file path/to/broken.json

# Repair and save to a new file
node skills/json-repair-kit/index.js --file broken.json --out fixed.json

# Scan directory and repair all .json files (recursive)
node skills/json-repair-kit/index.js --dir config/ --recursive
```

## Supported Repairs

- **Trailing Commas**: `{"a": 1,}` -> `{"a": 1}`
- **Single Quotes**: `{'a': 'b'}` -> `{"a": "b"}`
- **Unquoted Keys**: `{key: "value"}` -> `{"key": "value"}`
- **Comments**: Removes JS-style comments `//` (if parser supports it, standard Node `eval` may strip them if they are line comments outside of strings).
- **Hex/Octal Numbers**: `0xFF` -> `255`

## Safety

- **Backup**: Always creates a `.bak` file before overwriting (unless `--no-backup` is used, but default is safe).
- **Validation**: Verifies the repaired content is valid JSON before writing.
- **Eval Sandbox**: Uses `vm.runInNewContext` to parse, ensuring no access to global scope or process. It is safer than `eval()`.
