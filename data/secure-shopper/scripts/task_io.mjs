#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';

const WORKSPACE = '/home/miles/.openclaw/workspace';
const ART_DIR = path.join(WORKSPACE, 'artifacts', 'secure_shopping');

export function timestampId(d = new Date()) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

export async function writeNewTask({ userPrompt, sites = [], preferences = {} }) {
  if (!userPrompt || !String(userPrompt).trim()) throw new Error('userPrompt is required');
  await fs.mkdir(ART_DIR, { recursive: true });
  const id = timestampId();
  const file = path.join(ART_DIR, `${id}_shopping_task.json`);

  const payload = {
    schema: 'secure-shopper/v1',
    task: {
      id,
      userPrompt: String(userPrompt),
      startTime: new Date().toISOString(),
      endTime: null,
      preferences,
      sites,
      candidates: []
    }
  };

  await fs.writeFile(file, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  return { file, payload };
}

export async function finalizeTask(file, candidates) {
  const raw = JSON.parse(await fs.readFile(file, 'utf8'));
  raw.task.endTime = new Date().toISOString();
  raw.task.candidates = candidates;
  await fs.writeFile(file, JSON.stringify(raw, null, 2) + '\n', 'utf8');
  return raw;
}

export async function updateCandidateStatus(file, url, status) {
  const raw = JSON.parse(await fs.readFile(file, 'utf8'));
  const cand = raw.task.candidates?.find(c => c.url === url);
  if (!cand) throw new Error(`Candidate not found for url: ${url}`);
  cand.status = status;
  await fs.writeFile(file, JSON.stringify(raw, null, 2) + '\n', 'utf8');
  return raw;
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const cmd = process.argv[2];
  const arg = (name) => {
    const i = process.argv.indexOf(`--${name}`);
    return i === -1 ? null : process.argv[i + 1];
  };

  try {
    if (cmd === 'new') {
      const userPrompt = arg('prompt');
      const { file } = await writeNewTask({ userPrompt });
      console.log(file);
    } else if (cmd === 'status') {
      const file = arg('file');
      const url = arg('url');
      const status = arg('status');
      if (!file || !url || !status) throw new Error('Need --file --url --status');
      await updateCandidateStatus(file, url, status);
      console.log('OK');
    } else {
      console.error('Commands: new, status');
      process.exit(2);
    }
  } catch (e) {
    console.error(e?.stack || String(e));
    process.exit(1);
  }
}
