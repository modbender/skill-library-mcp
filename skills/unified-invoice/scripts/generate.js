#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const SKILL_DIR = path.resolve(__dirname, '..');
const DATA_DIR = path.join(SKILL_DIR, 'data');
const TEMPLATE_DIR = path.join(SKILL_DIR, 'templates');
const OUTPUT_DIR = path.join(SKILL_DIR, 'output');

// 데이터 로드 함수
function loadJSON(filename, defaultValue = {}) {
  const filepath = path.join(DATA_DIR, filename);
  if (!fs.existsSync(filepath)) {
    return defaultValue;
  }
  return JSON.parse(fs.readFileSync(filepath, 'utf-8'));
}

function saveJSON(filename, data) {
  const filepath = path.join(DATA_DIR, filename);
  fs.mkdirSync(path.dirname(filepath), { recursive: true });
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf-8');
}

// 금액 포맷 (천 단위 콤마)
function formatCurrency(amount) {
  return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 날짜 포맷 (YYYY-MM-DD)
function formatDate(date) {
  if (typeof date === 'string') return date;
  const d = date || new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 견적서 생성
async function generateQuote(options) {
  const myInfo = loadJSON('my-info.json');
  const clients = loadJSON('clients.json', []);
  const items = loadJSON('items.json', []);

  // 거래처 찾기
  const client = clients.find(c => c.name === options.client);
  if (!client) {
    throw new Error(`거래처를 찾을 수 없습니다: ${options.client}`);
  }

  // 품목 파싱
  let itemList = [];
  if (options.items) {
    // "품목명,수량,단가" 형식
    const itemStrings = options.items.split(';');
    itemList = itemStrings.map(str => {
      const [name, quantity, price] = str.split(',').map(s => s.trim());
      return {
        name,
        quantity: parseInt(quantity) || 1,
        price: parseInt(price) || 0,
        unit: '개'
      };
    });
  } else if (options.itemIds) {
    // 저장된 품목 ID 사용
    const ids = options.itemIds.split(',');
    itemList = ids.map(id => {
      const item = items.find(i => i.name === id.trim());
      if (!item) throw new Error(`품목을 찾을 수 없습니다: ${id}`);
      return {
        name: item.name,
        quantity: 1,
        price: item.price,
        unit: item.unit || '개'
      };
    });
  }

  // 금액 계산
  const subtotal = itemList.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  const vat = options.includeVAT !== false ? Math.round(subtotal * 0.1) : 0;
  const total = subtotal + vat;

  // 템플릿 로드
  const template = fs.readFileSync(path.join(TEMPLATE_DIR, 'quote.html'), 'utf-8');

  // 템플릿 변수 치환
  const issueDate = formatDate(options.issueDate);
  const validUntil = formatDate(options.validUntil || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000));

  let itemRows = '';
  itemList.forEach((item, idx) => {
    const amount = item.quantity * item.price;
    itemRows += `
      <tr>
        <td>${idx + 1}</td>
        <td>${item.name}</td>
        <td>${item.unit}</td>
        <td>${formatCurrency(item.quantity)}</td>
        <td>${formatCurrency(item.price)}</td>
        <td>${formatCurrency(amount)}</td>
      </tr>
    `;
  });

  const html = template
    .replace(/{{myCompanyName}}/g, myInfo.companyName || '')
    .replace(/{{myBusinessNumber}}/g, myInfo.businessNumber || '')
    .replace(/{{myCEO}}/g, myInfo.ceo || '')
    .replace(/{{myAddress}}/g, myInfo.address || '')
    .replace(/{{myPhone}}/g, myInfo.phone || '')
    .replace(/{{myEmail}}/g, myInfo.email || '')
    .replace(/{{clientName}}/g, client.name || '')
    .replace(/{{clientBusinessNumber}}/g, client.businessNumber || '')
    .replace(/{{clientCEO}}/g, client.ceo || '')
    .replace(/{{clientAddress}}/g, client.address || '')
    .replace(/{{clientPhone}}/g, client.phone || '')
    .replace(/{{issueDate}}/g, issueDate)
    .replace(/{{validUntil}}/g, validUntil)
    .replace(/{{itemRows}}/g, itemRows)
    .replace(/{{subtotal}}/g, formatCurrency(subtotal))
    .replace(/{{vat}}/g, formatCurrency(vat))
    .replace(/{{total}}/g, formatCurrency(total))
    .replace(/{{notes}}/g, options.notes || '');

  // HTML 저장
  const filename = `${issueDate}-견적서-${client.name}`;
  const htmlPath = path.join(OUTPUT_DIR, `${filename}.html`);
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(htmlPath, html, 'utf-8');

  console.log(`✅ 견적서 HTML 생성: ${htmlPath}`);

  // PDF 변환
  if (options.pdf !== false) {
    const pdfPath = path.join(OUTPUT_DIR, `${filename}.pdf`);
    await convertToPDF(htmlPath, pdfPath);
    console.log(`✅ PDF 생성: ${pdfPath}`);
    return pdfPath;
  }

  return htmlPath;
}

// 세금계산서 생성
async function generateTaxInvoice(options) {
  const myInfo = loadJSON('my-info.json');
  const clients = loadJSON('clients.json', []);
  const items = loadJSON('items.json', []);

  const client = clients.find(c => c.name === options.client);
  if (!client) {
    throw new Error(`거래처를 찾을 수 없습니다: ${options.client}`);
  }

  // 품목 파싱 (견적서와 동일)
  let itemList = [];
  if (options.items) {
    const itemStrings = options.items.split(';');
    itemList = itemStrings.map(str => {
      const [name, quantity, price] = str.split(',').map(s => s.trim());
      return {
        name,
        quantity: parseInt(quantity) || 1,
        price: parseInt(price) || 0
      };
    });
  } else if (options.itemIds) {
    const ids = options.itemIds.split(',');
    itemList = ids.map(id => {
      const item = items.find(i => i.name === id.trim());
      if (!item) throw new Error(`품목을 찾을 수 없습니다: ${id}`);
      return {
        name: item.name,
        quantity: 1,
        price: item.price
      };
    });
  }

  const subtotal = itemList.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  const vat = Math.round(subtotal * 0.1);
  const total = subtotal + vat;

  const template = fs.readFileSync(path.join(TEMPLATE_DIR, 'tax-invoice.html'), 'utf-8');

  const issueDate = formatDate(options.issueDate);
  const approvalNumber = `T${Date.now().toString().slice(-10)}`; // 임의 승인번호

  let itemRows = '';
  itemList.forEach((item, idx) => {
    const amount = item.quantity * item.price;
    itemRows += `
      <tr>
        <td>${issueDate}</td>
        <td>${item.name}</td>
        <td>${formatCurrency(item.quantity)}</td>
        <td>${formatCurrency(item.price)}</td>
        <td>${formatCurrency(amount)}</td>
        <td>${options.notes || ''}</td>
      </tr>
    `;
  });

  const html = template
    .replace(/{{approvalNumber}}/g, approvalNumber)
    .replace(/{{type}}/g, options.type || '영수')
    .replace(/{{issueDate}}/g, issueDate)
    .replace(/{{myCompanyName}}/g, myInfo.companyName || '')
    .replace(/{{myBusinessNumber}}/g, myInfo.businessNumber || '')
    .replace(/{{myCEO}}/g, myInfo.ceo || '')
    .replace(/{{myAddress}}/g, myInfo.address || '')
    .replace(/{{clientName}}/g, client.name || '')
    .replace(/{{clientBusinessNumber}}/g, client.businessNumber || '')
    .replace(/{{clientCEO}}/g, client.ceo || '')
    .replace(/{{clientAddress}}/g, client.address || '')
    .replace(/{{itemRows}}/g, itemRows)
    .replace(/{{subtotal}}/g, formatCurrency(subtotal))
    .replace(/{{vat}}/g, formatCurrency(vat))
    .replace(/{{total}}/g, formatCurrency(total));

  const filename = `${issueDate}-세금계산서-${client.name}`;
  const htmlPath = path.join(OUTPUT_DIR, `${filename}.html`);
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(htmlPath, html, 'utf-8');

  console.log(`✅ 세금계산서 HTML 생성: ${htmlPath}`);

  if (options.pdf !== false) {
    const pdfPath = path.join(OUTPUT_DIR, `${filename}.pdf`);
    await convertToPDF(htmlPath, pdfPath);
    console.log(`✅ PDF 생성: ${pdfPath}`);
    return pdfPath;
  }

  return htmlPath;
}

// HTML → PDF 변환 (puppeteer)
async function convertToPDF(htmlPath, pdfPath) {
  const browser = await puppeteer.connect({
    browserURL: 'http://localhost:18800'
  });

  const page = await browser.newPage();
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    printBackground: true,
    margin: { top: '20mm', right: '15mm', bottom: '20mm', left: '15mm' }
  });

  await page.close();
  // browser.disconnect() - 세션 유지
}

