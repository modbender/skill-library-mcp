/**
 * session-intel.js - Session Intelligence for interaction style detection
 * Phase 5: T-029 (style detection), T-030 (session metadata)
 */

import { openDb } from './db.js';

const INTERACTION_STYLES = {
  BRAINSTORM: 'brainstorm',    // Terse, rapid-fire, ideas
  DEEP_WORK: 'deep-work',      // Detailed, methodical, structured  
  CASUAL: 'casual',            // Relaxed, conversational
  URGENT: 'urgent',            // Fast, action-needed
  DEBUG: 'debug',              // Problem-solving, technical
  PLANNING: 'planning'         // Strategic, roadmap, future-focused
};

const MOOD_INDICATORS = {
  FRUSTRATED: ['stuck', 'broken', 'not working', 'failed', 'error'],
  EXCITED: ['awesome', 'great', 'love', 'perfect', 'amazing'],
  FOCUSED: ['need to', 'should', 'must', 'important', 'priority'],
  EXPLORATORY: ['what if', 'could we', 'maybe', 'consider', 'explore']
};

const URGENCY_INDICATORS = {
  HIGH: ['now', 'urgent', 'asap', 'immediately', 'critical', 'broken'],
  MEDIUM: ['soon', 'today', 'this week', 'should', 'need to'],
  LOW: ['eventually', 'someday', 'when', 'maybe', 'consider']
};

/**
 * Detect interaction style from message content (T-029)
 */
function detectInteractionStyle(message) {
  const text = message.toLowerCase();
  const words = text.split(/\s+/);
  const sentences = message.split(/[.!?]+/).filter(s => s.trim());
  
  const analysis = {
    primary: INTERACTION_STYLES.CASUAL,
    confidence: 0.5,
    indicators: [],
    mood: null,
    urgency: 'medium'
  };
  
  // Style detection patterns
  const patterns = [
    {
      style: INTERACTION_STYLES.BRAINSTORM,
      indicators: ['idea', 'what about', 'could', 'maybe', 'thoughts on'],
      weights: { short_sentences: 0.3, questions: 0.4, hypotheticals: 0.3 }
    },
    {
      style: INTERACTION_STYLES.DEEP_WORK,
      indicators: ['implement', 'build', 'create', 'design', 'architecture', 'detailed'],
      weights: { long_sentences: 0.4, technical_terms: 0.3, specific: 0.3 }
    },
    {
      style: INTERACTION_STYLES.URGENT,
      indicators: ['now', 'asap', 'urgent', 'broken', 'critical', 'immediately'],
      weights: { urgency_words: 0.6, short_sentences: 0.2, imperatives: 0.2 }
    },
    {
      style: INTERACTION_STYLES.DEBUG,
      indicators: ['error', 'failing', 'issue', 'problem', 'debug', 'fix'],
      weights: { problem_words: 0.5, questions: 0.3, technical_terms: 0.2 }
    },
    {
      style: INTERACTION_STYLES.PLANNING,
      indicators: ['plan', 'roadmap', 'strategy', 'phase', 'future', 'next'],
      weights: { planning_words: 0.4, long_sentences: 0.3, future_tense: 0.3 }
    }
  ];
  
  let bestScore = 0;
  
  for (const pattern of patterns) {
    let score = 0;
    const foundIndicators = [];
    
    // Check for indicator words
    for (const indicator of pattern.indicators) {
      if (text.includes(indicator)) {
        score += 0.2;
        foundIndicators.push(indicator);
      }
    }
    
    // Style-specific scoring
    if (pattern.style === INTERACTION_STYLES.BRAINSTORM) {
      const questions = (message.match(/\?/g) || []).length;
      const shortSentences = sentences.filter(s => s.trim().split(/\s+/).length < 8).length;
      score += (questions / sentences.length) * 0.4;
      score += (shortSentences / sentences.length) * 0.3;
    }
    
    if (pattern.style === INTERACTION_STYLES.DEEP_WORK) {
      const avgLength = words.length / sentences.length;
      if (avgLength > 12) score += 0.4;  // Long sentences
      if (text.match(/\b(implement|build|create|design|architecture)\b/)) score += 0.3;
    }
    
    if (pattern.style === INTERACTION_STYLES.URGENT) {
      const urgentWords = URGENCY_INDICATORS.HIGH.filter(word => text.includes(word));
      score += (urgentWords.length / words.length) * 2;  // Weight heavily
    }
    
    if (pattern.style === INTERACTION_STYLES.DEBUG) {
      const problemWords = ['error', 'fail', 'issue', 'problem', 'broken', 'stuck'].filter(word => text.includes(word));
      score += (problemWords.length / words.length) * 2;
    }
    
    if (pattern.style === INTERACTION_STYLES.PLANNING) {
      const planWords = ['plan', 'roadmap', 'strategy', 'phase', 'step', 'next'].filter(word => text.includes(word));
      score += (planWords.length / words.length) * 2;
    }
    
    if (score > bestScore) {
      bestScore = score;
      analysis.primary = pattern.style;
      analysis.confidence = Math.min(0.95, score);
      analysis.indicators = foundIndicators;
    }
  }
  
  // Mood detection
  for (const [mood, indicators] of Object.entries(MOOD_INDICATORS)) {
    const matches = indicators.filter(indicator => text.includes(indicator));
    if (matches.length > 0) {
      analysis.mood = mood.toLowerCase();
      break;
    }
  }
  
  // Urgency detection
  for (const [level, indicators] of Object.entries(URGENCY_INDICATORS)) {
    const matches = indicators.filter(indicator => text.includes(indicator));
    if (matches.length > 0) {
      analysis.urgency = level.toLowerCase();
      break;
    }
  }
  
  return analysis;
}

