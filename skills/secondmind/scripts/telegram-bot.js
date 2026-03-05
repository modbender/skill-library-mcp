#!/usr/bin/env node
// scripts/telegram-bot.js – Telegram Bot für Feedback + Status
// Läuft als Daemon, pollt Telegram Updates, verarbeitet Commands
const https = require('https');
const { initSchema, getConfig, getState, updateState, logProposalEvent, createProjectFromProposal, completeProject, getProjects, archiveKnowledgeForProposal } = require('../lib/db');
const { chatJSON } = require('../lib/llm');

const POLL_TIMEOUT = 30; // Long-polling seconds
let running = true;
let offset = 0;

async function main() {
  const db = initSchema();
  const config = getConfig();
  const token = config.notifications?.telegram?.botToken;
  const allowedChat = config.notifications?.telegram?.chatId;

  if (!token) {
    console.error('[BOT] Kein Telegram botToken in config.json');
    process.exit(1);
  }

  console.log('[BOT] 🤖 SecondMind Telegram Bot gestartet');
  console.log('[BOT] Warte auf Commands...');

  // Set bot commands menu
  await telegramAPI(token, 'setMyCommands', {
    commands: [
      { command: 'status', description: 'Show SecondMind status' },
      { command: 'proposals', description: 'List open proposals' },
      { command: 'projects', description: 'List active projects' },
      { command: 'accept', description: 'Accept – /accept <ID...> [comment]' },
      { command: 'reject', description: 'Reject – /reject <ID...> [comment]' },
      { command: 'defer', description: 'Defer – /defer <ID...> [comment]' },
      { command: 'complete', description: 'Mark project done – /complete <ID...>' },
      { command: 'drop', description: 'Kill forever – /drop <ID...> or /drop all' },
      { command: 'mute', description: 'Quiet mode – /mute 1d|1w' },
      { command: 'unmute', description: 'Resume notifications' },
      { command: 'search', description: 'Search knowledge – /search <term>' },
      { command: 'mood', description: 'Mood pulse (last 7 days)' },
      { command: 'help', description: 'Show available commands' },
    ]
  });

  while (running) {
    try {
      const updates = await getUpdates(token, offset);

      for (const update of updates) {
        offset = update.update_id + 1;
        const msg = update.message;
        if (!msg?.text) continue;

        // Security: nur erlaubte Chat ID
        const chatId = String(msg.chat.id);
        if (allowedChat && chatId !== String(allowedChat)) {
          console.log(`[BOT] Unauthorized: ${chatId}`);
          continue;
        }

        const text = msg.text.trim();
        console.log(`[BOT] ← ${text}`);

        try {
          const response = await handleCommand(db, text);
          if (response) {
            await sendMessage(token, chatId, response);
          }
        } catch (err) {
          await sendMessage(token, chatId, `❌ Fehler: ${err.message}`);
        }
      }
    } catch (err) {
      if (running) {
        console.error(`[BOT] Poll error: ${err.message}`);
        await sleep(5000);
      }
    }
  }
}