// CLI 인터페이스
const args = process.argv.slice(2);
const command = args[0];

async function main() {
  if (command === 'quote') {
    const options = {};
    for (let i = 1; i < args.length; i++) {
      if (args[i] === '--client') options.client = args[++i];
      else if (args[i] === '--items') options.items = args[++i];
      else if (args[i] === '--item-ids') options.itemIds = args[++i];
      else if (args[i] === '--notes') options.notes = args[++i];
      else if (args[i] === '--issue-date') options.issueDate = args[++i];
      else if (args[i] === '--valid-until') options.validUntil = args[++i];
      else if (args[i] === '--no-pdf') options.pdf = false;
    }

    if (!options.client || (!options.items && !options.itemIds)) {
      console.error('사용법: node generate.js quote --client "거래처명" --items "품목,수량,단가;..."');
      process.exit(1);
    }

    await generateQuote(options);
  } else if (command === 'tax') {
    const options = {};
    for (let i = 1; i < args.length; i++) {
      if (args[i] === '--client') options.client = args[++i];
      else if (args[i] === '--items') options.items = args[++i];
      else if (args[i] === '--item-ids') options.itemIds = args[++i];
      else if (args[i] === '--notes') options.notes = args[++i];
      else if (args[i] === '--issue-date') options.issueDate = args[++i];
      else if (args[i] === '--type') options.type = args[++i];
      else if (args[i] === '--no-pdf') options.pdf = false;
    }

    if (!options.client || (!options.items && !options.itemIds)) {
      console.error('사용법: node generate.js tax --client "거래처명" --items "품목,수량,단가;..."');
      process.exit(1);
    }

    await generateTaxInvoice(options);
  } else {
    console.log(`사용법:
  node generate.js quote --client "거래처명" --items "품목,수량,단가;..."
  node generate.js tax --client "거래처명" --items "품목,수량,단가;..."
    `);
  }
}

main().catch(err => {
  console.error('❌ 오류:', err.message);
  process.exit(1);
});
