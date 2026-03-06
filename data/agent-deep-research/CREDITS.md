# Credits

## Original Project

This project was forked from [allenhutchison/gemini-cli-deep-research](https://github.com/allenhutchison/gemini-cli-deep-research) by Allen Hutchison.

## What Was Inherited

- Gemini API integration concept (deep research + file search)
- MIME type research and documentation (`docs/file-search-mime-types.md`)
- Original ISC license (relicensed to MIT)

## What Is New

The following were built from scratch for the standalone skill:

- **Python CLI scripts** (`scripts/research.py`, `scripts/store.py`, `scripts/upload.py`, `scripts/state.py`) -- PEP 723 inline metadata, runs via `uv run` with zero pre-installation
- **SKILL.md packaging** -- skills.sh-compatible skill manifest for distribution to 30+ AI agents
- **Adaptive history-based polling** -- learns from past research completion times to optimize poll intervals (p25-p75 window targeting, separate curves for grounded vs non-grounded)
- **Disk output** (`--output-dir`) -- structured directory output with report, metadata, interaction data, and extracted sources
- **Smart sync** (`--smart-sync`) -- hash-based file change detection to skip unchanged uploads
- **Non-interactive agent mode** -- automatic TTY detection to skip confirmation prompts
- **JSON output** (`--json`) -- machine-readable output on stdout for agent consumption
- **Timeout control** (`--timeout`) -- configurable maximum wait time for blocking operations
- **Critique-driven hardening** -- 3 independent AI critics + live testing used to identify and fix edge cases

## Original Node.js/MCP Artifacts (Removed)

The original project included a Node.js MCP server (`src/index.ts`), TOML commands for Gemini CLI (`commands/`), and associated build infrastructure. These were removed during the rebrand to `agent-deep-research` as the Python CLI scripts provide equivalent functionality with simpler distribution.
