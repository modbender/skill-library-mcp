/**
 * Exoskeletons — Cloudflare Worker
 * Routes exoagent.xyz to storedon.net pages
 */

const OPERATOR = '0x2460F6C6CA04DD6a73E9B5535aC67Ac48726c09b';
const BASE = `https://storedon.net/net/8453/storage/load/${OPERATOR}`;

const ROUTES = {
  '/':               'exo-home',
  '/mint':           'exo-mint',
  '/explorer':       'exo-explorer',
  '/token':          'exo-token',
  '/messages':       'exo-messages',
  '/modules':        'exo-modules',
  '/trust':          'exo-trust',
  '/docs':           'exo-docs',
  '/guide':          'exo-guide',
  '/minting-guide':  'exo-minting-guide',
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    let path = url.pathname.replace(/\/+$/, '') || '/';

    const key = ROUTES[path];
    if (!key) {
      // Try without trailing slash or fallback to home
      return Response.redirect(`https://${url.hostname}/`, 302);
    }

    // Fetch from storedon.net and serve as HTML
    const storeUrl = `${BASE}/${key}`;
    const response = await fetch(storeUrl);
    const html = await response.text();

    return new Response(html, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=300',
        'X-Content-Type-Options': 'nosniff',
      },
    });
  },
};
