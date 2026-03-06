# soccer-cli

A command-line interface to check soccer scores, game details, and player stats using the [API-Football](https://www.api-football.com/) service.

This tool is an OpenClaw skill that provides a set of commands to quickly retrieve football data directly in your terminal. You can get the latest score for your favorite team, see detailed events from a specific match (like goals and cards), and view the full squad with player ratings and minutes played.

## Installation

1.  **Prerequisites:**
    -   You must have **Go** (version 1.18 or higher) installed.
    -   Ensure `~/.local/bin` is in your shell's `PATH`.

2.  **Build and Install:**
    Clone this repository and run the installer:
    ```bash
    git clone https://github.com/jrojas537/soccer-cli.git
    cd soccer-cli
    chmod +x install.sh
    ./install.sh
    ```
    This will compile the program and move the `soccer-cli` binary to `~/.local/bin/`.

3.  **Configure API Key:**
    The CLI needs a free API key from [API-Football](https://www.api-football.com/).

    Create a configuration file at `~/.config/soccer-cli/config.yaml`:
    ```bash
    mkdir -p ~/.config/soccer-cli
    touch ~/.config/soccer-cli/config.yaml
    ```

    Add your API key to the file in the following format:
    ```yaml
    apikey: YOUR_API_KEY_HERE
    ```

## Usage

### Get the latest score for a team
This command returns the most recent match result and its Fixture ID.

```bash
soccer-cli scores "<team-name>"
```
**Example:**
```
$ soccer-cli scores "Manchester United"
+---------+------------+--------------------+---------+-----------+-----------+
|   ID    |    DATE    |        HOME        |  SCORE  |   AWAY    |  STATUS   |
+---------+------------+--------------------+---------+-----------+-----------+
| 1134599 | 2026-02-15 | Manchester United  | 2 - 1   | Liverpool | Match Finished |
+---------+------------+--------------------+---------+-----------+-----------+
```

### Get detailed events from a game
Using the Fixture ID from the `scores` command, you can get a log of goals, assists, and cards.

```bash
soccer-cli game <fixture_id>
```
**Example:**
```
$ soccer-cli game 1134599
```

### Get the squad and player stats for a game
Also using the Fixture ID, you can retrieve the full squad list with positions, minutes played, and individual player ratings.

```bash
soccer-cli squad <fixture_id>
```
**Example:**
```
$ soccer-cli squad 1134599
```

---
*Built as an OpenClaw skill.*
