/**
 * nav.js — shared nav for your build dashboard
 *
 * Usage:
 *   1. Add <link rel="stylesheet" href="/nav.css"> in <head>
 *   2. Add <nav id="nav"></nav> in <body>
 *   3. Add <script src="/nav.js"></script> after the nav element
 *
 * Configure NAV_CONFIG below to match your project.
 */
(function () {

  // ── CONFIG — customize this ──────────────────────────────────────
  const NAV_CONFIG = {
    // Brand text shown in the top-left logo area.
    // Can be a single string or an object with parts for color split:
    //   { prefix: 'MY', accent: 'APP' }
    // If string: rendered as-is with --brand color on first word
    brand: { prefix: 'MY', accent: 'APP' },

    // Nav links
    links: [
      { href: '/',      label: 'Home' },
      { href: '/build', label: 'The Build' },
      // Add more pages here:
      // { href: '/roadmap', label: 'Roadmap' },
    ],

    // Top-right badge (e.g. your social handle)
    badge: {
      label: '@yourhandle ↗',
      href:  'https://x.com/yourhandle',
    },
  };
  // ────────────────────────────────────────────────────────────────

  const currentPath = window.location.pathname;

  // Build logo HTML
  let logoHtml;
  if (typeof NAV_CONFIG.brand === 'string') {
    logoHtml = `<span class="nav-logo-text">${NAV_CONFIG.brand}</span>`;
  } else {
    logoHtml = `<span class="nav-logo-prefix">${NAV_CONFIG.brand.prefix}</span><span class="nav-logo-accent">${NAV_CONFIG.brand.accent}</span>`;
  }

  // Build nav links HTML
  const navLinks = NAV_CONFIG.links
    .map(l => {
      const isActive = currentPath === l.href || (l.href !== '/' && currentPath.startsWith(l.href));
      return `<a href="${l.href}"${isActive ? ' class="active"' : ''}>${l.label}</a>`;
    })
    .join('');

  // Render nav
  const html = `
    <a href="/" class="nav-logo">${logoHtml}</a>
    <div class="nav-links">${navLinks}</div>
    <a href="${NAV_CONFIG.badge.href}" target="_blank" class="nav-badge">${NAV_CONFIG.badge.label}</a>
  `;

  const nav = document.getElementById('nav');
  if (nav) nav.innerHTML = html;

  // Scroll effect — adds background blur when scrolled
  window.addEventListener('scroll', () => {
    nav?.classList.toggle('scrolled', window.scrollY > 20);
  });

})();
