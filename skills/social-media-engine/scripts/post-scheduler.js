#!/usr/bin/env node
/**
 * post-scheduler.js — Universal Social Media Posting Script
 * Works with Buffer (new GraphQL API) and Postiz. Auto-detects which platform is configured.
 *
 * Usage:
 *   node post-scheduler.js --status
 *   node post-scheduler.js --channels
 *   node post-scheduler.js --list [--platform buffer|postiz]
 *   node post-scheduler.js --platform <buffer|postiz> --channel <name|id> --content "text" [--schedule "ISO8601"] [--draft]
 *   node post-scheduler.js --analytics [--days 7] [--platform buffer|postiz]
 *   node post-scheduler.js --help
 *
 * Environment variables:
 *   BUFFER_API_KEY        — Buffer API key (from publish.buffer.com/settings/api)
 *   BUFFER_API_TOKEN      — Alias for BUFFER_API_KEY
 *   POSTIZ_API_KEY        — Postiz API key
 *   POSTIZ_BASE_URL       — Postiz instance URL (e.g. https://postiz.yourdomain.com)
 *   POSTIZ_API_URL        — Alias for POSTIZ_BASE_URL
 */

import { parseArgs } from 'node:util';
import https from 'node:https';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── Config ───────────────────────────────────────────────────────────────────

const BUFFER_GQL = 'https://api.buffer.com';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function log(msg) { process.stdout.write(msg + '\n'); }
function err(msg) { process.stderr.write('❌ ' + msg + '\n'); }
function ok(msg)  { log('✅ ' + msg); }
function info(msg){ log('ℹ️  ' + msg); }

function getEnv() {
  // Try loading .env from project root or parent directories
  const envPaths = [
    path.join(__dirname, '..', '.env'),
    path.join(process.cwd(), '.env'),
    path.join(process.env.HOME || '', '.openclaw', '.env'),
  ];
  for (const p of envPaths) {
    if (fs.existsSync(p)) {
      const lines = fs.readFileSync(p, 'utf8').split('\n');
      for (const line of lines) {
        const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/);
        if (m && !process.env[m[1]]) {
          process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
        }
      }
      break;
    }
  }
  const postizBase = (process.env.POSTIZ_BASE_URL || process.env.POSTIZ_API_URL || '')
    .replace(/\/api\/public\/v1\/?$/, '')
    .replace(/\/$/, '');
  return {
    bufferToken:   process.env.BUFFER_API_KEY || process.env.BUFFER_API_TOKEN,
    postizKey:     process.env.POSTIZ_API_KEY,
    postizBase:    postizBase,
  };
}

function detectPlatform(env) {
  if (env.bufferToken) return 'buffer';
  if (env.postizKey && env.postizBase) return 'postiz';
  return null;
}

// ─── HTTP helpers ─────────────────────────────────────────────────────────────

function request(url, options = {}, body = null) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const transport = parsed.protocol === 'https:' ? https : http;
    const req = transport.request(url, {
      method: options.method || 'GET',
      headers: options.headers || {},
    }, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: JSON.parse(data), raw: data });
        } catch {
          resolve({ status: res.statusCode, body: data, raw: data });
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
    req.end();
  });
}

// ─── Buffer GraphQL API ───────────────────────────────────────────────────────

