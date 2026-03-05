# Janitor - AI Agent Cleanup & Session Management Skill

## Overview

**Janitor** is an intelligent cleanup and session management skill for OpenClaw AI agents. It automatically manages cache, optimizes memory usage, and **prevents context overflow** by monitoring token usage and intelligently pruning old sessions.

Think of Janitor as your **AI Agent's Intelligent Maintenance Crew** that:
- 🧹 Cleans cache files to optimize token usage
- 🗑️ Frees up unused memory and RAM
- 🔍 **Monitors context usage in real-time (NEW!)**
- 🤖 **Automatically prunes old sessions (NEW!)**
- 📦 **Archives sessions before deletion (NEW!)**
- 🚨 **Emergency recovery at 95% context usage (NEW!)**
- 📊 Reports cleanup statistics back to the agent
- 🔔 **Multi-channel notifications (NEW!)**

## Quick Start

### Installation

```bash
cd /Users/sarthiborkar/Desktop/butler-main/janitor
npm install  # No dependencies needed!
```

### Basic Usage

```javascript
const Janitor = require('./src/Janitor');

// Create janitor instance
const janitor = new Janitor();

// Run cleanup
const result = await janitor.cleanup();
console.log(result);
// {
//   filesDeleted: 42,
//   spaceSaved: "1.2 MB",
//   duration: "150ms",
//   memoryFreed: true
// }

// Get report
const report = await janitor.report();
```

## Features

### 1. Cache Cleanup

Automatically cleans cache files that consume disk space and slow down operations:

```javascript
const janitor = new Janitor();

// Clean cache files
await janitor.cleanup();
```

**Cleaned Items:**
- `node_modules/.cache/**` - Node module caches
- `**/*.cache` - Generic cache files
- `.DS_Store` - macOS metadata files
- `dist/**/*.map` - Source map files
- `coverage/**` - Test coverage reports
- `tmp/**` - Temporary files
- `**/*.log` - Old log files (>7 days)

### 2. Memory Optimization

Frees up unused memory to optimize token usage:

```javascript
const janitor = new Janitor();

// Free memory
janitor.freeMemory();

// Check memory usage
const memoryStats = janitor.getMemoryUsage();
console.log(memoryStats);
// {
//   rss: "45.2 MB",
//   heapTotal: "12.8 MB",
//   heapUsed: "8.4 MB",
//   external: "1.2 MB"
// }
```

**Memory Operations:**
- Triggers garbage collection (if enabled)
- Clears Node.js require cache
- Reports memory usage statistics

### 3. Unused File Cleanup

Removes files not accessed for a configurable period:

```javascript
const janitor = new Janitor({
  unusedFileAgeDays: 7  // Delete files not accessed in 7 days
});

await janitor.cleanup();
```

**Safety Features:**
- Never deletes important files (package.json, README.md, src/, .git/, etc.)
- Configurable age threshold
- Reports files before deletion

### 4. Post-Push Cleanup

Automatically clean up after GitHub push:

```javascript
const janitor = new Janitor({
  autoCleanAfterPush: true
});

// After git push
await janitor.cleanupAfterPush();
```

**Use Case:**
After pushing code to GitHub, temporary build artifacts, cache files, and coverage reports are no longer needed locally.

### 5. Reporting & Statistics

Get detailed cleanup statistics:

```javascript
const janitor = new Janitor();

// Run some cleanups
await janitor.cleanup();
await janitor.cleanup();

// Get stats
const stats = janitor.getStats();
console.log(stats);
// {
//   totalCleanups: 2,
//   totalFilesDeleted: 84,
//   totalSpaceSaved: "2.4 MB",
//   memoryUsage: { ... }
// }

// Get full report with recommendations
const report = await janitor.report();
console.log(report);
// {
//   timestamp: "2026-02-07T...",
//   status: "healthy",
//   stats: { ... },
//   recommendations: [
//     "Regular cleanup recommended."
//   ]
// }
```

## Configuration

### Default Configuration

```javascript
{
  enabled: true,
  autoCleanAfterPush: true,
  unusedFileAgeDays: 7,
  cachePatterns: [
    '**/*.cache',
    '**/node_modules/.cache/**',
    '**/.DS_Store',
    '**/dist/**/*.map',
    '**/tmp/**',
    '**/*.log',
    '**/coverage/**'
  ]
}
```

### Custom Configuration

```javascript
const janitor = new Janitor({
  enabled: true,
  autoCleanAfterPush: false,  // Disable auto-cleanup after push
  unusedFileAgeDays: 14,       // Keep files for 2 weeks
  cachePatterns: [
    '**/*.cache',
    '**/my-custom-cache/**'
  ]
});
```

## Integration with Butler

### Method 1: Direct Integration

```javascript
const Butler = require('../src/Butler');
const Janitor = require('../janitor/src/Janitor');

const butler = new Butler();
const janitor = new Janitor();

// Spawn agent and cleanup after
async function runTaskWithCleanup() {
  const results = await butler.spawnAgent(
    'DataAnalysis',
    'Analyze data and generate report',
    200000
  );

  // Cleanup after task
  const cleanupResult = await janitor.cleanup();
  console.log('Cleanup:', cleanupResult);

  return results;
}

runTaskWithCleanup();
```

### Method 2: Auto-Cleanup Hook

