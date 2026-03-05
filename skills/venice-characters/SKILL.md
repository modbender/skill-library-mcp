---
name: venice-characters
description: Browse Venice AI's character personas library - discover AI characters for roleplay, creative writing, and conversations.
homepage: https://venice.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🎭",
        "requires": { "bins": ["uv"], "env": ["VENICE_API_KEY"] },
        "primaryEnv": "VENICE_API_KEY",
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Venice Characters

Browse Venice AI's library of character personas - discover AI characters for roleplay, creative writing, and engaging conversations.

**API Base URL:** `https://api.venice.ai/api/v1`
**Documentation:** [docs.venice.ai](https://docs.venice.ai)

## Setup

1. Get your API key from [venice.ai](https://venice.ai) → Settings → API Keys
2. Set the environment variable:

```bash
export VENICE_API_KEY="your_api_key_here"
```

---

## Browse Characters

```bash
uv run {baseDir}/scripts/characters.py
```

**Options:**

- `--search`: Search by name or description
- `--tag`: Filter by tag
- `--limit`: Max results (default: 20)
- `--format`: Output format: `table`, `json`, `list` (default: `table`)
- `--output`: Save to file

---

## Examples

**List popular characters:**
```bash
uv run {baseDir}/scripts/characters.py
```

**Search for a character:**
```bash
uv run {baseDir}/scripts/characters.py --search "assistant"
```

**Filter by tag:**
```bash
uv run {baseDir}/scripts/characters.py --tag "creative"
```

**Export to JSON:**
```bash
uv run {baseDir}/scripts/characters.py --format json --output characters.json
```

---

## Character Info

Each character includes:
- **Name & Description** - Character identity
- **Slug** - Unique identifier for API use
- **Model** - The LLM powering the character
- **Tags** - Categories/themes
- **Stats** - Popularity metrics

---

## Using Characters

Characters can be used with Venice's chat completions by specifying the character slug in your prompts or via the Venice web interface.

---

## Runtime Note

This skill uses `uv run` which automatically installs Python dependencies (httpx) via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata. No manual Python package installation required - `uv` handles everything.

---

## API Reference

| Endpoint | Description | Auth |
|----------|-------------|------|
| `GET /characters` | List all characters | API key |
| `GET /characters/:slug` | Get character details | API key |

Full API docs: [docs.venice.ai](https://docs.venice.ai)

