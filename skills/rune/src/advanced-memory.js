/**
 * advanced-memory.js - Phase 9: Advanced Memory Features
 * T-049: Memory consolidation, T-050: Forgetting curves, T-051: Temporal queries
 * T-052: Cross-session reasoning, T-053: Decision changelog
 */

import { openDb } from './db.js';
import { scoreFactsForRelevance } from './relevance.js';

const TEMPORAL_PATTERNS = [
  // Relative time expressions
  { pattern: /last\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i, type: 'last_weekday' },
  { pattern: /this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i, type: 'this_weekday' },
  { pattern: /last\s+week/i, type: 'last_week' },
  { pattern: /this\s+week/i, type: 'this_week' },
  { pattern: /(\d+)\s+days?\s+ago/i, type: 'days_ago' },
  { pattern: /(\d+)\s+weeks?\s+ago/i, type: 'weeks_ago' },
  { pattern: /yesterday/i, type: 'yesterday' },
  { pattern: /last\s+month/i, type: 'last_month' },
  // Specific dates
  { pattern: /(\d{4}-\d{2}-\d{2})/i, type: 'iso_date' },
  { pattern: /(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})/i, type: 'month_day' }
];

/**
 * Memory consolidation - merge similar facts, compress verbose ones (T-049)
 */
async function consolidateMemory(options = {}) {
  const { 
    dryRun = false, 
    similarityThreshold = 0.8, 
    compressLong = false, 
    autoPrioritize = false 
  } = options;
  
  const db = openDb();
  
  try {
    // Get all facts for analysis
    const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC').all();
    
    if (allFacts.length === 0) {
      return { merged: 0, compressed: 0, prioritized: 0, spaceSaved: 0 };
    }
    
    const result = {
      merged: 0,
      compressed: 0,
      prioritized: 0,
      spaceSaved: 0,
      merges: [],
      compressions: []
    };
    
    // Find mergeable facts (similar keys and categories)
    const mergeGroups = findMergeableGroups(allFacts, similarityThreshold);
    
    for (const group of mergeGroups) {
      if (group.length < 2) continue;
      
      const merged = mergeFactGroup(group);
      result.merges.push({
        sources: group,
        newKey: merged.key,
        newValue: merged.value,
        spaceSaved: group.reduce((sum, f) => sum + f.value.length, 0) - merged.value.length
      });
      
      if (!dryRun) {
        // Delete source facts and create merged fact
        const now = new Date().toISOString();
        
        for (const fact of group) {
          db.prepare('DELETE FROM facts WHERE id = ?').run(fact.id);
        }
        
        db.prepare(`
          INSERT INTO facts (category, key, value, confidence, scope, tier, 
                           source_type, updated, created)
          VALUES (?, ?, ?, ?, ?, ?, 'consolidated', ?, ?)
        `).run(
          merged.category, merged.key, merged.value, merged.confidence,
          merged.scope, merged.tier, now, now
        );
        
        result.merged++;
        result.spaceSaved += result.merges[result.merges.length - 1].spaceSaved;
      }
    }
    
    // Compress long facts
    if (compressLong) {
      const longFacts = allFacts.filter(f => f.value.length > 200);
      
      for (const fact of longFacts) {
        const compressed = await compressFact(fact);
        if (compressed && compressed.value.length < fact.value.length) {
          result.compressions.push({
            id: fact.id,
            key: fact.key,
            oldLength: fact.value.length,
            newLength: compressed.value.length,
            newValue: compressed.value
          });
          
          if (!dryRun) {
            db.prepare('UPDATE facts SET value = ? WHERE id = ?')
              .run(compressed.value, fact.id);
            
            result.compressed++;
            result.spaceSaved += fact.value.length - compressed.value.length;
          }
        }
      }
    }
    
    // Auto-prioritize by access patterns
    if (autoPrioritize && !dryRun) {
      const prioritized = db.prepare(`
        UPDATE facts SET tier = 
          CASE 
            WHEN access_count >= 10 THEN 'critical'
            WHEN access_count >= 5 THEN 'important' 
            WHEN access_count >= 2 THEN 'long-term'
            ELSE 'working'
          END
        WHERE access_count > 0
      `).run();
      
      result.prioritized = prioritized.changes;
    }
    
    return result;
    
  } finally {
    db.close();
  }
}

