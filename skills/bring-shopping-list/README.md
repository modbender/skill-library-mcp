# bring-shopping-list

An agent skill for managing [Bring!](https://www.getbring.com/) shopping lists. Add, remove, complete, and view items on your Bring! shopping list through natural language.

Compatible with Claude Code, Cursor, Windsurf, OpenAI Codex CLI, GitHub Copilot, Gemini CLI, and other agents supporting the [SKILL.md standard](https://agentskills.io/specification).

## Installation

Copy this folder into your agent's skills directory:

```bash
# Claude Code
cp -r bring-shopping-list ~/.claude/skills/

# Cursor
cp -r bring-shopping-list ~/.cursor/skills/

# Codex CLI
cp -r bring-shopping-list ~/.codex/skills/

# or project-specific (example for Claude Code)
cp -r bring-shopping-list your-project/.claude/skills/
```

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Bring! account with email/password login

> **Google login users:** Go to your Bring! account settings and set a separate password for API access.

### Environment Variables

Set these in your shell or in a `.env` file:

```bash
BRING_EMAIL=your-email@example.com
BRING_PASSWORD=your-password
```

## Usage

Once installed, your agent will automatically use this skill when you ask about shopping or groceries:

- "Add milk and eggs to the shopping list"
- "What's on my list?"
- "Remove butter from the list"

### CLI

#### With uv (recommended, no install needed)

```bash
uv run --with bring-api --with python-dotenv python bring.py list
uv run --with bring-api --with python-dotenv python bring.py add "Milk" "Eggs" "Butter:unsalted"
uv run --with bring-api --with python-dotenv python bring.py remove "Milk"
uv run --with bring-api --with python-dotenv python bring.py complete "Eggs"
```

#### With pip

```bash
pip install -r requirements.txt
python bring.py list
python bring.py add "Milk" "Eggs" "Butter:unsalted"
python bring.py remove "Milk"
python bring.py complete "Eggs"
```

Items support optional specifications via colon syntax: `"Milk:low fat"`, `"Butter:Irish"`.

## How It Works

The skill uses the unofficial [bring-api](https://github.com/miaucl/bring-api) Python package to interact with Bring's API. It authenticates with your credentials, finds your default shopping list, and performs operations on it.

## License

MIT
