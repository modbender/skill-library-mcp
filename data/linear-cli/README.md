# linear-cli

(ClawHub skill slug: `linear-cli`)

Minimal Linear CLI for Clawban workflows, implemented with **Api2Cli (a2c)** and Linear's **GraphQL API**.

This repo intentionally contains **no custom HTTP client code**: all requests are declared in `a2c/config.xfer`.

## Prerequisites

- `a2c` installed and on your `PATH`
- A Linear API key

## Setup

```bash
export LINEAR_API_KEY="<your_linear_api_key>"
```

## Usage

Use the wrapper script (recommended):

```bash
./scripts/linear --help
./scripts/linear whoami
```

Or call `a2c` directly:

```bash
a2c --config ./a2c --workspace linear help
```

## Commands

### whoami

```bash
./scripts/linear whoami
```

### List issues by team

```bash
./scripts/linear issues-team <team_id>
```

Example:

```bash
./scripts/linear issues-team 2f4c0b77-1111-2222-3333-8d6c0d4f9999
```

### List issues by project

```bash
./scripts/linear issues-project <project_id>
```

### Get issue

```bash
./scripts/linear issue <issue_id>
```

### Add comment

```bash
./scripts/linear comment <issue_id> "This is a comment in **Markdown**"
```

### Set workflow state

```bash
./scripts/linear set-state <issue_id> <state_id>
```

## Notes

- Linear IDs used by these commands are **UUIDs** (GraphQL `String`).
- To discover `team_id`, `project_id`, or `state_id`, use Linear UI or extend `a2c/config.xfer` with additional discovery queries.

## Smoke test

```bash
# 1) dependency present
command -v a2c

# 2) help renders (no API key required)
./scripts/linear --help

# 3) auth works
export LINEAR_API_KEY="<your_linear_api_key>"
./scripts/linear whoami
```

## OpenClaw / ClawHub

This repository is structured as a publishable OpenClaw skill:

- Skill manifest: `SKILL.md`
- ClawHub metadata: `.clawhub/origin.json`
- Version: `VERSION`

## Development

- Config: `a2c/config.xfer`
- Wrapper: `scripts/linear`
