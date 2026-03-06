#!/usr/bin/env node
/**
 * Exoskeletons — Build self-contained HTML pages for Net Protocol upload
 * Inlines shared CSS + JS, converts cross-page links to absolute storedon.net URLs
 */

const fs = require('fs');
const path = require('path');

const SITE_DIR = path.join(__dirname, 'site');
const DIST_DIR = path.join(__dirname, 'dist');
const SHARED_DIR = path.join(SITE_DIR, 'shared');

const OPERATOR = '0x2460F6C6CA04DD6a73E9B5535aC67Ac48726c09b';
const DOMAIN = 'https://exoagent.xyz';
const STOREDON_BASE = `https://storedon.net/net/8453/storage/load/${OPERATOR}/`;

// Pages to process (skip gallery.html — it's deprecated)
const PAGES = {
  'index.html':         'exo-home',
  'mint.html':          'exo-mint',
  'explorer.html':      'exo-explorer',
  'token.html':         'exo-token',
  'messages.html':      'exo-messages',
  'modules.html':       'exo-modules',
  'trust.html':         'exo-trust',
  'docs.html':          'exo-docs',
  'guide.html':         'exo-guide',
  'minting-guide.html': 'exo-minting-guide',
};

// Clean URL paths for the domain
const DOMAIN_PATHS = {
  'index.html':         '/',
  'mint.html':          '/mint',
  'explorer.html':      '/explorer',
  'token.html':         '/token',
  'messages.html':      '/messages',
  'modules.html':       '/modules',
  'trust.html':         '/trust',
  'docs.html':          '/docs',
  'guide.html':         '/guide',
  'minting-guide.html': '/minting-guide',
};

// Read shared resources
const cssContent = fs.readFileSync(path.join(SHARED_DIR, 'exo-style.css'), 'utf8');
const coreJsContent = fs.readFileSync(path.join(SHARED_DIR, 'exo-core.js'), 'utf8');
const uiJsContent = fs.readFileSync(path.join(SHARED_DIR, 'exo-ui.js'), 'utf8');

// Create dist directory
if (!fs.existsSync(DIST_DIR)) fs.mkdirSync(DIST_DIR);

// Build URL map for cross-page link replacement
const linkMap = {};
for (const [file, path] of Object.entries(DOMAIN_PATHS)) {
  linkMap[file] = path === '/' ? DOMAIN + '/' : DOMAIN + path;
}

function replacePageLinks(html) {
  let result = html;

  // Replace href="page.html" and href="page.html#..." patterns
  for (const [file, url] of Object.entries(linkMap)) {
    // Escape dots for regex
    const escaped = file.replace('.', '\\.');

    // href="page.html" (exact, no hash)
    result = result.replace(new RegExp(`href="${escaped}"`, 'g'), `href="${url}"`);

    // href="page.html#..." (with hash fragment — keep the fragment)
    result = result.replace(new RegExp(`href="${escaped}#`, 'g'), `href="${url}#`);

    // href='page.html' (single quotes)
    result = result.replace(new RegExp(`href='${escaped}'`, 'g'), `href='${url}'`);
    result = result.replace(new RegExp(`href='${escaped}#`, 'g'), `href='${url}#`);
  }

  return result;
}

function replaceJsPageLinks(js) {
  let result = js;

  for (const [file, url] of Object.entries(linkMap)) {
    // In JS template literals and strings: 'page.html', "page.html"
    // Handle: href: 'page.html', href="page.html#${...}"
    const escaped = file.replace('.', '\\.');

    // JS string href construction: href="page.html# or href="page.html"
    result = result.replace(new RegExp(`"${escaped}#`, 'g'), `"${url}#`);
    result = result.replace(new RegExp(`"${escaped}"`, 'g'), `"${url}"`);
    result = result.replace(new RegExp(`'${escaped}'`, 'g'), `'${url}'`);
    result = result.replace(new RegExp(`'${escaped}#`, 'g'), `'${url}#`);
  }

  return result;
}

let totalSize = 0;

for (const [file, key] of Object.entries(PAGES)) {
  const filePath = path.join(SITE_DIR, file);
  if (!fs.existsSync(filePath)) {
    console.log(`  SKIP ${file} (not found)`);
    continue;
  }

  let html = fs.readFileSync(filePath, 'utf8');

  // 1. Replace CSS link with inline <style>
  html = html.replace(
    '<link rel="stylesheet" href="shared/exo-style.css">',
    `<style>\n${cssContent}\n</style>`
  );

  // 2. Replace exo-core.js script with inline <script>
  //    Handle the JS links BEFORE inlining
  const modifiedCoreJs = replaceJsPageLinks(coreJsContent);
  html = html.replace(
    '<script src="shared/exo-core.js"></script>',
    `<script>\n${modifiedCoreJs}\n</script>`
  );

  // 3. Replace exo-ui.js script with inline <script>
  const modifiedUiJs = replaceJsPageLinks(uiJsContent);
  html = html.replace(
    '<script src="shared/exo-ui.js"></script>',
    `<script>\n${modifiedUiJs}\n</script>`
  );

  // 4. Replace cross-page links in the HTML body
  html = replacePageLinks(html);

  // 5. Also replace links in any inline <script> blocks (page-specific JS)
  //    This handles things like: href="token.html#${tokenId}" in mint.html's inline script
  html = html.replace(/<script>([\s\S]*?)<\/script>/g, (match, scriptContent) => {
    // Don't re-process the already-inlined shared scripts (they're already done)
    // But DO process the page's own inline scripts
    const modified = replaceJsPageLinks(scriptContent);
    return `<script>${modified}</script>`;
  });

  // Write to dist
  const outPath = path.join(DIST_DIR, `${key}.html`);
  fs.writeFileSync(outPath, html);
  const size = Buffer.byteLength(html, 'utf8');
  totalSize += size;
  console.log(`  ${key}.html — ${(size / 1024).toFixed(1)}KB`);
}

console.log(`\nTotal: ${(totalSize / 1024).toFixed(1)}KB across ${Object.keys(PAGES).length} pages`);
console.log(`Output: ${DIST_DIR}/`);
console.log(`\nUpload with:`);
console.log(`  source .env`);
for (const [file, key] of Object.entries(PAGES)) {
  const label = file.replace('.html', '').replace('-', ' ');
  console.log(`  npx @net-protocol/cli@latest storage upload --file dist/${key}.html --key "${key}" --text "Exoskeletons ${label}" --private-key $PRIVATE_KEY --chain-id 8453`);
}
