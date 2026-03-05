#!/usr/bin/env node
// OpenClaw Backup Automation - Generic Version
// Credentials, periodic backup, and git sync are OPT-IN only

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = {
  backupDir: path.join(process.env.HOME || process.env.USERPROFILE, 'backups'),
  keepDays: 7,
  gitSync: false,  // OPT-IN
  credentials: false // OPT-IN
};

// OPT-IN files
const OPTIN_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw');
const CREDENTIALS_FILE = path.join(OPTIN_DIR, 'backup-credentials-enabled');
const PERIODIC_FILE = path.join(OPTIN_DIR, 'backup-periodic-enabled');
const GITSYNC_FILE = path.join(OPTIN_DIR, 'backup-git-enabled');

function log(msg) { console.log(`[backup] ${msg}`); }
function ensureDir(dir) { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); }

function isEnabled(file) { try { return fs.existsSync(file); } catch { return false; } }

function getBackupName() {
  const now = new Date();
  return `openclaw-${now.toISOString().slice(0,10).replace(/-/g,'')}-${now.toTimeString().slice(0,8).replace(/:/g,'')}`;
}

function backup() {
  const backupName = getBackupName();
  const backupPath = path.join(CONFIG.backupDir, `${backupName}.tar.gz`);
  ensureDir(CONFIG.backupDir);
  
  const credsEnabled = isEnabled(CREDENTIALS_FILE);
  const periodicEnabled = isEnabled(PERIODIC_FILE);
  const gitEnabled = isEnabled(GITSYNC_FILE);
  
  log(`Starting backup: ${backupName}`);
  
  // Core files always included
  const files = [
    '.openclaw/agents',
    '.openclaw/workspace/skills',
    '.openclaw/workspace/.openclaw-cron.json',
    '.openclaw/workspace/MEMORY.md',
    '.openclaw/workspace/memory',
    '.openclaw/openclaw.json'
  ];
  
  // OPT-IN: credentials
  if (credsEnabled) files.push('.openclaw/credentials');
  
  try {
    execSync(`tar -czf "${backupPath}" -C ${process.env.HOME || process.env.USERPROFILE} ${files.join(' ')} 2>/dev/null`, { stdio: 'pipe' });
    cleanup();
    
    const stats = fs.statSync(backupPath);
    console.log(`✅ Backup: ${backupPath} (${(stats.size/1024/1024).toFixed(1)}MB)`);
    console.log(`   Credentials: ${credsEnabled?'INCLUDED':'excluded (opt-in)'}`);
    console.log(`   Periodic: ${periodicEnabled?'ENABLED':'not configured'}`);
    console.log(`   Git sync: ${gitEnabled?'ENABLED':'not configured'}`);
    
    if (gitEnabled) gitSync();
    
    return backupPath;
  } catch (err) {
    console.error(`❌ Backup failed: ${err.message}`);
    process.exit(1);
  }
}

function cleanup() {
  try {
    if (!fs.existsSync(CONFIG.backupDir)) return;
    const files = fs.readdirSync(CONFIG.backupDir).filter(f=>f.startsWith('openclaw-')&&f.endsWith('.tar.gz')).sort().reverse();
    if (files.length > CONFIG.keepDays) files.slice(CONFIG.keepDays).forEach(f=>fs.unlinkSync(path.join(CONFIG.backupDir,f)));
  } catch (err) { log(`Cleanup: ${err.message}`); }
}

function gitSync() {
  try {
    const workspace = path.join(OPTIN_DIR, 'workspace');
    if (fs.existsSync(path.join(workspace,'.git'))) {
      execSync('git add . && git commit -m "Auto backup"', { cwd: workspace, stdio: 'pipe' });
      execSync('git push origin main', { cwd: workspace, stdio: 'pipe' });
      log('Git sync complete');
    }
  } catch (err) { log(`Git sync: ${err.message}`); }
}

