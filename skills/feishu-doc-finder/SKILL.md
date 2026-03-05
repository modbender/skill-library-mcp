---
name: feishu-file-finder
description: Find and download files from Feishu chat history by filename.
version: 1.0.0
---

# Feishu File Finder

A utility skill to search for a file in a Feishu chat (by filename) and download it.
Useful when OpenClaw's auto-download misses a file or for retrieving past files.

## Prerequisites

- `FEISHU_APP_ID` and `FEISHU_APP_SECRET` must be set in environment.

## Usage

```bash
cd skills/feishu-file-finder
npm install

# Basic usage
node index.js --chat <chat_id> --file <filename>

# Options
# -o, --output <dir>   Save path (default: current dir)
# -h, --hours <num>    Search history lookback (default: 24h)
```

## Example

```bash
export FEISHU_APP_ID=...
export FEISHU_APP_SECRET=...

node index.js --chat oc_87435... --file travel-planner.zip
```
