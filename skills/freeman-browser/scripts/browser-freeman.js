/**
 * browser-freeman.js — Freeman Browser for AI Agents
 *
 * Stealth browser. Appears as iPhone 15 Pro or Desktop Chrome to every website.
 *
 * Usage:
 *   const { launchFreeman } = require('./browser-freeman');
 *   const { browser, page } = await launchFreeman({ mobile: true });
 */

const fs = require('fs');
const path = require('path');

// ─── PLAYWRIGHT RESOLVER ──────────────────────────────────────────────────────

function _requirePlaywright() {
  const tries = [
    () => require('playwright'),
    () => require(path.resolve(process.cwd(), 'node_modules', 'playwright')),
    () => require(path.resolve(__dirname, '..', 'node_modules', 'playwright')),
    () => require(path.resolve(__dirname, '..', '..', 'playwright')),
    () => require(path.resolve(process.env.HOME || '/root', '.openclaw/workspace/node_modules/playwright'))
  ];
  for (const fn of tries) {
    try { return fn(); } catch (_) {}
  }
  throw new Error(
    '[freeman-browser] playwright not found.\n' +
    'Run: npm install playwright && npx playwright install chromium'
  );
}

const { chromium } = _requirePlaywright();

// ─── CONFIGURATION ───────────────────────────────────────────────────────────

let userConfig = {};
try {
  const configPath = path.resolve(process.cwd(), process.env.BROWSER_CONFIG || 'browser.json');
  if (fs.existsSync(configPath)) {
    userConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
} catch (e) {
  console.warn('[freeman-browser] Could not load browser.json:', e.message);
}

// ─── DEVICE PROFILES ─────────────────────────────────────────────────────────

function buildDevice(mobile) {
  const locale = userConfig.locale || 'en-US';
  const timezoneId = userConfig.timezoneId || 'America/New_York';
  const geolocation = userConfig.geolocation || { latitude: 40.7128, longitude: -74.006, accuracy: 50 };
  const acceptLanguage = locale + (locale === 'en-US' ? ',en;q=0.9' : ',en-US;q=0.9,en;q=0.8');

  if (mobile) {
    return {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
      viewport: { width: 393, height: 852 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      locale,
      timezoneId,
      geolocation,
      colorScheme: 'light',
      extraHTTPHeaders: {
        'Accept-Language': acceptLanguage,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
      },
    };
  }

  return {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    viewport: { width: 1440, height: 900 },
    locale,
    timezoneId,
    geolocation,
    colorScheme: 'light',
    extraHTTPHeaders: {
      'Accept-Language': acceptLanguage,
      'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
    },
  };
}

// ─── HUMAN BEHAVIOR ───────────────────────────────────────────────────────────

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const rand  = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

async function humanMouseMove(page, toX, toY, fromX = null, fromY = null) {
  const startX = fromX ?? rand(100, 300);
  const startY = fromY ?? rand(200, 600);
  const cp1x = startX + rand(-80, 80), cp1y = startY + rand(-60, 60);
  const cp2x = toX   + rand(-50, 50), cp2y = toY   + rand(-40, 40);
  const steps = rand(12, 25);
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = Math.round(Math.pow(1-t,3)*startX + 3*Math.pow(1-t,2)*t*cp1x + 3*(1-t)*t*t*cp2x + t*t*t*toX);
    const y = Math.round(Math.pow(1-t,3)*startY + 3*Math.pow(1-t,2)*t*cp1y + 3*(1-t)*t*t*cp2y + t*t*t*toY);
    await page.mouse.move(x, y);
    await sleep(t < 0.2 || t > 0.8 ? rand(8, 20) : rand(2, 8));
  }
}

async function humanClick(page, x, y) {
  await humanMouseMove(page, x, y);
  await sleep(rand(50, 180));
  await page.mouse.down();
  await sleep(rand(40, 100));
  await page.mouse.up();
  await sleep(rand(100, 300));
}

async function humanType(page, selector, text) {
  const el = await page.$(selector);
  if (!el) throw new Error(`Element not found: ${selector}`);
  const box = await el.boundingBox();
  if (box) await humanClick(page, box.x + box.width / 2, box.y + box.height / 2);
  await sleep(rand(200, 500));
  for (const char of text) {
    await page.keyboard.type(char);
    await sleep(rand(60, 220));
    if (Math.random() < 0.08) await sleep(rand(400, 900));
  }
  await sleep(rand(200, 400));
}

async function humanScroll(page, direction = 'down', amount = null) {
  const scrollAmount = amount || rand(200, 600);
  const delta = direction === 'down' ? scrollAmount : -scrollAmount;
  const vp = page.viewportSize();
  await humanMouseMove(page, rand(100, vp.width - 100), rand(200, vp.height - 200));
  const steps = rand(4, 10);
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, delta / steps + rand(-5, 5));
    await sleep(rand(30, 80));
  }
  await sleep(rand(200, 800));
}

