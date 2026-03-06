/* =============================================================
   BRIDGE COMMAND — Dashboard Controller
   Connects to FastAPI backend at localhost:9120
   ============================================================= */

(function () {
  'use strict';

  // ---- Config ----
  const API_BASE = localStorage.getItem('bridge_api_base') || 'http://localhost:9120';
  let TOKEN = localStorage.getItem('bridge_token') || '';
  let ws = null;
  let wsRetryTimer = null;
  let wsRetries = 0;
  const WS_MAX_RETRIES = 20;
  const WS_RETRY_DELAY = 3000;

  // ---- DOM refs ----
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  const statusDot      = $('#statusDot');
  const statusLabel    = $('#statusLabel');
  const tokenModal     = $('#tokenModal');
  const tokenInput     = $('#tokenInput');
  const pendingBadge   = $('#pendingBadge');
  const approvalList   = $('#approvalList');
  const emptyApprovals = $('#emptyApprovals');
  const fileTree       = $('#fileTree');
  const auditLog       = $('#auditLog');
  const toastContainer = $('#toastContainer');

  // ---- State ----
  let approvals = [];
  let showAll = true;

  // ===========================================================
  //  API HELPERS
  // ===========================================================

  function headers() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TOKEN}`
    };
  }

  async function api(path, opts = {}) {
    const url = `${API_BASE}${path}`;
    try {
      const res = await fetch(url, { headers: headers(), ...opts });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status}: ${text}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`[API] ${path}:`, err);
      throw err;
    }
  }

  // ===========================================================
  //  TOKEN / AUTH
  // ===========================================================

  function openTokenModal() {
    tokenInput.value = TOKEN;
    tokenModal.classList.add('modal--open');
    setTimeout(() => tokenInput.focus(), 100);
  }

  function closeTokenModal() {
    tokenModal.classList.remove('modal--open');
  }

  function saveToken() {
    TOKEN = tokenInput.value.trim();
    localStorage.setItem('bridge_token', TOKEN);
    closeTokenModal();
    toast('Token saved', 'success');
    connectWs();
    refreshAll();
  }

  $('#tokenBtn').addEventListener('click', openTokenModal);
  $('#tokenCancel').addEventListener('click', closeTokenModal);
  $('#tokenSave').addEventListener('click', saveToken);
  tokenInput.addEventListener('keydown', e => { if (e.key === 'Enter') saveToken(); });
  $('.modal__backdrop', tokenModal).addEventListener('click', closeTokenModal);

  // ===========================================================
  //  WEBSOCKET
  // ===========================================================

  function setConnectionStatus(state) {
    statusDot.className = 'status-dot';
    if (state === 'connected') {
      statusDot.classList.add('status-dot--connected');
      statusLabel.textContent = 'CONNECTED';
      $('#wsStatus').textContent = 'LIVE';
      $('#wsStatus').className = 'status-card__value status-card__value--ok';
    } else if (state === 'error') {
      statusDot.classList.add('status-dot--error');
      statusLabel.textContent = 'DISCONNECTED';
      $('#wsStatus').textContent = 'DOWN';
      $('#wsStatus').className = 'status-card__value status-card__value--error';
    } else {
      statusLabel.textContent = 'CONNECTING';
      $('#wsStatus').textContent = '...';
      $('#wsStatus').className = 'status-card__value';
    }
  }

  function connectWs() {
    if (ws) {
      ws.onclose = null;
      ws.close();
    }
    if (!TOKEN) {
      setConnectionStatus('error');
      return;
    }

    const wsBase = API_BASE.replace(/^http/, 'ws');
    const wsUrl = `${wsBase}/ws/approvals?token=${encodeURIComponent(TOKEN)}`;

    setConnectionStatus('connecting');

    try {
      ws = new WebSocket(wsUrl);
    } catch {
      setConnectionStatus('error');
      scheduleWsRetry();
      return;
    }

    ws.onopen = () => {
      wsRetries = 0;
      setConnectionStatus('connected');
    };

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        handleWsMessage(msg);
      } catch { /* ignore non-JSON */ }
    };

    ws.onerror = () => {
      setConnectionStatus('error');
    };

    ws.onclose = () => {
      setConnectionStatus('error');
      scheduleWsRetry();
    };
  }

  function scheduleWsRetry() {
    if (wsRetryTimer) clearTimeout(wsRetryTimer);
    if (wsRetries >= WS_MAX_RETRIES) return;
    wsRetries++;
    wsRetryTimer = setTimeout(connectWs, WS_RETRY_DELAY);
  }

  function handleWsMessage(msg) {
    // Server sends approval updates via WS
    if (msg.type === 'new_request' || msg.type === 'approval_update') {
      toast(`New access request: ${shortenPath(msg.data?.resolved_path || msg.data?.path || 'unknown')}`, 'info');
      loadApprovals();
    } else if (msg.type === 'decision') {
      loadApprovals();
    }
    // Fallback: treat any message as a signal to refresh
    else {
      loadApprovals();
    }
  }

  // ===========================================================
  //  TABS
  // ===========================================================

  $$('.nav__tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      $$('.nav__tab').forEach(t => {
        t.classList.remove('nav__tab--active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('nav__tab--active');
      tab.setAttribute('aria-selected', 'true');

      $$('.panel').forEach(p => {
        p.hidden = true;
        p.classList.remove('panel--active');
      });
      const panel = $(`#panel-${target}`);
      panel.hidden = false;
      panel.classList.add('panel--active');

      // Lazy load
      if (target === 'files') loadFileTree();
      if (target === 'audit') loadAudit();
      if (target === 'status') loadStatus();
    });
  });

  // ===========================================================
  //  APPROVALS
  // ===========================================================

  async function loadApprovals() {
    try {
      const data = await api('/approvals/');
      approvals = Array.isArray(data) ? data : (data.approvals || []);
      renderApprovals();
    } catch (err) {
      approvalList.innerHTML = '';
      emptyApprovals.style.display = '';
      approvalList.appendChild(emptyApprovals);
    }
  }

  function renderApprovals() {
    approvalList.innerHTML = '';

    let filtered = approvals;
    if (!showAll) {
      filtered = approvals.filter(a => a.status === 'pending');
    }

    // Sort: pending first, then by created_at desc
    filtered.sort((a, b) => {
      if (a.status === 'pending' && b.status !== 'pending') return -1;
      if (b.status === 'pending' && a.status !== 'pending') return 1;
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    });

    const pendingCount = approvals.filter(a => a.status === 'pending').length;
    if (pendingCount > 0) {
      pendingBadge.textContent = pendingCount;
      pendingBadge.hidden = false;
    } else {
      pendingBadge.hidden = true;
    }

    if (filtered.length === 0) {
      emptyApprovals.style.display = '';
      approvalList.appendChild(emptyApprovals);
      return;
    }

    emptyApprovals.style.display = 'none';

    filtered.forEach(approval => {
      const card = document.createElement('div');
      const statusClass = approval.status || 'pending';
      card.className = `approval-card approval-card--${statusClass}`;

      const path = approval.resolved_path || approval.path || 'unknown';
      const scope = approval.scope || 'file';
      const access = approval.access || approval.access_level || 'read';
      const reason = approval.reason || '';
      const created = approval.created_at ? formatTime(approval.created_at) : '';
      const expires = approval.expires_at ? formatTime(approval.expires_at) : '';

      card.innerHTML = `
        <div class="approval-card__top">
          <div class="approval-card__meta">
            <div class="approval-card__path">${escapeHtml(shortenPath(path))}</div>
            <div class="approval-card__tags">
              <span class="tag tag--scope">${escapeHtml(scope)}</span>
              <span class="tag tag--access">${escapeHtml(access)}</span>
              <span class="tag tag--status tag--${statusClass}">${escapeHtml(approval.status || 'pending')}</span>
            </div>
          </div>
        </div>
        ${reason ? `<div class="approval-card__reason">"${escapeHtml(reason)}"</div>` : ''}
        <div class="approval-card__time">
          ${created ? `Requested: ${created}` : ''}
          ${expires ? ` &middot; Expires: ${expires}` : ''}
        </div>
        <div class="approval-card__actions" id="actions-${approval.id}"></div>
      `;

      const actionsEl = card.querySelector(`#actions-${approval.id}`);

      if (approval.status === 'pending') {
        const approveBtn = createBtn('APPROVE', 'btn--approve', () => decideApproval(approval.id, 'approved'));
        const denyBtn = createBtn('DENY', 'btn--deny', () => decideApproval(approval.id, 'denied'));
        actionsEl.appendChild(approveBtn);
        actionsEl.appendChild(denyBtn);
      } else if (approval.status === 'approved') {
        const revokeBtn = createBtn('REVOKE', 'btn--revoke', () => revokeApproval(approval.id));
        actionsEl.appendChild(revokeBtn);
      }

      approvalList.appendChild(card);
    });
  }

  async function decideApproval(id, decision) {
    try {
      await api(`/approvals/${id}/decide`, {
        method: 'POST',
        body: JSON.stringify({ decision })
      });
      toast(`${decision === 'approved' ? 'Approved' : 'Denied'} access`, decision === 'approved' ? 'success' : 'error');
      loadApprovals();
    } catch (err) {
      toast(`Failed: ${err.message}`, 'error');
    }
  }

  async function revokeApproval(id) {
    try {
      await api(`/approvals/${id}`, { method: 'DELETE' });
      toast('Approval revoked', 'info');
      loadApprovals();
    } catch (err) {
      toast(`Revoke failed: ${err.message}`, 'error');
    }
  }

  $('#refreshApprovals').addEventListener('click', loadApprovals);
  $('#showAllApprovals').addEventListener('change', (e) => {
    showAll = e.target.checked;
    renderApprovals();
  });

  // ===========================================================
  //  FILE TREE
  // ===========================================================

  async function loadFileTree() {
    const depth = parseInt($('#depthSelect').value) || 3;
    try {
      fileTree.innerHTML = '<div class="skeleton skeleton--card"></div><div class="skeleton skeleton--card"></div>';
      const data = await api(`/files/tree?depth=${depth}`);
      renderTree(data);
    } catch (err) {
      fileTree.innerHTML = `<div class="empty-state">
        <div class="empty-state__icon">&#9888;</div>
        <div class="empty-state__text">Failed to load file tree</div>
        <div class="empty-state__sub">${escapeHtml(err.message)}</div>
      </div>`;
    }
  }

  function renderTree(data) {
    fileTree.innerHTML = '';
    const roots = Array.isArray(data) ? data : (data.roots || data.children || [data]);
    roots.forEach(root => {
      const el = buildTreeNode(root, true);
      fileTree.appendChild(el);
    });
  }

  function buildTreeNode(node, isRoot = false) {
    const container = document.createElement('div');
    container.className = `tree-node${isRoot ? ' tree-node--root' : ''}`;

    const isDir = node.is_dir || node.type === 'directory' || (node.children && node.children.length > 0);
    const hasChildren = node.children && node.children.length > 0;

    const item = document.createElement('div');
    item.className = 'tree-item';

    if (isDir && hasChildren) {
      const toggle = document.createElement('span');
      toggle.className = 'tree-item__toggle';
      toggle.textContent = '\u25B6';
      item.appendChild(toggle);

      const childrenContainer = document.createElement('div');
      childrenContainer.className = 'tree-children';

      node.children.forEach(child => {
        childrenContainer.appendChild(buildTreeNode(child));
      });

      toggle.addEventListener('click', () => {
        toggle.classList.toggle('tree-item__toggle--open');
        childrenContainer.classList.toggle('tree-children--open');
      });

      // Auto-expand roots
      if (isRoot) {
        toggle.classList.add('tree-item__toggle--open');
        childrenContainer.classList.add('tree-children--open');
      }

      const icon = document.createElement('span');
      icon.className = 'tree-item__icon tree-item__icon--dir';
      icon.textContent = '\u25A0';
      item.appendChild(icon);

      const name = document.createElement('span');
      name.className = 'tree-item__name tree-item__name--dir';
      name.textContent = node.name || node.path || 'root';
      item.appendChild(name);

      container.appendChild(item);
      container.appendChild(childrenContainer);
    } else {
      const spacer = document.createElement('span');
      spacer.style.width = '14px';
      spacer.style.display = 'inline-block';
      item.appendChild(spacer);

      const icon = document.createElement('span');
      icon.className = 'tree-item__icon tree-item__icon--file';
      icon.textContent = getFileIcon(node.name || '');
      item.appendChild(icon);

      const name = document.createElement('span');
      name.className = 'tree-item__name';
      name.textContent = node.name || node.path || '?';
      item.appendChild(name);

      if (node.language) {
        const lang = document.createElement('span');
        lang.className = 'tag tag--scope';
        lang.textContent = node.language;
        lang.style.marginLeft = '8px';
        item.appendChild(lang);
      }

      container.appendChild(item);
    }

    return container;
  }

  function getFileIcon(name) {
    const ext = name.split('.').pop().toLowerCase();
    const icons = {
      py: '\u{1F40D}', js: '\u26A1', ts: '\u{1F535}', json: '{}',
      md: '\u{1F4DD}', html: '\u{1F310}', css: '\u{1F3A8}', yml: '\u2699',
      yaml: '\u2699', toml: '\u2699', txt: '\u{1F4C4}', rs: '\u{1F980}',
      go: '\u{1F439}', java: '\u2615', rb: '\u{1F48E}', sh: '$',
      sql: '\u{1F4CA}', xml: '<>', lock: '\u{1F512}', env: '\u{1F6AB}'
    };
    return icons[ext] || '\u25CB';
  }

  $('#refreshTree').addEventListener('click', loadFileTree);
  $('#depthSelect').addEventListener('change', loadFileTree);

  // ===========================================================
  //  AUDIT LOG
  // ===========================================================

  async function loadAudit() {
    try {
      auditLog.innerHTML = '<div class="skeleton skeleton--line"></div>'.repeat(6);
      const data = await api('/audit/?limit=100');
      renderAudit(Array.isArray(data) ? data : (data.entries || []));
    } catch (err) {
      auditLog.innerHTML = `<div class="empty-state">
        <div class="empty-state__icon">&#9888;</div>
        <div class="empty-state__text">Failed to load audit log</div>
        <div class="empty-state__sub">${escapeHtml(err.message)}</div>
      </div>`;
    }
  }

  function renderAudit(entries) {
    auditLog.innerHTML = '';
    if (entries.length === 0) {
      auditLog.innerHTML = `<div class="empty-state">
        <div class="empty-state__icon">&#128220;</div>
        <div class="empty-state__text">No audit entries</div>
        <div class="empty-state__sub">File access events will be logged here</div>
      </div>`;
      return;
    }

    entries.forEach(entry => {
      const row = document.createElement('div');
      row.className = 'audit-entry';

      const actionClass = getActionClass(entry.action);

      row.innerHTML = `
        <span class="audit-entry__action audit-entry__action--${actionClass}">${escapeHtml(entry.action || '?')}</span>
        <span class="audit-entry__path">${escapeHtml(shortenPath(entry.path || entry.resolved_path || ''))}</span>
        <span class="audit-entry__time">${entry.timestamp ? formatTime(entry.timestamp) : ''}</span>
      `;

      auditLog.appendChild(row);
    });
  }

  function getActionClass(action) {
    if (!action) return 'request';
    const a = action.toLowerCase();
    if (a.includes('read')) return 'read';
    if (a.includes('write')) return 'write';
    if (a.includes('approv')) return 'approve';
    if (a.includes('den')) return 'deny';
    if (a.includes('revok')) return 'revoke';
    return 'request';
  }

  let auditFilterTimeout;
  $('#auditSearch').addEventListener('input', (e) => {
    clearTimeout(auditFilterTimeout);
    auditFilterTimeout = setTimeout(() => {
      const q = e.target.value.trim().toLowerCase();
      $$('.audit-entry', auditLog).forEach(el => {
        const path = el.querySelector('.audit-entry__path')?.textContent?.toLowerCase() || '';
        el.style.display = path.includes(q) || !q ? '' : 'none';
      });
    }, 200);
  });

  $('#refreshAudit').addEventListener('click', loadAudit);

  // ===========================================================
  //  STATUS
  // ===========================================================

  async function loadStatus() {
    try {
      const data = await api('/health');
      $('#serverStatus').textContent = 'ONLINE';
      $('#serverStatus').className = 'status-card__value status-card__value--ok';

      const roots = data.workspace_roots || data.roots || [];
      const workspaceItems = $('#workspaceItems');
      workspaceItems.innerHTML = '';

      roots.forEach(root => {
        const item = document.createElement('div');
        item.className = 'workspace-item';
        item.innerHTML = `<span class="workspace-item__icon">&#128193;</span><span>${escapeHtml(root)}</span>`;
        workspaceItems.appendChild(item);
      });

      if (roots.length === 0) {
        workspaceItems.innerHTML = '<div class="empty-state__sub">No workspace roots configured</div>';
      }

      // Active approvals count
      try {
        const appData = await api('/approvals/');
        const all = Array.isArray(appData) ? appData : (appData.approvals || []);
        const active = all.filter(a => a.status === 'approved').length;
        $('#activeCount').textContent = active;
      } catch {
        $('#activeCount').textContent = '?';
      }

    } catch (err) {
      $('#serverStatus').textContent = 'OFFLINE';
      $('#serverStatus').className = 'status-card__value status-card__value--error';
    }
  }

  $('#refreshStatus').addEventListener('click', loadStatus);

  // ===========================================================
  //  UTILITIES
  // ===========================================================

  function createBtn(text, className, handler) {
    const btn = document.createElement('button');
    btn.className = `btn ${className}`;
    btn.textContent = text;
    btn.addEventListener('click', handler);
    return btn;
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function shortenPath(path) {
    if (!path) return '';
    // Keep last 3 segments
    const parts = path.replace(/\\/g, '/').split('/');
    if (parts.length <= 4) return path;
    return '.../' + parts.slice(-3).join('/');
  }

  function formatTime(ts) {
    try {
      const d = new Date(ts);
      const now = new Date();
      const diff = now - d;

      if (diff < 60000) return 'just now';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;

      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) +
        ' ' + d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    } catch {
      return ts;
    }
  }

  function toast(message, type = 'info') {
    const el = document.createElement('div');
    el.className = `toast toast--${type}`;
    el.textContent = message;
    toastContainer.appendChild(el);

    setTimeout(() => {
      el.classList.add('toast--exit');
      setTimeout(() => el.remove(), 300);
    }, 3500);
  }

  function refreshAll() {
    loadApprovals();
    // Other panels load lazily on tab switch
  }

  // ===========================================================
  //  INIT
  // ===========================================================

  function init() {
    if (!TOKEN) {
      openTokenModal();
    } else {
      connectWs();
      refreshAll();
    }

    // Poll approvals every 15s as fallback
    setInterval(() => {
      if (TOKEN) loadApprovals();
    }, 15000);
  }

  init();

})();
