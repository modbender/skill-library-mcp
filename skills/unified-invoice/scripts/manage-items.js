#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.resolve(__dirname, '..', 'data');
const ITEMS_FILE = path.join(DATA_DIR, 'items.json');

function loadItems() {
  if (!fs.existsSync(ITEMS_FILE)) {
    return [];
  }
  return JSON.parse(fs.readFileSync(ITEMS_FILE, 'utf-8'));
}

function saveItems(items) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(ITEMS_FILE, JSON.stringify(items, null, 2), 'utf-8');
}

function addItem(name, options) {
  const items = loadItems();
  
  // 중복 체크
  if (items.some(i => i.name === name)) {
    console.error(`❌ 이미 존재하는 품목입니다: ${name}`);
    process.exit(1);
  }

  const item = {
    name,
    price: parseInt(options.price) || 0,
    unit: options.unit || '개',
    description: options.description || '',
    createdAt: new Date().toISOString()
  };

  items.push(item);
  saveItems(items);
  console.log(`✅ 품목 추가: ${name} (${item.price.toLocaleString()}원/${item.unit})`);
}

function editItem(name, options) {
  const items = loadItems();
  const item = items.find(i => i.name === name);

  if (!item) {
    console.error(`❌ 품목을 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  if (options.price) item.price = parseInt(options.price);
  if (options.unit) item.unit = options.unit;
  if (options.description) item.description = options.description;

  saveItems(items);
  console.log(`✅ 품목 수정: ${name}`);
}

function removeItem(name) {
  const items = loadItems();
  const filtered = items.filter(i => i.name !== name);

  if (filtered.length === items.length) {
    console.error(`❌ 품목을 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  saveItems(filtered);
  console.log(`✅ 품목 삭제: ${name}`);
}

function listItems() {
  const items = loadItems();

  if (items.length === 0) {
    console.log('등록된 품목이 없습니다.');
    return;
  }

  console.log(`총 ${items.length}개 품목:\n`);
  items.forEach((item, idx) => {
    console.log(`${idx + 1}. ${item.name}`);
    console.log(`   단가: ${item.price.toLocaleString()}원 / ${item.unit}`);
    if (item.description) {
      console.log(`   설명: ${item.description}`);
    }
    console.log('');
  });
}

function viewItem(name) {
  const items = loadItems();
  const item = items.find(i => i.name === name);

  if (!item) {
    console.error(`❌ 품목을 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  console.log(`품목 정보: ${item.name}\n`);
  console.log(`단가: ${item.price.toLocaleString()}원`);
  console.log(`단위: ${item.unit}`);
  console.log(`설명: ${item.description || '(없음)'}`);
  console.log(`등록일: ${item.createdAt}`);
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'add') {
  const name = args[1];
  const options = {};
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--price') options.price = args[++i];
    else if (args[i] === '--unit') options.unit = args[++i];
    else if (args[i] === '--description') options.description = args[++i];
  }
  addItem(name, options);
} else if (command === 'edit') {
  const name = args[1];
  const options = {};
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--price') options.price = args[++i];
    else if (args[i] === '--unit') options.unit = args[++i];
    else if (args[i] === '--description') options.description = args[++i];
  }
  editItem(name, options);
} else if (command === 'remove') {
  removeItem(args[1]);
} else if (command === 'list') {
  listItems();
} else if (command === 'view') {
  viewItem(args[1]);
} else {
  console.log(`사용법:
  node manage-items.js add "품목명" --price 500000 --unit "일" --description "..."
  node manage-items.js edit "품목명" --price 600000
  node manage-items.js remove "품목명"
  node manage-items.js list
  node manage-items.js view "품목명"
  `);
}
