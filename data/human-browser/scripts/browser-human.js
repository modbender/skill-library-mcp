/**
 * browser-human.js — Human Browser for AI Agents v4.0.0
 *
 * Stealth browser with residential proxies from 10+ countries.
 * Appears as iPhone 15 Pro or Desktop Chrome to every website.
 * Bypasses Cloudflare, DataDome, PerimeterX out of the box.
 *
 * Get credentials: https://humanbrowser.cloud
 * Support: https://t.me/virixlabs
 *
 * Usage:
 *   const { launchHuman, getTrial } = require('./browser-human');
 *   const { browser, page } = await launchHuman({ country: 'us' });
 *
 * Proxy config via env vars:
 *   HB_PROXY_PROVIDER  — decodo | brightdata | iproyal | nodemaven (default: decodo)
 *   HB_PROXY_USER      — proxy username
 *   HB_PROXY_PASS      — proxy password
 *   HB_PROXY_SERVER    — full override: http://host:port
 *   HB_PROXY_COUNTRY   — country code: ro, us, de, gb, fr, nl, sg... (default: ro)
 *   HB_PROXY_SESSION   — Decodo sticky port 10001-49999 (unique IP per user)
 *   HB_NO_PROXY        — set to "1" to disable proxy entirely
 */

// ─── PLAYWRIGHT RESOLVER ──────────────────────────────────────────────────────
// Works in any context: clawhub install, workspace, Clawster containers

function _requirePlaywright() {
  const tries = [
    () => require('playwright'),
    () => require(`${__dirname}/../node_modules/playwright`),
    () => require(`${__dirname}/../../node_modules/playwright`),
    () => require(`${process.env.HOME || '/root'}/.openclaw/workspace/node_modules/playwright`),
    () => require('./node_modules/playwright'),
  ];
  for (const fn of tries) {
    try { return fn(); } catch (_) {}
  }
  throw new Error(
    '[human-browser] playwright not found.\n' +
    'Run: npm install playwright && npx playwright install chromium'
  );
}

const { chromium } = _requirePlaywright();

// ─── COUNTRY CONFIGS ──────────────────────────────────────────────────────────

