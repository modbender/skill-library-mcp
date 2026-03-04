#!/usr/bin/env node
/**
 * emostate_tick.js
 *
 * Input JSON:
 * - --payload-file <path> (recommended for agents/automation)
 * - --payload-json '<json>'
 * - stdin (backward-compatible fallback)
 *
 * Payload shape:
 * {
 *   event: {...},
 *   emotions: [{axis, level, comment?, need?, coping?, body_signal? ...}, ...],
 *   state: { mood_label?, intent?, need_stack?, need_level?, avoid?, reason? }
 * }
 */

import fs from 'fs';
import os from 'os';
import path from 'path';

import {
  createPage,
  queryDataSource,
} from './notionctl_bridge.js';

function usage() {
  process.stdout.write(
    'Usage:\n' +
    '  node skills/soul-in-sapphire/scripts/emostate_tick.js --payload-file /path/to/payload.json\n' +
    '  node skills/soul-in-sapphire/scripts/emostate_tick.js --payload-json \'{"event":{...},"emotions":[],"state":{...}}\'\n' +
    '  cat payload.json | node skills/soul-in-sapphire/scripts/emostate_tick.js\n'
  );
}

function die(msg) {
  process.stderr.write(String(msg) + '\n');
  process.exit(1);
}

function expandHome(p) {
  if (!p) return p;
  if (p === '~') return os.homedir();
  if (p.startsWith('~/')) return path.join(os.homedir(), p.slice(2));
  return p;
}

function parseArgs(argv) {
  const out = { payloadFile: null, payloadJson: null, help: false };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      out.help = true;
      continue;
    }
    if (a === '--payload-file') {
      out.payloadFile = argv[++i] || '';
      continue;
    }
    if (a.startsWith('--payload-file=')) {
      out.payloadFile = a.slice('--payload-file='.length);
      continue;
    }
    if (a === '--payload-json') {
      out.payloadJson = argv[++i] || '';
      continue;
    }
    if (a.startsWith('--payload-json=')) {
      out.payloadJson = a.slice('--payload-json='.length);
      continue;
    }
    die(`Unknown argument: ${a}`);
  }

  if (out.payloadFile && out.payloadJson) {
    die('Use either --payload-file or --payload-json, not both.');
  }
  return out;
}

function readRawPayload(args) {
  if (args.payloadFile) {
    const fp = expandHome(args.payloadFile);
    if (!fp || !fs.existsSync(fp)) die(`Payload file not found: ${fp || args.payloadFile}`);
    const raw = fs.readFileSync(fp, 'utf-8').trim();
    if (!raw) die(`Payload file is empty: ${fp}`);
    return { raw, source: `--payload-file ${fp}` };
  }

  if (args.payloadJson != null) {
    const raw = String(args.payloadJson).trim();
    if (!raw) die('--payload-json is empty');
    return { raw, source: '--payload-json' };
  }

  const raw = fs.readFileSync(0, 'utf-8').trim();
  if (!raw) die('Expected JSON payload via --payload-file, --payload-json, or stdin');
  return { raw, source: 'stdin' };
}

function parsePayload(args) {
  const { raw, source } = readRawPayload(args);
  try {
    return JSON.parse(raw);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    die(`Invalid JSON in ${source}: ${msg}`);
  }
}

function hasText(v) {
  return typeof v === 'string' && v.trim().length > 0;
}

function hasNumberLike(v) {
  return !(v === null || v === undefined || v === '');
}

const AXES = [
  'arousal','valence','focus','confidence','stress','curiosity','social','solitude',
  'joy','anger','sadness','fun','pain',
];

const NORMAL_HALF_LIFE_HOURS = 24.0;

function clamp010(x) {
  if (x < 0) return 0;
  if (x > 10) return 10;
  return x;
}

function nowIso() {
  // local offset ISO seconds
  const d = new Date();
  const tz = -d.getTimezoneOffset();
  const sign = tz >= 0 ? '+' : '-';
  const pad = n => String(Math.floor(Math.abs(n))).padStart(2,'0');
  const hh = pad(tz/60);
  const mm = pad(tz%60);
  const iso = d.toISOString().replace('Z','');
  return `${iso}${sign}${hh}:${mm}`;
}

function titleProp(s) {
  return { title: [{ type: 'text', text: { content: String(s) } }] };
}
function rtProp(s) {
  if (!s) return { rich_text: [] };
  return { rich_text: [{ type: 'text', text: { content: String(s) } }] };
}
function selectProp(name) {
  return { select: name ? { name: String(name) } : null };
}
function multiProp(arr) {
  const xs = Array.isArray(arr) ? arr : [];
  return { multi_select: xs.filter(Boolean).map(n => ({ name: String(n) })) };
}
function numProp(x) {
  if (x === null || x === undefined || x === '') return { number: null };
  return { number: Number(x) };
}
function dateProp(start) {
  if (!start) return { date: null };
  return { date: { start: String(start) } };
}
function urlProp(u) {
  if (!u) return { url: null };
  return { url: String(u) };
}
function relProp(pageId) {
  return { relation: [{ id: pageId }] };
}

