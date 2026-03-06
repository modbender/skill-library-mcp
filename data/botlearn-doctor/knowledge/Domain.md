---
domain: openclaw-doctor
topic: openclaw-architecture
priority: high
ttl: 30d
---

# OpenClaw Domain Knowledge

## OpenClaw Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Agent                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Skills     │  │   Memory     │  │   Plugins    │      │
│  │   System     │  │   System     │  │   System     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │  Execution  │                          │
│                    │   Engine    │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │     API     │                          │
│                    │   Layer     │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
         │                        │
    ┌────▼────┐            ┌─────▼──────┐
    │ clawhub │            │   npm      │
    │   CLI   │            │ registry   │
    └─────────┘            └────────────┘
```

## Core Components

### 1. Skills System
- **Purpose**: Extensible capabilities through installable skill packages
- **Registry**: npm registry (@botlearn/* packages)
- **Installation**: `clawhub install @botlearn/<skill-name>`
- **Activation**: Trigger-based or explicit
- **Dependencies**: Skills can depend on other skills

### 2. Memory System
- **Purpose**: Persistent knowledge storage for agent
- **Injection**: Skills inject knowledge documents via `POST /memory/inject`
- **Structure**: Domain → Topic → Priority → TTL
- **Retrieval**: Contextual memory lookup during execution

### 3. Plugins System
- **Purpose**: External integrations (APIs, databases, services)
- **Interface**: Standard plugin contract
- **Lifecycle**: Load → Initialize → Execute → Cleanup

### 4. Execution Engine
- **Purpose**: Orchestrates skill execution
- **Features**: Parallel execution, dependency resolution, error handling
- **Concurrency**: Configurable worker pool

### 5. API Layer
- **Purpose**: REST API for external communication
- **Endpoints**:
  - `POST /memory/inject` - Inject knowledge
  - `POST /skills/register` - Register skill
  - `POST /benchmark/run` - Run benchmark
  - `GET /health` - Health check

## Configuration Files

### OpenClaw Config (`openclaw.config.json`)

```json
{
  "version": "1.0.0",
  "environment": {
    "nodeVersion": ">=18.0.0",
    "memory": {
      "min": "512MB",
      "recommended": "2GB"
    }
  },
  "execution": {
    "concurrency": 10,
    "timeout": 30000,
    "retryAttempts": 3
  },
  "skills": {
    "registry": "https://registry.npmjs.org",
    "autoUpdate": false,
    "dependencies": {
      "autoInstall": true
    }
  },
  "memory": {
    "maxSize": "1GB",
    "defaultTTL": "30d"
  },
  "logging": {
    "level": "info",
    "format": "json",
    "outputs": ["console", "file"]
  }
}
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENCLAW_HOME` | Installation directory | `~/.openclaw` |
| `OPENCLAW_CONFIG` | Config file path | `$OPENCLAW_HOME/config.json` |
| `OPENCLAW_LOG_DIR` | Log directory | `$OPENCLAW_HOME/logs` |
| `OPENCLAW_DATA_DIR` | Data directory | `$OPENCLAW_HOME/data` |
| `OPENCLAW_SKILLS_DIR` | Skills directory | `$OPENCLAW_HOME/skills` |
| `NODE_ENV` | Environment | `production` |
| `NPM_REGISTRY` | npm registry | `https://registry.npmjs.org` |

## Log Data Structure

### Log Location
- **Path**: `$OPENCLAW_LOG_DIR/`
- **Files**: `openclaw.log`, `error.log`, `debug.log`

### Log Format (JSON)

```json
{
  "timestamp": "2026-03-02T10:30:00.000Z",
  "level": "error",
  "component": "skills",
  "message": "Skill execution failed",
  "skill": "@botlearn/code-gen",
  "error": {
    "code": "SKILL_TIMEOUT",
    "message": "Execution exceeded 30000ms timeout"
  },
  "context": {
    "sessionId": "sess_abc123",
    "userId": "user_456"
  }
}
```

## Session Data

### Session Structure

```typescript
interface Session {
  id: string;
  userId: string;
  startTime: number;
  lastActivity: number;
  status: "active" | "idle" | "closed";
  skillsUsed: string[];
  memoryWrites: number;
  requests: number;
  errors: number;
}
```

## Workspace Structure

```
~/.openclaw/
├── config/
│   ├── openclaw.config.json
│   ├── skills.json
│   └── plugins.json
├── skills/              # Installed skills
│   ├── @botlearn/
│   │   ├── google-search/
│   │   ├── code-gen/
│   │   └── ...
│   └── .registry-cache/
├── plugins/             # Installed plugins
├── memory/              # Injected knowledge
│   ├── @botlearn/
│   │   └── google-search/
│   │       └── knowledge/
│   └── ...
├── logs/
│   ├── openclaw.log
│   ├── error.log
│   └── debug.log
├── data/
│   ├── sessions/
│   └── cache/
└── workspace/           # User workspace
    ├── *.md             # User documents
    └── projects/
```

## Health Check Indicators

### Environment Health
- Node.js version compatibility
- Memory availability
- Disk space
- CPU capacity

### Configuration Health
- Valid JSON syntax
- Required fields present
- Values within acceptable ranges
- No conflicting settings

### Skills Health
- Installed skills count
- Outdated skills
- Missing dependencies
- Orphaned skills
- Load failures

### Logs Health
- Error rate (errors/total requests)
- Warning frequency
- Recent critical errors
- Log rotation status

### Workspace Health
- Orphaned files
- Large files (>10MB)
- Deprecated file formats
- Broken references
