# Zettel Brainstormer

An AI-powered skill for expanding **Zettelkasten** notes into comprehensive writing drafts.

## Overview

This skill provides a **3-stage pipeline** to transform your atomic notes into a coherent draft:
1.  **Find Links**: Scans a seed note and identifies connections. Supports:
    - **Standard**: Wikilinks and Tag matching.
    - **`obsidian-cli` (Recommended)**: Uses the native CLI for fast vault indexing.
    - **`zettel-link` (Optional)**: Semantic discovery for "hidden" connections without explicit links.
2.  **Preprocess**: Reads the files and context to generate a high-quality Markdown outline using a sub-agent.
3.  **Draft**: Reads the outline and context to generate a high-quality Markdown draft using a Pro LLM.

## Documentation

**👉 See [SKILL.md](SKILL.md) for full installation, configuration, and usage instructions.**

## Quick Start

### Prerequisites
-   Python 3.10+
-   Your favorite AI Agent system (OpenCode, Cursor, OpenClaw, etc.)
-   Optionally, `OPENAI_API_KEY` (or OpenRouter key) set in environment.

### Installation
```bash
# Clone repository
npx skills install https://github.com/hxy9243/skills/blob/main/zettel-brainstormer/
```

### Usage

1. Prompt your AI Agent to configure the skill.
2. Prompt your AI Agent to run the skill.


## License
MIT