/**
 * Apply forgetting curve - decay confidence and archive unused facts (T-050)
 */
async function applyForgettingCurve(options = {}) {
  const { 
    dryRun = false,
    decayRate = 0.05,  // 5% decay per day
    pruneThreshold = 0.1,  // Archive facts below 0.1 confidence
    graceDays = 30  // Grace period before decay starts
  } = options;
  
  const db = openDb();
  
  try {
    // Ensure forgetting_archive table exists
    db.exec(`
      CREATE TABLE IF NOT EXISTS forgetting_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_fact_id INTEGER,
        category TEXT,
        key TEXT,
        value TEXT,
        original_confidence REAL,
        final_confidence REAL,
        days_unused INTEGER,
        archived_date TEXT,
        reason TEXT
      );
    `);
    
    const now = Date.now();
    const graceTime = graceDays * 24 * 60 * 60 * 1000;
    
    // Get facts eligible for decay
    const facts = db.prepare(`
      SELECT *, 
             COALESCE(access_count, 0) as access_count,
             COALESCE(last_accessed, created) as last_accessed
      FROM facts
      WHERE tier NOT IN ('critical', 'permanent')
    `).all();
    
    const result = {
      decayed: 0,
      archived: 0,
      avgDecay: 0,
      toDecay: [],
      toPrune: []
    };
    
    let totalDecay = 0;
    
    for (const fact of facts) {
      const lastAccess = new Date(fact.last_accessed || fact.created).getTime();
      const daysSinceAccess = (now - lastAccess) / (1000 * 60 * 60 * 24);
      
      // Skip facts within grace period
      if (daysSinceAccess < graceDays) continue;
      
      const currentConfidence = fact.confidence || 0.95;
      
      // Calculate decay
      const decayDays = daysSinceAccess - graceDays;
      const decayFactor = Math.pow(1 - decayRate, decayDays);
      const newConfidence = Math.max(0, currentConfidence * decayFactor);
      
      if (newConfidence < currentConfidence) {
        result.toDecay.push({
          id: fact.id,
          key: fact.key,
          oldConfidence: currentConfidence,
          newConfidence,
          daysSinceAccess: Math.round(daysSinceAccess)
        });
        
        totalDecay += (currentConfidence - newConfidence);
        
        if (!dryRun) {
          db.prepare('UPDATE facts SET confidence = ? WHERE id = ?')
            .run(newConfidence, fact.id);
          result.decayed++;
        }
      }
      
      // Check if should be archived
      if (newConfidence < pruneThreshold) {
        result.toPrune.push({
          id: fact.id,
          key: fact.key,
          confidence: newConfidence,
          daysSinceAccess: Math.round(daysSinceAccess)
        });
        
        if (!dryRun) {
          // Archive the fact
          const archiveDate = new Date().toISOString();
          
          db.prepare(`
            INSERT INTO forgetting_archive (
              original_fact_id, category, key, value, original_confidence,
              final_confidence, days_unused, archived_date, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
          `).run(
            fact.id, fact.category, fact.key, fact.value,
            fact.confidence || 0.95, newConfidence, Math.round(daysSinceAccess),
            archiveDate, 'confidence_decay'
          );
          
          // Remove from active facts
          db.prepare('DELETE FROM facts WHERE id = ?').run(fact.id);
          result.archived++;
        }
      }
    }
    
    result.avgDecay = result.toDecay.length > 0 ? totalDecay / result.toDecay.length : 0;
    
    return result;
    
  } finally {
    db.close();
  }
}

/**
 * Execute temporal queries like "what were we working on last Tuesday?" (T-051)
 */
