// ── Schedule Routes: /api/schedule ──

import { Router } from 'express';
import { readFile } from 'fs/promises';
import { execFile } from 'child_process';
import os from 'os';
import path from 'path';
import { broadcastEvent } from '../sse.js';

const router = Router();
const OC_CONFIG = path.join(os.homedir(), '.openclaw', 'openclaw.json');

function ocCli(...args) {
  return new Promise((resolve, reject) => {
    execFile('openclaw', args, { timeout: 10000 }, (err, stdout) => {
      if (err) return reject(err);
      try {
        const jsonStart = stdout.search(/[\[{]/);
        if (jsonStart === -1) return resolve(null);
        resolve(JSON.parse(stdout.slice(jsonStart)));
      } catch (e) {
        reject(new Error(`JSON parse failed: ${e.message}`));
      }
    });
  });
}

router.get('/schedule', async (req, res) => {
  try {
    let heartbeat = { every: '30m', enabled: true };
    try {
      const ocConfig = JSON.parse(await readFile(OC_CONFIG, 'utf-8'));
      const hb = ocConfig?.agents?.defaults?.heartbeat;
      if (hb) {
        heartbeat = { every: hb.every || '30m', enabled: hb.every !== '0m' && hb.every !== '0', target: hb.target || 'last' };
      }
    } catch {}

    try {
      const hbPath = path.join(os.homedir(), '.openclaw', 'workspace', 'HEARTBEAT.md');
      heartbeat.content = await readFile(hbPath, 'utf-8');
    } catch {}

    try {
      const last = await ocCli('system', 'heartbeat', 'last', '--json');
      if (last?.ts) { heartbeat.lastRun = last.ts; heartbeat.lastStatus = last.status || null; }
    } catch {}

    let jobs = [];
    try {
      const data = await ocCli('cron', 'list', '--all', '--json');
      jobs = (data?.jobs || []).map(j => ({
        id: j.id, name: j.name || 'Unnamed', enabled: j.enabled !== false,
        schedule: j.schedule, lastRun: j.state?.lastRunAtMs || null,
        lastStatus: j.state?.lastStatus || null, nextRun: j.state?.nextRunAtMs || null,
      }));
    } catch (err) {
      console.error('[SCHEDULE] cron list error:', err.message);
    }

    res.json({ heartbeat, jobs });
  } catch (err) {
    console.error('[SCHEDULE] error:', err);
    res.status(500).json({ error: 'failed to read schedule' });
  }
});

router.patch('/schedule/:id', async (req, res) => {
  const { enabled } = req.body;
  if (typeof enabled !== 'boolean') return res.status(400).json({ error: 'enabled (boolean) required' });
  try {
    await ocCli('cron', enabled ? 'enable' : 'disable', req.params.id);
    broadcastEvent('schedule-update');
    res.json({ ok: true });
  } catch (err) {
    console.error('[SCHEDULE] toggle error:', err.message);
    res.status(500).json({ error: 'failed to toggle job' });
  }
});

export default router;
