/* ── Newsletter Reader — app.js ── */

const state = {
  stories: [],
  votes: {},   // storyId → 'up' | 'down' | 'save'
  notes: {},   // storyId → note string
  date: null,
};

// ── DOM refs ──
const loadingEl   = document.getElementById('loading');
const errorEl     = document.getElementById('error');
const errorMsgEl  = document.getElementById('error-msg');
const storiesEl   = document.getElementById('stories-list');
const headerMeta  = document.getElementById('header-meta');
const refreshBtn  = document.getElementById('refresh-btn');
const retryBtn    = document.getElementById('retry-btn');
const toastEl     = document.getElementById('toast');

// ── Init ──
loadData();
refreshBtn.addEventListener('click', () => loadData(true));
retryBtn.addEventListener('click',   () => loadData(true));

// ── Load stories ──
async function loadData(forceRefresh = false) {
  showLoading();
  if (forceRefresh) {
    refreshBtn.classList.add('spinning');
  }

  try {
    const res = await fetch('/api/today', { cache: forceRefresh ? 'reload' : 'default' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Server error ${res.status}`);
    }
    const data = await res.json();
    state.stories = data.stories || [];
    state.date = data.date;

    // Load existing votes from localStorage
    loadVotesFromStorage();

    // Load notes from server
    try {
      const nr = await fetch('/api/notes');
      if (nr.ok) state.notes = await nr.json();
    } catch {}

    renderHeader(data);
    renderStories();
  } catch (err) {
    showError(err.message);
  } finally {
    refreshBtn.classList.remove('spinning');
  }
}

// ── Render header ──
function renderHeader(data) {
  const date = data.date ? formatDate(data.date) : '';
  const count = (data.stories || []).length;
  headerMeta.textContent = `${date} · ${count} stor${count === 1 ? 'y' : 'ies'}`;
}

// ── Render all story cards ──
function renderStories() {
  storiesEl.innerHTML = '';
  showStories();

  if (!state.stories.length) {
    showError('No stories in today\'s digest.');
    return;
  }

  state.stories
    .slice()
    .sort((a, b) => (a.rank || 0) - (b.rank || 0))
    .forEach(story => {
      const card = buildCard(story);
      storiesEl.appendChild(card);
    });
}

// ── Build a story card ──
function buildCard(story) {
  const div = document.createElement('div');
  div.className = 'story-card';
  div.dataset.id = story.id;

  const vote = state.votes[story.id];
  if (vote === 'up')   div.classList.add('voted-up');
  if (vote === 'down') div.classList.add('voted-down');
  if (vote === 'save') div.classList.add('voted-save');

  const scoreText = story.score != null
    ? `${Math.round(story.score * 100)}% match`
    : '';

  // Bullets HTML
  const hasBullets = story.bullets && story.bullets.length > 0;
  const bulletsHtml = hasBullets ? `
    <button class="bullets-toggle" aria-expanded="false">
      <svg class="chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
      Key points
    </button>
    <ul class="bullets-list">
      ${story.bullets.map(b => `<li>${escapeHtml(b)}</li>`).join('')}
    </ul>
  ` : '';

  const searchQuery = encodeURIComponent(`subject:"${story.subject || story.headline}"`);
  const gmailUrl = story.subject || story.headline
    ? `googlegmail:///search?q=${searchQuery}`
    : story.gmailUrl;
  const gmailHtml = gmailUrl ? `
    <a class="gmail-link" href="${escapeHtml(gmailUrl)}" target="_blank" rel="noopener">
      Open in Gmail
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
    </a>
  ` : '';

  const hasBody = !!(story.hasBody || story.body);

  const upActive   = vote === 'up'   ? ' active-up'   : '';
  const downActive = vote === 'down' ? ' active-down' : '';
  const saveActive = vote === 'save' ? ' active-save' : '';

  const hasNote = !!state.notes[story.id];

  div.innerHTML = `
    <div class="card-top">
      <span class="source-pill">${escapeHtml(story.source || '')}</span>
      <span class="score-badge">${escapeHtml(scoreText)}</span>
      ${hasNote ? '<span class="note-indicator" title="Has note">✏️</span>' : ''}
    </div>
    <div class="card-headline">${escapeHtml(story.headline || story.subject || '')}</div>
    <div class="card-summary">${escapeHtml(truncateSummary(story.summary || ''))}</div>
    ${bulletsHtml}
    <div class="card-divider"></div>
    <div class="card-actions">
      ${hasBody ? `<button class="btn-read-full" data-id="${story.id}" data-source="${escapeHtml(story.source)}" data-headline="${escapeHtml(story.headline || story.subject)}">Read full email →</button>` : ''}
      <button class="action-btn btn-save${saveActive}" data-id="${story.id}" data-action="save" title="Save to reading list">
        <span class="btn-icon">🔖</span>
      </button>
    </div>
  `;

  // Bullets toggle
  const toggle = div.querySelector('.bullets-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const list = div.querySelector('.bullets-list');
      const isOpen = toggle.classList.contains('open');
      toggle.classList.toggle('open', !isOpen);
      list.classList.toggle('open', !isOpen);
      toggle.setAttribute('aria-expanded', String(!isOpen));
    });
  }

  // Read full → open modal (fetch body on demand)
  const readToggle = div.querySelector('.btn-read-full');
  if (readToggle) {
    readToggle.addEventListener('click', async () => {
      openEmailModal({
        storyId:  story.id,
        source:   readToggle.dataset.source,
        headline: readToggle.dataset.headline,
        body:     null, // will load async
        gmailUrl,
        note:     state.notes[story.id] || '',
      });
      // Fetch body after modal opens
      try {
        const r = await fetch(`/api/story/${story.id}`);
        const data = await r.json();
        setModalBody(data.body || '');
      } catch {
        setModalBody('<p style="padding:20px;color:#999">Failed to load email.</p>');
      }
    });
  }

  // Vote/save buttons
  div.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      const id = btn.dataset.id;
      const action = btn.dataset.action;
      handleAction(id, action, div);
    });
  });

  return div;
}

