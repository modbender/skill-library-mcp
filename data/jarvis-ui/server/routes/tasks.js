// ── Tasks Routes: /api/tasks CRUD ──

import { Router } from 'express';
import { readFile, writeFile } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { broadcastEvent } from '../sse.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TASKS_FILE = path.join(__dirname, '..', '..', 'tasks.json');

const router = Router();

async function loadTasks() {
  try { if (existsSync(TASKS_FILE)) return JSON.parse(await readFile(TASKS_FILE, 'utf8')); } catch {}
  return [];
}

async function saveTasks(tasks) {
  await writeFile(TASKS_FILE, JSON.stringify(tasks, null, 2));
}

function generateId() {
  return `t_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

router.get('/tasks', async (req, res) => {
  res.json(await loadTasks());
});

router.post('/tasks', async (req, res) => {
  const { title, description, priority, tags, schedule } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });

  const task = {
    id: generateId(), title, description: description || '', status: 'pending',
    priority: priority || 'medium', progress: null, tags: tags || [],
    schedule: schedule || null, createdAt: Date.now(), updatedAt: Date.now(),
  };
  const tasks = await loadTasks();
  tasks.unshift(task);
  await saveTasks(tasks);
  broadcastEvent('task-update');
  res.json(task);
});

router.patch('/tasks/:id', async (req, res) => {
  const tasks = await loadTasks();
  const idx = tasks.findIndex(t => t.id === req.params.id);
  if (idx < 0) return res.status(404).json({ error: 'not found' });

  const allowed = ['title', 'description', 'status', 'priority', 'progress', 'tags', 'schedule'];
  for (const key of allowed) {
    if (req.body[key] !== undefined) tasks[idx][key] = req.body[key];
  }
  tasks[idx].updatedAt = Date.now();
  if (req.body.status === 'done' && !tasks[idx].completedAt) tasks[idx].completedAt = Date.now();
  if (req.body.status !== 'done') delete tasks[idx].completedAt;

  await saveTasks(tasks);
  broadcastEvent('task-update');
  res.json(tasks[idx]);
});

router.delete('/tasks/:id', async (req, res) => {
  let tasks = await loadTasks();
  const before = tasks.length;
  tasks = tasks.filter(t => t.id !== req.params.id);
  if (tasks.length === before) return res.status(404).json({ error: 'not found' });
  await saveTasks(tasks);
  broadcastEvent('task-update');
  res.json({ ok: true });
});

export default router;
