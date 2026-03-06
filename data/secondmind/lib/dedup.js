// lib/dedup.js – Proposal deduplication: Hash → FTS Prefilter → LLM Judge
const crypto = require('crypto');
const { getDb, getConfig, logProposalEvent } = require('./db');
const { checkDuplicate } = require('./extractor');
const { ftsEscape } = require('./search');

// German + English stopwords (compact set)
const STOPWORDS = new Set([
  // DE
  'der', 'die', 'das', 'ein', 'eine', 'einer', 'eines', 'einem', 'einen',
  'und', 'oder', 'aber', 'auch', 'als', 'mit', 'von', 'zu', 'für', 'auf',
  'ist', 'sind', 'war', 'wird', 'werden', 'hat', 'haben', 'kann', 'könnte',
  'soll', 'sollte', 'muss', 'noch', 'schon', 'nicht', 'nur', 'sehr', 'mehr',
  'bei', 'nach', 'über', 'unter', 'durch', 'aus', 'bis', 'wenn', 'weil',
  'dass', 'sich', 'man', 'es', 'ich', 'du', 'er', 'sie', 'wir', 'ihr',
  'dem', 'den', 'des', 'im', 'am', 'zum', 'zur', 'ins', 'ans',
  'was', 'wie', 'wer', 'wo', 'mal', 'dann', 'denn', 'doch', 'so',
  'diese', 'dieser', 'dieses', 'jetzt', 'hier', 'da', 'dort',
  // EN
  'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
  'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
  'will', 'would', 'could', 'should', 'may', 'might', 'can',
  'for', 'of', 'to', 'in', 'on', 'at', 'by', 'with', 'from',
  'not', 'no', 'it', 'its', 'this', 'that', 'which', 'who', 'what',
  'how', 'all', 'each', 'some', 'any', 'if', 'then', 'so', 'as',
  'up', 'out', 'about', 'into', 'just', 'also', 'very', 'more',
  'your', 'you', 'my', 'our', 'their', 'his', 'her',
]);

/**
 * Generate a normalized topic hash from title + description.
 * Cheap fast-path dedup – catches obvious duplicates without any API calls.
 */
function generateTopicHash(title, description = '') {
  const text = `${title} ${description}`.toLowerCase();

  const normalized = text
    // Normalize version numbers: v1.2.3, 1.0, etc.
    .replace(/v?\d+\.\d+(\.\d+)*/g, '_VER_')
    // Normalize IPs
    .replace(/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/g, '_IP_')
    // Normalize ports
    .replace(/:\d{2,5}\b/g, '_PORT_')
    // Normalize paths
    .replace(/\/[\w\-\/.]+/g, '_PATH_')
    // Remove special chars
    .replace(/[^a-zäöüß\s_]/g, ' ')
    // Split, filter stopwords, sort
    .split(/\s+/)
    .filter(w => w.length > 1 && !STOPWORDS.has(w))
    .sort()
    .join(' ');

  if (!normalized.trim()) return null;

  return crypto.createHash('sha256')
    .update(normalized)
    .digest('hex')
    .slice(0, 16);
}

/**
 * Find existing proposal with same topic hash.
 * Returns the proposal or null.
 */
function findDuplicateByHash(db, hash) {
  if (!hash) return null;
  return db.prepare(`
    SELECT * FROM proposals
    WHERE topic_hash = ?
    AND status NOT IN ('completed', 'dead')
    ORDER BY proposed_at DESC LIMIT 1
  `).get(hash) || null;
}

/**
 * Find candidate duplicates via FTS5 prefilter.
 * Returns max 10 proposals sorted by relevance.
 */
function findCandidatesByFTS(db, title, description = '') {
  const searchText = `${title} ${description}`;
  const escaped = ftsEscape(searchText);
  if (!escaped) return [];

  try {
    return db.prepare(`
      SELECT p.*, rank
      FROM proposals_fts fts
      JOIN proposals p ON p.id = fts.rowid
      WHERE proposals_fts MATCH ?
      AND p.status NOT IN ('completed', 'dead')
      ORDER BY rank LIMIT 10
    `).all(escaped);
  } catch {
    // FTS table empty or not ready
    return [];
  }
}

/**
 * Full dedup pipeline: Hash → FTS → LLM
 * Returns: { isDuplicate, action, matchedId, matchedProposal, message }
 */
