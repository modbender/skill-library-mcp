---
name: memory-cache
description: "High-performance temporary storage system using Redis. Supports
  namespaced keys (mema:*), TTL management, and session context caching. Use
  for: (1) Saving agent state, (2) Caching API results, (3) Sharing data between
  sub-agents."
---


# Memory Cache

Standardized Redis-backed caching system for OpenClaw agents.

## Prerequisites
- **Binary**: `python3` must be available on the host.
- **Credentials**: `REDIS_URL` environment variable (e.g., `redis://localhost:6379/0`).

## Setup
1. Copy `env.example.txt` to `.env`.
2. Configure your connection in `.env`.
3. Dependencies are listed in `requirements.txt`.

## Core Workflows

### 1. Store and Retrieve
- **Store**: `python3 $WORKSPACE/skills/memory-cache/scripts/cache_manager.py set mema:cache:<name> <value> [--ttl 3600]`
- **Fetch**: `python3 $WORKSPACE/skills/memory-cache/scripts/cache_manager.py get mema:cache:<name>`

### 2. Search & Maintenance
- **Scan**: `python3 $WORKSPACE/skills/memory-cache/scripts/cache_manager.py scan [pattern]`
- **Ping**: `python3 $WORKSPACE/skills/memory-cache/scripts/cache_manager.py ping`

## Key Naming Convention
Strictly enforce the `mema:` prefix:
- `mema:context:*` – Session state.
- `mema:cache:*` – Volatile data.
- `mema:state:*` – Persistent state.
