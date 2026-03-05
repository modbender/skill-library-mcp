#!/usr/bin/env node
/**
 * X CDP Skill setup wizard.
 * Checks environment, installs dependencies, launches Chromium, guides login.
 *
 * Usage: node scripts/setup.js [--port 18802] [--profile ./chromium-profile]
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const net = require('net');

const DEFAULT_PORT = 18802;
const DEFAULT_PROFILE = path.join(os.homedir(), 'chromium-profiles', 'x-cdp');

// Parse args
const args = { port: DEFAULT_PORT, profile: DEFAULT_PROFILE };
for (let i = 2; i < process.argv.length; i++) {
  if (process.argv[i] === '--port' && process.argv[i + 1]) {
    args.port = parseInt(process.argv[i + 1], 10);
    i++;
  } else if (process.argv[i] === '--profile' && process.argv[i + 1]) {
    args.profile = path.resolve(process.argv[i + 1]);
    i++;
  }
}

const STEPS = ['chromium', 'puppeteer', 'launch', 'login'];
let currentStep = 0;

function log(msg) { console.log(`[setup] ${msg}`); }
function ok(msg) { console.log(`  ✅ ${msg}`); }
function fail(msg) { console.log(`  ❌ ${msg}`); }
function info(msg) { console.log(`  ℹ️  ${msg}`); }

// ─── Step 1: Find Chromium ───

function findChromium() {
  log('Step 1/4: Checking for Chromium...');

  const platform = os.platform();
  const candidates = [];

  if (platform === 'darwin') {
    candidates.push(
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    );
  } else if (platform === 'linux') {
    candidates.push(
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/snap/bin/chromium',
    );
  } else if (platform === 'win32') {
    const programFiles = process.env['ProgramFiles'] || 'C:\\Program Files';
    const programFilesX86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)';
    const localAppData = process.env['LOCALAPPDATA'] || '';
    candidates.push(
      path.join(programFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(programFilesX86, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Chromium', 'Application', 'chrome.exe'),
    );
  }

  // Also try `which` on unix
  if (platform !== 'win32') {
    for (const cmd of ['chromium', 'chromium-browser', 'google-chrome']) {
      try {
        const p = execSync(`which ${cmd}`, { encoding: 'utf8' }).trim();
        if (p && !candidates.includes(p)) candidates.unshift(p);
      } catch (_) {}
    }
  }

  for (const c of candidates) {
    if (fs.existsSync(c)) {
      ok(`Found: ${c}`);
      return c;
    }
  }

  fail('No Chromium/Chrome found.');
  log('');
  log('Install Chromium:');
  if (platform === 'darwin') {
    log('  brew install --cask chromium');
    log('  # or download from https://www.chromium.org/getting-involved/download-chromium/');
  } else if (platform === 'linux') {
    log('  sudo apt install chromium-browser   # Debian/Ubuntu');
    log('  sudo dnf install chromium           # Fedora');
    log('  # or download from https://www.chromium.org/getting-involved/download-chromium/');
  } else {
    log('  Download from https://www.chromium.org/getting-involved/download-chromium/');
  }
  log('');
  log('Why Chromium over Chrome?');
  log('  Chrome auto-updates and may break automation unexpectedly.');
  log('  Chromium gives you version control. But Chrome works too if you prefer.');
  return null;
}

// ─── Step 2: Check puppeteer-core ───

function checkPuppeteer() {
  log('Step 2/4: Checking puppeteer-core...');

  const searchPaths = [
    path.join('/tmp', 'node_modules'),
    path.join(os.homedir(), 'node_modules'),
    ...module.paths,
  ];

  for (const p of searchPaths) {
    const modPath = path.join(p, 'puppeteer-core');
    if (fs.existsSync(modPath)) {
      ok(`Found at ${modPath}`);
      return p;
    }
  }

  fail('puppeteer-core not found.');
  log('');
  log('Install it:');
  log('  npm install -g puppeteer-core');
  log('  # or install to /tmp for quick use:');
  log('  cd /tmp && npm init -y && npm install puppeteer-core');
  log('');
  log('Then set NODE_PATH so scripts can find it:');
  log('  export NODE_PATH=/tmp/node_modules');

  // Offer auto-install
  log('');
  log('Auto-installing to /tmp/node_modules ...');
  try {
    execSync('cd /tmp && npm init -y 2>/dev/null; npm install puppeteer-core 2>&1', {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    ok('puppeteer-core installed to /tmp/node_modules');
    return '/tmp/node_modules';
  } catch (e) {
    fail(`Auto-install failed: ${e.message}`);
    log('Please install manually and re-run setup.');
    return null;
  }
}

// ─── Step 3: Launch Chromium ───

function isPortOpen(port) {
  return new Promise((resolve) => {
    const sock = new net.Socket();
    sock.setTimeout(1000);
    sock.on('connect', () => { sock.destroy(); resolve(true); });
    sock.on('error', () => { sock.destroy(); resolve(false); });
    sock.on('timeout', () => { sock.destroy(); resolve(false); });
    sock.connect(port, '127.0.0.1');
  });
}

async function launchChromium(chromiumPath) {
  log(`Step 3/4: Launching Chromium on port ${args.port}...`);

  const portOpen = await isPortOpen(args.port);
  if (portOpen) {
    ok(`Port ${args.port} already in use. Chromium may already be running.`);
    // Verify it's actually Chromium CDP
    try {
      const http = require('http');
      const data = await new Promise((resolve, reject) => {
        http.get(`http://localhost:${args.port}/json/version`, (res) => {
          let body = '';
          res.on('data', (d) => body += d);
          res.on('end', () => resolve(body));
        }).on('error', reject);
      });
      const info = JSON.parse(data);
      ok(`Connected: ${info.Browser || 'unknown browser'}`);
      return true;
    } catch (_) {
      fail(`Port ${args.port} is open but doesn't respond to CDP. Something else is using it.`);
      return false;
    }
  }

  // Create profile directory
  if (!fs.existsSync(args.profile)) {
    fs.mkdirSync(args.profile, { recursive: true });
    info(`Created profile directory: ${args.profile}`);
  }

  const launchArgs = [
    `--remote-debugging-port=${args.port}`,
    `--user-data-dir=${args.profile}`,
    '--no-first-run',
    '--no-default-browser-check',
  ];

  log(`  Launching: ${chromiumPath}`);
  log(`  Profile:   ${args.profile}`);
  log(`  CDP port:  ${args.port}`);

  const child = spawn(chromiumPath, launchArgs, {
    detached: true,
    stdio: 'ignore',
  });
  child.unref();

  // Wait for CDP to be ready
  for (let i = 0; i < 15; i++) {
    await new Promise(r => setTimeout(r, 1000));
    if (await isPortOpen(args.port)) {
      ok(`Chromium launched (PID ${child.pid}), CDP ready on port ${args.port}`);
      return true;
    }
  }

  fail('Chromium launched but CDP port not responding after 15s.');
  log('Try launching manually:');
  log(`  "${chromiumPath}" --remote-debugging-port=${args.port} --user-data-dir=${args.profile}`);
  return false;
}

// ─── Step 4: Check X login ───

async function checkLogin(nodePath) {
  log('Step 4/4: Checking X login status...');

  // Dynamically load puppeteer
  if (nodePath) module.paths.unshift(nodePath);
  const pptr = require('puppeteer-core');

  let browser, page;
  try {
    browser = await pptr.connect({ browserURL: `http://localhost:${args.port}` });
    page = await browser.newPage();
    await page.goto('https://x.com/home', { waitUntil: 'networkidle2', timeout: 20000 });
    await new Promise(r => setTimeout(r, 2000));

    // Check if redirected to login
    const url = page.url();
    if (url.includes('/login') || url.includes('/i/flow/login')) {
      fail('Not logged in to X.');
      log('');
      log('Please log in manually:');
      log(`  1. Open http://localhost:${args.port} in your browser (or use the Chromium window)`);
      log('  2. Navigate to https://x.com and log in with your account');
      log('  3. Re-run this setup to verify');
      await page.close();
      browser.disconnect();
      return null;
    }

    // Try to get handle
    const handle = await page.evaluate(() => {
      const btn = document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"]');
      if (!btn) return null;
      const match = btn.textContent?.match(/@\w+/);
      return match ? match[0] : null;
    }).catch(() => null);

    if (handle) {
      ok(`Logged in as ${handle}`);
    } else {
      ok('Logged in (handle not detected, but page loaded)');
    }

    await page.close();
    browser.disconnect();
    return handle || '__logged_in__';
  } catch (e) {
    fail(`Login check failed: ${e.message}`);
    if (page) try { await page.close(); } catch (_) {}
    if (browser) try { browser.disconnect(); } catch (_) {}
    return null;
  }
}

// ─── Main ───

(async () => {
  log('X CDP Skill Setup');
  log('=================');
  log('');

  // Step 1
  const chromiumPath = findChromium();
  if (!chromiumPath) {
    log('');
    log('Fix: Install Chromium, then re-run setup.');
    process.exit(1);
  }
  log('');

  // Step 2
  const nodePath = checkPuppeteer();
  if (!nodePath) {
    process.exit(1);
  }
  log('');

  // Step 3
  const launched = await launchChromium(chromiumPath);
  if (!launched) {
    process.exit(1);
  }
  log('');

  // Step 4
  const handle = await checkLogin(nodePath);
  log('');

  if (handle) {
    log('🎉 Setup complete! All checks passed.');
    log('');
    log('Quick test:');
    log(`  NODE_PATH=${nodePath} node scripts/post-tweet.js "Hello from X CDP!" --port ${args.port} --dry-run`);
  } else {
    log('⚠️  Almost there. Log in to X in the Chromium window, then re-run:');
    log(`  node scripts/setup.js --port ${args.port} --profile ${args.profile}`);
  }
})();
