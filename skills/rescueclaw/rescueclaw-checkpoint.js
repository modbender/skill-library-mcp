/**
 * RescueClaw Checkpoint API
 * 
 * Provides safety checkpoint functionality for risky agent operations.
 * When a checkpoint is created, RescueClaw monitors the agent and will
 * auto-restore from backup if it becomes unresponsive.
 */

const fs = require('fs');
const { execSync } = require('child_process');

const path = require('path');
const os = require('os');
const CHECKPOINT_PATH = path.join(os.homedir(), '.openclaw', 'rescueclaw', 'checkpoint-request.json');

/**
 * Create a checkpoint before a risky operation
 * @param {string} reason - Description of the operation
 * @param {number} rollbackWindowSec - Seconds to monitor (default: 300)
 * @returns {Promise<void>}
 */
async function createCheckpoint(reason, rollbackWindowSec = 300) {
  const checkpoint = {
    action: 'checkpoint',
    reason: reason || 'Manual checkpoint',
    timestamp: new Date().toISOString(),
    rollback_window_seconds: rollbackWindowSec
  };
  
  try {
    // Ensure directory exists
    const dir = require('path').dirname(CHECKPOINT_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Write checkpoint file
    fs.writeFileSync(CHECKPOINT_PATH, JSON.stringify(checkpoint, null, 2));
    console.log(`🛟 Checkpoint created: ${reason}`);
  } catch (err) {
    console.error('⚠️  Failed to create checkpoint:', err.message);
    throw err;
  }
}

/**
 * Clear the checkpoint after successful operation
 * @returns {Promise<void>}
 */
async function clearCheckpoint() {
  try {
    if (fs.existsSync(CHECKPOINT_PATH)) {
      fs.unlinkSync(CHECKPOINT_PATH);
      console.log('✅ Checkpoint cleared');
    }
  } catch (err) {
    console.error('⚠️  Failed to clear checkpoint:', err.message);
    // Don't throw - this is not critical
  }
}

/**
 * Get RescueClaw status
 * @returns {Promise<object>} Status information
 */
async function getStatus() {
  try {
    const output = execSync('rescueclaw status --json', {
      encoding: 'utf-8',
      timeout: 5000
    });
    return JSON.parse(output);
  } catch (err) {
    // If JSON output not available, try plain text
    try {
      const output = execSync('rescueclaw status', {
        encoding: 'utf-8',
        timeout: 5000
      });
      return { raw: output, available: true };
    } catch {
      return { available: false, error: err.message };
    }
  }
}

/**
 * Check if RescueClaw daemon is running
 * @returns {Promise<boolean>}
 */
async function isRunning() {
  try {
    const status = await getStatus();
    return status.available !== false;
  } catch {
    return false;
  }
}

module.exports = {
  createCheckpoint,
  clearCheckpoint,
  getStatus,
  isRunning,
  CHECKPOINT_PATH
};
