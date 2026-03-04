---
name: db-query
description: Query project databases with automatic SSH tunnel management. Use when you need to execute SQL queries against configured databases, especially those accessible only via SSH tunnels. Automatically manages SSH connection lifecycle (establishes tunnel before query, closes after). Supports multiple databases distinguished by description/name from config file.
---

# Database Query

## Overview

Query databases through a centralized configuration file with automatic SSH tunnel management. Handles connection details, SSH tunnel setup/teardown, and query execution.

## Security

**Passwords are never exposed in process lists.** The skill uses environment variables for credentials:
- `MYSQL_PWD` for database passwords (passed to mysql client)
- `SSHPASS` for SSH tunnel passwords (passed to sshpass)

**Recommended:** Store credentials in environment variables instead of the config file for better security.

## Configuration

### Setup

1. **Create config file** at `~/.config/clawdbot/db-config.json`:
   ```bash
   mkdir -p ~/.config/clawdbot
   # Copy example config and edit
   cp /usr/lib/node_modules/clawdbot/skills/db-query/scripts/config.example.json ~/.config/clawdbot/db-config.json
   ```

2. **Add database entries** with these fields:
   - `name`: Description used to find the database (required)
   - `host`: Database host (required)
   - `port`: Database port (default: 3306)
   - `database`: Database name (required)
   - `user`: Database user (required)
   - `password`: Database password (optional, can use env var)
   - `ssh_tunnel`: Optional SSH tunnel configuration

3. **SSH tunnel configuration** (if needed):
   - `enabled`: true/false
   - `ssh_host`: Remote SSH host
   - `ssh_user`: SSH username
   - `ssh_port`: SSH port (default: 22)
   - `local_port`: Local port to forward (e.g., 3307)
   - `remote_host`: Remote database host behind SSH (default: localhost)
   - `remote_port`: Remote database port (default: 3306)

### Environment Variables (Recommended)

Instead of storing passwords in the config file, use environment variables:

```bash
# Format: DB_PASSWORD_<DATABASE_NAME> (spaces replaced with underscores, uppercase)
export DB_PASSWORD_PRODUCTION_USER_DB="your_db_password"

# Format: SSH_PASSWORD_<DATABASE_NAME> for SSH tunnel password
export SSH_PASSWORD_PRODUCTION_USER_DB="your_ssh_password"
```

### Example Config

```json
{
  "databases": [
    {
      "name": "Production User DB",
      "host": "localhost",
      "port": 3306,
      "database": "user_db",
      "user": "db_user",
      "password": "",
      "ssh_tunnel": {
        "enabled": true,
        "ssh_host": "prod.example.com",
        "ssh_user": "deploy",
        "local_port": 3307
      }
    }
  ]
}
```

Set environment variables (recommended):
```bash
export DB_PASSWORD_PRODUCTION_USER_DB="your_db_password"
export SSH_PASSWORD_PRODUCTION_USER_DB="your_ssh_password"
```

## Usage

### List Databases

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py --list
```

### Query a Database

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py \
  --database "Production User DB" \
  --query "SELECT * FROM users LIMIT 10"
```

The script will:
1. Find database by matching description in config
2. Start SSH tunnel (if configured)
3. Execute query
4. **Automatically close SSH tunnel** (important for cleanup)

### With Custom Config Path

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py \
  --config /path/to/custom-config.json \
  --database "test" \
  --query "SHOW TABLES"
```

## Requirements

- MySQL client: `apt install mysql-client` or equivalent
- SSH client: usually pre-installed on Linux/Mac
- Python 3.6+

## Notes

- SSH tunnels are automatically closed after query execution
- Use `--list` to see all configured databases and their descriptions
- Database search is case-insensitive partial match on `name` field
- Local ports for SSH tunnels should be unique per database
