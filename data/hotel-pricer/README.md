# hotel-pricer

`hotel-pricer` is a command-line interface (CLI) tool for searching hotel availability and pricing using the Amadeus Self-Service API. It is designed to be used both by humans and as a skill within the OpenClaw agent framework.

## Features

-   Search for hotels by city, dates, and number of guests.
-   Securely stores API credentials.
-   Implements token caching to reduce API calls.
-   Outputs clean, formatted JSON.

## Prerequisites

-   Go (v1.18+)
-   An [Amadeus for Developers](https://developers.amadeus.com/) account with an active API Key and API Secret.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jrojas537/hotel-pricer.git
    cd hotel-pricer
    ```

2.  **Build the binary:**
    ```bash
    go build
    ```

3.  **Move the binary to your PATH:**
    ```bash
    sudo mv hotel-pricer /usr/local/bin/
    ```

## Configuration

Before you can use the tool, you must set your Amadeus API credentials:

```bash
hotel-pricer config set --api-key YOUR_API_KEY --api-secret YOUR_API_SECRET
```

## Usage

To perform a search, use the `search` subcommand with the required flags.

```bash
hotel-pricer search --city <IATA_CODE> --check-in <YYYY-MM-DD> --check-out <YYYY-MM-DD> [flags]
```

### Example

```bash
hotel-pricer search --city NYC --check-in 2024-12-24 --check-out 2024-12-28 --guests 2
```

### All Flags

-   `--city, -c`: City code (IATA) to search for hotels (required).
-   `--check-in, -i`: Check-in date in YYYY-MM-DD format (required).
-   `--check-out, -o`: Check-out date in YYYY-MM-DD format (required).
-   `--guests, -g`: Number of guests (default: 1).
-   `--radius, -r`: Search radius in kilometers (default: 20).
