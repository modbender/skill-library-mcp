#!/usr/bin/env node
/**
 * Compare P&L output with bookkeeper data
 * 
 * This uses the generalizable P&L system which:
 * - Applies Stripe gross-up automatically
 * - Uses month offset for accrual basis
 * - Adds synthetic amortization
 * 
 * Usage: node compare-with-bookkeeper.mjs <entity_id> <bookkeeper_excel_dir>
 */

import ExcelJS from 'exceljs';
import { getDb } from './lib/db.js';
import { buildPnl } from './lib/pnl.js';
import { join } from 'path';
import { readdir } from 'fs/promises';

const db = getDb();

async function parseBookkeeperPnL(dir) {
  // Find the main P&L file
  const files = await readdir(dir);
  const pnlFile = files.find(f => f.includes('Income_Statement') && f.endsWith('.xlsx') && !f.includes('(1)') && !f.includes('(4)'));
  
  if (!pnlFile) {
    throw new Error(`No P&L file found in ${dir}`);
  }
  
  const filePath = join(dir, pnlFile);
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);
  
  const ws = workbook.worksheets[0];
  const pnl = {};
  
  // Parse header row to get months (Row 5)
  const headerRow = ws.getRow(5);
  const months = [];
  for (let col = 2; col <= 13; col++) {
    const val = headerRow.getCell(col).value;
    if (val) {
      const dateStr = typeof val === 'object' ? val.toString() : String(val);
      const match = dateStr.match(/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?(\d{4})/i);
      if (match) {
        const monthNames = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'];
        const monthIdx = monthNames.indexOf(match[1].toLowerCase()) + 1;
        months.push({ col, label: `${match[1]} ${match[2]}`, key: `${match[2]}-${String(monthIdx).padStart(2, '0')}` });
      }
    }
  }
  
  const categories = [
    { row: 8, name: 'Sales/Service Revenue', bkName: 'Sales' },
    { row: 12, name: 'Contractors' },
    { row: 13, name: 'Servers & Hosting' },
    { row: 14, name: 'Stripe Fees' },
    { row: 20, name: 'Advertising' },
    { row: 21, name: 'Amortization' },
    { row: 22, name: 'Bank Service Charges' },
    { row: 23, name: 'Business Licensing, Fees & Tax', bkName: 'Business Licensing, Fees, & Tax' },
    { row: 24, name: 'Legal & Professional Fees' },
    { row: 25, name: 'Performance fees (Seller)' },
    { row: 26, name: 'Software expenses' },
    { row: 27, name: 'Wages & Salaries' },
    { row: 33, name: 'Other Income' },
  ];
  
  for (const cat of categories) {
    const row = ws.getRow(cat.row);
    pnl[cat.name] = {};
    
    for (const month of months) {
      let val = row.getCell(month.col).value;
      if (val && typeof val === 'object' && 'result' in val) val = val.result;
      if (val && typeof val === 'object') val = 0;
      pnl[cat.name][month.key] = typeof val === 'number' ? val : parseFloat(val) || 0;
    }
  }
  
  return { months, pnl };
}

function extractPnlData(generatedPnl) {
  const data = {};
  
  for (const section of generatedPnl.sections) {
    for (const cat of section.categories) {
      data[cat.name] = {};
      for (const [month, value] of Object.entries(cat.monthly)) {
        data[cat.name][month] = value;
      }
    }
  }
  
  return data;
}

