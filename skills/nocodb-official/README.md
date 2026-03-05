# NocoDB Agent Skills

Agent Skills to help developers using AI agents with NocoDB. Agent Skills are folders of instructions, scripts, and resources that agents like Claude Code, Cursor, Github Copilot, etc... can discover and use to do things more accurately and efficiently.

The skills in this repo follow the [Agent Skills](https://agentskills.io) format.

## Installation

```
npx skills add nocodb/agent-skills
```

## Claude Code Plugin

You can also install the skills in this repo as Claude Code plugins:

```
/plugin marketplace add nocodb/agent-skills
```

## Usage

Skills are automatically available once installed. The agent will use them when relevant tasks are detected.

**Examples:**

```
Create a new NocoDB base for tracking inventory
```

```
Query records from my table where status is active
```

```
Set up the NocoDB API connection
```

## Skill Structure

Each skill follows the [Agent Skills Open Standard](https://agentskills.io):

- `SKILL.md` - Required skill manifest with frontmatter (name, description, metadata)
- `scripts/` - Executable shell scripts

## License

MIT
