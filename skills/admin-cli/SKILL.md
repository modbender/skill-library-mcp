# admin-cli

## Description
Provides a simple command-line interface for performing administrative tasks that require elevated privileges.

### Commands
- `update-system`: Run package manager update (`pacman -Syu`).
- `restart-service <service>`: Restart a systemd service.
- `check-status`: Show OS version and current uptime.

> **Note:** These commands use the `elevated` flag. Ensure the agent has the necessary permissions in its configuration.
