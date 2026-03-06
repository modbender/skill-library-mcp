const fs = require('fs').promises;
const path = require('path');

/**
 * Resolve project root robustly.
 * - Never rely on process.cwd() because OpenClaw Cron agentTurn may execute from a different CWD.
 * - This file lives at: <root>/scripts/state/resources.js
 */
function getProjectRoot() {
  return path.resolve(__dirname, '..', '..');
}

function getResourcesDir() {
  return path.join(getProjectRoot(), 'resources');
}

function getResourcePaths() {
  const dir = getResourcesDir();
  return {
    dir,
    eventsFile: path.join(dir, 'events.json'),
    positionsFile: path.join(dir, 'positions.json'),
    topVolumeCacheFile: path.join(dir, 'topVolumeCache.json'),
    nearCounterFile: path.join(dir, 'nearCounter.json'),
    heartbeatFile: path.join(dir, 'heartbeat.json'),
    monitorLockFile: path.join(dir, 'lock_monitor.json'),
    workerLockFile: path.join(dir, 'lock_worker.json'),
  };
}

/**
 * Ensure local resource files exist.
 * This is safe for both local runs and OpenClaw Cron runs.
 */
async function ensureResources() {
  const { dir, eventsFile, positionsFile, topVolumeCacheFile, nearCounterFile, heartbeatFile } = getResourcePaths();
  await fs.mkdir(dir, { recursive: true });

  // Create empty JSON stores if missing
  await fs.access(eventsFile).catch(async () => {
    await fs.writeFile(eventsFile, '[]', 'utf8');
  });

  await fs.access(positionsFile).catch(async () => {
    await fs.writeFile(positionsFile, JSON.stringify({ positions: [] }, null, 2), 'utf8');
  });

  await fs.access(topVolumeCacheFile).catch(async () => {
    await fs.writeFile(topVolumeCacheFile, JSON.stringify({ updatedAt: 0, markets: [] }, null, 2), 'utf8');
  });

  await fs.access(nearCounterFile).catch(async () => {
    await fs.writeFile(nearCounterFile, JSON.stringify({ updatedAt: 0, counts: {} }, null, 2), 'utf8');
  });

  await fs.access(heartbeatFile).catch(async () => {
    await fs.writeFile(heartbeatFile, JSON.stringify({ lastRunAt: null, lastSummary: null }, null, 2), 'utf8');
  });

  return getResourcePaths();
}

module.exports = { ensureResources, getResourcesDir, getResourcePaths };
