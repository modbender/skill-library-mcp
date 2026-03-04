---
name: docker-container-cleaner
description: CLI tool to clean up stopped Docker containers, unused images, volumes, and networks to free up disk space.
version: 1.0.0
author: skill-factory
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - docker
---

# Docker Container Cleaner

## What This Does

A CLI tool that helps clean up Docker resources to free up disk space. It can:
- List and remove stopped containers
- Remove dangling images (images with no tag)
- Remove unused images (not used by any container)
- Remove unused volumes
- Remove unused networks
- Perform a "prune all" operation (Docker system prune)

The tool provides a safe, interactive mode by default, showing what will be removed and asking for confirmation before deleting anything.

## When To Use

- Your Docker disk usage is growing and you need to free up space
- You have many stopped containers that are no longer needed
- You have old, unused images taking up disk space
- You want to clean up Docker resources in a controlled, safe way
- You need to automate Docker cleanup in scripts or CI/CD pipelines

## Usage

Interactive cleanup (recommended for first use):
```bash
python3 scripts/main.py clean
```

Remove stopped containers only:
```bash
python3 scripts/main.py clean --containers
```

Remove dangling images only:
```bash
python3 scripts/main.py clean --images --dangling
```

Remove unused images (all images not used by containers):
```bash
python3 scripts/main.py clean --images --unused
```

Remove unused volumes:
```bash
python3 scripts/main.py clean --volumes
```

Remove unused networks:
```bash
python3 scripts/main.py clean --networks
```

Force cleanup (no confirmation):
```bash
python3 scripts/main.py clean --all --force
```

Dry run (show what would be removed):
```bash
python3 scripts/main.py clean --all --dry-run
```

## Examples

### Example 1: Interactive cleanup

```bash
python3 scripts/main.py clean
```

Output:
```
Docker Cleanup Tool
===================

Found resources:
- Stopped containers: 3 (using 1.2GB)
- Dangling images: 5 (using 850MB)
- Unused images: 2 (using 450MB)
- Unused volumes: 1 (using 100MB)
- Unused networks: 0

Total disk space that can be freed: 2.6GB

What would you like to clean up?
1. Remove stopped containers
2. Remove dangling images
3. Remove unused images
4. Remove unused volumes
5. Remove unused networks
6. All of the above
7. Cancel

Enter choice [1-7]: 2

About to remove 5 dangling images (850MB):
- python:3.9-alpine (dangling)
- node:16-slim (dangling)
- ...

Are you sure? (y/N): y
Removing images...
✅ Cleanup complete! Freed 850MB of disk space.
```

### Example 2: Script-friendly JSON output

```bash
python3 scripts/main.py status --format json
```

Output:
```json
{
  "containers": {
    "running": 2,
    "stopped": 3,
    "stopped_size_mb": 1200
  },
  "images": {
    "total": 15,
    "dangling": 5,
    "dangling_size_mb": 850,
    "unused": 2,
    "unused_size_mb": 450
  },
  "volumes": {
    "total": 4,
    "unused": 1,
    "unused_size_mb": 100
  },
  "networks": {
    "total": 3,
    "unused": 0
  },
  "total_reclaimable_mb": 2600
}
```

## Requirements

- Python 3.x
- **Docker**: Must be installed and the Docker daemon must be running
- **Docker CLI**: Must be available in PATH (`docker` command)
- **Docker SDK for Python**: Optional, but recommended for better performance

Install Docker SDK for Python (optional):
```bash
pip install docker
```

## Limitations

- This is a CLI tool, not an auto-integration plugin
- Requires Docker daemon to be running and accessible
- Some operations require elevated permissions (sudo)
- Cannot clean up resources in use by running containers
- Image size calculations are approximate
- Network and volume cleanup may fail if resources are in use
- Does not clean up Docker build cache (use `docker builder prune`)
- Does not clean up Docker Compose resources automatically
- Performance depends on number of Docker resources
- Large cleanup operations may take significant time