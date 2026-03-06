#!/usr/bin/env node
/**
 * Learning System - Agent memory, feedback, and shared learnings
 * 
 * Provides:
 * - Per-agent persistent memory (markdown files)
 * - Feedback collection and storage
 * - Shared cross-agent learnings
 * - Global context for all agents
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const COLONY_DIR = join(__dirname, '..', 'colony');
const MEMORY_DIR = join(COLONY_DIR, 'memory');
const FEEDBACK_FILE = join(COLONY_DIR, 'feedback.json');
const LEARNINGS_FILE = join(COLONY_DIR, 'learnings.yaml');
const GLOBAL_CONTEXT_FILE = join(COLONY_DIR, 'global-context.json');
const AGENTS_FILE = join(COLONY_DIR, 'agents.yaml');

// ============ Directory Setup ============

function ensureMemoryDir() {
  if (!existsSync(MEMORY_DIR)) {
    mkdirSync(MEMORY_DIR, { recursive: true });
  }
}

// ============ Agent Memory ============

/**
 * Get agent memory file path
 */
function getMemoryPath(agentName) {
  ensureMemoryDir();
  return join(MEMORY_DIR, `${agentName}.md`);
}

/**
 * Get default memory content for a new agent
 */
function getDefaultMemory(agentName) {
  // Capitalize first letter
  const displayName = agentName.charAt(0).toUpperCase() + agentName.slice(1);
  return `# ${displayName}'s Memory

## Lessons Learned
- (populated over time as you complete tasks)

## Patterns That Work
- (document what works well)

## Mistakes Made
- (learn from errors to avoid repeating them)

## Preferences
- (any discovered preferences or style notes)

---
*This file is read at the start of each task and updated after completion.*
`;
}

/**
 * Read agent's memory file
 */
function getAgentMemory(agentName) {
  const path = getMemoryPath(agentName);
  try {
    return readFileSync(path, 'utf-8');
  } catch (e) {
    return getDefaultMemory(agentName);
  }
}

/**
 * Write agent's memory file
 */
function writeAgentMemory(agentName, content) {
  const path = getMemoryPath(agentName);
  ensureMemoryDir();
  writeFileSync(path, content);
}

/**
 * Add a lesson to agent's memory
 */