async function handleCommand(db, text) {
  // Parse command
  const match = text.match(/^\/(\w+)(?:\s+(.*))?$/);
  if (!match) {
    // Auch ohne / akzeptieren: "accept 3 gute idee"
    const matchNoSlash = text.match(/^(accept|reject|defer|drop|complete|done|status|proposals|projects|search|mood|help|mute|unmute)(?:\s+(.*))?$/i);
    if (matchNoSlash) return handleCommand(db, `/${matchNoSlash[1]} ${matchNoSlash[2] || ''}`);

    // NL-Fallback: Check if this looks like feedback on recent proposals
    const lastDigest = getState('last_digest_ids');
    if (lastDigest && looksLikeFeedback(text)) {
      return handleNLFeedback(db, text, lastDigest);
    }
    return null;
  }

  const cmd = match[1].toLowerCase();
  const args = (match[2] || '').trim();

  switch (cmd) {
    case 'start':
    case 'help':
      return helpText();

    case 'status':
      return statusText(db);

    case 'proposals':
    case 'p':
      return proposalsText(db, args);

    case 'projects':
    case 'pj':
      return projectsText(db, args);

    case 'accept':
    case 'a':
      return feedbackAction(db, args, 'accepted');

    case 'reject':
    case 'r':
      return feedbackAction(db, args, 'rejected');

    case 'defer':
    case 'd':
      return feedbackAction(db, args, 'deferred');

    case 'drop':
      return feedbackAction(db, args, 'dead');

    case 'complete':
    case 'done':
      return feedbackAction(db, args, 'completed');

    case 'mute':
      return handleMute(args);

    case 'unmute':
      return handleUnmute();

    case 'search':
    case 's':
      return searchText(db, args);

    case 'mood':
      return moodText(db);

    default:
      return `❓ Unbekannt: /${cmd}\n${helpText()}`;
  }
}

function helpText() {
  return `🧠 *SecondMind Bot*

/status – Overview
/proposals – Open proposals
/projects – Active projects
/accept <ID...> [comment]
/reject <ID...> [comment]
/defer <ID...> [comment]
/complete <ID...> – Mark project done
/drop <ID...> – Never suggest again
/drop all older\\_than 14d
/mute 1d|1w – Quiet mode
/unmute – Notifications back on
/search <term>
/mood – Mood pulse

_Shortcuts: /a /r /d /p /pj /s_
_Bulk: /accept 1 3 5 | /reject all_
_NL: "Take the first two, drop the rest"_`;
}

function statusText(db) {
  const k = db.prepare('SELECT COUNT(*) as c FROM knowledge_entries').get();
  const a = db.prepare('SELECT COUNT(*) as c FROM longterm_archive').get();
  const pOpen = db.prepare("SELECT COUNT(*) as c FROM proposals WHERE status='proposed'").get();
  const pTotal = db.prepare('SELECT COUNT(*) as c FROM proposals').get();
  const buf = db.prepare('SELECT COUNT(*) as c, SUM(CASE WHEN processed=0 THEN 1 ELSE 0 END) as u FROM shortterm_buffer').get();

  // Projects
  let projLine = '';
  try {
    const projActive = db.prepare("SELECT COUNT(*) as c FROM projects WHERE status='active'").get();
    const projDone = db.prepare("SELECT COUNT(*) as c FROM projects WHERE status='completed'").get();
    projLine = `\n📦 Projects: ${projActive.c} active / ${projDone.c} done`;
  } catch { /* table might not exist yet */ }

  let emo = '';
  try {
    const moods = db.prepare(`
      SELECT mood, COUNT(*) as c FROM social_context
      WHERE detected_at > datetime('now', '-7 days')
      GROUP BY mood ORDER BY c DESC LIMIT 5
    `).all();
    if (moods.length > 0) {
      const mi = { frustration:'😤', excitement:'🎉', worry:'😰', celebration:'🥳', stress:'😫', curiosity:'🤔', boredom:'😴', gratitude:'🙏' };
      emo = '\n🎭 ' + moods.map(m => `${mi[m.mood]||'❓'}${m.c}`).join(' ');
    }
  } catch {}

  const li = getState('last_ingest');
  const lc = getState('last_consolidate');
  const linit = getState('last_initiative');

  return `🧠 *Status*

📚 Knowledge: ${k.c} Einträge
🗄️ Archiv: ${a.c}
📥 Buffer: ${buf.c} (${buf.u || 0} offen)
💡 Proposals: ${pOpen.c} offen / ${pTotal.c} total${projLine}${emo}

⏰ Ingest: ${timeAgo(li)}
⏰ Consolidate: ${timeAgo(lc)}
⏰ Initiative: ${timeAgo(linit)}`;
}

