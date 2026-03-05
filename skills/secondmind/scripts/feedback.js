#!/usr/bin/env node
// scripts/feedback.js – Bulk feedback: accept/reject/defer/drop/mute
// v1.3.0: Multi-ID, /drop (dead), /mute, bulk transactions, event logging
const { getDb, logProposalEvent, updateState, getState, createProjectFromProposal, archiveKnowledgeForProposal } = require('../lib/db');

const STATUS_MAP = {
  accept: 'accepted', reject: 'rejected', defer: 'deferred',
  complete: 'completed', start: 'in_progress', drop: 'dead',
};

const ICONS = {
  accepted: '✅', rejected: '❌', deferred: '⏸️',
  completed: '🏁', in_progress: '🔄', dead: '💀',
};

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    printUsage();
    return;
  }

  const action = args[0].toLowerCase();

  // === /mute ===
  if (action === 'mute') {
    return handleMute(args[1]);
  }
  if (action === 'unmute') {
    return handleUnmute();
  }

  const newStatus = STATUS_MAP[action];
  if (!newStatus) {
    console.log(`❌ Unknown action: ${action}`);
    printUsage();
    return;
  }

  const db = getDb();
  const rest = args.slice(1);

  // === /accept all | /drop all older_than 14d ===
  if (rest[0]?.toLowerCase() === 'all') {
    return handleAll(db, newStatus, rest.slice(1));
  }

  // === Parse IDs and optional comment ===
  const { ids, comment } = parseIdsAndComment(rest);

  if (ids.length === 0) {
    console.log(`❌ No valid IDs given.`);
    printUsage();
    return;
  }

  // === Bulk execute ===
  executeBulk(db, ids, newStatus, comment);
}

/**
 * Parse mixed ID + comment input.
 * "1 3 5" → ids=[1,3,5], comment=null
 * "3 gute idee" → ids=[3], comment="gute idee"
 * "1,3,5 mach mal" → ids=[1,3,5], comment="mach mal"
 */
