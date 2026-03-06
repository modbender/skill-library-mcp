OpenClaw CLI Cheatsheet
=======================

Quick reference for common OpenClaw CLI commands, safe usage rules, and copy-paste examples.

What this package provides
- A concise cheatsheet covering: agent, message, config, sessions, gateway/daemon, skills, agents, memory, cron, hooks, models, channels, health/status/doctor, logs, and obsidian commands.
- Safety rules and recommended workflow before running any operational commands.
- Copy-paste examples and notes for common tasks.

Usage
- Read the cheatsheet before making configuration or gateway changes.
- Use the provided examples as starting points; verify flags with `openclaw <command> --help` when unsure.

Example commands

# Send a message (copy-paste)
openclaw message send --channel telegram --target <chat_id> --message "Hello from OpenClaw"

# Create a quick calendar event (via gog)
gog calendar create iam@minhl.net --summary "퀵 호출" --from "2026-02-20T09:00:00+09:00" --to "2026-02-20T09:15:00+09:00"

Safety & Notes
- Never run destructive commands (config.apply, gateway uninstall, cron rm) without explicit confirmation.
- Keep personal tokens or local paths out of published files.

License
This repository/package is licensed under the MIT License. See LICENSE for details.