// ── Handle vote/save ──
async function handleAction(storyId, action, cardEl) {
  const prevVote = state.votes[storyId];

  if (action === 'save') {
    // Save is additive — toggle off if already saved
    if (prevVote === 'save') {
      // Can't unsave, just show toast
      showToast('🔖 Already saved');
      return;
    }
    state.votes[storyId] = 'save';
    updateCardState(cardEl, storyId);
    saveVotesToStorage();
    showToast('🔖 Saved to reading list');
    try {
      await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ storyId }),
      });
    } catch { /* silent fail */ }
    return;
  }

  // Toggle vote off if same, otherwise switch
  if (prevVote === action) {
    delete state.votes[storyId];
  } else {
    state.votes[storyId] = action;
  }

  updateCardState(cardEl, storyId);
  saveVotesToStorage();

  const newVote = state.votes[storyId];
  if (newVote) {
    showToast(newVote === 'up' ? '👍 Noted' : '👎 Noted');
    try {
      await fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ storyId, vote: newVote }),
      });
    } catch { /* silent fail */ }
  }
}

// ── Update card visual state ──
function updateCardState(cardEl, storyId) {
  const vote = state.votes[storyId];
  cardEl.classList.remove('voted-up', 'voted-down', 'voted-save');
  if (vote === 'up')   cardEl.classList.add('voted-up');
  if (vote === 'down') cardEl.classList.add('voted-down');
  if (vote === 'save') cardEl.classList.add('voted-save');

  const upBtn   = cardEl.querySelector('.btn-up');
  const downBtn = cardEl.querySelector('.btn-down');
  const saveBtn = cardEl.querySelector('.btn-save');

  if (upBtn)   { upBtn.classList.toggle('active-up', vote === 'up'); }
  if (downBtn) { downBtn.classList.toggle('active-down', vote === 'down'); }
  if (saveBtn) { saveBtn.classList.toggle('active-save', vote === 'save'); }
}

