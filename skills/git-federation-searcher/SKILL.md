---
name: git-federation-searcher
description: Search across multiple self-hosted Git instances including Gitea, Forgejo, GitLab, and Codeberg. Aggregates search results from Codeberg.org, Gitea.com, OpenDev, NotABug, and Gitdab. Supports API-based search with fallback to web search via SearXNG. Allows adding custom private instances with API token support.
---

# Git Federation Searcher

Search across multiple self-hosted Git instances in parallel.

## Overview

This tool searches across various Git hosting platforms (not just GitHub/GitLab) including:
- Codeberg
- Gitea.com
- NotABug
- Gitdab
- Self-hosted instances

## Features

- **Multi-Instance Search**: Search 5+ instances at once
- **Auto-Discovery**: Detects if instances are reachable
- **Add Custom Instances**: Add your own Gitea/GitLab instances
- **Fallback to Web**: Uses SearXNG if API search fails
- **Type Detection**: Auto-detects Gitea vs GitLab vs Forgejo
- **Results by Stars**: Sorted by popularity

## Default Instances

| Instance | Type | URL |
|----------|------|-----|
| Codeberg | Gitea | https://codeberg.org |
| Gitea.com | Gitea | https://gitea.com |
| OpenDev | Gitea | https://opendev.org |
| NotABug | Gogs | https://notabug.org |
| Gitdab | Forgejo | https://gitdab.com |

## Usage

### Command Line

```bash
# Search all instances
python3 git_federation_searcher.py "whisper"

# List configured instances
python3 git_federation_searcher.py --list

# Add custom instance
python3 git_federation_searcher.py --add MyGitea https://git.example.com gitea

# Remove instance
python3 git_federation_searcher.py --remove MyGitea
```

### Telegram Bot

```
/gitsearch whisper              # Search all instances
/gitinstances                   # List all configured
/gitadd Name URL Type           # Add custom instance
```

## Supported Git Types

| Type | API | Notes |
|------|-----|-------|
| Gitea | ✅ Full | Best support |
| Forgejo | ✅ Full | Gitea fork, same API |
| GitLab | ✅ Full | Uses v4 API |
| Gogs | ✅ Partial | Basic search only |

## Requirements

- Python 3.7+
- curl (for API calls)
- (Optional) SearXNG for web fallback