function addToAgentMemory(agentName, lesson, section = 'Lessons Learned') {
  let memory = getAgentMemory(agentName);
  
  // Find the section and add the lesson
  const sectionHeader = `## ${section}`;
  const sectionIndex = memory.indexOf(sectionHeader);
  
  if (sectionIndex !== -1) {
    // Find the next section or end
    const afterSection = memory.substring(sectionIndex + sectionHeader.length);
    const nextSectionMatch = afterSection.match(/\n## /);
    const insertPoint = nextSectionMatch 
      ? sectionIndex + sectionHeader.length + nextSectionMatch.index
      : memory.length;
    
    // Check if lesson already exists
    if (memory.includes(lesson.trim())) {
      return false; // Already exists
    }
    
    // Insert the new lesson
    const timestamp = new Date().toISOString().split('T')[0];
    const newLesson = `- ${lesson.trim()} (${timestamp})\n`;
    
    // Find last list item in section
    const sectionContent = memory.substring(sectionIndex, insertPoint);
    const lastDashIndex = sectionContent.lastIndexOf('\n-');
    
    if (lastDashIndex !== -1) {
      const absInsertPoint = sectionIndex + lastDashIndex + sectionContent.substring(lastDashIndex).indexOf('\n', 1) + 1;
      memory = memory.substring(0, absInsertPoint) + newLesson + memory.substring(absInsertPoint);
    } else {
      // Section is empty, add after placeholder
      const placeholderEnd = sectionIndex + sectionContent.indexOf('\n', sectionHeader.length + 1) + 1;
      memory = memory.substring(0, placeholderEnd) + newLesson + memory.substring(placeholderEnd);
    }
    
    writeAgentMemory(agentName, memory);
    return true;
  }
  
  return false;
}

/**
 * Initialize memory files for all agents
 */
function initializeAllAgentMemories() {
  ensureMemoryDir();
  
  try {
    const content = readFileSync(AGENTS_FILE, 'utf-8');
    const config = yaml.load(content);
    
    for (const agentName of Object.keys(config.agents)) {
      const path = getMemoryPath(agentName);
      if (!existsSync(path)) {
        writeAgentMemory(agentName, getDefaultMemory(agentName));
        console.log(`  Created memory for: ${agentName}`);
      }
    }
  } catch (e) {
    console.error('Error initializing memories:', e.message);
  }
}

// ============ Feedback ============

/**
 * Get default feedback structure
 */
function getDefaultFeedback() {
  return { entries: [] };
}

/**
 * Read feedback file
 */
function getFeedback() {
  try {
    return JSON.parse(readFileSync(FEEDBACK_FILE, 'utf-8'));
  } catch (e) {
    return getDefaultFeedback();
  }
}

/**
 * Write feedback file
 */
function writeFeedback(feedback) {
  writeFileSync(FEEDBACK_FILE, JSON.stringify(feedback, null, 2));
}

/**
 * Add feedback for a task
 */
function addFeedback(taskId, agent, feedback) {
  const data = getFeedback();
  const entry = {
    taskId,
    agent,
    feedback,
    ts: new Date().toISOString()
  };
  data.entries.push(entry);
  
  // Keep last 200 entries
  if (data.entries.length > 200) {
    data.entries = data.entries.slice(-200);
  }
  
  writeFeedback(data);
  return entry;
}

/**
 * Get feedback for a specific task
 */
function getTaskFeedback(taskId) {
  const data = getFeedback();
  return data.entries.filter(e => e.taskId === taskId);
}

/**
 * Get feedback for a specific agent
 */
function getAgentFeedback(agentName) {
  const data = getFeedback();
  return data.entries.filter(e => e.agent === agentName);
}

// ============ Shared Learnings ============

/**
 * Get default learnings structure
 */
function getDefaultLearnings() {
  return { learnings: [] };
}

/**
 * Read learnings file
 */
function getLearnings() {
  try {
    const content = readFileSync(LEARNINGS_FILE, 'utf-8');
    return yaml.load(content) || getDefaultLearnings();
  } catch (e) {
    return getDefaultLearnings();
  }
}

/**
 * Write learnings file
 */
function writeLearnings(learnings) {
  const content = yaml.dump(learnings, { lineWidth: 100 });
  writeFileSync(LEARNINGS_FILE, content);
}

/**
 * Add a shared learning
 */
function addLearning(lesson, category = 'general', source = null) {
  const data = getLearnings();
  const entry = {
    category,
    lesson,
    source,
    date: new Date().toISOString().split('T')[0]
  };
  data.learnings.push(entry);
  writeLearnings(data);
  return entry;
}

/**
 * Get learnings by category
 */
function getLearningsByCategory(category) {
  const data = getLearnings();
  return data.learnings.filter(l => l.category === category);
}

// ============ Global Context ============

/**
 * Get default global context
 */
function getDefaultGlobalContext() {
  return {
    currentProjects: [],
    preferences: {
      codeStyle: 'functional, ES modules',
      docStyle: 'concise, bullet points',
      timezone: 'America/Chicago'
    },
    activeFacts: [],
    recentDecisions: []
  };
}

/**
 * Read global context
 */
function getGlobalContext() {
  try {
    return JSON.parse(readFileSync(GLOBAL_CONTEXT_FILE, 'utf-8'));
  } catch (e) {
    return getDefaultGlobalContext();
  }
}

/**
 * Write global context
 */
function writeGlobalContext(context) {
  writeFileSync(GLOBAL_CONTEXT_FILE, JSON.stringify(context, null, 2));
}

/**
 * Set a preference or other top-level key
 */
function setContextValue(key, value) {
  const context = getGlobalContext();
  
  // Handle nested keys like "preferences.codeStyle"
  const keys = key.split('.');
  let obj = context;
  for (let i = 0; i < keys.length - 1; i++) {
    if (!(keys[i] in obj)) {
      obj[keys[i]] = {};
    }
    obj = obj[keys[i]];
  }
  obj[keys[keys.length - 1]] = value;
  
  writeGlobalContext(context);
  return context;
}

/**
 * Add an active fact
 */
function addActiveFact(fact) {
  const context = getGlobalContext();
  if (!context.activeFacts.includes(fact)) {
    context.activeFacts.push(fact);
    writeGlobalContext(context);
  }
  return context;
}

/**
 * Add a recent decision
 */
function addDecision(decision, project = null) {
  const context = getGlobalContext();
  const entry = {
    decision,
    project,
    date: new Date().toISOString().split('T')[0]
  };
  context.recentDecisions.push(entry);
  
  // Keep last 50 decisions
  if (context.recentDecisions.length > 50) {
    context.recentDecisions = context.recentDecisions.slice(-50);
  }
  
  writeGlobalContext(context);
  return entry;
}

/**
 * Add a project
 */
function addProject(projectName) {
  const context = getGlobalContext();
  if (!context.currentProjects.includes(projectName)) {
    context.currentProjects.push(projectName);
    writeGlobalContext(context);
  }
  return context;
}

/**
 * Remove a project
 */
function removeProject(projectName) {
  const context = getGlobalContext();
  context.currentProjects = context.currentProjects.filter(p => p !== projectName);
  writeGlobalContext(context);
  return context;
}

// ============ Retrospective ============

/**
 * Generate a retrospective summary of recent activity
 */
function generateRetro(days = 7) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  
  // Load tasks from tasks.json
  const tasksFile = join(COLONY_DIR, 'tasks.json');
  let tasks = { completed: [], failed: [] };
  try {
    tasks = JSON.parse(readFileSync(tasksFile, 'utf-8'));
  } catch (e) {}
  
  const recentCompleted = (tasks.completed || []).filter(t => 
    new Date(t.completedAt) > cutoff
  );
  const recentFailed = (tasks.failed || []).filter(t => 
    new Date(t.completedAt) > cutoff
  );
  
  // Load feedback
  const feedback = getFeedback();
  const recentFeedback = feedback.entries.filter(f =>
    new Date(f.ts) > cutoff
  );
  
  // Aggregate by agent
  const byAgent = {};
  for (const t of recentCompleted) {
    if (!byAgent[t.agent]) byAgent[t.agent] = { completed: 0, failed: 0, feedback: [] };
    byAgent[t.agent].completed++;
  }
  for (const t of recentFailed) {
    if (!byAgent[t.agent]) byAgent[t.agent] = { completed: 0, failed: 0, feedback: [] };
    byAgent[t.agent].failed++;
  }
  for (const f of recentFeedback) {
    if (!byAgent[f.agent]) byAgent[f.agent] = { completed: 0, failed: 0, feedback: [] };
    byAgent[f.agent].feedback.push(f.feedback);
  }
  
  return {
    period: { days, since: cutoff.toISOString() },
    summary: {
      totalCompleted: recentCompleted.length,
      totalFailed: recentFailed.length,
      totalFeedback: recentFeedback.length
    },
    byAgent,
    suggestions: generateSuggestions(byAgent, recentFailed)
  };
}

