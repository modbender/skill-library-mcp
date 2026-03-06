#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const VERSION = '0.1.6';

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function readLines(filePath) {
  const txt = fs.readFileSync(filePath, 'utf8');
  return txt
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l && !l.startsWith('#'));
}

function compilePatterns(rel) {
  const filePath = path.resolve(path.dirname(new URL(import.meta.url).pathname), rel);
  const lines = readLines(filePath);
  return lines.map((s) => new RegExp(s, 'i'));
}

function parseArgs(argv) {
  let cmd = argv[0] || 'help';
  const args = { paths: [], lang: 'en', format: 'text', preset: undefined, diff: undefined, exclude: [], positional: [] };

  // allow: openclaw-sec --help
  if (cmd.startsWith('--')) {
    cmd = 'help';
  }

  const rest = argv.slice(1);
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === '--lang') args.lang = rest[++i] || args.lang;
    else if (a === '--format') args.format = rest[++i] || args.format;
    else if (a === '--out') args.out = rest[++i];
    else if (a === '--preset') args.preset = rest[++i] || args.preset; // repo|workspace
    else if (a === '--diff') args.diff = rest[++i] || args.diff; // staged|head|worktree
    else if (a === '--paths') {
      // comma-separated or repeated
      const v = rest[++i] || '';
      args.paths.push(...v.split(',').map(s => s.trim()).filter(Boolean));
    } else if (a === '--exclude') {
      const v = rest[++i] || '';
      args.exclude.push(...v.split(',').map(s => s.trim()).filter(Boolean));
    } else if (a === '--file') args.file = rest[++i];
    else if (a === '--text') args.text = rest[++i];
    else if (a === '--stdin') args.stdin = true;
    else if (a === '-h' || a === '--help') args.help = true;
    else if (!a.startsWith('-')) args.positional.push(a);
  }

  return { cmd, args };
}

function t(lang, key) {
  const en = {
    usage: `openclaw-sec v${VERSION}\n\nUsage:\n  openclaw-sec check [--lang en|ko] [--format text|json] [--out report.md] [--preset repo|workspace] [--paths ".,skills,scripts,context"] [--exclude "pattern1,pattern2"]\n  openclaw-sec scan-secrets [--preset repo|workspace] [--diff staged|head|worktree] [--out report.md] [--paths ...] [--exclude ...]\n  openclaw-sec scan-egress  [--preset repo|workspace] [--diff staged|head|worktree] [--out report.md] [--paths ...] [--exclude ...]\n  openclaw-sec scan-prompt (--file <path> | --text <text> | --stdin) [--out report.md]\n  openclaw-sec integrity init|check [--out integrity_manifest.json]\n  openclaw-sec release-check [--diff staged|head|worktree] [--out report.md]\n\nExit codes: 0 PASS, 1 WARN, 2 BLOCK\n`,
    pass: 'PASS',
    warn: 'WARN',
    block: 'BLOCK',
  };
  const ko = {
    usage: `openclaw-sec v${VERSION}\n\n사용법:\n  openclaw-sec check [--lang en|ko] [--format text|json] [--out report.md] [--preset repo|workspace] [--paths ".,skills,scripts,context"] [--exclude "pattern1,pattern2"]\n  openclaw-sec scan-secrets [--preset repo|workspace] [--diff staged|head|worktree] [--out report.md] [--paths ...] [--exclude ...]\n  openclaw-sec scan-egress  [--preset repo|workspace] [--diff staged|head|worktree] [--out report.md] [--paths ...] [--exclude ...]\n  openclaw-sec scan-prompt (--file <path> | --text <text> | --stdin) [--out report.md]\n  openclaw-sec integrity init|check [--out integrity_manifest.json]\n  openclaw-sec release-check [--diff staged|head|worktree] [--out report.md]\n\n종료코드: 0 PASS, 1 WARN, 2 BLOCK\n`,
    pass: 'PASS',
    warn: 'WARN',
    block: 'BLOCK',
  };
  return (lang === 'ko' ? ko : en)[key] || en[key] || key;
}