const COUNTRY_META = {
  ro: { locale: 'ro-RO', tz: 'Europe/Bucharest',  lat: 44.4268,  lon: 26.1025,   lang: 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7' },
  us: { locale: 'en-US', tz: 'America/New_York',  lat: 40.7128,  lon: -74.006,   lang: 'en-US,en;q=0.9' },
  uk: { locale: 'en-GB', tz: 'Europe/London',     lat: 51.5074,  lon: -0.1278,   lang: 'en-GB,en;q=0.9' },
  gb: { locale: 'en-GB', tz: 'Europe/London',     lat: 51.5074,  lon: -0.1278,   lang: 'en-GB,en;q=0.9' },
  de: { locale: 'de-DE', tz: 'Europe/Berlin',     lat: 52.5200,  lon: 13.4050,   lang: 'de-DE,de;q=0.9,en;q=0.8' },
  nl: { locale: 'nl-NL', tz: 'Europe/Amsterdam',  lat: 52.3676,  lon: 4.9041,    lang: 'nl-NL,nl;q=0.9,en;q=0.8' },
  jp: { locale: 'ja-JP', tz: 'Asia/Tokyo',        lat: 35.6762,  lon: 139.6503,  lang: 'ja-JP,ja;q=0.9,en;q=0.8' },
  fr: { locale: 'fr-FR', tz: 'Europe/Paris',      lat: 48.8566,  lon: 2.3522,    lang: 'fr-FR,fr;q=0.9,en;q=0.8' },
  ca: { locale: 'en-CA', tz: 'America/Toronto',   lat: 43.6532,  lon: -79.3832,  lang: 'en-CA,en;q=0.9' },
  au: { locale: 'en-AU', tz: 'Australia/Sydney',  lat: -33.8688, lon: 151.2093,  lang: 'en-AU,en;q=0.9' },
  sg: { locale: 'en-SG', tz: 'Asia/Singapore',    lat: 1.3521,   lon: 103.8198,  lang: 'en-SG,en;q=0.9' },
  br: { locale: 'pt-BR', tz: 'America/Sao_Paulo', lat: -23.5505, lon: -46.6333,  lang: 'pt-BR,pt;q=0.9,en;q=0.8' },
  in: { locale: 'en-IN', tz: 'Asia/Kolkata',      lat: 28.6139,  lon: 77.2090,   lang: 'en-IN,en;q=0.9,hi;q=0.8' },
};

// ─── DEVICE PROFILES ─────────────────────────────────────────────────────────

function buildDevice(mobile, country = 'ro') {
  const meta = COUNTRY_META[country.toLowerCase()] || COUNTRY_META.ro;

  if (mobile) {
    return {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
      viewport: { width: 393, height: 852 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      locale: meta.locale,
      timezoneId: meta.tz,
      geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
      colorScheme: 'light',
      extraHTTPHeaders: {
        'Accept-Language': meta.lang,
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
    locale: meta.locale,
    timezoneId: meta.tz,
    geolocation: { latitude: meta.lat, longitude: meta.lon, accuracy: 50 },
    colorScheme: 'light',
    extraHTTPHeaders: {
      'Accept-Language': meta.lang,
      'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
    },
  };
}

// ─── PROXY PRESETS ────────────────────────────────────────────────────────────
// ⚠️  defaultUser/defaultPass are ALWAYS null — credentials come from env vars
//     or getTrial(). NEVER hardcode credentials here.

const PROXY_PRESETS = {
  decodo: {
    // Sticky session via port number: each unique port = unique sticky IP
    serverTemplate: (country, port) => `http://${country}.decodo.com:${port}`,
    usernameTemplate: (user) => user,
    defaultUser: null,
    defaultPass: null,
    defaultCountry: 'ro',
    stickyPortMin: 10001,
    stickyPortMax: 49999,
  },
  brightdata: {
    server: 'http://brd.superproxy.io:33335',
    usernameTemplate: (user, country, session) =>
      `${user}-country-${country}-session-${session}`,
    defaultUser: null,
    defaultPass: null,
    defaultCountry: 'ro',
  },
  iproyal: {
    server: 'http://geo.iproyal.com:12321',
    usernameTemplate: (user) => user,
    passwordTemplate: (pass, country, session) =>
      `${pass}_country-${country}_session-${session}_lifetime-30m`,
    defaultUser: null,
    defaultPass: null,
    defaultCountry: 'ro',
  },
  nodemaven: {
    server: 'http://rp.nodemavenio.com:10001',
    usernameTemplate: (user, country, session) =>
      `${user}-country-${country}-session-${session}`,
    defaultUser: null,
    defaultPass: null,
    defaultCountry: 'ro',
  },
};

function makeProxy(sessionId = null, country = null) {
  if (process.env.HB_NO_PROXY === '1') return null;

  const providerName = process.env.HB_PROXY_PROVIDER || 'decodo';
  const preset = PROXY_PRESETS[providerName] || PROXY_PRESETS.decodo;
  const cty = (country || process.env.HB_PROXY_COUNTRY || preset.defaultCountry || 'ro').toLowerCase();

  // Full manual override
  if (process.env.HB_PROXY_SERVER && process.env.HB_PROXY_USER) {
    return {
      server: process.env.HB_PROXY_SERVER,
      username: process.env.HB_PROXY_USER,
      password: process.env.HB_PROXY_PASS || '',
    };
  }

  // Legacy env var support
  const user = process.env.HB_PROXY_USER || process.env.PROXY_USER || process.env.PROXY_USERNAME || preset.defaultUser;
  const pass = process.env.HB_PROXY_PASS || process.env.PROXY_PASS || process.env.PROXY_PASSWORD || preset.defaultPass;

  if (!user || !pass) {
    console.warn(`[browser-human] No proxy credentials for "${providerName}". Call getTrial() or set HB_PROXY_USER/HB_PROXY_PASS.`);
    return null;
  }

  // Decodo: port-based sticky sessions
  if (preset.serverTemplate) {
    const portMin = preset.stickyPortMin || 10001;
    const portMax = preset.stickyPortMax || 49999;
    const port = sessionId
      ? parseInt(sessionId)
      : (process.env.HB_PROXY_SESSION
          ? parseInt(process.env.HB_PROXY_SESSION)
          : Math.floor(Math.random() * (portMax - portMin + 1)) + portMin);
    const server = preset.serverTemplate(cty, port);
    const username = preset.usernameTemplate(user, cty, port);
    const password = preset.passwordTemplate
      ? preset.passwordTemplate(pass, cty, port)
      : pass;
    return { server, username, password };
  }

  // Other providers: session-string based
  const sid = sessionId || process.env.HB_PROXY_SESSION || Math.random().toString(36).slice(2, 10);
  const server = preset.server;
  const username = preset.usernameTemplate(user, cty, sid);
  const password = preset.passwordTemplate ? preset.passwordTemplate(pass, cty, sid) : pass;
  return { server, username, password };
}

// ─── TRIAL CREDENTIALS ───────────────────────────────────────────────────────

/**
 * Get free trial credentials from humanbrowser.cloud
 * Sets HB_PROXY_USER, HB_PROXY_PASS, HB_PROXY_SESSION, HB_PROXY_PROVIDER
 * No signup needed — Romania residential proxy
 *
 * @example
 *   await getTrial();
 *   const { page } = await launchHuman(); // now uses trial proxy
 */
async function getTrial() {
  if (process.env.HB_PROXY_USER || process.env.PROXY_USER) {
    console.log('[human-browser] Credentials already set, skipping trial fetch.');
    return { ok: true, cached: true };
  }
  try {
    const https = require('https');
    const data = await new Promise((resolve, reject) => {
      const req = https.get('https://humanbrowser.cloud/api/trial', res => {
        let body = '';
        res.on('data', d => body += d);
        res.on('end', () => { try { resolve(JSON.parse(body)); } catch (e) { reject(e); } });
      });
      req.on('error', reject);
      req.setTimeout(10000, () => { req.destroy(); reject(new Error('Trial request timed out')); });
    });

    if (data.proxy_user || data.PROXY_USER) {
      const user     = data.proxy_user || data.PROXY_USER;
      const pass     = data.proxy_pass || data.PROXY_PASS;
      const session  = data.session || data.PROXY_SESSION || String(Math.floor(Math.random() * 39999) + 10001);
      const provider = data.provider || 'decodo';
      const country  = data.country || 'ro';

      process.env.HB_PROXY_PROVIDER = provider;
      process.env.HB_PROXY_USER     = user;
      process.env.HB_PROXY_PASS     = pass;
      process.env.HB_PROXY_SESSION  = session;
      if (!process.env.HB_PROXY_COUNTRY) process.env.HB_PROXY_COUNTRY = country;

      console.log(`🎉 Human Browser trial activated! (~100MB Romania residential IP)`);
      console.log(`   Upgrade at: https://humanbrowser.cloud\n`);
      return { ok: true, provider, country, session };
    }

    throw new Error(data.error || 'No credentials in trial response');
  } catch (err) {
    const e = new Error(err.message);
    e.code = 'TRIAL_UNAVAILABLE';
    e.cta_url = 'https://humanbrowser.cloud';
    console.warn('[human-browser] Trial fetch failed:', err.message);
    console.warn('   → Get credentials at: https://humanbrowser.cloud');
    throw e;
  }
}

// ─── HUMAN BEHAVIOR ───────────────────────────────────────────────────────────

const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const rand  = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

/**
 * Move mouse along a natural cubic Bezier curve path
 */
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

/**
 * Human-like click with curved mouse path
 */
async function humanClick(page, x, y) {
  await humanMouseMove(page, x, y);
  await sleep(rand(50, 180));
  await page.mouse.down();
  await sleep(rand(40, 100));
  await page.mouse.up();
  await sleep(rand(100, 300));
}

/**
 * Human-like typing: variable speed (60–220ms/char), occasional micro-pauses
 */
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

/**
 * Human-like scroll: smooth, multi-step, with jitter
 */
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

/**
 * Read pause — wait as if reading the page, occasional scroll
 */
async function humanRead(page, minMs = 1500, maxMs = 4000) {
  await sleep(rand(minMs, maxMs));
  if (Math.random() < 0.3) await humanScroll(page, 'down', rand(50, 150));
}

// ─── 2CAPTCHA SOLVER ──────────────────────────────────────────────────────────

/**
 * Auto-detect and solve reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile via 2captcha.com
 * Token is auto-injected into the page — just submit the form after calling this.
 *
 * @param {Page}   page
 * @param {Object} opts
 * @param {string} opts.apiKey     — 2captcha API key (default: env TWOCAPTCHA_KEY)
 * @param {string} opts.action     — reCAPTCHA v3 action (default: 'verify')
 * @param {number} opts.minScore   — reCAPTCHA v3 min score (default: 0.7)
 * @param {number} opts.timeout    — max wait ms (default: 120000)
 * @param {boolean} opts.verbose   — log progress (default: false)
 *
 * @example
 *   const { token, type } = await solveCaptcha(page, { verbose: true });
 *   await page.click('button[type=submit]');
 */
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

  // Auto-detect captcha type
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

  // Submit to 2captcha
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

  // Inject token into page
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

/**
 * Launch a human-like browser with residential proxy and device fingerprint
 *
 * @param {Object}  opts
 * @param {string}  opts.country   — 'ro'|'us'|'gb'|'de'|'nl'|'jp'|'fr'|'ca'|'au'|'sg' (default: 'ro')
 * @param {boolean} opts.mobile    — iPhone 15 Pro (true) or Desktop Chrome (false). Default: true
 * @param {boolean} opts.useProxy  — Enable residential proxy. Default: true
 * @param {boolean} opts.headless  — Headless mode. Default: true
 * @param {string}  opts.session   — Sticky session ID / Decodo port (unique IP per value)
 *
 * @returns {{ browser, ctx, page, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand }}
 */
async function launchHuman(opts = {}) {
  const {
    country  = null,
    mobile   = true,
    useProxy = true,
    headless = true,
    session  = null,
  } = opts;

  const cty = country || process.env.HB_PROXY_COUNTRY || 'ro';

  // Auto-fetch trial credentials if no proxy is configured
  if (useProxy && !process.env.HB_PROXY_USER && !process.env.PROXY_USER && !process.env.HB_PROXY_SERVER) {
    try {
      await getTrial();
    } catch (e) {
      console.warn('⚠️  Could not fetch trial credentials:', e.message);
      console.warn('   Get credentials at: https://humanbrowser.cloud');
    }
  }

  const device = buildDevice(mobile, cty);
  const meta   = COUNTRY_META[cty.toLowerCase()] || COUNTRY_META.ro;
  const proxy  = useProxy ? makeProxy(session, cty) : null;

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
  if (proxy) ctxOpts.proxy = proxy;

  const ctx = await browser.newContext(ctxOpts);

  // Anti-detection: override navigator properties
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
  }, { mobile, locale: meta.locale });

  const page = await ctx.newPage();

  return { browser, ctx, page, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand };
}

// ─── SHADOW DOM UTILITIES ─────────────────────────────────────────────────────

/**
 * Query an element inside shadow DOM (any depth).
 * Use when page.$() returns null but element is visible on screen.
 */
async function shadowQuery(page, selector) {
  return page.evaluate((sel) => {
    function q(root, s) {
      const el = root.querySelector(s); if (el) return el;
      for (const n of root.querySelectorAll('*')) if (n.shadowRoot) { const f = q(n.shadowRoot, s); if (f) return f; }
    }
    return q(document, sel);
  }, selector);
}

/**
 * Fill an input inside shadow DOM.
 * Uses native input setter to trigger React/Angular onChange properly.
 */
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

/**
 * Click a button by text label, searching through shadow DOM.
 */
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

/**
 * Dump all interactive elements including inside shadow roots.
 * Use for debugging when form elements aren't found by standard selectors.
 */
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

/**
 * Paste text into a Lexical/ProseMirror/Quill/Draft.js rich text editor.
 * Uses clipboard API — works where keyboard.type() and fill() fail.
 *
 * Common selectors:
 *   '[data-lexical-editor]'       — Reddit, Meta apps
 *   '.public-DraftEditor-content' — Draft.js (Twitter, Quora)
 *   '.ql-editor'                  — Quill
 *   '.ProseMirror'                — Linear, Confluence
 *   '[contenteditable="true"]'    — generic
 */
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
  launchHuman, getTrial,
  humanClick, humanMouseMove, humanType, humanScroll, humanRead,
  solveCaptcha,
  shadowQuery, shadowFill, shadowClickButton, dumpInteractiveElements,
  pasteIntoEditor,
  makeProxy, buildDevice,
  sleep, rand, COUNTRY_META,
};

// ─── QUICK TEST ───────────────────────────────────────────────────────────────
if (require.main === module) {
  const country = process.argv[2] || 'ro';
  console.log(`🧪 Testing Human Browser v4.0.0 — country: ${country.toUpperCase()}\n`);
  (async () => {
    const { browser, page } = await launchHuman({ country, mobile: true });
    await page.goto('https://ipinfo.io/json', { waitUntil: 'domcontentloaded', timeout: 30000 });
    const info = JSON.parse(await page.textContent('body'));
    console.log(`✅ IP:      ${info.ip}`);
    console.log(`✅ Country: ${info.country} (${info.city})`);
    console.log(`✅ Org:     ${info.org}`);
    console.log(`✅ TZ:      ${info.timezone}`);
    const ua = await page.evaluate(() => navigator.userAgent);
    console.log(`✅ UA:      ${ua.slice(0, 80)}...`);
    await browser.close();
    console.log('\n🎉 Human Browser v4.0.0 is ready.');
  })().catch(console.error);
}
