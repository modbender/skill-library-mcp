#!/usr/bin/env node
/**
 * Portmanteau Forge (offline)
 * Generates candidate names from building blocks.
 * Does NOT check ENS availability.
 *
 * Usage:
 *   node scripts/forge.mjs --max 10 --count 30 --lane social
 *   node scripts/forge.mjs --max 10 --pattern "{work}{mesh}" --count 50
 */

const args = process.argv.slice(2);
const getArg = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};

const maxLen = parseInt(getArg('max', '10'), 10);
const count = parseInt(getArg('count', '40'), 10);
const lane = getArg('lane', 'mix');
const pattern = getArg('pattern', '');

const blocks = {
  work: ['work', 'gig', 'bounty', 'job', 'task', 'quest', 'sprint'],
  social: ['crew', 'guild', 'coop', 'team', 'circle', 'swarm'],
  coord: ['handoff', 'relay', 'dispatch', 'router', 'queue', 'sync', 'link', 'bridge'],
  trust: ['claim', 'record', 'proof', 'attest', 'receipt', 'audit', 'verify', 'badge'],
  money: ['pay', 'tip', 'fund', 'split', 'settle', 'escrow'],
  net: ['mesh', 'hub', 'hq', 'lane', 'rail', 'ring', 'fabric'],
  misc: ['log', 'pack', 'loop', 'stack'],
};

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function renderPattern(p) {
  return p.replace(/\{(.*?)\}/g, (_, key) => {
    const list = blocks[key] || [];
    if (!list.length) return '';
    return pick(list);
  });
}

function genOne() {
  if (pattern) return renderPattern(pattern);

  // High hit-rate patterns
  const patterns = [
    '{work}{net}',
    '{work}{social}',
    '{work}{misc}',
    '{trust}{misc}',
    '{money}{net}',
    '{coord}{net}',
    '{coord}{social}',
    '{bounty}{net}',
  ];

  // Lane weighting
  let p;
  if (lane === 'social') p = pick(['{work}{social}', '{coord}{social}', '{money}{social}']);
  else if (lane === 'trust') p = pick(['{trust}{misc}', '{trust}{net}', '{trust}{social}']);
  else if (lane === 'money') p = pick(['{money}{net}', '{money}{misc}', '{money}{social}']);
  else p = pick(patterns);

  // {bounty} special-case
  return renderPattern(p.replace('{bounty}', 'bounty'));
}

function ok(name) {
  if (!name) return false;
  if (name.length > maxLen) return false;
  if (!/^[a-z]+$/.test(name)) return false;
  // avoid awkward repeats
  if (/(.)\1\1/.test(name)) return false;
  return true;
}

const out = new Set();
let guard = 0;
while (out.size < count && guard++ < count * 200) {
  const n = genOne().toLowerCase();
  if (ok(n)) out.add(n);
}

for (const n of out) console.log(n);