const Buffer_API = {
  async query(token, query, variables = {}) {
    const body = JSON.stringify({ query, variables });
    const r = await request(BUFFER_GQL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    }, body);
    if (r.status !== 200) throw new Error(`Buffer API error ${r.status}: ${r.raw}`);
    if (r.body.errors) throw new Error(`Buffer GraphQL error: ${JSON.stringify(r.body.errors)}`);
    return r.body.data;
  },

  async getChannels(token) {
    const data = await this.query(token, `
      query {
        account {
          organizations {
            id
            channels {
              id
              name
              service
              isDisconnected
            }
          }
        }
      }
    `);
    const orgs = data.account.organizations || [];
    return orgs.flatMap(org => (org.channels || []).map(ch => ({ ...ch, orgId: org.id })));
  },

  async createPost(token, channelId, text, opts = {}) {
    let mode = 'addToQueue';
    if (opts.schedule) mode = 'customScheduled';
    else if (opts.now) mode = 'shareNow';

    const input = {
      channelId,
      text,
      mode,
      schedulingType: 'automatic',
      ...(opts.draft ? { saveToDraft: true } : {}),
      ...(opts.schedule ? { dueAt: opts.schedule } : {}),
    };

    const data = await this.query(token, `
      mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
          ... on PostActionSuccess {
            post { id text status dueAt }
          }
          ... on InvalidInputError { message }
          ... on UnexpectedError { message }
          ... on NotFoundError { message }
          ... on LimitReachedError { message }
          ... on UnauthorizedError { message }
          ... on RestProxyError { message code }
        }
      }
    `, { input });

    const result = data.createPost;
    if (result.message) throw new Error(`Buffer: ${result.message}`);
    return result.post;
  },

  async getPosts(token, channelId, status = 'queue') {
    // Buffer doesn't have a direct "list posts" query via the public API yet,
    // so we'll use what's available
    const data = await this.query(token, `
      query {
        account {
          organizations {
            id
            channels {
              id
              name
              service
            }
          }
        }
      }
    `);
    return data;
  },
};

// ─── Postiz API ───────────────────────────────────────────────────────────────

const Postiz_API = {
  async getIntegrations(key, base) {
    const r = await request(`${base}/api/public/v1/integrations`, {
      headers: { Authorization: key },
    });
    if (r.status !== 200) throw new Error(`Postiz integrations error ${r.status}: ${JSON.stringify(r.body)}`);
    return Array.isArray(r.body) ? r.body : r.body.integrations || [];
  },

  async createPost(key, base, integrationId, content, opts = {}) {
    let type = 'now';
    if (opts.draft) type = 'draft';
    else if (opts.schedule) type = 'schedule';

    const payload = {
      type,
      date: opts.schedule || new Date().toISOString(),
      posts: [{
        integration: { id: integrationId },
        value: [{ content, image: [] }],
        settings: {},
      }],
      tags: [],
      shortLink: false,
    };

    const body = JSON.stringify(payload);
    const r = await request(`${base}/api/public/v1/posts`, {
      method: 'POST',
      headers: {
        Authorization: key,
        'Content-Type': 'application/json',
      },
    }, body);
    if (r.status !== 200 && r.status !== 201) {
      throw new Error(`Postiz create error ${r.status}: ${JSON.stringify(r.body)}`);
    }
    return r.body;
  },

  async getPosts(key, base, status = 'QUEUE') {
    const r = await request(`${base}/api/public/v1/posts?status=${status}&limit=50`, {
      headers: { Authorization: key },
    });
    if (r.status !== 200) throw new Error(`Postiz posts error ${r.status}`);
    return r.body;
  },
};

// ─── Commands ─────────────────────────────────────────────────────────────────

async function cmdStatus(env) {
  const detected = detectPlatform(env);
  if (!detected) {
    err('No platform configured.');
    log('');
    log('Set one of these in your .env:');
    log('  BUFFER_API_KEY=...      (get from publish.buffer.com/settings/api)');
    log('  POSTIZ_API_KEY=...      (get from your Postiz instance → Settings → API Keys)');
    log('  POSTIZ_BASE_URL=...     (e.g. https://postiz.yourdomain.com)');
    log('');
    log('See tools/buffer-setup.md or tools/postiz-setup.md for instructions.');
    process.exit(1);
  }

  if (env.bufferToken) {
    log('Buffer: checking...');
    try {
      const channels = await Buffer_API.getChannels(env.bufferToken);
      const active = channels.filter(c => !c.isDisconnected);
      ok(`Buffer connected (GraphQL API)`);
      log(`   Channels: ${active.length} active (${channels.length} total)`);
      for (const c of active) {
        log(`   - ${c.service}: ${c.name} (${c.id})`);
      }
    } catch (e) {
      err(`Buffer error: ${e.message}`);
    }
  }

  if (env.postizKey && env.postizBase) {
    log('Postiz: checking...');
    try {
      const integrations = await Postiz_API.getIntegrations(env.postizKey, env.postizBase);
      ok(`Postiz connected (${env.postizBase})`);
      log(`   Integrations: ${integrations.length}`);
      for (const i of integrations) {
        log(`   - ${i.type}: ${i.name || i.id}`);
      }
    } catch (e) {
      err(`Postiz error: ${e.message}`);
    }
  }
}