function proposalsText(db, filter) {
  const status = filter || 'proposed';
  let sql = 'SELECT * FROM proposals';
  const params = [];
  if (status !== 'all') { sql += ' WHERE status = ?'; params.push(status); }
  sql += ' ORDER BY proposed_at DESC LIMIT 10';

  const rows = db.prepare(sql).all(...params);
  if (rows.length === 0) return `Nix offen (${status}). Alles erledigt 👍`;

  // Save digest IDs for NL-feedback
  updateState('last_digest_ids', JSON.stringify(rows.map(r => r.id)));
  updateState('last_digest_at', new Date().toISOString());

  const eff = { quick:'⚡', medium:'🔧', large:'🏗️' };
  const cat = { automation:'🤖', project:'📦', tool:'🔨', optimization:'⚡', fix:'🔧', social:'🎭', follow_up:'📌', learning:'📚' };

  let t = `💡 *Offene Vorschläge:*\n\n`;
  for (const p of rows) {
    const effort = p.effort_estimate || 'medium';
    const type = p.type || 'optimization';
    t += `${cat[type]||'💡'} *#${p.id} ${p.title}*\n${p.description}`;
    if (p.follow_up) t += `\n💬 _${p.follow_up}_`;
    t += `\n${eff[effort]||''} ${effort}\n\n`;
  }
  return t + '_/accept <ID...> | /reject <ID...> | /drop <ID...>_';
}

function projectsText(db, filter) {
  const status = (filter || 'active').toLowerCase();
  let rows;
  if (status === 'all') {
    rows = db.prepare('SELECT * FROM projects ORDER BY started_at DESC LIMIT 20').all();
  } else {
    rows = db.prepare('SELECT * FROM projects WHERE status = ? ORDER BY started_at DESC LIMIT 20').all(status);
  }

  if (rows.length === 0) return `📦 No projects (${status}). Nothing tracked yet.`;

  const icons = { active: '🔄', completed: '✅', paused: '⏸️', abandoned: '🚫' };
  let t = `📦 *Projects (${status}):*\n\n`;
  for (const p of rows) {
    const age = Math.floor((Date.now() - new Date(p.started_at).getTime()) / 86400000);
    t += `${icons[p.status] || '📦'} *#${p.id} ${p.title}*\n`;
    t += `${p.description.slice(0, 120)}${p.description.length > 120 ? '...' : ''}\n`;
    t += `📅 ${age}d old`;
    if (p.completed_at) t += ` | ✅ ${new Date(p.completed_at).toLocaleDateString('de-DE')}`;
    if (p.notes) t += `\n💬 _${p.notes}_`;
    t += '\n\n';
  }

  if (status === 'active') {
    t += '_/complete <proposal-ID> – Mark as done_';
  }
  return t;
}

