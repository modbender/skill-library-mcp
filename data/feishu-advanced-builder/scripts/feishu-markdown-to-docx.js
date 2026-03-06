#!/usr/bin/env node
/**
 * feishu-markdown-to-docx - 将 Markdown 转换为飞书文档，支持表格
 */

const fs = require('fs');
const { 
  parseMarkdown, 
  generateBlockId,
  BlockType 
} = require('feishu-markdown');

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
    // Handle rate limiting with retry
    if (res.status === 429 && retryCount < maxRetries) {
      const delay = Math.min(2000 * Math.pow(2, retryCount), 60000); // Exponential backoff
      console.error(`Rate limited, retrying in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
      return feishuFetch(path, { method, token, body, retryCount: retryCount + 1, maxRetries });
    }
    throw new Error(`Non-JSON response: ${res.status} ${text.slice(0, 500)}`);
  }

  if (!res.ok || json.code !== 0) {
    // Handle specific rate limit error code
    if (json.code === 1254043 || json.msg?.includes('rate limit') || json.msg?.includes('Rate limit')) {
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

function mapLanguage(lang) {
  const map = {
    javascript: 30, js: 30,
    python: 49, py: 49,
    java: 29,
    go: 22,
    rust: 53,
    typescript: 63, ts: 63,
    sql: 56,
    bash: 7, shell: 60,
    json: 28,
    html: 24,
    css: 12,
    yaml: 67, yml: 67,
    xml: 66,
    markdown: 39, md: 39,
    plaintext: 1
  };
  return map[lang.toLowerCase()] || 1;
}

/**
 * 将 Markdown AST 转换为飞书 blocks
 */
function transformMarkdownToBlocks(ast) {
  const blocks = [];
  
  function processNode(node, parentList = null) {
    if (!node) return;
    
    if (node.type === 'root' || node.type === 'document') {
      for (const child of node.children || []) {
        processNode(child, blocks);
      }
    } else if (node.type === 'heading') {
      const level = Math.min(node.depth, 9);
      const content = (node.children || []).map(c => c.value || '').join('');
      const headingKey = 'heading' + level;
      blocks.push({
        block_type: level + 2,
        [headingKey]: {
          elements: [{ text_run: { content } }]
        }
      });
    } else if (node.type === 'paragraph') {
      const content = (node.children || []).map(c => c.value || '').join('');
      if (content.trim()) {
        blocks.push({
          block_type: 2,
          text: { elements: [{ text_run: { content } }] }
        });
      }
    } else if (node.type === 'list') {
      const isOrdered = node.ordered || false;
      for (const item of node.children || []) {
        const textContent = (item.children || []).map(c => {
          if (c.children) return c.children.map(cc => cc.value || '').join('');
          return c.value || '';
        }).join('');
        
        blocks.push({
          block_type: isOrdered ? 13 : 12,
          [isOrdered ? 'ordered' : 'bullet']: {
            elements: [{ text_run: { content: textContent } }]
          }
        });
      }
    } else if (node.type === 'code') {
      const content = node.value || '';
      const lang = node.lang || '';
      blocks.push({
        block_type: 14,
        code: {
          elements: [{ text_run: { content } }],
          style: { language: mapLanguage(lang), wrap: false }
        }
      });
    } else if (node.type === 'table') {
      const rows = node.children || [];
      const rowCount = rows.length;
      const colCount = rows[0] && rows[0].children ? rows[0].children.length : 0;
      
      if (rowCount > 0 && colCount > 0) {
        const MAX_CELLS = 28; // Feishu API limit per table
        
        // Collect all cell contents
        const allCellContents = [];
        for (let r = 0; r < rowCount; r++) {
          const row = rows[r];
          const cells = row.children || [];
          const rowContents = [];
          for (let c = 0; c < colCount; c++) {
            const content = (cells[c]?.children || []).map(cc => cc.value || '').join('');
            rowContents.push(content);
          }
          allCellContents.push(rowContents);
        }
        
        // If small enough, create as single table
        if (rowCount * colCount <= MAX_CELLS) {
          const tableId = generateBlockId();
          const cellIds = allCellContents.flatMap(() => 
            Array(colCount).fill(null).map(() => generateBlockId())
          );
          
          blocks.push({
            _isTable: true,
            tableId,
            cellIds,
            cellContents: allCellContents,
            rowCount,
            colCount
          });
        } else {
          // Split into multiple tables with header repeat
          const maxRowsPerTable = Math.floor(MAX_CELLS / colCount);
          
          for (let startRow = 0; startRow < rowCount; startRow += maxRowsPerTable) {
            const endRow = Math.min(startRow + maxRowsPerTable, rowCount);
            const subRowCount = endRow - startRow;
            const tableId = generateBlockId();
            
            const subCellContents = allCellContents.slice(startRow, endRow);
            const cellIds = subCellContents.flatMap(() => 
              Array(colCount).fill(null).map(() => generateBlockId())
            );
            
            blocks.push({
              _isTable: true,
              tableId,
              cellIds,
              cellContents: subCellContents,
              rowCount: subRowCount,
              colCount,
              _isPartial: true,
              _isLast: endRow >= rowCount
            });
            
            // No divider - tables will be adjacent
          }
        }
      }
    } else if (node.type === 'thematicBreak') {
      blocks.push({ block_type: 22, divider: {} });
    }
  }
  
  processNode(ast);
  return blocks;
}

// Helper: add cells to existing table in batches
async function addTableCells(token, docId, tableBlockId, newCellIds) {
  const BATCH_SIZE = 10; // Smaller batch size to avoid API limit
  const createdCellIds = [];
  
  for (let i = 0; i < newCellIds.length; i += BATCH_SIZE) {
    const batch = newCellIds.slice(i, i + BATCH_SIZE);
    const res = await feishuFetch(
      `/docx/v1/documents/${docId}/blocks/${tableBlockId}/children?document_revision_id=-1`,
      {
        method: 'POST',
        token,
        body: { children: batch.map(id => ({ block_id: id, block_type: 32 })) }
      }
    );
    if (res.data?.children) {
      createdCellIds.push(...res.data.children.map(c => c.block_id));
    }
  }
  
  return createdCellIds;
}

async function appendBlockToDoc(token, docId, parentBlockId, block) {
  // Handle table specially
  if (block._isTable) {
    const { tableId, cellIds, cellContents, rowCount, colCount } = block;
    
    // Create table block
    const tableRes = await feishuFetch(
      `/docx/v1/documents/${docId}/blocks/${parentBlockId}/children?document_revision_id=-1`,
      {
        method: 'POST',
        token,
        body: {
          children: [{
            block_id: tableId,
            block_type: 31,
            table: {
              property: { row_size: rowCount, column_size: colCount }
            },
            children: cellIds
          }]
        }
      }
    );
    
    // Get the actual created table block ID and cell IDs from response
    const createdTable = tableRes.data?.children?.[0];
    const createdTableBlockId = createdTable?.block_id;
    const createdCellIds = createdTable?.children || [];
    
    if (!createdTableBlockId) {
      throw new Error('Failed to create table: ' + JSON.stringify(tableRes));
    }
    
    // Add content to each cell using the REAL cell IDs from Feishu response
    for (let i = 0; i < createdCellIds.length; i++) {
      const realCellId = createdCellIds[i];
      const row = Math.floor(i / colCount);
      const col = i % colCount;
      const content = cellContents[row]?.[col] || '';
      
      await feishuFetch(
        `/docx/v1/documents/${docId}/blocks/${realCellId}/children?document_revision_id=-1`,
        {
          method: 'POST',
          token,
          body: {
            children: [{
              block_type: 2,
              text: { elements: [{ text_run: { content } }] }
            }]
          }
        }
      );
    }
    
    return { type: 'table', status: 'created' };
  }
  
  // Regular block
  const res = await feishuFetch(
    `/docx/v1/documents/${docId}/blocks/${parentBlockId}/children?document_revision_id=-1`,
    {
      method: 'POST',
      token,
      body: { children: [block] }
    }
  );
  
  return { type: 'block', status: res.data };
}

function print(obj) {
  process.stdout.write(`${JSON.stringify(obj, null, 2)}\n`);
}

async function main() {
  const args = parseArgs(process.argv);
  const cmd = args._;

  if (!cmd || ['-h', '--help', 'help'].includes(cmd)) {
    print({
      usage: [
        'node feishu-markdown-to-docx.js run --doc-id <id> --parent-block-id <id> --markdown-file <file>',
        'Example:',
        '  node feishu-markdown-to-docx.js run --doc-id xxx --parent-block-id xxx --markdown-file /tmp/test.md'
      ]
    });
    return;
  }

  if (cmd === 'run') {
    if (!args.docId || !args.parentBlockId || !args.markdownFile) {
      throw new Error('Missing required params: --doc-id, --parent-block-id, --markdown-file');
    }
    
    const md = fs.readFileSync(args.markdownFile, 'utf8');
    const ast = parseMarkdown(md);
    const blocks = transformMarkdownToBlocks(ast);
    
    const token = await getTenantToken();
    const results = [];
    
    for (let i = 0; i < blocks.length; i++) {
      const block = blocks[i];
      try {
        const result = await appendBlockToDoc(token, args.docId, args.parentBlockId, block);
        results.push(result);
        // Add delay between blocks - longer for tables
        const delay = block._isTable ? 1500 : 500;
        await new Promise(r => setTimeout(r, delay));
      } catch (e) {
        results.push({ type: 'error', message: e.message });
        // On error, wait much longer
        await new Promise(r => setTimeout(r, 5000));
      }
    }
    
    print({ ok: true, blocksCreated: blocks.length, results });
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

main().catch((err) => {
  process.stderr.write(`[feishu-markdown-to-docx] ${err.message}\n`);
  process.exit(1);
});
