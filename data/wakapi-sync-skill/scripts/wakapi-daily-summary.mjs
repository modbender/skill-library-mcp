#!/usr/bin/env node
/*
  Wakapi daily summary → CSV

  Env:
    WAKAPI_URL (required)
    WAKAPI_API_KEY (required)
    WAKAPI_OUT_DIR (required)
    WAKAPI_TOP_N_PROJECTS (default 10)
    WAKAPI_TOP_N_LANGUAGES (default 10)

  Data source:
    GET /api/v1/users/current/statusbar/today
    GET /api/v1/users/current/summaries?range=today (fallback for top projects/languages)
*/

import fs from 'node:fs/promises';
import path from 'node:path';

function getConfig() {
  const WAKAPI_URL = process.env.WAKAPI_URL;
  const WAKAPI_API_KEY = process.env.WAKAPI_API_KEY;
  const OUT_DIR = process.env.WAKAPI_OUT_DIR;
  const TOP_N_PROJECTS = Number(process.env.WAKAPI_TOP_N_PROJECTS || 10);
  const TOP_N_LANGUAGES = Number(process.env.WAKAPI_TOP_N_LANGUAGES || 10);

  if (!WAKAPI_URL || !WAKAPI_API_KEY || !OUT_DIR) {
    console.error('Missing required env vars: WAKAPI_URL, WAKAPI_API_KEY, WAKAPI_OUT_DIR');
    process.exit(2);
  }

  return { WAKAPI_URL, WAKAPI_API_KEY, OUT_DIR, TOP_N_PROJECTS, TOP_N_LANGUAGES };
}

function ymdLocal(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function b64(str) {
  return Buffer.from(str, 'utf8').toString('base64');
}

async function httpJson(url, apiKey) {
  const headers = {
    'Accept': 'application/json',
    'Authorization': `Basic ${b64(apiKey)}`,
  };

  const res = await fetch(url, { headers });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${res.statusText} for ${url}\n${text.slice(0, 500)}`);
  }
  return res.json();
}

function toHours(seconds) {
  return Math.round((seconds / 3600) * 100) / 100;
}

function csvEscape(value) {
  if (value === null || value === undefined) return '';
  const s = String(value);
  if (/[",\n\r]/.test(s)) return `"${s.replaceAll('"', '""')}"`;
  return s;
}

function rowsToCsv(header, rows) {
  const lines = [];
  lines.push(header.join(','));
  for (const r of rows) lines.push(r.map(csvEscape).join(','));
  return lines.join('\n') + '\n';
}

async function readCsv(file) {
  try {
    const content = await fs.readFile(file, 'utf8');
    return content;
  } catch (e) {
    if (e && e.code === 'ENOENT') return null;
    throw e;
  }
}

function parseCsvSimple(content) {
  // Very simple parser for our generated CSV (no embedded newlines expected).
  const lines = content.trim().split(/\r?\n/);
  const header = lines.shift().split(',');
  const rows = lines.filter(Boolean).map(line => {
    // handle quoted fields with commas
    const out = [];
    let cur = '';
    let inQ = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQ) {
        if (ch === '"') {
          if (line[i + 1] === '"') { cur += '"'; i++; }
          else inQ = false;
        } else cur += ch;
      } else {
        if (ch === ',') { out.push(cur); cur = ''; }
        else if (ch === '"') inQ = true;
        else cur += ch;
      }
    }
    out.push(cur);
    const obj = {};
    header.forEach((h, idx) => (obj[h] = out[idx] ?? ''));
    return obj;
  });
  return { header, rows };
}

async function upsertCsvByKeys(file, header, keyCols, newRows) {
  const existing = await readCsv(file);
  let rows = [];
  if (existing) {
    const parsed = parseCsvSimple(existing);
    // keep existing header, but ensure it matches expected
    // if mismatch, we regenerate from scratch with only newRows.
    const sameHeader = parsed.header.join(',') === header.join(',');
    if (sameHeader) rows = parsed.rows;
  }

  const key = (r) => keyCols.map(k => r[k]).join('||');
  const idx = new Map(rows.map(r => [key(r), r]));
  for (const nr of newRows) idx.set(key(nr), nr);

  const merged = Array.from(idx.values());
  // stable sort by date then rank if present
  merged.sort((a, b) => {
    if (a.date && b.date && a.date !== b.date) return a.date < b.date ? -1 : 1;
    if (a.rank && b.rank) return Number(a.rank) - Number(b.rank);
    return 0;
  });

  const csv = rowsToCsv(header, merged.map(r => header.map(h => r[h] ?? '')));
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, csv, 'utf8');
}

function pickTop(items, topN) {
  return (items || []).slice(0, topN);
}

function extractTopFromStatusbarToday(statusbar) {
  // Wakapi often returns: { data: { grand_total: { total_seconds }, projects:[{name,total_seconds,percent}], languages:[...] } }
  const data = statusbar?.data ?? statusbar;
  const grand = data?.grand_total ?? data?.grandTotal ?? data?.grand_total;
  const totalSeconds = grand?.total_seconds ?? grand?.totalSeconds;

  const projects = (data?.projects || []).map(p => ({
    name: p.name ?? p.project ?? p.key,
    seconds: p.total_seconds ?? p.totalSeconds ?? p.seconds,
    percent: p.percent,
  }));

  const languages = (data?.languages || []).map(l => ({
    name: l.name ?? l.language ?? l.key,
    seconds: l.total_seconds ?? l.totalSeconds ?? l.seconds,
    percent: l.percent,
  }));

  return { totalSeconds, projects, languages };
}

