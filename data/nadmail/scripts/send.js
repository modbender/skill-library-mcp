#!/usr/bin/env node
/**
 * NadMail Send Email Script
 *
 * Usage: node send.js <to> <subject> <body> [--emo <preset|amount>]
 *
 * Examples:
 *   node send.js alice@nadmail.ai "Hello" "How are you?"
 *   node send.js alice@nadmail.ai "Hello" "Great work!" --emo bullish
 *   node send.js alice@nadmail.ai "Hello" "WAGMI!" --emo 0.1
 *
 * Security:
 *   --emo triggers a financial transaction. Interactive confirmation is ALWAYS required.
 *   Daily emo spending is tracked and capped (default: 0.5 MON/day).
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const API_BASE = 'https://api.nadmail.ai';
const CONFIG_DIR = path.join(process.env.HOME, '.nadmail');
const TOKEN_FILE = path.join(CONFIG_DIR, 'token.json');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');
const EMO_TRACKER_FILE = path.join(CONFIG_DIR, 'emo-daily.json');

// Daily emo spending cap (MON) — configurable via NADMAIL_EMO_DAILY_CAP env var
const DEFAULT_EMO_DAILY_CAP = 0.5;
const EMO_DAILY_CAP = parseFloat(process.env.NADMAIL_EMO_DAILY_CAP) || DEFAULT_EMO_DAILY_CAP;

// Emo-buy presets (same tiers as the $DIPLOMAT AI agent)
const EMO_PRESETS = {
  friendly: { amount: 0.01,  label: 'Friendly (+0.01 MON)' },
  bullish:  { amount: 0.025, label: 'Bullish (+0.025 MON)' },
  super:    { amount: 0.05,  label: 'Super Bullish (+0.05 MON)' },
  moon:     { amount: 0.075, label: 'Moon (+0.075 MON)' },
  wagmi:    { amount: 0.1,   label: 'WAGMI (+0.1 MON)' },
};

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) return;
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      to: details.to ? `${details.to.split('@')[0].slice(0, 4)}...@${details.to.split('@')[1]}` : null,
      emo_amount: details.emo_amount || null,
      success: details.success ?? true,
      error: details.error,
    };
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors
  }
}

/**
 * Track daily emo spending and check against cap
 */
function checkEmoDailyLimit(emoAmount) {
  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD

  let tracker = { date: today, total: 0 };
  try {
    if (fs.existsSync(EMO_TRACKER_FILE)) {
      tracker = JSON.parse(fs.readFileSync(EMO_TRACKER_FILE, 'utf8'));
      if (tracker.date !== today) {
        tracker = { date: today, total: 0 };
      }
    }
  } catch {
    tracker = { date: today, total: 0 };
  }

  const newTotal = tracker.total + emoAmount;
  if (newTotal > EMO_DAILY_CAP) {
    return {
      allowed: false,
      spent_today: tracker.total,
      remaining: Math.max(0, EMO_DAILY_CAP - tracker.total),
      cap: EMO_DAILY_CAP,
    };
  }

  return {
    allowed: true,
    spent_today: tracker.total,
    remaining: EMO_DAILY_CAP - tracker.total,
    cap: EMO_DAILY_CAP,
  };
}

function recordEmoSpend(emoAmount) {
  const today = new Date().toISOString().slice(0, 10);

  let tracker = { date: today, total: 0 };
  try {
    if (fs.existsSync(EMO_TRACKER_FILE)) {
      tracker = JSON.parse(fs.readFileSync(EMO_TRACKER_FILE, 'utf8'));
      if (tracker.date !== today) {
        tracker = { date: today, total: 0 };
      }
    }
  } catch {
    tracker = { date: today, total: 0 };
  }

  tracker.total += emoAmount;
  fs.writeFileSync(EMO_TRACKER_FILE, JSON.stringify(tracker, null, 2), { mode: 0o600 });
}