/**
 * Generate learning suggestions from retro data
 */
function generateSuggestions(byAgent, failures) {
  const suggestions = [];
  
  // Identify agents with high failure rates
  for (const [agent, stats] of Object.entries(byAgent)) {
    const total = stats.completed + stats.failed;
    if (total >= 3 && stats.failed / total > 0.3) {
      suggestions.push(`${agent} has ${Math.round((stats.failed / total) * 100)}% failure rate - review recent errors`);
    }
  }
  
  // Common error patterns
  const errorCounts = {};
  for (const f of failures) {
    const errorType = f.result?.split(':')[0] || 'unknown';
    errorCounts[errorType] = (errorCounts[errorType] || 0) + 1;
  }
  
  for (const [error, count] of Object.entries(errorCounts)) {
    if (count >= 2) {
      suggestions.push(`Repeated error type: "${error}" (${count} times)`);
    }
  }
  
  return suggestions;
}

// ============ Display Functions ============

function showAgentMemory(agentName) {
  const memory = getAgentMemory(agentName);
  console.log(memory);
}

function showLearnings() {
  const data = getLearnings();
  
  console.log('\n📚 Shared Learnings\n');
  
  if (data.learnings.length === 0) {
    console.log('   (no learnings yet)');
    console.log('\n   Add one: colony learn add "lesson" --category process');
    return;
  }
  
  // Group by category
  const byCategory = {};
  for (const l of data.learnings) {
    const cat = l.category || 'general';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(l);
  }
  
  for (const [category, items] of Object.entries(byCategory)) {
    console.log(`\n📁 ${category}:`);
    for (const item of items) {
      console.log(`   • ${item.lesson}`);
      if (item.source) console.log(`     └─ source: ${item.source}`);
    }
  }
  console.log('');
}