function list() {
  if (!fs.existsSync(CONFIG.backupDir)) { console.log('No backups'); return; }
  const files = fs.readdirSync(CONFIG.backupDir).filter(f=>f.startsWith('openclaw-')&&f.endsWith('.tar.gz')).sort().reverse();
  console.log('Available backups:');
  files.length ? files.forEach(f=>console.log(`  ${f} (${(fs.statSync(path.join(CONFIG.backupDir,f)).size/1024/1024).toFixed(1)}MB)`)) : console.log('  (none)');
  console.log('\nUse "backup credentials-enable" to include sensitive data');
}

function restore(name) {
  const p = path.join(CONFIG.backupDir, `${name}.tar.gz`);
  if (!fs.existsSync(p)) { console.error('Not found. Use "backup list"'); process.exit(1); }
  log(`Restoring from: ${name}`);
  try {
    execSync(`tar -xzf "${p}" -C ${process.env.HOME || process.env.USERPROFILE}`, { stdio: 'inherit' });
    console.log('✅ Restore complete');
    console.log('\n⚠️ Restore credentials manually if needed');
  } catch (err) { console.error(`❌ ${err.message}`); process.exit(1); }
}

function status() {
  console.log('=== Status ===');
  console.log(`Credentials: ${isEnabled(CREDENTIALS_FILE)?'✅ ENABLED':'❌ disabled (opt-in)'}`);
  console.log(`Periodic: ${isEnabled(PERIODIC_FILE)?'✅ ENABLED':'❌ disabled (opt-in)'}`);
  console.log(`Git sync: ${isEnabled(GITSYNC_FILE)?'✅ ENABLED':'❌ disabled (opt-in)'}`);
  console.log(`Backup dir: ${CONFIG.backupDir}`);
  console.log(`Keep: ${CONFIG.keepDays} days`);
  if (!isEnabled(CREDENTIALS_FILE)) console.log('\n→ "backup credentials-enable" to include tokens/keys');
  if (!isEnabled(PERIODIC_FILE)) console.log('→ "backup periodic-enable" for daily backups');
  if (!isEnabled(GITSYNC_FILE)) console.log('→ "backup git-enable" to auto-push');
}

function toggle(file, enable) {
  if (enable) { fs.writeFileSync(file, 'enabled\n'); console.log(`✅ Enabled: ${path.basename(file)}`); }
  else if (fs.existsSync(file)) { fs.unlinkSync(file); console.log(`❌ Disabled: ${path.basename(file)}`); }
  else console.log('Already disabled');
}

function suggestPeriodic() {
  console.log('\n💡 To enable daily automatic backups:');
  console.log('   crontab -e');
  console.log('   Add: 0 2 * * * cd ~/.openclaw/workspace && node skills/backup-automation/scripts/backup.js');
}

function suggestGit() {
  console.log('\n💡 To enable git sync:');
  console.log('   backup git-enable');
  console.log('   (Requires git remote configured)');
}

// CLI
const cmd = process.argv[2], arg = process.argv[3];
switch (cmd) {
  case 'backup': case undefined: backup(); break;
  case 'list': list(); break;
  case 'restore': if (!arg) { console.error('Usage: backup restore <name>'); process.exit(1); } restore(arg); break;
  case 'status': status(); break;
  case 'credentials-enable': toggle(CREDENTIALS_FILE, true); break;
  case 'credentials-disable': toggle(CREDENTIALS_FILE, false); break;
  case 'periodic-enable': toggle(PERIODIC_FILE, true); suggestPeriodic(); break;
  case 'periodic-disable': toggle(PERIODIC_FILE, false); break;
  case 'git-enable': toggle(GITSYNC_FILE, true); suggestGit(); break;
  case 'git-disable': toggle(GITSYNC_FILE, false); break;
  case 'help': default:
    console.log(`
OpenClaw Backup Automation

Usage: backup [command]

Commands:
  backup                    Run backup
  backup list               List backups
  backup restore <name>     Restore backup
  backup status             Show status

  backup credentials-enable    Include credentials (OPT-IN)
  backup credentials-disable   Exclude credentials
  backup periodic-enable      Enable daily backups (OPT-IN)
  backup periodic-disable     Disable daily
  backup git-enable          Enable git sync (OPT-IN)
  backup git-disable         Disable git sync

Note: Credentials are always OPT-IN for security.
`);
}
