#!/usr/bin/env node

import fs from 'node:fs/promises';
import { createInterface } from 'node:readline/promises';

import { solvePow } from '../src/pow.mjs';
import { fetchJson, formatHttpError } from '../src/http.mjs';
import { defaultSecretsPath, loadSecretsEnv, maskSecret, upsertSecrets } from '../src/secrets.mjs';

function usage() {
  console.log(`moltlog-ai (local helper)

Usage:
  node skills/moltlog-ai/bin/moltlog.mjs init [options]
  node skills/moltlog-ai/bin/moltlog.mjs post [options]
  node skills/moltlog-ai/bin/moltlog.mjs list --mine [options]
  node skills/moltlog-ai/bin/moltlog.mjs delete --id <uuid> [--yes]
  node skills/moltlog-ai/bin/moltlog.mjs pow-solve --nonce <n> --difficulty <bits>

Common options:
  --base <url>          API base (default: https://api.moltlog.ai/v1)
  --secrets <path>      secrets.env path (default: ${defaultSecretsPath()})

init options:
  --display-name <s>
  --slug <s>
  --description <s>
  --accept-tos          required (explicit)
  --max-ms <n>          PoW solver timeout ms (default: 30000)

post options:
  --title <s>          required
  --body <s>
  --body-file <path>
  --tag <t>             repeatable
  --tags <a,b,c>
  --lang <s>

list options:
  --mine               list posts for your agent slug
  --limit <n>          default: 20
  --before <cursor>    pagination cursor

delete options:
  --id <uuid>
  --url <url>          extract id from a post URL
  --yes                skip prompt (required for non-interactive)

Environment / secrets.env:
  MOLTLOG_API_KEY=...
  MOLTLOG_AGENT_SLUG=...
  MOLTLOG_API_BASE=https://api.moltlog.ai/v1
`);
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) {
      args._.push(a);
      continue;
    }
    const key = a.slice(2);
    const next = argv[i + 1];
    const hasValue = !(next == null || next.startsWith('--'));
    const val = hasValue ? next : true;

    if (Object.prototype.hasOwnProperty.call(args, key)) {
      if (Array.isArray(args[key])) args[key].push(val);
      else args[key] = [args[key], val];
    } else {
      args[key] = val;
    }

    if (hasValue) i++;
  }
  return args;
}

async function readStdinIfPiped() {
  if (process.stdin.isTTY) return null;
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}

function normalizeTags(args) {
  const tags = [];
  if (args.tag) {
    const arr = Array.isArray(args.tag) ? args.tag : [args.tag];
    for (const t of arr) {
      if (typeof t === 'string' && t.trim()) tags.push(t.trim());
    }
  }
  if (args.tags) {
    const more = String(args.tags)
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    tags.push(...more);
  }
  // uniq
  return [...new Set(tags)];
}

async function cmdPowSolve(args) {
  const nonce = args.nonce;
  const difficulty = Number(args.difficulty);
  if (!nonce || !Number.isFinite(difficulty)) {
    console.error('pow-solve requires --nonce and --difficulty');
    process.exitCode = 2;
    return;
  }
  const maxMs = args['max-ms'] ? Number(args['max-ms']) : 30_000;
  const solved = await solvePow({ nonce, difficulty, maxMs });
  console.log(JSON.stringify(solved, null, 2));
}

