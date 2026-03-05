#!/usr/bin/env node
// scripts/initiative.js – Proactive Initiative Engine v1.3.0
// Features: Archive Retrieval, Dedup Pipeline, Gentle Reminders,
//           Conversation Opener Heuristic, Auto-Throttle, Mute Support
const { getDb, getConfig, acquireLock, releaseLock, updateState, getState, logProposalEvent, getProjects } = require('../lib/db');
const { generateInitiative } = require('../lib/extractor');
const { notifyProposals, notifyNudges } = require('../lib/notifier');
const { dedupCheck, generateTopicHash } = require('../lib/dedup');
const { search } = require('../lib/search');

async function runInitiative() {
  if (!acquireLock('initiative')) return;

  try {
    const db = getDb();
    const config = getConfig();

    // === MUTE CHECK ===
    const muteUntil = getState('mute_until');
    if (muteUntil && new Date(muteUntil) > new Date()) {
      console.log(`[INITIATIVE] Muted until ${muteUntil}. Skipping.`);
      return;
    }

    // === CONVERSATION OPENER HEURISTIC ===
    // Don't pile on if there's already a recent notification
    const recentNotifications = db.prepare(`
      SELECT COUNT(*) as c FROM proposal_events
      WHERE action IN ('proposed', 'nudge')
      AND created_at > datetime('now', '-6 hours')
    `).get();

    if (recentNotifications.c > 0) {
      console.log(`[INITIATIVE] Recent notification exists (${recentNotifications.c}). Checking reminders only.`);
      // Still run reminders, but skip generating new proposals
      await runReminders(db, config);
      return;
    }

    // === KNOWLEDGE CONTEXT ===
    const recentKnowledge = db.prepare(`
      SELECT id, category, title, summary, tags FROM knowledge_entries
      WHERE last_updated > datetime('now', '-24 hours')
      ORDER BY last_updated DESC LIMIT 20
    `).all();

    const openTodos = db.prepare(`
      SELECT id, title, summary, tags FROM knowledge_entries
      WHERE category = 'todo' AND status = 'active' LIMIT 10
    `).all();

    const unresolvedProblems = db.prepare(`
      SELECT id, title, summary, tags FROM knowledge_entries
      WHERE category = 'problem' AND status = 'active' LIMIT 10
    `).all();

    const stalledProjects = db.prepare(`
      SELECT id, title, summary, tags FROM knowledge_entries
      WHERE category = 'project' AND status = 'active'
      AND last_updated < datetime('now', '-3 days') LIMIT 5
    `).all();

    // === SOCIAL INTELLIGENCE CONTEXT ===
    let staleFrustrations = [];
    try {
      staleFrustrations = db.prepare(`
        SELECT person, trigger_text, topic_ref, days_ago, problem_title, problem_status
        FROM v_stale_frustrations
        WHERE days_ago > 3
        LIMIT 5
      `).all();
    } catch { /* View might not exist on first run */ }

    let upcomingEvents = [];
    try {
      upcomingEvents = db.prepare(`
        SELECT person, event_type, description, event_date, days_until
        FROM v_upcoming_events
        LIMIT 5
      `).all();
    } catch { /* View might not exist */ }

    const recentMoods = db.prepare(`
      SELECT mood, COUNT(*) as count, MAX(detected_at) as latest
      FROM social_context
      WHERE detected_at > datetime('now', '-7 days')
      GROUP BY mood ORDER BY count DESC LIMIT 5
    `).all();

    // === PROPOSAL CONTEXT ===
    // Full blacklist: ALL rejected/dead/completed titles (never suggest again)
    const blacklistedTitles = db.prepare(`
      SELECT DISTINCT title FROM proposals
      WHERE status IN ('rejected', 'dead', 'completed')
    `).all().map(r => r.title);

    // Recent proposals (any status) - so LLM knows what's already in pipeline
    const recentProposals = db.prepare(`
      SELECT title, type, status FROM proposals
      WHERE proposed_at > datetime('now', '-30 days')
    `).all();

    const feedbackStats = db.prepare(`
      SELECT
        COUNT(CASE WHEN status='accepted' THEN 1 END) as accepted,
        COUNT(CASE WHEN status='rejected' THEN 1 END) as rejected,
        COUNT(CASE WHEN status='dead' THEN 1 END) as dead,
        GROUP_CONCAT(DISTINCT CASE WHEN status='rejected' THEN type END) as rejected_types
      FROM proposals WHERE proposed_at > datetime('now', '-30 days')
    `).get();

    // Feedback profile by type (learning signal)
    const feedbackProfile = db.prepare(`
      SELECT
        type,
        COUNT(CASE WHEN status='accepted' THEN 1 END) as accepted,
        COUNT(CASE WHEN status IN ('rejected','dead') THEN 1 END) as rejected
      FROM proposals
      WHERE proposed_at > datetime('now', '-30 days')
      GROUP BY type
    `).all();

    if (blacklistedTitles.length > 0) {
      console.log(`[INITIATIVE] 🚫 ${blacklistedTitles.length} blacklisted topic(s)`);
    }

    // === PROJECTS CONTEXT ===
    let activeProjects = [];
    let completedProjects = [];
    try {
      activeProjects = getProjects('active');
      completedProjects = getProjects('completed');
      if (activeProjects.length > 0) {
        console.log(`[INITIATIVE] 📦 ${activeProjects.length} active project(s), ${completedProjects.length} completed`);
      }
    } catch { /* table might not exist yet */ }

    // Skip if no activity at all
    if (recentKnowledge.length === 0 && openTodos.length === 0
        && unresolvedProblems.length === 0 && staleFrustrations.length === 0
        && upcomingEvents.length === 0) {
      console.log('[INITIATIVE] No activity. Skipping.');
      // Still run reminders even without new activity
      await runReminders(db, config);
      return;
    }

    // === ARCHIVE RETRIEVAL ===
    const contextKeywords = [
      ...recentKnowledge.map(k => k.title),
      ...unresolvedProblems.map(p => p.title),
      ...openTodos.map(t => t.title),
      ...stalledProjects.map(p => p.title),
    ].join(' ');

    let archiveContext = [];
    if (contextKeywords.trim()) {
      try {
        const archiveLimit = config.initiative?.archiveRetrievalLimit || 10;
        archiveContext = await search(contextKeywords, {
          limit: archiveLimit,
          rerank: true,
          tier: 'longterm',
        });
        if (archiveContext.length > 0) {
          console.log(`[INITIATIVE] 📚 ${archiveContext.length} archive hit(s) for context`);
        }
      } catch (err) {
        console.warn(`[INITIATIVE] Archive retrieval failed: ${err.message}`);
      }
    }

    console.log('[INITIATIVE] Analyzing...');
    if (staleFrustrations.length > 0)
      console.log(`[INITIATIVE] 🎭 ${staleFrustrations.length} stale frustration(s) detected`);
    if (upcomingEvents.length > 0)
      console.log(`[INITIATIVE] 📅 ${upcomingEvents.length} upcoming event(s)`);

    // === LLM ANALYSIS ===
    const suggestions = await generateInitiative({
      recent: recentKnowledge,
      todos: openTodos,
      problems: unresolvedProblems,
      stalled_projects: stalledProjects,
      stale_frustrations: staleFrustrations,
      upcoming_events: upcomingEvents,
      recent_moods: recentMoods,
      already_proposed: recentProposals,
      blacklisted_titles: blacklistedTitles,
      feedback_stats: feedbackStats,
      feedback_profile: feedbackProfile,
      active_projects: activeProjects.map(p => ({
        id: p.id, title: p.title, description: p.description,
        started_at: p.started_at,
      })),
      completed_projects: completedProjects.map(p => ({
        id: p.id, title: p.title,
        completed_at: p.completed_at,
      })),
      archive_context: archiveContext.map(h => ({
        title: h.title,
        summary: h.summary,
        category: h.category,
        tags: h.tags,
      })),
      current_time: new Date().toISOString(),
    });

    // Normalize: LLM might return single object instead of array
    const proposalList = Array.isArray(suggestions)
      ? suggestions
      : (suggestions && typeof suggestions === 'object' && suggestions.title)
        ? [suggestions]
        : [];

    if (proposalList.length === 0) {
      console.log('[INITIATIVE] No suggestions.');
      await runReminders(db, config);
      return;
    }

    // === AUTO-THROTTLE: Check if we should reduce proposals ===
    const throttle = getState('proposal_throttle');
    const maxProposals = throttle === '1' ? 1 : (config.initiative?.maxProposalsPerRun || 3);

    // === INSERT PROPOSALS (with Dedup Pipeline) ===
    const insertProposal = db.prepare(`
      INSERT INTO proposals (type, title, description, reasoning, follow_up, source_ids, priority, effort_estimate, topic_hash)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    let inserted = 0;
    const nudgeMessages = [];

    for (const s of proposalList.slice(0, maxProposals)) {
      if (!s.title || !s.description) continue;

      // === HARD BLACKLIST CHECK (safety net if LLM ignores instructions) ===
      const titleLower = s.title.toLowerCase();
      const descLower = (s.description || '').toLowerCase();
      const proposalText = titleLower + ' ' + descLower;

      const isBlacklisted = blacklistedTitles.some(bt => {
        const btLower = bt.toLowerCase();
        // Exact title match
        if (titleLower === btLower) return true;
        // Extract significant words (>3 chars) from blacklisted title
        const btWords = btLower.split(/\s+/).filter(w => w.length > 3);
        if (btWords.length === 0) return false;
        // Count how many blacklisted keywords appear in new proposal (title + description)
        const hits = btWords.filter(w => proposalText.includes(w));
        // If >=50% of blacklisted keywords found → match
        return hits.length >= btWords.length * 0.5;
      });

      if (isBlacklisted) {
        console.log(`[INITIATIVE] 🚫 Blacklist hit: "${s.title}" – skipped`);
        continue;
      }

      // === DEDUP PIPELINE ===
      const dedupResult = await dedupCheck(db, {
        title: s.title,
        description: s.description,
      }, config);

      if (dedupResult.isDuplicate) {
        const icon = dedupResult.method === 'hash' ? '🔗' : '🧠';
        console.log(`[INITIATIVE] ${icon} Dedup (${dedupResult.method}): "${s.title}" → ${dedupResult.action} (matched #${dedupResult.matchedId})`);

        if (dedupResult.action === 'nudge' && dedupResult.message) {
          nudgeMessages.push({
            id: dedupResult.matchedId,
            title: dedupResult.matchedProposal.title,
            message: dedupResult.message,
          });
        }
        continue;
      }

      // === INSERT NEW PROPOSAL ===
      const hash = dedupResult.topicHash || generateTopicHash(s.title, s.description);

      insertProposal.run(
        s.type || 'optimization', s.title, s.description,
        s.reasoning || null, s.follow_up || null,
        JSON.stringify(s.sources || []),
        s.priority || 'medium', s.effort || 'medium',
        hash
      );

      // Log event
      const newId = db.prepare('SELECT last_insert_rowid() as id').get().id;
      logProposalEvent(newId, 'proposed', null);

      inserted++;

      const icon = s.type === 'social' ? '🎭' : s.type === 'follow_up' ? '📚' : '💡';
      console.log(`[INITIATIVE] ${icon} ${s.priority?.toUpperCase()}: ${s.title}`);
    }

    updateState('last_initiative');
    console.log(`[INITIATIVE] Done. ${inserted} new proposal(s), ${nudgeMessages.length} nudge(s).`);

    // === SEND NOTIFICATIONS ===
    if (inserted > 0) {
      const newProposals = db.prepare(
        "SELECT * FROM proposals ORDER BY proposed_at DESC LIMIT ?"
      ).all(inserted);
      try {
        await notifyProposals(newProposals);
      } catch (err) {
        console.error(`[INITIATIVE] Notification failed: ${err.message}`);
      }
    }

    // Send nudge notifications
    if (nudgeMessages.length > 0) {
      try {
        await notifyNudges(nudgeMessages);
      } catch (err) {
        console.error(`[INITIATIVE] Nudge notification failed: ${err.message}`);
      }
    }

    // === RUN REMINDERS ===
    await runReminders(db, config);

  } finally {
    releaseLock('initiative');
  }
}

