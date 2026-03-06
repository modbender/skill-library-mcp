#!/usr/bin/env node

/**
 * Poll Fireflies for new meeting transcripts since last check.
 * Designed to run via cron every 30 minutes.
 *
 * Usage:
 *   node poll-new-meetings.js          # Check for new meetings since last poll
 *   node poll-new-meetings.js --force  # Re-check last 7 days regardless
 */

const { readFileSync, writeFileSync, mkdirSync, existsSync } = require('node:fs');
const { join } = require('node:path');
const { homedir } = require('node:os');

const HOME = homedir();
const MEMORY_DIR = join(HOME, process.env.OPENCLAW_WORKSPACE || 'clawd', 'memory/meetings');
const STATE_FILE = join(HOME, 'clawd/memory/meetings/.poll-state.json');
const API_KEY_PATH = join(HOME, '.openclaw/secrets/fireflies-api-key.txt');
const FIREFLIES_API = 'https://api.fireflies.ai/graphql';

function loadApiKey() {
  try { return readFileSync(API_KEY_PATH, 'utf-8').trim(); }
  catch { return null; }
}

function loadState() {
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { lastPollAt: null, processedIds: [] }; }
}

function saveState(state) {
  mkdirSync(MEMORY_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

async function graphql(query, variables = {}) {
  const apiKey = loadApiKey();
  if (!apiKey) throw new Error('No API key');
  const res = await fetch(FIREFLIES_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify({ query, variables }),
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors));
  return data.data;
}

function formatDuration(s) { return s ? `${Math.floor(s / 60)}m` : '?'; }
function formatTs(ms) {
  if (!ms && ms !== 0) return '';
  const t = Math.floor(ms / 1000);
  return `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`;
}
function slugify(t) {
  return (t || 'untitled').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
}

function toMarkdown(t) {
  // Fireflies returns date as epoch — could be seconds or milliseconds
  const epochMs = t.date > 1e12 ? t.date : t.date * 1000;
  const date = t.date ? new Date(epochMs) : new Date();
  const dateStr = date.toISOString().split('T')[0];
  const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone });

  let md = `# Meeting: ${t.title || 'Untitled'}\n`;
  md += `**Date:** ${dateStr} at ${timeStr} CT\n`;
  md += `**Duration:** ${formatDuration(t.duration)}\n`;
  if (t.organizer_email) md += `**Organizer:** ${t.organizer_email}\n`;
  if (t.participants?.length) md += `**Participants:** ${t.participants.join(', ')}\n`;
  md += `**Fireflies ID:** ${t.id}\n\n`;

  const s = t.summary;
  if (s) {
    if (s.overview) md += `## Summary\n${s.overview}\n\n`;
    else if (s.bullet_gist) md += `## Summary\n${s.bullet_gist}\n\n`;
    if (s.action_items) {
      md += `## Action Items\n`;
      const items = Array.isArray(s.action_items) ? s.action_items : s.action_items.split('\n').filter(Boolean);
      for (const i of items) { const c = i.replace(/^[-•*]\s*/, '').trim(); if (c) md += `- [ ] ${c}\n`; }
      md += '\n';
    }
    if (s.outline) md += `## Key Topics\n${s.outline}\n\n`;
    if (s.keywords?.length) md += `**Keywords:** ${s.keywords.join(', ')}\n\n`;
  }

  if (t.sentences?.length) {
    md += `## Full Transcript\n`;
    let last = null;
    for (const sent of t.sentences) {
      const speaker = sent.speaker_name || 'Unknown';
      if (speaker !== last) { md += `\n**${speaker}** [${formatTs(sent.start_time)}]:\n`; last = speaker; }
      md += `${sent.text} `;
    }
    md += '\n';
  }

  return { md, dateStr };
}

async function main() {
  const force = process.argv.includes('--force');
  const apiKey = loadApiKey();
  if (!apiKey) {
    console.log(JSON.stringify({ status: 'error', message: 'No API key at ' + API_KEY_PATH }));
    process.exit(1);
  }

  const state = loadState();
  const processedSet = new Set(state.processedIds || []);

  // Fetch recent transcripts
  const data = await graphql(`{ transcripts(limit: 20) { id title date duration organizer_email participants } }`);
  const transcripts = data.transcripts || [];

  if (transcripts.length === 0) {
    console.log(JSON.stringify({ status: 'no_meetings', message: 'No transcripts found' }));
    return;
  }

  // Filter to unprocessed
  const newOnes = force
    ? transcripts
    : transcripts.filter(t => !processedSet.has(t.id));

  if (newOnes.length === 0) {
    console.log(JSON.stringify({ status: 'up_to_date', checked: transcripts.length, message: 'No new meetings since last poll' }));
    saveState({ ...state, lastPollAt: new Date().toISOString() });
    return;
  }

  mkdirSync(MEMORY_DIR, { recursive: true });
  const results = [];

  for (const stub of newOnes) {
    try {
      const full = (await graphql(`
        query($id: String!) { transcript(id: $id) {
          id title date duration organizer_email participants
          sentences { index text start_time end_time speaker_name }
          summary { keywords action_items outline overview bullet_gist }
        }}
      `, { id: stub.id })).transcript;

      if (!full || (!full.sentences?.length && !full.summary)) {
        continue; // Skip empty transcripts
      }

      const { md, dateStr } = toMarkdown(full);
      const file = `${dateStr}-${slugify(full.title)}.md`;
      writeFileSync(join(MEMORY_DIR, file), md);
      processedSet.add(full.id);
      results.push({ id: full.id, title: full.title, file, sentences: full.sentences?.length || 0 });
    } catch (err) {
      console.error(`Error fetching ${stub.id}: ${err.message}`);
    }
  }

  saveState({
    lastPollAt: new Date().toISOString(),
    processedIds: [...processedSet],
  });

  console.log(JSON.stringify({
    status: results.length > 0 ? 'new_meetings' : 'up_to_date',
    newMeetings: results.length,
    meetings: results,
  }, null, 2));
}

main().catch(err => {
  console.error('Poll error:', err.message);
  process.exit(1);
});
