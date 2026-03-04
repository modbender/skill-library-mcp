#!/usr/bin/env node
/**
 * broadcast.js — Cross-group signal router for OpenClaw
 *
 * Usage:
 *   node broadcast.js --message "Hello!" --groups "github-ops,social-media"
 *   node broadcast.js --message "Alert!" --groups "-1003871838436,-1003578613620"
 *   node broadcast.js --message "All hands!" --groups all --channel telegram
 *
 * Env vars:
 *   OPENCLAW_PORT   — Gateway port (default: 3000)
 *   OPENCLAW_TOKEN  — Gateway auth token
 *   GROUPS_CONFIG_PATH — Path to groups registry JSON
 */

'use strict';

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ── Config ────────────────────────────────────────────────────────────────────
const GATEWAY_PORT = parseInt(process.env.OPENCLAW_PORT || '3000', 10);
const GATEWAY_TOKEN = process.env.OPENCLAW_TOKEN || '';

const GROUPS_CONFIG_PATH = process.env.GROUPS_CONFIG_PATH ||
  path.join(__dirname, '..', 'config', 'groups.json');

function loadGroups() {
  try {
    return JSON.parse(fs.readFileSync(GROUPS_CONFIG_PATH, 'utf8'));
  } catch {
    return {};
  }
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { message: null, groups: null, channel: 'telegram', delay: 500 };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--message' || args[i] === '-m') opts.message = args[++i];
    else if (args[i] === '--groups' || args[i] === '-g') opts.groups = args[++i];
    else if (args[i] === '--channel') opts.channel = args[++i];
    else if (args[i] === '--delay') opts.delay = parseInt(args[++i], 10);
  }
  return opts;
}

function resolveGroups(groupsArg, registry) {
  if (!groupsArg) return Object.values(registry);
  if (groupsArg === 'all') return Object.values(registry);

  return groupsArg.split(',').map(g => {
    g = g.trim();
    // If it's a negative number (Telegram chat ID), use as-is
    if (/^-?\d+$/.test(g)) return g;
    // Otherwise resolve by name
    const resolved = registry[g] || registry[g.replace(/-/g, '_')];
    if (!resolved) {
      console.warn(`⚠️  Unknown group name: "${g}" — skipping`);
      return null;
    }
    return resolved;
  }).filter(Boolean);
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function sendToGateway(channel, to, message, token) {
  return new Promise((resolve) => {
    const body = JSON.stringify({ channel, to, message });
    const options = {
      hostname: 'localhost',
      port: GATEWAY_PORT,
      path: '/api/send',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        resolve({ status: res.statusCode, body: data });
      });
    });
    req.on('error', (err) => {
      resolve({ status: 0, body: err.message });
    });
    req.write(body);
    req.end();
  });
}

async function main() {
  const opts = parseArgs();

  if (!opts.message) {
    console.error('❌ --message is required');
    console.error('   Usage: node broadcast.js --message "Hello!" --groups "github-ops,amazon-ops"');
    process.exit(1);
  }

  const registry = loadGroups();
  const targets = resolveGroups(opts.groups, registry);

  if (targets.length === 0) {
    console.error('❌ No valid targets resolved. Check --groups and config/groups.json');
    process.exit(1);
  }

  console.log(`\n📡 Broadcasting to ${targets.length} group(s) via ${opts.channel}`);
  console.log(`   Message: ${opts.message.slice(0, 80)}${opts.message.length > 80 ? '...' : ''}\n`);

  const results = [];

  for (const target of targets) {
    const { status, body } = await sendToGateway(opts.channel, target, opts.message, GATEWAY_TOKEN);
    const ok = status === 200 || status === 201;
    const label = Object.entries(registry).find(([, v]) => v === target)?.[0] || target;
    const receipt = ok ? '✅' : `❌ (${status})`;
    console.log(`  ${receipt} ${label} (${target})`);
    results.push({ target, label, status, ok });

    if (opts.delay > 0 && targets.indexOf(target) < targets.length - 1) {
      await sleep(opts.delay);
    }
  }

  const succeeded = results.filter(r => r.ok).length;
  const failed = results.filter(r => !r.ok).length;
  console.log(`\n✅ Broadcast complete: ${succeeded} sent, ${failed} failed`);

  if (failed > 0) process.exit(1);
}

main().catch(err => {
  console.error(`FATAL: ${err.message}`);
  process.exit(1);
});
