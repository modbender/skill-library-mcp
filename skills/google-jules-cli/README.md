# Jules Tools Skill for OpenClaw

This repository contains an **OpenClaw AgentSkill** that enables AI agents to interface with the [Jules Tools CLI](https://jules.google/docs/cli/reference/). This allows your AI assistant to manage Google's Jules coding sessions, including starting new tasks, listing sessions, and retrieving code changes.

## Features

- **Installation Check**: Verifies if the `jules` CLI is installed and guides the installation if needed.
- **Authentication**: Provides instructions for logging in with your Google account.
- **Session Management**: Supports listing, creating, and pulling results from remote coding sessions.

## Installation

To add this skill to your OpenClaw agent:

1.  **Clone or Copy**: Place the `jules-tools-skill` directory into your OpenClaw skills directory (typically `skills/` or `~/.openclaw/skills/`).

    ```bash
    cp -r jules-tools-skill ~/.openclaw/skills/
    ```

2.  **Restart OpenClaw**: Restart your OpenClaw agent to load the new skill.

3.  **Verify**: Ask your agent "List my Jules sessions" or "Help me install Jules Tools" to verify the skill is active.

## Usage

Once installed, you can interact with the skill through natural language commands to your agent.

**Examples:**

- "Install Jules Tools CLI."
- "Login to Jules."
- "Start a new coding session to fix the login bug in this repo."
- "List my active Jules sessions."
- "Pull the changes from session 12345."

## Requirements

- **OpenClaw**: A running instance of OpenClaw (or compatible agent framework).
- **Node.js & npm**: Required to install the `@google/jules` package.
- **Google Account**: Required for authentication with Jules.

## License

This project is licensed under the MIT License.
