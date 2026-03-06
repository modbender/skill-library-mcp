#!/usr/bin/env node

/**
 * Fireflies.ai Webhook Receiver
 *
 * Listens for webhook notifications from Fireflies when transcription completes.
 * Fetches full transcript via GraphQL API and writes to memory/meetings/.
 *
 * Usage:
 *   node webhook-server.js              # Start on default port 3142
 *   PORT=8080 node webhook-server.js    # Start on custom port
 */

const http = require('node:http');
const crypto = require('node:crypto');
const { readFileSync, writeFileSync, mkdirSync, existsSync } = require('node:fs');
const { join } = require('node:path');
const { homedir } = require('node:os');

const HOME = homedir();
const PORT = process.env.PORT || 3142;
const MEMORY_DIR = join(HOME, process.env.OPENCLAW_WORKSPACE || 'clawd', 'memory/meetings');
const API_KEY_PATH = join(HOME, '.openclaw/secrets/fireflies-api-key.txt');
const SECRET_PATH = join(HOME, '.openclaw/secrets/fireflies-webhook-secret.txt');
const FIREFLIES_API = 'https://api.fireflies.ai/graphql';

function loadSecret(path) {
  try {
    return readFileSync(path, 'utf-8').trim();
  } catch {
    return null;
  }
}

function verifySignature(payload, signature, secret) {
  if (!secret || !signature) return !secret; // Skip if no secret configured
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

async function fetchTranscript(meetingId, apiKey) {
  const query = `
    query Transcript($transcriptId: String!) {
      transcript(id: $transcriptId) {
        id
        title
        date
        duration
        organizer_email
        participants
        sentences {
          index
          text
          raw_text
          start_time
          end_time
          speaker_name
          speaker_id
        }
        summary {
          keywords
          action_items
          outline
          shorthand_bullet
          overview
          bullet_gist
        }
      }
    }
  `;

  const res = await fetch(FIREFLIES_API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      query,
      variables: { transcriptId: meetingId },
    }),
  });

  if (!res.ok) {
    throw new Error(`Fireflies API error: ${res.status} ${await res.text()}`);
  }

  const data = await res.json();
  if (data.errors) {
    throw new Error(`GraphQL errors: ${JSON.stringify(data.errors)}`);
  }

  return data.data.transcript;
}

function formatDuration(seconds) {
  if (!seconds) return 'Unknown';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

function formatTimestamp(ms) {
  if (!ms && ms !== 0) return '';
  const totalSecs = Math.floor(ms / 1000);
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function slugify(text) {
  return (text || 'untitled')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 60);
}

function formatMeetingMarkdown(transcript) {
  // Fireflies returns date as epoch — could be seconds or milliseconds
  const epochMs = transcript.date > 1e12 ? transcript.date : transcript.date * 1000;
  const date = transcript.date ? new Date(epochMs) : new Date();
  const dateStr = date.toISOString().split('T')[0];
  const timeStr = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone,
  });

  let md = `# Meeting: ${transcript.title || 'Untitled Meeting'}\n`;
  md += `**Date:** ${dateStr} at ${timeStr} CT\n`;
  md += `**Duration:** ${formatDuration(transcript.duration)}\n`;
  if (transcript.organizer_email) {
    md += `**Organizer:** ${transcript.organizer_email}\n`;
  }
  if (transcript.participants?.length) {
    md += `**Participants:** ${transcript.participants.join(', ')}\n`;
  }
  md += `**Fireflies ID:** ${transcript.id}\n\n`;

  // Summary
  const summary = transcript.summary;
  if (summary) {
    if (summary.overview) {
      md += `## Summary\n${summary.overview}\n\n`;
    } else if (summary.bullet_gist) {
      md += `## Summary\n${summary.bullet_gist}\n\n`;
    }

    if (summary.action_items) {
      md += `## Action Items\n`;
      const items = Array.isArray(summary.action_items)
        ? summary.action_items
        : summary.action_items.split('\n').filter(Boolean);
      for (const item of items) {
        const clean = item.replace(/^[-•*]\s*/, '');
        if (clean.trim()) md += `- [ ] ${clean.trim()}\n`;
      }
      md += '\n';
    }

    if (summary.outline) {
      md += `## Key Topics\n${summary.outline}\n\n`;
    }

    if (summary.keywords?.length) {
      md += `**Keywords:** ${summary.keywords.join(', ')}\n\n`;
    }
  }

  // Full transcript with speaker labels
  if (transcript.sentences?.length) {
    md += `## Full Transcript\n`;
    let lastSpeaker = null;
    for (const s of transcript.sentences) {
      const ts = formatTimestamp(s.start_time);
      const speaker = s.speaker_name || 'Unknown';
      if (speaker !== lastSpeaker) {
        md += `\n**${speaker}** [${ts}]:\n`;
        lastSpeaker = speaker;
      }
      md += `${s.text} `;
    }
    md += '\n';
  }

  return { md, dateStr };
}

async function processWebhook(body) {
  const apiKey = loadSecret(API_KEY_PATH);
  if (!apiKey) {
    console.error('No API key found at', API_KEY_PATH);
    return { error: 'No API key configured' };
  }

  const { meetingId, eventType } = body;

  if (eventType !== 'Transcription completed') {
    console.log(`Ignoring event: ${eventType}`);
    return { status: 'ignored', eventType };
  }

  console.log(`Fetching transcript for meeting: ${meetingId}`);
  const transcript = await fetchTranscript(meetingId, apiKey);

  if (!transcript) {
    console.error('No transcript returned for', meetingId);
    return { error: 'No transcript found' };
  }

  // Write to memory
  mkdirSync(MEMORY_DIR, { recursive: true });
  const { md, dateStr } = formatMeetingMarkdown(transcript);
  const filename = `${dateStr}-${slugify(transcript.title)}.md`;
  const filepath = join(MEMORY_DIR, filename);
  writeFileSync(filepath, md);

  console.log(`✅ Saved: ${filename} (${transcript.sentences?.length || 0} sentences)`);

  return {
    status: 'processed',
    meetingId,
    title: transcript.title,
    file: filename,
    sentences: transcript.sentences?.length || 0,
  };
}

const server = http.createServer(async (req, res) => {
  // Health check
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'fireflies-webhook' }));
    return;
  }

  // Webhook endpoint
  if (req.method === 'POST' && (req.url === '/' || req.url === '/webhook')) {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', async () => {
      try {
        // Verify signature if secret is configured
        const secret = loadSecret(SECRET_PATH);
        const signature = req.headers['x-hub-signature'];
        if (secret && !verifySignature(body, signature, secret)) {
          console.error('Invalid webhook signature');
          res.writeHead(401);
          res.end('Invalid signature');
          return;
        }

        const parsed = JSON.parse(body);
        console.log(`Webhook received: ${parsed.eventType} for ${parsed.meetingId}`);

        const result = await processWebhook(parsed);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (err) {
        console.error('Webhook error:', err.message);
        res.writeHead(500);
        res.end(JSON.stringify({ error: err.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`Fireflies webhook receiver listening on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Webhook URL: http://localhost:${PORT}/webhook`);
  console.log(`API key: ${loadSecret(API_KEY_PATH) ? 'configured' : '⚠️  NOT SET — add to ' + API_KEY_PATH}`);
  console.log(`Webhook secret: ${loadSecret(SECRET_PATH) ? 'configured' : 'not set (signature verification disabled)'}`);
  console.log(`Output directory: ${MEMORY_DIR}`);
});
