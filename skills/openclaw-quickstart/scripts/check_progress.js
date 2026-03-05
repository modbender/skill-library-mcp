#!/usr/bin/env node
/**
 * check_progress.js - OpenClaw Quickstart Task Progress Checker
 *
 * Detection priority:
 *   1. .quickstart-progress.json  (written by AI via mark_done.js — most accurate)
 *   2. File system scan           (objective evidence: SOUL.md, .pptx, etc.)
 *   3. memory/*.md keyword scan   (fallback for ephemeral tasks)
 *
 * Usage:
 *   node check_progress.js [--workspace /path/to/workspace] [--mark-done]
 *
 *   --mark-done  Auto-write newly detected completions back to progress.json
 *
 * Output (JSON):
 *   {
 *     "tasks": [{ "id": 1, "name": "...", "done": true/false, "source": "progress|scan|memory" }],
 *     "completed": 3, "total": 8, "all_done": false,
 *     "next_task": { "id": 4, "name": "..." }
 *   }
 */

const fs   = require('fs');
const path = require('path');

// ── Args ─────────────────────────────────────────────────────────────────────
const args      = process.argv.slice(2);
const wsIdx     = args.indexOf('--workspace');
const workspace = wsIdx !== -1 ? args[wsIdx + 1] : path.join(process.env.HOME, '.openclaw', 'workspace');
const markDone  = args.includes('--mark-done');

// ── Helpers ──────────────────────────────────────────────────────────────────
function readFile(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return ''; }
}
function exists(p) { return fs.existsSync(p); }

function globFiles(dir, ext) {
  if (!exists(dir)) return [];
  return fs.readdirSync(dir).filter(f => f.endsWith(ext)).map(f => path.join(dir, f));
}

function memoryContains(ws, ...keywords) {
  const memDir = path.join(ws, 'memory');
  if (!exists(memDir)) return false;
  for (const f of globFiles(memDir, '.md')) {
    const c = readFile(f).toLowerCase();
    if (keywords.some(k => c.includes(k.toLowerCase()))) return true;
  }
  return false;
}

function scanDirForPattern(dir, patterns) {
  if (!exists(dir)) return false;
  for (const f of fs.readdirSync(dir)) {
    const full = path.join(dir, f);
    const stat = fs.statSync(full);
    if (stat.isFile() && patterns.some(p => f.toLowerCase().includes(p))) return true;
    if (stat.isDirectory() && scanDirForPattern(full, patterns)) return true;
  }
  return false;
}

// ── Load progress.json ───────────────────────────────────────────────────────
const progressFile = path.join(workspace, '.quickstart-progress.json');
let savedProgress = {};
try {
  if (exists(progressFile)) savedProgress = JSON.parse(readFile(progressFile));
} catch {}

// ── File-system / memory checks (fallback) ───────────────────────────────────
function scanTask1() {
  for (const fname of ['SOUL.md', 'IDENTITY.md']) {
    const c = readFile(path.join(workspace, fname));
    if (c.length > 100 && (c.toLowerCase().includes('name') || c.includes('名字') || c.includes('identity')))
      return true;
  }
  return false;
}

function scanTask2() {
  const c = readFile(path.join(workspace, 'USER.md'));
  const match = c.match(/\*\*Name:\*\*\s*(.+)/);
  if (match && match[1].trim()) return true;
  return c.length > 200;
}

function scanTask3() {
  return memoryContains(workspace, 'weather', '天气', 'wttr');
}

function scanTask4() {
  if (scanDirForPattern(workspace, ['日报', '周报', 'report', 'daily', 'weekly'])) return true;
  return memoryContains(workspace, '日报', '周报', 'report');
}

function scanTask5() {
  const cronPaths = [
    path.join(process.env.HOME, '.openclaw', 'crons.json'),
    path.join(process.env.HOME, '.openclaw', 'config', 'crons.json'),
  ];
  for (const cp of cronPaths) {
    try {
      const d = JSON.parse(readFile(cp));
      if ((Array.isArray(d) ? d : Object.values(d)).length > 0) return true;
    } catch {}
  }
  return memoryContains(workspace, 'cron', '提醒', 'reminder', '定时');
}

