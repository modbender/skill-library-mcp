# flight-pricer Skill

A command-line interface (CLI) to search for flight prices using the Duffel API.

This skill has been structured as a professional-grade CLI tool, inspired by the quality standard of the `gog` skill.

## Prerequisites

- Python 3.7+ and `pip`.
- A Duffel API key.

## Installation

The skill is designed to be installed as a proper command-line tool within its own virtual environment. This isolates its dependencies and makes it available system-wide for the agent.

From the workspace root:

```bash
# 1. Activate the virtual environment
source flight-pricer/.venv/bin/activate

# 2. Perform an editable install
pip install -e flight-pricer/

# 3. Deactivate (optional, the command is now linked)
deactivate
```

This only needs to be done once.

## Setup

Before you can search for flights, you must configure the skill with your Duffel API key.

### `config set`

Securely saves your API key to `~/.config/flight-pricer/config.yaml`.

**Usage:**
```bash
flight-pricer config set --api-key <YOUR_DUFFEL_API_KEY>
```

## Commands

### `search`

Searches for flight offers based on the specified criteria. The command will automatically use the API key from your configuration.

**Usage:**
```bash
flight-pricer search [OPTIONS]
```

**Required Options:**

- `--from <IATA>`: Departure airport IATA code (e.g., `DTW`).
- `--to <IATA>`: Arrival airport IATA code (e.g., `MIA`).
- `--depart <YYYY-MM-DD>`: Departure date.

**Optional Options:**

- `--return <YYYY-MM-DD>`: Return date for a round-trip flight.
- `--passengers <number>`: Number of passengers (default: 1).
- `--max-stops <number>`: Maximum number of connections.
- `--non-stop`: A convenient alias for `--max-stops 0`.
- `--cabin <class>`: Cabin class. Choices: `economy`, `business`, `first`, `premium_economy`.

**Example:**

Search for a non-stop, first-class flight for one person from Detroit to Miami, departing April 6, 2026 and returning April 10, 2026.

```bash
flight-pricer search --from DTW --to MIA --depart 2026-04-06 --return 2026-04-10 --non-stop --cabin first
```
