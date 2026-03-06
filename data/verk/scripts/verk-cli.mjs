#!/usr/bin/env node

/**
 * Verk CLI — OpenClaw skill wrapper for Verk REST API
 * Uses built-in Node.js fetch (Node 18+), no external dependencies.
 *
 * Required env vars:
 *   VERK_API_KEY  — Verk API key (format: verk_sk_...)
 *   VERK_ORG_ID   — Organization ID
 *
 * Optional:
 *   VERK_API_URL  — Override base URL (default: https://c0x9lrm7ih.execute-api.us-east-1.amazonaws.com/v1)
 */

const API_BASE = process.env.VERK_API_URL || 'https://c0x9lrm7ih.execute-api.us-east-1.amazonaws.com/v1';
const API_KEY = process.env.VERK_API_KEY;
const ORG_ID = process.env.VERK_ORG_ID;

// ─── Helpers ──────────────────────────────────────────────

function die(msg) {
  console.error(JSON.stringify({ error: msg }));
  process.exit(1);
}

if (!API_KEY) die('VERK_API_KEY environment variable is required');
if (!ORG_ID) die('VERK_ORG_ID environment variable is required');

function orgUrl(path) {
  return `${API_BASE}/organizations/${ORG_ID}${path}`;
}

async function request(method, url, body) {
  const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  };

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const errMsg = data?.error?.message || data?.message || `HTTP ${res.status}`;
    die(errMsg);
  }

  return data;
}

function parseArgs(argv) {
  const args = {};
  const positional = [];
  let i = 0;

  while (i < argv.length) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i += 2;
      } else {
        args[key] = true;
        i += 1;
      }
    } else {
      positional.push(arg);
      i += 1;
    }
  }

  return { args, positional };
}

// ─── Task commands ────────────────────────────────────────

async function tasksList(args) {
  const params = new URLSearchParams();
  if (args.status) params.set('status', args.status);
  if (args.priority) params.set('priority', args.priority);
  if (args.search) params.set('search', args.search);
  if (args.limit) params.set('limit', args.limit);

  const qs = params.toString();
  const url = orgUrl(`/tasks${qs ? '?' + qs : ''}`);
  const data = await request('GET', url);
  console.log(JSON.stringify(data, null, 2));
}

async function tasksGet(taskId) {
  if (!taskId) die('Task ID is required: tasks get <taskId>');
  const data = await request('GET', orgUrl(`/tasks/${taskId}`));
  console.log(JSON.stringify(data, null, 2));
}

async function tasksCreate(args) {
  if (!args.title) die('--title is required for task creation');

  const body = { title: args.title };
  if (args.description) body.description = args.description;
  if (args.status) body.status = args.status;
  if (args.priority) body.priority = args.priority;
  if (args.assigned) body.assigned_to = args.assigned.split(',');
  if (args.project) body.project_id = args.project;
  if (args.due) body.due_date = args.due;

  const data = await request('POST', orgUrl('/tasks'), body);
  console.log(JSON.stringify(data, null, 2));
}

async function tasksUpdate(taskId, args) {
  if (!taskId) die('Task ID is required: tasks update <taskId> [--field value]');

  const body = {};
  if (args.title) body.title = args.title;
  if (args.description) body.description = args.description;
  if (args.status) body.status = args.status;
  if (args.priority) body.priority = args.priority;
  if (args.assigned) body.assigned_to = args.assigned.split(',');
  if (args.project) body.project_id = args.project;
  if (args.due) body.due_date = args.due;

  if (Object.keys(body).length === 0) die('At least one field to update is required');

  const data = await request('PUT', orgUrl(`/tasks/${taskId}`), body);
  console.log(JSON.stringify(data, null, 2));
}

async function tasksDelete(taskId) {
  if (!taskId) die('Task ID is required: tasks delete <taskId>');
  const data = await request('DELETE', orgUrl(`/tasks/${taskId}`));
  console.log(JSON.stringify(data, null, 2));
}

async function tasksComment(taskId, args) {
  if (!taskId) die('Task ID is required: tasks comment <taskId> --text "..."');
  if (!args.text) die('--text is required for adding a comment');

  const body = { comment_text: args.text };
  const data = await request('POST', orgUrl(`/tasks/${taskId}/comments`), body);
  console.log(JSON.stringify(data, null, 2));
}

// ─── Project commands ─────────────────────────────────────

async function projectsList() {
  const data = await request('GET', orgUrl('/projects'));
  console.log(JSON.stringify(data, null, 2));
}

// ─── Flow commands ────────────────────────────────────────

async function flowsList() {
  const data = await request('GET', orgUrl('/flows'));
  console.log(JSON.stringify(data, null, 2));
}

// ─── Router ───────────────────────────────────────────────

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0) {
    die('Usage: verk-cli.mjs <resource> <action> [options]\n  Resources: tasks, projects, flows\n  Run with --help for details');
  }

  const resource = argv[0];
  const action = argv[1];
  const rest = argv.slice(2);
  const { args, positional } = parseArgs(rest);

  switch (resource) {
    case 'tasks':
      switch (action) {
        case 'list':    return tasksList(args);
        case 'get':     return tasksGet(positional[0]);
        case 'create':  return tasksCreate(args);
        case 'update':  return tasksUpdate(positional[0], args);
        case 'delete':  return tasksDelete(positional[0]);
        case 'comment': return tasksComment(positional[0], args);
        default:        die(`Unknown tasks action: ${action}. Available: list, get, create, update, delete, comment`);
      }
      break;

    case 'projects':
      switch (action) {
        case 'list':  return projectsList();
        default:      die(`Unknown projects action: ${action}. Available: list`);
      }
      break;

    case 'flows':
      switch (action) {
        case 'list':    return flowsList();
        default:        die(`Unknown flows action: ${action}. Available: list`);
      }
      break;

    default:
      die(`Unknown resource: ${resource}. Available: tasks, projects, flows`);
  }
}

main().catch(err => die(err.message));