/**
 * Gentle Reminder Engine: Check deferred + stalled accepted proposals.
 */
async function runReminders(db, config) {
  const cooldownDays = config.initiative?.reminderCooldownDays || 7;
  const maxNudges = config.initiative?.maxNudgesPerProposal || 2;
  const nudges = [];

  // === Deferred proposals past cooldown ===
  try {
    const deferred = db.prepare(`
      SELECT p.*,
        (SELECT COUNT(*) FROM proposal_events pe
         WHERE pe.proposal_id = p.id AND pe.action = 'nudge') as nudge_count,
        (SELECT MAX(pe.created_at) FROM proposal_events pe
         WHERE pe.proposal_id = p.id) as last_event_at
      FROM proposals p
      WHERE p.status = 'deferred'
      AND julianday('now') - julianday(
        COALESCE((SELECT MAX(pe.created_at) FROM proposal_events pe
                  WHERE pe.proposal_id = p.id), p.proposed_at)
      ) > ?
    `).all(cooldownDays);

    for (const p of deferred) {
      if (p.nudge_count >= maxNudges) {
        // Max nudges reached → auto-dead
        db.prepare("UPDATE proposals SET status = 'dead' WHERE id = ?").run(p.id);
        logProposalEvent(p.id, 'dead', `Max ${maxNudges} nudges reached – auto-archived`);
        console.log(`[REMINDER] 💀 #${p.id} "${p.title}" → dead (max nudges)`);
        continue;
      }

      logProposalEvent(p.id, 'nudge', 'Cooldown reminder');
      nudges.push({
        id: p.id,
        title: p.title,
        message: `Du hattest das verschoben – immer noch relevant?`,
      });
      console.log(`[REMINDER] 🔔 #${p.id} "${p.title}" → nudge (${p.nudge_count + 1}/${maxNudges})`);
    }
  } catch (err) {
    console.warn(`[REMINDER] Deferred check failed: ${err.message}`);
  }

  // === Accepted proposals without progress (>14 days) ===
  try {
    const stalled = db.prepare(`
      SELECT * FROM proposals
      WHERE status = 'accepted'
      AND julianday('now') - julianday(COALESCE(resolved_at, proposed_at)) > 14
      AND id NOT IN (
        SELECT proposal_id FROM proposal_events
        WHERE action = 'nudge'
        AND created_at > datetime('now', '-7 days')
      )
    `).all();

    for (const p of stalled) {
      logProposalEvent(p.id, 'nudge', 'Stalled accepted – progress check');
      nudges.push({
        id: p.id,
        title: p.title,
        message: `Hey, die Sache mit "${p.title}" – brauchst du Hilfe oder soll ich's droppen?`,
      });
      console.log(`[REMINDER] ⏳ #${p.id} "${p.title}" → stalled reminder`);
    }
  } catch (err) {
    console.warn(`[REMINDER] Stalled check failed: ${err.message}`);
  }

  // === Ignored proposals (shown 2+ times, never interacted) ===
  try {
    const ignored = db.prepare(`
      SELECT * FROM proposals
      WHERE status = 'proposed'
      AND times_presented >= 2
    `).all();

    for (const p of ignored) {
      db.prepare("UPDATE proposals SET status = 'dead' WHERE id = ?").run(p.id);
      logProposalEvent(p.id, 'dead', 'Ignored 2+ times – auto-archived');
      console.log(`[REMINDER] 👻 #${p.id} "${p.title}" → dead (ignored 2x)`);
    }
  } catch (err) {
    console.warn(`[REMINDER] Ignored check failed: ${err.message}`);
  }

  // Send nudge notifications
  if (nudges.length > 0) {
    try {
      await notifyNudges(nudges);
    } catch (err) {
      console.error(`[REMINDER] Nudge notification failed: ${err.message}`);
    }
  }
}

runInitiative().catch(err => {
  console.error('[INITIATIVE] Fatal:', err.message);
  releaseLock('initiative');
  process.exit(1);
});
