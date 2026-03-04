#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const BASE_DIR = path.resolve(__dirname, '..');
const VERSION = '0.2.0';

const { scan } = require('./injectionScanner');
const { init: initBaselines, check: checkFiles } = require('./fileIntegrity');
const { getStatus: getRateStatus, loadAlerts, saveAlert, loadConfig } = require('./monitor');

function loadShieldConfig() {
  return loadConfig();
}

function cmd_status() {
  const config = loadShieldConfig();
  const rate = getRateStatus();
  const integrity = checkFiles(config.monitoredFiles || []);
  const changes = integrity.filter(r => r.status === 'CHANGED').length;
  const alerts = loadAlerts();
  const lastAlert = alerts.length > 0 ? alerts[alerts.length - 1].timestamp : 'None';

  console.log(`\n🛡️  Sentinel Shield v${VERSION} — ACTIVE`);
  console.log('━'.repeat(40));
  console.log(`Rate Limit:     ${rate.current}/${rate.max} calls this window`);
  console.log(`Injection Scan: ${config.injectionScanning !== false ? 'ENABLED' : 'DISABLED'} (16 patterns)`);
  console.log(`File Integrity: ${integrity.length} files monitored, ${changes} changes`);
  console.log(`Last Alert:     ${lastAlert}`);
  console.log(`Alerts (24h):   ${alerts.filter(a => Date.now() - new Date(a.timestamp).getTime() < 86400000).length}`);
  console.log();
}

function cmd_audit() {
  const config = loadShieldConfig();
  console.log('\n🛡️  Sentinel Shield — Full Audit');
  console.log('━'.repeat(40));

  // Rate limit
  const rate = getRateStatus();
  console.log(`\n📊 Rate Limiting`);
  console.log(`  Window: ${rate.windowSeconds}s | Current: ${rate.current}/${rate.max}`);

  // File integrity
  console.log(`\n🔒 File Integrity`);
  const results = checkFiles(config.monitoredFiles || []);
  for (const r of results) {
    const icon = r.status === 'OK' ? '✅' : r.status === 'CHANGED' ? '🔴' : '⚠️';
    console.log(`  ${icon} ${r.file} — ${r.status}`);
  }

  // Injection scanner
  console.log(`\n🔍 Injection Scanner: ${config.injectionScanning !== false ? 'ACTIVE' : 'DISABLED'}`);

  // Recent alerts
  const alerts = loadAlerts();
  const recent = alerts.slice(-5);
  console.log(`\n🚨 Recent Alerts (last 5 of ${alerts.length} total)`);
  if (recent.length === 0) console.log('  No alerts recorded');
  for (const a of recent) {
    console.log(`  [${a.level}] ${a.timestamp} — ${a.message}`);
  }
  console.log();
}

function cmd_alerts(hours = 24) {
  const alerts = loadAlerts();
  const cutoff = Date.now() - hours * 3600000;
  const recent = alerts.filter(a => new Date(a.timestamp).getTime() > cutoff);
  console.log(`\n🚨 Alerts — Last ${hours} hours (${recent.length} total)`);
  console.log('━'.repeat(40));
  if (recent.length === 0) { console.log('  No alerts'); return; }
  for (const a of recent) {
    console.log(`  [${a.level}] ${a.timestamp}`);
    console.log(`    ${a.type}: ${a.message}`);
  }
  console.log();
}

function cmd_ratelimit() {
  const rate = getRateStatus();
  const pct = Math.round(rate.current / rate.max * 100);
  console.log(`\n📊 Rate Limit Status`);
  console.log('━'.repeat(40));
  console.log(`  Current: ${rate.current}/${rate.max} (${pct}%)`);
  console.log(`  Window:  ${rate.windowSeconds}s`);
  const bar = '█'.repeat(Math.round(pct / 5)) + '░'.repeat(20 - Math.round(pct / 5));
  console.log(`  [${bar}] ${pct}%`);
  console.log();
}

function cmd_kill() {
  saveAlert({ level: 'CRITICAL', type: 'KILL_SWITCH', message: 'Kill switch activated manually' });
  // Reset rate counters
  const countsFile = path.join(BASE_DIR, 'data', 'call_counts.json');
  fs.writeFileSync(countsFile, JSON.stringify({ calls: [], windowStart: Date.now() }));
  console.log('🔴 KILL SWITCH ACTIVATED');
  console.log('  Rate counters reset');
  console.log('  Kill event logged');
}

function cmd_scan(text) {
  if (!text) { console.error('Usage: sentinel scan --text "content to check"'); process.exit(1); }
  const result = scan(text);
  console.log(`\n🔍 Injection Scan Results`);
  console.log('━'.repeat(40));
  console.log(`  Status: ${result.clean ? '✅ CLEAN' : '🔴 THREATS DETECTED'}`);
  console.log(`  Scanned: ${result.scannedLength} chars against ${result.patternCount} patterns`);
  if (!result.clean) {
    console.log(`  Findings:`);
    for (const f of result.findings) {
      console.log(`    [${f.severity.toUpperCase()}] ${f.id}: "${f.matched}"`);
    }
  }
  console.log();
}

function cmd_init() {
  const config = loadShieldConfig();
  const baselines = initBaselines(config.monitoredFiles || []);
  console.log('🛡️  Baselines initialized');
  for (const [file, info] of Object.entries(baselines)) {
    const status = info.hash.startsWith('ERROR') || info.hash === 'FILE_NOT_FOUND' ? '⚠️' : '✅';
    console.log(`  ${status} ${file} → ${info.hash.substring(0, 16)}...`);
  }
  saveAlert({ level: 'INFO', type: 'INIT', message: `Baselines initialized for ${Object.keys(baselines).length} files` });
}

// CLI router
const args = process.argv.slice(2);
const cmd = args[0];

switch (cmd) {
  case 'status': cmd_status(); break;
  case 'audit': cmd_audit(); break;
  case 'alerts': {
    const hoursIdx = args.indexOf('--hours');
    const hours = hoursIdx >= 0 ? parseInt(args[hoursIdx + 1]) || 24 : 24;
    cmd_alerts(hours);
    break;
  }
  case 'ratelimit': cmd_ratelimit(); break;
  case 'kill': cmd_kill(); break;
  case 'scan': {
    const textIdx = args.indexOf('--text');
    const text = textIdx >= 0 ? args.slice(textIdx + 1).join(' ') : null;
    cmd_scan(text);
    break;
  }
  case 'init': cmd_init(); break;
  default:
    console.log(`Sentinel Shield v${VERSION}`);
    console.log('Commands: status | audit | alerts [--hours N] | ratelimit | kill | scan --text "..." | init');
}
