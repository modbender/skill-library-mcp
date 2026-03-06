#!/usr/bin/env node
/**
 * Parse bookkeeper Excel files to understand their categorization
 */
import ExcelJS from 'exceljs';
import { readdirSync } from 'fs';
import { join } from 'path';

const BOOKKEEPER_DIR = '/home/andrew/clawd/projects/heath-ledger/bookkeeper-examples';

async function parseAllFiles() {
  const files = readdirSync(BOOKKEEPER_DIR).filter(f => f.endsWith('.xlsx'));
  
  for (const file of files) {
    console.log('\n' + '='.repeat(80));
    console.log('FILE:', file);
    console.log('='.repeat(80));
    
    const wb = new ExcelJS.Workbook();
    await wb.xlsx.readFile(join(BOOKKEEPER_DIR, file));
    
    for (const ws of wb.worksheets) {
      console.log('\n--- Sheet:', ws.name, '---');
      const rows = [];
      ws.eachRow({ includeEmpty: false }, (row, rowNum) => {
        const values = [];
        row.eachCell({ includeEmpty: true }, (cell, colNum) => {
          values.push(cell.value);
        });
        rows.push({ rowNum, values });
      });
      
      // Print first 50 rows to understand structure
      for (const row of rows.slice(0, 50)) {
        console.log(`Row ${row.rowNum}:`, JSON.stringify(row.values));
      }
      if (rows.length > 50) {
        console.log(`... and ${rows.length - 50} more rows`);
      }
    }
  }
}

parseAllFiles().catch(console.error);
