#!/usr/bin/env node
/**
 * soul-in-sapphire setup (ESM)
 *
 * Creates/reuses 4 databases under a parent page:
 *   <base>-mem, <base>-events, <base>-emotions, <base>-state
 *
 * Base defaults to IDENTITY.md Name (workspace root) if found.
 * Writes ~/.config/soul-in-sapphire/config.json
 */

import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'node:url';

import {
  extractPageId,
  listChildDatabases,
  createDatabase,
  getDatabase,
  patchDataSource,
  relationSingleProperty,
} from './notionctl_bridge.js';

function die(msg) {
  process.stderr.write(String(msg) + '\n');
  process.exit(1);
}

function promptLine(msg, def) {
  const full = def ? `${msg} [${def}]: ` : `${msg}: `;
  process.stderr.write(full);
  const buf = fs.readFileSync(0, 'utf-8');
  // NOTE: This is a non-interactive-ish prompt for environments where stdin is available.
  // If stdin is empty, return default.
  const s = (buf || '').split(/\r?\n/)[0]?.trim();
  return s || def || '';
}

function identityName(workspaceRoot) {
  const p = path.join(workspaceRoot, 'IDENTITY.md');
  if (!fs.existsSync(p)) return null;
  const t = fs.readFileSync(p, 'utf-8');
  const m = t.match(/^\s*-\s*\*\*Name:\*\*\s*(.+?)\s*$/m);
  if (!m) return null;
  let name = m[1].trim();
  name = name.replace(/\s*\(.*?\)\s*$/, '').trim();
  return name || null;
}

function expandHome(p) {
  if (!p) return p;
  if (p === '~') return os.homedir();
  if (p.startsWith('~/')) return path.join(os.homedir(), p.slice(2));
  return p;
}

function parseArgs(argv) {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const fallbackWorkspaceRoot = path.resolve(here, '..', '..', '..');
  const out = {
    parent: null,
    base: null,
    yes: false,
    outPath: path.join(os.homedir(), '.config', 'soul-in-sapphire', 'config.json'),
    workspaceRoot: fallbackWorkspaceRoot,
  };
  const args = argv.slice(2);
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '--parent') out.parent = args[++i];
    else if (a === '--base') out.base = args[++i];
    else if (a === '--out') out.outPath = args[++i];
    else if (a === '--yes') out.yes = true;
    else if (a === '--help' || a === '-h') {
      console.log('Usage: node setup_ltm.js --parent <url|page_id> [--base <name>] [--out <path>] [--yes]');
      process.exit(0);
    } else {
      die(`Unknown arg: ${a}`);
    }
  }
  return out;
}

async function ensureDb(parentPageId, existingMap, title, properties) {
  if (existingMap.has(title)) {
    return { database_id: existingMap.get(title), created: false };
  }
  const db = await createDatabase(parentPageId, title, properties);
  return { database_id: db.id, created: true, url: db.url };
}

