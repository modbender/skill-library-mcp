import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { getDb } from './lib/db.js';
import { buildPnl } from './lib/pnl.js';
import { aggregateBalanceSheet } from './lib/balance-sheet.js';
import { aggregateCashFlow } from './lib/cash-flow.js';
import { generateBooksExcel } from './lib/excel-books.js';

const [,, entityId, startDate, endDate, outputPath] = process.argv;
if (!entityId || !startDate || !endDate) {
  console.error('Usage: generate_books.mjs <entity_id> <start_date> <end_date> [output_path]');
  process.exit(1);
}

const db = getDb();
const entity = db.prepare('SELECT name FROM entities WHERE id = ?').get(Number(entityId));
if (!entity) { console.error(`Entity ${entityId} not found`); process.exit(1); }

console.log(`Generating books for ${entity.name} (${startDate} to ${endDate})...`);

const pnl = buildPnl(db, Number(entityId), startDate, endDate);
if (!pnl) { console.error('No transaction data found for this period'); process.exit(1); }

const netIncome = pnl.summary.netIncome;
const bs = aggregateBalanceSheet(db, Number(entityId), startDate, endDate, netIncome);
const cf = aggregateCashFlow(db, Number(entityId), startDate, endDate);

const buffer = await generateBooksExcel(pnl, bs, cf, pnl.transactions);

const skillDir = join(dirname(new URL(import.meta.url).pathname), '..');
const dataDir = join(skillDir, 'data');
mkdirSync(dataDir, { recursive: true });
const outFile = outputPath || join(dataDir, `books-${entityId}-${startDate}-${endDate}.xlsx`);

writeFileSync(outFile, Buffer.from(buffer));
console.log(`Books written to ${outFile}`);
console.log(`  Revenue: $${pnl.summary.revenue.toFixed(2)}`);
console.log(`  Net Income: $${netIncome.toFixed(2)}`);
console.log(`  Uncategorized: ${pnl.uncategorizedCount} transactions`);
