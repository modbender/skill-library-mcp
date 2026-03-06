# Tailscale Network Orchestrator Skill for ClawBot

## Overview

The **Tailscale Network Orchestrator** is a ClawBot skill designed to provide direct management and monitoring of your Tailscale network and connected devices. It leverages the `tailscale` command-line interface (CLI) installed on the host system where ClawBot is running. This allows for secure and direct interaction with your Tailscale network, enabling you to check status and list devices without needing to expose sensitive API keys directly within the skill's code.

## Features

*   **Tailscale Status:** Get a summary of your Tailscale connection status.
*   **Device Listing:** View all connected devices in your Tailscale network, including their IP addresses and online status.
*   **Secure Operation:** Relies on the locally installed `tailscale` CLI, avoiding the need for API key management within the skill itself.

## Prerequisites

This skill requires the **Tailscale CLI** to be installed and configured on the system where your ClawBot instance is running. If you haven't already, please install Tailscale by following the official instructions:

*   [Install Tailscale](https://tailscale.com/download)

Ensure that the `tailscale` command is accessible in your system's PATH.

## Installation

1.  **Create Skill Directory:** Create a new folder named `tailscale-orchestrator` in your ClawBot skills directory (e.g., `~/.openclaw/skills/` or `<project>/skills/`).
2.  **Download Files:** Place the `SKILL.md`, `main.py`, `requirements.txt`, and `README.md` files into this new directory.
3.  **No Python Dependencies:** This skill uses only standard Python libraries and the `tailscale` CLI, so no `pip install` is required for Python dependencies.

## Usage

Once installed and configured, you can trigger the skill via your ClawBot interface using phrases like:

*   "manage tailscale"
*   "tailscale status"
*   "list tailscale devices"

### Examples

*   To get the current Tailscale status:
    ```
    ClawBot, tailscale status
    ```
*   To list all connected devices:
    ```
    ClawBot, list tailscale devices
    ```

## Security Considerations

*   **Local CLI Dependency:** This skill executes local `tailscale` CLI commands. Ensure your ClawBot environment is secure and that you trust the `tailscale` CLI installation.
*   **Permissions:** The user running ClawBot must have appropriate permissions to execute `tailscale` commands.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests on the GitHub repository for this skill.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
