---
name: xmind-generator
description: Generate XMind mind map files (.xmind) from Markdown outlines or plain text descriptions. Use when a user asks to create a mind map, visualize a structure, or export to XMind format. Supports both Markdown outline syntax (# headings, - bullets, indentation) and free-form text descriptions. Output is saved as a .xmind file in the workspace directory, openable directly in XMind app.
runtime: node
---

# XMind Generator

Generate `.xmind` files from Markdown outlines or plain text using the XMind SDK.

## Script

`scripts/generate_xmind.js` — main generator. Requires Node.js and the `xmind` npm package.

## Installation

**Install dependencies before first use:**
```bash
cd <skill_dir>
npm install
```

## Usage

```bash
# From Markdown outline file
node scripts/generate_xmind.js --input outline.md --output /path/to/output.xmind

# From inline text (use \n for newlines)
node scripts/generate_xmind.js --text "# Root\n- Branch 1\n  - Leaf\n- Branch 2" --output output.xmind

# From stdin
echo "..." | node scripts/generate_xmind.js --output output.xmind
```

**Always run from the skill directory:**
```bash
cd <skill_dir>
```

**Default output location:** the OpenClaw workspace directory.

## Input Format

Both formats are supported:

**Markdown outline:**
```markdown
# Root Topic
- Main Branch 1
  - Sub topic 1
  - Sub topic 2
- Main Branch 2
  - Sub topic 3
    - Leaf node
```

**Plain text / free-form description:**
When user provides a description instead of an outline, first convert it to Markdown outline structure, then pass to the script.

## Workflow

1. If user provides a Markdown outline → pass directly to script via `--text` or `--input`
2. If user provides a plain text description → convert to Markdown outline first, then generate
3. Output file goes to workspace directory unless user specifies otherwise
4. Confirm the output path to the user after generation