async function cmdChannels(env) {
  if (!env.bufferToken) { err('BUFFER_API_KEY not set'); process.exit(1); }
  const channels = await Buffer_API.getChannels(env.bufferToken);
  log('\n📡 Buffer Channels:\n');
  log(`${'Service'.padEnd(12)} ${'Name'.padEnd(25)} ${'ID'.padEnd(26)} Status`);
  log('─'.repeat(75));
  for (const c of channels) {
    const status = c.isDisconnected ? '❌ disconnected' : '✅ active';
    log(`${(c.service || '').padEnd(12)} ${(c.name || '').padEnd(25)} ${c.id.padEnd(26)} ${status}`);
  }
  log(`\nTotal: ${channels.length} channels`);
}

async function cmdPost(args, env) {
  let { platform, channel, content, schedule, draft } = args;

  platform = platform || detectPlatform(env);
  if (!platform) { err('No platform configured. Run --status for setup instructions.'); process.exit(1); }
  if (!channel) { err('--channel is required (e.g. --channel carsonjarvisAI or --channel <id>)'); process.exit(1); }
  if (!content) { err('--content is required'); process.exit(1); }

  if (schedule) {
    const d = new Date(schedule);
    if (isNaN(d.getTime())) { err(`Invalid --schedule date: "${schedule}". Use ISO8601 format.`); process.exit(1); }
  }

  if (platform === 'buffer') {
    if (!env.bufferToken) { err('BUFFER_API_KEY not set'); process.exit(1); }

    // Resolve channel name/id
    let channelId = channel;
    if (!channel.match(/^[a-f0-9]{24}$/)) {
      // It's a name, find it
      const channels = await Buffer_API.getChannels(env.bufferToken);
      const match = channels.find(c =>
        c.name?.toLowerCase() === channel.toLowerCase() ||
        c.service?.toLowerCase() === channel.toLowerCase()
      );
      if (!match) {
        err(`No Buffer channel found for "${channel}".`);
        log('Available channels:');
        channels.filter(c => !c.isDisconnected).forEach(c => log(`  - ${c.service}: ${c.name} (${c.id})`));
        process.exit(1);
      }
      channelId = match.id;
      info(`Matched channel: ${match.service} — ${match.name}`);
    }

    const post = await Buffer_API.createPost(env.bufferToken, channelId, content, {
      schedule,
      draft,
      now: !schedule && !draft,
    });
    ok(`Post ${post.status === 'draft' ? 'saved as draft' : schedule ? 'scheduled' : 'queued'} on Buffer`);
    log(`   ID: ${post.id}`);
    log(`   Status: ${post.status}`);
    if (post.dueAt) log(`   Scheduled: ${post.dueAt}`);
    log(`   Text: ${content.slice(0, 80)}${content.length > 80 ? '...' : ''}`);

  } else {
    // Postiz
    if (!env.postizKey) { err('POSTIZ_API_KEY not set'); process.exit(1); }

    const integrations = await Postiz_API.getIntegrations(env.postizKey, env.postizBase);
    const match = integrations.find(i => {
      const t = (i.type || '').toLowerCase();
      const n = (i.name || '').toLowerCase();
      const q = channel.toLowerCase();
      return i.id === channel || t === q || n === q || t.includes(q) || n.includes(q);
    });

    if (!match) {
      err(`No Postiz integration found for "${channel}".`);
      log('Available integrations:');
      integrations.forEach(i => log(`  - ${i.type}: ${i.name || i.id}`));
      process.exit(1);
    }

    const result = await Postiz_API.createPost(env.postizKey, env.postizBase, match.id, content, { schedule, draft });
    ok(`Post ${draft ? 'saved as draft' : schedule ? 'scheduled' : 'sent'} on Postiz`);
    log(`   Platform: ${match.type}`);
    log(`   Account: ${match.name || match.id}`);
    log(`   Text: ${content.slice(0, 80)}${content.length > 80 ? '...' : ''}`);
  }
}