function defaultPaths(preset) {
  if (preset === 'repo') {
    // Prefer git-tracked context rather than walking the whole tree.
    return ['.'];
  }
  // workspace
  const candidates = ['.', 'skills', 'scripts', 'context'];
  return candidates.filter(p => fs.existsSync(p));
}

function shouldSkipDir(name) {
  return new Set(['.git', 'node_modules', '.venv', '.venv-wfb', 'dist', 'build', '.next', '.DS_Store']).has(name);
}

function normalizePath(p) {
  return String(p || '').replace(/\\/g, '/');
}

function isExcluded(filePath, excludeGlobs = []) {
  const fp = normalizePath(filePath);
  for (const g of excludeGlobs) {
    const ng = normalizePath(g);

    // If g is a bare filename (no slashes), match basename.
    if (ng && !ng.includes('/') && fp.split('/').pop() === ng) return true;

    const gg = ng.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*');
    try {
      const re = new RegExp('^' + gg + '$');
      if (re.test(fp) || re.test(fp.replace(/^\.\/?/, ''))) return true;
    } catch {
      // ignore invalid patterns
    }

    // Also allow simple prefix exclusions.
    const pref = ng.replace(/\*.*$/, '');
    if (pref && (fp.startsWith(pref) || fp.replace(/^\.\/?/, '').startsWith(pref))) return true;
  }
  return false;
}

function walkFiles(root, exclude = []) {
  const out = [];
  const st = fs.statSync(root);
  if (st.isFile()) return isExcluded(root, exclude) ? [] : [root];
  if (!st.isDirectory()) return out;

  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    if (isExcluded(dir, exclude)) continue;
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      if (shouldSkipDir(e.name)) continue;
      const p = path.join(dir, e.name);
      if (isExcluded(p, exclude)) continue;
      if (e.isDirectory()) stack.push(p);
      else if (e.isFile()) out.push(p);
    }
  }
  return out;
}

function safeSnippet(line, re) {
  // Redact matched segment to avoid leaking secrets.
  try {
    return line.replace(re, (m) => '*'.repeat(Math.min(12, m.length)));
  } catch {
    return '[redacted]';
  }
}

function scanTextLines({ filePath, content, patterns, maxHits = 20 }) {
  const hits = [];
  const lines = content.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const re of patterns) {
      if (re.test(line)) {
        hits.push({ file: filePath, line: i + 1, pattern: String(re), excerpt: safeSnippet(line, re).slice(0, 240) });
        if (hits.length >= maxHits) return hits;
      }
    }
  }
  return hits;
}

function extractUrlsFromText(content, max = 50) {
  const urls = [];
  const re = /https?:\/\/[^\s)\]}>"']+/gi;
  const matches = String(content || '').match(re) || [];
  for (const m of matches) {
    let u = m.trim();
    // strip trailing punctuation
    u = u.replace(/[\.,;:!\?]+$/g, '');
    if (!urls.includes(u)) urls.push(u);
    if (urls.length >= max) break;
  }
  return urls;
}

function urlWarnings(url) {
  const u = String(url || '');
  const warnings = [];
  const shorteners = [
    't.co', 'bit.ly', 'tinyurl.com', 'goo.gl', 'is.gd', 'ow.ly', 'buff.ly', 'rebrand.ly', 'linktr.ee'
  ];
  try {
    const h = new URL(u).hostname.toLowerCase();
    if (shorteners.includes(h)) warnings.push('SHORTLINK');
    if (h.includes('hooks.') || u.includes('/webhook')) warnings.push('WEBHOOK_LIKE');
  } catch {
    // ignore parse errors
  }
  if (/\butm_[a-z_]+=/.test(u) || /[\?&](ref|aff|affiliate|invite|code)=/i.test(u)) warnings.push('TRACKING_OR_REFERRAL');
  return warnings;
}