function expDecayToward(x, target, hours, halfLifeHours) {
  if (hours <= 0) return x;
  if (halfLifeHours <= 0) return target;
  const lam = Math.log(2) / halfLifeHours;
  return target + (x - target) * Math.exp(-lam * hours);
}

function imprintHalfLife(severity) {
  const s = Math.max(0, Math.min(10, severity));
  return NORMAL_HALF_LIFE_HOURS * (1 + s);
}

function parseIso(s) {
  if (!s) return null;
  const t = String(s).replace('Z', '+00:00');
  const d = new Date(t);
  return isNaN(d.getTime()) ? null : d;
}

function propText(prop) {
  if (!prop) return '';
  const t = prop.type;
  if (t === 'rich_text' || t === 'title') {
    return (prop[t] || []).map(x => x?.plain_text || '').join('').trim();
  }
  if (t === 'date') return prop.date?.start || '';
  return '';
}

function readConfig() {
  const p = path.join(os.homedir(), '.config', 'soul-in-sapphire', 'config.json');
  if (!fs.existsSync(p)) die(`Missing config: ${p}. Run setup_ltm.js first.`);
  return JSON.parse(fs.readFileSync(p, 'utf-8'));
}

function initialState() {
  const s = {};
  for (const ax of AXES) s[ax] = 5;
  return s;
}

function maybeAddImprints(stateJson, emotions, event) {
  let imprints = Array.isArray(stateJson.imprints) ? stateJson.imprints : [];
  const control = event?.control;
  const controlV = (control === null || control === undefined) ? null : Number(control);

  for (const emo of emotions) {
    const axis = emo?.axis;
    if (!AXES.includes(axis)) continue;
    const level = Number(emo?.level);
    if (!Number.isFinite(level)) continue;
    if (level < 9) continue;
    if (controlV !== null && Number.isFinite(controlV) && controlV > 3) continue;

    const sev = Math.max(0, Math.min(10, level));
    const tag = `imprint:${axis}:${event?.trigger || 'event'}`;
    imprints.push({
      tag,
      axis,
      severity: sev,
      created_at: event?.when || null,
      decay_half_life_hours: imprintHalfLife(sev),
      notes: emo?.comment || '',
    });
  }

  // dedupe by (tag, created_at)
  const seen = new Set();
  const dedupRev = [];
  for (let i = imprints.length - 1; i >= 0; i--) {
    const it = imprints[i] || {};
    const key = `${it.tag || ''}|${it.created_at || ''}`;
    if (seen.has(key)) continue;
    seen.add(key);
    dedupRev.push(it);
  }
  stateJson.imprints = dedupRev.reverse();
}

function assertPayloadShape(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    die('Invalid payload: expected a JSON object.');
  }
  if (payload.event !== undefined && (typeof payload.event !== 'object' || payload.event === null || Array.isArray(payload.event))) {
    die('Invalid payload: event must be an object.');
  }
  if (payload.emotions !== undefined && !Array.isArray(payload.emotions)) {
    die('Invalid payload: emotions must be an array.');
  }
  if (payload.state !== undefined && (typeof payload.state !== 'object' || payload.state === null || Array.isArray(payload.state))) {
    die('Invalid payload: state must be an object.');
  }
}

function hasMeaningfulEvent(event) {
  return (
    hasText(event?.title) ||
    hasText(event?.context) ||
    hasText(event?.trigger) ||
    hasText(event?.source) ||
    hasText(event?.link) ||
    hasNumberLike(event?.importance) ||
    hasNumberLike(event?.uncertainty) ||
    hasNumberLike(event?.control)
  );
}

function hasMeaningfulEmotion(emotions) {
  return emotions.some((emo) => (
    emo && typeof emo === 'object' && (
      hasText(emo.axis) ||
      hasNumberLike(emo.level) ||
      hasText(emo.comment) ||
      hasText(emo.need) ||
      hasText(emo.coping) ||
      (Array.isArray(emo.body_signal) && emo.body_signal.some(Boolean))
    )
  ));
}

function hasMeaningfulState(state) {
  return (
    hasText(state?.title) ||
    hasText(state?.reason) ||
    hasText(state?.source) ||
    hasText(state?.mood_label) ||
    hasText(state?.intent) ||
    hasText(state?.need_stack) ||
    hasNumberLike(state?.need_level) ||
    (Array.isArray(state?.avoid) && state.avoid.some(Boolean))
  );
}

