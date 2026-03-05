/**
 * self-improvement.js - Self-improvement loop for measurable performance gains
 * Phase 8: T-044 through T-048 - Learn from mistakes, detect patterns, get better
 */

import { openDb } from './db.js';
import fs from 'fs';
import path from 'path';

const PATTERN_TYPES = {
  MISTAKE: 'mistake',           // Repeated errors
  SKILL_NEGLECT: 'skill-neglect', // Not using available skills
  EFFICIENCY: 'efficiency',     // Time/token waste patterns  
  CONTEXT_LOSS: 'context-loss', // Forgetting known information
  SUCCESS: 'success'           // Positive patterns to reinforce
};

const SEVERITY_LEVELS = {
  CRITICAL: 'critical',  // >5 occurrences, blocks work
  WARNING: 'warning',    // 3-5 occurrences, needs attention
  INFO: 'info'          // 2 occurrences, monitor
};

/**
 * Analyze patterns in performance data (T-045)
 */
async function analyzePatterns(days = 30, options = {}) {
  const { minFrequency = 2, includeSuccesses = false } = options;
  const db = openDb();
  
  try {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    
    // Get performance events for analysis
    const events = db.prepare(`
      SELECT event_type, detail, category, created 
      FROM performance_log 
      WHERE created > ?
      ORDER BY created DESC
    `).all(cutoffDate);
    
    if (events.length === 0) {
      return [];
    }
    
    // Group similar events
    const patterns = {};
    
    events.forEach(event => {
      // Normalize the detail text to find patterns
      const normalized = normalizeEventDetail(event.detail);
      const key = `${event.event_type}:${normalized}`;
      
      if (!patterns[key]) {
        patterns[key] = {
          type: event.event_type,
          normalizedDetail: normalized,
          originalDetail: event.detail,
          category: event.category,
          occurrences: [],
          frequency: 0
        };
      }
      
      patterns[key].occurrences.push(event.created);
      patterns[key].frequency++;
    });
    
    // Filter and analyze patterns
    const significantPatterns = Object.values(patterns)
      .filter(p => p.frequency >= minFrequency)
      .filter(p => includeSuccesses || p.type !== 'success')
      .map(pattern => analyzePattern(pattern, days))
      .sort((a, b) => b.severity_score - a.severity_score);
    
    return significantPatterns;
    
  } finally {
    db.close();
  }
}

/**
 * Generate weekly self-review (T-048)
 */
async function generateSelfReview(days = 7, options = {}) {
  const { autoInject = false, save = false } = options;
  const db = openDb();
  
  try {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    const endDate = new Date().toISOString();
    
    // Gather performance data
    const mistakes = db.prepare(`
      SELECT * FROM performance_log 
      WHERE event_type = 'mistake' AND created > ?
      ORDER BY created DESC
    `).all(cutoffDate);
    
    const successes = db.prepare(`
      SELECT * FROM performance_log 
      WHERE event_type = 'success' AND created > ?
      ORDER BY created DESC
    `).all(cutoffDate);
    
    const skillsUsed = db.prepare(`
      SELECT * FROM performance_log 
      WHERE event_type = 'skill-used' AND created > ?
      ORDER BY created DESC
    `).all(cutoffDate);
    
    // Analyze patterns
    const patterns = await analyzePatterns(days, { minFrequency: 2, includeSuccesses: false });
    
    // Generate review content
    const sections = [];
    
    sections.push(`# Self-Review: ${new Date().toDateString()}`);
    sections.push(`*Period: Last ${days} day(s)*`);
    sections.push('');
    
    // Performance overview
    sections.push('## 📊 Performance Overview');
    sections.push(`- **Successes**: ${successes.length}`);
    sections.push(`- **Mistakes**: ${mistakes.length}`);  
    sections.push(`- **Skills Used**: ${skillsUsed.length}`);
    sections.push(`- **Patterns Detected**: ${patterns.length}`);
    sections.push('');
    
    // What went well
    if (successes.length > 0) {
      sections.push('## ✅ What Went Well');
      successes.slice(0, 5).forEach(s => {
        sections.push(`- ${s.detail}`);
      });
      if (successes.length > 5) {
        sections.push(`- ...and ${successes.length - 5} more successes`);
      }
      sections.push('');
    }
    
    // Areas for improvement
    if (mistakes.length > 0) {
      sections.push('## ❌ Areas for Improvement');
      
      // Group similar mistakes
      const mistakeGroups = groupSimilarEvents(mistakes);
      Object.entries(mistakeGroups).slice(0, 5).forEach(([key, group]) => {
        sections.push(`- **${key}** (${group.length}x)`);
        if (group.length === 1) {
          sections.push(`  - ${group[0].detail}`);
        } else {
          sections.push(`  - Latest: ${group[0].detail}`);
        }
      });
      sections.push('');
    }
    
    // Pattern insights
    if (patterns.length > 0) {
      sections.push('## 🔍 Pattern Insights');
      
      const criticalPatterns = patterns.filter(p => p.severity === 'critical');
      const warningPatterns = patterns.filter(p => p.severity === 'warning');
      
      if (criticalPatterns.length > 0) {
        sections.push('**Critical Issues:**');
        criticalPatterns.forEach(p => {
          sections.push(`- ${p.description} (${p.frequency}x) - ${p.suggestions || 'needs intervention'}`);
        });
        sections.push('');
      }
      
      if (warningPatterns.length > 0) {
        sections.push('**Attention Needed:**');
        warningPatterns.forEach(p => {
          sections.push(`- ${p.description} (${p.frequency}x)`);
        });
        sections.push('');
      }
    }
    
    // Action items
    const actionItems = generateActionItems(mistakes, patterns);
    if (actionItems.length > 0) {
      sections.push('## 🎯 Action Items');
      actionItems.forEach((item, idx) => {
        sections.push(`${idx + 1}. ${item.action}`);
        if (item.reason) {
          sections.push(`   *${item.reason}*`);
        }
      });
      sections.push('');
    }
    
    // Goals for next period
    sections.push('## 🎯 Goals for Next Week');
    sections.push('- Reduce critical pattern frequency by 50%');
    if (mistakes.length > 3) {
      sections.push('- Focus on mistake prevention vs reaction');
    }
    if (skillsUsed.length < 5) {
      sections.push('- Increase skill utilization');
    }
    sections.push('- Continue tracking performance metrics');
    
    const content = sections.join('\n');
    
    // Auto-inject top lessons (T-046)
    let improvements = 0;
    if (autoInject) {
      improvements = await autoInjectLessons(patterns, mistakes);
    }
    
    // Save insights as facts
    if (save) {
      await saveReviewInsights(patterns, mistakes, successes);
    }
    
    return {
      content,
      patterns,
      improvements,
      actionItems,
      metrics: {
        mistakes: mistakes.length,
        successes: successes.length,
        skillsUsed: skillsUsed.length,
        patterns: patterns.length
      }
    };
    
  } finally {
    db.close();
  }
}

