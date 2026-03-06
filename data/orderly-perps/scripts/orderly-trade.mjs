#!/usr/bin/env node
/**
 * Orderly Network Trade Tool
 * Opens perp positions for funding rate farming
 */

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const CONFIG = {
  ORDERLY_KEYS_FILE: process.env.ORDERLY_KEYS_FILE || path.join(process.env.HOME || '', '.orderly-keys.json'),
  ORDERLY_API: 'https://api-evm.orderly.org'
};

function loadOrderlyKeys() {
  if (!fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    throw new Error('Orderly keys not found. Run orderly-register.mjs first.');
  }
  return JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
}

function signMessage(message, keys) {
  const secretKeyHex = keys.priv_key_hex;
  const secretKeyBytes = Buffer.from(secretKeyHex, 'hex');
  
  const privateKey = crypto.createPrivateKey({
    key: Buffer.concat([
      Buffer.from('302e020100300506032b657004220420', 'hex'),
      secretKeyBytes
    ]),
    format: 'der',
    type: 'pkcs8'
  });
  
  const signature = crypto.sign(null, Buffer.from(message), privateKey);
  return signature.toString('base64');
}

async function getSymbolInfo(symbol) {
  const url = `${CONFIG.ORDERLY_API}/v1/public/info/${symbol}`;
  const response = await fetch(url);
  return response.json();
}

async function placeOrder(symbol, side, quantity, orderType = 'MARKET') {
  const keys = loadOrderlyKeys();
  const timestamp = Date.now();
  
  // Create order request
  const orderData = {
    symbol: symbol,
    order_type: orderType,
    side: side.toUpperCase(),
    order_quantity: quantity,
    reduce_only: false
  };
  
  const bodyStr = JSON.stringify(orderData);
  const method = 'POST';
  const urlPath = '/v1/order';
  const message = `${timestamp}${method}${urlPath}${bodyStr}`;
  
  const signature = signMessage(message, keys);
  
  console.log(`\n📤 Placing order...`);
  console.log(`   Symbol: ${symbol}`);
  console.log(`   Side: ${side}`);
  console.log(`   Quantity: ${quantity}`);
  console.log(`   Type: ${orderType}`);
  
  const response = await fetch(`${CONFIG.ORDERLY_API}${urlPath}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'orderly-account-id': keys.account_id,
      'orderly-key': keys.orderly_key,
      'orderly-signature': signature,
      'orderly-timestamp': timestamp.toString()
    },
    body: bodyStr
  });
  
  const data = await response.json();
  return data;
}

async function getPositions() {
  const keys = loadOrderlyKeys();
  const timestamp = Date.now();
  
  const method = 'GET';
  const urlPath = '/v1/positions';
  const message = `${timestamp}${method}${urlPath}`;
  
  const signature = signMessage(message, keys);
  
  const response = await fetch(`${CONFIG.ORDERLY_API}${urlPath}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'orderly-account-id': keys.account_id,
      'orderly-key': keys.orderly_key,
      'orderly-signature': signature,
      'orderly-timestamp': timestamp.toString()
    }
  });
  
  return response.json();
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  console.log(`\n📊 Orderly Trade Tool`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  if (command === 'positions') {
    const positions = await getPositions();
    console.log(`\n📍 Current Positions:`);
    console.log(JSON.stringify(positions, null, 2));
    return;
  }
  
  if (command === 'buy' || command === 'sell') {
    const symbol = args[1];
    const quantity = parseFloat(args[2]);
    
    if (!symbol || !quantity) {
      console.log(`\nUsage: node orderly-trade.mjs buy|sell <SYMBOL> <QUANTITY>`);
      console.log(`Example: node orderly-trade.mjs buy PERP_SPX500_USDC 0.01`);
      process.exit(1);
    }
    
    // Get symbol info first
    console.log(`\n📋 Getting symbol info...`);
    const info = await getSymbolInfo(symbol);
    if (!info.success) {
      console.log(`❌ Symbol not found: ${symbol}`);
      console.log(JSON.stringify(info, null, 2));
      process.exit(1);
    }
    console.log(`   ${symbol} - min qty: ${info.data.base_min}, tick: ${info.data.quote_tick}`);
    
    // Place order
    const result = await placeOrder(symbol, command.toUpperCase(), quantity);
    
    if (result.success) {
      console.log(`\n✅ ORDER PLACED!`);
      console.log(`   Order ID: ${result.data.order_id}`);
      console.log(`   Status: ${result.data.status}`);
    } else {
      console.log(`\n❌ Order failed:`);
      console.log(JSON.stringify(result, null, 2));
    }
    return;
  }
  
  console.log(`\nUsage:`);
  console.log(`  node orderly-trade.mjs positions            - View positions`);
  console.log(`  node orderly-trade.mjs buy <SYMBOL> <QTY>   - Buy/Long`);
  console.log(`  node orderly-trade.mjs sell <SYMBOL> <QTY>  - Sell/Short`);
  console.log(`\nExamples:`);
  console.log(`  node orderly-trade.mjs buy PERP_SPX500_USDC 0.01`);
  console.log(`  node orderly-trade.mjs sell PERP_ETH_USDC 0.001`);
}

main().catch(console.error);
