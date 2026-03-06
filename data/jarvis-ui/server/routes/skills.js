// ── Skills Routes: /api/skills ──

import { Router } from 'express';
import { readFile, readdir, access } from 'fs/promises';
import os from 'os';
import path from 'path';

const router = Router();

const SKILL_EMOJI = {
  whisper: '🎤', 'x-api': '🐦', gog: '📧', gmail: '📧', calendar: '📅',
  weather: '🌤️', nordvpn: '🔐', github: '🐙', gemini: '✨', imsg: '💬',
  healthcheck: '🛡️', 'azure-anthropic': '☁️', meditation: '🧘',
  'video-frames': '🎬', 'skill-creator': '🛠️', slack: '💼', discord: '🎮',
  spotify: '🎵', notion: '📝', obsidian: '📓', trello: '📋',
};

async function findGlobalSkillsDir() {
  const candidates = [
    '/opt/homebrew/lib/node_modules/openclaw/skills',
    '/usr/local/lib/node_modules/openclaw/skills',
    '/usr/lib/node_modules/openclaw/skills',
  ];
  for (const dir of candidates) {
    try { await access(dir); return dir; } catch {}
  }
  return null;
}

async function parseSkillMd(filePath) {
  try {
    const content = await readFile(filePath, 'utf8');
    const meta = {};
    const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (fmMatch) {
      for (const line of fmMatch[1].split('\n')) {
        const [key, ...rest] = line.split(':');
        if (key && rest.length) {
          let val = rest.join(':').trim();
          if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) val = val.slice(1, -1);
          meta[key.trim()] = val;
        }
      }
    }
    return meta;
  } catch { return {}; }
}

router.get('/skills', async (req, res) => {
  const skills = [];
  const seen = new Set();

  const userDir = path.join(os.homedir(), '.openclaw', 'workspace', 'skills');
  try {
    const entries = await readdir(userDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
      const meta = await parseSkillMd(path.join(userDir, entry.name, 'SKILL.md'));
      skills.push({
        name: meta.name || entry.name, slug: entry.name,
        description: meta.description || '', emoji: SKILL_EMOJI[entry.name] || '📦',
        source: 'workspace', path: path.join(userDir, entry.name),
      });
      seen.add(entry.name);
    }
  } catch {}

  const globalDir = await findGlobalSkillsDir();
  if (globalDir) {
    try {
      const entries = await readdir(globalDir, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isDirectory() || entry.name.startsWith('.') || seen.has(entry.name)) continue;
        const meta = await parseSkillMd(path.join(globalDir, entry.name, 'SKILL.md'));
        skills.push({
          name: meta.name || entry.name, slug: entry.name,
          description: meta.description || '', emoji: SKILL_EMOJI[entry.name] || '📦',
          source: 'global', path: path.join(globalDir, entry.name),
        });
      }
    } catch {}
  }

  skills.sort((a, b) => {
    if (a.source !== b.source) return a.source === 'workspace' ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
  res.json(skills);
});

export default router;
