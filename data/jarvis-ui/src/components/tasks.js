// ── TASKS 任務管理系統 ──
// 進階版：CRUD、優先級、排程、進度追蹤

import { getAccentHex } from '../config/theme.js';

function getPriorityMap() {
  return {
    critical: { label: 'CRIT', color: '#ff2d2d', icon: '⚠' },
    high:     { label: 'HIGH', color: getAccentHex(), icon: '▲' },
    medium:   { label: 'MED',  color: '#ff8c42', icon: '●' },
    low:      { label: 'LOW',  color: '#666',    icon: '▽' },
  };
}

const PRIORITY_MAP = getPriorityMap();

const STATUS_MAP = {
  pending:  { label: 'PENDING',  icon: '○', class: 'pending' },
  running:  { label: 'RUNNING',  icon: '▶', class: 'active' },
  done:     { label: 'DONE',     icon: '✓', class: 'done' },
  failed:   { label: 'FAILED',   icon: '✗', class: 'failed' },
  deferred: { label: 'DEFERRED', icon: '◇', class: 'deferred' },
};

let tasks = [];
let filter = 'all'; // all | active | done

// ── API ──

async function fetchTasks() {
  try {
    const res = await fetch('/api/tasks');
    if (!res.ok) throw new Error('fetch failed');
    tasks = await res.json();
    render();
  } catch (err) {
    console.error('[TASKS] fetch error:', err);
  }
}

async function createTask(task) {
  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    if (!res.ok) throw new Error('create failed');
    const created = await res.json();
    tasks.unshift(created);
    render();
    return created;
  } catch (err) {
    console.error('[TASKS] create error:', err);
  }
}

