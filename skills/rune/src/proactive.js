/**
 * proactive.js - Proactive memory system for volunteering relevant context
 * Phase 5: T-031 - "Last time you worked on this, you hit X"
 */

import { scoreFactsForRelevance } from './relevance.js';
import { openDb } from './db.js';

const PROACTIVE_THRESHOLD = 0.7;
const STRONG_RELEVANCE_THRESHOLD = 0.8;

/**
 * Generate proactive memory response based on message context
 */
async function generateProactiveMemory(message, options = {}) {
  const { 
    engine = 'ollama', 
    model, 
    style = 'context',
    quietMode = false,
    sessionId
  } = options;

  const db = openDb();
  
  try {
    // Get all facts
    const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC').all();
    
    if (allFacts.length === 0) {
      return '';
    }

    // Score for relevance
    const scoredFacts = await scoreFactsForRelevance(message, allFacts, {
      engine,
      model,
      limit: 50,
      threshold: 0.3  // Lower threshold to catch more patterns
    });

    // Extract high-relevance facts by category
    const strongFacts = scoredFacts.filter(f => f.relevance_score >= PROACTIVE_THRESHOLD);
    const veryStrongFacts = scoredFacts.filter(f => f.relevance_score >= STRONG_RELEVANCE_THRESHOLD);
    
    if (quietMode && veryStrongFacts.length === 0) {
      return '';
    }

    // Categorize relevant facts
    const context = categorizeFactsForProactive(strongFacts, scoredFacts);
    
    // Generate response based on style
    switch (style) {
      case 'tips':
        return generateTipsStyle(message, context);
      case 'warnings': 
        return generateWarningsStyle(message, context);
      case 'summary':
        return generateSummaryStyle(message, context);
      case 'context':
      default:
        return generateContextStyle(message, context);
    }
    
  } finally {
    db.close();
  }
}

/**
 * Categorize facts for proactive responses
 */
function categorizeFactsForProactive(strongFacts, allRelevantFacts) {
  const lessons = strongFacts.filter(f => f.category === 'lesson');
  const decisions = strongFacts.filter(f => f.category === 'decision');
  const projects = strongFacts.filter(f => f.category === 'project');
  const tools = strongFacts.filter(f => f.category === 'tool');
  const preferences = strongFacts.filter(f => f.category === 'preference');
  
  // Look for past performance events
  const db = openDb();
  const perfEvents = db.prepare(`
    SELECT * FROM performance_log 
    WHERE event_type IN ('mistake', 'success', 'lesson')
    ORDER BY created DESC LIMIT 10
  `).all();
  db.close();
  
  // Filter performance events by relevance to message
  const relevantEvents = perfEvents.filter(event => 
    message.toLowerCase().includes(event.detail.toLowerCase().split(' ')[0]) ||
    event.detail.toLowerCase().includes(message.toLowerCase().split(' ')[0])
  );

  return {
    lessons,
    decisions,
    projects,
    tools,
    preferences,
    perfEvents: relevantEvents,
    allFacts: allRelevantFacts
  };
}

/**
 * Generate context-style proactive response
 */
function generateContextStyle(message, context) {
  let response = '';
  
  // Lead with strongest lessons/warnings
  if (context.lessons.length > 0) {
    const topLesson = context.lessons[0];
    response += `💡 **Heads up:** ${topLesson.value}\n`;
  }
  
  // Recent performance patterns
  if (context.perfEvents.length > 0) {
    const recentEvent = context.perfEvents[0];
    if (recentEvent.event_type === 'mistake') {
      response += `⚠️ **Last time:** ${recentEvent.detail}\n`;
    }
  }
  
  // Key decisions/preferences
  if (context.decisions.length > 0) {
    response += `⚖️ **Decision:** ${context.decisions[0].value}\n`;
  }
  
  if (context.preferences.length > 0) {
    response += `🎯 **Preference:** ${context.preferences[0].value}\n`;
  }
  
  // Relevant project status
  const projectsWithStatus = context.projects.filter(p => 
    p.key.includes('status') || p.key.includes('state') || p.value.toLowerCase().includes('complete')
  );
  if (projectsWithStatus.length > 0) {
    response += `📊 **Status:** ${projectsWithStatus[0].value}\n`;
  }
  
  return response.trim();
}

/**
 * Generate tips-focused proactive response
 */
function generateTipsStyle(message, context) {
  const tips = [];
  
  // Extract actionable lessons
  context.lessons.forEach(lesson => {
    tips.push(`💡 ${lesson.value}`);
  });
  
  // Add tool recommendations
  context.tools.forEach(tool => {
    if (tool.relevance_score > 0.8) {
      tips.push(`🔧 Consider: ${tool.value}`);
    }
  });
  
  // Add past success patterns
  context.perfEvents.forEach(event => {
    if (event.event_type === 'success') {
      tips.push(`✅ ${event.detail}`);
    }
  });
  
  return tips.length > 0 ? tips.slice(0, 3).join('\n') : '';
}

/**
 * Generate warnings-focused proactive response
 */
function generateWarningsStyle(message, context) {
  const warnings = [];
  
  // Critical lessons (typically mistakes to avoid)
  context.lessons.forEach(lesson => {
    if (lesson.value.toLowerCase().includes('never') || lesson.value.toLowerCase().includes('don\'t')) {
      warnings.push(`⚠️ ${lesson.value}`);
    }
  });
  
  // Recent mistakes
  context.perfEvents.forEach(event => {
    if (event.event_type === 'mistake') {
      warnings.push(`❌ Watch out: ${event.detail}`);
    }
  });
  
  return warnings.length > 0 ? warnings.slice(0, 2).join('\n') : '';
}

/**
 * Generate summary-style proactive response
 */
function generateSummaryStyle(message, context) {
  const items = [];
  
  if (context.projects.length > 0) {
    items.push(`**Project:** ${context.projects[0].value}`);
  }
  
  if (context.decisions.length > 0) {
    items.push(`**Decision:** ${context.decisions[0].value}`);
  }
  
  if (context.lessons.length > 0) {
    items.push(`**Lesson:** ${context.lessons[0].value}`);
  }
  
  return items.slice(0, 3).join(' | ');
}

/**
 * Simple relevance check - does message match any high-scoring facts?
 */
async function hasProactiveContext(message, options = {}) {
  try {
    const response = await generateProactiveMemory(message, { 
      ...options, 
      quietMode: true 
    });
    return response.trim().length > 0;
  } catch {
    return false;
  }
}

export { 
  generateProactiveMemory,
  hasProactiveContext,
  PROACTIVE_THRESHOLD,
  STRONG_RELEVANCE_THRESHOLD
};