// ── localStorage persistence ──
function saveVotesToStorage() {
  try {
    localStorage.setItem('newsletter-votes', JSON.stringify(state.votes));
  } catch {}
}

function loadVotesFromStorage() {
  try {
    const raw = localStorage.getItem('newsletter-votes');
    if (raw) {
      const saved = JSON.parse(raw);
      // Only keep votes for today's stories
      const ids = new Set(state.stories.map(s => s.id));
      state.votes = {};
      for (const [id, vote] of Object.entries(saved)) {
        if (ids.has(id)) state.votes[id] = vote;
      }
    } else {
      state.votes = {};
    }
  } catch {
    state.votes = {};
  }
}

// ── Toast ──
let toastTimer = null;
function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.remove('hidden');
  requestAnimationFrame(() => { toastEl.classList.add('show'); });
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastEl.classList.remove('show');
    setTimeout(() => toastEl.classList.add('hidden'), 250);
  }, 1800);
}

// ── View state helpers ──
function showLoading() {
  loadingEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  storiesEl.classList.add('hidden');
}

function showError(msg) {
  loadingEl.classList.add('hidden');
  storiesEl.classList.add('hidden');
  errorMsgEl.textContent = msg;
  errorEl.classList.remove('hidden');
}

function showStories() {
  loadingEl.classList.add('hidden');
  errorEl.classList.add('hidden');
  storiesEl.classList.remove('hidden');
}

// ── Helpers ──
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function truncateSummary(text, maxLen = 320) {
  if (!text || text.length <= maxLen) return text;
  // Try to cut at sentence boundary
  const cut = text.slice(0, maxLen);
  const lastStop = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('! '), cut.lastIndexOf('? '));
  if (lastStop > 80) return text.slice(0, lastStop + 1);
  return cut.trimEnd() + '…';
}

function formatDate(dateStr) {
  try {
    const d = new Date(dateStr + 'T12:00:00Z');
    return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' });
  } catch {
    return dateStr;
  }
}

// ── Email modal ──
let modalFrame = null;

