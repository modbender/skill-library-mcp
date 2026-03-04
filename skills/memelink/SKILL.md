---
name: memelink
description: >
  Generate memes, image macros, and meme URLs from the terminal using the
  Memegen.link API. Use when creating memes, picking meme templates, generating
  funny images, or building meme URLs from text. Supports auto-generate,
  template-based, and custom background modes.
argument-hint: "[text or template]"
license: MIT
homepage: https://github.com/dedene/memelink-cli
metadata:
  author: dedene
  version: "1.1.0"
  openclaw:
    primaryEnv: MEMEGEN_API_KEY
    requires:
      bins:
        - memelink
    install:
      - kind: brew
        tap: dedene/tap
        formula: memelink
        bins: [memelink]
      - kind: go
        package: github.com/dedene/memelink-cli/cmd/memelink
        bins: [memelink]
---

# memelink CLI

Generate memes from the terminal. Wraps the Memegen.link API.

## Quick Start

```bash
# Auto-generate — API picks the best template
memelink "when the code finally compiles"

# Template-based — specify template ID + text lines
memelink drake "tabs" "spaces"

# Custom background
memelink custom --background https://example.com/bg.jpg "top" "bottom"

# Copy to clipboard and open in browser
memelink drake "before memelink" "after memelink" -c -o

# JSON output for scripting
memelink --json "deploy on friday"
```

## Commands

- `memelink "text"` -- auto-select template, generate meme (default command)
- `memelink <template> "top" "bottom"` -- generate from specific template
- `memelink custom --background <url> "text"` -- custom background image
- `memelink templates` -- list templates; interactive fuzzy picker in TTY (alias: ls)
- `memelink templates <id>` -- show template detail
- `memelink templates --filter <query>` -- filter templates
- `memelink fonts` -- list available fonts
- `memelink config path|list|get|set|unset` -- manage config
- `memelink version` -- print version info

Command aliases: `generate` → `gen`, `g`; `templates` → `ls`

## Generate Flags

- `--format png|jpg|gif|webp` / `-f` -- output format
- `--font <name>` -- font name
- `--layout default|top` -- text layout
- `--width N` / `--height N` -- image dimensions
- `--style <style>` -- template style (repeatable)
- `--text-color <hex>` -- text color per line (repeatable)
- `--background <url>` -- custom background (with 'custom' template)
- `--center x,y` / `--scale N` -- overlay position and scale
- `--safe` -- filter NSFW content
- `--copy` / `-c` -- copy URL to clipboard
- `--open` / `-o` -- open in browser
- `--output <path>` / `-O` -- download image
- `--preview` / `--no-preview` -- inline terminal preview

## Configuration

Config file: `~/.config/memelink/config.json`

```bash
memelink config set default_format png
memelink config get default_format
memelink config list
```

Keys: default_format, default_font, default_layout, safe, auto_copy, auto_open, preview, cache_ttl

## Environment

- `MEMEGEN_API_KEY` -- optional API key for higher rate limits

## Global Flags

- `--json` -- JSON output (pipe-friendly)
- `--no-input` -- disable interactive prompts
- `--verbose` -- debug logging
- `--color auto|always|never` -- color output


## Installation

```bash
brew install dedene/tap/memelink-cli
```
