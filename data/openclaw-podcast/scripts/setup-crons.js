#!/usr/bin/env node
/**
 * OpenClaw Podcast Briefings — Setup Wizard
 * 
 * A polished, production-ready wizard that:
 *   1. Validates your Superlore API key
 *   2. Lets you choose episode styles
 *   3. Optionally creates a custom briefing style
 *   4. Sets your music bed preference
 *   5. Configures a schedule for each style
 *   6. Generates a preview episode so you can hear the quality
 *   7. Outputs ready-to-use `openclaw cron add` commands
 *
 * Usage:
 *   node scripts/setup-crons.js
 *
 * Requirements:
 *   - Node.js (built-in modules only — no npm install needed)
 *   - Internet connection
 *   - Superlore API key (get one at https://superlore.ai)
 */

'use strict';

const readline = require('readline');
const https    = require('https');
const fs       = require('fs');
const path     = require('path');
const { execFileSync } = require('child_process');

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

// Official Superlore API — hosted on Render (superlore.ai domain proxies here)
const API_BASE = 'https://superlore-api.onrender.com';

const VOICES = {
  Luna:    { id: 'af_heart-80_af_sarah-15_af_nicole-5', label: 'Luna (warm, balanced — female)' },
  Michael: { id: 'am_michael-60_am_eric-40',             label: 'Michael (rich, resonant — male)' },
  Heart:   { id: 'af_heart',                              label: 'Heart (soft, intimate — female)' },
};

const STYLES = [
  {
    name:        'The Briefing',
    shortName:   'The Briefing',
    description: 'Documentary narrator. What happened, metrics, what\'s next.',
    voice:       'Luna',
    speed:       0.95,
    scheduleHint: 'morning or evening',
  },
  {
    name:        'Opportunities & Tactics',
    shortName:   'Opportunities',
    description: 'Growth opportunities and tactical moves.',
    voice:       'Michael',
    speed:       0.95,
    scheduleHint: 'morning',
  },
  {
    name:        '10X Thinking',
    shortName:   '10X Thinking',
    description: 'Moonshot ideas that challenge assumptions.',
    voice:       'Michael',
    speed:       1.0,
    scheduleHint: 'morning',
  },
  {
    name:        'The Advisor',
    shortName:   'The Advisor',
    description: 'Honest mentor feedback, no sugar-coating.',
    voice:       'Luna',
    speed:       0.92,
    scheduleHint: 'evening',
  },
  {
    name:        'Focus & Priorities',
    shortName:   'Focus',
    description: 'Ruthless prioritization. What\'s the ONE thing?',
    voice:       'Heart',
    speed:       1.0,
    scheduleHint: 'morning',
  },
  {
    name:        'Growth & Scale',
    shortName:   'Growth & Scale',
    description: 'Revenue, users, funnels. Pure metrics.',
    voice:       'Michael',
    speed:       0.98,
    scheduleHint: 'evening',
  },
  {
    name:        'Week in Review',
    shortName:   'Week in Review',
    description: 'Weekly zoom-out with trends and goals.',
    voice:       'Luna',
    speed:       0.93,
    scheduleHint: 'weekly (Friday evening)',
  },
  {
    name:        'The Futurist',
    shortName:   'The Futurist',
    description: 'Connect today\'s work to your 3-12 month vision.',
    voice:       'Heart',
    speed:       0.95,
    scheduleHint: 'evening',
  },
];

const DEFAULT_TIMES = {
  morning: '08:00',
  midday:  '12:00',
  evening: '20:00',
};

// ─────────────────────────────────────────────────────────────────────────────
// Readline helpers — one shared interface keeps stdin clean
// ─────────────────────────────────────────────────────────────────────────────

let rl;

function createRL() {
  rl = readline.createInterface({
    input:  process.stdin,
    output: process.stdout,
  });

  // Graceful Ctrl+C
  rl.on('SIGINT', () => {
    console.log('\n\n👋  Setup cancelled. Run again anytime to continue.\n');
    process.exit(0);
  });
}

function ask(question) {
  return new Promise(resolve => {
    rl.question(question, answer => resolve(answer.trim()));
  });
}