async function dedupCheck(db, newProposal, config) {
  const threshold = config.initiative?.dedupThreshold || 0.85;
  const hash = generateTopicHash(newProposal.title, newProposal.description);

  // === Stufe 0: Hash Match ===
  if (hash) {
    const hashMatch = findDuplicateByHash(db, hash);
    if (hashMatch) {
      console.log(`[DEDUP] Hash match: "${newProposal.title}" ≈ #${hashMatch.id} "${hashMatch.title}"`);
      return {
        isDuplicate: true,
        method: 'hash',
        matchedId: hashMatch.id,
        matchedProposal: hashMatch,
        ...resolveAction(db, hashMatch),
      };
    }
  }

  // === Stufe 1: FTS Prefilter ===
  const candidates = findCandidatesByFTS(db, newProposal.title, newProposal.description);
  if (candidates.length === 0) {
    return { isDuplicate: false, topicHash: hash };
  }

  // === Stufe 2: LLM Judge (only Top 10 from FTS) ===
  try {
    const result = await checkDuplicate(newProposal, candidates.map(c => ({
      id: c.id,
      title: c.title,
      description: (c.description || '').slice(0, 100),
    })));

    if (result && result.is_duplicate && result.confidence >= threshold && result.match_id) {
      const matched = candidates.find(c => c.id === result.match_id);
      if (matched) {
        console.log(`[DEDUP] LLM match (${result.confidence}): "${newProposal.title}" ≈ #${matched.id} "${matched.title}"`);
        return {
          isDuplicate: true,
          method: 'llm',
          confidence: result.confidence,
          matchedId: matched.id,
          matchedProposal: matched,
          ...resolveAction(db, matched),
        };
      }
    }
  } catch (err) {
    console.warn(`[DEDUP] LLM check failed: ${err.message}. Proceeding as new.`);
  }

  return { isDuplicate: false, topicHash: hash };
}

/**
 * Decide what to do with a duplicate based on the original's status.
 * Returns: { action, message }
 */
function resolveAction(db, original) {
  const status = original.status;

  switch (status) {
    case 'proposed': {
      // Bump the existing proposal
      db.prepare(`
        UPDATE proposals
        SET times_presented = times_presented + 1,
            last_presented_at = datetime('now')
        WHERE id = ?
      `).run(original.id);
      logProposalEvent(original.id, 'dedup_hit', 'Same topic resurfaced – bumped');
      return {
        action: 'bump',
        message: null, // Silent – don't spam about it
      };
    }

    case 'deferred': {
      // Nudge: topic came back, remind the user
      const nudgeCount = db.prepare(`
        SELECT COUNT(*) as c FROM proposal_events
        WHERE proposal_id = ? AND action = 'nudge'
      `).get(original.id)?.c || 0;

      const maxNudges = 2;
      if (nudgeCount >= maxNudges) {
        db.prepare("UPDATE proposals SET status = 'dead' WHERE id = ?").run(original.id);
        logProposalEvent(original.id, 'dead', `Max ${maxNudges} nudges reached – auto-archived`);
        return { action: 'auto_dead', message: null };
      }

      logProposalEvent(original.id, 'dedup_hit', 'Topic resurfaced while deferred');
      logProposalEvent(original.id, 'nudge', 'Reminder because topic resurfaced');
      return {
        action: 'nudge',
        message: `Das Thema "${original.title}" taucht wieder auf – willst du's diesmal angehen oder soll ich's endgültig droppen?`,
      };
    }

    case 'accepted':
    case 'in_progress': {
      logProposalEvent(original.id, 'dedup_hit', 'Topic resurfaced – already in progress');
      return {
        action: 'already_active',
        message: null, // Don't nag about stuff they already accepted
      };
    }

    case 'rejected': {
      // Only resurface if there's genuinely new context.
      // Since we got here via LLM, the LLM already found it similar –
      // so we DON'T create a new proposal. Respect the rejection.
      logProposalEvent(original.id, 'dedup_hit', 'Topic resurfaced after rejection – suppressed');
      return {
        action: 'suppressed',
        message: null,
      };
    }

    default:
      return { action: 'skip', message: null };
  }
}

module.exports = {
  generateTopicHash,
  findDuplicateByHash,
  findCandidatesByFTS,
  dedupCheck,
};
