#!/usr/bin/env node
/**
 * Push fixed images to Amazon listings via SP-API.
 * Serves images via local HTTP server on a public port.
 * Amazon crawls the URLs and updates listings within 15-30 mins.
 *
 * Usage:
 *   node push_images.js --dir ./image_fix/ --sku "MY-SKU" --slots PT03,PT05
 *   node push_images.js --dir ./image_fix/ --from-report report.json
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const SellingPartnerAPI = require('amazon-sp-api');

const CREDS_PATH = process.env.AMAZON_SPAPI_PATH || './amazon-sp-api.json';
function getCfg() { return JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8')); }
function getClient() {
  const creds = getCfg();
  return new SellingPartnerAPI({
    region: creds.region || 'eu',
    refresh_token: creds.refreshToken,
    credentials: {
      SELLING_PARTNER_APP_CLIENT_ID: creds.lwaClientId,
      SELLING_PARTNER_APP_CLIENT_SECRET: creds.lwaClientSecret,
    }
  });
}

const SLOT_ATTR_MAP = {
  MAIN: 'main_product_image_locator',
  PT01: 'other_product_image_locator_1',
  PT02: 'other_product_image_locator_2',
  PT03: 'other_product_image_locator_3',
  PT04: 'other_product_image_locator_4',
  PT05: 'other_product_image_locator_5',
  PT06: 'other_product_image_locator_6',
  PT07: 'other_product_image_locator_7',
  PT08: 'other_product_image_locator_8',
};

function startServer(dir, port = 8899) {
  const server = http.createServer((req, res) => {
    const filePath = path.join(dir, req.url.replace(/^\//, ''));
    if (fs.existsSync(filePath)) {
      res.writeHead(200, { 'Content-Type': 'image/jpeg' });
      fs.createReadStream(filePath).pipe(res);
    } else {
      res.writeHead(404); res.end();
    }
  });
  server.listen(port, '0.0.0.0');
  return server;
}

async function getPublicIp() {
  try {
    const res = await fetch('https://api.ipify.org');
    return res.text();
  } catch { return 'localhost'; }
}

async function patchImage(sp, sku, slot, imageUrl) {
  const cfg = getCfg();
  const attr = SLOT_ATTR_MAP[slot];
  if (!attr) throw new Error(`Unknown slot: ${slot}`);

  return sp.callAPI({
    operation: 'patchListingsItem',
    endpoint: 'listingsItems',
    path: { sellerId: cfg.sellerId, sku },
    query: { marketplaceIds: cfg.marketplace },
    body: {
      productType: process.env.PRODUCT_TYPE || 'PRODUCT',
      patches: [{
        op: 'replace',
        path: `/attributes/${attr}`,
        value: [{ media_location: imageUrl, marketplace_id: cfg.marketplace }]
      }]
    }
  });
}

function parseArgs() {
  const a = process.argv.slice(2);
  const out = { dir: null, sku: null, slots: [], report: null, port: 8899 };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--dir') out.dir = a[++i];
    else if (a[i] === '--sku') out.sku = a[++i];
    else if (a[i] === '--slots') out.slots = a[++i].split(',');
    else if (a[i] === '--from-report') out.report = a[++i];
    else if (a[i] === '--port') out.port = parseInt(a[++i]);
  }
  return out;
}

async function main() {
  const args = parseArgs();
  if (!args.dir) { console.error('--dir required'); process.exit(1); }

  const ip = await getPublicIp();
  const port = args.port;
  const baseUrl = `http://${ip}:${port}`;

  console.log(`\n🚀 Amazon Listing Image Pusher`);
  console.log(`📡 Serving images at ${baseUrl}\n`);

  const server = startServer(args.dir, port);
  const sp = getClient();

  // Build fix list
  let fixes = [];
  if (args.report) {
    const report = JSON.parse(fs.readFileSync(args.report, 'utf8'));
    for (const entry of report.report) {
      for (const issue of entry.issues) {
        const fixedFile = path.join(args.dir, `${entry.sku}_${issue.slot}_fixed.jpg`);
        if (fs.existsSync(fixedFile)) {
          fixes.push({ sku: entry.sku, slot: issue.slot, file: path.basename(fixedFile) });
        }
      }
    }
  } else if (args.sku && args.slots.length) {
    for (const slot of args.slots) {
      const files = fs.readdirSync(args.dir).filter(f => f.includes('_fixed.jpg'));
      const file = files.find(f => f.toLowerCase().includes(slot.toLowerCase()));
      if (file) fixes.push({ sku: args.sku, slot, file });
    }
  } else {
    // Auto-detect: all *_fixed.jpg files in dir
    const files = fs.readdirSync(args.dir).filter(f => f.endsWith('_fixed.jpg'));
    console.log(`Found ${files.length} fixed images. Use --sku + --slots or --from-report for targeted push.`);
    server.close();
    process.exit(0);
  }

  console.log(`Pushing ${fixes.length} image(s)...\n`);
  let success = 0;
  for (const fix of fixes) {
    process.stdout.write(`  ${fix.sku} [${fix.slot}] ${fix.file}... `);
    try {
      const r = await patchImage(sp, fix.sku, fix.slot, `${baseUrl}/${fix.file}`);
      console.log(`✅ ${r?.status || 'ACCEPTED'}`);
      success++;
    } catch (e) {
      console.log(`❌ ${e.message.slice(0, 80)}`);
    }
    await new Promise(r => setTimeout(r, 600));
  }

  console.log(`\n✅ ${success}/${fixes.length} patches accepted`);
  console.log(`⏳ Keeping server alive 15 mins for Amazon to crawl...`);

  setTimeout(() => {
    server.close();
    console.log('🔒 Server closed. Done.');
    process.exit(0);
  }, 15 * 60 * 1000);
}

main().catch(e => { console.error(e.message); process.exit(1); });