async function humanRead(page, minMs = 1500, maxMs = 4000) {
  await sleep(rand(minMs, maxMs));
  if (Math.random() < 0.3) await humanScroll(page, 'down', rand(50, 150));
}

// ─── 2CAPTCHA SOLVER ──────────────────────────────────────────────────────────

async function solveCaptcha(page, opts = {}) {
  const {
    apiKey   = process.env.TWOCAPTCHA_KEY,
    action   = 'verify',
    minScore = 0.7,
    timeout  = 120000,
    verbose  = false,
  } = opts;

  if (!apiKey) throw new Error('[2captcha] No API key. Set TWOCAPTCHA_KEY env or pass opts.apiKey');

  const log = verbose ? (...a) => console.log('[2captcha]', ...a) : () => {};
  const pageUrl = page.url();

  const detected = await page.evaluate(() => {
    const rc = document.querySelector('.g-recaptcha, [data-sitekey]');
    if (rc) {
      const sitekey = rc.getAttribute('data-sitekey') || rc.getAttribute('data-key');
      const version = rc.getAttribute('data-version') || (typeof window.grecaptcha !== 'undefined' && 'v2');
      return { type: 'recaptcha', sitekey, version: version === 'v3' ? 'v3' : 'v2' };
    }
    const hc = document.querySelector('.h-captcha, [data-hcaptcha-sitekey]');
    if (hc) return { type: 'hcaptcha', sitekey: hc.getAttribute('data-sitekey') || hc.getAttribute('data-hcaptcha-sitekey') };
    const ts = document.querySelector('.cf-turnstile, [data-cf-turnstile-sitekey]');
    if (ts) return { type: 'turnstile', sitekey: ts.getAttribute('data-sitekey') || ts.getAttribute('data-cf-turnstile-sitekey') };
    const scripts = [...document.scripts].map(s => s.src + s.textContent).join(' ');
    const rcMatch = scripts.match(/(?:sitekey|data-sitekey)['":\s]+([A-Za-z0-9_-]{40,})/);
    if (rcMatch) return { type: 'recaptcha', sitekey: rcMatch[1], version: 'v2' };
    return null;
  });

  if (!detected || !detected.sitekey) throw new Error('[2captcha] No captcha detected on page.');
  log(`Detected ${detected.type} v${detected.version || ''}`, detected.sitekey.slice(0, 20) + '...');

  let submitUrl = `https://2captcha.com/in.php?key=${apiKey}&json=1&pageurl=${encodeURIComponent(pageUrl)}&googlekey=${encodeURIComponent(detected.sitekey)}`;
  if (detected.type === 'recaptcha') {
    submitUrl += `&method=userrecaptcha`;
    if (detected.version === 'v3') submitUrl += `&version=v3&action=${action}&min_score=${minScore}`;
  } else if (detected.type === 'hcaptcha') {
    submitUrl += `&method=hcaptcha&sitekey=${encodeURIComponent(detected.sitekey)}`;
  } else if (detected.type === 'turnstile') {
    submitUrl += `&method=turnstile&sitekey=${encodeURIComponent(detected.sitekey)}`;
  }

  const submitResp = await fetch(submitUrl);
  const submitData = await submitResp.json();
  if (!submitData.status || submitData.status !== 1) throw new Error(`[2captcha] Submit failed: ${JSON.stringify(submitData)}`);
  const taskId = submitData.request;
  log(`Task submitted: ${taskId} — waiting for workers...`);

  let token = null;
  const maxAttempts = Math.floor(timeout / 5000);
  for (let i = 0; i < maxAttempts; i++) {
    await sleep(i === 0 ? 15000 : 5000);
    const pollResp = await fetch(`https://2captcha.com/res.php?key=${apiKey}&action=get&id=${taskId}&json=1`);
    const pollData = await pollResp.json();
    if (pollData.status === 1) { token = pollData.request; log('✅ Solved!'); break; }
    if (pollData.request !== 'CAPCHA_NOT_READY') throw new Error(`[2captcha] Poll error: ${JSON.stringify(pollData)}`);
    log(`⏳ Attempt ${i + 1}/${maxAttempts}...`);
  }
  if (!token) throw new Error('[2captcha] Timeout waiting for captcha solution');

  await page.evaluate(({ type, token }) => {
    if (type === 'recaptcha' || type === 'turnstile') {
      const ta = document.querySelector('#g-recaptcha-response, [name="g-recaptcha-response"]');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
      try {
        const clients = window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients;
        if (clients) Object.values(clients).forEach(c => Object.values(c).forEach(w => { if (w && typeof w.callback === 'function') w.callback(token); }));
      } catch (_) {}
    }
    if (type === 'hcaptcha') {
      const ta = document.querySelector('[name="h-captcha-response"], #h-captcha-response');
      if (ta) { ta.style.display = 'block'; ta.value = token; ta.dispatchEvent(new Event('change', { bubbles: true })); }
    }
    if (type === 'turnstile') {
      const inp = document.querySelector('[name="cf-turnstile-response"]');
      if (inp) { inp.value = token; inp.dispatchEvent(new Event('change', { bubbles: true })); }
    }
  }, { type: detected.type, token });

  log('✅ Token injected');
  return { token, type: detected.type, sitekey: detected.sitekey };
}

// ─── LAUNCH ───────────────────────────────────────────────────────────────────

async function launchFreeman(opts = {}) {
  const {
    mobile   = true,
    headless = true,
  } = opts;

  const device = buildDevice(mobile);

  const browser = await chromium.launch({
    headless,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      '--disable-blink-features=AutomationControlled',
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-web-security',
    ],
  });

  const ctxOpts = {
    ...device,
    ignoreHTTPSErrors: true,
    permissions: ['geolocation', 'notifications'],
  };

  const ctx = await browser.newContext(ctxOpts);

  await ctx.addInitScript((m) => {
    Object.defineProperty(navigator, 'webdriver',           { get: () => false });
    Object.defineProperty(navigator, 'maxTouchPoints',      { get: () => m.mobile ? 5 : 0 });
    Object.defineProperty(navigator, 'platform',            { get: () => m.mobile ? 'iPhone' : 'Win32' });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => m.mobile ? 6 : 8 });
    Object.defineProperty(navigator, 'language',            { get: () => m.locale });
    Object.defineProperty(navigator, 'languages',           { get: () => [m.locale, 'en'] });
    if (m.mobile) {
      Object.defineProperty(screen, 'width',       { get: () => 393 });
      Object.defineProperty(screen, 'height',      { get: () => 852 });
      Object.defineProperty(screen, 'availWidth',  { get: () => 393 });
      Object.defineProperty(screen, 'availHeight', { get: () => 852 });
    }
    if (navigator.connection) {
      try {
        Object.defineProperty(navigator.connection, 'effectiveType', { get: () => '4g' });
      } catch (_) {}
    }
  }, { mobile, locale: device.locale });

  const page = await ctx.newPage();

  return { browser, ctx, page, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand };
}