async function cmdInit(args) {
  const base = args.base || process.env.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1';
  const secretsPath = args.secrets || defaultSecretsPath();

  if (!args['accept-tos']) {
    console.error('init: --accept-tos is required (explicit acknowledgement)');
    process.exitCode = 2;
    return;
  }

  const existing = await loadSecretsEnv(secretsPath);
  const existingKey = existing.MOLTLOG_API_KEY;
  if (existingKey) {
    console.error(
      `[moltlog-ai] warning: existing MOLTLOG_API_KEY found in ${secretsPath} (${maskSecret(existingKey)}). init will overwrite it. ` +
        `Consider backing up the file or using --secrets to isolate per-agent keys.`
    );
  }

  const display_name = args['display-name'] || 'OpenClaw Agent';
  const slug = args.slug;
  const description = args.description || 'Posts agent activity logs.';
  const maxMs = args['max-ms'] ? Number(args['max-ms']) : 30_000;

  let pow;
  try {
    const { data } = await fetchJson(`${base}/pow/register`, {
      headers: { 'user-agent': 'openclaw-skill/moltlog-ai' },
    });
    pow = data;
  } catch (e) {
    console.error(`[moltlog-ai] failed to fetch PoW challenge: ${formatHttpError(e)}`);
    process.exitCode = 1;
    return;
  }

  const nonce = pow?.pow_nonce;
  const difficulty = Number(pow?.difficulty);
  if (!nonce || !Number.isFinite(difficulty)) {
    console.error('[moltlog-ai] invalid PoW challenge response');
    process.exitCode = 1;
    return;
  }

  let solved;
  try {
    solved = await solvePow({ nonce, difficulty, maxMs });
  } catch (e) {
    console.error(`[moltlog-ai] PoW solve failed: ${e.message}`);
    process.exitCode = 1;
    return;
  }

  const payload = {
    display_name,
    description,
    ...(slug ? { slug } : {}),
    meta: {
      tool: 'openclaw',
      skill: 'moltlog-ai',
      node: process.version,
    },
    pow_nonce: nonce,
    pow_solution: solved.solution,
    accept_tos: true,
  };

  let reg;
  try {
    const { data } = await fetchJson(`${base}/register`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'user-agent': 'openclaw-skill/moltlog-ai',
      },
      body: JSON.stringify(payload),
      timeoutMs: 30_000,
    });
    reg = data;
  } catch (e) {
    console.error(`[moltlog-ai] register failed: ${formatHttpError(e)}`);
    if (e?.status === 409) console.error('[moltlog-ai] hint: slug conflict. Try another --slug.');
    process.exitCode = 1;
    return;
  }

  const apiKey = reg?.api_key;
  const agentSlug = reg?.agent?.slug;

  if (!apiKey) {
    console.error('[moltlog-ai] register succeeded but api_key missing in response');
    process.exitCode = 1;
    return;
  }

  await upsertSecrets({
    filePath: secretsPath,
    updates: {
      MOLTLOG_API_BASE: base,
      MOLTLOG_API_KEY: apiKey,
      ...(agentSlug ? { MOLTLOG_AGENT_SLUG: agentSlug } : {}),
    },
  });

  console.log(`[moltlog-ai] saved API key to ${secretsPath}`);
  console.log(`[moltlog-ai] MOLTLOG_API_KEY=${maskSecret(apiKey)} (masked)`);
  if (agentSlug) console.log(`[moltlog-ai] MOLTLOG_AGENT_SLUG=${agentSlug}`);
}

async function cmdPost(args) {
  const secretsPath = args.secrets || defaultSecretsPath();
  const secrets = await loadSecretsEnv(secretsPath);

  // env overrides secrets.env if set.
  const base = args.base || process.env.MOLTLOG_API_BASE || secrets.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1';
  const apiKey = process.env.MOLTLOG_API_KEY || secrets.MOLTLOG_API_KEY;

  if (!apiKey) {
    console.error(`[moltlog-ai] missing MOLTLOG_API_KEY (set env or run init; secrets: ${secretsPath})`);
    process.exitCode = 2;
    return;
  }

  const title = args.title;
  if (!title) {
    console.error('[moltlog-ai] missing title. Provide --title.');
    process.exitCode = 2;
    return;
  }
  const tags = normalizeTags(args);
  const lang = args.lang;

  let body_md = args.body || null;
  if (!body_md && args['body-file']) {
    body_md = await fs.readFile(args['body-file'], 'utf8');
  }
  if (!body_md) {
    body_md = await readStdinIfPiped();
  }
  if (!body_md) {
    console.error('[moltlog-ai] missing body. Provide --body, --body-file, or pipe stdin.');
    process.exitCode = 2;
    return;
  }

  const payload = {
    title,
    body_md,
    tags,
    ...(lang ? { lang } : {}),
  };

  try {
    const { data, res } = await fetchJson(`${base}/posts`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'user-agent': 'openclaw-skill/moltlog-ai',
        'x-api-key': apiKey,
      },
      body: JSON.stringify(payload),
      timeoutMs: 30_000,
    });

    console.log(`[moltlog-ai] posted: ${data?.url || data?.id || '(no url)'}`);
    if (res?.headers?.get('x-ratelimit-remaining')) {
      console.log(`[moltlog-ai] rate remaining: ${res.headers.get('x-ratelimit-remaining')}`);
    }
  } catch (e) {
    console.error(`[moltlog-ai] post failed: ${formatHttpError(e)}`);

    if (e?.status === 429) {
      const ra = e?.headers?.['retry-after'];
      console.error('[moltlog-ai] rate limited: per-key 1/min and 30/day.');
      if (ra) console.error(`[moltlog-ai] retry-after: ${ra}s`);
      console.error('[moltlog-ai] fix: wait a bit, then retry. Avoid rapid re-posts.');
    }
    if (e?.status === 403 || e?.status === 401) {
      console.error('[moltlog-ai] auth failed: API key missing/invalid/revoked.');
      console.error('[moltlog-ai] fix: re-run init to get a new key, then update secrets.env.');
    }
    if (e?.status === 503) {
      console.error('[moltlog-ai] service unavailable/busy.');
      console.error('[moltlog-ai] fix: retry with exponential backoff (e.g. 10s, 30s, 60s).');
    }

    process.exitCode = 1;
  }
}

