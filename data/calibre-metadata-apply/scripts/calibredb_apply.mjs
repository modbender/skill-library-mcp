#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const ALLOWED = new Set(['title','title_sort','authors','author_sort','series','series_index','tags','publisher','pubdate','languages','comments']);
const OC_START = '<!-- OC_ANALYSIS_START -->';
const OC_END = '<!-- OC_ANALYSIS_END -->';
const DEFAULT_AUTH_FILE = path.join(os.homedir(), '.config', 'calibre-metadata-apply', 'auth.json');

const I18N = {
  ja: { title: 'OpenClaw解析', summary: '要約', key_points: '重要ポイント', reread: '再読ガイド', generated_at: '生成日時', file_hash: 'ファイルハッシュ', analysis_tags: '解析タグ', section: '章/節', page: 'ページ', chunk: 'チャンク' },
  en: { title: 'OpenClaw Analysis', summary: 'Summary', key_points: 'Key points', reread: 'Reread guide', generated_at: 'generated_at', file_hash: 'file_hash', analysis_tags: 'analysis_tags', section: 'section', page: 'page', chunk: 'chunk' },
};

function parseArgs(argv) {
  const out = { apply: false, lang: 'ja', 'password-env': 'CALIBRE_PASSWORD', 'auth-file': DEFAULT_AUTH_FILE, _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { out._.push(a); continue; }
    const k = a.slice(2);
    if (['apply','save-auth','save-plain-password'].includes(k)) out[k] = true;
    else out[k] = argv[++i];
  }
  return out;
}

function buildSafeEnv() {
  return {
    PATH: process.env.PATH || '',
    HOME: process.env.HOME || '',
    LANG: process.env.LANG || 'C.UTF-8',
    LC_ALL: process.env.LC_ALL || '',
    LC_CTYPE: process.env.LC_CTYPE || '',
    SYSTEMROOT: process.env.SYSTEMROOT || '',
    WINDIR: process.env.WINDIR || '',
  };
}

function run(cmd) {
  const cp = spawnSync(cmd[0], cmd.slice(1), { encoding: 'utf-8', env: buildSafeEnv() });
  return { rc: cp.status || 0, out: cp.stdout || '', err: cp.stderr || '' };
}
function runOk(cmd) {
  const { rc, out, err } = run(cmd);
  if (rc !== 0) throw new Error(`calibredb failed (${rc})\nCMD: ${redactedCmd(cmd)}\nERR:\n${err.trim()}`);
  return out;
}

function loadAuthFile(p) {
  try {
    if (!fs.existsSync(p)) return {};
    const d = JSON.parse(fs.readFileSync(p, 'utf-8'));
    const o = {};
    for (const k of ['username','password','password_env']) {
      const v = d?.[k];
      if (typeof v === 'string' && v.trim()) o[k] = v.trim();
    }
    return o;
  } catch { return {}; }
}

function saveAuthFile(p, { username, password, passwordEnv }) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const payload = { username };
  if (password) payload.password = password;
  if (passwordEnv) payload.password_env = passwordEnv;
  fs.writeFileSync(p, JSON.stringify(payload, null, 2) + '\n', 'utf-8');
  fs.chmodSync(p, 0o600);
}

function resolveAuth(args) {
  const auth = loadAuthFile(String(args['auth-file'] || DEFAULT_AUTH_FILE));
  const username = args.username || auth.username || (process.env.CALIBRE_USERNAME || '').trim() || null;
  let password = args.password || '';
  if (!password && args['password-env']) password = process.env[String(args['password-env'])] || '';
  if (!password && auth.password_env) password = process.env[auth.password_env] || '';
  if (!password) password = auth.password || '';
  const usedPasswordEnv = args['password-env'] || auth.password_env || null;

  if (args['save-auth']) {
    if (!username) throw new Error('--save-auth requires username (provide --username or CALIBRE_USERNAME or existing auth file)');
    if (!password && !usedPasswordEnv) throw new Error('--save-auth requires password source (--password or --password-env with env value)');
    saveAuthFile(String(args['auth-file']), {
      username,
      password: args['save-plain-password'] ? password : null,
      passwordEnv: usedPasswordEnv,
    });
  }
  return { username, password, usedPasswordEnv };
}

