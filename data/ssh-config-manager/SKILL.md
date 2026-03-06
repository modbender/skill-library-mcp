---
name: ssh-config-manager
description: CLI tool to manage SSH config files, organize hosts, generate configs, and test connections.
version: 1.0.0
author: skill-factory
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# SSH Config Manager

## What This Does

A CLI tool to manage SSH configuration files (`~/.ssh/config`). It helps you organize SSH hosts, generate configurations, test connections, and keep your SSH config clean and maintainable.

Key features:
- **Parse and display** existing SSH configs in readable format
- **Add/remove/edit** hosts in your SSH config
- **Organize hosts** with tags, groups, or categories
- **Test SSH connections** to verify hosts work
- **Generate configs** from templates or JSON/YAML input
- **Validate syntax** to ensure config files are correct
- **Backup and restore** your SSH config before making changes

## When To Use

- Your `~/.ssh/config` file has become messy with dozens of hosts
- You need to quickly test if SSH connections work
- You want to share SSH configs with team members
- You frequently switch between different environments (work/home/cloud)
- You want to organize hosts by project, environment, or team
- You need to validate SSH config syntax before applying changes

## Usage

Basic commands:

```bash
# List all hosts in your SSH config
python3 scripts/main.py list

# Add a new host
python3 scripts/main.py add --host myserver --hostname 192.168.1.100 --user admin

# Test SSH connection to a host
python3 scripts/main.py test --host myserver

# Organize hosts by tags
python3 scripts/main.py organize --tag work --hosts server1,server2,server3

# Generate SSH config from YAML template
python3 scripts/main.py generate --template servers.yaml --output ~/.ssh/config

# Validate SSH config syntax
python3 scripts/main.py validate --file ~/.ssh/config
```

## Examples

### Example 1: List and organize hosts

```bash
python3 scripts/main.py list --format table
```

Output:
```
┌─────────────────┬──────────────────────┬───────────┬───────────────┐
│ Host            │ Hostname             │ User      │ Tags          │
├─────────────────┼──────────────────────┼───────────┼───────────────┤
│ github          │ github.com           │ git       │ git           │
│ work-server     │ 192.168.1.100       │ admin     │ work,prod     │
│ staging         │ staging.example.com  │ deploy    │ work,staging  │
│ personal-vps    │ 45.33.22.11          │ root      │ personal      │
└─────────────────┴──────────────────────┴───────────┴───────────────┘
```

### Example 2: Add a new host with advanced options

```bash
python3 scripts/main.py add \
  --host new-server \
  --hostname server.example.com \
  --user ec2-user \
  --port 2222 \
  --identity ~/.ssh/id_rsa \
  --tag "aws,production" \
  --description "Production web server"
```

### Example 3: Test multiple hosts

```bash
python3 scripts/main.py test --hosts work-server,staging,personal-vps
```

Output:
```
Testing SSH connections...
✅ work-server (192.168.1.100): Connected successfully
✅ staging (staging.example.com): Connected successfully
❌ personal-vps (45.33.22.11): Connection timeout
```

### Example 4: Generate config from template

```yaml
# servers.yaml
hosts:
  web-prod:
    hostname: web.example.com
    user: deploy
    port: 22
    identityfile: ~/.ssh/deploy_key
    tags: [web, production]
    
  db-backup:
    hostname: db-backup.internal
    user: backup
    port: 2222
    proxycommand: "ssh -W %h:%p bastion"
    tags: [database, backup]
```

```bash
python3 scripts/main.py generate --template servers.yaml --output ~/.ssh/config
```

## Requirements

- Python 3.x
- SSH client installed (`ssh` command available in PATH)
- Read/write access to `~/.ssh/config` (or specified config file)

## Limitations

- This is a CLI tool, not an auto-integration plugin
- Requires Python 3.x and SSH client to be installed
- SSH config syntax validation is basic (doesn't catch all edge cases)
- Connection testing requires SSH keys to be set up properly
- Does not manage SSH keys or certificates
- Limited to standard SSH config options
- Performance depends on number of hosts in config
- Network timeouts can affect connection testing
- Does not support all SSH config advanced features (Match blocks, etc.)
- Backup files use simple timestamp naming