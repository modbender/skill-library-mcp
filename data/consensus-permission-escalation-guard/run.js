import fs from 'node:fs';
import path from 'node:path';
import { handler } from './src/index.mjs';

const i = process.argv.indexOf('--input');
if (i < 0 || !process.argv[i + 1]) {
  console.error('Usage: run.js --input <file>');
  process.exit(2);
}

const cwd = process.cwd();
const inputPath = path.resolve(cwd, process.argv[i + 1]);
if (!inputPath.startsWith(cwd + path.sep) && inputPath !== cwd) {
  console.error('Refusing to read input outside current working directory');
  process.exit(2);
}
if (path.extname(inputPath).toLowerCase() !== '.json') {
  console.error('Input must be a .json file');
  process.exit(2);
}

const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
const out = await handler(input);
const outDir = path.resolve(cwd, 'out');
fs.mkdirSync(outDir, { recursive: true });
const f = path.join(outDir, `permission-escalation-${Date.now()}.json`);
fs.writeFileSync(f, JSON.stringify(out, null, 2));
console.log(JSON.stringify({ ok: !out.error, outFile: f, decision: out.final_decision || null }, null, 2));
