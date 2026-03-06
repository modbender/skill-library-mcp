// ── SCHEDULE 排程面板 ──
// SYSTEM（heartbeat）+ CRON JOBS（可開關）

let heartbeat = null;
let jobs = [];

// ── SVG Icons ──

const ICON = {
  pulse: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  clock: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  play: `<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`,
  pause: `<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`,
  check: `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  x: `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
};

// ── API ──

async function fetchSchedule() {
  try {
    const res = await fetch('/api/schedule');
    if (!res.ok) throw new Error('fetch failed');
    const data = await res.json();
    heartbeat = data.heartbeat;
    jobs = data.jobs;
    render();
  } catch (err) {
    console.error('[SCHEDULE] fetch error:', err);
  }
}

async function toggleJob(id, enabled) {
  try {
    const res = await fetch(`/api/schedule/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    if (!res.ok) throw new Error('toggle failed');
    // 更新本地狀態
    const job = jobs.find(j => j.id === id);
    if (job) job.enabled = enabled;
    render();
  } catch (err) {
    console.error('[SCHEDULE] toggle error:', err);
  }
}

// ── 格式化 ──

function formatSchedule(schedule) {
  if (!schedule) return '—';

  if (schedule.kind === 'cron') {
    // 把常見 cron 表達式翻譯成人話
    const expr = schedule.expr;
    const parts = expr.split(/\s+/);
    if (parts.length === 5) {
      const [min, hour, dom, mon, dow] = parts;
      const dowNames = ['日', '一', '二', '三', '四', '五', '六'];

      // 每天固定時間: 0 9 * * * → 每天 09:00
      if (dom === '*' && mon === '*' && dow === '*' && !hour.includes('/') && !min.includes('/')) {
        return `每天 ${hour.padStart(2, '0')}:${min.padStart(2, '0')}`;
      }
      // 每小時: 0 */2 * * * → 每 2 小時
      if (hour.startsWith('*/')) {
        return `每 ${hour.slice(2)} 小時`;
      }
      // 每分鐘間隔: */5 * * * * → 每 5 分鐘
      if (min.startsWith('*/')) {
        return `每 ${min.slice(2)} 分鐘`;
      }
      // 每週某天: 0 9 * * 1 → 每週一 09:00
      if (dom === '*' && mon === '*' && /^\d$/.test(dow)) {
        return `每週${dowNames[parseInt(dow)]} ${hour.padStart(2, '0')}:${min.padStart(2, '0')}`;
      }
    }
    return expr; // fallback 顯示原始表達式
  }

  if (schedule.kind === 'every') {
    const ms = schedule.everyMs;
    if (ms >= 3600000) return `每 ${ms / 3600000} 小時`;
    if (ms >= 60000) return `每 ${ms / 60000} 分鐘`;
    return `每 ${ms / 1000} 秒`;
  }

  if (schedule.kind === 'at') {
    const d = new Date(schedule.at);
    return d.toLocaleString('en-CA', { timeZone: 'Asia/Taipei', hour: '2-digit', minute: '2-digit', hour12: false });
  }
  return '—';
}

// heartbeat 間隔翻譯
function formatHeartbeat(every) {
  if (!every) return '每 30 分鐘';
  const match = every.match(/^(\d+)(ms|s|m|h)$/i);
  if (!match) return every;
  const val = parseInt(match[1]);
  const unit = match[2].toLowerCase();
  if (unit === 'h') return `每 ${val} 小時`;
  if (unit === 'm') return `每 ${val} 分鐘`;
  if (unit === 's') return `每 ${val} 秒`;
  return every;
}

function formatTime(ms) {
  if (!ms) return '—';
  const d = new Date(ms);
  const now = new Date();
  const todayStr = now.toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });
  const dateStr = d.toLocaleDateString('en-CA', { timeZone: 'Asia/Taipei' });
  const timeStr = d.toLocaleTimeString('en-CA', { timeZone: 'Asia/Taipei', hour: '2-digit', minute: '2-digit', hour12: false });
  if (dateStr === todayStr) return timeStr;
  return `${dateStr.slice(5)} ${timeStr}`;
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── 渲染 ──

function render() {
  const container = document.getElementById('rtab-schedule');
  if (!container) return;

  container.innerHTML = `
    <div class="sched-section">
      <div class="sched-section-title">${ICON.pulse} SYSTEM</div>
      <div class="sched-items">
        ${heartbeat ? `
          <div class="sched-item">
            <div class="sched-row-main">
              <span class="sched-expr">${escapeHtml(formatHeartbeat(heartbeat.every))}</span>
              <span class="sched-name">HEARTBEAT</span>
              <span class="sched-status ${heartbeat.enabled ? 'on' : 'off'}">
                ${heartbeat.enabled ? ICON.check : ICON.x}
              </span>
            </div>
            <div class="sched-row-meta">
              <span class="sched-meta">LAST: ${formatTime(heartbeat.lastRun)}${heartbeat.lastStatus ? ` · ${heartbeat.lastStatus.toUpperCase().replace('OK-TOKEN', 'OK')}` : ''}</span>
            </div>
            ${heartbeat.content ? `
              <div class="sched-hb-toggle" data-action="expand-hb">▸ 查看內容</div>
              <div class="sched-hb-content hidden">
                <pre class="sched-hb-pre">${escapeHtml(heartbeat.content)}</pre>
              </div>
            ` : ''}
          </div>
        ` : ''}
      </div>
    </div>

    <div class="sched-section">
      <div class="sched-section-title">${ICON.clock} CRON JOBS</div>
      <div class="sched-items">
        ${jobs.length === 0
          ? `<div class="sched-empty">NO SCHEDULED JOBS</div>`
          : jobs.map(renderJob).join('')
        }
      </div>
    </div>
  `;

  bindEvents(container);
}

function renderJob(job) {
  return `
    <div class="sched-item" data-id="${job.id}">
      <div class="sched-row-main">
        <span class="sched-expr">${escapeHtml(formatSchedule(job.schedule))}</span>
        <span class="sched-name">${escapeHtml(job.name)}</span>
        <button class="sched-toggle ${job.enabled ? 'on' : 'off'}" data-action="toggle" title="${job.enabled ? 'DISABLE' : 'ENABLE'}">
          ${job.enabled ? ICON.pause : ICON.play}
        </button>
      </div>
      <div class="sched-row-meta">
        <span class="sched-meta">LAST: ${formatTime(job.lastRun)}${job.lastStatus ? ` · ${job.lastStatus.toUpperCase()}` : ''}</span>
        <span class="sched-meta">NEXT: ${formatTime(job.nextRun)}</span>
      </div>
    </div>
  `;
}

// ── 事件 ──

function bindEvents(container) {
  container.querySelectorAll('[data-action="toggle"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const item = btn.closest('.sched-item');
      const id = item.dataset.id;
      const job = jobs.find(j => j.id === id);
      if (job) toggleJob(id, !job.enabled);
    });
  });

  // heartbeat 內容展開/收合
  container.querySelectorAll('[data-action="expand-hb"]').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const content = toggle.nextElementSibling;
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        toggle.textContent = '▾ 隱藏內容';
      } else {
        content.classList.add('hidden');
        toggle.textContent = '▸ 查看內容';
      }
    });
  });
}

// ── SSE 監聽 ──

function listenSSE() {
  // 共用 chat.js 建立的 SSE 連線
  const tryBind = () => {
    const source = window.__jarvisSSE;
    if (!source) { setTimeout(tryBind, 1000); return; }
    source.addEventListener('message', (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'schedule-update') fetchSchedule();
      } catch {}
    });
  };
  tryBind();
}

// ── 初始化 ──

export function initSchedule() {
  fetchSchedule();
  listenSSE();
}