function openEmailModal({ storyId, source, headline, body, gmailUrl, note }) {
  let modal = document.getElementById('email-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'email-modal';
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-sheet">
        <div class="modal-header">
          <div class="modal-meta">
            <span class="modal-source"></span>
            <span class="modal-headline"></span>
          </div>
          <button class="modal-close" aria-label="Close">✕</button>
        </div>
        <div class="modal-body-wrap">
          <iframe class="modal-frame" sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox" title="Email content"></iframe>
        </div>
        <div class="modal-footer">
          <div class="modal-vote-row">
            <button class="modal-vote-btn modal-btn-up" data-action="up">👍 Interesting</button>
            <button class="modal-vote-btn modal-btn-down" data-action="down">👎 Not for me</button>
          </div>
          <div class="note-area">
            <textarea class="note-input" placeholder="Add a note or follow-up thought…" rows="2"></textarea>
            <div class="note-actions">
              <a class="modal-gmail-btn" target="_blank" rel="noopener">Open in Gmail →</a>
              <button class="note-save-btn">Save note</button>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector('.modal-close').addEventListener('click', closeEmailModal);
    modal.querySelector('.modal-backdrop').addEventListener('click', closeEmailModal);
    modalFrame = modal.querySelector('.modal-frame');
  }

  // Populate
  modal.querySelector('.modal-source').textContent = source || '';
  modal.querySelector('.modal-headline').textContent = headline || '';
  modal.dataset.storyId = storyId || '';

  const noteInput = modal.querySelector('.note-input');
  noteInput.value = note || '';

  const saveBtn = modal.querySelector('.note-save-btn');
  // Remove old listener by replacing the button
  const newSaveBtn = saveBtn.cloneNode(true);
  saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
  newSaveBtn.addEventListener('click', async () => {
    const sid = modal.dataset.storyId;
    const text = noteInput.value.trim();
    try {
      await fetch('/api/note', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ storyId: sid, note: text }),
      });
      state.notes[sid] = text || undefined;
      if (!text) delete state.notes[sid];
      // Update note indicator on card
      const card = document.querySelector(`.story-card[data-id="${sid}"]`);
      if (card) {
        const top = card.querySelector('.card-top');
        const existing = top.querySelector('.note-indicator');
        if (text && !existing) {
          const span = document.createElement('span');
          span.className = 'note-indicator';
          span.title = 'Has note';
          span.textContent = '✏️';
          top.appendChild(span);
        } else if (!text && existing) {
          existing.remove();
        }
      }
      showToast(text ? '✏️ Note saved' : '✏️ Note cleared');
    } catch {
      showToast('Failed to save note');
    }
  });

  // Vote buttons
  const currentVote = state.votes[storyId] || null;
  const upBtn   = modal.querySelector('.modal-btn-up');
  const downBtn = modal.querySelector('.modal-btn-down');
  upBtn.classList.toggle('active-up',     currentVote === 'up');
  downBtn.classList.toggle('active-down', currentVote === 'down');

  // Replace buttons to clear old listeners
  const freshUp   = upBtn.cloneNode(true);
  const freshDown = downBtn.cloneNode(true);
  upBtn.parentNode.replaceChild(freshUp, upBtn);
  downBtn.parentNode.replaceChild(freshDown, downBtn);

  [freshUp, freshDown].forEach(btn => {
    btn.addEventListener('click', async () => {
      const sid = modal.dataset.storyId;
      const action = btn.dataset.action;
      const card = document.querySelector(`.story-card[data-id="${sid}"]`);
      if (card) await handleAction(sid, action, card);
      // Update modal button states
      const v = state.votes[sid];
      freshUp.classList.toggle('active-up',     v === 'up');
      freshDown.classList.toggle('active-down', v === 'down');
    });
  });

  const gmailBtn = modal.querySelector('.modal-gmail-btn');
  if (gmailUrl) { gmailBtn.href = gmailUrl; gmailBtn.style.display = ''; }
  else { gmailBtn.style.display = 'none'; }

  // Show loading state immediately; body is populated async via setModalBody()
  modalFrame.srcdoc = `<html><body style="margin:0;display:flex;align-items:center;justify-content:center;height:100vh;background:#fff">
    <div style="width:28px;height:28px;border:2.5px solid rgba(0,0,0,0.08);border-top-color:#0066CC;border-radius:50%;animation:spin 0.7s linear infinite"></div>
    <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
  </body></html>`;

  // Soft interest signal — opening counts as a weak positive
  fetch('/api/vote', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ storyId: storyId, vote: 'open' })
  }).catch(() => {});

  // Open
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeEmailModal() {
  const modal = document.getElementById('email-modal');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
    if (modalFrame) modalFrame.srcdoc = '';
  }
}

function setModalBody(html) {
  if (!modalFrame) return;
  const wrapped = [
    '<html><head>',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<style>',
    '* { box-sizing: border-box; }',
    'body { margin: 0 !important; padding: 16px 18px !important; background: #fff; }',
    'img { max-width: 100% !important; height: auto !important; }',
    'table { max-width: 100% !important; }',
    '</style>',
    '</head><body>',
    html,
    '</body></html>',
  ].join('');

  modalFrame.onload = function() {
    try {
      const doc = modalFrame.contentDocument;
      if (!doc) return;
      // Force every link to open in new tab (external browser)
      doc.querySelectorAll('a[href]').forEach(function(a) {
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
      });
    } catch(e) {}
  };

  modalFrame.srcdoc = wrapped;
}
