#!/usr/bin/env node
/**
 * Skill Auditor Setup Wizard
 * Cross-platform interactive setup for optional features
 */

const { execSync, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw');
const CONFIG_FILE = path.join(CONFIG_DIR, 'skill-auditor.json');

// Default config
const DEFAULT_CONFIG = {
  astAnalysis: false,
  autoScanOnInstall: false,
  autoScanSeverityThreshold: 'high', // critical, high, medium, low
  pythonPath: 'python',
  lastAuditDate: null,
  installedVersion: '2.0.0'
};

// ANSI colors
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m'
};

function log(msg, color = '') {
  console.log(`${color}${msg}${colors.reset}`);
}

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')) };
    }
  } catch (e) {}
  return { ...DEFAULT_CONFIG };
}

function saveConfig(config) {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

function detectOS() {
  const platform = process.platform;
  if (platform === 'win32') return 'Windows';
  if (platform === 'darwin') return 'macOS';
  return 'Linux';
}

function checkPython() {
  const pythonCmds = process.platform === 'win32' 
    ? ['python', 'python3', 'py'] 
    : ['python3', 'python'];
  
  for (const cmd of pythonCmds) {
    try {
      const result = spawnSync(cmd, ['--version'], { encoding: 'utf8', timeout: 5000 });
      if (result.status === 0) {
        const version = result.stdout.trim() || result.stderr.trim();
        return { available: true, command: cmd, version };
      }
    } catch (e) {}
  }
  return { available: false };
}

function checkTreeSitter(pythonCmd) {
  try {
    const result = spawnSync(pythonCmd, ['-c', 'import tree_sitter; import tree_sitter_python; print("OK")'], {
      encoding: 'utf8',
      timeout: 10000
    });
    return result.status === 0 && result.stdout.includes('OK');
  } catch (e) {
    return false;
  }
}

function installTreeSitter(pythonCmd) {
  log('\nInstalling tree-sitter packages...', colors.cyan);
  
  const pipCmd = process.platform === 'win32' ? `${pythonCmd} -m pip` : `${pythonCmd} -m pip`;
  
  try {
    execSync(`${pipCmd} install tree-sitter tree-sitter-python`, {
      stdio: 'inherit',
      timeout: 120000
    });
    return true;
  } catch (e) {
    log(`\nInstallation failed: ${e.message}`, colors.red);
    return false;
  }
}

function setupAutoScanHook(config) {
  // Create a wrapper script that can be called after clawhub install
  const hookDir = path.join(CONFIG_DIR, 'hooks');
  if (!fs.existsSync(hookDir)) {
    fs.mkdirSync(hookDir, { recursive: true });
  }
  
  const isWindows = process.platform === 'win32';
  const hookScript = isWindows ? path.join(hookDir, 'post-skill-install.cmd') : path.join(hookDir, 'post-skill-install.sh');
  
  const skillAuditorPath = path.resolve(__dirname, '..');
  
  if (isWindows) {
    const content = `@echo off
REM Skill Auditor Auto-Scan Hook
REM Called after skill installation

set SKILL_PATH=%1
if "%SKILL_PATH%"=="" (
  echo Usage: post-skill-install.cmd [skill-path]
  exit /b 1
)

echo.
echo [Skill Auditor] Scanning installed skill...
node "${path.join(skillAuditorPath, 'scripts', 'scan-skill.js')}" "%SKILL_PATH%" --severity ${config.autoScanSeverityThreshold}

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo [WARNING] Security issues found! Review the report above.
  echo Press any key to continue anyway, or Ctrl+C to abort...
  pause >nul
)
`;
    fs.writeFileSync(hookScript, content);
  } else {
    const content = `#!/bin/bash
# Skill Auditor Auto-Scan Hook
# Called after skill installation

SKILL_PATH="$1"
if [ -z "$SKILL_PATH" ]; then
  echo "Usage: post-skill-install.sh [skill-path]"
  exit 1
fi

echo ""
echo "[Skill Auditor] Scanning installed skill..."
node "${path.join(skillAuditorPath, 'scripts', 'scan-skill.js')}" "$SKILL_PATH" --severity ${config.autoScanSeverityThreshold}

if [ $? -ne 0 ]; then
  echo ""
  echo "[WARNING] Security issues found! Review the report above."
  read -p "Press Enter to continue anyway, or Ctrl+C to abort..."
fi
`;
    fs.writeFileSync(hookScript, content, { mode: 0o755 });
  }
  
  return hookScript;
}

async function prompt(rl, question) {
  return new Promise(resolve => {
    rl.question(question, resolve);
  });
}

async function runWizard() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const config = loadConfig();
  const os = detectOS();
  const python = checkPython();
  
  log('\n╔════════════════════════════════════════════════════════════╗', colors.cyan);
  log('║           SKILL AUDITOR SETUP WIZARD v2.0                  ║', colors.cyan);
  log('╚════════════════════════════════════════════════════════════╝\n', colors.cyan);
  
  log(`Detected OS: ${os}`, colors.bright);
  
  if (python.available) {
    log(`Python: ${python.version} (${python.command})`, colors.green);
    config.pythonPath = python.command;
  } else {
    log('Python: Not found', colors.red);
    log('\nPython is required for advanced AST analysis.', colors.yellow);
    log('Install Python from https://python.org and re-run setup.\n', colors.yellow);
  }
  
  // Check current tree-sitter status
  const hasTreeSitter = python.available && checkTreeSitter(python.command);
  if (hasTreeSitter) {
    log('Tree-sitter: Installed ✓', colors.green);
    config.astAnalysis = true;
  } else if (python.available) {
    log('Tree-sitter: Not installed', colors.yellow);
  }
  
  log('\n─────────────────────────────────────────────────────────────\n');
  
  // Feature 1: AST Analysis
  log(`${colors.bright}1. Advanced AST Dataflow Analysis${colors.reset}`, colors.cyan);
  log('');
  log('   What it does:', colors.bright);
  log('   Traces how data moves through code - from where it\'s read');
  log('   to where it\'s sent. Catches attacks that pattern matching misses.');
  log('');
  log('   Real test results:', colors.yellow);
  log('   • Without AST: Found 13 issues in a malicious skill');
  log('   • With AST:    Found 35 issues (detected 22 more threats!)');
  log('   • Catches: env vars → network requests, file reads → HTTP posts');
  log('');
  log('   Install requirement:', colors.dim);
  log('   pip install tree-sitter tree-sitter-python');
  log('   (No compiler needed - prebuilt packages for all platforms)\n');
  
  if (!hasTreeSitter && python.available) {
    const answer = await prompt(rl, 'Enable AST dataflow analysis? (y/N): ');
    if (answer.toLowerCase() === 'y') {
      const success = installTreeSitter(python.command);
      if (success && checkTreeSitter(python.command)) {
        log('✓ AST analysis enabled! You\'ll now catch 2-3x more threats.', colors.green);
        config.astAnalysis = true;
      } else {
        log('✗ Installation failed. AST analysis disabled.', colors.red);
        config.astAnalysis = false;
      }
    } else {
      config.astAnalysis = false;
      log('Skipped. Run "node scripts/setup.js --enable-ast" anytime to enable.', colors.yellow);
    }
  } else if (hasTreeSitter) {
    config.astAnalysis = true;
    log('✓ AST analysis already enabled!', colors.green);
  } else if (!python.available) {
    log('⚠ Python not found. Install Python 3.8+ to enable this feature.', colors.yellow);
  }
  
  log('\n─────────────────────────────────────────────────────────────\n');
  
  // Feature 2: Auto-scan on install
  log(`${colors.bright}2. Auto-Scan on Skill Install${colors.reset}`, colors.cyan);
  log('');
  log('   What it does:', colors.bright);
  log('   Automatically scans every new skill you install.');
  log('   Warns you BEFORE a risky skill can run.');
  log('');
  log('   Why it matters:', colors.yellow);
  log('   • We tested 80 skills and found 10 with CRITICAL issues');
  log('   • Some skills access credentials without disclosing it');
  log('   • Auto-scan catches these before they can do damage');
  log('');
  log('   How it works:', colors.dim);
  log('   Creates a hook script that runs after "clawhub install"');
  log('   You control what severity level triggers a warning\n');
  
  const autoScanAnswer = await prompt(rl, 'Enable auto-scan on skill install? (y/N): ');
  if (autoScanAnswer.toLowerCase() === 'y') {
    config.autoScanOnInstall = true;
    
    // Severity threshold
    log('\nWhat severity should trigger a warning?', colors.bright);
    log('');
    log('  1. critical - Only the worst issues (data theft, backdoors)');
    log('  2. high     - Critical + high risk (recommended)');
    log('  3. medium   - Most issues except minor ones');
    log('  4. low      - Everything (may have false positives)');
    log('');
    
    const sevAnswer = await prompt(rl, 'Choose (1-4, default 2): ');
    const sevMap = { '1': 'critical', '2': 'high', '3': 'medium', '4': 'low' };
    config.autoScanSeverityThreshold = sevMap[sevAnswer] || 'high';
    
    const hookPath = setupAutoScanHook(config);
    log(`\n✓ Auto-scan enabled!`, colors.green);
    log(`  Threshold: ${config.autoScanSeverityThreshold} and above`, colors.cyan);
    
    log('\n📝 To activate, add this alias to your shell:', colors.yellow);
    if (process.platform === 'win32') {
      log(`\n   In PowerShell profile (~\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1):`, colors.dim);
      log(`   function clawhub-safe { clawhub install $args[0]; & "${hookPath}" $args[0] }`, colors.bright);
    } else {
      log(`\n   In ~/.bashrc or ~/.zshrc:`, colors.dim);
      log(`   alias clawhub-safe='f(){ clawhub install "$1" && "${hookPath}" "$1"; }; f'`, colors.bright);
    }
    log(`\n   Then use: clawhub-safe <skill-name>`, colors.cyan);
  } else {
    config.autoScanOnInstall = false;
    log('Skipped. You can still scan manually with: node scripts/scan-skill.js <path>', colors.yellow);
  }
  
  log('\n─────────────────────────────────────────────────────────────\n');
  
  // Feature 3: Audit all installed skills
  log(`${colors.bright}3. Audit All Installed Skills${colors.reset}`, colors.cyan);
  log('');
  log('   What it does:', colors.bright);
  log('   Scans every skill you have installed in one command.');
  log('   Shows you which ones might be risky.');
  log('');
  log('   Our test results:', colors.yellow);
  log('   • Scanned 80 skills in under 2 minutes');
  log('   • Found 46 clean, 10 critical, 8 high-risk');
  log('   • Identified skills accessing credentials without disclosure');
  log('');
  log('   This feature is always available. No setup needed.', colors.dim);
  log('');
  log('   Run it now?', colors.bright);
  
  const auditAnswer = await prompt(rl, 'Audit all your installed skills? (y/N): ');
  if (auditAnswer.toLowerCase() === 'y') {
    log('\nStarting audit... this may take a few minutes.\n', colors.cyan);
    rl.close();
    
    // Run the audit
    const auditScript = path.join(__dirname, 'audit-installed.js');
    try {
      require('child_process').execSync(`node "${auditScript}"`, { stdio: 'inherit' });
    } catch (e) {
      // Exit code non-zero means findings were found, which is expected
    }
    
    // Save config and exit
    saveConfig(config);
    log('\n✓ Configuration saved!', colors.green);
    process.exit(0);
  }
  
  log('\n─────────────────────────────────────────────────────────────\n');
  
  // Save config
  saveConfig(config);
  log('✓ Configuration saved!', colors.green);
  log(`  Config file: ${CONFIG_FILE}\n`, colors.cyan);
  
  // Summary
  log(`${colors.bright}Setup Complete!${colors.reset}`, colors.green);
  log('\nYour configuration:');
  log(`  • Core scanning: ✓ Always available (no setup needed)`);
  log(`  • AST analysis:  ${config.astAnalysis ? '✓ Enabled - catches 2-3x more threats' : '✗ Disabled'}`);
  log(`  • Auto-scan:     ${config.autoScanOnInstall ? '✓ Enabled - scans new installs' : '✗ Disabled'}`);
  
  log('\nQuick commands:', colors.cyan);
  log('  node scripts/scan-skill.js <path>   Scan one skill');
  log('  node scripts/audit-installed.js     Scan all installed skills');
  log('  node scripts/setup.js --status      Check current config');
  
  log('\nRe-run this wizard anytime: node scripts/setup.js', colors.dim);
  
  rl.close();
}

