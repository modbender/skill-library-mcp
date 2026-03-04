# Skill: JSON Processor (jq)
# Description: The standard for surgical JSON reading and manipulation.
# Category: DevTools
# Keywords: [json, jq, optimization, token-saving, automation]

## 1. Installation
Ensure `jq` is available in your environment.

*   **macOS:** `brew install jq`
*   **Linux (Debian/Ubuntu):** `sudo apt-get install jq -y`
*   **Windows:** `winget install jqlang.jq` or `choco install jq`

## 2. When to Use
*   **Token Efficiency:** When you only need one field from a 500-line JSON file.
*   **Safety:** When editing config files (prevents syntax errors common with `sed`/`awk`).
*   **Formatting:** When you need to turn a minified JSON blob into a readable structure.
*   **Rule:** If a JSON file is > 50 lines, DO NOT `cat` it. Use `jq`.

## 3. RTFM (Read The Manual)
*   **Full Manual:** `man jq`
*   **Surgical Search:** `man jq | grep -C 5 "search_term"`
*   **Online:** https://jqlang.github.io/jq/manual/

## 4. Basic Syntax
*   **Identity (Pretty Print):** `jq . file.json`
*   **Select Key:** `jq '.key'`
*   **Select Array Index:** `jq '.[0]'`
*   **Pipe Keys:** `jq '.key | .subkey'`
*   **Multiple Keys:** `jq '{new_name: .old_key, id: .id}'`

## 5. Advanced: Token Cost Reduction
Agents must minimize output tokens. Never dump a massive JSON object just to check one value.

### A. Compact Output (`-c`)
Removes whitespace/newlines. Essential for piping to other tools or logging.
```bash
jq -c '.items[] | {id, status}' large_data.json
```

### B. In-Place Editing (Safe Pattern)
`jq` does not have an `-i` flag like `sed`. Use this pattern to safely update a file:
```bash
# Update a value
jq '.config.debug = true' config.json > config.tmp && mv config.tmp config.json
```

### C. Raw Output (`-r`)
Returns raw strings without quotes. Perfect for setting shell variables.
```bash
# Bad: "v1.0.0"
# Good: v1.0.0
VERSION=$(jq -r '.version' package.json)
```

### D. Selecting & Filtering
Don't read everything. Filter at the source.
```bash
# Only get successful events
jq '.events[] | select(.status == "success")' logs.json
```
