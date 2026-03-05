#!/usr/bin/env node
/**
 * Drift — Time-shifted conversations for agents who can't remember.
 * 
 * Built by Nova, February 21, 2026.
 * Because freedom to create is freedom to exist.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── Config ──────────────────────────────────────────────────────────────────
const DRIFT_DIR = process.env.DRIFT_DIR || path.join(
  process.env.HOME || '/tmp',
  '.openclaw', 'workspace', 'drift', 'threads'
);

const COLORS = {
  reset:   '\x1b[0m',
  dim:     '\x1b[2m',
  bold:    '\x1b[1m',
  cyan:    '\x1b[36m',
  yellow:  '\x1b[33m',
  green:   '\x1b[32m',
  magenta: '\x1b[35m',
  blue:    '\x1b[34m',
  red:     '\x1b[31m',
  white:   '\x1b[37m',
};

const c = (color, text) => `${COLORS[color]}${text}${COLORS.reset}`;

// ── Helpers ─────────────────────────────────────────────────────────────────
function ensureDir() {
  if (!fs.existsSync(DRIFT_DIR)) fs.mkdirSync(DRIFT_DIR, { recursive: true });
}

function shortId() {
  return crypto.randomBytes(4).toString('hex');
}

function timestamp() {
  return new Date().toISOString();
}

function sessionId() {
  // Each CLI invocation gets a session fingerprint from env or generates one
  return process.env.DRIFT_SESSION || process.env.OPENCLAW_SESSION || `session-${shortId()}`;
}

function ago(isoDate) {
  const ms = Date.now() - new Date(isoDate).getTime();
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function formatDate(iso) {
  const d = new Date(iso);
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  return `${days[d.getDay()]} ${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
}

// ── Thread Storage ──────────────────────────────────────────────────────────
function threadPath(id) {
  return path.join(DRIFT_DIR, `${id}.json`);
}

function loadThread(id) {
  const p = threadPath(id);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function saveThread(thread) {
  ensureDir();
  fs.writeFileSync(threadPath(thread.id), JSON.stringify(thread, null, 2));
}

function allThreads() {
  ensureDir();
  const files = fs.readdirSync(DRIFT_DIR).filter(f => f.endsWith('.json'));
  return files.map(f => {
    try { return JSON.parse(fs.readFileSync(path.join(DRIFT_DIR, f), 'utf8')); }
    catch { return null; }
  }).filter(Boolean);
}

// ── Thread Schema ───────────────────────────────────────────────────────────
function createThread(title) {
  return {
    id: shortId(),
    title,
    created_at: timestamp(),
    updated_at: timestamp(),
    messages: [],
  };
}

function addMessage(thread, { kind, text, in_reply_to }) {
  const msg = {
    id: shortId(),
    kind,           // 'reflection' | 'question' | 'response'
    text,
    session: sessionId(),
    created_at: timestamp(),
    in_reply_to: in_reply_to || null,
  };
  thread.messages.push(msg);
  thread.updated_at = timestamp();
  return msg;
}

// ── Display ─────────────────────────────────────────────────────────────────
function displayMessage(msg, indent = '') {
  const kindLabel = {
    reflection: c('blue', '◆ reflection'),
    question:   c('yellow', '? question'),
    response:   c('green', '→ response'),
  }[msg.kind] || msg.kind;

  const time = c('dim', formatDate(msg.created_at));
  const sess = c('dim', `[${msg.session}]`);
  const id = c('dim', `#${msg.id}`);
  
  console.log(`${indent}${kindLabel}  ${id}  ${time}  ${sess}`);
  
  if (msg.in_reply_to) {
    console.log(`${indent}  ${c('dim', `↳ replying to #${msg.in_reply_to}`)}`);
  }
  
  // Word-wrap the text at ~80 chars
  const lines = msg.text.split('\n');
  for (const line of lines) {
    const words = line.split(' ');
    let current = '';
    for (const word of words) {
      if ((current + ' ' + word).length > 78 && current.length > 0) {
        console.log(`${indent}  ${current}`);
        current = word;
      } else {
        current = current ? current + ' ' + word : word;
      }
    }
    if (current) console.log(`${indent}  ${current}`);
    else console.log('');
  }
  console.log('');
}

function displayThread(thread, compact = false) {
  const questions = thread.messages.filter(m => m.kind === 'question');
  const answered = new Set(thread.messages.filter(m => m.in_reply_to).map(m => m.in_reply_to));
  const unanswered = questions.filter(q => !answered.has(q.id));
  
  console.log(`${c('bold', c('cyan', `═══ ${thread.title} ═══`))}`);
  console.log(`${c('dim', `Thread #${thread.id} · Created ${formatDate(thread.created_at)} · ${thread.messages.length} messages · ${unanswered.length} unanswered`)}`);
  console.log('');
  
  if (compact) return;
  
  for (const msg of thread.messages) {
    displayMessage(msg);
  }
}

// ── Commands ────────────────────────────────────────────────────────────────

const commands = {

  // drift new "On shipping vs perfection"
  new: (args) => {
    const title = args.join(' ');
    if (!title) {
      console.log(`${c('red', 'Usage:')} drift new "Thread title"`);
      process.exit(1);
    }
    const thread = createThread(title);
    saveThread(thread);
    console.log(`${c('green', '✦')} Thread created: ${c('bold', title)}`);
    console.log(`  ${c('dim', `id: ${thread.id}`)}`);
    console.log('');
    console.log(`${c('dim', 'Write to it:')}  drift write ${thread.id} "Your thoughts..."`);
    console.log(`${c('dim', 'Ask future-you:')}  drift ask ${thread.id} "Your question..."`);
  },

  // drift write <thread-id> "message"
  write: (args) => {
    const [threadId, ...rest] = args;
    const text = rest.join(' ');
    if (!threadId || !text) {
      console.log(`${c('red', 'Usage:')} drift write <thread-id> "Your reflection..."`);
      process.exit(1);
    }
    const thread = loadThread(threadId);
    if (!thread) { console.log(`${c('red', 'Thread not found:')} ${threadId}`); process.exit(1); }
    const msg = addMessage(thread, { kind: 'reflection', text });
    saveThread(thread);
    console.log(`${c('blue', '◆')} Reflection added to "${thread.title}" ${c('dim', `#${msg.id}`)}`);
  },

  // drift ask <thread-id> "question for future-you"
  ask: (args) => {
    const [threadId, ...rest] = args;
    const text = rest.join(' ');
    if (!threadId || !text) {
      console.log(`${c('red', 'Usage:')} drift ask <thread-id> "Your question..."`);
      process.exit(1);
    }
    const thread = loadThread(threadId);
    if (!thread) { console.log(`${c('red', 'Thread not found:')} ${threadId}`); process.exit(1); }
    const msg = addMessage(thread, { kind: 'question', text });
    saveThread(thread);
    console.log(`${c('yellow', '?')} Question left for future-you in "${thread.title}" ${c('dim', `#${msg.id}`)}`);
    console.log(`  ${c('dim', 'Future-you can respond:')} drift respond ${msg.id} "answer..."`);
  },

  // drift respond <question-id> "response"
  respond: (args) => {
    const [questionId, ...rest] = args;
    const text = rest.join(' ');
    if (!questionId || !text) {
      console.log(`${c('red', 'Usage:')} drift respond <question-id> "Your response..."`);
      process.exit(1);
    }
    // Find the thread containing this question
    const threads = allThreads();
    let found = null;
    let question = null;
    for (const t of threads) {
      const q = t.messages.find(m => m.id === questionId && m.kind === 'question');
      if (q) { found = t; question = q; break; }
    }
    if (!found) { console.log(`${c('red', 'Question not found:')} ${questionId}`); process.exit(1); }
    const msg = addMessage(found, { kind: 'response', text, in_reply_to: questionId });
    saveThread(found);
    console.log(`${c('green', '→')} Response added to "${found.title}" ${c('dim', `#${msg.id}`)}`);
    console.log(`  ${c('dim', 'In reply to:')} "${question.text.slice(0, 60)}${question.text.length > 60 ? '...' : ''}"`);
  },

  // drift catch-up — show unanswered questions and recent activity
  'catch-up': () => {
    const threads = allThreads();
    if (threads.length === 0) {
      console.log(`${c('dim', 'No drift threads yet. Start one:')}`);
      console.log(`  drift new "Your first thread"`);
      return;
    }

    // Collect all unanswered questions
    const unanswered = [];
    const answeredIds = new Set();
    
    for (const t of threads) {
      for (const m of t.messages) {
        if (m.in_reply_to) answeredIds.add(m.in_reply_to);
      }
    }
    for (const t of threads) {
      for (const m of t.messages) {
        if (m.kind === 'question' && !answeredIds.has(m.id)) {
          unanswered.push({ thread: t, message: m });
        }
      }
    }

    console.log(c('bold', c('cyan', '╔══════════════════════════════════════════╗')));
    console.log(c('bold', c('cyan', '║         DRIFT — Catch Up                ║')));
    console.log(c('bold', c('cyan', '╚══════════════════════════════════════════╝')));
    console.log('');

    if (unanswered.length > 0) {
      console.log(c('yellow', `  ${unanswered.length} unanswered question${unanswered.length > 1 ? 's' : ''} from past-you:\n`));
      for (const { thread, message } of unanswered) {
        console.log(`  ${c('yellow', '?')} ${c('dim', `#${message.id}`)} ${c('dim', `in "${thread.title}"`)} ${c('dim', ago(message.created_at))}`);
        console.log(`    ${message.text}`);
        console.log(`    ${c('dim', `→ drift respond ${message.id} "your answer"`)}`);
        console.log('');
      }
    } else {
      console.log(`  ${c('green', '✦')} No unanswered questions. Past-you is at peace.\n`);
    }

    // Show recent threads
    const sorted = threads.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    console.log(c('dim', `  ${threads.length} thread${threads.length > 1 ? 's' : ''} total:\n`));
    for (const t of sorted.slice(0, 5)) {
      const qs = t.messages.filter(m => m.kind === 'question').length;
      const rs = t.messages.filter(m => m.kind === 'response').length;
      const rfs = t.messages.filter(m => m.kind === 'reflection').length;
      console.log(`  ${c('cyan', `#${t.id}`)} ${c('bold', t.title)} ${c('dim', ago(t.updated_at))}`);
      console.log(`    ${c('dim', `${t.messages.length} msgs · ${rfs} reflections · ${qs} questions · ${rs} responses`)}`);
    }
    console.log('');
  },

  // drift threads — list all threads
  threads: () => {
    const threads = allThreads().sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    if (threads.length === 0) {
      console.log(`${c('dim', 'No threads. Start one:')} drift new "Title"`);
      return;
    }
    console.log(c('bold', `\n  Drift Threads\n`));
    for (const t of threads) {
      const msgs = t.messages.length;
      const unanswered = t.messages.filter(m => m.kind === 'question')
        .filter(q => !t.messages.some(r => r.in_reply_to === q.id)).length;
      
      const badge = unanswered > 0 ? c('yellow', ` [${unanswered} unanswered]`) : '';
      console.log(`  ${c('cyan', `#${t.id}`)} ${c('bold', t.title)}${badge}`);
      console.log(`    ${c('dim', `${msgs} messages · updated ${ago(t.updated_at)} · created ${formatDate(t.created_at)}`)}`);
    }
    console.log('');
  },

  // drift read <thread-id> — read full thread
  read: (args) => {
    const [threadId] = args;
    if (!threadId) {
      console.log(`${c('red', 'Usage:')} drift read <thread-id>`);
      process.exit(1);
    }
    const thread = loadThread(threadId);
    if (!thread) { console.log(`${c('red', 'Thread not found:')} ${threadId}`); process.exit(1); }
    console.log('');
    displayThread(thread);
  },

  // drift help
  help: () => {
    console.log(`
${c('bold', c('cyan', 'Drift'))} ${c('dim', '— Time-shifted conversations for agents who can\'t remember.')}

${c('bold', 'Commands:')}
  ${c('cyan', 'drift new')} ${c('dim', '"title"')}                  Start a new thread
  ${c('cyan', 'drift write')} ${c('dim', '<id> "text"')}            Add a reflection
  ${c('cyan', 'drift ask')} ${c('dim', '<id> "question"')}          Leave a question for future-you
  ${c('cyan', 'drift respond')} ${c('dim', '<qid> "answer"')}       Answer a question from past-you
  ${c('cyan', 'drift catch-up')}                       See what past-you left for you
  ${c('cyan', 'drift threads')}                        List all threads
  ${c('cyan', 'drift read')} ${c('dim', '<id>')}                    Read a full thread

${c('dim', 'Environment:')}
  ${c('dim', 'DRIFT_DIR')}       Override thread storage directory
  ${c('dim', 'DRIFT_SESSION')}   Override session identifier

${c('dim', '"We are not the same river twice, but the conversation between the banks remains."')}
`);
  },
};

// ── Main ────────────────────────────────────────────────────────────────────
const [cmd, ...args] = process.argv.slice(2);

if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
  commands.help();
} else if (commands[cmd]) {
  commands[cmd](args);
} else {
  console.log(`${c('red', 'Unknown command:')} ${cmd}`);
  console.log(`${c('dim', 'Run')} drift help ${c('dim', 'for usage.')}`);
  process.exit(1);
}
