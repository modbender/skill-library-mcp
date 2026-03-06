// cdp.js - CDP wrapper using fetch (no shell)
const CDP_URL = 'http://localhost:9222/json';

function validateHttpUrl(input) {
  if (!input || typeof input !== 'string') throw new Error('Missing url');
  const trimmed = input.trim();
  if (!trimmed) throw new Error('Missing url');

  let parsed;
  try {
    parsed = new URL(trimmed);
  } catch {
    throw new Error(`Invalid URL: ${input}`);
  }

  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error(`Blocked URL scheme: ${parsed.protocol} (only http/https allowed)`);
  }

  return parsed.toString();
}

async function status() {
  const resp = await fetch(CDP_URL);
  if (!resp.ok) throw new Error(`CDP error: ${resp.status}`);
  return resp.json();
}

async function listTabs() {
  const resp = await fetch(`${CDP_URL}/list`);
  if (!resp.ok) throw new Error(`CDP error: ${resp.status}`);
  return resp.json();
}

async function newTab(url) {
  const safeUrl = validateHttpUrl(url);
  const payload = JSON.stringify({ url: safeUrl });
  const resp = await fetch(`${CDP_URL}/new`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
  });
  if (!resp.ok) throw new Error(`CDP error: ${resp.status}`);
  return resp.json();
}

async function gotoTab(tabId, url) {
  const safeId = String(tabId).replace(/[^A-Za-z0-9_-]/g, '');
  const safeUrl = validateHttpUrl(url);
  const payload = JSON.stringify({ url: safeUrl });
  const resp = await fetch(`${CDP_URL}/runtime/activate/${safeId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
  });
  if (!resp.ok) throw new Error(`CDP error: ${resp.status}`);
  return resp.json();
}

function evaluate(tabId, js) {
  // Note: For full CDP eval, use pw.js instead
  return null;
}

// CLI for bin scripts
if (require.main === module) {
  const args = process.argv.slice(2);
  const cmd = args[0];
  (async () => {
    let out;
    switch (cmd) {
      case 'status':
      case 'tabs':
        out = cmd === 'tabs' ? await listTabs() : await status();
        break;
      case 'new':
        if (!args[1]) throw new Error('Usage: node cdp.js new <url>');
        out = await newTab(args[1]);
        break;
      case 'goto':
        if (!args[1] || !args[2]) throw new Error('Usage: node cdp.js goto <tabId> <url>');
        out = await gotoTab(args[1], args[2]);
        break;
      default:
        throw new Error(`Unknown command: ${cmd}`);
    }
    console.log(JSON.stringify(out));
  })().catch(err => {
    console.error(err.message || err);
    process.exit(1);
  });
} else {
  module.exports = { status, listTabs, newTab, gotoTab, evaluate };
}
