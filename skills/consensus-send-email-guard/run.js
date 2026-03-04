import fs from 'node:fs';
import path from 'node:path';
import { handler } from './src/index.mjs';

const args = process.argv.slice(2);
const inputIdx = args.indexOf('--input');
if (inputIdx === -1) {
  console.error('Usage: node run.js --input <json-file>');
  process.exit(2);
}

const inputPath = args[inputIdx + 1];
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const out = await handler(input);
const outDir = path.resolve('./out');
fs.mkdirSync(outDir, { recursive: true });
const outFile = path.join(outDir, `send-email-guard-${Date.now()}.json`);
fs.writeFileSync(outFile, JSON.stringify(out, null, 2));
console.log(JSON.stringify({ ok: !out.error, outFile, decision: out.final_decision || null }, null, 2));
