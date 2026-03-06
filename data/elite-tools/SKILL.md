---
name: elite-tools
description: Elite CLI tooling for efficient shell operations with optimized token usage. Use when executing shell commands, traversing directories, or manipulating files to minimize token consumption and prevent regex escaping errors. Covers fdfind, batcat, sd, sg/ast-grep, jc, gron, yq, difft, tealdeer, and html2text.
version: 0.0.1
---

# Elite CLI Tools

## PRIMARY DIRECTIVE

Prefer these modern CLI utilities over legacy POSIX tools (`find`, `cat`, `sed`, `grep`, `awk`, `diff`, `man`). They produce cleaner, more structured output and reduce token waste.

**Note on binary names:** On Debian/Ubuntu, some binaries are renamed to avoid conflicts: `fd` → `fdfind`, `bat` → `batcat`. On other distros they use their upstream names. Adapt accordingly.

## Quick Reference

| # | Tool | Replaces | Binary | Primary Use |
|---|------|----------|--------|-------------|
| 1 | fd | `find` | `fdfind` | Fast file discovery |
| 2 | bat | `cat`/`less` | `batcat` | File viewing with syntax highlighting |
| 3 | sd | `sed` | `sd` | Intuitive find & replace |
| 4 | ast-grep | `grep`/`rg` | `sg` | AST-based code search & rewrite |
| 5 | jc | `awk`/`cut` | `jc` | CLI output → JSON |
| 6 | gron | `jq` (exploration) | `gron` | JSON → greppable assignments |
| 7 | yq | `sed` on YAML | `yq` | YAML/JSON/XML/CSV processor |
| 8 | difftastic | `diff` | `difft` | Structural syntax-aware diffs |
| 9 | tealdeer | `man` | `tldr` | Concise command examples |
| 10 | html2text | raw HTML parsing | `html2text` | HTML → clean Markdown |

## Detailed Tool Guide

For full descriptions, rationale, and extended examples for each tool, read [references/tools-deep-dive.md](references/tools-deep-dive.md).
