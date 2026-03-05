#!/usr/bin/env node
/**
 * CAPTCHA Relay v2 — Human-in-the-loop CAPTCHA solving
 *
 * Two modes:
 *   screenshot (default) — Grid overlay screenshot, human replies with cell numbers, clicks injected.
 *                           No network infrastructure needed.
 *   relay                 — Detects CAPTCHA type + sitekey, serves real widget on relay page,
 *                           human solves natively, token injected via CDP.
 *                           Requires Tailscale or tunnel for network access.
 *
 * Usage:
 *   node index.js                            # screenshot mode (default)
 *   node index.js --mode screenshot          # explicit screenshot mode
 *   node index.js --mode relay               # token relay mode
 *   node index.js --screenshot               # alias for --mode screenshot
 *   node index.js --mode relay --no-tunnel   # relay via Tailscale/LAN
 *
 * As module:
 *   const { solveCaptcha, solveCaptchaScreenshot } = require('./index');
 */

const { detectCaptcha } = require('./lib/detect');
const { createRelayServer } = require('./lib/server');
const { startTunnel, stopTunnel, getLocalIp, getTailscaleIp } = require('./lib/tunnel');
const { injectToken } = require('./lib/inject');
const { captureAndAnnotate, injectGridClicks } = require('./fallback/screenshot');

async function solveCaptcha(opts = {}) {
  const {
    cdpPort = 18800,
    timeout = 120000,
    inject = true,
    useTunnel = true,
    // Allow manual override
    type: overrideType,
    sitekey: overrideSitekey,
    pageUrl: overridePageUrl,
  } = opts;

  const log = (msg) => process.stderr.write(`[captcha-relay] ${msg}\n`);

  // Step 1: Detect CAPTCHA
  log('Detecting CAPTCHA...');
  let detection;
  if (overrideType && overrideSitekey) {
    detection = { type: overrideType, sitekey: overrideSitekey, pageUrl: overridePageUrl };
  } else {
    detection = await detectCaptcha(cdpPort);
  }

  if (!detection.type || !detection.sitekey) {
    throw new Error('No CAPTCHA detected on page. Detection result: ' + JSON.stringify(detection));
  }

  log(`Found ${detection.type} with sitekey ${detection.sitekey.substring(0, 20)}...`);

  // Step 2: Start relay server
  log('Starting relay server...');
  const relay = await createRelayServer({
    type: detection.type,
    sitekey: detection.sitekey,
    pageUrl: detection.pageUrl,
    timeout,
  });

  log(`Relay server on port ${relay.port}`);

  // Step 3: Get public URL
  let tunnel = null;
  let url;
  if (useTunnel) {
    log('Starting tunnel...');
    tunnel = await startTunnel(relay.port);
    url = tunnel.url;
    log(`Public URL: ${url}`);
  } else {
    const tsIp = getTailscaleIp();
    const ip = tsIp || getLocalIp();
    url = `http://${ip}:${relay.port}`;
    log(`${tsIp ? 'Tailscale' : 'Local'} URL: ${url}`);
  }

  // Step 4: Output URL for notification (caller sends to Telegram)
  const result = {
    type: detection.type,
    sitekey: detection.sitekey,
    pageUrl: detection.pageUrl,
    relayUrl: url,
    port: relay.port,
    isLocal: tunnel ? tunnel.isLocal : true,
  };

  // Output URL immediately so caller can send notification
  console.log(JSON.stringify({ event: 'ready', ...result }));

  // Step 5: Wait for token
  log('Waiting for human to solve CAPTCHA...');
  const token = await relay.waitForToken();

  if (!token) {
    stopTunnel(tunnel);
    throw new Error('CAPTCHA solving timed out');
  }

  log(`Token received (${token.length} chars)`);

  // Step 6: Inject token
  if (inject) {
    log('Injecting token...');
    const injectResult = await injectToken({
      type: detection.type,
      token,
      cdpPort,
    });
    log(`Injection result: ${injectResult}`);
    result.injected = true;
    result.injectionMethod = injectResult;
  }

  result.token = token;
  result.solved = true;

  // Cleanup
  stopTunnel(tunnel);

  console.log(JSON.stringify({ event: 'solved', ...result }));
  return result;
}

/**
 * Screenshot-based fallback for when token relay can't work
 */
async function solveCaptchaScreenshot(opts = {}) {
  const { cdpPort = 18800 } = opts;
  const log = (msg) => process.stderr.write(`[captcha-relay] ${msg}\n`);

  log('Using screenshot fallback...');
  const capture = await captureAndAnnotate(cdpPort);

  console.log(JSON.stringify({
    event: 'screenshot-ready',
    imagePath: capture.imagePath,
    prompt: capture.prompt,
    rows: capture.rows,
    cols: capture.cols,
    totalCells: capture.totalCells,
  }));

  return capture;
}

// CLI mode
if (require.main === module) {
  const args = process.argv.slice(2);
  const getArg = (name, def) => {
    const i = args.indexOf(name);
    return i >= 0 ? args[i + 1] : def;
  };
  const hasFlag = (name) => args.includes(name);

  // Determine mode: --mode screenshot|relay, --screenshot as alias
  const explicitMode = getArg('--mode', null);
  const useScreenshot = hasFlag('--screenshot');
  const mode = explicitMode || (useScreenshot ? 'screenshot' : 'screenshot'); // default: screenshot

  const opts = {
    cdpPort: parseInt(getArg('--cdp-port', '18800')),
    timeout: parseInt(getArg('--timeout', '120')) * 1000,
    inject: !hasFlag('--no-inject'),
    useTunnel: !hasFlag('--no-tunnel'),
  };

  const run = mode === 'relay' ? solveCaptcha : solveCaptchaScreenshot;

  run(opts).catch(e => {
    console.error(JSON.stringify({ event: 'error', error: e.message }));
    process.exit(1);
  });
}

module.exports = { solveCaptcha, solveCaptchaScreenshot, injectGridClicks };
