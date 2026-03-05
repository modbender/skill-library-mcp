# HoneyDew — OpenClaw Skill

By [Smartify Inc.](https://smartify.ai) | [dev@smartify.ai](mailto:dev@smartify.ai)

**Source:** [github.com/smartify-inc/Honeydew](https://github.com/smartify-inc/Honeydew)

Manage your Kanban boards and tasks through the OpenClaw agent.

## What it does

This skill teaches your OpenClaw agent how to interact with a running [HoneyDew](https://github.com/smartify-inc/Honeydew) instance. The agent can create, update, move, and delete cards; manage boards, columns, and labels; transfer tasks between user and agent profiles; and check board summaries, overdue items, and urgent cards — all through the REST API.

## Prerequisites

- **HoneyDew running locally.** Clone the repo, run `./install.sh`, then `./start.sh`. The backend API must be reachable (default: `http://localhost:8000`).
- **No API keys required.** The app is designed for local / trusted-network use with no authentication.

## Installation

Install the skill into your OpenClaw workspace:

```bash
clawhub install Honeydew
```

Or clone the HoneyDew repo and point OpenClaw at the `skills/` directory.

## Usage

Once the skill is installed and the app is running, ask the agent to manage your tasks:

- "Create a high-priority task called 'Deploy v2' on my board."
- "Move card 5 to In Progress."
- "Show me all overdue cards."
- "Transfer the 'Fix login bug' card to me."
- "Add a 'frontend' label to card 12."

The agent will call the HoneyDew API automatically.

## Configuration

Set the `SMARTIFY_API_URL` environment variable if your instance is not at the default `http://localhost:8000`:

```bash
export SMARTIFY_API_URL=http://192.168.1.50:8000
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Connection refused" or health check fails | Make sure HoneyDew is running (`./start.sh`) |
| Wrong port | Set `SMARTIFY_API_URL` to the correct base URL |
| Cards not showing | Check that the board exists (`GET /api/boards`) |
| Profile mismatch | Verify `config.json` profile IDs match what you pass to the API |

## Screenshot

![HoneyDew board](screenshots/screenshot.png)

To seed a board with this "Ship the beta release" example (user tasks, agent-completed with token/time badges, one blocked, one transferred back), run:

```bash
python scripts/seed_board_for_screenshot.py
```

Then open http://localhost:5173 and capture the board.

## Publishing

From the repo root, publish with the display name **HoneyDew** (not "HoneyDew by Smartify"):

```bash
clawhub publish "$(pwd)/skills/honeydew" --slug honeydew --name "HoneyDew" --version 1.0.x --tags latest --changelog "..."
```

## Links

- [HoneyDew repo](https://github.com/smartify-inc/Honeydew)
- [Full API documentation](https://github.com/smartify-inc/Honeydew#api-endpoints)
- [Python agent tools reference](https://github.com/smartify-inc/Honeydew#agent-integration)

## License

MIT
