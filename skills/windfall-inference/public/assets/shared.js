/* Windfall Shared — nav + footer injection, mobile menu */
(function () {
  'use strict';

  var page = document.body.getAttribute('data-page') || '';
  var isDark = document.body.getAttribute('data-theme') === 'dark';

  // ---- Logo SVG (inline for nav and footer) ----
  var logoSvg = '<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">'
    + '<path d="M24 2L44 24L24 46L4 24Z" stroke="currentColor" stroke-width="2" fill="none"/>'
    + '<path d="M24 10L36 24L24 38L12 24Z" stroke="currentColor" stroke-width="1.2" fill="none" opacity="0.5"/>'
    + '<path d="M14 20C18 18 22 22 26 18C30 14 34 20 38 18" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
    + '<path d="M10 26C14 24 18 28 22 24C26 20 30 26 34 24" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>'
    + '<path d="M14 32C18 30 22 34 26 30C30 26 34 32 38 30" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.6"/>'
    + '</svg>';

  // Ecofrontiers diamond (smaller, for footer)
  var ecoLogo = '<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">'
    + '<path d="M24 4L42 24L24 44L6 24Z" stroke="currentColor" stroke-width="2" fill="none"/>'
    + '<path d="M24 12L36 24L24 36L12 24Z" stroke="currentColor" stroke-width="1.2" fill="none" opacity="0.4"/>'
    + '</svg>';

  // Social SVGs
  var xIcon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>';
  var linkedinIcon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>';

  // ---- Helper: active link class ----
  function linkClass(linkPage) {
    return linkPage === page ? ' active' : '';
  }

  // ---- Build navigation HTML ----
  var navHtml = '<nav class="wf-nav" role="navigation">'
    + '<div class="wf-nav-inner">'
    +   '<div class="wf-nav-left">'
    +     '<a href="/" class="wf-nav-logo">'
    +       logoSvg
    +       '<div class="wf-nav-brand">'
    +         '<span class="wf-wordmark">Windfall</span>'
    +         '<span class="wf-byline">by Ecofrontiers</span>'
    +       '</div>'
    +     '</a>'
    +   '</div>'
    +   '<div class="wf-nav-right">'
    +     '<div class="wf-nav-links">'
    +       '<a href="/#how"' + linkClass('how') + '>How it works</a>'
    +       '<a href="/#savings"' + linkClass('savings') + '>Pricing</a>'
    +       '<a href="/topup"' + linkClass('topup') + '>Top Up</a>'
    +     '</div>'
    +     '<a href="/dashboard" class="wf-nav-cta">Dashboard</a>'
    +   '</div>'
    +   '<button class="wf-hamburger" aria-label="Toggle menu" aria-expanded="false">'
    +     '<span></span><span></span><span></span>'
    +   '</button>'
    + '</div>'
    + '</nav>'
    + '<div class="wf-mobile-menu">'
    +   '<a href="/#how">How it works</a>'
    +   '<a href="/#savings">Pricing</a>'
    +   '<a href="/topup"' + linkClass('topup') + '>Top Up</a>'
    +   '<a href="/dashboard">Dashboard</a>'
    + '</div>';

  // ---- Build footer HTML ----
  var footerHtml = '<footer class="wf-footer">'
    + '<div class="wf-footer-inner">'
    +   '<div class="wf-footer-left">'
    +     '<span>&copy; ' + new Date().getFullYear() + ' Ecofrontiers SARL</span>'
    +   '</div>'
    +   '<div class="wf-footer-center">'
    +     '<a href="/terms">Terms</a>'
    +     '<span class="wf-footer-dot"></span>'
    +     '<a href="/privacy">Privacy</a>'
    +     '<span class="wf-footer-dot"></span>'
    +     '<a href="/imprint">Imprint</a>'
    +     '<span class="wf-footer-dot"></span>'
    +     '<a href="/status"><span class="wf-status-dot"></span>API Status</a>'
    +   '</div>'
    +   '<div class="wf-footer-right">'
    +     '<a href="https://paragraph.com/@ecofrontiers" target="_blank" rel="noopener">Blog</a>'
    +     '<a href="https://x.com/ecofrontiers" target="_blank" rel="noopener" aria-label="X">' + xIcon + '</a>'
    +     '<a href="https://www.linkedin.com/company/ecofrontiers" target="_blank" rel="noopener" aria-label="LinkedIn">' + linkedinIcon + '</a>'
    +   '</div>'
    + '</div>'
    + '</footer>';

  // ---- Inject ----
  // Nav: insert at top of body
  document.body.insertAdjacentHTML('afterbegin', navHtml);

  // Footer: insert at bottom of body
  document.body.insertAdjacentHTML('beforeend', footerHtml);

  // ---- Favicon: replace emoji with SVG logo ----
  var existingIcon = document.querySelector('link[rel="icon"]');
  if (existingIcon) existingIcon.remove();
  var iconLink = document.createElement('link');
  iconLink.rel = 'icon';
  iconLink.type = 'image/svg+xml';
  iconLink.href = '/assets/windfall-logo.svg';
  document.head.appendChild(iconLink);

  // ---- Mobile menu toggle ----
  var hamburger = document.querySelector('.wf-hamburger');
  var mobileMenu = document.querySelector('.wf-mobile-menu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open');
      var isOpen = hamburger.classList.contains('open');
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // ---- Live status dot (footer) ----
  // Fetches /status and colors the dot based on system health
  function updateStatusDot() {
    var dot = document.querySelector('.wf-footer .wf-status-dot');
    if (!dot) return;
    fetch('/status')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var status = data.system && data.system.status;
        if (status === 'healthy') {
          dot.style.background = '#4ade80';
          dot.style.boxShadow = '0 0 4px rgba(74, 222, 128, 0.6)';
        } else if (status === 'degraded') {
          dot.style.background = '#facc15';
          dot.style.boxShadow = '0 0 4px rgba(250, 204, 21, 0.6)';
          dot.style.animation = 'none';
        } else {
          dot.style.background = '#f87171';
          dot.style.boxShadow = '0 0 4px rgba(248, 113, 113, 0.6)';
          dot.style.animation = 'none';
        }
      })
      .catch(function () {
        dot.style.background = '#f87171';
        dot.style.boxShadow = '0 0 4px rgba(248, 113, 113, 0.6)';
        dot.style.animation = 'none';
      });
  }
  updateStatusDot();
  setInterval(updateStatusDot, 60000);
})();