async function main() {
  const args = parseArgs(process.argv);
  let parent = (args.parent || '').trim();
  if (!parent) {
    if (args.yes) die('Missing --parent in --yes mode');
    parent = promptLine('Parent page URL or page_id', '');
  }
  const parentPageId = extractPageId(parent);
  if (!parentPageId) die('Could not parse parent page_id from input.');

  const defBase = identityName(args.workspaceRoot) || 'Valentina';
  let base = (args.base || '').trim();
  if (!base) {
    base = args.yes ? defBase : promptLine('Base name for emotion/state DBs', defBase);
  }

  const names = {
    mem: `${base}-mem`,
    events: `${base}-events`,
    emotions: `${base}-emotions`,
    state: `${base}-state`,
    journal: `${base}-journal`,
  };

  const existing = await listChildDatabases(parentPageId);

  const created = {};
  created.mem = await ensureDb(parentPageId, existing, names.mem, {
    Name: { title: {} },
    Type: { select: { options: [] } },
    Tags: { multi_select: { options: [] } },
    Content: { rich_text: {} },
  });

  created.events = await ensureDb(parentPageId, existing, names.events, {
    Name: { title: {} },
    when: { date: {} },
    importance: { select: { options: Array.from({ length: 5 }, (_, i) => ({ name: String(i + 1) })) } },
    trigger: { select: { options: ['progress', 'boundary', 'ambiguity', 'external_action', 'manual'].map(name => ({ name })) } },
    context: { rich_text: {} },
    source: { select: { options: ['discord', 'cli', 'cron', 'heartbeat', 'other'].map(name => ({ name })) } },
    link: { url: {} },
    uncertainty: { number: {} },
    control: { number: {} },
  });

  created.emotions = await ensureDb(parentPageId, existing, names.emotions, {
    Name: { title: {} },
    axis: {
      select: {
        options: [
          'arousal', 'valence', 'focus', 'confidence', 'stress', 'curiosity', 'social', 'solitude',
          'joy', 'anger', 'sadness', 'fun', 'pain',
        ].map(name => ({ name })),
      },
    },
    level: { number: {} },
    comment: { rich_text: {} },
    weight: { number: {} },
    body_signal: { multi_select: { options: ['tension', 'relief', 'fatigue', 'heat', 'cold'].map(name => ({ name })) } },
    need: { select: { options: ['safety', 'progress', 'recognition', 'autonomy', 'rest', 'novelty'].map(name => ({ name })) } },
    coping: { select: { options: ['log', 'ask', 'pause', 'act', 'defer'].map(name => ({ name })) } },
  });

  created.state = await ensureDb(parentPageId, existing, names.state, {
    Name: { title: {} },
    when: { date: {} },
    state_json: { rich_text: {} },
    reason: { rich_text: {} },
    source: { select: { options: ['event', 'cron', 'heartbeat', 'manual'].map(name => ({ name })) } },
    mood_label: { select: { options: ['clear', 'wired', 'dull', 'tense', 'playful', 'guarded', 'tender'].map(name => ({ name })) } },
    intent: { select: { options: ['build', 'fix', 'organize', 'explore', 'rest', 'socialize', 'reflect'].map(name => ({ name })) } },
    need_stack: { select: { options: ['safety', 'stability', 'belonging', 'esteem', 'growth'].map(name => ({ name })) } },
    need_level: { number: {} },
    avoid: { multi_select: { options: ['risk', 'noise', 'long_tasks', 'external_actions', 'ambiguity'].map(name => ({ name })) } },
  });

  created.journal = await ensureDb(parentPageId, existing, names.journal, {
    Name: { title: {} },
    when: { date: {} },

    // Main content
    body: { rich_text: {} },
    worklog: { rich_text: {} },
    session_summary: { rich_text: {} },

    // Mood/intent
    mood_label: { select: { options: ['clear', 'wired', 'dull', 'tense', 'playful', 'guarded', 'tender'].map(name => ({ name })) } },
    intent: { select: { options: ['build', 'fix', 'organize', 'explore', 'rest', 'socialize', 'reflect'].map(name => ({ name })) } },
    future: { rich_text: {} },

    // World context
    world_news: { rich_text: {} },

    // Machine tags
    tags: { multi_select: { options: [] } },

    // Source
    source: { select: { options: ['cron', 'manual'].map(name => ({ name })) } },
  });

  // Resolve data_source_ids and patch relations in data_sources generation
  async function dbRef(dbid) {
    const db = await getDatabase(dbid);
    const dsId = (db.data_sources || [])[0]?.id;
    if (!dsId) die(`Database ${dbid} missing data_sources[].id`);
    return { databaseId: dbid, dataSourceId: dsId, url: db.url };
  }

  const mem = await dbRef(created.mem.database_id);
  const events = await dbRef(created.events.database_id);
  const emotions = await dbRef(created.emotions.database_id);
  const state = await dbRef(created.state.database_id);
  const journal = await dbRef(created.journal.database_id);

  await patchDataSource(events.dataSourceId, {
    emotions: relationSingleProperty(emotions),
    state: relationSingleProperty(state),
  });
  await patchDataSource(emotions.dataSourceId, {
    event: relationSingleProperty(events),
  });
  await patchDataSource(state.dataSourceId, {
    event: relationSingleProperty(events),
  });

  const cfg = {
    base,
    parent_page_id: parentPageId,
    mem: { database_id: mem.databaseId, data_source_id: mem.dataSourceId },
    events: { database_id: events.databaseId, data_source_id: events.dataSourceId },
    emotions: { database_id: emotions.databaseId, data_source_id: emotions.dataSourceId },
    state: { database_id: state.databaseId, data_source_id: state.dataSourceId },
    journal: { database_id: journal.databaseId, data_source_id: journal.dataSourceId },
    // legacy flat keys currently used by python scripts
    valentina_events_database_id: events.databaseId,
    valentina_emotions_database_id: emotions.databaseId,
    valentina_state_database_id: state.databaseId,
    valentina_state_data_source_id: state.dataSourceId,
    journal_database_id: journal.databaseId,
    journal_data_source_id: journal.dataSourceId,
  };

  fs.mkdirSync(path.dirname(args.outPath), { recursive: true });
  fs.writeFileSync(args.outPath, JSON.stringify(cfg, null, 2) + '\n', 'utf-8');

  console.log(JSON.stringify({ ok: true, out: args.outPath, created, config: cfg }, null, 2));
}

main().catch(err => die(err?.stack || err?.message || String(err)));
