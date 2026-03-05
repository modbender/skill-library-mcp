// ── SKILLS 技能面板 ──
// 即時掃描本機 skills，分類顯示

let skills = [];
let sourceFilter = 'workspace'; // all | workspace | global
let expandedSkill = null;

// ── API ──

async function fetchSkills() {
  try {
    const res = await fetch('/api/skills');
    if (!res.ok) throw new Error('fetch failed');
    skills = await res.json();
    render();
  } catch (err) {
    console.error('[SKILLS] fetch error:', err);
  }
}

// ── 渲染 ──

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function getFilteredSkills() {
  if (sourceFilter === 'all') return skills;
  return skills.filter(s => s.source === sourceFilter);
}

function renderSkillItem(skill) {
  const isExpanded = expandedSkill === skill.slug;
  const sourceTag = skill.source === 'workspace' ? 'LOCAL' : 'GLOBAL';
  const sourceClass = skill.source === 'workspace' ? 'source-local' : 'source-global';

  return `
    <div class="skill-item-v2 ${isExpanded ? 'expanded' : ''}" data-slug="${skill.slug}">
      <div class="skill-row-main">
        <span class="skill-icon-v2">${skill.emoji}</span>
        <span class="skill-name-v2">${escapeHtml(skill.name.toUpperCase())}</span>
        <span class="skill-source-tag ${sourceClass}">${sourceTag}</span>
        <button class="skill-expand-btn" data-action="toggle" title="DETAILS">
          ${isExpanded ? '▾' : '▸'}
        </button>
      </div>
      ${isExpanded ? `
        <div class="skill-details">
          <div class="skill-desc">${escapeHtml(skill.description || 'No description')}</div>
          <div class="skill-path-row">
            <span class="skill-path-label">PATH:</span>
            <span class="skill-path-value">${escapeHtml(skill.path)}</span>
          </div>
        </div>
      ` : ''}
    </div>
  `;
}

function render() {
  const container = document.getElementById('rtab-skills');
  if (!container) return;

  const filtered = getFilteredSkills();
  const counts = {
    all: skills.length,
    workspace: skills.filter(s => s.source === 'workspace').length,
    global: skills.filter(s => s.source === 'global').length,
  };

  container.innerHTML = `
    <div class="skills-header">
      <div class="skills-filters">
        <button class="skills-filter-btn ${sourceFilter === 'all' ? 'active' : ''}" data-filter="all">
          ALL <span class="skills-count">${counts.all}</span>
        </button>
        <button class="skills-filter-btn ${sourceFilter === 'workspace' ? 'active' : ''}" data-filter="workspace">
          LOCAL <span class="skills-count">${counts.workspace}</span>
        </button>
        <button class="skills-filter-btn ${sourceFilter === 'global' ? 'active' : ''}" data-filter="global">
          GLOBAL <span class="skills-count">${counts.global}</span>
        </button>
      </div>
      <button class="skills-refresh-btn" id="skills-refresh-btn" title="REFRESH">⟳</button>
    </div>

    <div class="skills-list-v2" id="skills-list">
      ${filtered.length === 0
        ? `<div class="skills-empty">NO SKILLS FOUND</div>`
        : filtered.map(renderSkillItem).join('')
      }
    </div>

    <div class="skills-stats">
      <span>${counts.workspace} LOCAL</span>
      <span class="skills-stats-sep">|</span>
      <span>${counts.global} GLOBAL</span>
      <span class="skills-stats-sep">|</span>
      <span>${counts.all} TOTAL</span>
    </div>
  `;

  bindEvents(container);
}

// ── 事件 ──

function bindEvents(container) {
  // Filter
  container.querySelectorAll('.skills-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sourceFilter = btn.dataset.filter;
      render();
    });
  });

  // Refresh
  container.querySelector('#skills-refresh-btn')?.addEventListener('click', () => {
    fetchSkills();
  });

  // Expand/collapse
  container.querySelectorAll('.skill-item-v2').forEach(item => {
    const slug = item.dataset.slug;

    item.querySelector('[data-action="toggle"]')?.addEventListener('click', (e) => {
      e.stopPropagation();
      expandedSkill = expandedSkill === slug ? null : slug;
      render();
    });

    // 點整行也展開
    item.querySelector('.skill-row-main')?.addEventListener('click', () => {
      expandedSkill = expandedSkill === slug ? null : slug;
      render();
    });
  });
}

// ── 初始化 ──

export function initSkills() {
  fetchSkills();
}