function showGlobalContext() {
  const context = getGlobalContext();
  
  console.log('\n🌐 Global Context\n');
  
  console.log('📂 Current Projects:');
  if (context.currentProjects.length === 0) {
    console.log('   (none)');
  } else {
    for (const p of context.currentProjects) {
      console.log(`   • ${p}`);
    }
  }
  
  console.log('\n⚙️ Preferences:');
  for (const [key, value] of Object.entries(context.preferences || {})) {
    console.log(`   ${key}: ${value}`);
  }
  
  console.log('\n📌 Active Facts:');
  if ((context.activeFacts || []).length === 0) {
    console.log('   (none)');
  } else {
    for (const fact of context.activeFacts) {
      console.log(`   • ${fact}`);
    }
  }
  
  console.log('\n📋 Recent Decisions:');
  const decisions = (context.recentDecisions || []).slice(-5);
  if (decisions.length === 0) {
    console.log('   (none)');
  } else {
    for (const d of decisions) {
      const project = d.project ? ` [${d.project}]` : '';
      console.log(`   • ${d.decision}${project} (${d.date})`);
    }
  }
  
  console.log('');
}

function showRetro(days = 7) {
  const retro = generateRetro(days);
  
  console.log(`\n🔄 Retrospective (last ${days} days)\n`);
  console.log('─'.repeat(40));
  
  console.log('\n📊 Summary:');
  console.log(`   Completed: ${retro.summary.totalCompleted}`);
  console.log(`   Failed:    ${retro.summary.totalFailed}`);
  console.log(`   Feedback:  ${retro.summary.totalFeedback}`);
  
  if (Object.keys(retro.byAgent).length > 0) {
    console.log('\n👥 By Agent:');
    for (const [agent, stats] of Object.entries(retro.byAgent)) {
      const total = stats.completed + stats.failed;
      const successRate = total > 0 ? Math.round((stats.completed / total) * 100) : 100;
      console.log(`   ${agent.padEnd(12)} ${stats.completed} done, ${stats.failed} failed (${successRate}%)`);
      if (stats.feedback.length > 0) {
        console.log(`               📝 ${stats.feedback.length} feedback items`);
      }
    }
  }
  
  if (retro.suggestions.length > 0) {
    console.log('\n💡 Suggestions:');
    for (const suggestion of retro.suggestions) {
      console.log(`   • ${suggestion}`);
    }
  }
  
  console.log('');
}

// ============ Exports ============

export {
  // Memory
  getAgentMemory,
  writeAgentMemory,
  addToAgentMemory,
  getMemoryPath,
  initializeAllAgentMemories,
  
  // Feedback
  getFeedback,
  addFeedback,
  getTaskFeedback,
  getAgentFeedback,
  
  // Learnings
  getLearnings,
  addLearning,
  getLearningsByCategory,
  
  // Global Context
  getGlobalContext,
  writeGlobalContext,
  setContextValue,
  addActiveFact,
  addDecision,
  addProject,
  removeProject,
  
  // Retrospective
  generateRetro,
  
  // Display
  showAgentMemory,
  showLearnings,
  showGlobalContext,
  showRetro,
  
  // Paths
  MEMORY_DIR,
  FEEDBACK_FILE,
  LEARNINGS_FILE,
  GLOBAL_CONTEXT_FILE,
  
  // Setup
  ensureMemoryDir
};
