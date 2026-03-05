#!/usr/bin/env node
'use strict';

/**
 * skill-select.js — 从 search-results.json 写入 selection.json
 * 用法: node skill-select.js --hotel 2
 */

const minimist = require('minimist');
const fs = require('fs');
const path = require('path');

const args = minimist(process.argv.slice(2));
const n = parseInt(args.hotel);
if (isNaN(n) || n < 1 || n > 4) {
  process.stderr.write('用法: node skill-select.js --hotel <1-4>\n');
  process.exit(1);
}

const resultsFile = path.join(__dirname, 'search-results.json');
if (!fs.existsSync(resultsFile)) {
  process.stderr.write('❌ 未找到 search-results.json，请先运行 skill-search.js\n');
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(resultsFile));
const h = data.hotels[n - 1];
if (!h) {
  process.stderr.write(`❌ 序号 ${n} 不存在（共 ${data.hotels.length} 家）\n`);
  process.exit(1);
}

const selection = {
  ...h,
  checkIn:  data.checkIn,
  checkOut: data.checkOut,
  adults:   data.adults,
  rooms:    data.rooms,
  nights:   data.nights,
};
fs.writeFileSync(path.join(__dirname, 'selection.json'), JSON.stringify(selection, null, 2));
console.log(JSON.stringify({ selected: h.name, propertyCode: h.propertyCode }));