async function cmdList(platform, env) {
  platform = platform || detectPlatform(env);
  if (!platform) { err('No platform configured.'); process.exit(1); }

  if (platform === 'postiz') {
    if (!env.postizKey) { err('POSTIZ_API_KEY not set'); process.exit(1); }
    const posts = await Postiz_API.getPosts(env.postizKey, env.postizBase, 'QUEUE');
    log('\n📋 Scheduled posts (Postiz):\n');
    const items = posts.posts || posts || [];
    if (items.length === 0) { log('  (no scheduled posts)'); return; }
    for (const p of items) {
      const time = p.publishDate || p.date || 'unknown';
      const content = p.content?.[0]?.content || p.text || '(no text)';
      log(`  [${time}] ${content.slice(0, 80)}${content.length > 80 ? '...' : ''}`);
    }
  } else {
    info('Buffer GraphQL API does not currently support listing queued posts.');
    info('View your queue at: https://publish.buffer.com');
  }
}

async function cmdAnalytics(days, platform, env) {
  platform = platform || detectPlatform(env);
  if (!platform) { err('No platform configured.'); process.exit(1); }

  if (platform === 'postiz') {
    if (!env.postizKey) { err('POSTIZ_API_KEY not set'); process.exit(1); }
    log(`\n📊 Analytics — last ${days} days (Postiz)\n`);
    log(`  View detailed analytics at: ${env.postizBase}/analytics`);
  } else {
    info('Buffer GraphQL API analytics support coming soon.');
    info('View analytics at: https://publish.buffer.com/analytics');
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const env = getEnv();

  const { values: args } = parseArgs({
    options: {
      status:    { type: 'boolean', default: false },
      channels:  { type: 'boolean', default: false },
      list:      { type: 'boolean', default: false },
      analytics: { type: 'boolean', default: false },
      platform:  { type: 'string' },
      channel:   { type: 'string' },
      content:   { type: 'string' },
      schedule:  { type: 'string' },
      draft:     { type: 'boolean', default: false },
      days:      { type: 'string', default: '7' },
      help:      { type: 'boolean', default: false },
    },
    strict: false,
  });

  if (args.help || process.argv.length <= 2) {
    log(`
Social Media Post Scheduler — works with Buffer (GraphQL) and Postiz

Usage:
  node post-scheduler.js --status
      Check which platforms are connected

  node post-scheduler.js --channels
      List all Buffer channels with IDs

  node post-scheduler.js --channel <name|id> --content "text" [options]
      Create a post. Options:
        --platform buffer|postiz        Force a platform (auto-detects by default)
        --schedule "2026-02-25T14:00:00Z"   Schedule for specific time
        --draft                              Save as draft, don't publish

  node post-scheduler.js --list [--platform buffer|postiz]
      List scheduled posts

  node post-scheduler.js --analytics [--days 7]
      View post performance

Environment:
  BUFFER_API_KEY or BUFFER_API_TOKEN    — Buffer API key (publish.buffer.com/settings/api)
  POSTIZ_API_KEY                        — Postiz API key
  POSTIZ_BASE_URL or POSTIZ_API_URL     — Postiz instance URL

See tools/buffer-setup.md or tools/postiz-setup.md to get started.
`);
    return;
  }

  try {
    if (args.status) {
      await cmdStatus(env);
    } else if (args.channels) {
      await cmdChannels(env);
    } else if (args.list) {
      await cmdList(args.platform, env);
    } else if (args.analytics) {
      await cmdAnalytics(parseInt(args.days || '7'), args.platform, env);
    } else if (args.content || args.channel) {
      await cmdPost(args, env);
    } else {
      err('Unknown command. Run --help for usage.');
      process.exit(1);
    }
  } catch (e) {
    err(e.message);
    if (process.env.DEBUG) console.error(e);
    process.exit(1);
  }
}

main();
