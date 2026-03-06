# Janitor Skill v1.1.0 - ClawHub.ai

Lightweight cleanup skill for AI agents with **automatic session management**. Removes cache files, logs, temporary files, and intelligently manages OpenClaw context to prevent token limit errors.

## ⚠️ Security Notice

**This is a high-privilege skill** that requires file deletion, process execution, and optional network access. Before installation:
1. **Read [SECURITY.md](SECURITY.md)** for complete security guidelines
2. Understand the risks and mitigations
3. Only install if you trust this skill

Key safety features: Protected files, path validation, command injection prevention, archives before deletion, dry-run mode.

## New in v1.1.0: Session Management

Never hit OpenClaw's 200k token context limit again! Janitor now automatically:
- Monitors context usage in real-time
- Archives and prunes old sessions
- Prevents context overflow errors
- Runs cleanup in the background
- Keeps your important conversations safe

## Quick Start

### Basic Cleanup

```javascript
const Janitor = require('./janitor');

const janitor = new Janitor();

// Run cleanup
const result = await janitor.cleanup();
console.log(result);
// { filesDeleted: 42, spaceSaved: "1.2 MB", duration: "150ms", memoryFreed: true }

// Get stats
const stats = janitor.getStats();
console.log(stats);

// Get report
await janitor.report();
```

### Session Management

```javascript
// View context usage dashboard
await janitor.showDashboard();

// Clean old sessions
await janitor.cleanContext('moderate');

// Emergency cleanup (keeps only last 6 hours)
await janitor.emergencyClean();

// Start background monitoring (runs every 5 minutes)
janitor.startMonitoring();

// List all sessions
await janitor.listSessions('age');

// View archives
await janitor.listArchives();
```

## What Gets Cleaned?

- `node_modules/.cache/**` - Node module caches
- `.cache/` - Cache directories
- `dist/`, `coverage/`, `tmp/` - Build artifacts and temp files
- `.DS_Store` - macOS metadata files
- `*.log` files older than 7 days

## Protected Files

These are NEVER deleted:
- `package.json`, `README.md`, `.env`
- `src/**` - Source files
- `.git/**` - Git repository
- `node_modules/**` - Dependencies (except `.cache`)

## Session Management Features

### Real-Time Context Monitoring
- Tracks OpenClaw's active context token usage
- Monitors per-session token counts
- Alerts when approaching limits (default: 80% of 200k tokens)
- Logs context usage trends

### Intelligent Session Pruning
Multi-tier pruning strategy:

**Tier 1: Conservative** - Age-based removal
- Deletes sessions older than 7 days (configurable)
- Exception: Keeps sessions marked as important

**Tier 2: Moderate** - Token-based cleanup
- 80% usage → Remove oldest 25% of sessions
- 90% usage → Remove oldest 50% of sessions

**Tier 3: Aggressive** - Emergency cleanup
- 95%+ usage → Keep only last 6 hours
- Archives everything before deletion

### Smart Session Preservation
Sessions are preserved based on:
1. **Recency** - Sessions from last 24 hours always kept
2. **Engagement** - Sessions with >10 messages preserved
3. **Activity** - Sessions with tool usage kept longer

### Session Archiving
- All pruned sessions are archived before deletion
- Compressed to `.tar.gz` for storage efficiency
- Archives kept for 30 days (configurable)
- Easy restoration via CLI

### Background Monitoring Service
- Runs every 5 minutes (configurable)
- Auto-cleanup when threshold exceeded
- Zero manual intervention required
- Continues monitoring in background

### Emergency Recovery
Automatic emergency cleanup when context usage exceeds 95%:
1. Stop OpenClaw gateway
2. Archive all current sessions
3. Delete all except last 6 hours
4. Restart gateway
5. Send notification

## Features

