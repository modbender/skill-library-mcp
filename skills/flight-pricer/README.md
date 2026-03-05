# flight-pricer

A professional-grade command-line interface (CLI) for searching flight prices using the Duffel API. This tool is designed for efficiency, security, and ease of use, both for direct user interaction and for integration with agents.

## Features

-   **World-Class CLI:** Proper command structure with subcommands (`search`, `config`).
-   **Secure Authentication:** Securely stores your Duffel API key in `~/.config/flight-pricer/config.yaml`. No hardcoded credentials.
-   **Comprehensive Search:** Filter flights by origin, destination, dates, cabin class, passenger count, and number of stops.
-   **Intuitive Aliases:** Includes convenient flags like `--non-stop`.
-   **Clean Output:** Displays results in a clean, human-readable table.
-   **Installable Package:** Packaged as a standard Python application, making `flight-pricer` available as a system command.

## Prerequisites

-   Python 3.7+
-   pip
-   A Duffel API Key ([Get one here](https://duffel.com/))

## Installation

1.  **Clone the repository (or ensure it is present in your workspace):**
    ```bash
    git clone https://github.com/jrojas537/flight-pricer.git
    cd flight-pricer
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Perform an editable installation:**
    This command links the script into your path, making `flight-pricer` a globally available command within the activated environment.
    ```bash
    pip install -e .
    ```

## Configuration

Before you can search, you must set your Duffel API key. This only needs to be done once.

```bash
flight-pricer config set --api-key YOUR_DUFFEL_API_KEY
```
This command will create the configuration file and securely store your key.

## Usage

The primary command is `search`. It takes several options to define your flight search.

### Options

-   `--from <IATA>`: **(Required)** Departure airport IATA code (e.g., `DTW`).
-   `--to <IATA>`: **(Required)** Arrival airport IATA code (e.g., `MIA`).
-   `--depart <YYYY-MM-DD>`: **(Required)** Departure date.
-   `--return <YYYY-MM-DD>`: (Optional) Return date for a round-trip flight.
-   `--passengers <number>`: (Optional) Number of passengers (default: 1).
-   `--max-stops <number>`: (Optional) Maximum number of connections.
-   `--non-stop`: (Optional) A convenient alias for `--max-stops 0`.
-   `--cabin <class>`: (Optional) Cabin class. Choices: `economy`, `business`, `first`, `premium_economy`.

### Examples

**Search for a non-stop, first-class flight for one person:**
```bash
flight-pricer search --from DTW --to MIA --depart 2026-04-06 --return 2026-04-10 --non-stop --cabin first
```

**Search for a one-way economy flight for two passengers:**
```bash
flight-pricer search --from JFK --to LAX --depart 2026-08-15 --passengers 2 --cabin economy
```
