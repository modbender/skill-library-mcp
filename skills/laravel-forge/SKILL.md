---
name: laravel-forge
description: Manage Laravel Forge servers, sites, deployments, databases, integrations, and more via the Forge API.
metadata:
  openclaw:
    requires:
      bins: [curl, jq]
      env: [LARAVEL_FORGE_API_TOKEN]
    credentials:
      primary:
        env: LARAVEL_FORGE_API_TOKEN
        file: ~/.openclaw/credentials/laravel-forge/config.json
        description: Laravel Forge API token + default org (generate at forge.laravel.com → Profile → API)
    scripts:
      laravel-forge:
        path: scripts/laravel-forge.sh
        description: Laravel Forge CLI wrapper
---

# Laravel Forge API Skill

Wraps the [Laravel Forge API](https://forge.laravel.com/docs/api-reference/introduction) in a single bash script. Organization-scoped, JSON:API format.

## Setup

**Option 1 — Environment variables:**
```bash
export LARAVEL_FORGE_API_TOKEN="your-token-here"
export LARAVEL_FORGE_ORG="your-default-org-slug"
```

**Option 2 — Credentials file (recommended):**
```bash
mkdir -p ~/.openclaw/credentials/laravel-forge
echo '{"token":"your-token-here","org":"your-default-org-slug"}' > ~/.openclaw/credentials/laravel-forge/config.json
```

Generate your token at: **forge.laravel.com → Profile → API**

The `org` field is optional — if omitted, the CLI auto-detects your first organization. Set it explicitly if you have multiple orgs or want to skip the extra API call. You can also override per-command with `--org`.

## Usage

```bash
laravel-forge <resource> <action> [args...] [--org ORG]
```

All commands support `--org ORG_SLUG` to override the default organization.

## Resources Overview

| Resource | Description |
|---|---|
| `user` | Current user info |
| `organizations` | List/get organizations |
| `providers` | Cloud provider info (regions, sizes) |
| `servers` | Server management (create, delete, events, archives) |
| `services` | Control services (nginx, mysql, postgres, redis, php, supervisor) |
| `php` | PHP version management & configuration (cli/fpm/pool configs, opcache) |
| `background-processes` | Background processes (supervisor daemons) |
| `firewall` | Firewall rules |
| `jobs` | Scheduled jobs (server-scoped and site-scoped) |
| `keys` | SSH keys |
| `databases` | Database schemas |
| `db-users` | Database users |
| `backups` | Backup configurations & instances |
| `monitors` | Server monitors (CPU, memory, disk) |
| `nginx-templates` | Nginx templates |
| `logs` | Server logs |
| `sites` | Site management |
| `domains` | Per-site domain management |
| `composer-credentials` | Per-site Composer credentials |
| `npm-credentials` | Per-site NPM credentials |
| `heartbeats` | Site heartbeats |
| `deployments` | Deployments & scripts |
| `webhooks` | Deployment webhooks |
| `commands` | Run commands on sites |
| `redirects` | Redirect rules |
| `security` | Security rules (HTTP basic auth) |
| `integrations` | Laravel integrations (Horizon, Octane, Reverb, Pulse, etc.) |
| `recipes` | Recipes & Forge recipes |
| `storage-providers` | Storage providers for backups |
| `teams` | Team management |
| `roles` | Role & permission management |
| `server-credentials` | Server credentials & VPCs |

## Quick Examples

### User & Organizations
```bash
laravel-forge user get
laravel-forge organizations list
laravel-forge organizations get --org my-org
```

### Servers
```bash
# List servers
laravel-forge servers list --org my-org

# Get server
laravel-forge servers get 12345 --org my-org

# Create server
laravel-forge servers create --org my-org \
  --name "Production API" \
  --provider digitalocean \
  --credential-id 1 \
  --type app \
  --ubuntu-version 22.04 \
  --php-version php82

# Server events
laravel-forge servers events 12345 --org my-org

# Archive/unarchive
laravel-forge servers archive 12345 --org my-org
laravel-forge servers unarchive 12345 --org my-org
```

### PHP Management
```bash
# List installed PHP versions
laravel-forge php versions 12345 --org my-org

# Install new PHP version
laravel-forge php install 12345 --version php83 --cli-default true

# Set CLI default
laravel-forge php update-cli-version 12345 --php-version php83

# Set site default
laravel-forge php update-site-version 12345 --php-version php82

# FPM config
laravel-forge php fpm-config 12345 php82
laravel-forge php update-fpm-config 12345 php82 --config "..."

# OPcache
laravel-forge php enable-opcache 12345
laravel-forge php disable-opcache 12345
```

### Sites
```bash
# List sites
laravel-forge sites list --org my-org
laravel-forge sites list 12345 --org my-org

# Create site
laravel-forge sites create 12345 --org my-org \
  --type php \
  --domain-mode single \
  --name example.com \
  --php-version php82 \
  --repository laravel/laravel \
  --branch main

# Update site
laravel-forge sites update 12345 67890 --php-version php83

# Environment
laravel-forge sites env 12345 67890
laravel-forge sites update-env 12345 67890 --environment "APP_ENV=production
APP_KEY=..."

# Nginx config
laravel-forge sites nginx 12345 67890
laravel-forge sites update-nginx 12345 67890 --config "..."

# Logs
laravel-forge sites log-nginx-access 12345 67890
laravel-forge sites log-nginx-error 12345 67890
laravel-forge sites log-application 12345 67890
```

### Domains
```bash
# List domains for a site
laravel-forge domains list 12345 67890 --org my-org

# Add domain
laravel-forge domains create 12345 67890 --org my-org \
  --name www.example.com \
  --allow-wildcards false \
  --www-redirect to-non-www

# Domain certificate
laravel-forge domains cert 12345 67890 1
laravel-forge domains create-cert 12345 67890 1 --type letsencrypt --letsencrypt true
laravel-forge domains cert-action 12345 67890 1 --action activate

# Domain Nginx config
laravel-forge domains nginx 12345 67890 1
laravel-forge domains update-nginx 12345 67890 1 --config "..."
```

### Deployments
```bash
# Deploy now
laravel-forge deployments deploy 12345 67890 --org my-org

# Deployment history
laravel-forge deployments list 12345 67890
laravel-forge deployments log 12345 67890 99

# Deployment script
laravel-forge deployments script 12345 67890
laravel-forge deployments update-script 12345 67890 --content "cd /home/forge/example.com
php artisan migrate --force"

# Push to deploy
laravel-forge deployments push-to-deploy 12345 67890
laravel-forge deployments delete-push-to-deploy 12345 67890
```

### Integrations
```bash
# Laravel Horizon
laravel-forge integrations horizon 12345 67890 get
laravel-forge integrations horizon 12345 67890 create
laravel-forge integrations horizon 12345 67890 delete

# Laravel Octane
laravel-forge integrations octane 12345 67890 create --port 8000 --server swoole

# Laravel Reverb
laravel-forge integrations reverb 12345 67890 create --host 0.0.0.0 --port 8080 --connections redis

# Laravel Pulse
laravel-forge integrations pulse 12345 67890 create

# Scheduler
laravel-forge integrations laravel-scheduler 12345 67890 create
```

### Commands
```bash
# Run command
laravel-forge commands run 12345 67890 --command "php artisan migrate --force"

# Get command output
laravel-forge commands list 12345 67890
laravel-forge commands output 12345 67890 42
```

### Databases
```bash
# List databases
laravel-forge databases list 12345 --org my-org

# Create database
laravel-forge databases create 12345 --name mydb --user myuser --password secret

# Sync databases
laravel-forge databases sync 12345

# Update root password
laravel-forge databases update-password 12345 --password newpass
```

### Backups
```bash
# List backup configs
laravel-forge backups configs 12345

# Create backup config
laravel-forge backups create-config 12345 \
  --storage-provider-id 1 \
  --frequency daily \
  --retention 14 \
  --database-ids "[1,2,3]"

# List backups
laravel-forge backups list 12345 1

# Create backup now
laravel-forge backups create 12345 1

# Restore backup
laravel-forge backups restore 12345 1 99 --database-id 1
```

### Firewall
```bash
laravel-forge firewall list 12345
laravel-forge firewall create 12345 --name "Allow HTTPS" --port 443 --type allow
laravel-forge firewall delete 12345 1
```

### Scheduled Jobs
```bash
# Server-scoped jobs
laravel-forge jobs list 12345
laravel-forge jobs create 12345 \
  --command "php /home/forge/app/artisan schedule:run" \
  --user forge \
  --frequency minutely

# Site-scoped jobs
laravel-forge jobs list 12345 67890
laravel-forge jobs create 12345 67890 \
  --command "php artisan custom:command" \
  --user forge \
  --frequency daily
```

### Recipes
```bash
# List org recipes
laravel-forge recipes list

# Create recipe
laravel-forge recipes create --name "Install Node" --user root --script "apt-get install nodejs"

# Run recipe
laravel-forge recipes run 1 --servers "[12345,67890]"

# Forge recipes (official)
laravel-forge recipes forge-recipes
laravel-forge recipes run-forge-recipe 1 --servers "[12345]"
```

### Teams
```bash
# List teams
laravel-forge teams list

# Create team
laravel-forge teams create --name "Development Team"

# Add members
laravel-forge teams members 1
laravel-forge teams invite 1 --role-id 2 --email dev@example.com
```

### Storage Providers
```bash
laravel-forge storage-providers list
laravel-forge storage-providers create \
  --name "S3 Backups" \
  --provider s3 \
  --bucket my-backups \
  --access-key KEY \
  --secret-key SECRET
```

### Services
```bash
# Control services
laravel-forge services nginx 12345 --action restart
laravel-forge services mysql 12345 --action stop
laravel-forge services php 12345 --action restart --version php82
```

### Help
```bash
# Main help
laravel-forge help

# Resource help
laravel-forge servers help
laravel-forge deployments help
laravel-forge integrations help
```

## Resource Hierarchy

**Top-level** (no org/server required):
- `user`
- `providers`

**Org-scoped:**
- `organizations`
- `recipes`
- `storage-providers`
- `teams`
- `roles`
- `server-credentials`

**Server-scoped:**
- `servers`, `services`, `php`, `background-processes`, `firewall`, `jobs` (server), `keys`, `databases`, `db-users`, `backups`, `monitors`, `nginx-templates`, `logs`

**Site-scoped:**
- `sites`, `domains`, `composer-credentials`, `npm-credentials`, `heartbeats`, `deployments`, `webhooks`, `commands`, `redirects`, `security`, `integrations`, `jobs` (site)

## Dependencies

- `curl` — HTTP requests
- `jq` — JSON parsing

## Notes

- All paths are **org-scoped** (except user, providers, predefined roles/permissions)
- Service actions use POST with `{"action":"..."}` body
- Domain certificates are now **per-domain**, not per-site
- PHP management is significantly expanded (cli/fpm/pool configs, version defaults)
- Integrations cover all major Laravel first-party packages
- Teams and roles provide fine-grained access control