- 🧹 **Core Cleanup** - Cache, logs, temp files
- 🗑️ **Memory Optimization** - Garbage collection
- 📊 **Statistics** - Track cleanups and space saved
- 🛡️ **Safe** - Protected file patterns
- 🚀 **Minimal Dependencies** - Only Node.js built-ins
- 🔍 **Context Monitoring** - Real-time token usage tracking
- 🤖 **Auto-Cleanup** - Background session management
- 📦 **Session Archiving** - Safe backup before deletion
- 🚨 **Emergency Recovery** - Automatic critical cleanup
- 📈 **Dashboard** - Beautiful CLI visualization

## Differences from Full Version

This is a **lightweight version** for ClawHub.ai with only core cleanup features.

**Missing features** (available in full version):
- ⏰ Automated scheduling/cron
- 💾 GitHub backups
- 🔄 Auto-cleanup after git push
- 📈 Advanced reporting
- ⚙️ Complex configuration

## Full Version

For advanced features, visit the main repository:

**https://github.com/openclaw/janitor**

The full version includes:
- Automated backup to GitHub
- Cron scheduling
- Session management
- Log rotation
- Storage monitoring
- And more...

## Usage in ClawHub.ai

Install as a skill:

```bash
# In your ClawHub.ai skills directory
cd skills/
git clone https://github.com/openclaw/janitor
cd janitor/skill
```

Use in your agent:

```javascript
const Janitor = require('./skills/janitor/skill/janitor');

const janitor = new Janitor();
await janitor.cleanup();
```

## CLI Commands

### Basic Commands
```bash
# Run cleanup
node index.js clean

# Show statistics
node index.js stats

# Generate report
node index.js report
```

### Session Management Commands
```bash
# Show context dashboard
node index.js context
node index.js dashboard

# Show compact status
node index.js context status

# Clean sessions (strategies: conservative, moderate, aggressive)
node index.js context clean moderate

# Emergency cleanup
node index.js context emergency

# List sessions (sort by: size, age, messages)
node index.js sessions
node index.js sessions age

# Start background monitoring
node index.js monitor start

# Stop monitoring
node index.js monitor stop

# Monitoring status
node index.js monitor status

# List archives
node index.js archives

# Restore archive
node index.js archives restore sessions-2026-02-08.tar.gz

# Cleanup old archives
node index.js archives cleanup

# Archive statistics
node index.js archives stats
```

## API Reference

### Basic Cleanup Methods

#### `cleanup(workingDir?: string): Promise<object>`
Run full cleanup operation.

Returns:
```javascript
{
  filesDeleted: number,
  spaceSaved: string,
  duration: string,
  memoryFreed: boolean
}
```

#### `getStats(): object`
Get cleanup statistics.

#### `report(): Promise<object>`
Generate cleanup report.

### Session Management Methods

#### `getContextUsage(): Promise<object>`
Get current context usage across all sessions.

Returns:
```javascript
{
  currentTokens: number,
  maxTokens: number,
  utilizationPercent: number,
  sessions: Array<SessionInfo>,
  lastChecked: Date,
  status: { level, emoji, message }
}
```

#### `showDashboard(): Promise<void>`
Display full context usage dashboard.

#### `showContextStatus(): Promise<void>`
Display compact context status.

#### `cleanContext(strategy?: string): Promise<object>`
Clean context/sessions using specified strategy.

Strategies: `'conservative'`, `'moderate'`, `'aggressive'`

Returns:
```javascript
{
  before: object,
  after: object,
  pruned: number,
  tokensFreed: number
}
```

#### `emergencyClean(): Promise<object>`
Execute emergency cleanup (keeps only last 6 hours).

Returns detailed cleanup report.

#### `startMonitoring(): void`
Start background context monitoring service.

#### `stopMonitoring(): void`
Stop background monitoring service.

#### `getMonitoringStatus(): object`
Get current monitoring status.

#### `listSessions(sortBy?: string): Promise<Array>`
List all sessions.

Sort options: `'size'`, `'age'`, `'messages'`

#### `listArchives(): Promise<Array>`
List all session archives.

#### `restoreArchive(archiveName: string): Promise<object>`
Restore archived sessions.

