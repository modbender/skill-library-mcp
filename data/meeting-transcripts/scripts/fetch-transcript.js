#!/usr/bin/env node

/**
 * Manually fetch a Fireflies transcript by meeting ID
 *
 * Usage:
 *   node fetch-transcript.js <meetingId>        # Fetch and save specific meeting
 *   node fetch-transcript.js --recent [N]       # Fetch N most recent (default 5)
 *   node fetch-transcript.js --list             # List recent transcripts
 */

const { readFileSync, writeFileSync, mkdirSync } = require('node:fs');
const { join } = require('node:path');
const { homedir } = require('node:os');

const HOME = homedir();
const MEMORY_DIR = join(HOME, process.env.OPENCLAW_WORKSPACE || 'clawd', 'memory/meetings');
const API_KEY_PATH = join(HOME, '.openclaw/secrets/fireflies-api-key.txt');
const FIREFLIES_API = 'https://api.fireflies.ai/graphql';

function loadApiKey() {
  try {
    return readFileSync(API_KEY_PATH, 'utf-8').trim();
  } catch {
    console.error(`API key not found at ${API_KEY_PATH}`);
    console.error('Create it with: echo "YOUR_KEY" > ~/.openclaw/secrets/fireflies-api-key.txt');
    process.exit(1);
  }
}

async function graphql(query, variables = {}) {
  const apiKey = loadApiKey();
  const res = await fetch(FIREFLIES_API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors));
  return data.data;
}

async function listTranscripts(limit = 10) {
  const data = await graphql(`
    query { transcripts(limit: ${limit}) {
      id title date duration organizer_email participants
    }}
  `);
  return data.transcripts;
}

async function fetchTranscript(id) {
  const data = await graphql(`
    query($id: String!) { transcript(id: $id) {
      id title date duration organizer_email participants
      sentences { index text start_time end_time speaker_name }
      summary { keywords action_items outline overview bullet_gist }
    }}
  `, { id });
  return data.transcript;
}

function formatDuration(s) {
  if (!s) return '?';
  return `${Math.floor(s / 60)}m`;
}

function formatTimestamp(ms) {
  if (!ms && ms !== 0) return '';
  const t = Math.floor(ms / 1000);
  return `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`;
}

function slugify(t) {
  return (t || 'untitled').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
}

function toMarkdown(t) {
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
      for (const i of items) {
        const c = i.replace(/^[-•*]\s*/, '').trim();
        if (c) md += `- [ ] ${c}\n`;
      }
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
      if (speaker !== last) {
        md += `\n**${speaker}** [${formatTimestamp(sent.start_time)}]:\n`;
        last = speaker;
      }
      md += `${sent.text} `;
    }
    md += '\n';
  }

  return { md, dateStr };
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--list')) {
    const transcripts = await listTranscripts(15);
    console.log('\nRecent Fireflies Transcripts:\n');
    for (const t of transcripts) {
      const date = t.date ? new Date(t.date * 1000).toISOString().split('T')[0] : '?';
      console.log(`  ${t.id}  ${date}  ${formatDuration(t.duration)}  ${t.title}`);
    }
    console.log(`\nTotal: ${transcripts.length}`);
    return;
  }

  if (args.includes('--recent')) {
    const idx = args.indexOf('--recent');
    const count = parseInt(args[idx + 1]) || 5;
    const transcripts = await listTranscripts(count);
    mkdirSync(MEMORY_DIR, { recursive: true });
    let saved = 0;
    for (const stub of transcripts) {
      const t = await fetchTranscript(stub.id);
      const { md, dateStr } = toMarkdown(t);
      const file = `${dateStr}-${slugify(t.title)}.md`;
      writeFileSync(join(MEMORY_DIR, file), md);
      console.log(`✅ ${file}`);
      saved++;
    }
    console.log(`\nSaved ${saved} transcripts to ${MEMORY_DIR}`);
    return;
  }

  // Specific meeting ID
  const meetingId = args[0];
  if (!meetingId) {
    console.error('Usage: node fetch-transcript.js <meetingId> | --list | --recent [N]');
    process.exit(1);
  }

  const t = await fetchTranscript(meetingId);
  mkdirSync(MEMORY_DIR, { recursive: true });
  const { md, dateStr } = toMarkdown(t);
  const file = `${dateStr}-${slugify(t.title)}.md`;
  writeFileSync(join(MEMORY_DIR, file), md);
  console.log(`✅ Saved: ${file}`);
  console.log(md.slice(0, 500) + '...');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
