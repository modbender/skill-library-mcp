#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      out[k] = v;
    }
  }
  return out;
}

function chunkText(s, maxChars) {
  const clean = s.split(/\r?\n/).filter(ln => ln.trim()).join('\n');
  if (clean.length <= maxChars) return [clean];
  const out = [];
  let i = 0;
  while (i < clean.length) {
    let j = Math.min(i + maxChars, clean.length);
    let cut = clean.lastIndexOf('\n', j);
    if (cut <= i) cut = clean.lastIndexOf('。', j);
    if (cut <= i) cut = j;
    out.push(clean.slice(i, cut).trim());
    i = cut;
  }
  return out.filter(Boolean);
}

function main() {
  const a = parseArgs(process.argv);
  const bookId = Number(a['book-id']);
  const title = String(a.title || '');
  const lang = String(a.lang || 'ja');
  const textPath = String(a['text-path'] || '');
  const outDir = String(a['out-dir'] || '');
  const maxChars = Number(a['max-chars'] || 20000);
  if (!bookId || !title || !textPath || !outDir) throw new Error('required: --book-id --title --text-path --out-dir');

  const text = fs.readFileSync(textPath, 'utf-8');
  const parts = chunkText(text, maxChars);
  fs.mkdirSync(outDir, { recursive: true });

  const sourceFiles = [];
  parts.forEach((part, idx) => {
    const p = path.join(outDir, `excerpt_part_${String(idx + 1).padStart(3, '0')}.txt`);
    fs.writeFileSync(p, part, 'utf-8');
    sourceFiles.push(p);
  });

  const payload = {
    book_id: bookId,
    title,
    lang,
    source_files: sourceFiles,
    notes: 'Read all source_files in order.',
  };
  const payloadPath = path.join(outDir, 'subagent_input.json');
  fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), 'utf-8');
  console.log(JSON.stringify({ ok: true, payload: payloadPath, parts: sourceFiles.length }));
}

try { main(); } catch (e) { console.error(String(e?.stack || e)); process.exit(1); }
