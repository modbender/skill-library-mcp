# Table Image Generator 📋

[![Tests](https://github.com/Cluka-399/table-image/actions/workflows/test.yml/badge.svg)](https://github.com/Cluka-399/table-image/actions/workflows/test.yml)
[![Tests](https://img.shields.io/badge/tests-37_passed-brightgreen)](https://github.com/Cluka-399/table-image/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25_features-brightgreen)](https://github.com/Cluka-399/table-image/blob/main/scripts/table.test.mjs)
[![Node](https://img.shields.io/badge/node-18%20|%2020%20|%2022-blue)](https://github.com/Cluka-399/table-image/actions)
[![ClawHub](https://img.shields.io/badge/ClawHub-v1.3.0-orange)](https://clawhub.ai/skills/table-image-generator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Cluka-399/table-image/blob/main/LICENSE)

Generate clean PNG table images from JSON data. **Stop using ASCII tables** — they look broken on Discord, Telegram, WhatsApp, and every messaging platform. This renders pixel-perfect images instead.

## Features

- 🎨 **Color Emoji** — Full Twemoji rendering (✅🔥🏆 etc.)
- 🌙 **Dark Mode** — Discord-style dark theme
- 🔄 **RTL Support** — Auto-detects Hebrew/Arabic, reverses columns
- 📝 **Word Wrapping** — Long text wraps (max 3 lines, configurable)
- 📐 **Smart Column Widths** — Headers always visible, proportional distribution
- ⚡ **Fast** — Generates in <100ms, no Puppeteer needed
- 📁 **Shell-Safe Input** — `--data-file` avoids quoting issues

## Installation

```bash
cd scripts && npm install
```

## Usage

```bash
# Recommended: use --data-file to avoid shell quoting issues
cat > /tmp/data.json << 'EOF'
[{"Name":"Alice","Score":95},{"Name":"Bob","Score":87}]
EOF
node scripts/table.mjs --data-file /tmp/data.json --dark --output table.png

# Or pipe via stdin
echo '[{"Name":"Alice","Score":95}]' | node scripts/table.mjs --dark --output table.png

# Simple inline (works for basic data)
node scripts/table.mjs --data '[{"A":"1","B":"2"}]' --output table.png
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--data` | JSON array of row objects | required* |
| `--data-file` | Read JSON from file (shell-safe) | — |
| `--output` | Output file path | table.png |
| `--title` | Table title | none |
| `--dark` | Dark mode (Discord-style) | false |
| `--columns` | Column order/subset (comma-separated) | all |
| `--headers` | Custom header names (comma-separated) | column keys |
| `--max-width` | Maximum table width in pixels | 800 |
| `--font-size` | Font size in pixels | 14 |
| `--header-color` | Header background color | #e63946 |
| `--no-stripe` | Disable alternating row colors | striped |
| `--align` | Column alignments: l,r,c (comma-separated) | auto |
| `--compact` | Reduce padding | false |
| `--rtl` | Force RTL layout (auto-detected) | auto |
| `--no-wrap` | Disable word wrapping (truncate) | wraps |
| `--max-lines` | Max lines per cell when wrapping | 3 |

\* Provide data via `--data`, `--data-file`, or stdin.

## Examples

### Dark Mode + Emoji
```bash
node scripts/table.mjs \
  --data-file skills.json \
  --title "🏆 Agent Leaderboard" \
  --dark --output leaderboard.png
```

### Hebrew RTL (auto-detected)
```bash
node scripts/table.mjs \
  --data-file hebrew.json \
  --title "הצוות" \
  --dark --output team.png
```

## Testing

```bash
cd scripts && node table.test.mjs
```

37 tests covering: generation, dark/light mode, titles, compact, stdin, data-file, RTL, word wrapping, emoji, column alignment, error handling, and edge cases.

CI runs on Node 18, 20, and 22 via GitHub Actions.

## ClawHub

```bash
clawhub install table-image-generator
```

## License

MIT
