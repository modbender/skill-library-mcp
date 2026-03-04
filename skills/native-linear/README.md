# linear

An [OpenClaw](https://clawhub.ai) skill for querying and managing Linear issues, projects, cycles, and teams — directly via `api.linear.app`, no third-party proxy.

## What it does

List and create issues, search across your workspace, manage projects and cycles, and update issue states — all by team name, no ID lookup required.

## Setup

**1. Create an API key**

Go to Linear → Settings → Account → Security & Access → API keys.

**2. Set the environment variable**

```bash
export LINEAR_API_KEY=lin_api_...
```

## Supported operations

| Resource | List | Get | Create | Update | Search |
|---|---|---|---|---|---|
| issues | ✅ | ✅ | ✅ | ✅ | ✅ |
| projects | ✅ | | | | |
| cycles | ✅ | | | | |
| teams | ✅ | | | | |
| states | ✅ | | | | |

## Usage

### Teams & states

```bash
python3 scripts/linear_query.py teams
python3 scripts/linear_query.py states --team "Engineering"
```

### Issues

```bash
# Your assigned issues
python3 scripts/linear_query.py my-issues
python3 scripts/linear_query.py my-issues --state "In Progress"

# Team issues
python3 scripts/linear_query.py issues --team "Engineering"
python3 scripts/linear_query.py issues --team "Engineering" --state "Todo"

# Specific issue
python3 scripts/linear_query.py issue ENG-123
```

### Search

```bash
python3 scripts/linear_query.py search "authentication bug"
```

### Create & update

```bash
python3 scripts/linear_query.py create --team "Engineering" --title "Fix login bug" --description "Fails on Safari" --priority 2
python3 scripts/linear_query.py update ENG-123 --state "Done"
python3 scripts/linear_query.py update ENG-123 --priority 1 --title "New title"
```

### Projects & cycles

```bash
python3 scripts/linear_query.py projects
python3 scripts/linear_query.py projects --team "Engineering"
python3 scripts/linear_query.py cycles --team "Engineering"
```

## Priority levels

| Value | Label |
|---|---|
| 0 | No priority |
| 1 | Urgent |
| 2 | High |
| 3 | Normal |
| 4 | Low |

## Requirements

- Python 3 (stdlib only, no pip installs)
- `LINEAR_API_KEY` environment variable

## How it works

All requests go to `https://api.linear.app/graphql` as POST requests with the GraphQL query in the body. Team names and state names are resolved to IDs automatically. No Bearer prefix needed — Linear accepts the API key directly in the `Authorization` header.