function scanUrls({ filePath, content, maxHits = 30 }) {
  const hits = [];
  const urls = extractUrlsFromText(content, 80);
  for (const url of urls) {
    const ws = urlWarnings(url);
    if (!ws.length) continue;
    hits.push({ file: filePath, line: 0, pattern: ws.join(','), excerpt: url.slice(0, 240) });
    if (hits.length >= maxHits) break;
  }
  return hits;
}

function scanUnifiedDiffUrls(diffText, exclude = [], maxHits = 30) {
  const hits = [];
  let curFile = '<diff>';
  const lines = String(diffText || '').split(/\r?\n/);
  for (const line of lines) {
    if (line.startsWith('+++ ')) {
      const m = line.match(/^\+\+\+\s+b\/(.*)$/);
      if (m && m[1]) curFile = m[1];
      continue;
    }
    if (isExcluded(curFile, exclude)) continue;
    if (!line.startsWith('+')) continue;
    if (line.startsWith('+++')) continue;
    const content = line.slice(1);
    const uh = scanUrls({ filePath: curFile, content, maxHits: 5 });
    for (const h of uh) {
      hits.push(h);
      if (hits.length >= maxHits) return hits;
    }
  }
  return hits;
}

function scanFiles({ roots, patterns, exclude = [] }) {
  const hits = [];
  const files = roots.flatMap(r => walkFiles(r, exclude));
  for (const f of files) {
    let buf;
    try {
      buf = fs.readFileSync(f);
    } catch {
      continue;
    }
    if (buf.length > 1024 * 1024) continue;
    if (buf.includes(0)) continue;
    const txt = buf.toString('utf8');
    hits.push(...scanTextLines({ filePath: f, content: txt, patterns }));
    if (hits.length >= 50) break;
  }
  return hits.slice(0, 50);
}

function scanFilesForUrls({ roots, exclude = [] }) {
  const hits = [];
  const files = roots.flatMap(r => walkFiles(r, exclude));
  for (const f of files) {
    let buf;
    try {
      buf = fs.readFileSync(f);
    } catch {
      continue;
    }
    if (buf.length > 1024 * 1024) continue;
    if (buf.includes(0)) continue;
    const txt = buf.toString('utf8');
    const uh = scanUrls({ filePath: f, content: txt, maxHits: 10 });
    for (const h of uh) hits.push(h);
    if (hits.length >= 40) break;
  }
  return hits.slice(0, 40);
}

function gitRoot() {
  const r = spawnSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' });
  if (r.status !== 0) return null;
  return (r.stdout || '').trim() || null;
}

function isInsideGitRepo() {
  const r = spawnSync('git', ['rev-parse', '--is-inside-work-tree'], { encoding: 'utf8' });
  return r.status === 0 && String(r.stdout || '').trim() === 'true';
}

function gitDiffText(mode) {
  // Returns unified diff text. Empty string if not available.
  const m = mode || 'staged';
  let args;
  if (m === 'staged') args = ['diff', '--cached', '-U0'];
  else if (m === 'head') args = ['diff', 'HEAD', '-U0'];
  else if (m === 'worktree') args = ['diff', '-U0'];
  else return '';

  const r = spawnSync('git', args, { encoding: 'utf8' });
  if (r.status !== 0) return '';
  return r.stdout || '';
}

function gitChangedFilesFromDiff(diffText) {
  const files = new Set();
  const lines = String(diffText || '').split(/\r?\n/);
  for (const line of lines) {
    if (line.startsWith('+++ ')) {
      const m = line.match(/^\+\+\+\s+b\/(.*)$/);
      if (m && m[1] && m[1] !== '/dev/null') files.add(m[1]);
    }
  }
  return Array.from(files);
}

