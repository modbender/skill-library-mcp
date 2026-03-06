---
name: linear
description: "Query and manage Linear issues, projects, cycles, and teams via the Linear GraphQL API. Use when you need to list or create issues, check cycle status, manage projects, or search across your workspace. Calls api.linear.app directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - LINEAR_API_KEY
      bins:
        - python3
    primaryEnv: LINEAR_API_KEY
    files:
      - "scripts/*"
---

# Linear

Interact with Linear directly via the Linear GraphQL API (`api.linear.app/graphql`).

## Setup (one-time)

1. Go to Linear → Settings → Account → Security & Access → API keys
2. Create a new key
3. Set environment variable:
   ```
   LINEAR_API_KEY=lin_api_...
   ```

## Usage

### List your teams
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py teams
```

### List issues assigned to you
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py my-issues
python3 /mnt/skills/user/linear/scripts/linear_query.py my-issues --state "In Progress"
```

### List issues for a team
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py issues --team "Engineering"
python3 /mnt/skills/user/linear/scripts/linear_query.py issues --team "Engineering" --state "Todo" --limit 20
```

### Get a specific issue
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py issue ENG-123
```

### Search issues
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py search "authentication bug"
```

### Create an issue
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py create --team "Engineering" --title "Fix login bug" --description "Users can't log in on Safari"
python3 /mnt/skills/user/linear/scripts/linear_query.py create --team "Engineering" --title "Add dark mode" --priority 2
```

### Update an issue
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py update ENG-123 --state "Done"
python3 /mnt/skills/user/linear/scripts/linear_query.py update ENG-123 --priority 1 --title "New title"
```

### List projects
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py projects
python3 /mnt/skills/user/linear/scripts/linear_query.py projects --team "Engineering"
```

### List cycles (sprints)
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py cycles --team "Engineering"
```

### List workflow states for a team
```bash
python3 /mnt/skills/user/linear/scripts/linear_query.py states --team "Engineering"
```

## Priority levels
- 0 = No priority
- 1 = Urgent
- 2 = High
- 3 = Normal
- 4 = Low