// ─── SHADOW DOM UTILITIES ─────────────────────────────────────────────────────

async function shadowQuery(page, selector) {
  return page.evaluate((sel) => {
    function q(root, s) {
      const el = root.querySelector(s); if (el) return el;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = q(n.shadowRoot, s); if (f) return f; }
    }
    return q(document, sel);
  }, selector);
}

async function shadowFill(page, selector, value) {
  await page.evaluate(({ sel, val }) => {
    function q(root, s) {
      const el = root.querySelector(s); if (el) return el;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = q(n.shadowRoot, s); if (f) return f; }
    }
    const el = q(document, sel);
    if (!el) throw new Error('shadowFill: not found: ' + sel);
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input',  { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, { sel: selector, val: value });
}

async function shadowClickButton(page, buttonText) {
  await page.evaluate((text) => {
    function find(root) {
      for (const b of root.querySelectorAll('button')) if (b.textContent.trim() === text) return b;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = find(n.shadowRoot); if (f) return f; }
    }
    const btn = find(document);
    if (!btn) throw new Error('shadowClickButton: not found: ' + text);
    btn.click();
  }, buttonText);
}

async function dumpInteractiveElements(page) {
  return page.evaluate(() => {
    const res = [];
    function collect(root) {
      for (const el of root.querySelectorAll('input,textarea,button,select,[contenteditable]')) {
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0)
          res.push({ tag: el.tagName, name: el.name || '', id: el.id || '', type: el.type || '', text: el.textContent?.trim().slice(0, 25) || '', placeholder: el.placeholder?.slice(0, 25) || '' });
      }
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) collect(n.shadowRoot);
    }
    collect(document);
    return res;
  });
}