```javascript
const Butler = require('../src/Butler');
const Janitor = require('../janitor/src/Janitor');

class ButlerWithJanitor extends Butler {
  constructor() {
    super();
    this.janitor = new Janitor({ autoCleanAfterPush: true });
  }

  async spawnAgent(...args) {
    const result = await super.spawnAgent(...args);

    // Auto-cleanup after agent completes
    await this.janitor.cleanup();

    return result;
  }
}

const butler = new ButlerWithJanitor();
```

## Examples

### Example 1: Basic Cleanup

```javascript
const Janitor = require('./src/Janitor');

async function basicCleanup() {
  const janitor = new Janitor();

  console.log('Starting cleanup...');
  const result = await janitor.cleanup();

  console.log(`✅ Deleted ${result.filesDeleted} files`);
  console.log(`✅ Saved ${result.spaceSaved}`);
}

basicCleanup();
```

### Example 2: Scheduled Cleanup

```javascript
const Janitor = require('./src/Janitor');

const janitor = new Janitor();

// Run cleanup every hour
setInterval(async () => {
  console.log('🧹 Running scheduled cleanup...');
  const result = await janitor.cleanup();
  console.log(`Cleaned: ${result.spaceSaved}`);
}, 60 * 60 * 1000); // 1 hour
```

### Example 3: Git Hook Integration

Create `.git/hooks/post-commit`:

```bash
#!/bin/sh
node janitor/src/index.js cleanup --after-push
```

### Example 4: Monitoring & Alerts

```javascript
const Janitor = require('./src/Janitor');

const janitor = new Janitor();

async function monitor() {
  const report = await janitor.report();

  if (report.recommendations.length > 0) {
    console.log('⚠️  Recommendations:');
    report.recommendations.forEach(r => console.log(`   - ${r}`));
  }

  // Send to monitoring system
  sendToMonitoring(report);
}

setInterval(monitor, 5 * 60 * 1000); // Every 5 minutes
```

## CLI Usage

Create `src/index.js`:

```javascript
#!/usr/bin/env node
const Janitor = require('./Janitor');

const janitor = new Janitor();

const args = process.argv.slice(2);
const command = args[0];

(async () => {
  switch (command) {
    case 'cleanup':
      const result = await janitor.cleanup();
      console.log('Result:', result);
      break;

    case 'report':
      const report = await janitor.report();
      console.log(JSON.stringify(report, null, 2));
      break;

    case 'stats':
      const stats = janitor.getStats();
      console.log(stats);
      break;

    default:
      console.log('Usage: node index.js [cleanup|report|stats]');
  }
})();
```

Then use:

```bash
node janitor/src/index.js cleanup
node janitor/src/index.js report
node janitor/src/index.js stats
```

## API Reference

### Constructor

```javascript
new Janitor(config?: object)
```

### Methods

#### `cleanup(workingDir?: string): Promise<CleanupResult>`

Run full cleanup operation.

**Returns:**
```javascript
{
  filesDeleted: number,
  spaceSaved: string,
  duration: string,
  memoryFreed: boolean
}
```

#### `cleanupAfterPush(): Promise<CleanupResult | null>`

Auto-cleanup after git push (if enabled).

#### `freeMemory(): void`

Free up memory by triggering garbage collection and clearing caches.

#### `getStats(): object`

Get cleanup statistics.

#### `report(): Promise<Report>`

Generate comprehensive report with recommendations.

#### `getMemoryUsage(): object`

Get current memory usage statistics.

## Best Practices

### 1. Regular Cleanup

Run cleanup regularly to prevent cache buildup:

```javascript
// Every hour
setInterval(() => janitor.cleanup(), 60 * 60 * 1000);
```

### 2. Post-Task Cleanup

Always cleanup after completing tasks:

```javascript
async function runTask() {
  // Do work
  await butler.spawnAgent(...);

  // Cleanup
  await janitor.cleanup();
}
```

### 3. Monitor Memory

Track memory usage to detect leaks:

```javascript
const memUsage = janitor.getMemoryUsage();
console.log('Heap used:', memUsage.heapUsed);
```

### 4. Safe Deletion

Janitor automatically protects important files, but you can add custom protection:

```javascript
// Override isImportant method if needed
janitor.isImportant = (filePath) => {
  const important = ['my-important-file.txt'];
  return important.some(name => filePath.includes(name));
};
```

## Performance

- Cleanup duration: 50-500ms (depends on file count)
- Memory overhead: <5MB
- No external dependencies
- Safe for concurrent operations

## Troubleshooting

### Issue: High Memory Usage

**Solution:** Run `janitor.freeMemory()` to trigger garbage collection.

### Issue: Files Not Being Deleted

**Solution:** Check if files are in protected directories (node_modules, .git, src).

### Issue: Cleanup Too Aggressive

**Solution:** Increase `unusedFileAgeDays` in config:

```javascript
const janitor = new Janitor({ unusedFileAgeDays: 30 });
```

## Roadmap

- [ ] Custom cleanup patterns via config file
- [ ] Integration with Butler dashboard
- [ ] Real-time cleanup monitoring
- [ ] Cloud storage cleanup (S3, GCS)
- [ ] Docker container cleanup
- [ ] Database cache cleanup

## License

MIT

## Support

- Issues: [GitHub Issues](https://github.com/zoro-jiro-san/butler/issues)
- Docs: This file

---

**Janitor v1.0.0** - Keeping your AI agents clean and efficient!
