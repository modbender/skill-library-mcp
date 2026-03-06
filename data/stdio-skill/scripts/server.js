#!/usr/bin/env node
/**
 * stdio-skill MCP server (minimal implementation; no external deps)
 *
 * Implements a tiny subset of MCP over stdio using LSP-style framing:
 *   Content-Length: <n>\r\n\r\n<json>
 *
 * Supports methods:
 * - initialize
 * - tools/list
 * - tools/call
 *
 * Tools are a filesystem-backed inbox/outbox at:
 *   <repo>/stdio/{inbox,outbox,tmp}
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..', '..'); // repo root
const BASE = path.join(ROOT, 'stdio');
const BOXES = {
  inbox: path.join(BASE, 'inbox'),
  outbox: path.join(BASE, 'outbox'),
  tmp: path.join(BASE, 'tmp'),
};

for (const p of Object.values(BOXES)) fs.mkdirSync(p, { recursive: true });

function safeName(name) {
  if (typeof name !== 'string' || !name.trim()) throw new Error('name must be a non-empty string');
  // prevent path traversal
  if (name.includes('..') || name.includes('/') || name.includes('\\')) throw new Error('invalid name');
  return name;
}

function resolveInBox(box, name) {
  if (!BOXES[box]) throw new Error(`unknown box: ${box}`);
  const n = safeName(name);
  const p = path.join(BOXES[box], n);
  // Ensure still within box
  const rel = path.relative(BOXES[box], p);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('path traversal');
  return p;
}

function listBox(box) {
  if (!BOXES[box]) throw new Error(`unknown box: ${box}`);
  const entries = fs.readdirSync(BOXES[box], { withFileTypes: true });
  return entries
    .filter((e) => e.isFile())
    .map((e) => {
      const p = path.join(BOXES[box], e.name);
      const st = fs.statSync(p);
      return { name: e.name, bytes: st.size, mtimeMs: st.mtimeMs };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

function readFileBase64(box, name) {
  const p = resolveInBox(box, name);
  const buf = fs.readFileSync(p);
  return { name, box, bytes: buf.length, contentBase64: buf.toString('base64') };
}

function writeFileBase64(box, name, contentBase64, overwrite = false) {
  const p = resolveInBox(box, name);
  const exists = fs.existsSync(p);
  if (exists && !overwrite) throw new Error('file exists (set overwrite=true to replace)');
  const buf = Buffer.from(String(contentBase64 || ''), 'base64');
  fs.writeFileSync(p, buf);
  return { name, box, bytes: buf.length, overwritten: exists };
}

function moveFile(fromBox, toBox, name, overwrite = false) {
  const src = resolveInBox(fromBox, name);
  const dst = resolveInBox(toBox, name);
  if (!fs.existsSync(src)) throw new Error('source not found');
  const dstExists = fs.existsSync(dst);
  if (dstExists && !overwrite) throw new Error('destination exists (set overwrite=true)');
  if (dstExists) fs.unlinkSync(dst);
  fs.renameSync(src, dst);
  return { name, fromBox, toBox, overwritten: dstExists };
}

function deleteFile(box, name) {
  const p = resolveInBox(box, name);
  if (!fs.existsSync(p)) return { name, box, deleted: false };
  fs.unlinkSync(p);
  return { name, box, deleted: true };
}

// --- MCP protocol framing ---
let buf = Buffer.alloc(0);
let framing = null; // 'lsp' | 'ndjson'

function send(obj) {
  const json = JSON.stringify(obj);
  if (framing === 'ndjson') {
    process.stdout.write(json + '\n');
    return;
  }
  // default to LSP-style framing
  const header = `Content-Length: ${Buffer.byteLength(json, 'utf8')}\r\n\r\n`;
  process.stdout.write(header);
  process.stdout.write(json);
}

function tryParseNdjson() {
  const s = buf.toString('utf8');
  const idx = s.indexOf('\n');
  if (idx === -1) return false;
  const line = s.slice(0, idx).trim();
  if (!line.startsWith('{')) return false;
  try {
    const msg = JSON.parse(line);
    buf = Buffer.from(s.slice(idx + 1), 'utf8');
    framing = framing || 'ndjson';
    handle(msg);
    return true;
  } catch {
    return false;
  }
}

function parseMessages() {
  while (true) {
    // If it looks like ndjson, handle that first.
    if (framing === 'ndjson') {
      if (!tryParseNdjson()) return;
      continue;
    }

    // Accept both CRLF and LF-only LSP framing.
    let sep = '\r\n\r\n';
    let headerEnd = buf.indexOf(sep);
    if (headerEnd === -1) {
      sep = '\n\n';
      headerEnd = buf.indexOf(sep);
    }

    if (headerEnd === -1) {
      // maybe ndjson
      if (tryParseNdjson()) continue;
      return;
    }

    const header = buf.slice(0, headerEnd).toString('utf8');
    const m = header.match(/Content-Length:\s*(\d+)/i);
    const sepLen = Buffer.byteLength(sep);

    if (!m) {
      // drop junk
      buf = buf.slice(headerEnd + sepLen);
      continue;
    }

    framing = framing || 'lsp';

    const len = parseInt(m[1], 10);
    const total = headerEnd + sepLen + len;
    if (buf.length < total) return;

    const body = buf.slice(headerEnd + sepLen, total).toString('utf8');
    buf = buf.slice(total);

    let msg;
    try {
      msg = JSON.parse(body);
    } catch (e) {
      continue;
    }
    handle(msg);
  }
}

function toolSchemas() {
  const boxEnum = ['inbox', 'outbox', 'tmp'];

  return [
    {
      name: 'stdio_paths',
      description: 'Return the resolved inbox/outbox/tmp paths on disk.',
      inputSchema: {
        type: 'object',
        properties: {},
        additionalProperties: false,
      },
    },
    {
      name: 'stdio_list',
      description: 'List files in a box (inbox|outbox|tmp) with sizes.',
      inputSchema: {
        type: 'object',
        properties: {
          box: { type: 'string', enum: boxEnum, default: 'inbox' },
        },
        required: ['box'],
        additionalProperties: false,
      },
    },
    {
      name: 'stdio_read',
      description: 'Read a file from a box and return base64 content.',
      inputSchema: {
        type: 'object',
        properties: {
          box: { type: 'string', enum: boxEnum },
          name: { type: 'string' },
        },
        required: ['box', 'name'],
        additionalProperties: false,
      },
    },
    {
      name: 'stdio_write',
      description: 'Write a file (base64) into a box.',
      inputSchema: {
        type: 'object',
        properties: {
          box: { type: 'string', enum: boxEnum },
          name: { type: 'string' },
          contentBase64: { type: 'string' },
          overwrite: { type: 'boolean', default: false },
        },
        required: ['box', 'name', 'contentBase64'],
        additionalProperties: false,
      },
    },
    {
      name: 'stdio_move',
      description: 'Move a file between boxes (rename within stdio/{inbox,outbox,tmp}).',
      inputSchema: {
        type: 'object',
        properties: {
          fromBox: { type: 'string', enum: boxEnum },
          toBox: { type: 'string', enum: boxEnum },
          name: { type: 'string' },
          overwrite: { type: 'boolean', default: false },
        },
        required: ['fromBox', 'toBox', 'name'],
        additionalProperties: false,
      },
    },
    {
      name: 'stdio_delete',
      description: 'Delete a file from a box.',
      inputSchema: {
        type: 'object',
        properties: {
          box: { type: 'string', enum: boxEnum },
          name: { type: 'string' },
        },
        required: ['box', 'name'],
        additionalProperties: false,
      },
    }
  ];
}

function okResult(content) {
  // MCP tool return shape: content array with text items is widely supported.
  return { content: [{ type: 'text', text: JSON.stringify(content, null, 2) }] };
}

function handle(msg) {
  const { id, method, params } = msg;
  if (!method) return;

  function reply(result) {
    if (id === undefined || id === null) return;
    send({ jsonrpc: '2.0', id, result });
  }

  function error(code, message) {
    if (id === undefined || id === null) return;
    send({ jsonrpc: '2.0', id, error: { code, message } });
  }

  try {
    if (method === 'initialize') {
      // Echo back the protocol version the client asked for when possible.
      const pv = params?.protocolVersion || '2024-11-05';
      reply({
        protocolVersion: pv,
        serverInfo: { name: 'stdio-skill', version: '0.1.0' },
        capabilities: { tools: {} },
      });
      return;
    }

    if (method === 'tools/list') {
      reply({ tools: toolSchemas() });
      return;
    }

    if (method === 'tools/call') {
      let name = params?.name;
      const args = params?.arguments || {};

      // No aliases; tool names are stable stdio_*.

      if (name === 'stdio_paths') {
        reply(okResult({ root: ROOT, ...BOXES }));
        return;
      }

      if (name === 'stdio_list') {
        reply(okResult({ box: args.box, entries: listBox(args.box) }));
        return;
      }

      if (name === 'stdio_read') {
        reply(okResult(readFileBase64(args.box, args.name)));
        return;
      }

      if (name === 'stdio_write') {
        reply(okResult(writeFileBase64(args.box, args.name, args.contentBase64, !!args.overwrite)));
        return;
      }

      if (name === 'stdio_move') {
        reply(okResult(moveFile(args.fromBox, args.toBox, args.name, !!args.overwrite)));
        return;
      }

      if (name === 'stdio_delete') {
        reply(okResult(deleteFile(args.box, args.name)));
        return;
      }

      error(-32601, `Unknown tool: ${name}`);
      return;
    }

    // ignore notifications like initialized
    if (method === 'initialized') return;

    error(-32601, `Unknown method: ${method}`);
  } catch (e) {
    error(-32000, String(e && e.message ? e.message : e));
  }
}

process.stdin.on('data', (chunk) => {
  buf = Buffer.concat([buf, chunk]);
  parseMessages();
});

process.stdin.on('end', () => process.exit(0));
