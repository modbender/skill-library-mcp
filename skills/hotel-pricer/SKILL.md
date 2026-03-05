# hotel-pricer Skill

A Go-based CLI for searching hotel availability and pricing using the Amadeus API.

## Description

This skill allows the agent to find hotel deals by city, check-in/out dates, and number of guests. It securely manages Amadeus API credentials and provides formatted JSON output.

## Prerequisites

- `go` (for installation)
- An Amadeus for Developers account with API Key and Secret.

## Installation

The `hotel-pricer` binary must be compiled and placed in the system's PATH.

```bash
# From the hotel-pricer source directory
go build
sudo mv hotel-pricer /usr/local/bin/
```

## Configuration

Credentials must be set before use.

```bash
hotel-pricer config set --api-key YOUR_API_KEY --api-secret YOUR_API_SECRET
```

## Usage

### Search for Hotels

```bash
hotel-pricer search --city <IATA_CODE> --check-in <YYYY-MM-DD> --check-out <YYYY-MM-DD> [flags]
```

**Example:**
`hotel-pricer search --city NYC --check-in 2024-12-24 --check-out 2024-12-28 --guests 2`

### Flags

- `--city, -c`: City code (IATA) (required)
- `--check-in, -i`: Check-in date (YYYY-MM-DD) (required)
- `--check-out, -o`: Check-out date (YYYY-MM-DD) (required)
- `--guests, -g`: Number of guests (default: 1)
- `--radius, -r`: Search radius in kilometers (default: 20)
