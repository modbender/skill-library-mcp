#!/usr/bin/env node
/**
 * Extract bookkeeper categorization mapping from Excel files
 */
import ExcelJS from 'exceljs';
import { readdirSync } from 'fs';
import { join } from 'path';

const BOOKKEEPER_DIR = '/home/andrew/clawd/projects/heath-ledger/bookkeeper-examples';

async function extractCategories() {
  const categoryMap = {};
  const files = readdirSync(BOOKKEEPER_DIR).filter(f => f.endsWith('.xlsx') && f.includes('Income_Statement'));
  
  for (const file of files) {
    console.log('\n=== FILE:', file, '===');
    const wb = new ExcelJS.Workbook();
    await wb.xlsx.readFile(join(BOOKKEEPER_DIR, file));
    
    for (const ws of wb.worksheets) {
      const sheetName = ws.name;
      console.log('Sheet:', JSON.stringify(sheetName));
      
      // Skip summary sheet
      if (sheetName.startsWith('Income Statement')) continue;
      
      const transactions = [];
      ws.eachRow({ includeEmpty: false }, (row, rowNum) => {
        if (rowNum < 8) return; // Skip headers
        const values = [];
        row.eachCell({ includeEmpty: true }, (cell, colNum) => {
          values.push(cell.value);
        });
        
        // Column format: Date, Contact, Description, Reference, Gross, Debit, Credit, Running Balance, Related account
        if (values.length >= 5 && values[0] && values[1]) {
          let date = values[0];
          const contact = values[1];
          const description = values[2];
          const gross = values[4];
          
          // Handle Date objects
          if (date instanceof Date) {
            date = date.toISOString().substring(0, 10);
          } else if (typeof date === 'string' && date.match(/^\d{4}-\d{2}/)) {
            date = date.substring(0, 10);
          } else {
            return; // Skip if not a valid date
          }
          
          if (contact && contact !== ' ') {
            transactions.push({
              date,
              contact: String(contact).trim(),
              description: String(description || '').trim(),
              amount: typeof gross === 'number' ? gross : parseFloat(gross) || 0
            });
          }
        }
      });
      
      console.log(`  Found ${transactions.length} transactions`);
      
      if (transactions.length > 0) {
        if (!categoryMap[sheetName]) categoryMap[sheetName] = [];
        categoryMap[sheetName].push(...transactions);
      }
    }
  }
  
  // Build counterparty → category mapping
  const counterpartyToCategory = {};
  for (const [category, txs] of Object.entries(categoryMap)) {
    for (const tx of txs) {
      const contact = tx.contact.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (!counterpartyToCategory[contact]) {
        counterpartyToCategory[contact] = { category, originalName: tx.contact, examples: [] };
      }
      if (counterpartyToCategory[contact].examples.length < 3) {
        counterpartyToCategory[contact].examples.push(tx);
      }
    }
  }
  
  console.log('\n\n=== BOOKKEEPER CATEGORY MAPPING ===\n');
  for (const [contact, info] of Object.entries(counterpartyToCategory).sort((a, b) => a[1].category.localeCompare(b[1].category))) {
    console.log(`${info.originalName.padEnd(35)} → ${info.category}`);
  }
  
  // Print specific sheets in detail
  for (const [sheetName, txs] of Object.entries(categoryMap)) {
    if (sheetName.toLowerCase().includes('server') || sheetName.toLowerCase().includes('hosting')) {
      console.log(`\n\n=== ${sheetName.toUpperCase()} TRANSACTIONS ===`);
      for (const tx of txs.slice(0, 60)) {
        console.log(`${tx.date} | ${tx.contact.padEnd(25)} | $${tx.amount.toFixed(2)}`);
      }
    }
    if (sheetName.toLowerCase().includes('contractor')) {
      console.log(`\n\n=== ${sheetName.toUpperCase()} TRANSACTIONS ===`);
      for (const tx of txs) {
        console.log(`${tx.date} | ${tx.contact.padEnd(35)} | $${tx.amount.toFixed(2)}`);
      }
    }
    if (sheetName.toLowerCase().includes('stripe')) {
      console.log(`\n\n=== ${sheetName.toUpperCase()} TRANSACTIONS (first 30) ===`);
      for (const tx of txs.slice(0, 30)) {
        console.log(`${tx.date} | ${tx.contact.padEnd(25)} | $${tx.amount.toFixed(2)}`);
      }
    }
    if (sheetName.toLowerCase() === 'sales') {
      console.log(`\n\n=== ${sheetName.toUpperCase()} TRANSACTIONS (first 30) ===`);
      for (const tx of txs.slice(0, 30)) {
        console.log(`${tx.date} | ${tx.contact.padEnd(25)} | $${tx.amount.toFixed(2)}`);
      }
    }
  }
}

extractCategories().catch(console.error);
