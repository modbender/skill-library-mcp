#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const WORKDIR = __dirname;
const STATE_PATH = path.join(WORKDIR, 'shipping-state.json');
const ENV_PATH = path.join(WORKDIR, '.env');

function loadEnv(file) {
  const env = {};
  if (!fs.existsSync(file)) return env;
  const txt = fs.readFileSync(file, 'utf8');
  for (const line of txt.split('\n')) {
    const m = line.match(/^([^#=]+)=(.*)$/);
    if (m) env[m[1].trim()] = m[2].trim();
  }
  return env;
}

function loadState() {
  if (!fs.existsSync(STATE_PATH)) {
    return { lastCheck: null, processedExpeditedOrderIds: [] };
  }
  try { return JSON.parse(fs.readFileSync(STATE_PATH, 'utf8')); }
  catch { return { lastCheck: null, processedExpeditedOrderIds: [] }; }
}

function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

async function callShipStation(endpoint, apiKey, apiSecret) {
  const auth = Buffer.from(`${apiKey}:${apiSecret}`).toString('base64');
  const res = await fetch(`https://ssapi.shipstation.com${endpoint}`, {
    headers: { Authorization: `Basic ${auth}`, 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error(`ShipStation API error: ${res.status} ${res.statusText}`);
  return res.json();
}

function isExpedited(order) {
  const haystack = [
    order.requestedShippingService,
    order.serviceCode,
    order.carrierCode,
    order.shippingService,
    order.advancedOptions?.customField1,
    order.advancedOptions?.customField2,
    order.advancedOptions?.customField3,
  ].filter(Boolean).join(' ').toLowerCase();

  const patterns = [
    'expedited', 'expedite', 'second day', '2-day', '2 day', 'two day',
    'priority', 'overnight', 'next day', 'one day', 'express'
  ];

  return patterns.some(p => haystack.includes(p));
}

(async () => {
  const env = loadEnv(ENV_PATH);
  const apiKey = process.env.SHIPSTATION_API_KEY || env.SHIPSTATION_API_KEY;
  const apiSecret = process.env.SHIPSTATION_API_SECRET || env.SHIPSTATION_API_SECRET;

  if (!apiKey || !apiSecret || apiKey.includes('your_')) {
    console.error('Missing ShipStation credentials');
    process.exit(2);
  }

  const state = loadState();
  const since = new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString();

  try {
    const data = await callShipStation(`/orders?modifyDateStart=${since}&pageSize=100`, apiKey, apiSecret);
    const orders = data.orders || [];

    const expedited = orders.filter(o => {
      if (state.processedExpeditedOrderIds.includes(o.orderId)) return false;
      return isExpedited(o);
    });

    for (const o of expedited) state.processedExpeditedOrderIds.push(o.orderId);
    state.processedExpeditedOrderIds = state.processedExpeditedOrderIds.slice(-2000);
    state.lastCheck = Date.now();
    saveState(state);

    const out = {
      scanned: orders.length,
      expeditedNew: expedited.map(o => ({
        orderId: o.orderNumber,
        customer: o.shipTo?.name || 'Unknown',
        total: o.orderTotal,
        marketplace: o.advancedOptions?.source || o.marketplace || 'unknown',
        service: o.requestedShippingService || o.serviceCode || o.carrierCode || 'unknown',
        orderDate: o.orderDate
      }))
    };

    console.log(JSON.stringify(out, null, 2));
    process.exit(expedited.length > 0 ? 1 : 0);
  } catch (e) {
    console.error(e.message);
    process.exit(2);
  }
})();