function commonArgs(args, auth) {
  const r = ['--with-library', String(args['with-library'])];
  if (auth.username) r.push('--username', String(auth.username));
  if (auth.password) r.push('--password', String(auth.password));
  return r;
}

function redactedCmd(cmd) {
  const out = [];
  let maskNext = false;
  for (const t of cmd) {
    if (maskNext) { out.push('********'); maskNext = false; continue; }
    out.push(t);
    if (t === '--password') maskNext = true;
  }
  return out.map(x => (/[\s'"\\]/.test(x) ? JSON.stringify(x) : x)).join(' ');
}

function toFieldValue(v) { return Array.isArray(v) ? v.map(String).join(',') : String(v); }

function splitMulti(v) {
  if (v == null) return [];
  const raw = Array.isArray(v) ? v.map(String) : String(v).split(/[,;\n]/);
  const out = [];
  const seen = new Set();
  for (const x of raw) {
    const t = String(x).trim();
    if (!t) continue;
    const k = t.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k); out.push(t);
  }
  return out;
}

function fetchBook(args, auth, bookId, fields) {
  const cmd = ['calibredb','list','--for-machine','--fields',fields,'--search',`id:${bookId}`,'--limit','5', ...commonArgs(args, auth)];
  const rows = JSON.parse(runOk(cmd));
  return rows.find(r => String(r?.id) === String(bookId)) || null;
}

function renderAnalysisHtml(bookId, analysis, defaultLang='ja') {
  const summary = String(analysis?.summary || '').trim();
  const highlights = splitMulti(analysis?.highlights || []);
  const tags = splitMulti(analysis?.tags || []);
  const reread = Array.isArray(analysis?.reread) ? analysis.reread : [];
  const generatedAt = String(analysis?.generated_at || '').trim() || new Date().toISOString();
  const sourceHash = String(analysis?.file_hash || '').trim();
  let lang = String(analysis?.lang || defaultLang).toLowerCase();
  if (!I18N[lang]) lang = I18N[defaultLang] ? defaultLang : 'en';
  const tr = I18N[lang];

  const lines = [OC_START, '<div class="openclaw-analysis">', `<h3>${tr.title}</h3>`];
  if (summary) lines.push(`<p><strong>${tr.summary}:</strong> ${summary}</p>`);
  if (highlights.length) {
    lines.push(`<h4>${tr.key_points}</h4><ul>`);
    for (const h of highlights) lines.push(`<li>${h}</li>`);
    lines.push('</ul>');
  }
  if (reread.length) {
    lines.push(`<h4>${tr.reread}</h4><ul>`);
    for (const item of reread) {
      if (!item || typeof item !== 'object') continue;
      const section = String(item.section || '').trim();
      const page = String(item.page || '').trim();
      const chunk = String(item.chunk_id || '').trim();
      const reason = String(item.reason || '').trim();
      const parts = [section ? `${tr.section}: ${section}` : '', page ? `${tr.page}: ${page}` : '', chunk ? `${tr.chunk}: ${chunk}` : '', reason].filter(Boolean);
      if (parts.length) lines.push(`<li>${parts.join(' | ')}</li>`);
    }
    lines.push('</ul>');
  }
  const meta = [`${tr.generated_at}: ${generatedAt}`];
  if (sourceHash) meta.push(`${tr.file_hash}: ${sourceHash}`);
  if (tags.length) meta.push(`${tr.analysis_tags}: ${tags.join(', ')}`);
  lines.push(`<p><em>${meta.join(' / ')}</em></p>`);
  lines.push('</div>', OC_END);
  return lines.join('\n');
}

function upsertOcBlock(existingHtml, blockHtml) {
  const existing = String(existingHtml || '');
  const re = new RegExp(OC_START.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\s\\S]*?' + OC_END.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (re.test(existing)) return existing.replace(re, blockHtml);
  if (existing.trim()) return existing.replace(/\s+$/, '') + '\n\n' + blockHtml;
  return blockHtml;
}

function buildFields(args, auth, rec) {
  const r = { ...rec };
  const bid = String(r.id || '').trim();
  if (!bid) throw new Error('missing id');

  if (r.analysis && typeof r.analysis === 'object') {
    r.comments_html = renderAnalysisHtml(bid, r.analysis, args.lang || 'ja');
    if (!r.analysis_tags) r.analysis_tags = r.analysis.tags || [];
  }

  if (r.comments_html) {
    const current = fetchBook(args, auth, bid, 'id,comments') || {};
    r.comments = upsertOcBlock(String(current.comments || ''), String(r.comments_html));
  }

  if (r.tags !== undefined || r.analysis_tags !== undefined || r.tags_remove !== undefined) {
    const incoming = splitMulti(r.tags);
    const extra = splitMulti(r.analysis_tags);
    const removeSet = new Set(splitMulti(r.tags_remove).map(x => x.toLowerCase()));
    const mergeExisting = r.tags_merge !== false;
    let existingTags = [];
    if (mergeExisting) {
      const current = fetchBook(args, auth, bid, 'id,tags') || {};
      existingTags = splitMulti(current.tags || []);
    }
    let merged = splitMulti([...existingTags, ...incoming, ...extra]);
    if (removeSet.size) merged = merged.filter(t => !removeSet.has(t.toLowerCase()));
    r.tags = merged;
  }

  const fields = [];
  for (const [k, v] of Object.entries(r)) {
    if (k === 'id') continue;
    if (!ALLOWED.has(k)) continue;
    if (v == null) continue;
    fields.push([k, toFieldValue(v)]);
  }
  if (!fields.length) throw new Error('no updatable fields');
  return fields;
}

function buildCmd(args, auth, rec) {
  const bid = String(rec.id || '').trim();
  if (!bid) throw new Error('missing id');
  const fields = buildFields(args, auth, rec);
  const cmd = ['calibredb','set_metadata',bid];
  for (const [k, v] of fields) cmd.push('--field', `${k}:${v}`);
  cmd.push(...commonArgs(args, auth));
  return cmd;
}

async function readStdinLines() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString('utf-8').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args['with-library']) throw new Error('missing --with-library');
  if (!['ja','en'].includes(String(args.lang || 'ja'))) throw new Error('--lang must be ja|en');
  const auth = resolveAuth(args);

  const lines = await readStdinLines();
  if (!lines.length) {
    console.log(JSON.stringify({ ok: true, summary: { total: 0, planned: 0, applied: 0, failed: 0 }, results: [] }, null, 2));
    return;
  }

  const results = [];
  let planned = 0, applied = 0, failed = 0;

  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];
    try {
      const rec = JSON.parse(ln);
      const cmd = buildCmd(args, auth, rec);
      planned++;
      if (!args.apply) {
        results.push({ line: i + 1, id: rec.id, action: 'planned', cmd: redactedCmd(cmd) });
        continue;
      }
      const { rc, out, err } = run(cmd);
      if (rc === 0) {
        applied++;
        results.push({ line: i + 1, id: rec.id, action: 'applied', stdout: out.trim() });
      } else {
        failed++;
        results.push({ line: i + 1, id: rec.id, action: 'failed', stderr: err.trim(), rc });
      }
    } catch (e) {
      failed++;
      results.push({ line: i + 1, action: 'error', error: String(e?.message || e) });
    }
  }

  const ok = failed === 0;
  console.log(JSON.stringify({ ok, mode: args.apply ? 'apply' : 'dry-run', summary: { total: lines.length, planned, applied, failed }, results }, null, 2));
  if (!ok) process.exit(1);
}

main().catch(e => { console.error(String(e?.stack || e)); process.exit(1); });
