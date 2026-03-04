#!/usr/bin/env node
/**
 * wreckit dashboard server
 * Serves the dashboard UI and provides a /api/status endpoint
 * that aggregates .wreckit/dashboard.json from all watched project paths.
 *
 * Usage:
 *   node server.mjs [--port 3939] [--projects ~/Projects/repo1,~/Projects/repo2]
 *   node server.mjs --watch ~/Projects  (auto-discover all subdirs with .wreckit/)
 */

import { createServer } from 'node:http';
import { readFile, readdir, stat } from 'node:fs/promises';
import { join, resolve, basename } from 'node:path';
import { existsSync } from 'node:fs';

const args = process.argv.slice(2);
const PORT = parseInt(getArg('--port', '3939'));
const projectsArg = getArg('--projects', '');
const watchDir = getArg('--watch', '');

function getArg(name, fallback) {
  const idx = args.indexOf(name);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : fallback;
}

// Resolve project directories
async function getProjectDirs() {
  if (projectsArg) {
    return projectsArg.split(',').map(p => resolve(p.trim()));
  }
  if (watchDir) {
    const dir = resolve(watchDir);
    const entries = await readdir(dir, { withFileTypes: true });
    const dirs = [];
    for (const entry of entries) {
      if (entry.isDirectory()) {
        const wreckitDir = join(dir, entry.name, '.wreckit');
        if (existsSync(wreckitDir)) {
          dirs.push(join(dir, entry.name));
        }
      }
    }
    return dirs;
  }
  // Default: scan ~/Projects
  const home = process.env.HOME || '/tmp';
  const defaultDir = join(home, 'Projects');
  if (existsSync(defaultDir)) {
    const entries = await readdir(defaultDir, { withFileTypes: true });
    return entries
      .filter(e => e.isDirectory())
      .map(e => join(defaultDir, e.name));
  }
  return [];
}

// Read dashboard.json from a project
async function readDashboard(projectDir) {
  const dashFile = join(projectDir, '.wreckit', 'dashboard.json');
  try {
    const raw = await readFile(dashFile, 'utf-8');
    const data = JSON.parse(raw);
    data.repo = data.repo || basename(projectDir);
    return data;
  } catch {
    return null;
  }
}

// Aggregate all project statuses
async function getStatus() {
  const dirs = await getProjectDirs();
  const runs = [];
  for (const dir of dirs) {
    const data = await readDashboard(dir);
    if (data) runs.push(data);
  }
  return { runs, timestamp: new Date().toISOString(), projectCount: dirs.length };
}

// Serve
const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (url.pathname === '/api/status') {
    const status = await getStatus();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(status));
    return;
  }

  // Serve dashboard HTML
  if (url.pathname === '/' || url.pathname === '/index.html') {
    const html = await readFile(new URL('./index.html', import.meta.url), 'utf-8');
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`🔨 wreckit dashboard → http://localhost:${PORT}`);
  console.log(`   API endpoint → http://localhost:${PORT}/api/status`);
  if (watchDir) console.log(`   Watching: ${resolve(watchDir)}`);
  else if (projectsArg) console.log(`   Projects: ${projectsArg}`);
  else console.log(`   Auto-scanning: ~/Projects/*/. wreckit/`);
});