function feedbackAction(db, args, newStatus) {
  if (!args) return `❌ Format: /accept <ID...> [Kommentar]\nBeispiel: /accept 3 oder /accept 1 3 5`;

  // === Handle "all" variants ===
  if (args.toLowerCase().startsWith('all')) {
    return feedbackAll(db, newStatus, args.slice(3).trim());
  }

  // === Parse IDs and optional comment ===
  const { ids, comment } = parseIdsAndComment(args);

  if (ids.length === 0) return `❌ Keine gültigen IDs gefunden.`;

  // === Bulk execute in transaction ===
  const icons = { accepted:'✅', rejected:'❌', deferred:'⏸️', completed:'🏁', dead:'💀' };
  const results = [];

  const update = db.prepare(`
    UPDATE proposals SET status = ?, user_feedback = ?, resolved_at = datetime('now')
    WHERE id = ?
  `);
  const selectOne = db.prepare('SELECT * FROM proposals WHERE id = ?');

  const transaction = db.transaction(() => {
    for (const id of ids) {
      const p = selectOne.get(id);
      if (!p) {
        results.push({ id, ok: false });
        continue;
      }
      update.run(newStatus, comment, id);
      logProposalEvent(id, newStatus, comment);
      results.push({ id, ok: true, title: p.title, followUp: p.follow_up });
    }
  });

  transaction();

  // Update throttle
  updateThrottle(newStatus);

  // Format response
  let response = '';
  for (const r of results) {
    if (!r.ok) {
      response += `❌ #${r.id} nicht gefunden.\n`;
    } else {
      response += `${icons[newStatus]||'📝'} *#${r.id}* "${r.title}" → *${newStatus}*\n`;
    }
  }

  if (ids.length > 1) {
    const okCount = results.filter(r => r.ok).length;
    response += `\n📊 ${okCount}/${ids.length} → ${newStatus}`;
  }

  // After accept: show follow-up for single proposal + create project
  const accepted = results.filter(r => r.ok && newStatus === 'accepted');
  if (accepted.length > 0) {
    for (const r of accepted) {
      const project = createProjectFromProposal(r.id);
      if (project) {
        response += `\n📦 Project #${project.id} created`;
      }
    }
    if (accepted.length === 1 && accepted[0].followUp) {
      response += `\n\n${accepted[0].followUp}`;
    } else if (accepted.length === 1) {
      response += `\n\nSoll ich das direkt angehen?`;
    }
  }

  // After complete: mark project as completed
  const completed = results.filter(r => r.ok && newStatus === 'completed');
  if (completed.length > 0) {
    for (const r of completed) {
      const project = completeProject(r.id);
      if (project) {
        response += `\n🏁 Project "${project.title}" completed`;
      }
    }
  }

  // After drop: archive related knowledge entries
  const dropped = results.filter(r => r.ok && newStatus === 'dead');
  if (dropped.length > 0) {
    for (const r of dropped) {
      const archived = archiveKnowledgeForProposal(r.id);
      if (archived > 0) {
        response += `\n🗄️ ${archived} knowledge entries archived`;
      }
    }
  }

  if (comment) response += `\n💬 ${comment}`;

  return response;
}

/**
 * Handle /accept all, /drop all older_than 14d
 */
function feedbackAll(db, newStatus, extraArgs) {
  let where = "status = 'proposed'";
  let label = 'alle offenen';

  const olderMatch = extraArgs.match(/older_than\s+(\d+[dwmh]?)/i);
  if (olderMatch) {
    const days = parseDuration(olderMatch[1]);
    if (days) {
      where += ` AND proposed_at < datetime('now', '-${days} days')`;
      label = `alle > ${days}d alten`;
    }
  }

  const proposals = db.prepare(`SELECT id FROM proposals WHERE ${where}`).all();
  if (proposals.length === 0) return `Nix gefunden (${label}). Alles erledigt 👍`;

  const ids = proposals.map(p => p.id);
  const icons = { accepted:'✅', rejected:'❌', dead:'💀', deferred:'⏸️' };

  const update = db.prepare(`
    UPDATE proposals SET status = ?, user_feedback = ?, resolved_at = datetime('now')
    WHERE id = ?
  `);

  const transaction = db.transaction(() => {
    for (const id of ids) {
      update.run(newStatus, `bulk: ${label}`, id);
      logProposalEvent(id, newStatus, `bulk: ${label}`);
    }
  });

  transaction();
  updateThrottle(newStatus);

  // Bulk archive knowledge for dropped proposals
  let archivedCount = 0;
  if (newStatus === 'dead') {
    for (const id of ids) {
      archivedCount += archiveKnowledgeForProposal(id);
    }
  }

  let response = `${icons[newStatus]||'📝'} ${ids.length} Proposals (${label}) → *${newStatus}*`;
  if (archivedCount > 0) {
    response += `\n🗄️ ${archivedCount} knowledge entries archived`;
  }
  return response;
}

/**
 * Parse IDs and optional comment from args string.
 * "1 3 5" → {ids:[1,3,5], comment:null}
 * "3 gute idee" → {ids:[3], comment:"gute idee"}
 */
