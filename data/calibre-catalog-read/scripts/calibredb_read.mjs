#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, chmodSync } from 'node:fs';
import { dirname } from 'node:path';
import os from 'node:os';

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      out[k] = v;
    } else {
      out._.push(a);
    }
  }
  return out;
}

const DEFAULT_AUTH_FILE = `${os.homedir()}/.config/calibre-catalog-read/auth.json`;

function loadAuthFile(path) {
  try {
    if (!existsSync(path)) return {};
    const raw = JSON.parse(readFileSync(path, 'utf8'));
    if (!raw || typeof raw !== 'object') return {};
    const out = {};
    for (const k of ['username', 'password', 'password_env']) {
      const v = raw[k];
      if (typeof v === 'string' && v.trim()) out[k] = v.trim();
    }
    return out;
  } catch {
    return {};
  }
}

function saveAuthFile(path, { username, password, passwordEnv }) {
  mkdirSync(dirname(path), { recursive: true });
  const payload = { username };
  if (password) payload.password = password;
  if (passwordEnv) payload.password_env = passwordEnv;
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  chmodSync(path, 0o600);
}

function resolveAuth(args) {
  const authFile = String(args['auth-file'] || DEFAULT_AUTH_FILE);
  const saved = loadAuthFile(authFile);
  const envUser = (process.env.CALIBRE_USERNAME || '').trim();
  const username = args.username ? String(args.username) : (saved.username || envUser || '');

  let password = args.password ? String(args.password) : '';
  const explicitEnv = args['password-env'] ? String(args['password-env']) : '';
  const savedEnv = saved.password_env || '';
  const passwordEnv = explicitEnv || savedEnv || 'CALIBRE_PASSWORD';

  if (!password && passwordEnv) password = process.env[passwordEnv] || '';
  if (!password && saved.password) password = saved.password;

  if (args['save-auth']) {
    if (!username) throw new Error('--save-auth requires username (via --username or auth file)');
    if (!password && !passwordEnv) throw new Error('--save-auth requires password source (--password or --password-env)');
    saveAuthFile(authFile, {
      username,
      password: args['save-plain-password'] ? password : '',
      passwordEnv,
    });
  }

  return { username, password };
}

function commonArgs(args) {
  const r = ['--with-library', String(args['with-library'] || '')];
  const auth = resolveAuth(args);
  if (auth.username) r.push('--username', auth.username);
  if (auth.password) r.push('--password', auth.password);
  return r;
}

function run(cmd) {
  const cp = spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf8' });
  if (cp.status !== 0) {
    throw new Error(`calibredb failed (${cp.status})\nCMD: ${cmd.map(x => JSON.stringify(x)).join(' ')}\nERR:\n${(cp.stderr || '').trim()}`);
  }
  return cp.stdout || '';
}

function toJson(text) {
  return JSON.parse(text);
}

function requireArg(args, key, hint = '') {
  if (!args[key]) {
    throw new Error(`missing --${key}${hint ? ` (${hint})` : ''}`);
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0];

  if (!cmd || !['list', 'search', 'id'].includes(cmd)) {
    console.log(JSON.stringify({
      ok: false,
      error: 'usage: calibredb_read.mjs <list|search|id> --with-library <url#lib> [--username u] [--password p|--password-env ENV] [--auth-file path] [--save-auth] [--save-plain-password] [--fields f] [--limit n] [--query q] [--book-id id]'
    }, null, 2));
    process.exit(1);
  }

  try {
    requireArg(args, 'with-library', 'http://HOST:PORT/#LIBRARY_ID');
    const fieldsDefault = 'id,title,authors,series,series_index,tags,formats,publisher,pubdate,languages,last_modified';
    const fields = String(args.fields || (cmd === 'id'
      ? `${fieldsDefault},comments`
      : fieldsDefault));
    const limit = Number(args.limit || 100);

    if (cmd === 'list') {
      const out = run([
        'calibredb', 'list', '--for-machine', '--fields', fields, '--limit', String(limit),
        ...commonArgs(args),
      ]);
      console.log(JSON.stringify({ ok: true, mode: 'list', fields, items: toJson(out) }, null, 2));
      return;
    }

    if (cmd === 'search') {
      requireArg(args, 'query');
      const query = String(args.query);
      const out = run([
        'calibredb', 'list', '--for-machine', '--fields', fields,
        '--search', query, '--limit', String(limit),
        ...commonArgs(args),
      ]);
      console.log(JSON.stringify({ ok: true, mode: 'search', query, fields, items: toJson(out) }, null, 2));
      return;
    }

    // id
    requireArg(args, 'book-id');
    const bookId = String(args['book-id']);
    const out = run([
      'calibredb', 'list', '--for-machine', '--fields', fields,
      '--search', `id:${bookId}`, '--limit', '5',
      ...commonArgs(args),
    ]);
    const rows = toJson(out);
    const item = rows.find(r => String(r?.id) === bookId) || null;
    console.log(JSON.stringify({ ok: true, mode: 'id', book_id: bookId, item }, null, 2));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: String(e?.message || e) }, null, 2));
    process.exit(1);
  }
}

main();