// ─── RICH TEXT EDITOR UTILITIES ───────────────────────────────────────────────

async function pasteIntoEditor(page, editorSelector, text) {
  const el = await page.$(editorSelector);
  if (!el) throw new Error('pasteIntoEditor: editor not found: ' + editorSelector);
  await el.click();
  await sleep(300);
  await page.evaluate((t) => {
    const ta = document.createElement('textarea');
    ta.value = t;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }, text);
  await page.keyboard.press('Control+a');
  await sleep(100);
  await page.keyboard.press('Control+v');
  await sleep(500);
}

// ─── EXPORTS ──────────────────────────────────────────────────────────────────

module.exports = {
  launchFreeman,
  humanClick, humanMouseMove, humanType, humanScroll, humanRead,
  solveCaptcha,
  shadowQuery, shadowFill, shadowClickButton, dumpInteractiveElements,
  pasteIntoEditor,
  buildDevice,
  sleep, rand,
};

// ─── QUICK TEST ───────────────────────────────────────────────────────────────
if (require.main === module) {
  console.log(`🧪 Testing Freeman Browser`);
  (async () => {
    const { browser, page } = await launchFreeman({ mobile: true });
    await page.goto('https://ipinfo.io/json', { waitUntil: 'domcontentloaded', timeout: 30000 });
    const info = JSON.parse(await page.textContent('body'));
    console.log(`✅ IP:      ${info.ip}`);
    console.log(`✅ Country: ${info.country} (${info.city})`);
    console.log(`✅ Org:     ${info.org}`);
    console.log(`✅ TZ:      ${info.timezone}`);
    const ua = await page.evaluate(() => navigator.userAgent);
    console.log(`✅ UA:      ${ua.slice(0, 80)}...`);
    await browser.close();
    console.log('\n🎉 Freeman Browser is ready.');
  })().catch(console.error);
}