function extractFromSummariesToday(summaries) {
  // WakaTime-like: { data: [ { grand_total: { total_seconds }, projects:[{name,total_seconds,percent}], languages:[...] } ] }
  const first = summaries?.data?.[0] ?? summaries?.data ?? summaries?.[0];
  const grand = first?.grand_total ?? first?.grandTotal;
  const totalSeconds = grand?.total_seconds ?? grand?.totalSeconds;

  const projects = (first?.projects || []).map(p => ({
    name: p.name,
    seconds: p.total_seconds,
    percent: p.percent,
  }));
  const languages = (first?.languages || []).map(l => ({
    name: l.name,
    seconds: l.total_seconds,
    percent: l.percent,
  }));

  return { totalSeconds, projects, languages };
}

async function main() {
  const { WAKAPI_URL, WAKAPI_API_KEY, OUT_DIR, TOP_N_PROJECTS, TOP_N_LANGUAGES } = getConfig();
  const date = ymdLocal();

  const base = WAKAPI_URL.replace(/\/$/, '');
  const statusbarUrl = `${base}/api/v1/users/current/statusbar/today`;
  const summariesUrl = `${base}/api/v1/users/current/summaries?range=today`;

  let statusbar;
  try {
    statusbar = await httpJson(statusbarUrl, WAKAPI_API_KEY);
  } catch (e) {
    console.error(`[wakapi-sync] Failed statusbar/today: ${e.message}`);
    throw e;
  }

  let { totalSeconds, projects, languages } = extractTopFromStatusbarToday(statusbar);

  // If statusbar doesn't contain top lists, fallback to summaries.
  const needFallback = (!projects?.length && !languages?.length) || (totalSeconds == null);
  if (needFallback) {
    const summaries = await httpJson(summariesUrl, WAKAPI_API_KEY);
    const extracted = extractFromSummariesToday(summaries);
    totalSeconds = totalSeconds ?? extracted.totalSeconds;
    projects = projects?.length ? projects : extracted.projects;
    languages = languages?.length ? languages : extracted.languages;
  }

  if (typeof totalSeconds !== 'number') {
    // As last resort: try statusbar->data->grand_total->total_seconds is number-like
    const n = Number(totalSeconds);
    if (!Number.isFinite(n)) throw new Error(`Unable to determine total seconds for ${date}`);
    totalSeconds = n;
  }

  // Normalize seconds
  projects = (projects || []).map(p => ({ ...p, seconds: Number(p.seconds ?? 0) }));
  languages = (languages || []).map(l => ({ ...l, seconds: Number(l.seconds ?? 0) }));

  const totalHours = toHours(totalSeconds);
  const projectsTop = pickTop(projects.sort((a,b)=>b.seconds-a.seconds), TOP_N_PROJECTS);
  const languagesTop = pickTop(languages.sort((a,b)=>b.seconds-a.seconds), TOP_N_LANGUAGES);

  const totalHeader = ['date','total_seconds','total_hours','projects_count','languages_count'];
  const totalRows = [{
    date,
    total_seconds: String(totalSeconds),
    total_hours: String(totalHours),
    projects_count: String(projectsTop.length),
    languages_count: String(languagesTop.length),
  }];

  const projectsHeader = ['date','rank','project','seconds','hours','percent'];
  const projectRows = projectsTop.map((p, i) => ({
    date,
    rank: String(i + 1),
    project: p.name ?? '',
    seconds: String(p.seconds ?? 0),
    hours: String(toHours(p.seconds ?? 0)),
    percent: p.percent != null ? String(p.percent) : '',
  }));

  const languagesHeader = ['date','rank','language','seconds','hours','percent'];
  const languageRows = languagesTop.map((l, i) => ({
    date,
    rank: String(i + 1),
    language: l.name ?? '',
    seconds: String(l.seconds ?? 0),
    hours: String(toHours(l.seconds ?? 0)),
    percent: l.percent != null ? String(l.percent) : '',
  }));

  const totalFile = path.join(OUT_DIR, 'daily-total.csv');
  const projectsFile = path.join(OUT_DIR, 'daily-top-projects.csv');
  const languagesFile = path.join(OUT_DIR, 'daily-top-languages.csv');

  await upsertCsvByKeys(totalFile, totalHeader, ['date'], totalRows);
  await upsertCsvByKeys(projectsFile, projectsHeader, ['date','rank'], projectRows);
  await upsertCsvByKeys(languagesFile, languagesHeader, ['date','rank'], languageRows);

  console.log(`[wakapi-sync] Wrote ${date}: total=${totalHours}h, projects=${projectsTop.length}, languages=${languagesTop.length}`);
}

// Allow importing functions for testing without running main().
import { fileURLToPath } from 'node:url';
const __filename = fileURLToPath(import.meta.url);
if (process.argv[1] === __filename) {
  main().catch((e) => {
    console.error(e?.stack || String(e));
    process.exit(1);
  });
}

export {
  csvEscape,
  rowsToCsv,
  parseCsvSimple,
  upsertCsvByKeys,
  extractTopFromStatusbarToday,
  extractFromSummariesToday,
  toHours,
  ymdLocal,
  pickTop,
};