function parseIdsAndComment(argsStr) {
  const parts = argsStr.split(/\s+/);
  const ids = [];
  const commentParts = [];
  let doneWithIds = false;

  for (const part of parts) {
    if (doneWithIds) {
      commentParts.push(part);
      continue;
    }
    const cleaned = part.replace(/^#/, '');
    if (/^\d+$/.test(cleaned)) {
      ids.push(parseInt(cleaned));
    } else {
      doneWithIds = true;
      commentParts.push(part);
    }
  }

  return {
    ids,
    comment: commentParts.length > 0 ? commentParts.join(' ') : null,
  };
}

/**
 * /mute 1d | 1w | 2h
 */
function handleMute(args) {
  if (!args) return '❌ Format: /mute <dauer> (z.B. 1d, 1w, 2h)';
  const hours = parseDurationHours(args.trim());
  if (!hours) return `❌ Unbekannte Dauer: ${args}. Nutze z.B. 1d, 1w, 2h`;

  const until = new Date(Date.now() + hours * 3600000);
  updateState('mute_until', until.toISOString());
  return `🔇 *Muted* bis ${until.toLocaleDateString('de-DE')} ${until.toLocaleTimeString('de-DE', {hour:'2-digit',minute:'2-digit'})}`;
}

function handleUnmute() {
  updateState('mute_until', null);
  return '🔊 *Unmuted.* Notifications sind wieder aktiv.';
}

/**
 * Check if text looks like proposal feedback (for NL fallback).
 */
function looksLikeFeedback(text) {
  const feedbackWords = /\b(nimm|nehm|akzeptier|annehm|ablehnen|reject|accept|drop|weg|gut|passt|mach|rest|ignor|ersten?|letzten?|alle)\b/i;
  return feedbackWords.test(text);
}

/**
 * Natural language feedback mapping via LLM.
 */
async function handleNLFeedback(db, text, lastDigestJson) {
  try {
    const digestIds = JSON.parse(lastDigestJson);
    const proposals = db.prepare(
      `SELECT id, title FROM proposals WHERE id IN (${digestIds.map(() => '?').join(',')})`
    ).all(...digestIds);

    if (proposals.length === 0) return null;

    const proposalList = proposals.map(p => `#${p.id}: ${p.title}`).join('\n');

    const result = await chatJSON({
      role: 'dedup', // reuse cheap model
      messages: [{
        role: 'user',
        content: `Mappe diese Anweisung auf Feedback-Aktionen für die Proposals.

Anweisung: "${text}"

Proposals:
${proposalList}

Antworte NUR als JSON-Array:
[{"id": <number>, "action": "accept"|"reject"|"defer"|"drop"}]
Nur IDs aus der Liste. NUR JSON.`
      }],
      maxTokens: 300
    });

    if (!Array.isArray(result) || result.length === 0) return null;

    const statusMap = { accept: 'accepted', reject: 'rejected', defer: 'deferred', drop: 'dead' };
    const icons = { accepted:'✅', rejected:'❌', deferred:'⏸️', dead:'💀' };
    let response = '🤖 *NL-Feedback verstanden:*\n\n';

    const transaction = db.transaction(() => {
      for (const item of result) {
        const status = statusMap[item.action];
        if (!status || !item.id) continue;
        const p = db.prepare('SELECT title FROM proposals WHERE id = ?').get(item.id);
        if (!p) continue;
        db.prepare(`
          UPDATE proposals SET status = ?, resolved_at = datetime('now') WHERE id = ?
        `).run(status, item.id);
        logProposalEvent(item.id, status, `NL: ${text.slice(0, 100)}`);
        response += `${icons[status]} #${item.id} "${p.title}" → ${status}\n`;
      }
    });

    transaction();
    return response;
  } catch (err) {
    console.error(`[BOT] NL feedback error: ${err.message}`);
    return null;
  }
}

/**
 * Auto-throttle based on feedback patterns.
 */
function updateThrottle(lastAction) {
  const streak = getState('rejection_streak') || '0';
  let count = parseInt(streak);

  if (['rejected', 'dead'].includes(lastAction)) {
    count++;
  } else if (lastAction === 'accepted') {
    count = Math.max(0, count - 2);
  }

  updateState('rejection_streak', String(count));

  if (count >= 5) {
    updateState('proposal_throttle', '1');
  } else if (count === 0) {
    const current = getState('proposal_throttle');
    if (current === '1') updateState('proposal_throttle', null);
  }
}

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

function searchText(db, query) {
  if (!query) return '❌ Format: /search <Begriff>';

  const escaped = query.replace(/[^\w\säöüÄÖÜß-]/g, ' ')
    .split(/\s+/).filter(w => w.length > 1)
    .map(w => `"${w}"`).join(' OR ');

  if (!escaped) return '❌ Keine sinnvollen Suchbegriffe.';

  let results = [];
  try {
    results = db.prepare(`
      SELECT ke.id, ke.category, ke.title, ke.summary
      FROM knowledge_fts fts
      JOIN knowledge_entries ke ON ke.id = fts.rowid
      WHERE knowledge_fts MATCH ?
      ORDER BY rank LIMIT 5
    `).all(escaped);
  } catch {}

  if (results.length === 0) return `🔍 Keine Ergebnisse für "${query}".`;

  let t = `🔍 *"${query}"*\n\n`;
  for (const r of results) {
    t += `[${r.category}] *${r.title}*\n${r.summary?.slice(0, 100)}...\n\n`;
  }
  return t;
}

function moodText(db) {
  try {
    const moods = db.prepare(`
      SELECT mood, COUNT(*) as c, MAX(detected_at) as latest
      FROM social_context
      WHERE detected_at > datetime('now', '-7 days')
      GROUP BY mood ORDER BY c DESC
    `).all();

    if (moods.length === 0) return '🎭 Keine Emotionen in den letzten 7 Tagen erfasst.';

    const mi = { frustration:'😤', excitement:'🎉', worry:'😰', celebration:'🥳', stress:'😫', curiosity:'🤔', boredom:'😴', gratitude:'🙏' };
    let t = '🎭 *Stimmungspuls (7 Tage)*\n\n';
    for (const m of moods) {
      const bar = '█'.repeat(Math.min(m.c, 15));
      t += `${mi[m.mood]||'❓'} ${m.mood}: ${bar} ${m.c}\n`;
    }

    // Stale frustrations
    try {
      const stale = db.prepare('SELECT COUNT(*) as c FROM v_stale_frustrations WHERE days_ago > 3').get();
      if (stale.c > 0) t += `\n⚠️ ${stale.c} ungelöste Frustration(en) > 3 Tage`;
    } catch {}

    return t;
  } catch {
    return '🎭 Social tables nicht verfügbar.';
  }
}

function timeAgo(isoStr) {
  if (!isoStr) return 'nie';
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `vor ${mins}min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `vor ${hours}h`;
  return `vor ${Math.floor(hours / 24)}d`;
}

// === Telegram API Helpers ===

function getUpdates(token, offset) {
  return telegramAPI(token, 'getUpdates', {
    offset, timeout: POLL_TIMEOUT, allowed_updates: ['message']
  }).then(r => r.result || []);
}

function sendMessage(token, chatId, text) {
  return telegramAPI(token, 'sendMessage', {
    chat_id: chatId, text, parse_mode: 'Markdown',
    disable_web_page_preview: true
  });
}

function telegramAPI(token, method, body) {
  const data = JSON.stringify(body);
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.telegram.org',
      path: `/bot${token}/${method}`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    }, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(d);
          json.ok ? resolve(json) : reject(new Error(json.description));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.setTimeout(35000, () => { req.destroy(); reject(new Error('Telegram timeout')); });
    req.write(data);
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
process.on('SIGINT', () => { running = false; console.log('\n[BOT] Stopping...'); });
process.on('SIGTERM', () => { running = false; });

main().catch(err => { console.error('[BOT] Fatal:', err.message); process.exit(1); });
