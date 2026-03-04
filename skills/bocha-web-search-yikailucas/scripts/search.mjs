#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const query = process.argv[2] || '';
let count = Number(process.argv[3] || 10);
if (!query.trim()) {
  console.error('用法: node scripts/search.mjs "查询词" [结果条数1-50]');
  process.exit(1);
}
if (!Number.isInteger(count)) {
  console.error('结果条数必须是整数');
  process.exit(1);
}
count = Math.max(1, Math.min(count, 50));

const bochaPath = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'bocha.mjs');
const ret = spawnSync(process.execPath, [bochaPath, 'web', '--query', query, '--count', String(count), '--pretty'], {
  stdio: 'inherit',
  env: process.env,
});
process.exit(ret.status ?? 1);