/**
 * Save session metadata to database (T-030)
 */
function saveSessionMetadata(sessionId, metadata) {
  const db = openDb();
  
  try {
    // Ensure session_metadata table exists
    db.exec(`
      CREATE TABLE IF NOT EXISTS session_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        style TEXT,
        mood TEXT,
        urgency TEXT,
        confidence REAL,
        topic_tags TEXT,
        message_sample TEXT,
        duration_minutes INTEGER,
        created TEXT NOT NULL,
        updated TEXT NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_session_meta_id ON session_metadata(session_id);
      CREATE INDEX IF NOT EXISTS idx_session_meta_created ON session_metadata(created);
    `);
    
    const now = new Date().toISOString();
    const topicTags = extractTopicTags(metadata.message || '');
    
    // Insert or update session metadata
    const existing = db.prepare('SELECT id FROM session_metadata WHERE session_id = ?').get(sessionId);
    
    if (existing) {
      db.prepare(`
        UPDATE session_metadata 
        SET style = ?, mood = ?, urgency = ?, confidence = ?, 
            topic_tags = ?, message_sample = ?, updated = ?
        WHERE session_id = ?
      `).run(
        metadata.style, metadata.mood, metadata.urgency, metadata.confidence,
        topicTags, metadata.message, now, sessionId
      );
    } else {
      db.prepare(`
        INSERT INTO session_metadata (
          session_id, style, mood, urgency, confidence, topic_tags, 
          message_sample, created, updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        sessionId, metadata.style, metadata.mood, metadata.urgency, 
        metadata.confidence, topicTags, metadata.message, now, now
      );
    }
    
  } finally {
    db.close();
  }
}

/**
 * Extract topic tags from message text
 */
function extractTopicTags(message) {
  const text = message.toLowerCase();
  const tags = [];
  
  // Common project/topic keywords
  const projectKeywords = ['cad-wiki', 'rune', 'whattimeisitin', 'forge', 'brokkr-mem'];
  const techKeywords = ['nextjs', 'vercel', 'github', 'docker', 'nginx', 'ollama'];
  const taskKeywords = ['deploy', 'build', 'debug', 'fix', 'create', 'update'];
  
  for (const keyword of [...projectKeywords, ...techKeywords, ...taskKeywords]) {
    if (text.includes(keyword) || text.includes(keyword.replace('-', ' '))) {
      tags.push(keyword);
    }
  }
  
  return tags.join(', ');
}

/**
 * Get session history and patterns (T-033: Time-aware behavior)
 */
function getSessionPatterns(sessionId, days = 30) {
  const db = openDb();
  
  try {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    
    const sessions = db.prepare(`
      SELECT * FROM session_metadata 
      WHERE session_id = ? AND created > ?
      ORDER BY created DESC
    `).all(sessionId, cutoffDate);
    
    if (sessions.length === 0) {
      return { patterns: [], insights: [] };
    }
    
    // Analyze patterns
    const styles = sessions.map(s => s.style).filter(Boolean);
    const moods = sessions.map(s => s.mood).filter(Boolean);
    const topics = sessions.flatMap(s => (s.topic_tags || '').split(', ')).filter(Boolean);
    
    const styleFreq = countFrequency(styles);
    const moodFreq = countFrequency(moods);
    const topicFreq = countFrequency(topics);
    
    const patterns = {
      preferred_style: Object.keys(styleFreq)[0] || 'casual',
      common_moods: Object.keys(moodFreq).slice(0, 3),
      frequent_topics: Object.keys(topicFreq).slice(0, 5),
      session_count: sessions.length
    };
    
    const insights = generateInsights(patterns, sessions);
    
    return { patterns, insights };
    
  } finally {
    db.close();
  }
}

/**
 * Count frequency of items
 */
function countFrequency(items) {
  return items.reduce((freq, item) => {
    freq[item] = (freq[item] || 0) + 1;
    return freq;
  }, {});
}

/**
 * Generate behavioral insights
 */
function generateInsights(patterns, sessions) {
  const insights = [];
  
  if (patterns.session_count > 5) {
    insights.push(`Active user: ${patterns.session_count} sessions in last 30 days`);
  }
  
  if (patterns.preferred_style) {
    insights.push(`Prefers ${patterns.preferred_style} interaction style`);
  }
  
  if (patterns.frequent_topics.length > 0) {
    insights.push(`Often discusses: ${patterns.frequent_topics.slice(0, 3).join(', ')}`);
  }
  
  // Time patterns (future enhancement)
  const hours = sessions.map(s => new Date(s.created).getHours());
  const commonHours = countFrequency(hours);
  const peakHour = Object.keys(commonHours)[0];
  if (peakHour) {
    insights.push(`Most active around ${peakHour}:00`);
  }
  
  return insights;
}

export {
  detectInteractionStyle,
  saveSessionMetadata,
  getSessionPatterns,
  extractTopicTags,
  INTERACTION_STYLES,
  MOOD_INDICATORS,
  URGENCY_INDICATORS
};