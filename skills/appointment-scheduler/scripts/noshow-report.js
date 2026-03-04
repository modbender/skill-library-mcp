#!/usr/bin/env node
/**
 * Generate no-show reports
 * Usage:
 *   node noshow-report.js
 *   node noshow-report.js --customer "김철수"
 *   node noshow-report.js --month 2026-02
 *   node noshow-report.js --flag-repeat
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const customer = args.includes('--customer') ? args[args.indexOf('--customer') + 1] : null;
const month = args.includes('--month') ? args[args.indexOf('--month') + 1] : null;
const flagRepeat = args.includes('--flag-repeat');

const NOSHOW_DIR = path.join(process.env.HOME, '.openclaw', 'workspace', 'data', 'appointments', 'noshow');
const HISTORY_FILE = path.join(NOSHOW_DIR, 'history.json');
const FLAGGED_FILE = path.join(NOSHOW_DIR, 'flagged-customers.json');

if (!fs.existsSync(HISTORY_FILE)) {
  console.log('ℹ️  No no-show history found');
  process.exit(0);
}

const history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));

if (customer) {
  // Show specific customer history
  const customerNoshows = history.filter(h => h.customer_name === customer);
  console.log(`\n📊 No-show history for ${customer}`);
  console.log('═'.repeat(60));
  console.log(`Total no-shows: ${customerNoshows.length}\n`);
  
  customerNoshows.forEach((h, index) => {
    console.log(`${index + 1}. ${h.date} ${h.time} - ${h.service}`);
    console.log(`   Marked: ${h.marked_at}`);
  });
  console.log('\n');
  
} else if (month) {
  // Monthly report
  const monthNoshows = history.filter(h => h.date.startsWith(month));
  console.log(`\n📊 No-show report for ${month}`);
  console.log('═'.repeat(60));
  console.log(`Total no-shows: ${monthNoshows.length}\n`);
  
  // Group by customer
  const byCustomer = {};
  monthNoshows.forEach(h => {
    const key = h.customer_phone || h.customer_email || h.customer_name;
    if (!byCustomer[key]) {
      byCustomer[key] = {
        name: h.customer_name,
        contact: h.customer_phone || h.customer_email,
        noshows: []
      };
    }
    byCustomer[key].noshows.push(h);
  });
  
  // Display
  Object.values(byCustomer).forEach(customer => {
    console.log(`${customer.name} (${customer.contact || 'N/A'}): ${customer.noshows.length} no-shows`);
  });
  console.log('\n');
  
} else if (flagRepeat) {
  // Flag repeat offenders
  const CONFIG_FILE = path.join(process.env.HOME, '.openclaw', 'workspace', 'config', 'appointment-scheduler.json');
  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  const threshold = config.noshow_policy?.flag_threshold || 3;
  
  // Group by customer
  const byCustomer = {};
  history.forEach(h => {
    const key = h.customer_phone || h.customer_email || h.customer_name;
    if (!byCustomer[key]) {
      byCustomer[key] = {
        name: h.customer_name,
        phone: h.customer_phone,
        email: h.customer_email,
        noshows: []
      };
    }
    byCustomer[key].noshows.push(h);
  });
  
  // Find repeat offenders
  let flagged = {};
  if (fs.existsSync(FLAGGED_FILE)) {
    flagged = JSON.parse(fs.readFileSync(FLAGGED_FILE, 'utf8'));
  }
  
  let newFlags = 0;
  Object.entries(byCustomer).forEach(([key, customer]) => {
    if (customer.noshows.length >= threshold && !flagged[key]) {
      flagged[key] = {
        customer_name: customer.name,
        phone: customer.phone,
        email: customer.email,
        noshow_count: customer.noshows.length,
        flagged_at: new Date().toISOString(),
        require_deposit: config.noshow_policy?.require_deposit_when_flagged || false
      };
      newFlags++;
    }
  });
  
  if (newFlags > 0) {
    fs.writeFileSync(FLAGGED_FILE, JSON.stringify(flagged, null, 2));
    console.log(`✅ Flagged ${newFlags} repeat offenders (threshold: ${threshold} no-shows)`);
  } else {
    console.log('ℹ️  No new customers to flag');
  }
  
} else {
  // Overall report
  console.log('\n📊 Overall No-show Report');
  console.log('═'.repeat(60));
  console.log(`Total no-shows: ${history.length}\n`);
  
  // Group by customer
  const byCustomer = {};
  history.forEach(h => {
    const key = h.customer_phone || h.customer_email || h.customer_name;
    if (!byCustomer[key]) {
      byCustomer[key] = {
        name: h.customer_name,
        contact: h.customer_phone || h.customer_email,
        noshows: []
      };
    }
    byCustomer[key].noshows.push(h);
  });
  
  // Sort by no-show count
  const sorted = Object.values(byCustomer).sort((a, b) => b.noshows.length - a.noshows.length);
  
  console.log('Top offenders:');
  sorted.slice(0, 10).forEach((customer, index) => {
    const flag = customer.noshows.length >= 3 ? '🚩' : '';
    console.log(`${index + 1}. ${customer.name} (${customer.contact || 'N/A'}): ${customer.noshows.length} no-shows ${flag}`);
  });
  
  // Show flagged customers
  if (fs.existsSync(FLAGGED_FILE)) {
    const flagged = JSON.parse(fs.readFileSync(FLAGGED_FILE, 'utf8'));
    const flaggedCount = Object.keys(flagged).length;
    console.log(`\n🚩 Flagged customers: ${flaggedCount}`);
  }
  
  console.log('\n');
}