#### `cleanupArchives(): Promise<object>`
Delete old archives (older than retention period).

#### `getArchiveStats(): Promise<object>`
Get archive statistics.

## Configuration

```javascript
const janitor = new Janitor({
  sessionManagement: {
    enabled: true,
    monitoring: {
      intervalMinutes: 5,
      alertThreshold: 80,      // Alert at 80% usage
      emergencyThreshold: 95   // Emergency at 95% usage
    },
    pruning: {
      maxSessionAge: 7,        // Delete sessions older than 7 days
      maxContextTokens: 160000,
      keepRecentHours: 24,     // Always keep last 24 hours
      keepMinimumSessions: 5   // Never go below 5 sessions
    },
    archiving: {
      enabled: true,
      retentionDays: 30,       // Keep archives for 30 days
      compression: true         // Compress archives
    },
    preservation: {
      pinned: true,
      highEngagement: true,    // Keep sessions with many messages
      minMessagesForImportant: 10
    }
  }
});
```

## Use Cases

### Raspberry Pi / Resource-Constrained Devices
Use aggressive settings to minimize memory usage:

```javascript
const janitor = new Janitor({
  sessionManagement: {
    monitoring: {
      intervalMinutes: 5,
      alertThreshold: 70,
      emergencyThreshold: 85
    },
    pruning: {
      maxSessionAge: 3,
      keepRecentHours: 12
    }
  }
});

janitor.startMonitoring();
```

### Desktop / High-Resource Systems
Use conservative settings to keep more history:

```javascript
const janitor = new Janitor({
  sessionManagement: {
    monitoring: {
      intervalMinutes: 15,
      alertThreshold: 85,
      emergencyThreshold: 95
    },
    pruning: {
      maxSessionAge: 14,
      keepRecentHours: 48
    }
  }
});
```

### Manual Control Only
Disable auto-cleanup, run manually when needed:

```javascript
const janitor = new Janitor({
  sessionManagement: {
    enabled: true,
    monitoring: {
      intervalMinutes: 5,
      alertThreshold: 90  // Only alert, don't auto-cleanup
    }
  }
});

// Check manually
await janitor.showDashboard();

// Clean when you want
await janitor.cleanContext('moderate');
```

## Troubleshooting

### Context Limit Errors
If you're getting `LLM request rejected: input length and max_tokens exceed context limit`:

```bash
# Check current usage
node index.js context status

# Run emergency cleanup
node index.js context emergency

# Start monitoring to prevent future issues
node index.js monitor start
```

### Restore Deleted Sessions
All pruned sessions are archived:

```bash
# List available archives
node index.js archives

# Restore specific archive
node index.js archives restore sessions-2026-02-08.tar.gz
```

### Disable Session Management
```javascript
const janitor = new Janitor({
  sessionManagement: {
    enabled: false
  }
});
```

## Systemd Service (Linux)

For automatic monitoring on Linux systems:

```bash
# Install service
sudo cp systemd/janitor-monitor.service.template /etc/systemd/system/janitor-monitor@.service
sudo systemctl daemon-reload
sudo systemctl enable janitor-monitor@$USER
sudo systemctl start janitor-monitor@$USER

# Check status
sudo systemctl status janitor-monitor@$USER

# View logs
sudo journalctl -u janitor-monitor@$USER -f
```

See `systemd/README.md` for complete installation instructions.

## Environment Variables

The following environment variables can be configured:

```bash
# Notification settings
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"
export DISCORD_WEBHOOK_URL="your-webhook-url"

# GitHub backup
export GITHUB_BACKUP_REPO="https://github.com/user/backups.git"

# OpenClaw home
export OPENCLAW_HOME="$HOME/.openclaw"
```

## Running Tests

```bash
node tests/run-tests.js
```

All tests should pass. If any fail, check the error messages and ensure all dependencies are properly installed.

## License

MIT

---

**Janitor v1.1.0** - Part of OpenClaw AI Agent Framework

**Full Feature Complete** - All PRD features implemented ✅
