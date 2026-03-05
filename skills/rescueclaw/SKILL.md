# RescueClaw Skill

Provides checkpoint/rollback safety net for risky operations.

## Before Risky Operations

Before modifying config, installing skills, or updating the gateway, create a checkpoint:

```javascript
const rescueclaw = require('./rescueclaw-checkpoint');
await rescueclaw.createCheckpoint('About to apply config changes');
```

RescueClaw will take an immediate backup. If the agent goes unresponsive within the rollback window, it auto-restores.

## After Successful Operations

Clear the checkpoint:

```javascript
const rescueclaw = require('./rescueclaw-checkpoint');
await rescueclaw.clearCheckpoint();
```

## Commands

The agent can also invoke RescueClaw CLI directly:

- `rescueclaw backup` — manual snapshot
- `rescueclaw status` — check health
- `rescueclaw list` — list backups

## Installation

The daemon binary is bundled for supported platforms (linux/arm64). On install, it copies to `~/.local/bin/rescueclaw`. For other platforms, download from [GitHub Releases](https://github.com/harman314/rescueclaw/releases).

Data is stored in `~/.openclaw/rescueclaw/` (user-local, no sudo required).

## API Reference

### `createCheckpoint(reason, rollbackWindowSec = 300)`

Creates a checkpoint file that RescueClaw monitors. If the agent becomes unresponsive within the rollback window, RescueClaw will immediately restore from the checkpoint backup.

**Parameters:**
- `reason` (string): Description of what operation is about to be performed
- `rollbackWindowSec` (number, optional): How many seconds to monitor for issues (default: 300)

**Returns:** Promise<void>

### `clearCheckpoint()`

Removes the checkpoint file, signaling that the risky operation completed successfully.

**Returns:** Promise<void>

### `getStatus()`

Gets RescueClaw daemon status by invoking the CLI.

**Returns:** Promise<object> with health status details

## Example: Safe Config Update

```javascript
const fs = require('fs');
const rescueclaw = require('./rescueclaw-checkpoint');

async function updateConfig(newConfig) {
  // Create safety checkpoint
  await rescueclaw.createCheckpoint('Updating OpenClaw config', 180);
  
  try {
    // Perform the risky operation
    fs.writeFileSync('~/.openclaw/openclaw.json', JSON.stringify(newConfig));
    
    // Restart gateway
    await exec('systemctl restart openclaw-gateway');
    
    // If we get here, it worked!
    await rescueclaw.clearCheckpoint();
    console.log('✅ Config updated successfully');
  } catch (err) {
    console.error('❌ Config update failed:', err);
    // Don't clear checkpoint - let RescueClaw auto-restore
  }
}
```
