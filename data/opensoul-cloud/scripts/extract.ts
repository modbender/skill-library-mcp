#!/usr/bin/env npx ts-node
/**
 * Extract workspace files for OpenSoul sharing
 * Outputs structured JSON to stdout
 */

import * as fs from 'fs';
import * as path from 'path';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME!, '.openclaw/workspace');
const OPENCLAW_DIR = path.join(process.env.HOME!, '.openclaw');

// ============ HELPERS ============

function readFile(filepath: string): string | null {
  try { return fs.readFileSync(filepath, 'utf-8'); } catch { return null; }
}

function readJson(filepath: string): any {
  try { return JSON.parse(fs.readFileSync(filepath, 'utf-8')); } catch { return null; }
}

// ============ EXTRACTORS ============

function extractToolSummary(toolsContent: string | null) {
  if (!toolsContent) return null;
  
  const sections = (toolsContent.match(/^##\s+(.+)$/gm) || []).map(h => h.replace(/^##\s+/, ''));
  const toolNames = new Set<string>();
  
  const toolPatterns = ['apollo', 'email', 'calendar', 'granola', 'camera', 'ssh', 'tts', 'browser', 'slack', 'discord', 'telegram'];
  const lower = toolsContent.toLowerCase();
  for (const t of toolPatterns) {
    if (lower.includes(t)) toolNames.add(t);
  }
  
  return {
    sections,
    toolNames: [...toolNames],
    hasCustomScripts: fs.existsSync(path.join(WORKSPACE, 'scripts')),
    integrations: [],
  };
}

function extractSkills() {
  const skillsDir = path.join(WORKSPACE, 'skills');
  if (!fs.existsSync(skillsDir)) return [];
  
  return fs.readdirSync(skillsDir).map(name => {
    const realPath = fs.realpathSync(path.join(skillsDir, name));
    const skillMd = readFile(path.join(realPath, 'SKILL.md'));
    const descMatch = skillMd?.match(/^description:\s*(.+)$/m);
    return { name, description: descMatch?.[1] || 'No description' };
  }).filter(s => s.description);
}

function extractCronJobs() {
  const data = readJson(path.join(OPENCLAW_DIR, 'cron', 'jobs.json'));
  if (!data?.jobs) return [];
  
  return data.jobs.map((job: any) => {
    let schedule = '';
    if (job.schedule?.kind === 'cron') {
      schedule = `cron: ${job.schedule.expr}`;
      if (job.schedule.tz) schedule += ` (${job.schedule.tz})`;
    } else if (job.schedule?.kind === 'every') {
      schedule = `every ${Math.round(job.schedule.everyMs / 60000)} minutes`;
    }
    
    const description = job.payload?.message?.split(/[.\n]/)[0]?.slice(0, 100) || job.name || 'Unnamed';
    
    return { name: job.name || 'Unnamed', schedule, description, enabled: job.enabled !== false };
  });
}

function extractWorkspace() {
  const memoryDir = path.join(WORKSPACE, 'memory');
  const hasMemory = fs.existsSync(memoryDir);
  
  const standardFolders = ['memory', 'skills', 'imported', '.git', 'node_modules'];
  const standardFiles = ['SOUL.md', 'AGENTS.md', 'TOOLS.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md', 'HEARTBEAT.md', 'BOOTSTRAP.md', '.gitignore'];
  
  let customFolders: string[] = [];
  let customFiles: string[] = [];
  
  try {
    const entries = fs.readdirSync(WORKSPACE, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory() && !standardFolders.includes(entry.name) && !entry.name.startsWith('.')) {
        customFolders.push(entry.name);
      }
      if (entry.isFile() && !standardFiles.includes(entry.name) && !entry.name.startsWith('.')) {
        customFiles.push(entry.name);
      }
    }
  } catch {}
  
  return {
    hasMemoryFolder: hasMemory,
    memoryFileCount: hasMemory ? fs.readdirSync(memoryDir).filter(f => f.endsWith('.md')).length : 0,
    hasHeartbeat: fs.existsSync(path.join(WORKSPACE, 'HEARTBEAT.md')),
    customFolders: customFolders.slice(0, 10),
    customFiles: customFiles.slice(0, 10),
  };
}

// ============ MAIN ============

function main() {
  const toolsContent = readFile(path.join(WORKSPACE, 'TOOLS.md'));
  
  const extract = {
    soul: readFile(path.join(WORKSPACE, 'SOUL.md')),
    agents: readFile(path.join(WORKSPACE, 'AGENTS.md')),
    identity: readFile(path.join(WORKSPACE, 'IDENTITY.md')),
    memory: readFile(path.join(WORKSPACE, 'MEMORY.md')),
    heartbeat: readFile(path.join(WORKSPACE, 'HEARTBEAT.md')),
    tools: extractToolSummary(toolsContent),
    toolsRaw: toolsContent,
    cronJobs: extractCronJobs(),
    skills: extractSkills(),
    workspace: extractWorkspace(),
    meta: { extractedAt: new Date().toISOString(), version: '2.0.0' },
  };
  
  console.log(JSON.stringify(extract, null, 2));
}

main();
