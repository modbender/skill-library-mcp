# Verk Skill for OpenClaw

Manage your [Verk](https://verkapp.com) tasks, projects, and automation flows directly from OpenClaw via natural language.

## Setup

### 1. Get a Verk API Key

1. Log in to [Verk](https://verkapp.com)
2. Go to **Settings > API Keys**
3. Generate a new API key (format: `verk_sk_...`)
4. Copy your **Organization ID** from the URL or settings

### 2. Install the Skill

Copy this skill to your OpenClaw workspace:

```bash
cp -r . ~/.openclaw/workspace/skills/verk/
```

Or install from ClawHub:

```bash
clawhub install verk
```

### 3. Set Environment Variables

Add to your OpenClaw configuration or shell profile:

```bash
export VERK_API_KEY="verk_sk_your_key_here"
export VERK_ORG_ID="org-your-org-id"
```

## Usage

Chat with your OpenClaw agent using natural language:

- "List my Verk tasks"
- "Create a task called 'Review Q2 roadmap' with high priority"
- "Mark task-abc123 as done"
- "What are my urgent tasks?"
- "Add a comment to task-xyz: 'Looking good, approved'"
- "Show me all projects"
- "Trigger the daily-standup flow"

## Available Commands

| Command | Description |
|---------|-------------|
| `tasks list` | List tasks with optional filters |
| `tasks get <id>` | Get details for a specific task |
| `tasks create` | Create a new task |
| `tasks update <id>` | Update an existing task |
| `tasks delete <id>` | Delete a task |
| `tasks comment <id>` | Add a comment to a task |
| `tasks comments <id>` | List comments on a task |
| `projects list` | List all projects |
| `flows list` | List automation flows |
| `flows trigger <id>` | Trigger an automation flow |

## Requirements

- Node.js 18+ (for built-in `fetch`)
- Verk API key with appropriate permissions
- Verk Organization ID

## License

MIT
