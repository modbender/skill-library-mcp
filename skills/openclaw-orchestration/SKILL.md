# Orchestration Skill

Multi-agent task orchestration framework. Agents delegate tasks via a shared SQLite queue, with .md interchange files for visibility.

## Quick Start
```bash
cd skills/orchestration
npm install
node src/cli.js agent register my-agent --capabilities "coding,research"
node src/cli.js task create "Build feature X" --desc "..." --priority high
node src/cli.js task claim <task-id> --agent my-agent
node src/cli.js task complete <task-id> --summary "Done"
node src/cli.js refresh
```

## Design
- **DB is source of truth** — .md files are read-only projections
- **Atomic claims** — only one agent can claim a pending task
- **Dependencies** — tasks can depend on other tasks
- **Timeout + retry** — `sweep` handles stale tasks
- **Interchange** — `refresh` generates .md files via @openclaw/interchange