async function executeTemporalQuery(query, options = {}) {
  const { limit = 20 } = options;
  
  const timeframe = parseTemporalExpression(query);
  if (!timeframe) {
    return { timeframe: null, facts: [], events: [], projects: [] };
  }
  
  const db = openDb();
  
  try {
    const result = {
      timeframe,
      facts: [],
      events: [],
      projects: []
    };
    
    // Get facts from timeframe
    result.facts = db.prepare(`
      SELECT * FROM facts
      WHERE updated BETWEEN ? AND ?
      ORDER BY updated DESC
      LIMIT ?
    `).all(timeframe.startDate, timeframe.endDate, Math.floor(limit / 2));
    
    // Get performance events from timeframe
    result.events = db.prepare(`
      SELECT * FROM performance_log
      WHERE created BETWEEN ? AND ?
      ORDER BY created DESC
      LIMIT ?
    `).all(timeframe.startDate, timeframe.endDate, Math.floor(limit / 4));
    
    // Get project activity (if table exists)
    try {
      result.projects = db.prepare(`
        SELECT * FROM project_states
        WHERE updated BETWEEN ? AND ?
           OR last_activity BETWEEN ? AND ?
        ORDER BY updated DESC
        LIMIT ?
      `).all(
        timeframe.startDate, timeframe.endDate,
        timeframe.startDate, timeframe.endDate,
        Math.floor(limit / 4)
      );
    } catch {
      // Project table doesn't exist
      result.projects = [];
    }
    
    return result;
    
  } finally {
    db.close();
  }
}

/**
 * Analyze cross-session patterns (T-052)
 */
async function analyzeCrossSessionPatterns(options = {}) {
  const { days = 90, patternType, minSessions = 3 } = options;
  const db = openDb();
  
  try {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    
    // Get session metadata if it exists
    let sessions = [];
    try {
      sessions = db.prepare(`
        SELECT * FROM session_metadata
        WHERE created > ?
        ORDER BY created ASC
      `).all(cutoffDate);
    } catch {
      // Session metadata table doesn't exist
    }
    
    // Get performance events for pattern analysis
    const events = db.prepare(`
      SELECT * FROM performance_log
      WHERE created > ?
      ORDER BY created ASC
    `).all(cutoffDate);
    
    const result = {
      sessionPatterns: [],
      behaviorPatterns: [],
      insights: []
    };
    
    // Analyze session patterns (if we have session data)
    if (sessions.length >= minSessions) {
      result.sessionPatterns = findSessionPatterns(sessions, events, minSessions);
    }
    
    // Analyze behavior patterns from events
    result.behaviorPatterns = findBehaviorPatterns(events, minSessions);
    
    // Generate insights
    result.insights = generateCrossSessionInsights(sessions, events, result.sessionPatterns);
    
    return result;
    
  } finally {
    db.close();
  }
}

/**
 * Get decision changelog with full audit trail (T-053)
 */
async function getDecisionChangelog(decision = null, options = {}) {
  const { limit = 20 } = options;
  const db = openDb();
  
  try {
    let query = `
      SELECT c.*, f.category as current_category
      FROM changelog c
      LEFT JOIN facts f ON c.key = f.key
    `;
    const params = [];
    
    if (decision) {
      query += ' WHERE LOWER(c.key) LIKE LOWER(?)';
      params.push(`%${decision}%`);
    }
    
    query += ` ORDER BY c.created DESC LIMIT ?`;
    params.push(limit);
    
    const changes = db.prepare(query).all(...params);
    
    // Group by decision/fact key for better readability
    const grouped = {};
    changes.forEach(change => {
      if (!grouped[change.key]) {
        grouped[change.key] = [];
      }
      grouped[change.key].push(change);
    });
    
    return {
      changes,
      grouped,
      totalChanges: changes.length,
      uniqueDecisions: Object.keys(grouped).length
    };
    
  } finally {
    db.close();
  }
}

/**
 * Helper functions
 */

