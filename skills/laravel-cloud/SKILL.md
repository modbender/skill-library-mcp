---
name: laravel-cloud
description: Manage Laravel Cloud infrastructure via API — apps, environments, deployments, databases, caches, domains, scaling, commands, storage, and WebSockets.
metadata:
  openclaw:
    requires:
      bins: [curl, jq]
      env: [LARAVEL_CLOUD_API_TOKEN]
    credentials:
      primary:
        env: LARAVEL_CLOUD_API_TOKEN
        file: ~/.openclaw/credentials/laravel-cloud/config.json
        description: Laravel Cloud API token (generate at cloud.laravel.com → Settings → API Tokens)
    scripts:
      laravel-cloud:
        path: scripts/laravel-cloud.sh
        description: Laravel Cloud CLI wrapper
---

# Laravel Cloud API Skill

Wraps the entire [Laravel Cloud REST API](https://cloud.laravel.com/docs) in a single bash script.

## Setup

**Option 1 — Environment variable (preferred):**
```bash
export LARAVEL_CLOUD_API_TOKEN="your-token-here"
```

**Option 2 — Credentials file:**
```bash
mkdir -p ~/.openclaw/credentials/laravel-cloud
echo '{"token":"your-token-here"}' > ~/.openclaw/credentials/laravel-cloud/config.json
```

Generate your token at: **cloud.laravel.com → Settings → API Tokens**

## Usage

```bash
laravel-cloud <resource> <action> [args...]
```

## Quick Reference

| Resource | Actions |
|---|---|
| `apps` | list, get, create, update, delete |
| `envs` | list, get, create, update, delete, start, stop, metrics, logs, vars-add, vars-replace |
| `commands` | list, get, run |
| `deployments` | list, get, initiate |
| `domains` | list, get, create, update, delete, verify |
| `instances` | list, get, sizes, create, update, delete |
| `bg-processes` | list, get, create, update, delete |
| `databases` | clusters, cluster, cluster-create, cluster-update, cluster-delete, cluster-metrics, types, list, get, create, delete, snapshots, snapshot, snapshot-create, snapshot-delete, restore, dedicated |
| `caches` | list, get, types, create, update, delete, metrics |
| `buckets` | list, get, create, update, delete |
| `bucket-keys` | list, get, create, update, delete |
| `websockets` | list, get, create, update, delete, metrics |
| `ws-apps` | list, get, create, update, delete, metrics |
| `ips` | list |
| `org` | get |
| `regions` | list |

## Common Examples

```bash
# List all applications
laravel-cloud apps list

# Create an application (requires --repository)
laravel-cloud apps create --name "my-app" --region us-east-1 --repository owner/repo

# List environments for an app
laravel-cloud envs list <app-id>

# Create an environment
laravel-cloud envs create <app-id> --name "Production" --branch main

# Start / stop an environment
laravel-cloud envs start <env-id>
laravel-cloud envs stop <env-id>

# View environment metrics and logs
laravel-cloud envs metrics <env-id> --period 24h
laravel-cloud envs logs <env-id>

# Set environment variables
laravel-cloud envs vars-add <env-id> --vars 'APP_KEY=base64:...,DB_HOST=localhost'
laravel-cloud envs vars-replace <env-id> --vars 'KEY1=val1,KEY2=val2'

# Trigger a deployment
laravel-cloud deployments initiate <env-id>

# Run an Artisan command
laravel-cloud commands run <env-id> --command "php artisan migrate --force"

# Get organization and regions
laravel-cloud org get
laravel-cloud regions list

# Manage databases
# NOTE: Creating a cluster auto-creates a "main" database (schema).
# Use that default — don't create an extra one. Wire the "main" schema
# to your environment via: envs update <env-id> --database-schema-id <main-schema-id>
# To find the schema ID: databases cluster <cluster-id> (with ?include=schemas)
laravel-cloud databases clusters
# DB types: laravel_mysql_84, laravel_mysql_8, neon_serverless_postgres_16/17/18, aws_rds_mysql_8, aws_rds_postgres_18
laravel-cloud databases cluster-create --name my-db --type laravel_mysql_84 --region us-east-1 --size db-flex.m-1vcpu-512mb --storage 5

# Manage caches
laravel-cloud caches list
# Cache types: upstash_redis (sizes: 250mb, 1gb, ...) or laravel_valkey (sizes: valkey-pro.250mb, ...)
laravel-cloud caches create --name my-cache --type laravel_valkey --region us-east-1 --size valkey-pro.250mb

# Object storage
laravel-cloud buckets list
laravel-cloud buckets create --name my-bucket --region us-east-1

# WebSocket clusters
laravel-cloud websockets list
laravel-cloud ws-apps list <ws-cluster-id>

# Per-resource help
laravel-cloud help
laravel-cloud envs help
laravel-cloud databases help
```

## Dependencies

- `curl` — HTTP requests
- `jq` — JSON parsing and pretty-printing

