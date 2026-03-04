# skill-search

Find and discover available skills without loading them all into context.

## The Problem

Every skill you load into an agent's context consumes tokens and attention. Loading 10+ skills at once clutters the prompt and degrades performance.

## The Solution

Keep only `skill-search` loaded. When you need a specific capability, search first, then load just that skill.

## Installation

Copy this folder into your agent's skills directory:

```bash
# For OpenClaw agents
cp -r skill-search ~/.openclaw/workspace/skills/

# Or wherever your agent loads skills from
```

## Usage

### From the Agent

When the agent receives a task, have it run:

```bash
./scripts/skill_search.py "weather"
```

This finds relevant skills without loading them into context.

### From Command Line

```bash
# Search for skills matching a keyword
./scripts/skill_search.py "pdf"

# List all available skills
./scripts/skill_search.py --list-all

# Output as JSON (for scripting)
./scripts/skill_search.py "image" --json
```

## Workflow

1. **User asks**: "I need to generate some images"
2. **Agent runs**: `skill_search.py "image"`
3. **Agent sees**: `openai-image-gen` — Batch-generate images via OpenAI Images API
4. **Agent loads**: Only `openai-image-gen/SKILL.md` and uses it

Result: One skill in context instead of ten.

## How It Works

The script searches:
- System skills: `/usr/local/lib/node_modules/openclaw/skills/`
- User skills: `~/.openclaw/workspace/skills/`

It parses `SKILL.md` frontmatter (name, description) to build an index without loading file contents.

## Files

- `SKILL.md` — Skill definition (loaded by agent)
- `scripts/skill_search.py` — Search executable
- `README.md` — This file

## License

MIT (or wherever this ends up)