function parseIdsAndComment(args) {
  const ids = [];
  const commentParts = [];
  let doneWithIds = false;

  for (const arg of args) {
    if (doneWithIds) {
      commentParts.push(arg);
      continue;
    }
    // Strip # prefix, split by comma
    const parts = arg.replace(/#/g, '').split(',').map(s => s.trim()).filter(Boolean);
    let allNumeric = true;
    for (const p of parts) {
      if (/^\d+$/.test(p)) {
        ids.push(parseInt(p));
      } else {
        allNumeric = false;
        commentParts.push(arg);
        break;
      }
    }
    if (!allNumeric) doneWithIds = true;
  }

  return {
    ids,
    comment: commentParts.length > 0 ? commentParts.join(' ') : null,
  };
}

/**
 * Execute bulk feedback in a transaction with event logging.
 */
function executeBulk(db, ids, newStatus, comment) {
  const update = db.prepare(`
    UPDATE proposals SET status = ?, user_feedback = ?, resolved_at = datetime('now')
    WHERE id = ?
  `);
  const selectOne = db.prepare('SELECT * FROM proposals WHERE id = ?');

  const results = [];

  const transaction = db.transaction(() => {
    for (const id of ids) {
      const p = selectOne.get(id);
      if (!p) {
        results.push({ id, ok: false, error: 'not found' });
        continue;
      }
      update.run(newStatus, comment, id);
      logProposalEvent(id, newStatus, comment);
      results.push({ id, ok: true, title: p.title, followUp: p.follow_up });
    }
  });

  transaction();

  // Output
  for (const r of results) {
    if (!r.ok) {
      console.log(`❌ #${r.id} nicht gefunden.`);
    } else {
      console.log(`${ICONS[newStatus] || '📝'} #${r.id} "${r.title}" → ${newStatus}`);
      if (newStatus === 'accepted' && r.followUp) {
        console.log(`\n💬 ${r.followUp}`);
      }
    }
  }

  // Auto-create projects for accepted proposals
  if (newStatus === 'accepted') {
    for (const r of results.filter(x => x.ok)) {
      const project = createProjectFromProposal(r.id);
      if (project) {
        console.log(`📦 Project #${project.id} "${r.title}" created`);
      }
    }
  }

  // Auto-complete projects when proposal is completed
  if (newStatus === 'completed') {
    const { completeProject } = require('../lib/db');
    for (const r of results.filter(x => x.ok)) {
      const project = completeProject(r.id);
      if (project) {
        console.log(`🏁 Project "${project.title}" completed`);
      }
    }
  }

  // On /drop: archive related knowledge entries so they don't keep generating proposals
  if (newStatus === 'dead') {
    for (const r of results.filter(x => x.ok)) {
      const archived = archiveKnowledgeForProposal(r.id);
      if (archived > 0) {
        console.log(`🗄️  ${archived} knowledge entry/entries archived for "${r.title}"`);
      }
    }
  }

  const okCount = results.filter(r => r.ok).length;
  if (ids.length > 1) {
    console.log(`\n📊 ${okCount}/${ids.length} Proposals → ${newStatus}`);
  }

  // Update throttle based on feedback pattern
  updateThrottle(db, newStatus);
}

/**
 * Handle "all" variants: /accept all, /drop all older_than 14d
 */
function handleAll(db, newStatus, extraArgs) {
  let where = "status = 'proposed'";
  let label = 'alle offenen';

  // Parse older_than filter
  if (extraArgs[0]?.toLowerCase() === 'older_than' && extraArgs[1]) {
    const days = parseDuration(extraArgs[1]);
    if (days) {
      where += ` AND proposed_at < datetime('now', '-${days} days')`;
      label = `alle > ${days} Tage alten`;
    }
  }

  const proposals = db.prepare(`SELECT id FROM proposals WHERE ${where}`).all();
  if (proposals.length === 0) {
    console.log(`Keine Proposals gefunden (${label}).`);
    return;
  }

  const ids = proposals.map(p => p.id);
  console.log(`${label}: ${ids.length} Proposals → ${newStatus}`);
  executeBulk(db, ids, newStatus, `bulk: ${label}`);
}

/**
 * /mute 1d | 1w | 2h
 */
function handleMute(duration) {
  if (!duration) {
    console.log('❌ Format: mute <duration> (z.B. 1d, 1w, 2h)');
    return;
  }
  const hours = parseDurationHours(duration);
  if (!hours) {
    console.log(`❌ Unbekannte Dauer: ${duration}. Nutze z.B. 1d, 1w, 2h`);
    return;
  }
  const until = new Date(Date.now() + hours * 3600000);
  updateState('mute_until', until.toISOString());
  console.log(`🔇 Muted bis ${until.toLocaleDateString('de-DE')} ${until.toLocaleTimeString('de-DE')}`);
}

function handleUnmute() {
  updateState('mute_until', null);
  console.log('🔊 Unmuted. Notifications sind wieder aktiv.');
}

/**
 * Auto-throttle: Track rejection streaks, adjust maxProposals.
 */
function updateThrottle(db, lastAction) {
  const streak = getState('rejection_streak') || '0';
  let count = parseInt(streak);

  if (['rejected', 'dead'].includes(lastAction)) {
    count++;
  } else if (lastAction === 'accepted') {
    count = Math.max(0, count - 2); // Acceptance reduces streak faster
  }

  updateState('rejection_streak', String(count));

  if (count >= 5) {
    updateState('proposal_throttle', '1');
    console.log('⚡ Auto-Drosselung: Zu viele Ablehnungen → max 1 Vorschlag pro Run');
  } else if (count === 0) {
    const current = getState('proposal_throttle');
    if (current === '1') {
      updateState('proposal_throttle', null);
      console.log('⚡ Drosselung aufgehoben → zurück auf Normal');
    }
  }
}

/**
 * Parse duration string to days: "14d" → 14, "2w" → 14
 */
function parseDuration(str) {
  const m = str.match(/^(\d+)([dwmh]?)$/i);
  if (!m) return null;
  const n = parseInt(m[1]);
  switch ((m[2] || 'd').toLowerCase()) {
    case 'h': return Math.max(1, Math.round(n / 24));
    case 'd': return n;
    case 'w': return n * 7;
    case 'm': return n * 30;
    default: return n;
  }
}

/**
 * Parse duration string to hours: "1d" → 24, "1w" → 168
 */
function parseDurationHours(str) {
  const m = str.match(/^(\d+)([dwmh]?)$/i);
  if (!m) return null;
  const n = parseInt(m[1]);
  switch ((m[2] || 'h').toLowerCase()) {
    case 'h': return n;
    case 'd': return n * 24;
    case 'w': return n * 168;
    case 'm': return n * 720;
    default: return n;
  }
}

function printUsage() {
  console.log(`Usage: node feedback.js <action> <ids...> [comment]

Actions:
  accept <id...>              Accept proposals
  reject <id...>              Reject proposals
  defer  <id...>              Defer proposals
  drop   <id...>              Kill proposals forever
  complete <id...>            Mark as completed
  start  <id...>              Mark as in_progress

Bulk:
  accept all                  Accept all open proposals
  drop all older_than 14d     Kill all proposals older than 14 days

Mute:
  mute 1d|1w|2h               Pause all notifications
  unmute                       Resume notifications

Examples:
  node feedback.js accept 1 3 5
  node feedback.js reject 2 4 nicht relevant
  node feedback.js drop all older_than 14d
  node feedback.js mute 1w`);
}

main();