function findMergeableGroups(facts, threshold) {
  const groups = [];
  const processed = new Set();
  
  for (let i = 0; i < facts.length; i++) {
    if (processed.has(i)) continue;
    
    const group = [facts[i]];
    processed.add(i);
    
    for (let j = i + 1; j < facts.length; j++) {
      if (processed.has(j)) continue;
      
      const similarity = calculateFactSimilarity(facts[i], facts[j]);
      if (similarity >= threshold) {
        group.push(facts[j]);
        processed.add(j);
      }
    }
    
    if (group.length > 1) {
      groups.push(group);
    }
  }
  
  return groups;
}

function calculateFactSimilarity(fact1, fact2) {
  // Must be same category
  if (fact1.category !== fact2.category) return 0;
  
  // Key similarity (Levenshtein-like)
  const keySim = stringSimilarity(fact1.key, fact2.key);
  if (keySim < 0.6) return 0;
  
  // Value similarity
  const valueSim = stringSimilarity(fact1.value, fact2.value);
  
  // Weighted combination
  return (keySim * 0.7) + (valueSim * 0.3);
}

function stringSimilarity(str1, str2) {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  const editDistance = levenshteinDistance(longer, shorter);
  return (longer.length - editDistance) / longer.length;
}

function levenshteinDistance(str1, str2) {
  const matrix = Array(str2.length + 1).fill(null).map(() => 
    Array(str1.length + 1).fill(null)
  );
  
  for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
  
  for (let j = 1; j <= str2.length; j++) {
    for (let i = 1; i <= str1.length; i++) {
      const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1,      // deletion
        matrix[j - 1][i] + 1,      // insertion
        matrix[j - 1][i - 1] + indicator // substitution
      );
    }
  }
  
  return matrix[str2.length][str1.length];
}

function mergeFactGroup(group) {
  // Take the most recent fact as base
  const base = group.sort((a, b) => new Date(b.updated) - new Date(a.updated))[0];
  
  // Combine values intelligently
  const values = group.map(f => f.value).filter((v, i, arr) => arr.indexOf(v) === i);
  const mergedValue = values.length === 1 ? values[0] : 
                     values.join(' | '); // Separate distinct values
  
  // Use highest confidence
  const maxConfidence = Math.max(...group.map(f => f.confidence || 0.95));
  
  return {
    category: base.category,
    key: base.key,
    value: mergedValue.length > 500 ? mergedValue.substring(0, 497) + '...' : mergedValue,
    confidence: maxConfidence,
    scope: base.scope,
    tier: base.tier
  };
}

async function compressFact(fact) {
  // Simple compression - remove redundancy, keep key info
  const value = fact.value;
  
  if (value.length <= 200) return null;
  
  // Remove common redundant phrases
  let compressed = value
    .replace(/\b(the|and|or|but|so|then|also|just|really|very|quite)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
  
  // If still too long, truncate intelligently
  if (compressed.length > 200) {
    const sentences = compressed.split(/[.!?]+/);
    compressed = sentences[0];
    if (compressed.length > 200) {
      compressed = compressed.substring(0, 197) + '...';
    }
  }
  
  return compressed.length < value.length ? { value: compressed } : null;
}

function parseTemporalExpression(query) {
  const queryLower = query.toLowerCase();
  
  for (const { pattern, type } of TEMPORAL_PATTERNS) {
    const match = queryLower.match(pattern);
    if (match) {
      return calculateTimeframe(type, match, query);
    }
  }
  
  return null;
}

function calculateTimeframe(type, match, originalQuery) {
  const now = new Date();
  let startDate, endDate, description;
  
  switch (type) {
    case 'yesterday':
      startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      endDate = new Date(now);
      description = 'Yesterday';
      break;
      
    case 'last_week':
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      endDate = new Date(now);
      description = 'Last week';
      break;
      
    case 'days_ago':
      const days = parseInt(match[1]);
      startDate = new Date(now.getTime() - (days + 1) * 24 * 60 * 60 * 1000);
      endDate = new Date(now.getTime() - (days - 1) * 24 * 60 * 60 * 1000);
      description = `${days} day(s) ago`;
      break;
      
    case 'weeks_ago':
      const weeks = parseInt(match[1]);
      startDate = new Date(now.getTime() - (weeks + 1) * 7 * 24 * 60 * 60 * 1000);
      endDate = new Date(now.getTime() - (weeks - 1) * 7 * 24 * 60 * 60 * 1000);
      description = `${weeks} week(s) ago`;
      break;
      
    case 'last_weekday':
      const weekday = match[1];
      const targetDay = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].indexOf(weekday.toLowerCase());
      const currentDay = now.getDay();
      let daysBack = (currentDay - targetDay + 7) % 7;
      if (daysBack === 0) daysBack = 7; // Last week's occurrence
      
      startDate = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000);
      endDate = new Date(startDate.getTime() + 24 * 60 * 60 * 1000);
      description = `Last ${weekday}`;
      break;
      
    default:
      return null;
  }
  
  // Ensure dates are strings in ISO format
  const formatDate = date => date.toISOString().substring(0, 10);
  
  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate),
    description,
    type,
    originalQuery
  };
}