/**
 * Analyze skill usage patterns (T-047)
 */
async function analyzeSkillUsage(days = 30, options = {}) {
  const { suggest = false } = options;
  const db = openDb();
  
  try {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
    
    // Get skill usage events
    const skillEvents = db.prepare(`
      SELECT detail, created FROM performance_log 
      WHERE event_type = 'skill-used' AND created > ?
      ORDER BY created DESC
    `).all(cutoffDate);
    
    // Extract skill names and count usage
    const skillUsage = {};
    const skillPattern = /Used skill: (\w+(?:-\w+)*)/i;
    
    skillEvents.forEach(event => {
      const match = event.detail.match(skillPattern);
      if (match) {
        const skill = match[1];
        if (!skillUsage[skill]) {
          skillUsage[skill] = {
            skill,
            count: 0,
            lastUsed: null,
            sessions: new Set()
          };
        }
        skillUsage[skill].count++;
        skillUsage[skill].lastUsed = event.created;
        
        // Track unique sessions (approximate by day)
        const day = event.created.substring(0, 10);
        skillUsage[skill].sessions.add(day);
      }
    });
    
    // Sort by usage frequency
    const used = Object.values(skillUsage)
      .sort((a, b) => b.count - a.count);
    
    // Identify neglected skills (hardcoded for now, could read from skill directory)
    const availableSkills = [
      'qmd', 'local-models', 'github', 'project-ops', 'vercel-deploy', 
      'seo-audit', 'web-perf', 'docker', 'nginx', 'sysadmin',
      'task-delegation', 'weather', 'coding-agent'
    ];
    
    const usedSkillNames = new Set(used.map(s => s.skill));
    const neglected = availableSkills
      .filter(skill => !usedSkillNames.has(skill))
      .map(skill => ({ skill, lastUsed: null, count: 0 }));
    
    // Generate suggestions
    const suggestions = [];
    if (suggest) {
      if (neglected.length > 0) {
        suggestions.push(`Consider using neglected skills: ${neglected.slice(0, 3).map(s => s.skill).join(', ')}`);
      }
      
      const lowUsage = used.filter(s => s.count === 1);
      if (lowUsage.length > 0) {
        suggestions.push(`Skills used only once might need more integration: ${lowUsage.slice(0, 3).map(s => s.skill).join(', ')}`);
      }
    }
    
    return {
      used,
      neglected,
      suggestions,
      totalSkillEvents: skillEvents.length,
      uniqueSkills: used.length,
      coverage: Math.round((used.length / availableSkills.length) * 100)
    };
    
  } finally {
    db.close();
  }
}

/**
 * Helper functions
 */
function normalizeEventDetail(detail) {
  // Remove specific details to find patterns
  return detail
    .toLowerCase()
    .replace(/\b\d+\b/g, 'N')  // Replace numbers with N
    .replace(/\b[a-f0-9]{8,}\b/g, 'HASH')  // Replace hashes
    .replace(/\b\w+@\w+\.\w+\b/g, 'EMAIL')  // Replace emails
    .replace(/\bhttps?:\/\/\S+\b/g, 'URL')  // Replace URLs
    .trim();
}

