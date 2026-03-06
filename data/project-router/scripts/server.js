#!/usr/bin/env node
/**
 * mcp-project-router (v1)
 *
 * MCP server that wraps the `project` CLI.
 *
 * Tools:
 * - project_detect
 * - project_context_read
 * - project_target_list
 * - project_target_run
 * - project_workspace_init_plan
 * - project_plan_apply
 * - project_artifact_add_plan
 * - project_search_keyword
 */

const { spawnSync } = require('child_process');
const fs = require('fs');

const PROJECT_BIN = '/home/safa/clawd/bin/project';

let buf = Buffer.alloc(0);
let framing = null; // 'lsp' | 'ndjson'

function send(obj) {
  const json = JSON.stringify(obj);
  if (framing === 'ndjson') {
    process.stdout.write(json + '\n');
    return;
  }
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
    if (framing === 'ndjson') {
      if (!tryParseNdjson()) return;
      continue;
    }

    let sep = '\r\n\r\n';
    let headerEnd = buf.indexOf(sep);
    if (headerEnd === -1) {
      sep = '\n\n';
      headerEnd = buf.indexOf(sep);
    }

    if (headerEnd === -1) {
      if (tryParseNdjson()) continue;
      return;
    }

    const header = buf.slice(0, headerEnd).toString('utf8');
    const m = header.match(/Content-Length:\s*(\d+)/i);
    const sepLen = Buffer.byteLength(sep);
    if (!m) {
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
    } catch {
      continue;
    }
    handle(msg);
  }
}

function okResult(content) {
  return { content: [{ type: 'text', text: typeof content === 'string' ? content : JSON.stringify(content, null, 2) }] };
}

function toolSchemas() {
  return [
    {
      name: 'project_detect',
      description: 'Detect current project root by searching for a .project bundle in parent directories.',
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    },
    {
      name: 'project_context_read',
      description: 'Read the current project context (PROJECT.md + target list).',
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    },
    {
      name: 'project_target_list',
      description: 'List targets for the current project.',
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    },
    {
      name: 'project_target_run',
      description: 'Run a target for the current project. Executes commands from .project/targets.json.',
      inputSchema: {
        type: 'object',
        properties: {
          target: { type: 'string' },
        },
        required: ['target'],
        additionalProperties: false,
      },
    },
    {
      name: 'project_workspace_init_plan',
      description: 'Create an init plan in the current directory (does not write until apply).',
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    },
    {
      name: 'project_plan_apply',
      description: 'Apply a previously created plan by planId.',
      inputSchema: {
        type: 'object',
        properties: { planId: { type: 'string' } },
        required: ['planId'],
        additionalProperties: false,
      },
    },
    {
      name: 'project_artifact_add_plan',
      description: 'Create a plan to add an artifact (path or url) to .project/index/artifacts.json.',
      inputSchema: {
        type: 'object',
        properties: {
          spec: { type: 'string' },
          tags: { type: 'array', items: { type: 'string' }, default: [] },
        },
        required: ['spec'],
        additionalProperties: false,
      },
    },
    {
      name: 'project_search_keyword',
      description: 'Keyword search within .project and common docs.',
      inputSchema: {
        type: 'object',
        properties: { term: { type: 'string' } },
        required: ['term'],
        additionalProperties: false,
      },
    },
  ];
}

function runProject(args) {
  if (!fs.existsSync(PROJECT_BIN)) {
    throw new Error(`project CLI not found at ${PROJECT_BIN}`);
  }
  const r = spawnSync(PROJECT_BIN, args, { encoding: 'utf8' });
  const out = (r.stdout || '') + (r.stderr || '');
  return { code: r.status ?? 1, out };
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
      const pv = params?.protocolVersion || '2024-11-05';
      reply({ protocolVersion: pv, serverInfo: { name: 'mcp-project-router', version: '0.1.0' }, capabilities: { tools: {} } });
      return;
    }

    if (method === 'tools/list') {
      reply({ tools: toolSchemas() });
      return;
    }

    if (method === 'tools/call') {
      const name = params?.name;
      const args = params?.arguments || {};

      if (name === 'project_detect') {
        const r = runProject(['detect']);
        if (r.code !== 0) throw new Error(r.out.trim() || 'detect failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_context_read') {
        const r = runProject(['context']);
        if (r.code !== 0) throw new Error(r.out.trim() || 'context failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_target_list') {
        const r = runProject(['target', 'list']);
        if (r.code !== 0) throw new Error(r.out.trim() || 'target list failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_target_run') {
        const r = runProject(['target', 'run', String(args.target)]);
        // pass-through output; allow nonzero to show failure logs
        reply(okResult({ exitCode: r.code, output: r.out }));
        return;
      }

      if (name === 'project_workspace_init_plan') {
        const r = runProject(['init']);
        if (r.code !== 0) throw new Error(r.out.trim() || 'init failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_plan_apply') {
        const r = runProject(['apply', String(args.planId)]);
        if (r.code !== 0) throw new Error(r.out.trim() || 'apply failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_artifact_add_plan') {
        const spec = String(args.spec);
        const tags = Array.isArray(args.tags) ? args.tags : [];
        const r = runProject(['artifact', 'add', spec, '--tags', tags.join(',')]);
        if (r.code !== 0) throw new Error(r.out.trim() || 'artifact add failed');
        reply(okResult(r.out));
        return;
      }

      if (name === 'project_search_keyword') {
        const r = runProject(['search', 'keyword', String(args.term)]);
        if (r.code !== 0) throw new Error(r.out.trim() || 'search failed');
        reply(okResult(r.out));
        return;
      }

      error(-32601, `Unknown tool: ${name}`);
      return;
    }

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
