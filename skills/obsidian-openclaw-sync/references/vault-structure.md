# OpenClaw Vault Structure Reference

## Standard Vault Layout

```
.openclaw/
├── media/               # Shared media (images, files, etc.)
├── projects/             # Project management folder - all active projects
├── team/                 # Team folder - shared team configurations
├── skills/               # Global skills - reusable skill definitions
├── workspace_default/    # Default workspace
├── workspace_agent1/     # Agent-specific workspace 1
├── workspace_agent2/     # Agent-specific workspace 2
└── ...
```

## Directory Descriptions

| Directory | Description |
|-----------|-------------|
| `.openclaw/` | Core configuration directory |
| `media/` | Shared media: images, files, templates |
| `projects/` | Project management: all active projects organized here |
| `team/` | Team resources: shared configs, team docs, collaborations |
| `skills/` | Global skills: reusable Claude Code skill definitions |
| `workspace_*/` | Agent workspaces: per-agent context and settings |

## Configuration Files

### .openclaw/workspace-state.json

Tracks the current state of workspaces and agents.

## iCloud Sync Path

The Obsidian iCloud vault is located at:
- `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<vault-name>/`

**Note:** Obsidian uses `iCloud~md~obsidian` format, not `com~apple~CloudDocs`.