function scanUnifiedDiff(diffText, patterns, id, severity, exclude = []) {
  // Very lightweight: track current file from +++ b/<file>, then scan added lines.
  const hits = [];
  let curFile = '<diff>';
  const lines = String(diffText || '').split(/\r?\n/);
  for (const line of lines) {
    if (line.startsWith('+++ ')) {
      const m = line.match(/^\+\+\+\s+b\/(.*)$/);
      if (m && m[1]) curFile = m[1];
      continue;
    }
    if (isExcluded(curFile, exclude)) continue;
    if (!line.startsWith('+')) continue;
    if (line.startsWith('+++')) continue;
    const content = line.slice(1);
    for (const re of patterns) {
      if (re.test(content)) {
        hits.push({ id, severity, file: curFile, line: 0, pattern: String(re), excerpt: safeSnippet(content, re).slice(0, 240) });
        if (hits.length >= 30) return hits;
      }
    }
  }
  return hits;
}

function checkAllowlist() {
  const inside = isInsideGitRepo();
  if (!inside) return { inside: false, root: null, exists: null, path: null, lines: [] };
  const root = gitRoot() || process.cwd();
  const p = path.join(root, '.aoi-allowlist');
  const exists = fs.existsSync(p);
  const lines = exists ? fs.readFileSync(p, 'utf8').split(/\r?\n/).map(l => l.trim()).filter(Boolean) : [];
  return { inside: true, root, exists, path: p, lines };
}

function compileAllowlistMatchers(allowLines) {
  // Allowlist entries are treated as path prefixes or directory globs.
  // Examples:
  // - scripts/
  // - docs/
  // - README.md
  const matchers = [];
  for (let raw of (allowLines || [])) {
    raw = String(raw).trim();
    if (!raw || raw.startsWith('#')) continue;
    const pat = normalizePath(raw);
    // directory prefix
    if (pat.endsWith('/')) {
      matchers.push((fp) => normalizePath(fp).startsWith(pat));
      continue;
    }
    // simple glob support
    const gg = pat.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*');
    try {
      const re = new RegExp('^' + gg + '$');
      matchers.push((fp) => re.test(normalizePath(fp)) || re.test(normalizePath(fp).replace(/^\.\/?/, '')));
    } catch {
      matchers.push((fp) => normalizePath(fp) === pat || normalizePath(fp).endsWith('/' + pat));
    }
  }
  return matchers;
}

function isPathAllowed(filePath, matchers) {
  const fp = normalizePath(filePath).replace(/^\.\/?/, '');
  for (const m of matchers) {
    try {
      if (m(fp)) return true;
    } catch {
      // ignore
    }
  }
  return false;
}

function gradeFromFindings(findings) {
  if (findings.some(f => f.severity === 'block')) return 'BLOCK';
  if (findings.some(f => f.severity === 'warn')) return 'WARN';
  return 'PASS';
}

function isSensitivePath(p) {
  const s = String(p || '');
  return (
    s.includes('/Users/') ||
    s.includes('~/.config/') ||
    s.includes('.config/') ||
    s.includes('/opt/') ||
    s.includes('the-alpha-oracle/vault') ||
    s.includes('/vault/')
  );
}

