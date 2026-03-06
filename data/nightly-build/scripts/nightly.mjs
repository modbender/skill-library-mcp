#!/usr/bin/env node

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

// --- CONFIG ---
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE_DIR = process.env.WORKSPACE_DIR || path.resolve(__dirname, '../../..');
const SKILLS_DIR = path.join(WORKSPACE_DIR, 'skills');
const MEMORY_DIR = path.join(WORKSPACE_DIR, 'memory');
const REPORT_FILE = path.join(MEMORY_DIR, 'nightly-report.md');

// --- HELPERS ---
function log(msg) {
  const ts = new Date().toISOString();
  console.error(`[${ts}] ${msg}`);
}

function run(cmd, cwd = WORKSPACE_DIR) {
  try {
    return execSync(cmd, { cwd, encoding: 'utf-8', timeout: 60000 }).trim();
  } catch (err) {
    return `ERROR: ${err.message?.split('\n')[0] || 'unknown'}`;
  }
}

// --- TASKS ---

function taskSystemLoad() {
  let r = '### ⚡ System Status\n\n';
  const uptime = run('uptime');
  r += `- Uptime: \`${uptime}\`\n`;
  const mem = run("vm_stat | head -5 | tail -3");
  if (mem && !mem.startsWith('ERROR')) r += `- Memory:\n\`\`\`\n${mem}\n\`\`\`\n`;
  return r;
}

function taskDiskUsage() {
  let r = '### 💾 Disk Usage\n\n';
  const df = run('df -h / | tail -1');
  const parts = df.split(/\s+/);
  if (parts.length >= 5) {
    r += `- Total: ${parts[1]} | Used: ${parts[2]} (${parts[4]}) | Free: ${parts[3]}\n`;
    const pct = parseInt(parts[4]);
    if (pct > 90) r += `- ⚠️ **Disk usage above 90%!**\n`;
    else r += `- ✅ Disk healthy\n`;
  } else {
    r += `\`${df}\`\n`;
  }
  return r;
}

function taskSkillAudit() {
  let r = '### 📦 Skill Inventory\n\n';
  if (!fs.existsSync(SKILLS_DIR)) return r + 'No skills directory found.\n';

  const skills = fs.readdirSync(SKILLS_DIR).filter(s =>
    fs.statSync(path.join(SKILLS_DIR, s)).isDirectory()
  );

  r += `Found **${skills.length}** skills:\n`;
  for (const s of skills) {
    const hasSkillMd = fs.existsSync(path.join(SKILLS_DIR, s, 'SKILL.md'));
    const hasPkg = fs.existsSync(path.join(SKILLS_DIR, s, 'package.json'));
    const icon = hasSkillMd ? '✅' : '⚠️';
    const extra = hasPkg ? ' (npm)' : '';
    r += `- ${icon} \`${s}\`${extra}\n`;
  }
  return r;
}

function taskGitStatus() {
  let r = '### 🔄 Git Status\n\n';
  const status = run('git status --porcelain');
  if (!status || status.startsWith('ERROR')) {
    r += 'Not a git repo or git not available.\n';
    return r;
  }
  const lines = status.split('\n').filter(Boolean);
  if (lines.length === 0) {
    r += '- ✅ Working tree clean\n';
  } else {
    r += `- 📝 ${lines.length} uncommitted change(s)\n`;
    // Show up to 10
    for (const l of lines.slice(0, 10)) r += `  - \`${l.trim()}\`\n`;
    if (lines.length > 10) r += `  - ... and ${lines.length - 10} more\n`;
  }
  return r;
}

function taskLogCleanup() {
  let r = '### 🧹 Cleanup\n\n';
  let cleaned = 0;

  // Clean old log files (> 7 days)
  const memDir = MEMORY_DIR;
  if (fs.existsSync(memDir)) {
    const now = Date.now();
    const files = fs.readdirSync(memDir);
    for (const f of files) {
      if (f.endsWith('.log')) {
        const fp = path.join(memDir, f);
        const stat = fs.statSync(fp);
        const ageDays = (now - stat.mtimeMs) / 86400000;
        if (ageDays > 7) {
          r += `- 🗑️ Removed old log: \`${f}\` (${Math.floor(ageDays)}d old)\n`;
          fs.unlinkSync(fp);
          cleaned++;
        }
      }
    }
  }

  if (cleaned === 0) r += '- ✅ Nothing to clean\n';
  return r;
}

function taskMemorySize() {
  let r = '### 🧠 Memory Stats\n\n';
  if (!fs.existsSync(MEMORY_DIR)) return r + 'No memory directory.\n';

  const files = fs.readdirSync(MEMORY_DIR);
  let totalSize = 0;
  let mdCount = 0;

  for (const f of files) {
    const fp = path.join(MEMORY_DIR, f);
    const stat = fs.statSync(fp);
    totalSize += stat.size;
    if (f.endsWith('.md')) mdCount++;
  }

  r += `- ${mdCount} memory files, ${files.length} total\n`;
  r += `- Total size: ${(totalSize / 1024).toFixed(1)} KB\n`;

  // Check MEMORY.md size
  const memMd = path.join(WORKSPACE_DIR, 'MEMORY.md');
  if (fs.existsSync(memMd)) {
    const sz = fs.statSync(memMd).size;
    r += `- MEMORY.md: ${(sz / 1024).toFixed(1)} KB`;
    if (sz > 10240) r += ` ⚠️ (getting large, consider pruning)`;
    r += '\n';
  }

  return r;
}

// --- MAIN ---
function main() {
  log('🌙 Nightly Build starting...');

  if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });

  const now = new Date();
  const dateStr = now.toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai' });
  const timeStr = now.toLocaleTimeString('zh-CN', { timeZone: 'Asia/Shanghai' });

  let report = `# 🌙 Nightly Build Report\n**${dateStr} ${timeStr}**\n\n`;

  report += taskSystemLoad() + '\n';
  report += taskDiskUsage() + '\n';
  report += taskSkillAudit() + '\n';
  report += taskGitStatus() + '\n';
  report += taskLogCleanup() + '\n';
  report += taskMemorySize() + '\n';

  report += '---\n*Generated by `nightly-build` skill* 🦞\n';

  fs.writeFileSync(REPORT_FILE, report);
  log(`Report saved to ${REPORT_FILE}`);

  // Output to stdout (agent reads this)
  console.log(report);
}

main();
