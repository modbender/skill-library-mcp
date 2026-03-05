---
name: "soccer-cli"
version: "1.0.0"
author: "J R"
description: "A CLI to check soccer scores, game details, and player stats from your terminal."
requires:
  bins:
    - name: "go"
      version: ">=1.18"
install: "install.sh"
usage: |
  soccer-cli scores "Manchester United"
  soccer-cli game <fixture_id>
  soccer-cli squad <fixture_id>
---

## soccer-cli

A command-line interface to check soccer scores, game details, and player stats using the API-Football service.

### Description

This skill provides a set of commands to quickly retrieve football data directly in your terminal. You can get the latest score for your favorite team, see detailed events from a specific match (like goals and cards), and view the full squad with player ratings and minutes played.

### Installation

1.  **Run the installer:**
    ```bash
    ./install.sh
    ```
    This will compile the Go program and move the `soccer-cli` binary to `~/.local/bin/`.

2.  **Configure API Key:**
    The CLI needs an API key from [API-Football](https://www.api-football.com/).

    Create a configuration file at `~/.config/soccer-cli/config.yaml`:
    ```bash
    mkdir -p ~/.config/soccer-cli
    touch ~/.config/soccer-cli/config.yaml
    ```

    Add your API key to the file in the following format:
    ```yaml
    apikey: YOUR_API_KEY_HERE
    ```

### Usage

-   **Get the latest score for a team:**
    ```bash
    soccer-cli scores "<team-name>"
    ```
    Example: `soccer-cli scores "Real Madrid"`

-   **Get detailed events from a game:**
    (Use the Fixture ID from the `scores` command)
    ```bash
    soccer-cli game <fixture_id>
    ```
    Example: `soccer-cli game 123456`

-   **Get the squad and player stats for a game:**
    ```bash
    soccer-cli squad <fixture_id>
    ```
    Example: `soccer-cli squad 123456`