async function main() {
  const entityId = parseInt(process.argv[2]) || 1;
  const bkDir = process.argv[3] || '/home/andrew/clawd/projects/heath-ledger/bookkeeper-examples';
  
  // Get entity settings for display
  const settings = db.prepare(`
    SELECT * FROM entity_settings WHERE entity_id = ?
  `).get(entityId);
  
  const entity = db.prepare('SELECT name FROM entities WHERE id = ?').get(entityId);
  
  console.log(`\nComparing P&L for: ${entity?.name || entityId}`);
  console.log(`Settings: Month Offset=${settings?.month_offset || 0}, Basis=${settings?.accounting_basis || 'cash'}, Amort=$${settings?.amortization_monthly || 0}/mo`);
  console.log('='.repeat(120));
  
  // Parse bookkeeper data
  console.log('\nParsing bookkeeper data...');
  const bookkeeper = await parseBookkeeperPnL(bkDir);
  
  // Generate P&L for each bookkeeper month (shifted by month_offset)
  // Bookkeeper "Dec 2024" = our PNL for "2025-01" when offset=1
  console.log('Generating P&L with accrual settings...\n');
  
  const results = [];
  
  for (const bkMonth of bookkeeper.months) {
    // The bookkeeper month key represents what THEY call it (e.g., "2024-12" for Dec 2024)
    // With month_offset=1, our Mercury data for "2025-01" should match their "2024-12"
    const offset = settings?.month_offset || 0;
    const [year, month] = bkMonth.key.split('-').map(Number);
    let mercYear = year;
    let mercMonth = month + offset;
    if (mercMonth > 12) { mercMonth -= 12; mercYear++; }
    const mercKey = `${mercYear}-${String(mercMonth).padStart(2, '0')}`;
    
    // Generate P&L for that Mercury month
    const startDate = `${mercKey}-01`;
    const endDate = new Date(mercYear, mercMonth, 0).toISOString().slice(0, 10);
    
    const pnl = buildPnl(db, entityId, startDate, endDate, {
      includeStripeGrossUp: true,
      includeAmortization: true,
      useMonthOffset: false, // We're already handling the offset manually for comparison
    });
    
    if (!pnl) {
      console.log(`--- ${bkMonth.label} → Mercury ${mercKey}: No data ---\n`);
      continue;
    }
    
    const ourData = extractPnlData(pnl);
    
    console.log(`--- ${bkMonth.label} → Mercury ${mercKey} ---`);
    
    // Compare each category
    for (const [category, bkMonthly] of Object.entries(bookkeeper.pnl)) {
      const bkValue = bkMonthly[bkMonth.key] || 0;
      let ourValue = ourData[category]?.[mercKey] || 0;
      
      // Handle sign conventions
      const isRevenue = category === 'Sales/Service Revenue' || category === 'Other Income';
      if (!isRevenue) {
        ourValue = Math.abs(ourValue);
      }
      
      const diff = bkValue - ourValue;
      const match = Math.abs(diff) <= 5;
      
      if (bkValue !== 0 || ourValue !== 0) {
        const status = match ? '✓' : '✗';
        console.log(`  ${status} ${category.padEnd(35)} BK: ${bkValue.toFixed(2).padStart(12)} | Ours: ${ourValue.toFixed(2).padStart(12)} | Diff: ${diff.toFixed(2).padStart(10)}`);
        
        results.push({
          bkMonth: bkMonth.label,
          mercMonth: mercKey,
          category,
          bkValue,
          ourValue,
          diff,
          match
        });
      }
    }
    
    // Show adjustments applied
    if (pnl.adjustments) {
      const adj = pnl.adjustments;
      console.log(`  [Adjustments: Gross-Up=$${adj.stripeGrossUp.toFixed(2)}, Fees=$${adj.stripeFees.toFixed(2)}, Amort=$${adj.amortization.toFixed(2)}]`);
    }
    console.log('');
  }
  
  // Summary
  const total = results.length;
  const matched = results.filter(r => r.match).length;
  console.log('='.repeat(120));
  console.log(`SUMMARY: ${matched}/${total} categories match within $5 (${((matched/total)*100).toFixed(1)}%)`);
  console.log('='.repeat(120));
  
  // Show remaining mismatches
  const mismatches = results.filter(r => !r.match).sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff));
  if (mismatches.length > 0) {
    console.log('\nRemaining mismatches (largest first):');
    for (const m of mismatches.slice(0, 20)) {
      console.log(`  ${m.bkMonth.padEnd(10)} ${m.category.padEnd(35)} BK=${m.bkValue.toFixed(2).padStart(10)}, Ours=${m.ourValue.toFixed(2).padStart(10)}, Diff=${m.diff.toFixed(2).padStart(10)}`);
    }
  }
  
  db.close();
}

main().catch(console.error);