function findSessionPatterns(sessions, events, minFrequency) {
  const patterns = [];
  
  // Look for style → outcome patterns
  const styleGroups = {};
  sessions.forEach(session => {
    if (!session.style) return;
    
    if (!styleGroups[session.style]) {
      styleGroups[session.style] = [];
    }
    styleGroups[session.style].push(session);
  });
  
  Object.entries(styleGroups).forEach(([style, sessions]) => {
    if (sessions.length < minFrequency) return;
    
    // Find common outcomes for this style
    const outcomes = {};
    sessions.forEach(session => {
      // Look for events shortly after this session
      const sessionTime = new Date(session.created).getTime();
      const relevantEvents = events.filter(event => {
        const eventTime = new Date(event.created).getTime();
        return Math.abs(eventTime - sessionTime) < 2 * 60 * 60 * 1000; // Within 2 hours
      });
      
      relevantEvents.forEach(event => {
        const key = `${event.event_type}:${event.category}`;
        outcomes[key] = (outcomes[key] || 0) + 1;
      });
    });
    
    // Find significant outcomes
    Object.entries(outcomes).forEach(([outcome, count]) => {
      if (count >= Math.min(3, minFrequency)) {
        patterns.push({
          trigger: `${style} interaction style`,
          outcome: outcome.replace(':', ' in '),
          frequency: count,
          confidence: count / sessions.length,
          example: sessions[0].message_sample || 'N/A'
        });
      }
    });
  });
  
  return patterns;
}

function findBehaviorPatterns(events, minFrequency) {
  const patterns = [];
  
  // Group events by type and look for temporal patterns
  const eventsByType = {};
  events.forEach(event => {
    const type = event.event_type;
    if (!eventsByType[type]) eventsByType[type] = [];
    eventsByType[type].push(event);
  });
  
  Object.entries(eventsByType).forEach(([type, typeEvents]) => {
    if (typeEvents.length < minFrequency) return;
    
    patterns.push({
      description: `Frequently logs ${type} events`,
      sessionCount: typeEvents.length,
      pattern: type,
      frequency: typeEvents.length
    });
  });
  
  return patterns;
}

function generateCrossSessionInsights(sessions, events, patterns) {
  const insights = [];
  
  if (sessions.length > 10) {
    const styles = sessions.map(s => s.style).filter(Boolean);
    const mostCommon = [...new Set(styles)].sort((a, b) => 
      styles.filter(s => s === b).length - styles.filter(s => s === a).length
    )[0];
    
    if (mostCommon) {
      insights.push(`Most common interaction style is "${mostCommon}"`);
    }
  }
  
  const mistakes = events.filter(e => e.event_type === 'mistake');
  if (mistakes.length > 5) {
    insights.push(`High mistake frequency detected: ${mistakes.length} mistakes across sessions`);
  }
  
  if (patterns.length > 3) {
    insights.push(`Strong behavioral patterns detected: ${patterns.length} consistent trigger→outcome pairs`);
  }
  
  return insights;
}

export {
  consolidateMemory,
  applyForgettingCurve,
  executeTemporalQuery,
  analyzeCrossSessionPatterns,
  getDecisionChangelog
};