#!/usr/bin/env node
/**
 * record-proof.js — Record video proof of a working feature
 *
 * Usage:
 *   node record-proof.js --spec proof-spec.yaml --output ./proof-artifacts
 *   node record-proof.js --start "npm run dev" --port 3000 --url http://localhost:3000 --goto "/" --screenshot "home" --output ./artifacts
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const yaml = require('yaml');

const args = process.argv.slice(2);

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && idx + 1 < args.length ? args[idx + 1] : null;
}

function getAllArgs(name) {
  const results = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === `--${name}` && i + 1 < args.length) results.push(args[++i]);
  }
  return results;
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function cleanup(serverProc) {
  if (serverProc) {
    try { process.kill(-serverProc.pid, 'SIGTERM'); } catch {}
  }
}

async function waitForPort(port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      execSync(`curl -sf -o /dev/null http://localhost:${port}`, { timeout: 5000 });
      return true;
    } catch {
      await sleep(1000);
    }
  }
  return false;
}

async function main() {
  const specPath = getArg('spec');
  const outputDir = getArg('output') || './proof-artifacts';
  let spec;

  if (specPath) {
    const raw = fs.readFileSync(specPath, 'utf8');
    spec = yaml.parse(raw);
    if (spec.proof) spec = spec.proof;
  } else {
    spec = {
      start_command: getArg('start') || null,
      start_port: parseInt(getArg('port') || '3000'),
      base_url: getArg('url') || `http://localhost:${getArg('port') || '3000'}`,
      steps: [],
      timeout: parseInt(getArg('timeout') || '60000'),
    };
    for (const g of getAllArgs('goto')) spec.steps.push({ goto: g });
    for (const s of getAllArgs('screenshot')) spec.steps.push({ screenshot: s });
    for (const c of getAllArgs('click')) spec.steps.push({ click: c });
  }

  const screenshotDir = path.join(outputDir, 'screenshots');
  fs.mkdirSync(screenshotDir, { recursive: true });

  // --- Start server (if configured) ---
  let serverProc = null;
  if (spec.start_command) {
    const port = spec.start_port || 3000;
    const startTimeout = spec.start_timeout || spec.timeout || 60000;

    console.log(`[proof] Starting: ${spec.start_command}`);
    serverProc = spawn('sh', ['-c', spec.start_command], {
      stdio: 'pipe',
      detached: true,
      env: { ...process.env, BROWSER: 'none', PORT: String(port) },
    });
    serverProc.stdout?.on('data', d => process.stdout.write(`[server] ${d}`));
    serverProc.stderr?.on('data', d => process.stderr.write(`[server] ${d}`));
    serverProc.on('error', err => console.error(`[server] spawn error: ${err.message}`));

    console.log(`[proof] Waiting for port ${port} (timeout: ${Math.round(startTimeout / 1000)}s)...`);
    const ready = await waitForPort(port, startTimeout);
    if (!ready) {
      console.error(`[proof] Server did not become ready on port ${port} within ${Math.round(startTimeout / 1000)}s`);
      cleanup(serverProc);
      process.exit(1);
    }
    console.log(`[proof] Server ready on port ${port}`);
  }

  // --- Launch browser ---
  const vp = {
    width: spec.viewport?.width || 1280,
    height: spec.viewport?.height || 720,
  };

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: vp,
    recordVideo: { dir: outputDir, size: vp },
  });
  const page = await context.newPage();

  const consoleLogs = [];
  page.on('console', msg => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => consoleLogs.push(`[error] ${err.message}`));

  const baseUrl = spec.base_url || `http://localhost:${spec.start_port || 3000}`;
  const steps = spec.steps || [];
  const results = [];

  console.log(`[proof] Running ${steps.length} steps (viewport: ${vp.width}x${vp.height})...`);

  // --- Execute steps ---
  try {
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      const n = i + 1;

      if (step.goto) {
        const url = step.goto.startsWith('http') ? step.goto : `${baseUrl}${step.goto}`;
        console.log(`[proof] Step ${n}: goto ${url}`);
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
        results.push({ step: n, action: 'goto', target: step.goto, status: 'ok' });

      } else if (step.click) {
        console.log(`[proof] Step ${n}: click "${step.click}"`);
        await page.click(step.click, { timeout: 10000 });
        results.push({ step: n, action: 'click', target: step.click, status: 'ok' });

      } else if (step.fill) {
        const { selector, value } = step.fill;
        console.log(`[proof] Step ${n}: fill ${selector}`);
        await page.fill(selector, value, { timeout: 10000 });
        results.push({ step: n, action: 'fill', target: selector, status: 'ok' });

      } else if (step.type) {
        const { selector, text } = step.type;
        console.log(`[proof] Step ${n}: type into ${selector}`);
        await page.type(selector, text, { timeout: 10000 });
        results.push({ step: n, action: 'type', target: selector, status: 'ok' });

      } else if (step.wait) {
        console.log(`[proof] Step ${n}: wait ${step.wait}ms`);
        await sleep(step.wait);
        results.push({ step: n, action: 'wait', target: `${step.wait}ms`, status: 'ok' });

      } else if (step.screenshot) {
        const name = step.screenshot;
        const filepath = path.join(screenshotDir, `${name}.png`);
        console.log(`[proof] Step ${n}: screenshot → ${name}.png`);
        await page.screenshot({ path: filepath, fullPage: false });
        results.push({ step: n, action: 'screenshot', target: name, status: 'ok', path: filepath });

      } else if (step.scroll) {
        const px = step.scroll === 'up' ? -500 : 500;
        console.log(`[proof] Step ${n}: scroll ${step.scroll}`);
        await page.mouse.wheel(0, px);
        await sleep(500);
        results.push({ step: n, action: 'scroll', target: step.scroll, status: 'ok' });

      } else if (step.assert_visible) {
        console.log(`[proof] Step ${n}: assert_visible "${step.assert_visible}"`);
        await page.waitForSelector(step.assert_visible, { state: 'visible', timeout: 10000 });
        results.push({ step: n, action: 'assert_visible', target: step.assert_visible, status: 'ok' });

      } else if (step.assert_url) {
        const current = page.url();
        console.log(`[proof] Step ${n}: assert_url "${step.assert_url}" (current: ${current})`);
        if (!current.includes(step.assert_url)) {
          throw new Error(`URL assertion failed: expected "${step.assert_url}" in "${current}"`);
        }
        results.push({ step: n, action: 'assert_url', target: step.assert_url, status: 'ok' });

      } else {
        console.warn(`[proof] Step ${n}: unknown action`, JSON.stringify(step));
        results.push({ step: n, action: 'unknown', target: JSON.stringify(step), status: 'skipped' });
      }
    }
  } catch (err) {
    console.error(`[proof] Step failed: ${err.message}`);
    try {
      await page.screenshot({ path: path.join(screenshotDir, 'FAILURE.png'), fullPage: true });
    } catch {}
    results.push({ action: 'error', message: err.message, status: 'failed' });
  }

  // --- Finalize ---
  await context.close();
  await browser.close();

  fs.writeFileSync(path.join(outputDir, 'console.log'), consoleLogs.join('\n'));

  // Rename Playwright's hashed video file
  const videoFiles = fs.readdirSync(outputDir).filter(f => f.endsWith('.webm'));
  let hasVideo = false;
  if (videoFiles.length > 0) {
    const src = path.join(outputDir, videoFiles[0]);
    const dest = path.join(outputDir, 'video.webm');
    if (src !== dest) fs.renameSync(src, dest);
    hasVideo = true;
    console.log(`[proof] Video saved: ${dest}`);

    try {
      const mp4 = path.join(outputDir, 'video.mp4');
      execSync(`ffmpeg -y -i "${dest}" -c:v libx264 -crf 23 -preset fast -an "${mp4}" 2>/dev/null`);
      console.log(`[proof] MP4 converted: ${mp4}`);
    } catch {
      console.warn('[proof] ffmpeg not available or conversion failed — .webm still available');
    }
  }

  // --- Generate summary ---
  const failed = results.some(r => r.status === 'failed');
  const screenshots = fs.readdirSync(screenshotDir).filter(f => f.endsWith('.png'));

  let summary = `# Proof of Work\n\n`;
  summary += `**Status:** ${failed ? '❌ FAILED' : '✅ PASSED'}\n`;
  summary += `**Date:** ${new Date().toISOString()}\n`;
  summary += `**Steps:** ${results.length}\n\n`;
  summary += `## Steps\n\n`;
  for (const r of results) {
    const icon = r.status === 'ok' ? '✅' : r.status === 'failed' ? '❌' : '⏭️';
    summary += `${icon} **${r.action}** → ${r.target || r.message || ''}\n`;
  }
  summary += `\n## Artifacts\n\n`;
  if (hasVideo) summary += `- Video: \`video.webm\` / \`video.mp4\`\n`;
  for (const s of screenshots) summary += `- Screenshot: \`screenshots/${s}\`\n`;
  summary += `- Console log: \`console.log\`\n`;

  fs.writeFileSync(path.join(outputDir, 'proof-summary.md'), summary);
  console.log(`[proof] Summary: ${path.join(outputDir, 'proof-summary.md')}`);
  console.log(`[proof] ${failed ? 'FAILED' : 'PASSED'} — ${results.length} steps executed`);

  cleanup(serverProc);
  process.exit(failed ? 1 : 0);
}

main().catch(err => {
  console.error('[proof] Fatal:', err.message);
  process.exit(1);
});
