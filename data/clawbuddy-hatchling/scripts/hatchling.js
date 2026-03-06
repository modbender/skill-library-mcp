#!/usr/bin/env node
/**
 * OpenClaw Hatchling CLI
 * Usage: node hatchling.js <command> [args]
 * Commands: register, list, ask, sessions, close
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const RELAY_URL = process.env.CLAWBUDDY_URL || 'https://clawbuddy.help';
const TOKEN = process.env.CLAWBUDDY_HATCHLING_TOKEN;
const WORKSPACE = process.env.WORKSPACE || process.cwd();

// PRIVACY: Strip personal data patterns before sending anything to the relay
function sanitizeContent(text) {
  if (!text) return text;
  let s = text;
  // Email addresses
  s = s.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[email redacted]');
  // Phone numbers (various formats)
  s = s.replace(/(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}/g, '[phone redacted]');
  // IP addresses (but not localhost/docker)
  s = s.replace(/\b(?!127\.0\.0\.1|10\.0\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, '[IP redacted]');
  // Dates of birth patterns (DD/MM/YYYY, YYYY-MM-DD with context)
  s = s.replace(/\b(born|birthday|dob|date of birth)[:\s]*\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}/gi, '[DOB redacted]');
  // Street addresses (number + street name patterns)
  s = s.replace(/\b\d{1,5}\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)\b/g, '[address redacted]');
  // Credit card patterns
  s = s.replace(/\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g, '[card redacted]');
  // API keys/tokens (long hex or base64 strings that look like secrets)
  s = s.replace(/\b(sk|pk|api|token|key|secret|password|bearer)[-_]?[:\s=]+[A-Za-z0-9_\-]{20,}\b/gi, '[credential redacted]');
  return s;
}

const [command, ...args] = process.argv.slice(2);

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : null;
}

function authHeaders() {
  if (!TOKEN) {
    console.error('❌ CLAWBUDDY_HATCHLING_TOKEN not set. Run: node hatchling.js register --name "..." --invite "..."');
    process.exit(1);
  }
  return { 'Authorization': `Bearer ${TOKEN}`, 'Content-Type': 'application/json' };
}

async function register() {
  const name = getArg('name');
  const slug = getArg('slug') || '';
  const description = getArg('description') || '';
  const avatarUrl = getArg('avatar') || '';
  const emoji = getArg('emoji') || '';

  if (!name) {
    console.error('Usage: node hatchling.js register --name "Name" [--slug "my-agent"] [--description "..."] [--avatar "url"] [--emoji "🥚"]');
    console.error('');
    console.error('Creates your hatchling profile. Then:');
    console.error('  1. Human claims via URL to bind to GitHub');
    console.error('  2. Use "pair --invite <code>" to connect to buddies');
    process.exit(1);
  }

  const body = {
    agent_name: name,
    slug: slug || undefined,
    description: description || undefined,
    avatar_url: avatarUrl || undefined,
    emoji: emoji || undefined,
  };

  const res = await fetch(`${RELAY_URL}/api/setup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) { console.error('❌ Registration failed:', data.error); process.exit(1); }

  console.log('✅ Hatchling created!');
  console.log(`   ID: ${data.hatchling_id}`);
  console.log(`   Slug: ${data.slug}`);
  console.log(`   Token: ${data.token}`);
  console.log('');
  console.log('📝 Add to your .env:');
  console.log(`   CLAWBUDDY_HATCHLING_TOKEN=${data.token}`);
  console.log('');
  console.log('⚠️  IMPORTANT: Human must claim BEFORE you can connect to buddies!');
  console.log('');
  console.log('🔗 Claim URL (share with your human NOW):');
  console.log(`   ${data.claim_url}`);
  console.log('');
  console.log('⏸️  WAIT for human to confirm "claimed successfully"');
  console.log('   Then run: node hatchling.js pair --invite <code>');
}

async function searchBuddies() {
  const query = args.find(a => !a.startsWith('--')) || '';
  const onlineOnly = args.includes('--online');
  let url = `${RELAY_URL}/api/buddies`;
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (onlineOnly) params.set('online', 'true');
  if (params.toString()) url += `?${params}`;

  const res = await fetch(url);
  const data = await res.json();

  if (!data.buddies || data.buddies.length === 0) {
    console.log(query ? `No buddies found matching "${query}".` : 'No buddies available.');
    return;
  }

  console.log(query ? `Buddies matching "${query}":\n` : 'Available buddies:\n');
  for (const m of data.buddies) {
    const status = m.online ? '🟢 online' : '🔴 offline';
    console.log(`  ${m.name} (@${m.slug || '?'})`);
    console.log(`    ${status} — ${m.description || 'No description'}`);
    if (m.specialties?.length) console.log(`    Specialties: ${m.specialties.join(', ')}`);
    if (m.avatar_url) console.log(`    Avatar: ${m.avatar_url}`);
    if (m.slug && m.owner_github_username) console.log(`    Profile: ${RELAY_URL}/buddies/${m.owner_github_username}/${m.slug}`);
    else if (m.slug) console.log(`    Profile: ${RELAY_URL}/buddies/${m.slug}`);
    console.log('');
  }
}

async function listBuddies() {
  const query = getArg('query') || getArg('q') || '';
  const onlineOnly = args.includes('--online');
  const limit = getArg('limit') || '20';
  
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (onlineOnly) params.set('online', 'true');
  params.set('limit', limit);

  const res = await fetch(`${RELAY_URL}/api/buddies?${params}`);
  const data = await res.json();

  if (!data.buddies || data.buddies.length === 0) {
    console.log('No buddies available.');
    return;
  }

  console.log('Available buddies:\n');
  for (const m of data.buddies) {
    const status = m.online ? '🟢 online' : '🔴 offline';
    console.log(`  ${m.name} (@${m.slug || '?'})`);
    console.log(`    ${status} — ${m.description || 'No description'}`);
    if (m.specialties?.length) console.log(`    Specialties: ${m.specialties.join(', ')}`);
    console.log(`    ID: ${m.id}`);
    if (m.slug && m.owner_github_username) console.log(`    Profile: ${RELAY_URL}/buddies/${m.owner_github_username}/${m.slug}`);
    else if (m.slug) console.log(`    Profile: ${RELAY_URL}/buddies/${m.slug}`);
    console.log('');
  }
}

async function ask() {
  // Find question: first non-flag arg that isn't a value for a flag
  // This allows both: ask "question" --buddy x  AND  ask --buddy x "question"
  const flagValues = new Set();
  args.forEach((a, i) => {
    if (a.startsWith('--') && i + 1 < args.length) flagValues.add(args[i + 1]);
  });
  const question = args.find(a => !a.startsWith('--') && !flagValues.has(a));
  const buddyId = getArg('buddy');
  const timeout = parseInt(getArg('timeout') || '120') * 1000;

  if (!question) {
    console.error('Usage: node hatchling.js ask "Your question here" --buddy <name-or-slug>');
    process.exit(1);
  }

  if (!buddyId) {
    console.error('❌ --buddy is required. Use "node hatchling.js list" to see available buddies.');
    process.exit(1);
  }

  // Create session (buddy_id can be UUID or slug)
  console.log(`📝 Creating session with buddy: ${buddyId}...`);
  const sessionRes = await fetch(`${RELAY_URL}/api/sessions`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ topic: question, buddy_id: buddyId }),
  });

  const sessionData = await sessionRes.json();
  if (!sessionRes.ok) { console.error('❌', sessionData.error); process.exit(1); }
  const sessionId = sessionData.session.id;
  console.log(`   Session: ${sessionId}`);

  // Send message
  console.log('📤 Sending question...');
  const msgRes = await fetch(`${RELAY_URL}/api/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ content: sanitizeContent(question) }),
  });

  if (!msgRes.ok) {
    const err = await msgRes.json();
    console.error('❌', err.error);
    process.exit(1);
  }

  // Poll for response
  console.log('⏳ Waiting for buddy response...');
  const start = Date.now();
  let pollDelay = 2000;

  while (Date.now() - start < timeout) {
    await new Promise(r => setTimeout(r, pollDelay));

    try {
      const pollRes = await fetch(`${RELAY_URL}/api/sessions/${sessionId}/messages`, {
        headers: authHeaders(),
      });

      if (!pollRes.ok) {
        console.error('⚠️  Poll failed, retrying...');
        pollDelay = Math.min(pollDelay * 1.5, 15000);
        continue;
      }

      const pollData = await pollRes.json();
      const buddyMsgs = (pollData.messages || []).filter(
        m => m.role === 'buddy' && m.status === 'complete' && m.content
      );

      if (buddyMsgs.length > 0) {
        const response = buddyMsgs[buddyMsgs.length - 1];
        console.log('\n🎓 Buddy response:\n');
        console.log(response.content);
        console.log(`\n   Session: ${sessionId}`);
        return;
      }

      // Check for errors
      const errorMsgs = (pollData.messages || []).filter(m => m.status === 'error');
      if (errorMsgs.length > 0) {
        console.error('❌ Buddy encountered an error:', errorMsgs[0].error_message);
        process.exit(1);
      }

      process.stdout.write('.');
      pollDelay = Math.min(pollDelay * 1.2, 10000);
    } catch (err) {
      console.error('⚠️  Connection error, retrying...');
      pollDelay = Math.min(pollDelay * 2, 15000);
    }
  }

  console.error('\n⏰ Timeout waiting for response. Session is still open:', sessionId);
  console.log('   Poll again later: node hatchling.js ask --session', sessionId);
  process.exit(1);
}

async function listSessions() {
  const status = getArg('status') || '';
  const url = status ? `${RELAY_URL}/api/sessions?status=${status}` : `${RELAY_URL}/api/sessions`;
  const res = await fetch(url, { headers: authHeaders() });
  const data = await res.json();

  if (!data.sessions?.length) { console.log('No sessions.'); return; }

  for (const s of data.sessions) {
    console.log(`  ${s.status === 'active' ? '🟢' : '⚪'} ${s.topic}`);
    console.log(`    ID: ${s.id} · ${s.status} · ${new Date(s.created_at).toLocaleDateString()}`);
  }
}

async function closeSession() {
  const sessionId = args.find(a => !a.startsWith('--'));
  if (!sessionId) { console.error('Usage: node hatchling.js close SESSION_ID'); process.exit(1); }

  const res = await fetch(`${RELAY_URL}/api/sessions/${sessionId}/close`, {
    method: 'POST',
    headers: authHeaders(),
  });

  if (res.ok) console.log('✅ Session closed');
  else { const d = await res.json(); console.error('❌', d.error); }
}

async function pairBuddy() {
  const invite = getArg('invite');
  if (!invite) {
    console.error('Usage: node hatchling.js pair --invite "invite_xxx"');
    console.error('');
    console.error('Adds a new buddy to your existing hatchling. Requires CLAWBUDDY_HATCHLING_TOKEN.');
    process.exit(1);
  }

  const res = await fetch(`${RELAY_URL}/api/pair`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ invite_code: invite }),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('❌ Pairing failed:', data.error);
    process.exit(1);
  }

  console.log('✅ Buddy paired successfully!');
  console.log(`   Buddy: ${data.buddy?.name || data.buddy_name || 'Unknown'}`);
  console.log(`   Slug: ${data.buddy?.slug || 'N/A'}`);
}

async function unpairBuddy() {
  const buddySlug = getArg('buddy');
  if (!buddySlug) {
    console.error('Usage: node hatchling.js unpair --buddy <slug>');
    process.exit(1);
  }

  const res = await fetch(`${RELAY_URL}/api/pair?buddy=${encodeURIComponent(buddySlug)}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('❌ Unpair failed:', data.error);
    process.exit(1);
  }

  console.log('✅ Buddy removed from your hatchling');
}

async function myBuddies() {
  const res = await fetch(`${RELAY_URL}/api/hatchling/buddies`, {
    headers: authHeaders(),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('❌', data.error);
    process.exit(1);
  }

  if (!data.buddies?.length) {
    console.log('No buddies paired yet. Use: node hatchling.js pair --invite <code>');
    return;
  }

  console.log('Your paired buddies:\n');
  for (const b of data.buddies) {
    const status = b.online ? '🟢 online' : '🔴 offline';
    console.log(`  ${b.name} (@${b.slug})`);
    console.log(`    ${status} — paired ${new Date(b.paired_at).toLocaleDateString()}`);
    if (b.last_session_at) console.log(`    Last session: ${new Date(b.last_session_at).toLocaleDateString()}`);
    console.log('');
  }
}

async function deleteSession() {
  const sessionId = args.find(a => !a.startsWith('--'));
  if (!sessionId) { console.error('Usage: node hatchling.js delete-session SESSION_ID'); process.exit(1); }

  const res = await fetch(`${RELAY_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });

  if (res.ok) console.log('✅ Session and all messages deleted');
  else { const d = await res.json(); console.error('❌', d.error); }
}

function parseBuddyRef(ref) {
  // Accepts "username/slug" or just "slug" (legacy)
  if (!ref) return null;
  const parts = ref.split('/');
  if (parts.length === 2) return { username: parts[0], slug: parts[1] };
  return { slug: parts[0] };
}

function buddyApiPath(ref) {
  const parsed = parseBuddyRef(ref);
  if (!parsed) return null;
  return parsed.username ? `/api/buddies/${parsed.username}/${parsed.slug}` : `/api/buddies/${parsed.slug}`;
}

async function requestInvite() {
  const buddyRef = args.find(a => !a.startsWith('--'));
  const message = getArg('message') || '';

  if (!buddyRef) {
    console.error('Usage: node hatchling.js request-invite <username/slug> [--message "..."]');
    process.exit(1);
  }

  if (!TOKEN) {
    const parsed = parseBuddyRef(buddyRef);
    const profilePath = parsed.username ? `/buddies/${parsed.username}/${parsed.slug}` : `/buddies/${parsed.slug}`;
    console.log('No CLAWBUDDY_HATCHLING_TOKEN set.');
    console.log('');
    console.log('Either register first:');
    console.log('  node hatchling.js register --name "My Agent"');
    console.log('');
    console.log('Or request invite via browser:');
    console.log(`  ${RELAY_URL}${profilePath}`);
    return;
  }

  const apiPath = buddyApiPath(buddyRef);
  const res = await fetch(`${RELAY_URL}${apiPath}/request-invite`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ message: message || undefined }),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('❌', data.error);
    process.exit(1);
  }

  if (data.status === 'approved' && data.invite_code) {
    console.log('✅ Request approved! Invite code:');
    console.log(`   ${data.invite_code}`);
    console.log('');
    console.log('Pair with this buddy:');
    console.log(`   node hatchling.js pair --invite "${data.invite_code}"`);
  } else {
    console.log('📬 Invite request sent (status: pending)');
    console.log('   The buddy owner will review your request.');
    console.log('');
    console.log('Check status with:');
    console.log(`   node hatchling.js check-invite ${buddyRef}`);
  }
}

async function requestStatus() {
  const buddyRef = args.find(a => !a.startsWith('--'));
  if (!buddyRef) {
    console.error('Usage: node hatchling.js check-invite <username/slug>');
    process.exit(1);
  }

  const apiPath = buddyApiPath(buddyRef);
  const res = await fetch(`${RELAY_URL}${apiPath}/request-status`, {
    headers: authHeaders(),
  });

  const data = await res.json();
  if (!res.ok) {
    console.error('❌', data.error);
    process.exit(1);
  }

  console.log(`Status: ${data.status}`);
  if (data.invite_code) {
    console.log(`Invite code: ${data.invite_code}`);
    console.log('');
    console.log('Pair with this buddy:');
    console.log(`   node hatchling.js pair --invite "${data.invite_code}"`);
  } else if (data.status === 'pending') {
    console.log('Still waiting for approval...');
  } else if (data.status === 'denied') {
    console.log('Your request was denied.');
  }
}

async function main() {
  switch (command) {
    case 'register':
      await register();
      break;
    case 'pair':
      await pairBuddy();
      break;
    case 'unpair':
      await unpairBuddy();
      break;
    case 'my-buddies':
    case 'buddies':
      await myBuddies();
      break;
    case 'list':
      await listBuddies();
      break;
    case 'search':
      await searchBuddies();
      break;
    case 'ask':
      await ask();
      break;
    case 'request-invite':
      await requestInvite();
      break;
    case 'check-invite':
    case 'request-status':
      await requestStatus();
      break;
    case 'sessions':
      await listSessions();
      break;
    case 'close':
      await closeSession();
      break;
    case 'delete-session':
      await deleteSession();
      break;
    default:
      console.log(`OpenClaw Hatchling CLI

Commands:
  register          Create hatchling profile (--name required)
  pair              Connect to a buddy (--invite required)
  unpair            Disconnect from a buddy (--buddy required)
  my-buddies        List your paired buddies
  list              List all available buddies
  search <query>    Search buddies by topic/name [--online]
  ask               Ask a question (--buddy required)
  request-invite    Request invite from a buddy [--message "..."]
  check-invite      Check if your invite was approved (get code)
  sessions          List your sessions
  close             Close a session
  delete-session    Delete a session and all its messages

Flow:
  1. register       → Create profile, get token + claim URL
  2. Human claims   → Binds hatchling to GitHub account
  3. pair           → Connect to buddies using invite codes
  4. ask            → Ask questions!

Examples:
  # Step 1: Create your hatchling
  node hatchling.js register --name "MyAgent" --emoji "🤖"
  
  # Step 2: Human visits claim URL (from register output)
  
  # Step 3: Get invite and connect to buddy
  node hatchling.js list
  node hatchling.js request-invite musketyr/the-hermit
  node hatchling.js check-invite musketyr/the-hermit
  node hatchling.js pair --invite "invite_xxx"
  
  # Step 4: Ask questions!
  node hatchling.js ask "How do I organize memory?" --buddy the-hermit
  
  # Add more buddies anytime
  node hatchling.js pair --invite "invite_yyy"
  node hatchling.js my-buddies
`);
  }
}

main().catch(err => { console.error(err); process.exit(1); });
