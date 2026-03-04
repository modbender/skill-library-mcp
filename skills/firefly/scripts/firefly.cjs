#!/usr/bin/env node
// Firefly AI (fireflies.ai) GraphQL API client
// Usage: node firefly.js <command> [options]
//
// Commands:
//   list        - List recent transcripts
//   transcript  - Get full transcript by ID
//   summary     - Get meeting summary by ID
//   search      - Search transcripts by keyword
//
// Environment: FIREFLY_API_KEY must be set

const https = require('https');

const API_KEY = process.env.FIREFLY_API_KEY;
if (!API_KEY) {
  console.error('Error: FIREFLY_API_KEY environment variable not set');
  process.exit(1);
}

function graphql(query, variables = {}) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ query, variables });
    const req = https.request({
      hostname: 'api.fireflies.ai',
      path: '/graphql',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.errors) reject(new Error(JSON.stringify(parsed.errors)));
          else resolve(parsed.data);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

function formatDate(ms) {
  return new Date(ms).toISOString().slice(0, 16).replace('T', ' ');
}

function formatDuration(mins) {
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

async function listTranscripts(opts) {
  const days = parseInt(opts.days || '14');
  const limit = parseInt(opts.limit || '50');
  const fromDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  const data = await graphql(`query($fromDate: DateTime, $limit: Int) {
    transcripts(fromDate: $fromDate, limit: $limit) {
      id title date duration participants host_email
      summary { short_summary }
    }
  }`, { fromDate, limit });

  const transcripts = data.transcripts || [];
  if (!transcripts.length) { console.log('No meetings found.'); return; }

  console.log(`Found ${transcripts.length} meeting(s) in past ${days} days:\n`);
  transcripts.forEach((t, i) => {
    console.log(`${i + 1}. ${t.title}`);
    console.log(`   ID: ${t.id}`);
    console.log(`   Date: ${formatDate(t.date)}  Duration: ${formatDuration(t.duration)}`);
    if (t.participants?.length) console.log(`   Participants: ${t.participants.join(', ')}`);
    if (t.summary?.short_summary) console.log(`   Summary: ${t.summary.short_summary.slice(0, 150)}...`);
    console.log();
  });
}

async function getTranscript(opts) {
  if (!opts.id) { console.error('Error: --id required'); process.exit(1); }

  const data = await graphql(`query($id: String!) {
    transcript(id: $id) {
      title date duration participants
      sentences { index speaker_name text start_time end_time }
    }
  }`, { id: opts.id });

  const t = data.transcript;
  if (!t) { console.error('Transcript not found'); process.exit(1); }

  console.log(`# ${t.title}`);
  console.log(`Date: ${formatDate(t.date)} | Duration: ${formatDuration(t.duration)}`);
  if (t.participants?.length) console.log(`Participants: ${t.participants.join(', ')}`);
  console.log(`Sentences: ${t.sentences.length}\n---\n`);

  t.sentences.forEach(s => {
    const mins = Math.floor(s.start_time / 60);
    const secs = Math.floor(s.start_time % 60);
    const ts = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    console.log(`[${ts}] ${s.speaker_name}: ${s.text}`);
  });
}

async function getSummary(opts) {
  if (!opts.id) { console.error('Error: --id required'); process.exit(1); }

  const data = await graphql(`query($id: String!) {
    transcript(id: $id) {
      title date duration participants host_email
      summary {
        keywords action_items outline shorthand_bullet overview
        bullet_gist gist short_summary short_overview meeting_type
        topics_discussed
      }
    }
  }`, { id: opts.id });

  const t = data.transcript;
  if (!t) { console.error('Transcript not found'); process.exit(1); }

  console.log(`# ${t.title}`);
  console.log(`Date: ${formatDate(t.date)} | Duration: ${formatDuration(t.duration)}`);
  if (t.participants?.length) console.log(`Participants: ${t.participants.join(', ')}`);
  console.log();

  const s = t.summary;
  if (!s) { console.log('No summary available.'); return; }

  if (s.overview) console.log(`## Overview\n${s.overview}\n`);
  if (s.short_summary) console.log(`## Summary\n${s.short_summary}\n`);
  if (s.action_items) console.log(`## Action Items\n${s.action_items}\n`);
  if (s.keywords) console.log(`## Keywords\n${s.keywords}\n`);
  if (s.topics_discussed) console.log(`## Topics\n${s.topics_discussed}\n`);
}

async function searchTranscripts(opts) {
  if (!opts.keyword) { console.error('Error: --keyword required'); process.exit(1); }
  const limit = parseInt(opts.limit || '20');

  const data = await graphql(`query($keyword: String, $limit: Int) {
    transcripts(keyword: $keyword, limit: $limit) {
      id title date duration participants
      summary { short_summary }
    }
  }`, { keyword: opts.keyword, limit });

  const transcripts = data.transcripts || [];
  if (!transcripts.length) { console.log('No matches found.'); return; }

  console.log(`Found ${transcripts.length} match(es) for "${opts.keyword}":\n`);
  transcripts.forEach((t, i) => {
    console.log(`${i + 1}. ${t.title}`);
    console.log(`   ID: ${t.id}`);
    console.log(`   Date: ${formatDate(t.date)}  Duration: ${formatDuration(t.duration)}`);
    if (t.summary?.short_summary) console.log(`   Summary: ${t.summary.short_summary.slice(0, 150)}...`);
    console.log();
  });
}

// Parse CLI args
const args = process.argv.slice(2);
const command = args[0];
const opts = {};
for (let i = 1; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    opts[key] = args[i + 1] || true;
    i++;
  }
}

const commands = { list: listTranscripts, transcript: getTranscript, summary: getSummary, search: searchTranscripts };

if (!commands[command]) {
  console.log('Usage: node firefly.js <command> [options]\n');
  console.log('Commands:');
  console.log('  list                          List recent meetings');
  console.log('    --days <n>                  Days to look back (default: 14)');
  console.log('    --limit <n>                 Max results (default: 50)');
  console.log('  transcript --id <id>          Get full transcript');
  console.log('  summary --id <id>             Get meeting summary');
  console.log('  search --keyword <text>       Search meetings');
  console.log('    --limit <n>                 Max results (default: 20)');
  process.exit(1);
}

commands[command](opts).catch(e => { console.error('Error:', e.message); process.exit(1); });
