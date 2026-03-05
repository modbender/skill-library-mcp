# SSH Config Manager

A CLI tool to manage SSH configuration files (`~/.ssh/config`). Organize hosts, generate configs, test connections, and keep your SSH config clean.

## Installation

Install via ClawHub:

```bash
clawhub install ssh-config-manager
```

## Usage

```bash
# List all hosts
python3 scripts/main.py list

# Add a new host
python3 scripts/main.py add --host myserver --hostname 192.168.1.100 --user admin

# Test SSH connection
python3 scripts/main.py test --host myserver

# Validate config syntax
python3 scripts/main.py validate

# Remove a host
python3 scripts/main.py remove --host myserver
```

## Features

- Parse and display SSH configs in readable format
- Add, edit, remove hosts
- Test SSH connections with timeout
- Validate config syntax
- Backup before making changes
- Organize hosts with tags (basic)

## Requirements

- Python 3.x
- SSH client installed

## Limitations

- Basic syntax validation
- Connection testing requires SSH keys setup
- Does not manage SSH keys
- Limited to standard SSH config options

## License

MIT