// ── Memory Routes: /api/memory ──

import { Router } from 'express';
import { readFile, readdir, access } from 'fs/promises';
import os from 'os';
import path from 'path';

const router = Router();
const MEMORY_DIR = path.join(os.homedir(), '.openclaw', 'workspace', 'memory');
const MEMORY_FILE = path.join(os.homedir(), '.openclaw', 'workspace', 'MEMORY.md');

router.get('/memory', async (req, res) => {
  const limit = parseInt(req.query.limit) || 7;
  const offset = parseInt(req.query.offset) || 0;

  try {
    let entries = [];
    try {
      const files = await readdir(MEMORY_DIR);
      entries = files.filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f)).sort((a, b) => b.localeCompare(a));
    } catch {}

    let totalFiles = entries.length;
    try { await access(MEMORY_FILE); totalFiles++; } catch {}

    const sliced = entries.slice(offset, offset + limit);
    const hasMore = (offset + limit) < entries.length;

    const now = new Date();
    const todayStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });
    const yesterdayStr = new Date(now.getTime() - 86400000).toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });
    const currentYear = todayStr.slice(0, 4);

    const days = [];
    for (const filename of sliced) {
      const date = filename.replace('.md', '');
      let topics = [];
      try {
        const content = await readFile(path.join(MEMORY_DIR, filename), 'utf-8');
        for (const line of content.split('\n')) {
          const match = line.match(/^## (.+)/);
          if (match) {
            topics.push(match[1].trim().replace(/^JARVIS UI\s*[—–-]\s*/, ''));
          }
        }
      } catch {}

      let label = '';
      if (date === todayStr) label = 'TODAY';
      else if (date === yesterdayStr) label = 'YESTERDAY';

      const year = date.slice(0, 4);
      const displayDate = year === currentYear ? date.slice(5) : date;
      days.push({ date, displayDate, label, topics });
    }

    const lastUpdate = entries.length > 0 ? entries[0].replace('.md', '') : null;
    let lastUpdateDisplay = lastUpdate;
    if (lastUpdate === todayStr) lastUpdateDisplay = 'TODAY';
    else if (lastUpdate === yesterdayStr) lastUpdateDisplay = 'YESTERDAY';

    res.json({ days, totalFiles, lastUpdate: lastUpdateDisplay, hasMore });
  } catch (err) {
    console.error('[MEMORY] error:', err);
    res.status(500).json({ error: 'failed to read memory' });
  }
});

export default router;
