#!/usr/bin/env node
/**
 * SealVera skill status check
 * Shows recent decisions, chain integrity, and retention coverage for this agent.
 */
'use strict';

const http  = require('http');
const https = require('https');

const G = s => `\x1b[32m${s}\x1b[0m`;
const R = s => `\x1b[31m${s}\x1b[0m`;
const D = s => `\x1b[2m${s}\x1b[0m`;
const B = s => `\x1b[1m${s}\x1b[0m`;
const Y = s => `\x1b[33m${s}\x1b[0m`;

const ENDPOINT = (process.env.SEALVERA_ENDPOINT || 'https://app.sealvera.com').replace(/\/$/, '');
const API_KEY  = process.env.SEALVERA_API_KEY || '';
const AGENT    = process.env.SEALVERA_AGENT   || 'openclaw-agent';

if (!API_KEY) {
  console.error(R('✗ SEALVERA_API_KEY not set'));
  process.exit(1);
}

function get(path) {
  return new Promise((resolve, reject) => {
    const url  = new URL(ENDPOINT + path);
    const mod  = url.protocol === 'https:' ? https : http;
    const req  = mod.request({
      hostname: url.hostname,
      port:     url.port || (url.protocol === 'https:' ? 443 : 80),
      path:     url.pathname + (url.search || ''),
      method:   'GET',
      headers:  { 'x-sealvera-key': API_KEY },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch(_) { resolve({ status: res.statusCode, body: {} }); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  console.log(`\n${B('SealVera')} — Agent Status\n`);

  // Org
  const { status: orgStatus, body: orgBody } = await get('/api/org');
  if (orgStatus !== 200) {
    console.error(R('✗ Could not reach SealVera. Check SEALVERA_API_KEY and SEALVERA_ENDPOINT.'));
    process.exit(1);
  }
  const org = orgBody.org || orgBody;
  console.log(B('Organization'));
  console.log(`  Name: ${org.name || org.id || 'default'}`);
  console.log(`  Plan: ${org.tier || 'free'}`);
  console.log('');

  // Recent decisions
  const { body: logsBody } = await get(`/api/logs?agent=${encodeURIComponent(AGENT)}&limit=5`);
  const logs = Array.isArray(logsBody) ? logsBody : (logsBody.logs || []);
  console.log(B(`Recent decisions — ${AGENT}`));
  if (!logs.length) {
    console.log(D('  No decisions logged yet. Run a task to see entries here.'));
  } else {
    logs.forEach(l => {
      const badge   = l.evidence_source === 'Agent-provided' ? G('●') : l.evidence_source === 'native' ? G('◆') : Y('●');
      const ts      = new Date(l.timestamp).toLocaleTimeString();
      const src     = l.evidence_source ? D(` [${l.evidence_source}]`) : '';
      console.log(`  ${badge} ${(l.decision || '-').padEnd(14)} ${(l.action || '').slice(0,32).padEnd(32)} ${D(ts)}${src}`);
    });
  }
  console.log('');

  // Chain integrity — response: { ok, agent, totalEntries, gaps, brokenLinks, lastVerified }
  const { body: chain } = await get(`/api/agents/${encodeURIComponent(AGENT)}/chain-verify`);
  if (chain.ok && chain.gaps && chain.gaps.length === 0 && chain.brokenLinks && chain.brokenLinks.length === 0) {
    console.log(G('✓') + ` Chain integrity: intact (${chain.totalEntries || 0} entries)`);
  } else if (chain.ok === false || (chain.gaps && chain.gaps.length > 0)) {
    console.log(R('✗') + ` Chain integrity: BROKEN — ${chain.gaps?.length || 0} gap(s), ${chain.brokenLinks?.length || 0} broken link(s)`);
  } else if (chain.totalEntries === 0 || chain.totalEntries === undefined) {
    console.log(D('  Chain: no entries yet'));
  } else {
    console.log(G('✓') + ` Chain: ${chain.totalEntries} entries`);
  }

  // Retention — response: { totalEntries, daysCovered, requiredDays, coveragePct, status }
  const { body: ret } = await get('/api/retention-status');
  if (ret.daysCovered !== undefined) {
    const pct   = Math.round(ret.coveragePct || 0);
    const color = pct >= 80 ? G : pct >= 30 ? Y : R;
    console.log(color(`  Retention: ${ret.daysCovered}d covered (${pct}% of ${ret.requiredDays}d EU AI Act requirement)`));
  }

  console.log(`\n${D('Dashboard: ' + ENDPOINT + '/dashboard')}\n`);
}

main().catch(err => {
  console.error(R('Error: ' + err.message));
  process.exit(1);
});