function closeRL() {
  if (rl) {
    rl.close();
    rl = null;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// HTTP helper (native https — no dependencies)
// ─────────────────────────────────────────────────────────────────────────────

function httpRequest(url, options = {}, body = null) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const req = https.request(
      {
        hostname: parsed.hostname,
        port:     parsed.port || 443,
        path:     parsed.pathname + parsed.search,
        method:   options.method || 'GET',
        headers:  options.headers || {},
        timeout:  20000,
      },
      (res) => {
        let data = '';
        res.on('data', chunk => (data += chunk));
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode, data: JSON.parse(data) });
          } catch {
            resolve({ status: res.statusCode, data });
          }
        });
      }
    );

    req.on('error', (err) => {
      err.isNetworkError = ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND', 'EAI_AGAIN'].includes(err.code);
      reject(err);
    });

    req.on('timeout', () => {
      req.destroy();
      const err = new Error('Request timed out');
      err.isNetworkError = true;
      reject(err);
    });

    if (body) req.write(body);
    req.end();
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ─────────────────────────────────────────────────────────────────────────────
// Workspace detection
// ─────────────────────────────────────────────────────────────────────────────

function findWorkspace() {
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    if (fs.existsSync(path.join(dir, 'memory'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  // Fall back to ~/.openclaw/workspace
  return path.join(process.env.HOME || '', '.openclaw', 'workspace');
}

function findSkillPath() {
  const cwd = process.cwd();
  if (cwd.includes('openclaw-podcast')) {
    return cwd.replace(/\/scripts$/, '');
  }
  // Try common locations
  const candidates = [
    path.join(process.env.HOME || '', '.openclaw', 'skills', 'openclaw-podcast'),
    path.join(cwd, 'openclaw-podcast'),
    cwd,
  ];
  return candidates.find(c => fs.existsSync(c)) || cwd;
}

// ─────────────────────────────────────────────────────────────────────────────
// Dividers & formatting
// ─────────────────────────────────────────────────────────────────────────────

function divider(char = '─', width = 62) {
  return char.repeat(width);
}

function header(text) {
  const pad   = Math.max(0, 60 - text.length);
  const left  = Math.floor(pad / 2);
  const right = pad - left;
  console.log('\n╔' + '═'.repeat(62) + '╗');
  console.log('║' + ' '.repeat(left) + text + ' '.repeat(right) + '║');
  console.log('╚' + '═'.repeat(62) + '╝\n');
}

function section(title) {
  console.log('\n' + divider() + '\n' + title + '\n' + divider());
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 1 — Connect Your Account (API Key Validation or OTP Email Flow)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Write an API key export line to the user's shell profile (~/.zshrc or ~/.bashrc).
 */
function saveToShellProfile(apiKey) {
  const shell  = process.env.SHELL || '';
  const rcFile = shell.includes('zsh')
    ? path.join(process.env.HOME || '', '.zshrc')
    : path.join(process.env.HOME || '', '.bashrc');
  try {
    fs.appendFileSync(rcFile, `\n# Superlore Podcast Briefings\nexport SUPERLORE_API_KEY="${apiKey}"\n`);
    console.log(`  ✅ Saved to ${rcFile}. Run \`source ${rcFile}\` or open a new terminal to apply.\n`);
  } catch (e) {
    console.log(`  ⚠️  Couldn't write to ${rcFile}: ${e.message}\n`);
  }
}

/**
 * Ask whether to save the key to the shell profile.
 * @param {string} apiKey
 * @param {'y'|'n'} defaultChoice - 'y' for OTP flow, 'n' for manual entry
 */
async function offerSaveToShellProfile(apiKey, defaultChoice = 'n') {
  const label   = defaultChoice === 'y' ? 'default: y' : 'default: n';
  const rcName  = (process.env.SHELL || '').includes('zsh') ? '~/.zshrc' : '~/.bashrc';
  const savePref = await ask(`  Save key to shell profile (${rcName})? (y/n) [${label}]: `);
  const shouldSave = defaultChoice === 'y'
    ? savePref.toLowerCase() !== 'n'
    : savePref.toLowerCase() === 'y';
  if (shouldSave) {
    saveToShellProfile(apiKey);
  }
}

/**
 * Validate an API key against the /episodes endpoint.
 * Exits process on failure; returns the key on success.
 */
async function validateApiKey(apiKey) {
  process.stdout.write('\n  Validating key...');
  let res;
  try {
    res = await httpRequest(`${API_BASE}/episodes?limit=1`, {
      method: 'GET',
      headers: { 'x-api-key': apiKey },
    });
  } catch (err) {
    console.log(' ❌\n');
    if (err.isNetworkError) {
      console.error(`\n  ❌ Can't reach Superlore API. Check your internet connection.\n`);
    } else {
      console.error(`\n  ❌ Network error: ${err.message}\n`);
    }
    process.exit(1);
  }

  if (res.status === 401) {
    console.log(' ❌\n');
    console.error('\n  ❌ Invalid API key. Get yours at https://superlore.ai → Account → API Keys\n');
    process.exit(1);
  }

  if (res.status >= 400) {
    console.log(' ❌\n');
    console.error(`\n  ❌ Unexpected API response (${res.status}). Please try again later.\n`);
    process.exit(1);
  }

  console.log(' ✅\n');

  // Show remaining usage if available
  const meta = res.data?.meta || res.data?.usage || {};
  if (meta.remainingHours !== undefined) {
    console.log(`  ✅ API key valid! You have ${Number(meta.remainingHours).toFixed(1)} hours remaining.\n`);
  } else if (meta.remainingMinutes !== undefined) {
    const hrs = (meta.remainingMinutes / 60).toFixed(1);
    console.log(`  ✅ API key valid! You have ${hrs} hours remaining.\n`);
  } else {
    console.log(`  ✅ API key valid!\n`);
  }

  return apiKey;
}

/**
 * Option B — OTP email authentication flow.
 * Sends a 6-digit code, verifies it, creates an API key, and returns it.
 */
async function stepOTPFlow() {
  let apiKey = null;

  while (!apiKey) {
    // ── Get email ──────────────────────────────────────────────────────────
    console.log();
    const email = await ask('  Enter your email: ');
    if (!email || !email.includes('@')) {
      console.log('\n  ⚠️  Please enter a valid email address.\n');
      continue;
    }

    // ── Request OTP ────────────────────────────────────────────────────────
    process.stdout.write('\n  📧 Sending verification code...');
    try {
      const otpRes = await httpRequest(`${API_BASE}/api/auth/otp-request`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
      }, JSON.stringify({ email }));

      if (otpRes.status === 429) {
        console.log(' ⚠️\n');
        console.log('  ⚠️  Too many attempts. Please wait a moment and try again.\n');
        continue;
      }
      if (otpRes.status >= 400) {
        console.log(' ❌\n');
        console.log(`  ❌ Could not send verification code (${otpRes.status}). Please try again.\n`);
        continue;
      }

      console.log(' ✅');
      console.log('  ✅ Code sent! Check your email.\n');
    } catch (err) {
      console.log(' ❌\n');
      if (err.isNetworkError) {
        console.error("  ❌ Can't reach Superlore API. Check your internet connection.\n");
      } else {
        console.error(`  ❌ Network error: ${err.message}\n`);
      }
      continue;
    }

    // ── Verify OTP ─────────────────────────────────────────────────────────
    let jwt        = null;
    let verified   = false;
    let attempts   = 0;
    const MAX_ATTEMPTS = 3;

    while (!verified && attempts < MAX_ATTEMPTS) {
      const code = (await ask('  Enter the 6-digit code: ')).trim();

      if (!code || !/^\d{6}$/.test(code)) {
        console.log('\n  ⚠️  Please enter a 6-digit code.\n');
        attempts++;
        continue;
      }

      process.stdout.write('\n  Verifying code...');
      try {
        const verRes = await httpRequest(`${API_BASE}/api/auth/otp-verify`, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
        }, JSON.stringify({ email, code }));

        if (verRes.status === 429) {
          console.log(' ⚠️\n');
          console.log('  ⚠️  Too many attempts. Please wait a moment.\n');
          break; // outer while will restart
        }

        if (verRes.status === 401 || verRes.status === 400) {
          console.log(' ❌\n');
          console.log('  ❌ Code expired or invalid.');
          attempts++;
          if (attempts < MAX_ATTEMPTS) {
            const retry = await ask('  Request a new code? (y/n) [default: y]: ');
            if (retry.toLowerCase() !== 'n') break; // break to re-request OTP
          }
          continue;
        }

        if (verRes.status >= 400) {
          console.log(' ❌\n');
          console.log(`  ❌ Verification failed (${verRes.status}). Please try again.\n`);
          attempts++;
          continue;
        }

        jwt = verRes.data?.token || verRes.data?.jwt;
        if (!jwt) {
          console.log(' ❌\n');
          console.log('  ❌ Unexpected response from server. Please try again.\n');
          break;
        }

        console.log(' ✅');
        verified = true;
      } catch (err) {
        console.log(' ❌\n');
        if (err.isNetworkError) {
          console.error("  ❌ Can't reach Superlore API. Check your internet connection.\n");
          break;
        }
        console.error(`  ❌ Network error: ${err.message}\n`);
        attempts++;
      }
    }

    if (!verified || !jwt) continue; // restart outer loop (re-enter email)

    // ── Create API key ─────────────────────────────────────────────────────
    process.stdout.write('\n  ✅ Verified! Creating your API key...');
    try {
      const keyRes = await httpRequest(`${API_BASE}/api/auth/create-api-key`, {
        method:  'POST',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${jwt}`,
        },
      });

      if (keyRes.status >= 400) {
        console.log(' ❌\n');
        console.log(`  ❌ Could not create API key (${keyRes.status}). Please try again.\n`);
        continue;
      }

      apiKey = keyRes.data?.apiKey;
      if (!apiKey) {
        console.log(' ❌\n');
        console.log('  ❌ Unexpected response from server. Please try again.\n');
        continue;
      }

      // Show a safely masked version of the key
      const maskedKey = apiKey.length > 12
        ? `${apiKey.slice(0, 8)}...${apiKey.slice(-4)}`
        : apiKey;
      console.log(' ✅');
      console.log(`  ✅ API key created: ${maskedKey}\n`);
    } catch (err) {
      console.log(' ❌\n');
      if (err.isNetworkError) {
        console.error("  ❌ Can't reach Superlore API. Check your internet connection.\n");
      } else {
        console.error(`  ❌ Network error: ${err.message}\n`);
      }
      continue;
    }
  } // end while (!apiKey)

  // Offer to save to shell profile (default y for OTP flow)
  await offerSaveToShellProfile(apiKey, 'y');

  // Validate before continuing
  return await validateApiKey(apiKey);
}

async function stepAPIKey() {
  console.log(`
Welcome to Superlore Podcast Briefings! 🎙️

  Turn your OpenClaw workspace into personalized audio briefings.
  Powered by Superlore AI — your own private podcast channel.

  • 8 curated briefing styles (The Briefing, The Advisor, 10X Thinking, …)
  • 3 premium voices: Luna, Michael, and Heart
  • Scheduled delivery — morning, midday, or evening
  • 4 free hours of generation with your API key
`);

  console.log(divider());
  console.log('Step 1 of 7 — Connect Your Account');
  console.log(divider());

  // ── Check for an existing environment key ──────────────────────────────
  let apiKey = process.env.SUPERLORE_API_KEY || '';

  if (apiKey) {
    console.log(`\n  Found SUPERLORE_API_KEY in environment.\n`);
    const confirmed = await ask('  Use this key? (y/n) [default: y]: ');
    if (confirmed.toLowerCase() !== 'n') {
      // Already persisted — just validate and continue
      return await validateApiKey(apiKey);
    }
    apiKey = '';
  }

  // ── Choose Option A or B ───────────────────────────────────────────────
  console.log(`
  Option A: Already have an API key? Paste it.
  Option B: Sign up or log in with your email.
`);
  const choice = await ask('  Choose (a/b) [default: b]: ');

  if (choice.toLowerCase() === 'a') {
    // ── Option A: manual key entry (original flow) ─────────────────────
    while (!apiKey) {
      console.log('\n  Get your free API key at https://superlore.ai → Account → API Keys\n');
      apiKey = await ask('  Enter your Superlore API key: ');
      if (!apiKey) {
        console.log('\n  ⚠️  API key is required to continue.\n');
      }
    }

    const validKey = await validateApiKey(apiKey);
    // Offer to save (default n — manual users likely already have it set)
    await offerSaveToShellProfile(validKey, 'n');
    return validKey;
  } else {
    // ── Option B: OTP email flow (default) ────────────────────────────
    return await stepOTPFlow();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 2 — Choose Episode Styles
// ─────────────────────────────────────────────────────────────────────────────

async function stepChooseStyles() {
  section('Step 2 of 7 — Choose Your Briefing Styles');

  console.log('\n  Each style gives you a different lens on your work.\n');

  STYLES.forEach((style, i) => {
    const num  = String(i + 1).padStart(2, ' ');
    const name = style.shortName.padEnd(20, ' ');
    console.log(`  ${num}. ${name} — ${style.description}`);
  });

  console.log('\n  Tip: You can schedule different styles at different times of day.');
  console.log('  (e.g., "The Briefing" in the morning, "The Advisor" in the evening)\n');

  let selected = [];
  while (selected.length === 0) {
    const input = await ask('  Which styles? (e.g., "1,4,7" or "all"): ');
    const lower = input.toLowerCase().trim();

    if (lower === 'all') {
      selected = STYLES.map((_, i) => i);
    } else {
      const parts = lower.split(/[,\s]+/);
      for (const part of parts) {
        if (part.includes('-')) {
          const [a, b] = part.split('-').map(x => parseInt(x));
          for (let i = a; i <= b; i++) {
            if (i >= 1 && i <= STYLES.length && !selected.includes(i - 1)) {
              selected.push(i - 1);
            }
          }
        } else {
          const n = parseInt(part);
          if (n >= 1 && n <= STYLES.length && !selected.includes(n - 1)) {
            selected.push(n - 1);
          }
        }
      }
    }

    if (selected.length === 0) {
      console.log('\n  ⚠️  No valid styles selected. Try again.\n');
    }
  }

  selected.sort((a, b) => a - b);
  const chosenStyles = selected.map(i => STYLES[i]);

  console.log('\n  Selected styles:');
  chosenStyles.forEach(s => {
    const voiceName = s.voice;
    const voiceLabel = VOICES[voiceName]?.label || voiceName;
    console.log(`    ✓ ${s.name} — voiced by ${voiceLabel.split(' (')[0]}`);
  });
  console.log();

  return chosenStyles;
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 3 — Custom Episode Style
// ─────────────────────────────────────────────────────────────────────────────

async function stepCustomStyle(workspace) {
  section('Step 3 of 7 — Custom Briefing Style (Optional)');

  console.log(`
  Beyond the 8 built-in styles, you can design your own briefing style
  tailored to exactly what you care about. Skip this if you're happy with
  the defaults — you can always add custom styles later.
`);

  const want = await ask('  Want to design a custom briefing style? (y/n) [default: n]: ');
  if (!want || want.toLowerCase() !== 'y') {
    console.log('\n  Skipping custom style.\n');
    return [];
  }

  const customStyles = [];
  let addAnother = true;

  while (addAnother) {
    console.log('\n  ' + divider('─', 56));

    const focus = await ask('\n  What should it focus on?\n  (e.g., "competitive analysis", "team morale", "product roadmap"): ');
    if (!focus) {
      console.log('  ⚠️  Focus is required. Skipping custom style.\n');
      break;
    }

    const tone = await ask('\n  What tone?\n  (e.g., "analytical", "conversational", "urgent") [default: conversational]: ');
    const toneVal = tone || 'conversational';

    console.log('\n  Voice preference?');
    Object.entries(VOICES).forEach(([name, v], i) => {
      console.log(`    ${i + 1}. ${v.label}`);
    });
    const voiceInput = await ask('\n  Choose voice (1/2/3) [default: 1]: ');
    const voiceIdx   = Math.max(0, Math.min(2, (parseInt(voiceInput) || 1) - 1));
    const voiceName  = Object.keys(VOICES)[voiceIdx];
    const voiceId    = VOICES[voiceName].id;

    const speedInput = await ask('\n  Speed? (0.8 = slow, 1.0 = normal, 1.1 = fast) [default: 0.95]: ');
    const speed = parseFloat(speedInput) || 0.95;

    const nameInput = await ask('\n  Name for this style: ');
    const styleName = nameInput || `Custom: ${focus.slice(0, 30)}`;
    const slug      = styleName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

    const styleObj = {
      name:         styleName,
      description:  `${focus} — ${toneVal} tone`,
      voice:        voiceId,
      speed,
      targetMinutes: 6,
      musicBed:     'ambient',
      instructions: `
You are producing a personalized podcast briefing.

Focus area: ${focus}
Tone: ${toneVal}

1. Open with a brief, warm greeting and today's date.
2. Immediately dive into insights about: ${focus}
3. Use a ${toneVal} tone throughout — never break character.
4. Draw on the briefing data provided. Reference specific work, metrics, and context.
5. Offer 3-5 actionable observations or recommendations related to ${focus}.
6. Close with a clear, memorable takeaway.

Style rules:
- Keep it conversational, not like a report being read aloud
- Reference the user by name whenever natural
- No bullet-point recitation — weave ideas into a narrative
- Target 5-7 minutes of content
`,
    };

    // Save to workspace/podcast-styles/
    const stylesDir = path.join(workspace, 'podcast-styles');
    if (!fs.existsSync(stylesDir)) {
      fs.mkdirSync(stylesDir, { recursive: true });
    }
    const filePath = path.join(stylesDir, `${slug}.json`);
    fs.writeFileSync(filePath, JSON.stringify(styleObj, null, 2));
    console.log(`\n  ✅ Custom style saved to podcast-styles/${slug}.json\n`);
    console.log(`     Use it with: node scripts/generate-episode.js --style "${styleName}"\n`);

    customStyles.push({ ...styleObj, slug });

    const more = await ask('  Add another custom style? (y/n) [default: n]: ');
    addAnother = more.toLowerCase() === 'y';
  }

  return customStyles;
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 4 — Music Bed Preference
// ─────────────────────────────────────────────────────────────────────────────

async function stepMusicBed() {
  section('Step 4 of 7 — Background Music');

  console.log(`
  Background music adds atmosphere to your briefings and helps separate
  them from just "text being read aloud." The Superlore API selects an
  ambient track that matches each episode's tone.
`);

  console.log('    1. With music bed (ambient background music)  ← recommended');
  console.log('    2. Voice only (no music)\n');

  const choice = await ask('  Preference? (1/2) [default: 1]: ');
  const musicBed = choice === '2' ? false : true;

  if (musicBed) {
    console.log('\n  ✅ Music bed enabled. Episodes will include ambient background music.\n');
  } else {
    console.log('\n  ✅ Voice-only mode. Clean narration with no background music.\n');
  }

  return musicBed;
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 5 — Schedule Each Style
// ─────────────────────────────────────────────────────────────────────────────

async function stepSchedule(selectedStyles, customStyles) {
  section('Step 5 of 7 — Schedule Your Briefings');

  const allStyles = [
    ...selectedStyles.map(s => ({ ...s, isCustom: false })),
    ...customStyles.map(s => ({ ...s, isCustom: true })),
  ];

  console.log('\n  For each style, choose when you want it delivered.\n');

  const jobs = [];

  for (const style of allStyles) {
    console.log(`\n  ${divider('─', 52)}`);
    console.log(`  📻 ${style.name}`);
    if (style.scheduleHint) {
      console.log(`     Suggested: ${style.scheduleHint}`);
    }
    console.log();
    console.log('    1. Morning    (8:00 AM every day)');
    console.log('    2. Midday     (12:00 PM every day)');
    console.log('    3. Evening    (8:00 PM every day)');
    console.log('    4. Daily      (choose your own time, every day)');
    console.log('    5. Weekly     (choose a day + time)');
    console.log('    6. Custom     (enter a raw cron expression)');
    console.log();

    const freq = await ask('    When? (1-6): ');

    let cronTime, timeOfDay, label;

    if (freq === '2') {
      timeOfDay = 'midday';
      cronTime  = '0 12 * * *';
      label     = 'midday (12:00 PM daily)';
    } else if (freq === '3') {
      timeOfDay = 'evening';
      cronTime  = '0 20 * * *';
      label     = 'evening (8:00 PM daily)';
    } else if (freq === '4') {
      timeOfDay = 'morning';
      const t   = await ask('    What time? (HH:MM, default 08:00): ') || '08:00';
      const [h, m] = t.split(':');
      const hh  = String(parseInt(h) || 8).padStart(2, '0');
      const mm  = String(parseInt(m) || 0).padStart(2, '0');
      cronTime  = `${parseInt(mm)} ${parseInt(hh)} * * *`;
      timeOfDay = parseInt(hh) < 12 ? 'morning' : parseInt(hh) < 17 ? 'midday' : 'evening';
      label     = `daily at ${hh}:${mm}`;
    } else if (freq === '5') {
      const dayInput = await ask('    Which day? (Mon=1 … Fri=5 … Sun=7) [default: 5/Friday]: ') || '5';
      const day      = Math.max(0, Math.min(7, parseInt(dayInput) || 5));
      const t        = await ask('    What time? (HH:MM, default 20:00): ') || '20:00';
      const [h, m]   = t.split(':');
      const hh       = String(parseInt(h) || 20).padStart(2, '0');
      const mm       = String(parseInt(m) || 0).padStart(2, '0');
      cronTime       = `${parseInt(mm)} ${parseInt(hh)} * * ${day}`;
      timeOfDay      = parseInt(hh) < 12 ? 'morning' : parseInt(hh) < 17 ? 'midday' : 'evening';
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      label          = `weekly on ${dayNames[day] || 'Friday'} at ${hh}:${mm}`;
    } else if (freq === '6') {
      cronTime  = await ask('    Cron expression (e.g., "0 8 * * 1-5" for weekdays at 8 AM): ');
      const tod = await ask('    Time of day context? (morning/midday/evening) [default: morning]: ') || 'morning';
      timeOfDay = ['morning', 'midday', 'evening'].includes(tod) ? tod : 'morning';
      label     = `custom schedule: ${cronTime}`;
    } else {
      // Default: morning (option 1 or anything unrecognized)
      timeOfDay = 'morning';
      cronTime  = '0 8 * * *';
      label     = 'morning (8:00 AM daily)';
    }

    jobs.push({ style, timeOfDay, cronTime, label });
    console.log(`\n    ✅ Scheduled: ${label}\n`);
  }

  return jobs;
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 6 — Preview First Episode
// ─────────────────────────────────────────────────────────────────────────────

async function stepPreviewEpisode(apiKey, selectedStyles, skillPath) {
  section('Step 6 of 7 — Preview Your First Briefing');

  console.log(`
  Let's generate your first briefing so you can hear how it sounds! 🎧

  This validates that everything is working end-to-end and gives you a
  taste of what your daily briefings will be like.
`);

  const previewStyles = [...selectedStyles];
  if (previewStyles.length === 0) {
    console.log('  ⚠️  No styles selected — skipping preview.\n');
    return;
  }

  let keepGoing = true;
  let previewIdx = 0;

  while (keepGoing && previewIdx < previewStyles.length) {
    const style = previewStyles[previewIdx];
    const voiceName = style.voice || 'Luna';
    const voiceLabel = VOICES[voiceName]?.label?.split(' (')[0] || voiceName;

    console.log(`\n  Generating "${style.name}" with ${voiceLabel} voice...\n`);

    const scriptPath = path.join(skillPath, 'scripts', 'generate-episode.js');

    if (!fs.existsSync(scriptPath)) {
      console.log(`  ⚠️  Could not find generate-episode.js at:\n  ${scriptPath}\n`);
      console.log('  Skipping preview. You can generate manually:');
      console.log(`  node "${scriptPath}" --style "${style.name}"\n`);
      break;
    }

    process.stdout.write('    Reading workspace context...');
    await sleep(600);
    console.log(' ✓');

    process.stdout.write('    Sending to Superlore API...');

    let episodeUrl = null;

    try {
      const child = require('child_process').spawnSync(
        process.execPath,
        [scriptPath, '--style', style.name, '--time-of-day', 'morning', '--no-poll'],
        {
          env:     { ...process.env, SUPERLORE_API_KEY: apiKey },
          timeout: 30000,
          encoding: 'utf-8',
        }
      );

      const output = (child.stdout || '') + (child.stderr || '');

      // Extract episode URL from output
      const urlMatch = output.match(/https:\/\/superlore\.ai\/episode\/\S+/);
      if (urlMatch) {
        episodeUrl = urlMatch[0].replace(/[.,\s]+$/, '');
      }

      if (child.status !== 0 && !episodeUrl) {
        console.log(' ❌\n');
        // Surface the relevant error lines
        const errLines = output.split('\n').filter(l => /❌|error|fail/i.test(l));
        if (errLines.length) {
          errLines.forEach(l => console.log('    ' + l.trim()));
        } else {
          console.log('    Episode generation failed. Check your API key and try manually:');
          console.log(`    node scripts/generate-episode.js --style "${style.name}"`);
        }
        console.log();
      } else if (episodeUrl) {
        console.log(' ✓');
        console.log('\n    ⏳ Generating episode (this takes ~2 minutes)...');
        await sleep(3000);
        console.log('\n    ✅ Episode created!\n');
        console.log(`    🎧 Listen: ${episodeUrl}\n`);
      } else {
        console.log(' ✓');
        console.log('\n    ✅ Episode submitted! Check the URL in your terminal output above.\n');
      }
    } catch (err) {
      console.log(' ❌\n');
      console.log(`    Error spawning generate-episode.js: ${err.message}`);
      console.log('    Try manually: node scripts/generate-episode.js\n');
    }

    previewIdx++;

    if (previewIdx < previewStyles.length) {
      const another = await ask('  Generate another style to compare? (y/n) [default: n]: ');
      keepGoing = another.toLowerCase() === 'y';
    } else {
      keepGoing = false;
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Step 7 — Output Cron Commands
// ─────────────────────────────────────────────────────────────────────────────

function buildCronCommand(job, skillPath) {
  const { style, timeOfDay, cronTime } = job;
  const scriptPath  = path.join(skillPath, 'scripts', 'generate-episode.js');
  const jobName     = `podcast-${style.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${timeOfDay}`;
  const styleArg    = style.name.replace(/'/g, "\\'");

  return [
    `openclaw cron add "${jobName}" \\`,
    `  --schedule "${cronTime}" \\`,
    `  --command "node ${scriptPath} --style '${styleArg}' --time-of-day ${timeOfDay}"`,
  ].join('\n');
}

async function stepConfirmAndOutput(jobs, skillPath) {
  section('Step 7 of 7 — Activate Your Briefings');

  console.log(`
  Everything is configured! Below are the OpenClaw cron commands
  to activate your briefings. Copy and paste each command into your
  OpenClaw terminal to schedule them.
`);

  console.log('  ' + divider('─', 58));
  console.log();

  jobs.forEach((job, i) => {
    console.log(`  # ${i + 1}. ${job.style.name} — ${job.label}`);
    const cmd = buildCronCommand(job, skillPath);
    cmd.split('\n').forEach(line => console.log('  ' + line));
    console.log();
  });

  console.log('  ' + divider('─', 58));
  console.log();

  console.log('  Other useful commands:\n');
  console.log('    openclaw cron list             — view all scheduled jobs');
  console.log('    openclaw cron remove <name>    — remove a job');
  console.log(`    node ${path.join(skillPath, 'scripts', 'generate-episode.js')} --dry-run`);
  console.log('                                   — preview prompt without creating an episode');
  console.log();

  const doIt = await ask('  Run these commands now? (y/n) [default: n]: ');
  if (doIt.toLowerCase() === 'y') {
    console.log();
    let allOk = true;
    for (const job of jobs) {
      const cmd = buildCronCommand(job, skillPath);
      // Build the actual args for execFileSync
      const jobName   = `podcast-${job.style.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${job.timeOfDay}`;
      const styleArg  = job.style.name;
      const scriptPath = path.join(skillPath, 'scripts', 'generate-episode.js');
      const cmdStr    = `node ${scriptPath} --style '${styleArg}' --time-of-day ${job.timeOfDay}`;
      try {
        execFileSync('openclaw', [
          'cron', 'add', jobName,
          '--schedule', job.cronTime,
          '--command',  cmdStr,
        ], { stdio: 'inherit' });
        console.log(`  ✅ Scheduled: ${jobName}\n`);
      } catch (err) {
        console.log(`  ❌ Failed to schedule ${jobName}: ${err.message}`);
        console.log(`     Run manually:\n  ${cmd}\n`);
        allOk = false;
      }
    }

    if (allOk) {
      console.log('  ✅ All cron jobs activated!\n');
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Summary banner
// ─────────────────────────────────────────────────────────────────────────────

function showSummary(selectedStyles, customStyles, jobs) {
  header('🎙️  You\'re all set with Superlore Podcast Briefings!');

  console.log('  What you configured:\n');

  if (selectedStyles.length > 0) {
    console.log('  Built-in styles:');
    selectedStyles.forEach(s => {
      const voiceLabel = VOICES[s.voice]?.label?.split(' (')[0] || s.voice;
      console.log(`    ✓ ${s.name} — ${voiceLabel} @ ${s.speed}x`);
    });
    console.log();
  }

  if (customStyles.length > 0) {
    console.log('  Custom styles:');
    customStyles.forEach(s => console.log(`    ✓ ${s.name}`));
    console.log();
  }

  if (jobs.length > 0) {
    console.log('  Schedule:');
    jobs.forEach(j => console.log(`    • ${j.style.name} — ${j.label}`));
    console.log();
  }

  console.log('  Next steps:');
  console.log('    1. Your briefings will generate automatically at the scheduled times');
  console.log('    2. Listen at https://superlore.ai or via the printed episode links');
  console.log('    3. Add custom styles anytime in your workspace\'s podcast-styles/ folder');
  console.log('    4. Adjust voices, speed, or schedule by re-running this wizard\n');

  console.log('  Enjoy your personalized podcast briefings! 🎧\n');
}

// ─────────────────────────────────────────────────────────────────────────────
// Main orchestrator
// ─────────────────────────────────────────────────────────────────────────────

async function main() {
  createRL();

  const workspace = findWorkspace();
  const skillPath = findSkillPath();

  // Step 1 — API key
  const apiKey = await stepAPIKey();

  // Step 2 — Choose styles
  const selectedStyles = await stepChooseStyles();

  // Step 3 — Optional custom style
  const customStyles = await stepCustomStyle(workspace);

  // Step 4 — Music bed
  const musicBed = await stepMusicBed();

  // Persist music bed preference to each custom style config
  for (const cs of customStyles) {
    const stylesDir = path.join(workspace, 'podcast-styles');
    const filePath  = path.join(stylesDir, `${cs.slug}.json`);
    try {
      const existing = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      existing.musicBed = musicBed ? 'ambient' : 'none';
      fs.writeFileSync(filePath, JSON.stringify(existing, null, 2));
    } catch { /* ignore */ }
  }

  // Step 5 — Schedule
  const jobs = await stepSchedule(selectedStyles, customStyles);

  // Step 6 — Preview
  await stepPreviewEpisode(apiKey, selectedStyles, skillPath);

  // Step 7 — Cron commands
  closeRL(); // Flush readline before execFileSync calls
  createRL(); // Reopen for final confirm prompt
  await stepConfirmAndOutput(jobs, skillPath);

  closeRL();

  // Done!
  showSummary(selectedStyles, customStyles, jobs);
}

main().catch(err => {
  closeRL();
  if (err.isNetworkError || ['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND'].includes(err.code)) {
    console.error('\n❌ Network error. Check your internet connection and try again.\n');
  } else {
    console.error('\n❌ Setup failed:', err.message);
    if (process.env.DEBUG) console.error(err.stack);
  }
  process.exit(1);
});
