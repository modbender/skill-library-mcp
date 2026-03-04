const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// Validate CID - only allow alphanumeric characters, reject empty, max 128 chars
function validateCID(cid) {
  if (!cid || typeof cid !== 'string') return false;
  if (cid.length === 0 || cid.length > 128) return false;
  return /^[a-zA-Z0-9]+$/.test(cid);
}

// Heartbeat check — verify memory files exist and aren't empty
// Auto-restore if missing or corrupted

const WORKSPACE_DIR = path.resolve(__dirname, '../..');
const SOUL_PATH = path.join(WORKSPACE_DIR, 'SOUL.md');
const MEMORY_DIR = path.join(WORKSPACE_DIR, 'memory');
const LOG_PATH = path.join(WORKSPACE_DIR, 'vault-log.json');

function getFileSize(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return stats.size;
  } catch {
    return 0;
  }
}

function getDirSize(dirPath) {
  try {
    const files = fs.readdirSync(dirPath);
    return files.length;
  } catch {
    return 0;
  }
}

function getLatestCID() {
  try {
    if (!fs.existsSync(LOG_PATH)) return null;
    const log = JSON.parse(fs.readFileSync(LOG_PATH, 'utf8'));
    if (log.length === 0) return null;
    return log[log.length - 1].cid;
  } catch {
    return null;
  }
}

async function heartbeat() {
  console.log('Running X1 Vault heartbeat check...\n');
  
  let issues = [];
  
  // Check SOUL.md
  const soulSize = getFileSize(SOUL_PATH);
  console.log(`SOUL.md: ${soulSize} bytes`);
  if (soulSize < 10) {
    issues.push('SOUL.md missing or too small (< 10 bytes)');
  }
  
  // Check memory/ directory
  const memoryFiles = getDirSize(MEMORY_DIR);
  console.log(`memory/ directory: ${memoryFiles} files`);
  if (memoryFiles === 0) {
    issues.push('memory/ directory empty');
  }
  
  // Report status
  console.log('\n--- Heartbeat Status ---');
  
  if (issues.length === 0) {
    console.log('✓ All checks passed — memory files healthy');
    console.log('No action needed.');
    return;
  }
  
  // Issues found — attempt auto-restore
  console.log('✗ Issues detected:');
  issues.forEach(issue => console.log(`  - ${issue}`));
  
  console.log('\nAttempting auto-restore from latest backup...');
  
  const latestCID = getLatestCID();
  if (!latestCID) {
    console.error('ERROR: No backups found in vault-log.json');
    console.error('Cannot auto-restore — manual intervention required');
    process.exit(1);
  }
  
  // Validate CID before using in shell command
  if (!validateCID(latestCID)) {
    console.error('ERROR: Invalid CID format. CID must only contain letters and numbers.');
    console.error('CID received:', latestCID);
    process.exit(1);
  }

  console.log(`Latest backup CID: ${latestCID}`);
  console.log('Triggering restore...\n');

  try {
    execFileSync('node', [path.join(__dirname, 'restore.js'), latestCID], {
      stdio: 'inherit',
      cwd: __dirname
    });
    console.log('\n✓ Auto-restore completed successfully');
  } catch (err) {
    console.error('\n✗ Auto-restore failed:', err.message);
    console.error('Manual restore required:');
    console.error(`  node src/restore.js ${latestCID}`);
    process.exit(1);
  }
}

heartbeat().catch(err => {
  console.error('Heartbeat failed:', err);
  process.exit(1);
});