function assertMeaningfulPayload(payload) {
  const event = payload.event || {};
  const emotions = payload.emotions || [];
  const state = payload.state || {};
  if (hasMeaningfulEvent(event) || hasMeaningfulEmotion(emotions) || hasMeaningfulState(state)) return;
  die('Meaningless payload: provide at least one non-empty event/emotions/state field.');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return;
  }

  const payload = parsePayload(args);
  assertPayloadShape(payload);
  assertMeaningfulPayload(payload);

  const cfg = readConfig();
  const eventsDb = cfg?.events?.database_id || cfg.valentina_events_database_id;
  const emotionsDb = cfg?.emotions?.database_id || cfg.valentina_emotions_database_id;
  const stateDb = cfg?.state?.database_id || cfg.valentina_state_database_id;
  const stateDs = cfg?.state?.data_source_id || cfg.valentina_state_data_source_id;
  if (!(eventsDb && emotionsDb && stateDb && stateDs)) die('Config missing events/emotions/state ids. Re-run setup.');

  const event = payload.event || {};
  const emotions = payload.emotions || [];
  const stateOverrides = payload.state || {};

  const when = event.when || nowIso();

  // 1) create event
  const eventProps = {
    Name: titleProp(event.title || '(event)'),
    when: dateProp(when),
    importance: selectProp(event.importance != null ? String(event.importance) : null),
    trigger: selectProp(event.trigger || null),
    context: rtProp(event.context || ''),
    source: selectProp(event.source || 'other'),
    link: urlProp(event.link || null),
    uncertainty: numProp(event.uncertainty),
    control: numProp(event.control),
  };
  const epage = await createPage(eventsDb, eventProps);
  const eventId = epage.id;

  // 2) create emotions linked
  for (const emo of emotions) {
    const props = {
      Name: titleProp(emo.title || `${emo.axis}=${emo.level}`),
      axis: selectProp(emo.axis || null),
      level: numProp(emo.level),
      comment: rtProp(emo.comment || ''),
      weight: numProp(emo.weight),
      body_signal: multiProp(emo.body_signal || []),
      need: selectProp(emo.need || null),
      coping: selectProp(emo.coping || null),
      event: relProp(eventId),
    };
    await createPage(emotionsDb, props);
  }

  // 3) load latest state
  const q = await queryDataSource(stateDs, {
    page_size: 1,
    sorts: [{ timestamp: 'created_time', direction: 'descending' }],
  });
  const latest = (q.results || [])[0] || null;

  let base = initialState();
  let baseObj = {};
  let baseWhen = null;

  if (latest) {
    const props = latest.properties || {};
    const sj = propText(props.state_json);
    const w = propText(props.when);
    baseWhen = parseIso(w);
    try {
      baseObj = sj ? JSON.parse(sj) : {};
    } catch {
      baseObj = {};
    }
    if (baseObj && typeof baseObj === 'object') {
      for (const ax of AXES) {
        if (ax in baseObj) base[ax] = Number(baseObj[ax]);
      }
    }
  }

  // 3.5) decay toward 5
  const nowDt = parseIso(when);
  if (nowDt && baseWhen) {
    const hours = (nowDt.getTime() - baseWhen.getTime()) / 3600000;
    if (hours > 0) {
      const byAxis = {};
      const imprints = Array.isArray(baseObj?.imprints) ? baseObj.imprints : [];
      for (const it of imprints) {
        const ax = it?.axis;
        if (!AXES.includes(ax)) continue;
        const hl = Number(it?.decay_half_life_hours);
        byAxis[ax] = Number.isFinite(hl) ? hl : imprintHalfLife(Number(it?.severity || 0));
      }
      for (const ax of AXES) {
        const hl = byAxis[ax] || NORMAL_HALF_LIFE_HOURS;
        base[ax] = clamp010(expDecayToward(Number(base[ax] || 5), 5, hours, hl));
      }
    }
  }

  // 4) apply emotion deltas (level-5)
  for (const emo of emotions) {
    const ax = emo?.axis;
    if (!AXES.includes(ax)) continue;
    const level = Number(emo?.level);
    if (!Number.isFinite(level)) continue;
    const delta = level - 5;
    base[ax] = clamp010(Number(base[ax] || 5) + delta);
  }

  const stateJson = { ...base };
  if (Array.isArray(baseObj?.imprints)) stateJson.imprints = baseObj.imprints;
  maybeAddImprints(stateJson, emotions, { ...event, when });
  stateJson.__meta = { version: 1 };

  // 5) write state
  const stProps = {
    Name: titleProp(stateOverrides.title || `state@${when}`),
    when: dateProp(when),
    state_json: rtProp(JSON.stringify(stateJson)),
    reason: rtProp(stateOverrides.reason || 'event tick'),
    source: selectProp(stateOverrides.source || 'event'),
    mood_label: selectProp(stateOverrides.mood_label || null),
    intent: selectProp(stateOverrides.intent || null),
    need_stack: selectProp(stateOverrides.need_stack || null),
    need_level: numProp(stateOverrides.need_level),
    avoid: multiProp(stateOverrides.avoid || []),
    event: relProp(eventId),
  };

  const spage = await createPage(stateDb, stProps);

  console.log(JSON.stringify({
    ok: true,
    event: { id: eventId, url: epage.url },
    state: { id: spage.id, url: spage.url, state_json: stateJson },
  }, null, 2));
}

main().catch(err => die(err?.stack || err?.message || String(err)));
