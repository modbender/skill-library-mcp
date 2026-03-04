// ── MEMORY 每日話題面板 ──
// 讀取 memory/*.md 的 ## 標題，顯示為 timeline

const PAGE_SIZE = 7;
let days = [];
let totalFiles = 0;
let lastUpdate = '';
let hasMore = false;
let currentOffset = 0;
let collapsedDates = new Set();

// ── API ──

async function fetchMemory(offset = 0, append = false) {
  try {
    const res = await fetch(`/api/memory?limit=${PAGE_SIZE}&offset=${offset}`);
    if (!res.ok) throw new Error('fetch failed');
    const data = await res.json();

    if (append) {
      days = [...days, ...data.days];
    } else {
      days = data.days;
    }
    totalFiles = data.totalFiles;
    lastUpdate = data.lastUpdate;
    hasMore = data.hasMore;
    currentOffset = offset + data.days.length;

    render();
  } catch (err) {
    console.error('[MEMORY] fetch error:', err);
  }
}

// ── 渲染 ──

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderDay(day) {
  const isCollapsed = collapsedDates.has(day.date);
  const arrow = isCollapsed ? '▸' : '▾';
  const labelSuffix = day.label ? ` <span class="mem-day-label">${day.label}</span>` : '';

  return `
    <div class="mem-day" data-date="${day.date}">
      <div class="mem-day-header" data-action="toggle">
        <span class="mem-day-arrow">${arrow}</span>
        <span class="mem-day-date">${escapeHtml(day.displayDate)}</span>
        ${labelSuffix}
        <span class="mem-day-count">${day.topics.length}</span>
      </div>
      ${!isCollapsed ? `
        <div class="mem-day-topics">
          ${day.topics.length > 0
            ? day.topics.map(t => `<div class="mem-topic">${escapeHtml(t)}</div>`).join('')
            : `<div class="mem-topic mem-topic-empty">No entries</div>`
          }
        </div>
      ` : ''}
    </div>
  `;
}

function render() {
  const container = document.getElementById('rtab-memory');
  if (!container) return;

  container.innerHTML = `
    <div class="mem-header">
      <div class="data-row">
        <span class="data-label">FILES:</span>
        <span class="data-value">${totalFiles}</span>
      </div>
      <div class="data-row">
        <span class="data-label">UPDATED:</span>
        <span class="data-value">${lastUpdate || '—'}</span>
      </div>
    </div>

    <div class="mem-timeline">
      ${days.length === 0
        ? `<div class="mem-empty">NO MEMORY FILES FOUND</div>`
        : days.map(renderDay).join('')
      }
    </div>

    ${hasMore ? `
      <div class="mem-more-wrapper">
        <button class="mem-more-btn" id="mem-more-btn">▼ MORE</button>
      </div>
    ` : ''}
  `;

  bindEvents(container);
}

// ── 事件 ──

function bindEvents(container) {
  // 折疊/展開
  container.querySelectorAll('.mem-day-header').forEach(header => {
    header.addEventListener('click', () => {
      const date = header.closest('.mem-day').dataset.date;
      if (collapsedDates.has(date)) {
        collapsedDates.delete(date);
      } else {
        collapsedDates.add(date);
      }
      render();
    });
  });

  // MORE 按鈕
  container.querySelector('#mem-more-btn')?.addEventListener('click', () => {
    fetchMemory(currentOffset, true);
  });
}

// ── 初始化 ──

export function initMemory() {
  fetchMemory(0);
}