function scanTask6() {
  return memoryContains(workspace, 'browser', '浏览器', 'screenshot', 'snapshot');
}

function scanTask7() {
  if (scanDirForPattern(workspace, ['.pptx', '.ppt'])) return true;
  return memoryContains(workspace, 'ppt', '幻灯片', 'presentation');
}

function scanTask8() {
  const skillDirs = [
    path.join(process.env.HOME, '.openclaw', 'skills'),
    path.join(process.env.HOME, '.openclaw', 'extensions'),
  ];
  const builtins = new Set(['feishu', 'skill-creator', 'clawhub', 'healthcheck', 'weather', 'video-frames']);
  for (const sd of skillDirs) {
    if (!exists(sd)) continue;
    const items = fs.readdirSync(sd).filter(f =>
      fs.statSync(path.join(sd, f)).isDirectory() && !builtins.has(f)
    );
    if (items.length > 0) return true;
  }
  return memoryContains(workspace, 'clawhub install', 'skill 安装', 'installed skill');
}

const SCAN_FNS = [null, scanTask1, scanTask2, scanTask3, scanTask4, scanTask5, scanTask6, scanTask7, scanTask8];

// ── Task Definitions ─────────────────────────────────────────────────────────
const TASKS = [
  { id: 1, name: '给 AI 取个名字',    name_en: 'Initialize AI Identity'  },
  { id: 2, name: '让 AI 记住你',      name_en: 'Save Your Preferences'   },
  { id: 3, name: '查今天天气',        name_en: 'Check the Weather'       },
  { id: 4, name: '写一篇日报',        name_en: 'Generate a Report'       },
  { id: 5, name: '建一个日历提醒',    name_en: 'Set a Reminder'          },
  { id: 6, name: '用浏览器收集信息',  name_en: 'Browser Info Gathering'  },
  { id: 7, name: '让 AI 做一张 PPT', name_en: 'Generate a PPT'          },
  { id: 8, name: '安装一个新 Skill',  name_en: 'Install a Skill'         },
];

// ── Main ─────────────────────────────────────────────────────────────────────
const newlyCompleted = [];

const tasks = TASKS.map(t => {
  const key = `task${t.id}`;

  // Priority 1: progress.json (written by AI via mark_done.js)
  if (savedProgress[key]?.done) {
    return { ...t, done: true, source: 'progress', completedAt: savedProgress[key].completedAt };
  }

  // Priority 2 & 3: file scan + memory
  let done = false;
  let source = null;
  try { done = SCAN_FNS[t.id](); source = done ? 'scan' : null; } catch {}

  // Auto-persist newly detected completions back to progress.json
  if (done && markDone) {
    savedProgress[key] = { done: true, completedAt: new Date().toISOString(), source: 'auto-scan' };
    newlyCompleted.push(t.id);
  }

  return { ...t, done, source };
});

// Write back if --mark-done and any new completions found
if (markDone && newlyCompleted.length > 0) {
  try {
    fs.writeFileSync(progressFile, JSON.stringify(savedProgress, null, 2), 'utf8');
  } catch (e) {
    process.stderr.write(`Warning: could not write progress.json: ${e.message}\n`);
  }
}

const completed  = tasks.filter(t => t.done).length;
const total      = tasks.length;
const all_done   = completed === total;
const next_task  = tasks.find(t => !t.done) || null;

console.log(JSON.stringify({
  tasks,
  completed,
  total,
  all_done,
  next_task,
  newly_completed: newlyCompleted,
  workspace,
}, null, 2));

// Signal for cron/heartbeat handler to run cleanup
if (all_done) {
  process.stderr.write('\nALL_TASKS_DONE\n');
}