function analyzePattern(pattern, days) {
  const frequency = pattern.frequency;
  const firstOccurrence = new Date(pattern.occurrences[pattern.occurrences.length - 1]);
  const lastOccurrence = new Date(pattern.occurrences[0]);
  const timespan = (lastOccurrence - firstOccurrence) / (1000 * 60 * 60 * 24);
  
  // Determine severity
  let severity = SEVERITY_LEVELS.INFO;
  let severity_score = frequency;
  
  if (frequency >= 5) {
    severity = SEVERITY_LEVELS.CRITICAL;
    severity_score = frequency * 2;
  } else if (frequency >= 3) {
    severity = SEVERITY_LEVELS.WARNING;
    severity_score = frequency * 1.5;
  }
  
  // Check if pattern is accelerating
  const recentOccurrences = pattern.occurrences.filter(date => {
    const daysSince = (Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24);
    return daysSince <= 3;
  });
  
  const trend = recentOccurrences.length >= (frequency * 0.6) ? 'accelerating' : 
                timespan < 1 ? 'burst' : 'stable';
  
  // Generate suggestions
  const suggestions = generatePatternSuggestions(pattern);
  
  return {
    type: pattern.type,
    description: pattern.originalDetail,
    normalizedPattern: pattern.normalizedDetail,
    frequency,
    severity,
    severity_score,
    trend,
    timespan: Math.round(timespan * 10) / 10,
    suggestions,
    occurrences: pattern.occurrences
  };
}

function generatePatternSuggestions(pattern) {
  const detail = pattern.normalizedDetail.toLowerCase();
  
  if (detail.includes('forgot') && detail.includes('memory.md')) {
    return 'Add MEMORY.md check to session startup routine';
  }
  
  if (detail.includes('skill') && detail.includes('not using')) {
    return 'Add skill reminder to relevant contexts';
  }
  
  if (detail.includes('ollama') && detail.includes('timeout')) {
    return 'Implement better Ollama health checks and fallbacks';
  }
  
  if (detail.includes('extraction') && detail.includes('failed')) {
    return 'Review extraction prompts and error handling';
  }
  
  return 'Create specific prevention strategy for this issue';
}

function groupSimilarEvents(events) {
  const groups = {};
  
  events.forEach(event => {
    const normalized = normalizeEventDetail(event.detail);
    if (!groups[normalized]) {
      groups[normalized] = [];
    }
    groups[normalized].push(event);
  });
  
  return groups;
}

function generateActionItems(mistakes, patterns) {
  const items = [];
  
  // High-frequency patterns get action items
  patterns.filter(p => p.severity === 'critical').forEach(pattern => {
    items.push({
      action: `Address critical pattern: ${pattern.description}`,
      reason: `Occurred ${pattern.frequency} times, ${pattern.trend} trend`
    });
  });
  
  // Common mistake categories
  const memoryMistakes = mistakes.filter(m => m.detail.toLowerCase().includes('memory'));
  if (memoryMistakes.length >= 2) {
    items.push({
      action: 'Implement automated memory check in session startup',
      reason: `${memoryMistakes.length} memory-related mistakes`
    });
  }
  
  const skillMistakes = mistakes.filter(m => m.detail.toLowerCase().includes('skill'));
  if (skillMistakes.length >= 2) {
    items.push({
      action: 'Add skill usage prompts to relevant workflows',
      reason: `${skillMistakes.length} skill-related mistakes`
    });
  }
  
  return items;
}

async function autoInjectLessons(patterns, mistakes) {
  // This would update TOOLS.md or AGENTS.md with critical lessons
  // For now, just return count of what would be injected
  const criticalPatterns = patterns.filter(p => p.severity === 'critical');
  return criticalPatterns.length;
}

async function saveReviewInsights(patterns, mistakes, successes) {
  // Save insights as facts in the database
  const db = openDb();
  
  try {
    const now = new Date().toISOString();
    
    if (patterns.length > 0) {
      const criticalCount = patterns.filter(p => p.severity === 'critical').length;
      db.prepare(`
        INSERT INTO facts (category, key, value, source_type, updated, created)
        VALUES ('performance', 'weekly.patterns.critical', ?, 'auto-review', ?, ?)
      `).run(`${criticalCount} critical patterns detected in weekly review`, now, now);
    }
    
    if (mistakes.length > 5) {
      db.prepare(`
        INSERT INTO facts (category, key, value, source_type, updated, created)
        VALUES ('performance', 'weekly.mistakes.high', ?, 'auto-review', ?, ?)
      `).run(`High mistake frequency: ${mistakes.length} mistakes this week`, now, now);
    }
    
  } finally {
    db.close();
  }
}

function escalatePatterns(patterns) {
  // Escalate critical patterns to notifications or immediate action
  const critical = patterns.filter(p => p.severity === 'critical');
  
  // In practice, this would send notifications or add to urgent task queue
  critical.forEach(pattern => {
    console.warn(`ESCALATED: ${pattern.description} (${pattern.frequency}x)`);
  });
  
  return critical;
}

export {
  analyzePatterns,
  generateSelfReview,
  analyzeSkillUsage,
  escalatePatterns,
  PATTERN_TYPES,
  SEVERITY_LEVELS
};