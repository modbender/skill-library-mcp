#!/usr/bin/env node
/**
 * Orderly Funding History Tool
 * Queries funding payment history with proper authentication
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

// Load stored keys
function loadKeys() {
  if (!fs.existsSync(CONFIG.ORDERLY_KEYS_FILE)) {
    throw new Error('Orderly keys not found. Run orderly-register.mjs first.');
  }
  return JSON.parse(fs.readFileSync(CONFIG.ORDERLY_KEYS_FILE, 'utf8'));
}

// Sign a message with ed25519 key
function signMessage(message, privateKeyHex) {
  const privateKey = crypto.createPrivateKey({
    key: Buffer.concat([
      Buffer.from('302e020100300506032b657004220420', 'hex'),
      Buffer.from(privateKeyHex, 'hex')
    ]),
    format: 'der',
    type: 'pkcs8'
  });
  
  const signature = crypto.sign(null, Buffer.from(message), privateKey);
  return signature.toString('base64url');
}

// Make authenticated GET request to Orderly
async function authenticatedGet(endpoint, keys) {
  const timestamp = Date.now();
  const method = 'GET';
  const urlPath = endpoint;
  
  // Message to sign: timestamp + method + path
  const message = `${timestamp}${method}${urlPath}`;
  
  // Sign with orderly secret (extract hex from ed25519:xxx format)
  const signature = signMessage(message, keys.priv_key_hex);
  
  const headers = {
    'Content-Type': 'application/json',
    'orderly-timestamp': timestamp.toString(),
    'orderly-account-id': keys.account_id,
    'orderly-key': keys.orderly_key,
    'orderly-signature': signature
  };
  
  const response = await fetch(`${CONFIG.ORDERLY_API}${endpoint}`, { headers });
  return response.json();
}

// Format funding history nicely
async function formatHistory(data) {
  if (!data.success || !data.data?.rows?.length) {
    console.log('\n📝 No funding payments received yet.');
    // Calculate actual time to next funding
    try {
      const fundingInfo = await fetch('https://api-evm.orderly.org/v1/public/funding_rate/PERP_SPX500_USDC');
      const fundingData = await fundingInfo.json();
      if (fundingData.success) {
        const nextTime = fundingData.data.next_funding_time;
        const minsLeft = Math.round((nextTime - Date.now()) / 60000);
        if (minsLeft > 60) {
          console.log(`   Next funding settlement in ${Math.floor(minsLeft/60)}h ${minsLeft%60}m\n`);
        } else {
          console.log(`   Next funding settlement in ${minsLeft}m\n`);
        }
      }
    } catch (e) {
      console.log('   Waiting for first funding settlement...\n');
    }
    return;
  }
  
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log('║               FUNDING PAYMENT HISTORY                          ║');
  console.log('╚════════════════════════════════════════════════════════════════╝\n');
  
  let totalCollected = 0;
  let totalPaid = 0;
  
  for (const row of data.data.rows) {
    const time = new Date(row.payment_time).toLocaleString();
    const amount = row.funding_fee;
    const rate = (row.funding_rate * 100).toFixed(4);
    const symbol = row.symbol.replace('PERP_', '').replace('_USDC', '');
    
    if (amount < 0) {
      // Negative = we received (counterintuitive but that's how Orderly reports)
      totalCollected += Math.abs(amount);
      console.log(`✅ ${time} | ${symbol.padEnd(8)} | +$${Math.abs(amount).toFixed(6)} collected | Rate: ${rate}%`);
    } else {
      totalPaid += amount;
      console.log(`❌ ${time} | ${symbol.padEnd(8)} | -$${amount.toFixed(6)} paid | Rate: ${rate}%`);
    }
  }
  
  console.log('\n────────────────────────────────────────────────────');
  console.log(`Total Collected: $${totalCollected.toFixed(6)}`);
  console.log(`Total Paid:      $${totalPaid.toFixed(6)}`);
  console.log(`Net:             $${(totalCollected - totalPaid).toFixed(6)}`);
  console.log('────────────────────────────────────────────────────\n');
}

// Check for new payments since last check (alert mode)
async function checkNewPayments(keys) {
  const stateFile = path.join(__dirname, '..', 'data', 'funding-state.json');
  
  let lastPaymentTime = 0;
  if (fs.existsSync(stateFile)) {
    const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    lastPaymentTime = state.lastPaymentTime || 0;
  }
  
  const result = await authenticatedGet('/v1/funding_fee/history', keys);
  
  if (!result.success || !result.data?.rows?.length) {
    // No payments yet
    const fundingInfo = await fetch('https://api-evm.orderly.org/v1/public/funding_rate/PERP_SPX500_USDC');
    const fundingData = await fundingInfo.json();
    if (fundingData.success) {
      const nextTime = fundingData.data.next_funding_time;
      const minsLeft = Math.round((nextTime - Date.now()) / 60000);
      console.log(`📭 No funding payments yet. Next settlement in ${minsLeft}m`);
    }
    return { newPayments: [], total: 0 };
  }
  
  const rows = result.data.rows;
  const newPayments = [];
  let totalNew = 0;
  
  for (const row of rows) {
    if (row.payment_time <= lastPaymentTime) break;
    
    const amount = Math.abs(row.funding_fee);
    const symbol = row.symbol.replace('PERP_', '').replace('_USDC', '');
    const collected = row.funding_fee < 0; // Negative = collected
    
    newPayments.push({
      time: new Date(row.payment_time).toISOString(),
      symbol,
      amount: collected ? amount : -amount,
      rate: row.funding_rate
    });
    
    if (collected) totalNew += amount;
  }
  
  // Save new state
  if (rows.length > 0) {
    fs.mkdirSync(path.dirname(stateFile), { recursive: true });
    fs.writeFileSync(stateFile, JSON.stringify({
      lastPaymentTime: rows[0].payment_time,
      lastCheck: Date.now()
    }));
  }
  
  return { newPayments, total: totalNew };
}

// Update funding-payments.json for dashboard
function updateFundingPaymentsFile(newPayments) {
  const paymentsFile = path.join(__dirname, '..', 'data', 'funding-payments.json');
  
  let data = { payments: [], summary: { totalCollected: 0, paymentCount: 0, startDate: null } };
  
  if (fs.existsSync(paymentsFile)) {
    try {
      data = JSON.parse(fs.readFileSync(paymentsFile, 'utf8'));
    } catch (e) {
      // Start fresh if corrupted
    }
  }
  
  // Add new payments
  for (const p of newPayments) {
    if (p.amount > 0) {
      data.payments.push({
        timestamp: p.time,
        symbol: p.symbol,
        amount: p.amount,
        rate: p.rate
      });
      data.summary.totalCollected += p.amount;
      data.summary.paymentCount++;
      if (!data.summary.startDate) {
        data.summary.startDate = p.time;
      }
    }
  }
  
  fs.writeFileSync(paymentsFile, JSON.stringify(data, null, 2));
  return data;
}

async function main() {
  const alertMode = process.argv.includes('--alert');
  
  try {
    const keys = loadKeys();
    
    if (alertMode) {
      // Alert mode: only output if there are new payments
      const { newPayments, total } = await checkNewPayments(keys);
      
      if (newPayments.length > 0) {
        // Update funding-payments.json for dashboard
        const updated = updateFundingPaymentsFile(newPayments);
        
        console.log(`🎉 FUNDING COLLECTED!`);
        for (const p of newPayments) {
          const sign = p.amount > 0 ? '+' : '';
          console.log(`   ${p.symbol}: ${sign}$${Math.abs(p.amount).toFixed(6)}`);
        }
        console.log(`   Total: +$${total.toFixed(6)} USDC`);
        console.log(`   Dashboard: $${updated.summary.totalCollected.toFixed(6)} total, ${updated.summary.paymentCount} payments`);
        
        // Sync to dashboard repo
        const dashboardDataDir = path.join(__dirname, '..', '..', 'ori-dashboard', 'data');
        if (fs.existsSync(dashboardDataDir)) {
          fs.copyFileSync(
            path.join(__dirname, '..', 'data', 'funding-payments.json'),
            path.join(dashboardDataDir, 'funding-payments.json')
          );
          console.log('   ✅ Dashboard synced');
        }
        
        console.log('ALERT:NEW_FUNDING');
      }
      return;
    }
    
    // Normal mode: show full history
    console.log('\n🔍 Querying Orderly Funding History...\n');
    console.log(`Account: ${keys.account_id.slice(0, 10)}...`);
    
    // Query funding fee history
    const result = await authenticatedGet('/v1/funding_fee/history', keys);
    
    if (!result.success) {
      console.log('❌ API Error:', result.message || JSON.stringify(result));
      return;
    }
    
    await formatHistory(result);
    
    // Also show current expected payment
    const posResult = await authenticatedGet('/v1/positions', keys);
    if (posResult.success && posResult.data?.rows?.length) {
      console.log('📊 Current Positions:');
      for (const pos of posResult.data.rows) {
        const symbol = pos.symbol.replace('PERP_', '').replace('_USDC', '');
        console.log(`   ${symbol}: ${pos.position_qty} @ $${pos.average_open_price}`);
      }
    }
    
  } catch (err) {
    console.error('Error:', err.message);
  }
}

main();