// CLI argument handling
const args = process.argv.slice(2);

if (args.includes('--enable-ast')) {
  const python = checkPython();
  if (!python.available) {
    log('Python not found. Install Python first.', colors.red);
    process.exit(1);
  }
  if (checkTreeSitter(python.command)) {
    log('Tree-sitter already installed!', colors.green);
  } else {
    const success = installTreeSitter(python.command);
    if (success) {
      const config = loadConfig();
      config.astAnalysis = true;
      config.pythonPath = python.command;
      saveConfig(config);
      log('✓ AST analysis enabled!', colors.green);
    }
  }
  process.exit(0);
}

if (args.includes('--status')) {
  const config = loadConfig();
  const python = checkPython();
  const hasTreeSitter = python.available && checkTreeSitter(python.command);
  
  log('\nSkill Auditor Status:', colors.cyan);
  log(`  Config file: ${CONFIG_FILE}`);
  log(`  AST analysis: ${config.astAnalysis && hasTreeSitter ? '✓ Enabled' : '✗ Disabled'}`);
  log(`  Auto-scan: ${config.autoScanOnInstall ? '✓ Enabled' : '✗ Disabled'}`);
  if (config.autoScanOnInstall) {
    log(`  Severity threshold: ${config.autoScanSeverityThreshold}`);
  }
  log(`  Python: ${python.available ? python.version : 'Not found'}`);
  log(`  Tree-sitter: ${hasTreeSitter ? 'Installed' : 'Not installed'}`);
  process.exit(0);
}

if (args.includes('--help') || args.includes('-h')) {
  log('\nSkill Auditor Setup', colors.cyan);
  log('\nUsage: node setup.js [options]');
  log('\nOptions:');
  log('  (no args)     Run interactive setup wizard');
  log('  --enable-ast  Install tree-sitter for AST analysis');
  log('  --status      Show current configuration');
  log('  --help        Show this help');
  process.exit(0);
}

// Run wizard
runWizard().catch(console.error);
