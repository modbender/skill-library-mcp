---
name: jules-tools-skill
version: 1.0.0
description: "Interface with Google's Jules Tools CLI to manage AI coding sessions."
permissions:
  exec:
    - jules
    - npm
---

# Jules Tools Skill

This skill allows the AI agent to interface with the **Jules Tools CLI** to manage Google's Jules AI coding sessions. With this skill, the agent can start new coding sessions, list active sessions, and retrieve results directly from the terminal.

## Prerequisites

Before using any Jules commands, ensure the `jules` CLI is installed and authenticated.

### 1. Installation

Check if `jules` is installed by running:

```bash
jules --version
```

If the command is not found, install it using `npm`:

```bash
npm install -g @google/jules
```

> **Note:** Installation might require `sudo` permissions depending on the system configuration. If `npm install -g` fails due to permissions, try `sudo npm install -g @google/jules` or ask the user for assistance.

### 2. Authentication

The agent must be authenticated to interact with Jules. To authenticate, run:

```bash
jules login
```

This command will open a browser window for the user to sign in with their Google account. If the agent is running in a headless environment, guide the user to perform this step on their local machine or provide alternative authentication methods if available (refer to `jules login --help`).

To verify authentication or log out, use:

```bash
jules logout
```

## Usage

The primary command for interacting with Jules is `jules remote`.

### List Sessions

To see all active or past coding sessions:

```bash
jules remote list --session
```

To list connected repositories:

```bash
jules remote list --repo
```

### Start a New Session

To start a new coding session (task) for Jules:

```bash
jules remote new --repo <repo_name> --session "<task_description>"
```

- `<repo_name>`: The repository name (e.g., `torvalds/linux`) or `.` for the current directory's repo.
- `<task_description>`: A clear description of what Jules should do (e.g., "Fix the bug in the login handler").

**Example:**

```bash
jules remote new --repo . --session "Add a new test case for the user profile component"
```

You can also start multiple parallel sessions:

```bash
jules remote new --repo . --session "Refactor the database schema" --parallel 2
```

### Retrieve Session Results

Once a session is complete, you can pull the results (code changes):

```bash
jules remote pull --session <session_id>
```

- `<session_id>`: The ID of the session you want to pull (obtained from `jules remote list`).

### General Help

For more information on any command:

```bash
jules --help
jules remote --help
```

## Troubleshooting

- **Command not found**: Ensure `jules` is in the system PATH after installation. You may need to restart the shell or source the profile.
- **Authentication errors**: Try running `jules logout` and then `jules login` again.
- **Network issues**: Ensure the agent has internet access to reach Google's servers.