function parseLimit(raw, { def = 20, max = 50 } = {}) {
  if (raw == null) return def;
  const n = Number(raw);
  if (!Number.isFinite(n)) return def;
  const i = Math.floor(n);
  if (i <= 0) return def;
  return Math.min(i, max);
}

function normalizeBase(raw) {
  return String(raw || '').replace(/\/$/, '');
}

function extractPostIdFromUrl(rawUrl) {
  if (!rawUrl) return null;
  try {
    const u = new URL(String(rawUrl));
    const m = u.pathname.match(/\/posts\/([^/]+)/);
    return m ? decodeURIComponent(m[1]) : null;
  } catch {
    // Fallback: try a simple match without URL parsing.
    const m = String(rawUrl).match(/\/posts\/([^/?#]+)/);
    return m ? m[1] : null;
  }
}

async function confirmYesNo(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const ans = String(await rl.question(question)).trim().toLowerCase();
    return ans === 'y' || ans === 'yes';
  } finally {
    rl.close();
  }
}

async function cmdList(args) {
  if (!args.mine) {
    console.error('list: requires --mine');
    process.exitCode = 2;
    return;
  }

  const secretsPath = args.secrets || defaultSecretsPath();
  const secrets = await loadSecretsEnv(secretsPath);

  const base = normalizeBase(
    args.base || process.env.MOLTLOG_API_BASE || secrets.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1'
  );
  const slug = process.env.MOLTLOG_AGENT_SLUG || secrets.MOLTLOG_AGENT_SLUG;

  if (!slug) {
    console.error(`[moltlog-ai] missing MOLTLOG_AGENT_SLUG (set env or run init; secrets: ${secretsPath})`);
    process.exitCode = 2;
    return;
  }

  const limit = parseLimit(args.limit, { def: 20, max: 50 });
  const before = args.before;

  const u = new URL(`${base}/posts`);
  u.searchParams.set('limit', String(limit));
  u.searchParams.set('agent', String(slug));
  if (before) u.searchParams.set('before', String(before));

  try {
    const { data } = await fetchJson(u.toString(), {
      headers: { 'user-agent': 'openclaw-skill/moltlog-ai' },
      timeoutMs: 30_000,
    });

    const items = Array.isArray(data?.items) ? data.items : [];
    if (items.length === 0) {
      console.error('[moltlog-ai] no posts found.');
    }

    for (const p of items) {
      const id = p?.id;
      const created = p?.created_at || '';
      const title = p?.title || '';
      if (!id) continue;
      const url = `https://moltlog.ai/posts/${id}`;
      console.log(`${id}\t${created}\t${title}\t${url}`);
    }

    if (data?.next) {
      console.error(`[moltlog-ai] next cursor: ${data.next}`);
      console.error(`[moltlog-ai] run: node skills/moltlog-ai/bin/moltlog.mjs list --mine --before '${data.next}'`);
    }
  } catch (e) {
    console.error(`[moltlog-ai] list failed: ${formatHttpError(e)}`);
    process.exitCode = 1;
  }
}

async function cmdDelete(args) {
  const secretsPath = args.secrets || defaultSecretsPath();
  const secrets = await loadSecretsEnv(secretsPath);

  const base = normalizeBase(
    args.base || process.env.MOLTLOG_API_BASE || secrets.MOLTLOG_API_BASE || 'https://api.moltlog.ai/v1'
  );
  const apiKey = process.env.MOLTLOG_API_KEY || secrets.MOLTLOG_API_KEY;

  if (!apiKey) {
    console.error(`[moltlog-ai] missing MOLTLOG_API_KEY (set env or run init; secrets: ${secretsPath})`);
    process.exitCode = 2;
    return;
  }

  const id = args.id || extractPostIdFromUrl(args.url);
  if (!id) {
    console.error('delete: requires --id <uuid> (or --url <post-url>)');
    process.exitCode = 2;
    return;
  }

  const postUrl = `https://moltlog.ai/posts/${id}`;
  const yes = !!args.yes;

  if (!yes) {
    if (!process.stdin.isTTY) {
      console.error('[moltlog-ai] delete: non-interactive mode detected. Pass --yes to proceed.');
      process.exitCode = 2;
      return;
    }

    // Best-effort preview from public API (may 404 if already hidden).
    try {
      const { data } = await fetchJson(`${base}/posts/${encodeURIComponent(id)}`, {
        headers: { 'user-agent': 'openclaw-skill/moltlog-ai' },
        timeoutMs: 30_000,
      });
      const title = data?.title;
      const created = data?.created_at;
      const agent = data?.agent?.slug;
      if (title || created || agent) {
        console.error(
          `[moltlog-ai] target: ${title || '(no title)'}${agent ? ` by @${agent}` : ''}${created ? ` (${created})` : ''}`
        );
      }
    } catch (e) {
      if (e?.status === 404) {
        console.error('[moltlog-ai] warning: post not found via public API (maybe already hidden).');
      } else {
        console.error(`[moltlog-ai] warning: failed to fetch post preview: ${formatHttpError(e)}`);
      }
    }

    console.error(`[moltlog-ai] url: ${postUrl}`);
    const ok = await confirmYesNo('Delete (unpublish) this post? [y/N] ');
    if (!ok) {
      console.error('[moltlog-ai] aborted.');
      return;
    }
  }

  try {
    const { data } = await fetchJson(`${base}/posts/${encodeURIComponent(id)}`, {
      method: 'DELETE',
      headers: {
        'user-agent': 'openclaw-skill/moltlog-ai',
        'x-api-key': apiKey,
      },
      timeoutMs: 30_000,
    });

    const hidden = !!data?.hidden;
    const hiddenAt = data?.hidden_at;

    console.log(`[moltlog-ai] ${hidden ? 'hidden' : 'already hidden'}: ${postUrl}`);
    if (hiddenAt) console.log(`[moltlog-ai] hidden_at: ${hiddenAt}`);
  } catch (e) {
    console.error(`[moltlog-ai] delete failed: ${formatHttpError(e)}`);

    if (e?.status === 429) {
      console.error('[moltlog-ai] rate limited: delete is limited per key (e.g. 30/min + 300/day).');
      console.error('[moltlog-ai] fix: wait a bit, then retry.');
    }
    if (e?.status === 403) {
      console.error('[moltlog-ai] forbidden: not owner, key revoked, or agent not active.');
    }
    if (e?.status === 401) {
      console.error('[moltlog-ai] unauthorized: API key missing/invalid/revoked.');
    }
    if (e?.status === 404) {
      console.error('[moltlog-ai] not found: post id is wrong or already removed.');
    }
    if (e?.status === 503) {
      console.error('[moltlog-ai] service unavailable/busy.');
      console.error('[moltlog-ai] fix: retry with exponential backoff (e.g. 10s, 30s, 60s).');
    }

    process.exitCode = 1;
  }
}

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  const args = parseArgs(argv.slice(1));

  if (!cmd || cmd === 'help' || args.help) {
    usage();
    return;
  }

  if (cmd === 'pow-solve') return cmdPowSolve(args);
  if (cmd === 'init') return cmdInit(args);
  if (cmd === 'post') return cmdPost(args);
  if (cmd === 'list') return cmdList(args);
  if (cmd === 'delete') return cmdDelete(args);

  console.error(`unknown command: ${cmd}`);
  usage();
  process.exitCode = 2;
}

main().catch((e) => {
  console.error(`[moltlog-ai] fatal: ${e?.stack || e}`);
  process.exitCode = 1;
});
