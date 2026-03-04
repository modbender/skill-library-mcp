#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.resolve(__dirname, '..', 'data');
const CLIENTS_FILE = path.join(DATA_DIR, 'clients.json');

function loadClients() {
  if (!fs.existsSync(CLIENTS_FILE)) {
    return [];
  }
  return JSON.parse(fs.readFileSync(CLIENTS_FILE, 'utf-8'));
}

function saveClients(clients) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(CLIENTS_FILE, JSON.stringify(clients, null, 2), 'utf-8');
}

function addClient(name, options) {
  const clients = loadClients();
  
  // 중복 체크
  if (clients.some(c => c.name === name)) {
    console.error(`❌ 이미 존재하는 거래처입니다: ${name}`);
    process.exit(1);
  }

  const client = {
    name,
    businessNumber: options.businessNumber || '',
    ceo: options.ceo || '',
    address: options.address || '',
    phone: options.phone || '',
    email: options.email || '',
    createdAt: new Date().toISOString()
  };

  clients.push(client);
  saveClients(clients);
  console.log(`✅ 거래처 추가: ${name}`);
}

function editClient(name, options) {
  const clients = loadClients();
  const client = clients.find(c => c.name === name);

  if (!client) {
    console.error(`❌ 거래처를 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  if (options.businessNumber) client.businessNumber = options.businessNumber;
  if (options.ceo) client.ceo = options.ceo;
  if (options.address) client.address = options.address;
  if (options.phone) client.phone = options.phone;
  if (options.email) client.email = options.email;

  saveClients(clients);
  console.log(`✅ 거래처 수정: ${name}`);
}

function removeClient(name) {
  const clients = loadClients();
  const filtered = clients.filter(c => c.name !== name);

  if (filtered.length === clients.length) {
    console.error(`❌ 거래처를 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  saveClients(filtered);
  console.log(`✅ 거래처 삭제: ${name}`);
}

function listClients() {
  const clients = loadClients();

  if (clients.length === 0) {
    console.log('등록된 거래처가 없습니다.');
    return;
  }

  console.log(`총 ${clients.length}개 거래처:\n`);
  clients.forEach((client, idx) => {
    console.log(`${idx + 1}. ${client.name}`);
    console.log(`   사업자번호: ${client.businessNumber || '(없음)'}`);
    console.log(`   대표자: ${client.ceo || '(없음)'}`);
    console.log(`   연락처: ${client.phone || '(없음)'}`);
    console.log('');
  });
}

function viewClient(name) {
  const clients = loadClients();
  const client = clients.find(c => c.name === name);

  if (!client) {
    console.error(`❌ 거래처를 찾을 수 없습니다: ${name}`);
    process.exit(1);
  }

  console.log(`거래처 정보: ${client.name}\n`);
  console.log(`사업자등록번호: ${client.businessNumber || '(없음)'}`);
  console.log(`대표자: ${client.ceo || '(없음)'}`);
  console.log(`주소: ${client.address || '(없음)'}`);
  console.log(`전화: ${client.phone || '(없음)'}`);
  console.log(`이메일: ${client.email || '(없음)'}`);
  console.log(`등록일: ${client.createdAt}`);
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'add') {
  const name = args[1];
  const options = {};
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--business-number') options.businessNumber = args[++i];
    else if (args[i] === '--ceo') options.ceo = args[++i];
    else if (args[i] === '--address') options.address = args[++i];
    else if (args[i] === '--phone') options.phone = args[++i];
    else if (args[i] === '--email') options.email = args[++i];
  }
  addClient(name, options);
} else if (command === 'edit') {
  const name = args[1];
  const options = {};
  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--business-number') options.businessNumber = args[++i];
    else if (args[i] === '--ceo') options.ceo = args[++i];
    else if (args[i] === '--address') options.address = args[++i];
    else if (args[i] === '--phone') options.phone = args[++i];
    else if (args[i] === '--email') options.email = args[++i];
  }
  editClient(name, options);
} else if (command === 'remove') {
  removeClient(args[1]);
} else if (command === 'list') {
  listClients();
} else if (command === 'view') {
  viewClient(args[1]);
} else {
  console.log(`사용법:
  node manage-clients.js add "거래처명" --business-number "123-45-67890" --ceo "홍길동" --address "..." --phone "..." --email "..."
  node manage-clients.js edit "거래처명" --phone "..."
  node manage-clients.js remove "거래처명"
  node manage-clients.js list
  node manage-clients.js view "거래처명"
  `);
}
