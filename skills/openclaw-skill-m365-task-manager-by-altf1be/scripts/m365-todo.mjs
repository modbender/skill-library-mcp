#!/usr/bin/env node

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { PublicClientApplication } from '@azure/msal-node';

const GRAPH_BASE = 'https://graph.microsoft.com/v1.0';
const SCOPES = ['User.Read', 'Tasks.ReadWrite', 'offline_access'];

function env(name, required = true, fallback = undefined) {
  const v = process.env[name] ?? fallback;
  if (required && !v) throw new Error(`Missing required env var: ${name}`);
  return v;
}

function defaultCachePath() {
  return path.join(os.homedir(), '.cache', 'openclaw', 'm365-task-manager-token.json');
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const [k, inline] = a.split('=');
      const key = k.slice(2);
      if (inline !== undefined) args[key] = inline;
      else if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) args[key] = argv[++i];
      else args[key] = true;
    } else {
      args._.push(a);
    }
  }
  return args;
}

function help() {
  console.log(`m365-todo - Microsoft Graph To Do CRUD\n
Usage:
  m365-todo info
  m365-todo lists
  m365-todo tasks:list --list-id <id>
  m365-todo tasks:list --list-name "Tasks"
  m365-todo tasks:create --list-id <id> --title "Task title" [--body "..."] [--due 2026-02-28]
  m365-todo tasks:update --list-id <id> --task-id <id> [--title "..."] [--body "..."] [--status notStarted|inProgress|completed|waitingOnOthers|deferred] [--due YYYY-MM-DD]
  m365-todo tasks:delete --list-id <id> --task-id <id>

Required env:
  M365_TENANT_ID
  M365_CLIENT_ID
Optional env:
  M365_TOKEN_CACHE_PATH
`);
}

async function createPca() {
  const tenantId = env('M365_TENANT_ID');
  const clientId = env('M365_CLIENT_ID');
  const cachePath = env('M365_TOKEN_CACHE_PATH', false, defaultCachePath());

  const pca = new PublicClientApplication({
    auth: {
      clientId,
      authority: `https://login.microsoftonline.com/${tenantId}`,
    },
  });

  ensureDir(cachePath);
  if (fs.existsSync(cachePath)) {
    try {
      const raw = fs.readFileSync(cachePath, 'utf8');
      pca.getTokenCache().deserialize(raw);
    } catch {
      // ignore corrupted cache, device login will refresh
    }
  }

  return { pca, cachePath };
}

async function saveCache(pca, cachePath) {
  const serialized = await pca.getTokenCache().serialize();
  fs.writeFileSync(cachePath, serialized, 'utf8');
}

async function getAccessToken() {
  const { pca, cachePath } = await createPca();
  const accounts = await pca.getTokenCache().getAllAccounts();

  if (accounts.length > 0) {
    try {
      const silent = await pca.acquireTokenSilent({
        account: accounts[0],
        scopes: SCOPES,
      });
      if (silent?.accessToken) {
        await saveCache(pca, cachePath);
        return silent.accessToken;
      }
    } catch {
      // fallback to device code
    }
  }

  const device = await pca.acquireTokenByDeviceCode({
    scopes: SCOPES,
    deviceCodeCallback: (resp) => {
      console.error(resp.message);
    },
  });

  if (!device?.accessToken) throw new Error('Failed to acquire access token');
  await saveCache(pca, cachePath);
  return device.accessToken;
}

async function graph(method, endpoint, token, body) {
  const res = await fetch(`${GRAPH_BASE}${endpoint}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = '';
    try {
      const j = await res.json();
      detail = j?.error?.message || JSON.stringify(j);
    } catch {
      detail = await res.text();
    }
    throw new Error(`Graph ${method} ${endpoint} failed (${res.status}): ${detail}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

function must(args, key) {
  const v = args[key];
  if (!v) throw new Error(`Missing --${key}`);
  return v;
}

function parseDueDate(d) {
  if (!d) return undefined;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) throw new Error('Invalid --due format. Use YYYY-MM-DD');
  return { dateTime: `${d}T17:00:00`, timeZone: 'Europe/Brussels' };
}

async function resolveListId(args, token) {
  if (args['list-id']) return args['list-id'];
  if (!args['list-name']) throw new Error('Provide --list-id or --list-name');

  const data = await graph('GET', '/me/todo/lists', token);
  const found = data.value.find((x) => x.displayName.toLowerCase() === String(args['list-name']).toLowerCase());
  if (!found) throw new Error(`List not found: ${args['list-name']}`);
  return found.id;
}

async function cmdInfo(token) {
  const me = await graph('GET', '/me?$select=id,displayName,userPrincipalName', token);
  console.log(JSON.stringify({
    connected: true,
    user: me,
    scopes: SCOPES,
  }, null, 2));
}

async function cmdLists(token) {
  const data = await graph('GET', '/me/todo/lists', token);
  console.log(JSON.stringify(data.value, null, 2));
}

async function cmdTasksList(args, token) {
  const listId = await resolveListId(args, token);
  const data = await graph('GET', `/me/todo/lists/${listId}/tasks?$top=100`, token);
  console.log(JSON.stringify(data.value, null, 2));
}

async function cmdTasksCreate(args, token) {
  const listId = await resolveListId(args, token);
  const title = must(args, 'title');
  const body = {
    title,
  };
  if (args.body) body.body = { content: String(args.body), contentType: 'text' };
  const due = parseDueDate(args.due);
  if (due) body.dueDateTime = due;

  const created = await graph('POST', `/me/todo/lists/${listId}/tasks`, token, body);
  console.log(JSON.stringify(created, null, 2));
}

async function cmdTasksUpdate(args, token) {
  const listId = await resolveListId(args, token);
  const taskId = must(args, 'task-id');
  const patch = {};

  if (args.title) patch.title = String(args.title);
  if (args.body) patch.body = { content: String(args.body), contentType: 'text' };
  if (args.status) patch.status = String(args.status);
  if (args.due) patch.dueDateTime = parseDueDate(args.due);

  if (Object.keys(patch).length === 0) throw new Error('No fields to update. Use --title/--body/--status/--due');

  const updated = await graph('PATCH', `/me/todo/lists/${listId}/tasks/${taskId}`, token, patch);
  console.log(JSON.stringify(updated, null, 2));
}

async function cmdTasksDelete(args, token) {
  const listId = await resolveListId(args, token);
  const taskId = must(args, 'task-id');
  await graph('DELETE', `/me/todo/lists/${listId}/tasks/${taskId}`, token);
  console.log(JSON.stringify({ deleted: true, listId, taskId }, null, 2));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  if (!command || command === '--help' || command === 'help') {
    help();
    process.exit(0);
  }

  const token = await getAccessToken();

  switch (command) {
    case 'info': return cmdInfo(token);
    case 'lists': return cmdLists(token);
    case 'tasks:list': return cmdTasksList(args, token);
    case 'tasks:create': return cmdTasksCreate(args, token);
    case 'tasks:update': return cmdTasksUpdate(args, token);
    case 'tasks:delete': return cmdTasksDelete(args, token);
    default:
      help();
      throw new Error(`Unknown command: ${command}`);
  }
}

main().catch((err) => {
  console.error(`ERROR: ${err.message}`);
  process.exit(1);
});