function sha256Hex(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

async function buildIntegrityManifest({ rootDir, exclude = [] }) {
  // Always exclude the manifest itself (prevents "unexpected" self mismatch).
  const ex = [...(exclude || []), 'integrity_manifest.json'];
  const files = walkFiles(rootDir, ex)
    .map(f => normalizePath(path.relative(rootDir, f)))
    .filter(rel => rel && !rel.startsWith('..'));

  files.sort();
  const entries = [];
  for (const rel of files) {
    const abs = path.join(rootDir, rel);
    let buf;
    try {
      buf = fs.readFileSync(abs);
    } catch {
      continue;
    }
    // skip huge/binary-ish
    if (buf.length > 2 * 1024 * 1024) continue;
    const hash = await sha256Hex(buf);
    entries.push({ path: rel, sha256: hash, bytes: buf.length });
  }

  return {
    version: VERSION,
    created_at: new Date().toISOString(),
    root: '.',
    entries,
  };
}

async function integrityInit({ outPath, exclude = [] }) {
  const rootDir = process.cwd();
  const ex = [...(exclude || []), outPath];
  const manifest = await buildIntegrityManifest({ rootDir, exclude: ex });
  fs.writeFileSync(outPath, JSON.stringify(manifest, null, 2) + '\n', 'utf8');
  return manifest;
}

async function integrityCheck({ manifestPath, exclude = [] }) {
  const rootDir = process.cwd();
  if (!fs.existsSync(manifestPath)) {
    return { ok: false, error: 'manifest_not_found' };
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const ex = [...(exclude || []), manifestPath];
  const cur = await buildIntegrityManifest({ rootDir, exclude: ex });

  const want = new Map((manifest.entries || []).map(e => [e.path, e.sha256]));
  const got = new Map((cur.entries || []).map(e => [e.path, e.sha256]));

  const mismatches = [];
  for (const [p, h] of want.entries()) {
    if (!got.has(p)) mismatches.push({ path: p, reason: 'missing' });
    else if (got.get(p) !== h) mismatches.push({ path: p, reason: 'hash_mismatch' });
  }
  for (const [p] of got.entries()) {
    if (!want.has(p)) mismatches.push({ path: p, reason: 'unexpected' });
  }

  return { ok: mismatches.length === 0, mismatches, manifestPath };
}

async function main() {
  const { cmd, args } = parseArgs(process.argv.slice(2));
  const lang = args.lang || 'en';

  if (args.help || cmd === 'help') {
    process.stdout.write(t(lang, 'usage'));
    process.exit(0);
  }

  // integrity commands (local-only)
  if (cmd === 'integrity') {
    const action = (args.positional[0] || '').toLowerCase();
    const outPath = args.out || 'integrity_manifest.json';
    // default exclude: nothing (we are already inside the skill folder when using this)
    const exclude = args.exclude || [];

    if (action === 'init') {
      const manifest = await integrityInit({ outPath, exclude });
      if (args.format === 'json') process.stdout.write(JSON.stringify({ ok: true, out: outPath, manifest }, null, 2) + '\n');
      else process.stdout.write(`PASS: integrity manifest written: ${outPath}\n`);
      process.exit(0);
    }

    if (action === 'check') {
      const res = await integrityCheck({ manifestPath: outPath, exclude });
      if (res.error === 'manifest_not_found') {
        if (args.format === 'json') process.stdout.write(JSON.stringify({ ok: false, error: res.error }, null, 2) + '\n');
        else process.stdout.write(`WARN: integrity manifest not found: ${outPath}\n`);
        process.exit(1);
      }
      if (!res.ok) {
        if (args.format === 'json') process.stdout.write(JSON.stringify(res, null, 2) + '\n');
        else {
          process.stdout.write(`BLOCK: integrity mismatch (${res.mismatches.length})\n`);
          for (const m of res.mismatches.slice(0, 10)) process.stdout.write(`- ${m.path} (${m.reason})\n`);
        }
        process.exit(2);
      }
      if (args.format === 'json') process.stdout.write(JSON.stringify(res, null, 2) + '\n');
      else process.stdout.write(`PASS: integrity OK (${outPath})\n`);
      process.exit(0);
    }

    process.stdout.write(t(lang, 'usage'));
    process.exit(1);
  }

  // release-check is a strict mode: require integrity manifest + run repo check.
  let runCmd = cmd;
  if (cmd === 'release-check') {
    runCmd = 'check';
    args.integrityRequired = true;
    args.preset = args.preset || 'repo';
    args.diff = args.diff || 'staged';
  }

  const preset = args.preset || 'workspace';
  // Default exclude: this skill folder itself (prevents self false-positives)
  const defaultExclude = ['skills/aoi-openclaw-security-toolkit-core/**'];
  const exclude = [...defaultExclude, ...(args.exclude || [])];

  const roots = (args.paths.length ? args.paths : defaultPaths(preset)).filter(p => fs.existsSync(p));
  args.exclude = exclude;
  const secretPatterns = compilePatterns('./rules/secret_patterns.txt');
  const egressPatterns = compilePatterns('./rules/egress_patterns.txt');
  const promptPatterns = compilePatterns('./rules/prompt_injection_patterns.txt');

  const findings = [];

  if (runCmd === 'scan-secrets' || runCmd === 'check') {
    if (args.diff && isInsideGitRepo()) {
      const diffText = gitDiffText(args.diff);
      const hits = scanUnifiedDiff(diffText, secretPatterns, 'SECRET_PATTERN', 'block', args.exclude);
      findings.push(...hits);
    } else {
      const hits = scanFiles({ roots, patterns: secretPatterns, exclude: args.exclude });
      for (const h of hits) findings.push({ id: 'SECRET_PATTERN', severity: 'block', ...h });
    }
  }

  if (runCmd === 'scan-egress' || runCmd === 'check') {
    let hits = [];
    if (args.diff && isInsideGitRepo()) {
      const diffText = gitDiffText(args.diff);
      hits = scanUnifiedDiff(diffText, egressPatterns, 'EGRESS_PATTERN', 'warn', args.exclude);
    } else {
      hits = scanFiles({ roots, patterns: egressPatterns, exclude: args.exclude }).map(h => ({ id: 'EGRESS_PATTERN', severity: 'warn', ...h }));
    }

    // Upgrade to BLOCK if the egress indicator is in a sensitive path.
    for (const h of hits) {
      const sev = isSensitivePath(h.file) ? 'block' : (h.severity || 'warn');
      findings.push({ ...h, severity: sev, id: h.id || 'EGRESS_PATTERN' });
    }
  }

  if (runCmd === 'scan-prompt') {
    let text = '';
    if (args.file) text = fs.readFileSync(args.file, 'utf8');
    else if (args.text) text = args.text;
    else if (args.stdin) text = fs.readFileSync(0, 'utf8');
    else die('scan-prompt requires --file, --text, or --stdin', 2);

    const hits = scanTextLines({ filePath: args.file || '<input>', content: text, patterns: promptPatterns, maxHits: 30 });
    for (const h of hits) findings.push({ id: 'PROMPT_INJECTION_PATTERN', severity: 'warn', ...h });

    const urlHits = scanUrls({ filePath: args.file || '<input>', content: text, maxHits: 30 });
    for (const h of urlHits) findings.push({ id: 'URL_SUSPICIOUS', severity: 'warn', ...h });
  } else if (runCmd === 'check') {
    // URL suspicious scan:
    // - preset=repo: scan diff added lines only (faster/less noisy)
    // - preset=workspace: scan files
    if (preset === 'repo' && isInsideGitRepo()) {
      const diffMode = args.diff || 'staged';
      const diffText = gitDiffText(diffMode);
      const urlHits = scanUnifiedDiffUrls(diffText, args.exclude, 30);
      for (const h of urlHits) findings.push({ id: 'URL_SUSPICIOUS', severity: 'warn', ...h });
    } else {
      const urlHits = scanFilesForUrls({ roots, exclude: args.exclude });
      for (const h of urlHits) findings.push({ id: 'URL_SUSPICIOUS', severity: 'warn', ...h });
    }
  }

  if (runCmd === 'check') {
    const al = checkAllowlist();
    if (al.inside && !al.exists) {
      findings.push({
        id: 'ALLOWLIST_MISSING',
        severity: 'block',
        file: al.path,
        line: 0,
        pattern: '.aoi-allowlist',
        excerpt: `Missing .aoi-allowlist at repo root: ${al.root}`
      });
    } else if (al.inside && al.exists) {
      // Enforce allowlist against changed files (default: staged) to prevent accidental leakage.
      const diffMode = args.diff || 'staged';
      const diffText = gitDiffText(diffMode);
      const changed = gitChangedFilesFromDiff(diffText).filter(f => !isExcluded(f, args.exclude));
      const matchers = compileAllowlistMatchers(al.lines);
      const violations = changed.filter(f => !isPathAllowed(f, matchers));

      for (const f of violations.slice(0, 30)) {
        findings.push({
          id: 'ALLOWLIST_VIOLATION',
          severity: 'block',
          file: f,
          line: 0,
          pattern: '.aoi-allowlist',
          excerpt: `Changed file not allowed by .aoi-allowlist (${diffMode})`
        });
      }
    } else if (!al.inside) {
      findings.push({
        id: 'NOT_A_GIT_REPO',
        severity: 'warn',
        file: '.',
        line: 0,
        pattern: 'git',
        excerpt: 'Not inside a git repository; repo-only checks skipped.'
      });
    }
  }

  // Integrity: optional (warn if missing), but required for release-check.
  const integrityPath = 'integrity_manifest.json';
  if (args.integrityRequired || fs.existsSync(integrityPath)) {
    const res = await integrityCheck({ manifestPath: integrityPath, exclude: args.exclude || [] });
    if (res.error === 'manifest_not_found') {
      findings.push({ id: 'INTEGRITY_MANIFEST_MISSING', severity: args.integrityRequired ? 'block' : 'warn', file: integrityPath, line: 0, pattern: 'sha256', excerpt: 'Integrity manifest not found.' });
    } else if (!res.ok) {
      findings.push({ id: 'INTEGRITY_MISMATCH', severity: 'block', file: integrityPath, line: 0, pattern: 'sha256', excerpt: `Integrity mismatch (${res.mismatches.length})` });
    }
  }

  const grade = gradeFromFindings(findings);
  const exitCode = grade === 'PASS' ? 0 : grade === 'WARN' ? 1 : 2;

  const out = {
    grade,
    scanned_paths: roots,
    findings: findings.slice(0, 50),
  };

  if (args.out) {
    const lines = [];
    lines.push(`# openclaw-sec report`);
    lines.push('');
    lines.push(`- Grade: **${grade}**`);
    lines.push(`- Preset: ${preset}`);
    if (args.diff) lines.push(`- Diff: ${args.diff}`);
    lines.push(`- Scanned paths: ${roots.join(', ')}`);
    lines.push('');
    lines.push(`## Findings (${out.findings.length})`);
    lines.push('');
    for (const f of out.findings) {
      // No excerpts in report to avoid leaking sensitive content.
      lines.push(`- [${f.severity}] ${f.id} — ${f.file}${f.line ? `:${f.line}` : ''}`);
    }
    lines.push('');
    fs.writeFileSync(args.out, lines.join('\n') + '\n', 'utf8');
  }

  if (args.format === 'json') {
    process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  } else {
    process.stdout.write(`${t(lang, grade.toLowerCase())}: ${grade}\n`);
    if (!findings.length) {
      process.stdout.write('No findings.\n');
    } else {
      process.stdout.write(`Findings (${out.findings.length}):\n`);
      for (const f of out.findings.slice(0, 10)) {
        process.stdout.write(`- [${f.severity}] ${f.id} :: ${f.file}:${f.line}\n`);
      }
      if (out.findings.length > 10) process.stdout.write(`… +${out.findings.length - 10} more\n`);
    }
    if (args.out) process.stdout.write(`Report written: ${args.out}\n`);
  }

  process.exit(exitCode);
}

main().catch((e) => {
  console.error(e?.stack || String(e));
  process.exit(2);
});
