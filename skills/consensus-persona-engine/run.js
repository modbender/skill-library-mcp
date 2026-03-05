import fs from 'node:fs';
import { handler } from './src/index.mjs';

const args = process.argv.slice(2);
const i = args.indexOf('--input');
if (i < 0 || !args[i + 1]) {
  console.error('Usage: node run.js --input <json-file>');
  process.exit(1);
}
const input = JSON.parse(fs.readFileSync(args[i + 1], 'utf8'));
const out = await handler(input);
console.log(JSON.stringify(out, null, 2));
