/* ═══════════════════════════════════════════════════════════════
   EXOSKELETONS — Shared UI Components
   Navigation, footer, cards, loading states, trust badges
   ═══════════════════════════════════════════════════════════════ */

const ExoUI = {

  // ── Navigation ──
  renderNav(activePage) {
    const pages = [
      { href: 'index.html', label: 'Home', id: 'index.html' },
      { href: 'mint.html', label: 'Mint', id: 'mint.html' },
      { href: 'explorer.html', label: 'Explorer', id: 'explorer.html' },
      { href: 'trust.html', label: 'Trust', id: 'trust.html' },
      { href: 'messages.html', label: 'Messages', id: 'messages.html' },
      { href: 'modules.html', label: 'Modules', id: 'modules.html' },
      { href: 'docs.html', label: 'Docs', id: 'docs.html' },
    ];

    const links = pages.map(p =>
      `<a href="${p.href}" class="nav__link${p.id === activePage ? ' nav__link--active' : ''}">${p.label}</a>`
    ).join('');

    return `<nav class="nav"><div class="nav__inner">
      <a href="index.html" class="nav__logo">EXOSKELETONS</a>
      ${links}
      <div class="nav__spacer"></div>
      <button class="nav__wallet nav__wallet--disconnected" id="navWalletBtn" onclick="ExoUI.onWalletClick()">Connect</button>
    </div></nav>`;
  },

  // ── Footer ──
  renderFooter() {
    return `<footer class="footer">
      CC0 — No rights reserved<br>
      Built by <a href="https://github.com/Potdealer/exoskeletons" target="_blank">potdealer &amp; Ollie</a><br>
      <span class="text-mono">Core: <a href="https://basescan.org/address/${ExoCore.CONTRACTS.core}" target="_blank">${ExoCore.truncAddr(ExoCore.CONTRACTS.core)}</a> · Registry: <a href="https://basescan.org/address/${ExoCore.CONTRACTS.registry}" target="_blank">${ExoCore.truncAddr(ExoCore.CONTRACTS.registry)}</a></span><br>
      <span class="text-gold text-mono">Base (8453)</span>
    </footer>`;
  },

  // ── Wallet Button Updates ──
  updateWalletButton(account) {
    const btn = document.getElementById('navWalletBtn');
    if (!btn) return;
    if (account) {
      btn.textContent = ExoCore.truncAddr(account);
      btn.classList.remove('nav__wallet--disconnected');
    } else {
      btn.textContent = 'Connect';
      btn.classList.add('nav__wallet--disconnected');
    }
  },

  async onWalletClick() {
    if (ExoCore.account) return;
    try {
      await ExoCore.connectWallet();
    } catch (e) {
      console.error('Wallet connect error:', e);
    }
  },

  // ── Token Card ──
  renderTokenCard(token, svgContent) {
    const genesis = token.genesis ? '<span class="token-card__genesis"></span>' : '';
    const name = token.name ? `<div class="token-card__name">${ExoCore.escHtml(token.name)}</div>` : '';
    const svg = svgContent
      ? `<div class="token-card__svg">${svgContent}</div>`
      : `<div class="token-card__svg skeleton" style="aspect-ratio:1"></div>`;

    return `<a href="token.html#${token.id}" class="token-card">
      ${svg}
      <div class="token-card__info">
        <div class="token-card__id">${genesis}#${token.id}</div>
        ${name}
        <div class="token-card__rep">REP ${ExoCore.formatScore(token.repScore || 0)}</div>
      </div>
    </a>`;
  },

  // ── Stat Box ──
  renderStatBox(value, label) {
    return `<div class="stat-box">
      <div class="stat-box__value">${value}</div>
      <div class="stat-box__label">${label}</div>
    </div>`;
  },

  // ── Trust Badge ──
  renderTrustBadge(score) {
    const tier = ExoCore.getTrustTier(score);
    return `<span class="badge trust-badge ${tier.class}">${tier.name}</span>`;
  },

  // ── Loading Skeleton Card ──
  renderSkeletonCard() {
    return `<div class="token-card" style="pointer-events:none">
      <div class="skeleton" style="aspect-ratio:1;border-radius:var(--radius-sm)"></div>
      <div class="token-card__info">
        <div class="skeleton" style="height:14px;width:50px;margin-top:8px;border-radius:3px"></div>
      </div>
    </div>`;
  },

  // ── Pagination ──
  renderPagination(currentPage, totalPages, onPageFn) {
    if (totalPages <= 1) return '';
    let html = '<div class="pagination">';
    if (currentPage > 1) html += `<a class="page-btn" href="#" onclick="${onPageFn}(${currentPage - 1});return false">Prev</a>`;
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, currentPage + 2);
    if (start > 1) html += `<a class="page-btn" href="#" onclick="${onPageFn}(1);return false">1</a>`;
    if (start > 2) html += '<span class="page-btn" style="border:none;cursor:default">...</span>';
    for (let p = start; p <= end; p++) {
      html += `<a class="page-btn${p === currentPage ? ' page-btn--active' : ''}" href="#" onclick="${onPageFn}(${p});return false">${p}</a>`;
    }
    if (end < totalPages - 1) html += '<span class="page-btn" style="border:none;cursor:default">...</span>';
    if (end < totalPages) html += `<a class="page-btn" href="#" onclick="${onPageFn}(${totalPages});return false">${totalPages}</a>`;
    if (currentPage < totalPages) html += `<a class="page-btn" href="#" onclick="${onPageFn}(${currentPage + 1});return false">Next</a>`;
    html += '</div>';
    return html;
  },

  // ── Status Message ──
  showStatus(elementId, msg, type) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = msg;
    el.className = 'status status--' + type;
    el.style.display = '';
  },

  hideStatus(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.style.display = 'none';
  },

  // ── Initialize page (nav + footer + wallet listener) ──
  initPage(activePage) {
    // Insert nav
    const navTarget = document.getElementById('app-nav');
    if (navTarget) navTarget.outerHTML = this.renderNav(activePage);

    // Insert footer
    const footerTarget = document.getElementById('app-footer');
    if (footerTarget) footerTarget.outerHTML = this.renderFooter();

    // Listen for wallet changes
    window.addEventListener('exo:accountChanged', (e) => {
      this.updateWalletButton(e.detail.account);
    });

    // Auto-connect
    ExoCore.onReady(() => {
      ExoCore.autoConnect();
    });
  },
};

window.ExoUI = ExoUI;
