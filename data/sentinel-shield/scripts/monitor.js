#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const https = require('node:https');

const DATA_DIR = path.resolve(__dirname, '..', 'data');
const COUNTS_FILE = path.join(DATA_DIR, 'call_counts.json');
const ALERTS_FILE = path.join(DATA_DIR, 'alerts.json');

function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'config', 'shield.json'), 'utf8'));
  } catch { return { rateLimit: { maxCalls: 50, windowSeconds: 60, alertThreshold: 40 } }; }
}

function loadCounts() {
  try { return JSON.parse(fs.readFileSync(COUNTS_FILE, 'utf8')); }
  catch { return { calls: [], windowStart: Date.now() }; }
}

function saveCounts(counts) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(COUNTS_FILE, JSON.stringify(counts));
}

function loadAlerts() {
  try { return JSON.parse(fs.readFileSync(ALERTS_FILE, 'utf8')); }
  catch { return []; }
}

function saveAlert(alert) {
  const alerts = loadAlerts();
  alerts.push({ ...alert, timestamp: new Date().toISOString() });
  // Keep last 500 alerts
  while (alerts.length > 500) alerts.shift();
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(ALERTS_FILE, JSON.stringify(alerts, null, 2));
}

function sendTelegram(config, message) {
  if (!config.telegram?.enabled || !config.telegram?.botToken || !config.telegram?.chatId) return;
  const data = JSON.stringify({ chat_id: config.telegram.chatId, text: message, parse_mode: 'Markdown' });
  const req = https.request({
    hostname: 'api.telegram.org',
    path: `/bot${config.telegram.botToken}/sendMessage`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
  });
  req.on('error', () => {}); // fire and forget
  req.write(data);
  req.end();
}

function recordCall(toolName) {
  const config = loadConfig();
  const rl = config.rateLimit;
  const counts = loadCounts();
  const now = Date.now();
  const windowMs = rl.windowSeconds * 1000;

  // Prune old calls outside window
  counts.calls = counts.calls.filter(t => now - t < windowMs);
  counts.calls.push(now);
  saveCounts(counts);

  const count = counts.calls.length;

  if (count >= rl.maxCalls) {
    const alert = { level: 'HIGH', type: 'RATE_LIMIT_HIT', message: `Rate limit hit: ${count}/${rl.maxCalls} calls in ${rl.windowSeconds}s`, tool: toolName };
    saveAlert(alert);
    sendTelegram(config, `🔴 *RATE LIMIT HIT*\n${count}/${rl.maxCalls} calls in ${rl.windowSeconds}s\nTool: ${toolName}`);
    return { blocked: true, count, max: rl.maxCalls };
  }

  if (count >= rl.alertThreshold) {
    const alert = { level: 'MEDIUM', type: 'RATE_LIMIT_WARNING', message: `Rate limit warning: ${count}/${rl.maxCalls} (${Math.round(count/rl.maxCalls*100)}%)`, tool: toolName };
    saveAlert(alert);
    sendTelegram(config, `⚠️ *Rate Limit Warning*\n${count}/${rl.maxCalls} calls (${Math.round(count/rl.maxCalls*100)}%)`);
  }

  return { blocked: false, count, max: rl.maxCalls };
}

function getStatus() {
  const config = loadConfig();
  const counts = loadCounts();
  const now = Date.now();
  const windowMs = config.rateLimit.windowSeconds * 1000;
  const activeCalls = counts.calls.filter(t => now - t < windowMs);
  return { current: activeCalls.length, max: config.rateLimit.maxCalls, windowSeconds: config.rateLimit.windowSeconds };
}

module.exports = { recordCall, getStatus, loadAlerts, saveAlert, sendTelegram, loadConfig };
