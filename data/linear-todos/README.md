# Linear Todos

A complete todo management system built on Linear with smart date parsing, priorities, and CLI tools.

## Features

- 📝 Natural language dates ("tomorrow", "next Monday", "in 3 days")
- ⚡ Priority levels (urgent, high, normal, low)
- 📅 Smart scheduling (day, week, month)
- ✅ Mark todos as done
- 💤 Snooze todos to later dates
- 📊 Daily review with organized output
- ☕ Morning digest with fun greetings

## Installation

```bash
clawhub install linear-todos
```

## Setup

### 1. Install Prerequisites

You need [uv](https://docs.astral.sh/uv/) installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Get a Linear API Key

1. Go to [linear.app/settings/api](https://linear.app/settings/api)
2. Create a new API key (name it "Linear Todos" or whatever you prefer)
3. Copy the key — you'll need it for the next step

### 4. Run Setup Wizard

```bash
uv run python main.py setup
```

This will:
- Verify your API key
- Show your Linear teams
- Let you pick which team to use for todos
- Save settings to `~/.config/linear-todos/config.json`

**Or use environment variables instead of the wizard:**

```bash
export LINEAR_API_KEY="lin_api_xxxxxxxx"
export LINEAR_TEAM_ID="your-team-id"  # optional
```

## Usage

```bash
# Create todos
uv run python main.py create "Call mom" --when day
uv run python main.py create "Pay taxes" --date 2025-04-15
uv run python main.py create "Review PR" --date "next Monday" --priority high

# List todos
uv run python main.py list

# Mark done
uv run python main.py done TODO-123

# Snooze to later
uv run python main.py snooze TODO-123 "next week"

# Daily review
uv run python main.py review
```

**See [SKILL.md](SKILL.md) for complete documentation.**

## Testing

```bash
uv run pytest tests/ -v
```

106 tests. All pass.

## License

MIT
