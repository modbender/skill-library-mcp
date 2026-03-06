const fs = require('fs');
const path = require('path');

// Read vault-log.json and display numbered list of backups
async function listBackups() {
  const logPath = path.resolve(__dirname, '../..', 'vault-log.json');
  
  if (!fs.existsSync(logPath)) {
    console.error('No vault-log.json found. No backups recorded.');
    process.exit(1);
  }
  
  const log = JSON.parse(fs.readFileSync(logPath, 'utf8'));
  
  if (log.length === 0) {
    console.log('No backups found.');
    return;
  }
  
  console.log('Available backups:\n');
  
  log.forEach((entry, index) => {
    const num = index + 1;
    const date = new Date(entry.timestamp).toLocaleString();
    const cid = entry.cid ? entry.cid.slice(0, 16) + '...' : 'N/A';
    const txStatus = entry.txHash ? '✓ anchored' : 'IPFS only';
    
    console.log(`${num}. ${date} — ${cid} (${txStatus})`);
  });
  
  console.log('\nTo restore a specific backup:');
  console.log('  node restore.js <CID>');
  console.log('\nTo restore only memory folder:');
  console.log('  node restore.js <CID> --only memory/');
}

listBackups().catch(err => {
  console.error('Failed to list backups:', err);
  process.exit(1);
});
