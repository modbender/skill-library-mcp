#!/usr/bin/env node
/**
 * E.x.O. Ecosystem Manager
 * 
 * Install, update, and monitor E.x.O. tools.
 * 
 * Usage:
 *   exo install <package>     Install a package
 *   exo list                  List available/installed packages
 *   exo doctor                Health check all installed tools
 *   exo status                Quick status of all tools
 *   exo update [--check]      Check for or apply updates
 *   exo cron setup            Setup daily health check cron
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');

const PACKAGES = require('./packages.json');
const VERSION = require('./package.json').version;

const OPENCLAW_CONFIG = path.join(os.homedir(), '.openclaw', 'openclaw.json');
const EXO_STATE = path.join(os.homedir(), '.openclaw', 'exo-state.json');

// Colors
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m'
};

function log(msg) { console.log(`📦 ${msg}`); }
function success(msg) { console.log(`${colors.green}✅ ${msg}${colors.reset}`); }
function warn(msg) { console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`); }
function error(msg) { console.error(`${colors.red}❌ ${msg}${colors.reset}`); }

function runCmd(cmd, options = {}) {
  try {
    return execSync(cmd, { 
      encoding: 'utf8', 
      stdio: options.silent ? 'pipe' : 'inherit',
      timeout: options.timeout || 30000,
      ...options 
    });
  } catch (e) {
    if (options.ignoreError) return null;
    throw e;
  }
}

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(EXO_STATE, 'utf8'));
  } catch {
    return { installed: {}, lastCheck: null };
  }
}

function saveState(state) {
  fs.mkdirSync(path.dirname(EXO_STATE), { recursive: true });
  fs.writeFileSync(EXO_STATE, JSON.stringify(state, null, 2));
}

async function getNpmVersion(packageName) {
  return new Promise((resolve) => {
    https.get(`https://registry.npmjs.org/${packageName}/latest`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data).version);
        } catch {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

async function getInstalledVersion(pkg) {
  if (!pkg.versionCmd) return null;
  try {
    const result = runCmd(pkg.versionCmd, { silent: true, ignoreError: true });
    return result?.trim() || null;
  } catch {
    return null;
  }
}

async function runDoctor(pkg) {
  if (!pkg.doctorCmd) return { status: 'no-doctor', message: 'No doctor command' };
  
  try {
    const result = runCmd(pkg.doctorCmd, { silent: true, ignoreError: true, timeout: 60000 });
    if (!result) return { status: 'error', message: 'Doctor command failed' };
    
    try {
      return JSON.parse(result);
    } catch {
      // Non-JSON output, try to parse status
      if (result.includes('healthy') || result.includes('✅') || result.includes('passed')) {
        return { status: 'healthy' };
      }
      return { status: 'unknown', message: result.substring(0, 100) };
    }
  } catch (e) {
    return { status: 'error', message: e.message };
  }
}

// ============================================================================
// Commands
// ============================================================================

async function cmdList() {
  console.log('');
  log('E.x.O. Packages');
  console.log('='.repeat(60));
  
  const state = loadState();
  
  // Group by install type
  const npmPackages = [];
  const internalPackages = [];
  
  for (const [id, pkg] of Object.entries(PACKAGES.packages)) {
    if (pkg.installType === 'internal') {
      internalPackages.push([id, pkg]);
    } else {
      npmPackages.push([id, pkg]);
    }
  }
  
  // NPM packages (public)
  console.log('\n  📦 Public (npm install):\n');
  for (const [id, pkg] of npmPackages) {
    const installed = state.installed[id];
    const statusIcon = installed ? colors.green + '✓' + colors.reset : colors.dim + '○' + colors.reset;
    
    console.log(`  ${statusIcon} ${pkg.name}`);
    console.log(`    ${colors.dim}${pkg.description}${colors.reset}`);
    if (installed) {
      console.log(`    ${colors.cyan}v${installed.version}${colors.reset}`);
    }
  }
  
  // Internal packages (require GitHub access)
  console.log('\n  🔒 Internal (requires GitHub access):\n');
  for (const [id, pkg] of internalPackages) {
    const localPath = pkg.localPath?.replace('~', os.homedir());
    const exists = localPath && fs.existsSync(localPath);
    const statusIcon = exists ? colors.green + '✓' + colors.reset : colors.dim + '○' + colors.reset;
    
    console.log(`  ${statusIcon} ${pkg.name}`);
    console.log(`    ${colors.dim}${pkg.description}${colors.reset}`);
    if (exists) {
      console.log(`    ${colors.cyan}${localPath}${colors.reset}`);
    } else {
      console.log(`    ${colors.dim}→ exo internal clone${colors.reset}`);
    }
  }
  
  console.log('');
}

async function cmdInstall(packages) {
  if (packages.length === 0 || packages[0] === '--all') {
    packages = Object.keys(PACKAGES.packages).filter(id => 
      PACKAGES.packages[id].npm && PACKAGES.packages[id].status !== 'development'
    );
  }
  
  console.log('');
  log('Installing E.x.O. packages...');
  console.log('');
  
  const state = loadState();
  
  for (const pkgId of packages) {
    const pkg = PACKAGES.packages[pkgId];
    if (!pkg) {
      warn(`Unknown package: ${pkgId}`);
      continue;
    }
    
    if (!pkg.npm) {
      warn(`${pkg.name} is not yet available on npm (status: ${pkg.status || 'development'})`);
      continue;
    }
    
    console.log(`Installing ${pkg.name}...`);
    
    try {
      // Install via npm
      runCmd(`npm install -g ${pkg.npm}`, { stdio: 'pipe' });
      
      // Run setup if available
      if (pkg.npm === 'jasper-recall') {
        console.log('  Running setup...');
        runCmd('npx jasper-recall setup', { stdio: 'inherit' });
      } else if (pkg.npm === 'hopeid') {
        console.log('  Running setup...');
        runCmd('npx hopeid setup', { stdio: 'inherit' });
      } else if (pkg.npm === 'jasper-context-compactor') {
        console.log('  Running setup...');
        runCmd('npx jasper-context-compactor setup', { stdio: 'inherit' });
      }
      
      // Get installed version
      const version = await getInstalledVersion(pkg);
      
      state.installed[pkgId] = {
        version: version || 'unknown',
        installedAt: new Date().toISOString()
      };
      
      success(`${pkg.name} installed`);
    } catch (e) {
      error(`Failed to install ${pkg.name}: ${e.message}`);
    }
  }
  
  saveState(state);
  console.log('');
  success('Done!');
}

async function cmdDoctor(options = {}) {
  const { json = false, telegram = false } = options;
  
  const state = loadState();
  const results = [];
  
  if (!json) {
    console.log('');
    log('E.x.O. Health Check');
    console.log('='.repeat(60));
    console.log('');
  }
  
  for (const [id, pkg] of Object.entries(PACKAGES.packages)) {
    // Skip if not installed (npm) or not present (internal)
    if (pkg.installType === 'internal') {
      const localPath = pkg.localPath?.replace('~', os.homedir());
      if (!localPath || !fs.existsSync(localPath)) {
        if (!json) console.log(`  ⚪ ${pkg.name} — not cloned (exo internal clone)`);
        continue;
      }
    } else if (!state.installed[id] && !pkg.npm) {
      continue;
    }
    
    // Check if installed (npm packages)
    const version = await getInstalledVersion(pkg);
    if (!version && pkg.npm && pkg.installType !== 'local') {
      if (!json) console.log(`  ⚪ ${pkg.name} — not installed`);
      continue;
    }
    
    // Run doctor
    const health = await runDoctor(pkg);
    const latestVersion = pkg.npm ? await getNpmVersion(pkg.npm) : null;
    const updateAvailable = latestVersion && version && latestVersion !== version;
    
    const result = {
      id,
      name: pkg.name,
      version: version || (pkg.installType === 'internal' ? 'internal' : null),
      latestVersion,
      updateAvailable,
      health,
      installType: pkg.installType || 'npm'
    };
    results.push(result);
    
    if (!json) {
      const statusIcon = health.status === 'healthy' ? '✅' : 
                         health.status === 'no-doctor' ? '✅' :  // No doctor = assume OK for internal
                         health.status === 'error' ? '❌' : '⚠️';
      const updateBadge = updateAvailable ? ` ${colors.yellow}→ v${latestVersion}${colors.reset}` : '';
      const versionStr = version ? `v${version}` : (pkg.installType === 'internal' ? colors.dim + '(internal)' + colors.reset : '');
      console.log(`  ${statusIcon} ${pkg.name} ${versionStr}${updateBadge}`);
      
      if (health.checks) {
        for (const [key, val] of Object.entries(health.checks)) {
          console.log(`     ${colors.dim}${key}: ${val}${colors.reset}`);
        }
      }
    }
  }
  
  if (json) {
    console.log(JSON.stringify({ results, timestamp: new Date().toISOString() }, null, 2));
    return results;
  }
  
  // Summary
  console.log('');
  const healthy = results.filter(r => r.health.status === 'healthy' || r.health.status === 'no-doctor').length;
  const issues = results.filter(r => r.health.status === 'error').length;
  const updates = results.filter(r => r.updateAvailable).length;
  const npmPackages = results.filter(r => r.installType === 'npm').length;
  const internalPackages = results.filter(r => r.installType === 'internal').length;
  
  if (issues === 0 && updates === 0) {
    const parts = [];
    if (npmPackages > 0) parts.push(`${npmPackages} public`);
    if (internalPackages > 0) parts.push(`${internalPackages} internal`);
    success(`All ${healthy} packages healthy (${parts.join(', ')})`);
  } else {
    if (issues > 0) warn(`${issues} package(s) have issues`);
    if (updates > 0) console.log(`📦 ${updates} update(s) available — run: exo update`);
  }
  console.log('');
  
  // Telegram notification if requested
  if (telegram && (issues > 0 || updates > 0)) {
    await sendTelegramReport(results);
  }
  
  return results;
}

async function cmdUpdate(options = {}) {
  const { check = false } = options;
  
  console.log('');
  log(check ? 'Checking for updates...' : 'Updating E.x.O. packages...');
  console.log('');
  
  const state = loadState();
  let updatesAvailable = [];
  
  for (const [id, pkg] of Object.entries(PACKAGES.packages)) {
    if (!pkg.npm) continue;
    
    const installed = await getInstalledVersion(pkg);
    if (!installed) continue;
    
    const latest = await getNpmVersion(pkg.npm);
    if (latest && latest !== installed) {
      updatesAvailable.push({ id, pkg, installed, latest });
      console.log(`  📦 ${pkg.name}: ${installed} → ${latest}`);
    }
  }
  
  if (updatesAvailable.length === 0) {
    success('All packages up to date!');
    console.log('');
    return;
  }
  
  if (check) {
    console.log('');
    console.log(`Run 'exo update' to apply ${updatesAvailable.length} update(s)`);
    console.log('');
    return;
  }
  
  // Apply updates
  console.log('');
  for (const { id, pkg, latest } of updatesAvailable) {
    console.log(`Updating ${pkg.name}...`);
    try {
      runCmd(`npm install -g ${pkg.npm}@latest`, { stdio: 'pipe' });
      state.installed[id] = {
        version: latest,
        installedAt: new Date().toISOString()
      };
      success(`${pkg.name} updated to v${latest}`);
    } catch (e) {
      error(`Failed to update ${pkg.name}: ${e.message}`);
    }
  }
  
  saveState(state);
  console.log('');
  success('Updates complete!');
  console.log('');
}

async function cmdStatus() {
  const state = loadState();
  
  console.log('');
  log('E.x.O. Status');
  console.log('');
  
  let installed = 0;
  for (const [id, pkg] of Object.entries(PACKAGES.packages)) {
    const version = await getInstalledVersion(pkg);
    if (version) {
      console.log(`  ✓ ${pkg.name} v${version}`);
      installed++;
    }
  }
  
  if (installed === 0) {
    console.log('  No E.x.O. packages installed');
    console.log('  Run: exo install --all');
  }
  
  console.log('');
}

async function cmdInternal(args) {
  const subCmd = args[0];
  
  if (subCmd === 'clone') {
    console.log('');
    log('Cloning internal E.x.O. repos...');
    console.log('');
    console.log('  This requires GitHub access to E-x-O-Entertainment-Studios-Inc.');
    console.log('');
    
    const repos = [
      { name: 'hopeClaw', repo: 'hopeClaw' },
      { name: 'moraClaw', repo: 'moraClaw' },
      { name: 'task-dashboard', repo: 'task-dashboard' }
    ];
    
    for (const { name, repo } of repos) {
      const targetDir = path.join(os.homedir(), 'projects', name);
      
      if (fs.existsSync(targetDir)) {
        success(`${name} already exists: ${targetDir}`);
      } else {
        console.log(`  Cloning ${name}...`);
        try {
          runCmd(`git clone https://github.com/E-x-O-Entertainment-Studios-Inc/${repo}.git ${targetDir}`, { stdio: 'inherit' });
          success(`Cloned ${name}`);
        } catch (e) {
          error(`Failed to clone ${name}: ${e.message}`);
          console.log('  Make sure you have access to the private repo.');
          continue;
        }
      }
      
      // Install dependencies if package.json exists
      const pkgJson = path.join(targetDir, 'package.json');
      if (fs.existsSync(pkgJson)) {
        console.log(`  Installing ${name} dependencies...`);
        try {
          runCmd(`cd ${targetDir} && npm install`, { stdio: 'pipe' });
          success(`${name} dependencies installed`);
        } catch (e) {
          warn(`${name} npm install had issues`);
        }
      }
      console.log('');
    }
    
    success('Internal packages ready!');
    console.log('');
    console.log('  Run "exo internal status" to verify.');
    console.log('');
    
  } else if (subCmd === 'status') {
    console.log('');
    log('Internal Package Status');
    console.log('');
    
    for (const [id, pkg] of Object.entries(PACKAGES.packages)) {
      if (pkg.installType !== 'internal') continue;
      
      const localPath = pkg.localPath?.replace('~', os.homedir());
      const exists = localPath && fs.existsSync(localPath);
      
      if (exists) {
        success(`${pkg.name}: ${localPath}`);
      } else {
        console.log(`  ○ ${pkg.name}: not cloned`);
      }
    }
    console.log('');
    
  } else {
    console.log(`
E.x.O. Internal Packages

These packages require GitHub access to E-x-O-Entertainment-Studios-Inc.

COMMANDS:
  exo internal clone     Clone task-dashboard (hopeClaw + moraClaw)
  exo internal status    Check which internal packages are available

PACKAGES:
  hopeClaw       Meta-cognitive intervention agent (WHY)
  moraClaw       Temporal orchestration agent (WHEN)
  task-dashboard Dev ops center (task tracking, workers)
`);
  }
}

async function cmdCronSetup() {
  console.log('');
  log('Setting up E.x.O. health check cron...');
  console.log('');
  
  // Check if OpenClaw is available
  if (!fs.existsSync(OPENCLAW_CONFIG)) {
    error('OpenClaw not found. Install OpenClaw first.');
    return;
  }
  
  // Create cron job via OpenClaw
  const cronPayload = {
    name: 'exo-health-check',
    schedule: { kind: 'cron', expr: '0 9 * * *', tz: 'America/Regina' },
    sessionTarget: 'main',
    payload: {
      kind: 'systemEvent',
      text: '🔧 Daily E.x.O. health check: Run `exo doctor --telegram` to check all tools and send report if issues found.'
    }
  };
  
  console.log('  Cron job config:');
  console.log(`    Schedule: Daily at 9am CST`);
  console.log(`    Action: Health check + Telegram alert if issues`);
  console.log('');
  console.log('  To activate, add to OpenClaw cron:');
  console.log('    openclaw cron add', JSON.stringify(cronPayload));
  console.log('');
  
  success('Cron setup instructions generated');
  console.log('');
}

async function sendTelegramReport(results) {
  const issues = results.filter(r => r.health.status === 'error');
  const updates = results.filter(r => r.updateAvailable);
  
  let msg = '🔧 E.x.O. Health Report\n\n';
  
  for (const r of results) {
    const icon = r.health.status === 'healthy' ? '✅' : 
                 r.health.status === 'error' ? '❌' : '⚪';
    const update = r.updateAvailable ? ` → v${r.latestVersion}` : '';
    msg += `${icon} ${r.name} v${r.version}${update}\n`;
  }
  
  if (updates.length > 0) {
    msg += `\n📦 ${updates.length} update(s) available\nRun: exo update`;
  }
  
  // This would use OpenClaw's message tool
  console.log('');
  console.log('Telegram report:');
  console.log(msg);
}

function showHelp() {
  console.log(`
E.x.O. Ecosystem Manager v${VERSION}

USAGE:
  exo <command> [options]

COMMANDS:
  install [packages...]   Install public packages (or --all)
  list                    List available packages
  status                  Quick status of installed tools
  doctor                  Health check all installed tools
  update [--check]        Check for or apply updates
  internal clone          Clone internal repos (requires GitHub access)
  internal status         Check internal package status
  cron setup              Setup daily health check cron
  help                    Show this help

OPTIONS:
  --json                  Output as JSON (doctor command)
  --telegram              Send report to Telegram if issues (doctor command)
  --all                   Install all available packages

EXAMPLES:
  exo install jasper-recall hopeids
  exo install --all
  exo doctor
  exo doctor --telegram
  exo update --check
  exo update

PACKAGES:
  jasper-recall           Local RAG for agent memory
  hopeids                 Intrusion detection for AI agents
  jasper-configguard      Safe OpenClaw config management
  context-compactor       Token-based context compaction
  hopeclaw                Meta-cognitive agent (dev)
  moraclaw                Scheduling agent (dev)
`);
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'install':
    case 'i':
      await cmdInstall(args.slice(1));
      break;
    case 'list':
    case 'ls':
      await cmdList();
      break;
    case 'doctor':
    case 'health':
      await cmdDoctor({
        json: args.includes('--json'),
        telegram: args.includes('--telegram')
      });
      break;
    case 'status':
      await cmdStatus();
      break;
    case 'update':
    case 'upgrade':
      await cmdUpdate({ check: args.includes('--check') });
      break;
    case 'cron':
      if (args[1] === 'setup') {
        await cmdCronSetup();
      } else {
        error('Usage: exo cron setup');
      }
      break;
    case 'internal':
      await cmdInternal(args.slice(1));
      break;
    case 'help':
    case '--help':
    case '-h':
    case undefined:
      showHelp();
      break;
    case '--version':
    case '-v':
      console.log(VERSION);
      break;
    default:
      error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
}

main().catch(e => {
  error(e.message);
  process.exit(1);
});
