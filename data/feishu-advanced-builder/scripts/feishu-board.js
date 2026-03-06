#!/usr/bin/env node
/*
 * Feishu Board API helper
 * 中文说明：
 * - 支持 tenant_access_token 获取
 * - 在 docx 中创建 whiteboard block（block_type=43）
 * - 调用画板语法接口填充 Mermaid / PlantUML
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

async function feishuFetch(path, { method = 'GET', token, body } = {}) {
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
    throw new Error(`Non-JSON response: ${res.status} ${text.slice(0, 500)}`);
  }

  if (!res.ok || json.code !== 0) {
    throw new Error(`Feishu API error (${method} ${path}): HTTP ${res.status}, code=${json.code}, msg=${json.msg}, body=${text.slice(0, 800)}`);
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

function deepFindWhiteboardToken(obj) {
  if (!obj || typeof obj !== 'object') return undefined;

  // board.token 是实际返回的字段名
  if (obj.board && typeof obj.board.token === 'string') return obj.board.token;
  if (typeof obj.whiteboard_token === 'string') return obj.whiteboard_token;
  if (obj.whiteboard && typeof obj.whiteboard.token === 'string') return obj.whiteboard.token;

  for (const key of Object.keys(obj)) {
    const v = obj[key];
    if (v && typeof v === 'object') {
      const found = deepFindWhiteboardToken(v);
      if (found) return found;
    }
  }
  return undefined;
}

async function createWhiteboardBlock({ token, docId, parentBlockId, index = 0 }) {
  const path = `/docx/v1/documents/${docId}/blocks/${parentBlockId}/children?document_revision_id=-1`;
  const payload = {
    children: [
      {
        block_type: 43,
        board: {
          align: 1,
        },
      },
    ],
    index: Number(index),
  };

  const createRes = await feishuFetch(path, {
    method: 'POST',
    token,
    body: payload,
  });

  const blockId = createRes?.data?.children?.[0]?.block_id || createRes?.data?.children?.[0];
  if (!blockId) {
    return { createRes, blockId: null, whiteboardToken: null };
  }

  const blockRes = await feishuFetch(
    `/docx/v1/documents/${docId}/blocks/${blockId}?document_revision_id=-1`,
    { method: 'GET', token }
  );

  const whiteboardToken = deepFindWhiteboardToken(blockRes?.data || blockRes);
  return { createRes, blockRes, blockId, whiteboardToken: whiteboardToken || null };
}

function normalizeSyntaxType(input) {
  if (!input) return 2;
  const s = String(input).toLowerCase();
  if (s === '1' || s === 'plantuml') return 1;
  if (s === '2' || s === 'mermaid') return 2;
  throw new Error(`Unsupported syntaxType: ${input}, expected mermaid|plantuml|1|2`);
}

async function fillDiagram({ token, whiteboardToken, code, syntaxType }) {
  const st = normalizeSyntaxType(syntaxType);
  const path = `/board/v1/whiteboards/${whiteboardToken}/nodes/plantuml`;
  const payload = {
    plant_uml_code: code,
    style_type: 1,
    syntax_type: st,
  };
  return feishuFetch(path, { method: 'POST', token, body: payload });
}

function readCode(args) {
  if (args.code) return args.code;
  if (args.codeFile) return fs.readFileSync(args.codeFile, 'utf8');
  throw new Error('Missing --code or --code-file');
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
        'node feishu-board.js get-tenant-token',
        'node feishu-board.js create-whiteboard --doc-id <id> --parent-block-id <id> [--index 0]',
        'node feishu-board.js fill-diagram --whiteboard-token <token> --syntax-type mermaid|plantuml --code-file /tmp/board.mmd',
        'node feishu-board.js run --doc-id <id> --parent-block-id <id> --syntax-type mermaid|plantuml --code-file /tmp/board.mmd [--index 0]',
      ],
    });
    return;
  }

  if (cmd === 'get-tenant-token') {
    const token = await getTenantToken();
    print({ ok: true, tenantAccessToken: token });
    return;
  }

  const token = await getTenantToken();

  if (cmd === 'create-whiteboard') {
    if (!args.docId || !args.parentBlockId) throw new Error('Missing --doc-id or --parent-block-id');
    const out = await createWhiteboardBlock({
      token,
      docId: args.docId,
      parentBlockId: args.parentBlockId,
      index: args.index || 0,
    });
    print({ ok: true, ...out });
    return;
  }

  if (cmd === 'fill-diagram') {
    if (!args.whiteboardToken) throw new Error('Missing --whiteboard-token');
    const code = readCode(args);
    const res = await fillDiagram({ token, whiteboardToken: args.whiteboardToken, code, syntaxType: args.syntaxType || 'mermaid' });
    print({ ok: true, response: res });
    return;
  }

  if (cmd === 'run') {
    if (!args.docId || !args.parentBlockId) throw new Error('Missing --doc-id or --parent-block-id');
    const code = readCode(args);
    const created = await createWhiteboardBlock({
      token,
      docId: args.docId,
      parentBlockId: args.parentBlockId,
      index: args.index || 0,
    });

    if (!created.whiteboardToken) {
      print({
        ok: false,
        message: 'Whiteboard block created but token not found from block detail. Use returned blockId to inspect docx block schema or provide existing whiteboard token and run fill-diagram.',
        blockId: created.blockId || null,
        createRes: created.createRes,
        blockRes: created.blockRes || null,
      });
      process.exitCode = 2;
      return;
    }

    const fillRes = await fillDiagram({
      token,
      whiteboardToken: created.whiteboardToken,
      code,
      syntaxType: args.syntaxType || 'mermaid',
    });

    print({
      ok: true,
      whiteboardToken: created.whiteboardToken,
      blockId: created.blockId,
      createWhiteboard: created.createRes,
      fillDiagram: fillRes,
    });
    return;
  }

  throw new Error(`Unknown command: ${cmd}`);
}

main().catch((err) => {
  process.stderr.write(`[feishu-board] ${err.message}\n`);
  process.exit(1);
});
