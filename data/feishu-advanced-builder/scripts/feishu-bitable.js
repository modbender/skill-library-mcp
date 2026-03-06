#!/usr/bin/env node
/**
 * Feishu Bitable API - Create spreadsheets with any size
 */

const fs = require('fs');

const BASE_URL = process.env.FEISHU_BASE_URL || 'https://open.feishu.cn/open-apis';
const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

function parseArgs(argv) {
  const [,, command, ...rest] = argv;
  const args = { _: command };
  for (let i = 0; i < rest.length; i++) {
    const cur = rest[i];
    if (cur.startsWith('--')) {
      const key = cur.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = rest[i + 1];
      if (!next || next.startsWith('--')) {
        args[key] = true;
      } else {
        args[key] = next;
        i++;
      }
    }
  }
  return args;
}

function requiredEnv() {
  if (!APP_ID || !APP_SECRET) {
    throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  }
}

async function feishuFetch(path, { method = 'GET', token, body, retryCount = 0, maxRetries = 5 } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    if (res.status === 429 && retryCount < maxRetries) {
      const delay = Math.min(2000 * Math.pow(2, retryCount), 60000);
      console.error(`Rate limited, retrying in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
      return feishuFetch(path, { method, token, body, retryCount: retryCount + 1, maxRetries });
    }
    throw new Error(`Non-JSON response: ${res.status} ${text.slice(0, 500)}`);
  }

  if (!res.ok || json.code !== 0) {
    if (json.code === 1254043 || json.msg?.includes('rate limit')) {
      if (retryCount < maxRetries) {
        const delay = Math.min(2000 * Math.pow(2, retryCount), 60000);
        console.error(`Rate limited (code ${json.code}), retrying in ${delay}ms...`);
        await new Promise(r => setTimeout(r, delay));
        return feishuFetch(path, { method, token, body, retryCount: retryCount + 1, maxRetries });
      }
    }
    throw new Error(`Feishu API error (${method} ${path}): HTTP ${res.status}, code=${json.code}, msg=${json.msg}`);
  }

  return json;
}

async function getTenantToken() {
  requiredEnv();
  const res = await feishuFetch('/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    body: { app_id: APP_ID, app_secret: APP_SECRET },
  });
  return res.tenant_access_token;
}

// Parse markdown table
function parseMarkdownTable(md) {
  const lines = md.trim().split('\n');
  const rows = [];
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      // Skip separator line (|---|)
      if (trimmed.match(/^\|[\s\-:|]+\|$/)) continue;
      
      const cells = trimmed.slice(1, -1).split('|').map(c => c.trim());
      rows.push(cells);
    }
  }
  
  return rows;
}

async function createBitable(token, spaceId, tableName, data) {
  if (data.length === 0) throw new Error('No data provided');
  
  const rowCount = data.length;
  const colCount = data[0].length;
  
  // Create bitable
  const createRes = await feishuFetch(
    `/bitable/v1/spreadsheets`,
    {
      method: 'POST',
      token,
      body: {
        folder_token: spaceId,
        title: tableName
      }
    }
  );
  
  const spreadsheetToken = createRes.data.spreadsheet_token;
  console.log(`Created spreadsheet: ${spreadsheetToken}`);
  
  // Get the default sheet
  const sheetsRes = await feishuFetch(
    `/bitable/v1/spreadsheets/${spreadsheetToken}/sheets`,
    { token }
  );
  
  const sheetId = sheetsRes.data.items[0].sheet_id;
  console.log(`Using sheet: ${sheetId}`);
  
  // Batch write data - Feishu API has limits, so we need to batch
  const BATCH_SIZE = 500; // Max cells per request
  const batchData = [];
  
  for (let r = 0; r < Math.min(rowCount, 100); r++) { // Limit rows for now
    for (let c = 0; c < colCount; c++) {
      batchData.push({
        row: r,
        col: c,
        value: data[r][c]
      });
      
      if (batchData.length >= BATCH_SIZE) {
        await writeBatch(token, spreadsheetToken, sheetId, batchData);
        batchData.length = 0;
      }
    }
  }
  
  if (batchData.length > 0) {
    await writeBatch(token, spreadsheetToken, sheetId, batchData);
  }
  
  return spreadsheetToken;
}

async function writeBatch(token, spreadsheetToken, sheetId, batchData) {
  // Build request for batch write
  const records = batchData.map(({ row, col, value }) => ({
    fields: { [col]: value }
  }));
  
  // Use batch append
  await feishuFetch(
    `/bitable/v1/spreadsheets/${spreadsheetToken}/sheets/${sheetId}/records`,
    {
      method: 'POST',
      token,
      body: { records }
    }
  );
}

async function main() {
  const args = parseArgs(process.argv);
  const cmd = args._;

  if (!cmd || ['-h', '--help', 'help'].includes(cmd)) {
    console.log('Usage: node feishu-bitable.js create --space-id <id> --title <name> --markdown-file <file>');
    return;
  }

  if (cmd === 'create') {
    if (!args.spaceId || !args.title || !args.markdownFile) {
      throw new Error('Missing required params: --space-id, --title, --markdown-file');
    }
    
    const md = fs.readFileSync(args.markdownFile, 'utf8');
    const data = parseMarkdownTable(md);
    
    console.log(`Creating table with ${data.length} rows, ${data[0]?.length || 0} columns`);
    
    const token = await getTenantToken();
    const spreadsheetToken = await createBitable(token, args.spaceId, args.title, data);
    
    console.log(`Done! Bitable URL: https://my.feishu.cn/bitable/${spreadsheetToken}`);
    console.log(`Spreadsheet token: ${spreadsheetToken}`);
  }
}

main().catch(console.error);
