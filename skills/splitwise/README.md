# OpenClaw Splitwise Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-Published-blue)](https://clawhub.com)

Create and manage expenses on Splitwise directly from your OpenClaw agent.

## Installation

```bash
clawhub install splitwise
```

## Configuration

Set the following environment variable:

- `SPLITWISE_API_KEY`: Your Splitwise Long-lived User Token.

## Usage

Ask your agent to:
- "Split the $50 grocery bill with Nancy"
- "Log a $15 expense for 'Coffee' with Bob"
- "Add a $100 dinner to our House group"

## Features

- **Automated 50/50 Splits**: Automatically calculates shares for two users.
- **Group Support**: Log expenses to specific Splitwise groups.
- **Secure**: Uses Python scripts for safe API interaction.