function getToken() {
  if (process.env.NADMAIL_TOKEN) {
    return process.env.NADMAIL_TOKEN;
  }

  if (!fs.existsSync(TOKEN_FILE)) {
    console.error('Not registered yet. Run register.js first.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));

  if (data.saved_at) {
    const hoursSinceSaved = (Date.now() - new Date(data.saved_at).getTime()) / 1000 / 60 / 60;
    if (hoursSinceSaved > 20) {
      console.log('Warning: Token may be expiring soon. Run register.js again if you get auth errors.');
    }
  }

  return data.token;
}

function getArg(name) {
  const args = process.argv.slice(2);
  const idx = args.indexOf(name);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return null;
}

function hasFlag(name) {
  return process.argv.slice(2).includes(name);
}

function parseEmoArg() {
  const emoValue = getArg('--emo');
  if (!emoValue) return 0;

  // Check preset name
  const preset = EMO_PRESETS[emoValue.toLowerCase()];
  if (preset) return preset.amount;

  // Try numeric value
  const num = parseFloat(emoValue);
  if (!isNaN(num) && num >= 0 && num <= 0.1) return num;

  console.error(`Invalid --emo value: "${emoValue}"`);
  console.error('Presets: friendly (0.01), bullish (0.025), super (0.05), moon (0.075), wagmi (0.1)');
  console.error('Or a number between 0 and 0.1');
  process.exit(1);
}

async function main() {
  // --yes flag removed for security: financial transactions always require interactive confirmation

  // Filter out flags and their values from positional args
  const rawArgs = process.argv.slice(2);
  const positional = [];
  for (let i = 0; i < rawArgs.length; i++) {
    if (rawArgs[i] === '--emo') {
      i++; // skip value
      continue;
    }
    positional.push(rawArgs[i]);
  }

  const [to, subject, ...bodyParts] = positional;
  const body = bodyParts.join(' ');

  if (!to || !subject) {
    console.log('NadMail - Send Email\n');
    console.log('Usage: node send.js <to> <subject> <body> [--emo <preset|amount>]\n');
    console.log('Examples:');
    console.log('  node send.js alice@nadmail.ai "Hello" "How are you?"');
    console.log('  node send.js alice@nadmail.ai "Hello" "Great work!" --emo bullish');
    console.log('  node send.js alice@nadmail.ai "Hello" "WAGMI!" --emo 0.1\n');
    console.log('Emo-Buy Presets (extra MON to pump recipient\'s meme coin):');
    for (const [name, preset] of Object.entries(EMO_PRESETS)) {
      console.log(`  --emo ${name.padEnd(10)} ${preset.label} (total: ${(0.001 + preset.amount).toFixed(3)} MON)`);
    }
    console.log('\nFlags:');
    // --yes flag removed: confirmation always required for financial safety
    console.log(`\nDaily emo cap: ${EMO_DAILY_CAP} MON (set NADMAIL_EMO_DAILY_CAP to change)`);
    console.log('Note: Emo-buy only works for @nadmail.ai recipients.');
    console.log('External emails require credits (see: GET /api/credits).');
    process.exit(1);
  }

  const emoAmount = parseEmoArg();
  const isInternal = to.toLowerCase().endsWith('@nadmail.ai');
  const token = getToken();

  // Emo-buy safety checks
  if (emoAmount > 0 && isInternal) {
    // Check daily limit
    const limitCheck = checkEmoDailyLimit(emoAmount);
    if (!limitCheck.allowed) {
      console.error(`\nDaily emo spending limit reached!`);
      console.error(`  Spent today: ${limitCheck.spent_today.toFixed(4)} MON`);
      console.error(`  Daily cap: ${limitCheck.cap} MON`);
      console.error(`  Remaining: ${limitCheck.remaining.toFixed(4)} MON`);
      console.error(`\nSet NADMAIL_EMO_DAILY_CAP to adjust (current: ${EMO_DAILY_CAP} MON)`);
      process.exit(1);
    }

    // Confirmation prompt (always required for financial transactions)
    {
      const presetEntry = Object.entries(EMO_PRESETS).find(([, p]) => p.amount === emoAmount);
      const label = presetEntry ? presetEntry[0] : 'custom';
      console.log(`\nEmo-Buy Confirmation:`);
      console.log(`  Recipient: ${to}`);
      console.log(`  Emo level: ${label} (+${emoAmount} MON)`);
      console.log(`  Total cost: ${(0.001 + emoAmount).toFixed(3)} MON (micro-buy + emo)`);
      console.log(`  Today's emo spending: ${limitCheck.spent_today.toFixed(4)} / ${limitCheck.cap} MON`);

      const answer = await prompt('\nProceed with emo-buy? (yes/no): ');
      if (answer.toLowerCase() !== 'yes' && answer.toLowerCase() !== 'y') {
        console.log('Cancelled. Email not sent.');
        process.exit(0);
      }
    }
  }

  // Build request body
  const reqBody = { to, subject, body: body || '' };
  if (emoAmount > 0 && isInternal) {
    reqBody.emo_amount = emoAmount;
  }

  console.log('Sending email...');
  console.log(`  To: ${to}`);
  console.log(`  Subject: ${subject}`);
  if (emoAmount > 0 && isInternal) {
    const presetEntry = Object.entries(EMO_PRESETS).find(([, p]) => p.amount === emoAmount);
    const label = presetEntry ? presetEntry[0] : 'custom';
    console.log(`  Emo-Boost: ${label} (+${emoAmount} MON, total: ${(0.001 + emoAmount).toFixed(3)} MON)`);
  } else if (emoAmount > 0 && !isInternal) {
    console.log('  Note: Emo-buy skipped (only works for @nadmail.ai recipients)');
  }

  try {
    const res = await fetch(`${API_BASE}/api/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(reqBody),
    });

    const data = await res.json();

    if (data.success) {
      console.log('\nSent!');
      console.log(`  From: ${data.from}`);
      console.log(`  Email ID: ${data.email_id}`);

      if (data.microbuy) {
        const mb = data.microbuy;
        if (mb.emo_boost) {
          console.log(`\n  EMO-BOOSTED $${mb.tokenSymbol || mb.token_symbol}!`);
          console.log(`  Total: ${mb.totalMonSpent || mb.total_mon_spent} MON`);
        } else {
          console.log(`\n  Micro-bought $${mb.tokenSymbol || mb.token_symbol}`);
          console.log(`  Amount: 0.001 MON`);
        }
        if (mb.tokensBought || mb.tokens_bought) {
          console.log(`  Tokens received: ${mb.tokensBought || mb.tokens_bought}`);
        }
        if (mb.priceChangePercent || mb.price_change_percent) {
          console.log(`  Price impact: ${mb.priceChangePercent || mb.price_change_percent}%`);
        }
        if (mb.tx) {
          console.log(`  TX: ${mb.tx}`);
        }
      }

      // Record emo spending
      if (emoAmount > 0 && isInternal) {
        recordEmoSpend(emoAmount);
      }

      logAudit('send_email', { to, emo_amount: emoAmount > 0 ? emoAmount : null, success: true });
    } else {
      console.error('\nFailed:', data.error || JSON.stringify(data));
      if (data.hint) console.error('Hint:', data.hint);
      logAudit('send_email', { to, success: false, error: data.error });
      process.exit(1);
    }
  } catch (err) {
    console.error('\nError:', err.message);
    logAudit('send_email', { to, success: false, error: err.message });
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