async function updateTask(id, patch) {
  try {
    const res = await fetch(`/api/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    });
    if (!res.ok) throw new Error('update failed');
    const updated = await res.json();
    const idx = tasks.findIndex(t => t.id === id);
    if (idx >= 0) tasks[idx] = updated;
    render();
    return updated;
  } catch (err) {
    console.error('[TASKS] update error:', err);
  }
}

async function deleteTask(id) {
  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('delete failed');
    tasks = tasks.filter(t => t.id !== id);
    render();
  } catch (err) {
    console.error('[TASKS] delete error:', err);
  }
}

async function cycleStatus(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;
  const order = ['pending', 'running', 'done'];
  const idx = order.indexOf(task.status);
  const next = order[(idx + 1) % order.length];
  await updateTask(id, { status: next });
}

async function cyclePriority(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;
  const order = ['low', 'medium', 'high', 'critical'];
  const idx = order.indexOf(task.priority);
  const next = order[(idx + 1) % order.length];
  await updateTask(id, { priority: next });
}

// ── 渲染 ──

function getFilteredTasks() {
  let filtered = [...tasks];
  if (filter === 'active') filtered = filtered.filter(t => t.status !== 'done');
  if (filter === 'done') filtered = filtered.filter(t => t.status === 'done');

  // 排序：priority (critical > high > medium > low), 然後 createdAt
  const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
  const statusOrder = { running: 0, pending: 1, deferred: 2, failed: 3, done: 4 };
  filtered.sort((a, b) => {
    const sa = statusOrder[a.status] ?? 5;
    const sb = statusOrder[b.status] ?? 5;
    if (sa !== sb) return sa - sb;
    const pa = priorityOrder[a.priority] ?? 3;
    const pb = priorityOrder[b.priority] ?? 3;
    if (pa !== pb) return pa - pb;
    return (b.createdAt || 0) - (a.createdAt || 0);
  });
  return filtered;
}

function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  const now = new Date();
  const diffMs = now - d;
  if (diffMs < 60000) return 'JUST NOW';
  if (diffMs < 3600000) return `${Math.floor(diffMs / 60000)}M AGO`;
  if (diffMs < 86400000) return `${Math.floor(diffMs / 3600000)}H AGO`;
  // 同年只顯示 MM/DD
  if (d.getFullYear() === now.getFullYear()) {
    return `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`;
  }
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`;
}

function formatSchedule(task) {
  if (!task.schedule) return '';
  if (task.schedule.type === 'once') {
    return `⏰ ${new Date(task.schedule.at).toLocaleString('zh-TW', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}`;
  }
  if (task.schedule.type === 'recurring') {
    return `🔄 ${task.schedule.label || task.schedule.cron || 'RECURRING'}`;
  }
  return '';
}

function renderTaskItem(task) {
  const status = STATUS_MAP[task.status] || STATUS_MAP.pending;
  const priorityMap = getPriorityMap();
  const priority = priorityMap[task.priority] || priorityMap.medium;
  const progress = task.progress ?? null;
  const schedule = formatSchedule(task);
  const time = formatTime(task.createdAt);

  return `
    <div class="task-item-v2 ${status.class}" data-id="${task.id}">
      <div class="task-row-main">
        <button class="task-status-btn ${status.class}" data-action="cycle-status" title="CYCLE STATUS">
          ${status.icon}
        </button>
        <span class="task-text-v2">${escapeHtml(task.title)}</span>
        <button class="task-priority-btn" data-action="cycle-priority" 
                style="color:${priority.color}" title="${priority.label}">
          ${priority.icon}
        </button>
        <button class="task-delete-btn" data-action="delete" title="DELETE">×</button>
      </div>
      ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
      <div class="task-row-meta">
        ${progress !== null ? `
          <div class="task-progress">
            <div class="task-progress-bar" style="width:${progress}%"></div>
            <span class="task-progress-text">${progress}%</span>
          </div>
        ` : ''}
        ${schedule ? `<span class="task-meta-tag schedule">${schedule}</span>` : ''}
        ${task.tags?.length ? task.tags.map(t => `<span class="task-meta-tag tag">${escapeHtml(t)}</span>`).join('') : ''}
        <span class="task-time">${time}</span>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function render() {
  const container = document.getElementById('rtab-tasks');
  if (!container) return;

  const filtered = getFilteredTasks();
  const counts = {
    all: tasks.length,
    active: tasks.filter(t => t.status !== 'done').length,
    done: tasks.filter(t => t.status === 'done').length,
  };

  container.innerHTML = `
    <div class="tasks-header">
      <div class="tasks-filters">
        <button class="tasks-filter-btn ${filter === 'all' ? 'active' : ''}" data-filter="all">
          ALL <span class="tasks-count">${counts.all}</span>
        </button>
        <button class="tasks-filter-btn ${filter === 'active' ? 'active' : ''}" data-filter="active">
          ACTIVE <span class="tasks-count">${counts.active}</span>
        </button>
        <button class="tasks-filter-btn ${filter === 'done' ? 'active' : ''}" data-filter="done">
          DONE <span class="tasks-count">${counts.done}</span>
        </button>
      </div>
      <button class="tasks-add-btn" id="tasks-add-btn" title="NEW TASK">+</button>
    </div>

    <div class="tasks-add-form" id="tasks-add-form" style="display:none">
      <input type="text" class="tasks-input" id="tasks-input-title" placeholder="TASK TITLE..." />
      <div class="tasks-form-row">
        <select class="tasks-select" id="tasks-input-priority">
          <option value="medium">● MED</option>
          <option value="low">▽ LOW</option>
          <option value="high">▲ HIGH</option>
          <option value="critical">⚠ CRIT</option>
        </select>
        <input type="text" class="tasks-input tasks-input-tags" id="tasks-input-tags" placeholder="TAGS (COMMA SEP)" />
        <button class="tasks-submit-btn" id="tasks-submit-btn">ADD</button>
      </div>
    </div>

    <div class="tasks-list-v2" id="tasks-list">
      ${filtered.length === 0 
        ? `<div class="tasks-empty">NO TASKS ${filter !== 'all' ? `(${filter.toUpperCase()})` : ''}</div>`
        : filtered.map(renderTaskItem).join('')
      }
    </div>

    <div class="tasks-stats">
      <span>${counts.active} ACTIVE</span>
      <span class="tasks-stats-sep">|</span>
      <span>${counts.done} COMPLETED</span>
    </div>
  `;

  bindEvents(container);
}

// ── 事件綁定 ──

function bindEvents(container) {
  // Filter buttons
  container.querySelectorAll('.tasks-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      filter = btn.dataset.filter;
      render();
    });
  });

  // Add button toggle
  const addBtn = container.querySelector('#tasks-add-btn');
  const addForm = container.querySelector('#tasks-add-form');
  if (addBtn && addForm) {
    addBtn.addEventListener('click', () => {
      const visible = addForm.style.display !== 'none';
      addForm.style.display = visible ? 'none' : 'flex';
      if (!visible) {
        container.querySelector('#tasks-input-title')?.focus();
      }
    });
  }

  // Submit
  const submitBtn = container.querySelector('#tasks-submit-btn');
  const titleInput = container.querySelector('#tasks-input-title');
  if (submitBtn && titleInput) {
    const doSubmit = () => {
      const title = titleInput.value.trim();
      if (!title) return;
      const priority = container.querySelector('#tasks-input-priority')?.value || 'medium';
      const tagsRaw = container.querySelector('#tasks-input-tags')?.value || '';
      const tags = tagsRaw.split(',').map(t => t.trim()).filter(Boolean);
      createTask({ title, priority, tags });
      titleInput.value = '';
      if (container.querySelector('#tasks-input-tags')) container.querySelector('#tasks-input-tags').value = '';
      addForm.style.display = 'none';
    };
    submitBtn.addEventListener('click', doSubmit);
    titleInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') doSubmit();
    });
  }

  // Task item actions (event delegation)
  container.querySelectorAll('.task-item-v2').forEach(item => {
    const id = item.dataset.id;

    item.querySelector('[data-action="cycle-status"]')?.addEventListener('click', (e) => {
      e.stopPropagation();
      cycleStatus(id);
    });

    item.querySelector('[data-action="cycle-priority"]')?.addEventListener('click', (e) => {
      e.stopPropagation();
      cyclePriority(id);
    });

    item.querySelector('[data-action="delete"]')?.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteTask(id);
    });
  });
}

// ── SSE 監聽（即時更新） ──

function listenSSE() {
  // 共用 chat.js 建立的 SSE 連線
  const tryBind = () => {
    const source = window.__jarvisSSE;
    if (!source) { setTimeout(tryBind, 1000); return; }
    source.addEventListener('message', (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'task-update') fetchTasks();
      } catch {}
    });
  };
  tryBind();
}

// ── 初始化 ──

export function initTasks() {
  fetchTasks();
  listenSSE();
}
