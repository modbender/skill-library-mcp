#!/usr/bin/env node
/**
 * Audit System - Logging and statistics for Colony agents
 * 
 * Provides:
 * - Event logging to append-only JSONL log
 * - Per-agent statistics tracking
 * - Global statistics aggregation
 * - Query functions for audit data
 */

import { readFileSync, writeFileSync, appendFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const COLONY_DIR = join(__dirname, '..', 'colony');
const AUDIT_DIR = join(COLONY_DIR, 'audit');
const AGENTS_AUDIT_DIR = join(AUDIT_DIR, 'agents');
const LOG_FILE = join(AUDIT_DIR, 'log.jsonl');
const GLOBAL_STATS_FILE = join(AUDIT_DIR, 'global.json');

// ============ Directory Setup ============

function ensureAuditDirs() {
  if (!existsSync(AUDIT_DIR)) {
    mkdirSync(AUDIT_DIR, { recursive: true });
  }
  if (!existsSync(AGENTS_AUDIT_DIR)) {
    mkdirSync(AGENTS_AUDIT_DIR, { recursive: true });
  }
}

// ============ Event Logging ============

/**
 * Log an event to the append-only log file
 * @param {Object} event - Event object with at least { event: string }
 */
function logEvent(event) {
  ensureAuditDirs();
  const entry = {
    ...event,
    ts: event.ts || new Date().toISOString()
  };
  appendFileSync(LOG_FILE, JSON.stringify(entry) + '\n');
  return entry;
}

/**
 * Log task started event
 */
function logTaskStarted(taskId, agent, options = {}) {
  return logEvent({
    event: 'task_started',
    taskId,
    agent,
    processRunId: options.runId || null,
    stage: options.stageId || null
  });
}

/**
 * Log task completed event
 */
function logTaskCompleted(taskId, agent, durationMs, tokens = {}, success = true) {
  const event = logEvent({
    event: 'task_completed',
    taskId,
    agent,
    durationMs,
    tokens: {
      in: tokens.in || 0,
      out: tokens.out || 0
    },
    success
  });
  
  // Update stats
  updateAgentStats(agent, {
    success: true,
    durationMs,
    tokensIn: tokens.in || 0,
    tokensOut: tokens.out || 0
  });
  
  return event;
}

/**
 * Log task failed event
 */
function logTaskFailed(taskId, agent, durationMs, error) {
  const event = logEvent({
    event: 'task_failed',
    taskId,
    agent,
    durationMs,
    error: String(error).substring(0, 500)
  });
  
  // Update stats
  updateAgentStats(agent, {
    success: false,
    durationMs,
    error: String(error).substring(0, 200)
  });
  
  return event;
}

/**
 * Log checkpoint events
 */
function logCheckpointWaiting(runId, stage) {
  return logEvent({ event: 'checkpoint_waiting', runId, stage });
}

function logCheckpointApproved(runId, stage) {
  return logEvent({ event: 'checkpoint_approved', runId, stage });
}

function logCheckpointRejected(runId, stage, reason) {
  return logEvent({ event: 'checkpoint_rejected', runId, stage, reason });
}

/**
 * Log process events
 */
function logProcessStarted(runId, processId, context) {
  return logEvent({
    event: 'process_started',
    runId,
    processId,
    context: String(context).substring(0, 500)
  });
}

function logProcessCompleted(runId, processId, durationMs) {
  return logEvent({
    event: 'process_completed',
    runId,
    processId,
    durationMs
  });
}

/**
 * Log feedback received
 */
function logFeedbackReceived(taskId, agent, feedback) {
  return logEvent({
    event: 'feedback_received',
    taskId,
    agent,
    feedback: String(feedback).substring(0, 1000)
  });
}

// ============ Agent Stats ============

/**
 * Get default agent stats structure
 */
function getDefaultAgentStats(agentName) {
  return {
    agent: agentName,
    stats: {
      totalTasks: 0,
      successful: 0,
      failed: 0,
      avgDurationMs: 0,
      totalTokensIn: 0,
      totalTokensOut: 0,
      lastActive: null
    },
    byTaskType: {},
    recentFailures: []
  };
}

/**
 * Read agent stats from file
 */
function getAgentStats(agentName) {
  ensureAuditDirs();
  const statsFile = join(AGENTS_AUDIT_DIR, `${agentName}.json`);
  try {
    return JSON.parse(readFileSync(statsFile, 'utf-8'));
  } catch (e) {
    return getDefaultAgentStats(agentName);
  }
}

/**
 * Write agent stats to file
 */
function writeAgentStats(agentName, stats) {
  ensureAuditDirs();
  const statsFile = join(AGENTS_AUDIT_DIR, `${agentName}.json`);
  writeFileSync(statsFile, JSON.stringify(stats, null, 2));
}

/**
 * Update agent stats after a task completes
 */
function updateAgentStats(agentName, result) {
  const stats = getAgentStats(agentName);
  const s = stats.stats;
  
  // Update counters
  s.totalTasks++;
  if (result.success) {
    s.successful++;
  } else {
    s.failed++;
    // Add to recent failures
    stats.recentFailures.push({
      ts: new Date().toISOString(),
      error: result.error || 'Unknown error'
    });
    // Keep only last 10 failures
    if (stats.recentFailures.length > 10) {
      stats.recentFailures = stats.recentFailures.slice(-10);
    }
  }
  
  // Update duration average
  if (result.durationMs) {
    const totalDuration = s.avgDurationMs * (s.totalTasks - 1) + result.durationMs;
    s.avgDurationMs = Math.round(totalDuration / s.totalTasks);
  }
  
  // Update token usage
  s.totalTokensIn += result.tokensIn || 0;
  s.totalTokensOut += result.tokensOut || 0;
  
  // Update last active
  s.lastActive = new Date().toISOString();
  
  writeAgentStats(agentName, stats);
  
  // Also update global stats
  updateGlobalStats();
  
  return stats;
}

// ============ Global Stats ============

/**
 * Get default global stats structure
 */
function getDefaultGlobalStats() {
  return {
    totalTasks: 0,
    totalProcesses: 0,
    avgTaskDurationMs: 0,
    avgApprovalWaitMs: 0,
    successRate: 1.0,
    tokenUsage: { totalIn: 0, totalOut: 0 },
    byAgent: {}
  };
}

/**
 * Read global stats
 */
function getGlobalStats() {
  ensureAuditDirs();
  try {
    return JSON.parse(readFileSync(GLOBAL_STATS_FILE, 'utf-8'));
  } catch (e) {
    return getDefaultGlobalStats();
  }
}

/**
 * Recalculate and write global stats from all agent stats
 */
function updateGlobalStats() {
  ensureAuditDirs();
  
  const global = getDefaultGlobalStats();
  
  // Read all agent stats files
  try {
    const files = readdirSync(AGENTS_AUDIT_DIR);
    for (const file of files) {
      if (!file.endsWith('.json')) continue;
      const agentName = file.replace('.json', '');
      try {
        const agentStats = JSON.parse(readFileSync(join(AGENTS_AUDIT_DIR, file), 'utf-8'));
        const s = agentStats.stats;
        
        // Aggregate
        global.totalTasks += s.totalTasks;
        global.tokenUsage.totalIn += s.totalTokensIn;
        global.tokenUsage.totalOut += s.totalTokensOut;
        
        // Store per-agent summary
        global.byAgent[agentName] = {
          totalTasks: s.totalTasks,
          successful: s.successful,
          failed: s.failed,
          avgDurationMs: s.avgDurationMs,
          lastActive: s.lastActive
        };
      } catch (e) {
        // Skip invalid files
      }
    }
    
    // Calculate averages
    if (global.totalTasks > 0) {
      let totalSuccess = 0;
      let totalDuration = 0;
      let agentCount = 0;
      
      for (const agent of Object.values(global.byAgent)) {
        totalSuccess += agent.successful;
        if (agent.avgDurationMs > 0) {
          totalDuration += agent.avgDurationMs;
          agentCount++;
        }
      }
      
      global.successRate = Math.round((totalSuccess / global.totalTasks) * 100) / 100;
      global.avgTaskDurationMs = agentCount > 0 ? Math.round(totalDuration / agentCount) : 0;
    }
    
    // Count processes from log
    const events = getRecentEvents(10000); // Read all events
    const processStarts = events.filter(e => e.event === 'process_started');
    global.totalProcesses = processStarts.length;
    
  } catch (e) {
    // No agent files yet
  }
  
  writeFileSync(GLOBAL_STATS_FILE, JSON.stringify(global, null, 2));
  return global;
}

// ============ Query Functions ============

/**
 * Get recent events from log
 */
function getRecentEvents(limit = 20) {
  ensureAuditDirs();
  try {
    const content = readFileSync(LOG_FILE, 'utf-8');
    const lines = content.trim().split('\n').filter(l => l);
    const events = lines.map(l => {
      try {
        return JSON.parse(l);
      } catch {
        return null;
      }
    }).filter(e => e);
    
    return events.slice(-limit).reverse();
  } catch (e) {
    return [];
  }
}

/**
 * Get slowest tasks
 */
function getSlowestTasks(limit = 10) {
  const events = getRecentEvents(10000);
  const completed = events.filter(e => 
    e.event === 'task_completed' && e.durationMs
  );
  
  completed.sort((a, b) => b.durationMs - a.durationMs);
  return completed.slice(0, limit);
}

/**
 * Get recent failures
 */
function getRecentFailures(limit = 10) {
  const events = getRecentEvents(10000);
  return events.filter(e => e.event === 'task_failed').slice(0, limit);
}

/**
 * Get events by type
 */
function getEventsByType(eventType, limit = 50) {
  const events = getRecentEvents(10000);
  return events.filter(e => e.event === eventType).slice(0, limit);
}

// ============ Display Functions ============

function formatDuration(ms) {
  if (!ms) return '-';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function formatTimestamp(ts) {
  if (!ts) return '-';
  const date = new Date(ts);
  const now = new Date();
  const diff = now - date;
  
  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return `${Math.floor(diff / 86400000)}d ago`;
}

function showAuditDashboard() {
  const global = getGlobalStats();
  
  console.log('\n📊 Colony Audit Dashboard\n');
  console.log('─'.repeat(50));
  
  console.log('\n📈 Global Statistics:');
  console.log(`   Total Tasks:     ${global.totalTasks}`);
  console.log(`   Total Processes: ${global.totalProcesses}`);
  console.log(`   Success Rate:    ${(global.successRate * 100).toFixed(0)}%`);
  console.log(`   Avg Duration:    ${formatDuration(global.avgTaskDurationMs)}`);
  console.log(`   Tokens In:       ${global.tokenUsage.totalIn.toLocaleString()}`);
  console.log(`   Tokens Out:      ${global.tokenUsage.totalOut.toLocaleString()}`);
  
  console.log('\n👥 Agent Summary:');
  const agents = Object.entries(global.byAgent)
    .sort((a, b) => b[1].totalTasks - a[1].totalTasks);
  
  if (agents.length === 0) {
    console.log('   (no agent activity yet)');
  } else {
    for (const [name, stats] of agents) {
      const success = stats.totalTasks > 0 
        ? Math.round((stats.successful / stats.totalTasks) * 100) 
        : 100;
      const active = formatTimestamp(stats.lastActive);
      console.log(`   ${name.padEnd(12)} ${String(stats.totalTasks).padStart(4)} tasks | ${success}% success | ${formatDuration(stats.avgDurationMs)} avg | ${active}`);
    }
  }
  
  // Recent events
  const recent = getRecentEvents(5);
  if (recent.length > 0) {
    console.log('\n📝 Recent Events:');
    for (const event of recent) {
      const icon = event.event.includes('completed') ? '✓' :
                   event.event.includes('failed') ? '✗' :
                   event.event.includes('started') ? '▶' :
                   event.event.includes('waiting') ? '⏸' :
                   event.event.includes('approved') ? '✓' : '•';
      console.log(`   ${icon} ${event.event} ${event.taskId || event.runId || ''} (${formatTimestamp(event.ts)})`);
    }
  }
  
  console.log('');
}

function showAgentAudit(agentName) {
  const stats = getAgentStats(agentName);
  const s = stats.stats;
  
  console.log(`\n📊 Agent Audit: ${agentName}\n`);
  console.log('─'.repeat(40));
  
  console.log('\n📈 Statistics:');
  console.log(`   Total Tasks:   ${s.totalTasks}`);
  console.log(`   Successful:    ${s.successful}`);
  console.log(`   Failed:        ${s.failed}`);
  console.log(`   Success Rate:  ${s.totalTasks > 0 ? Math.round((s.successful / s.totalTasks) * 100) : 100}%`);
  console.log(`   Avg Duration:  ${formatDuration(s.avgDurationMs)}`);
  console.log(`   Tokens In:     ${s.totalTokensIn.toLocaleString()}`);
  console.log(`   Tokens Out:    ${s.totalTokensOut.toLocaleString()}`);
  console.log(`   Last Active:   ${formatTimestamp(s.lastActive)}`);
  
  if (stats.recentFailures.length > 0) {
    console.log('\n❌ Recent Failures:');
    for (const failure of stats.recentFailures.slice(-5)) {
      console.log(`   • ${formatTimestamp(failure.ts)}: ${failure.error.substring(0, 60)}`);
    }
  }
  
  console.log('');
}

function showAuditLog(limit = 20) {
  const events = getRecentEvents(limit);
  
  console.log(`\n📜 Recent Events (last ${events.length})\n`);
  
  if (events.length === 0) {
    console.log('   (no events yet)');
    return;
  }
  
  for (const event of events) {
    const icon = event.event.includes('completed') ? '✓' :
                 event.event.includes('failed') ? '✗' :
                 event.event.includes('started') ? '▶' :
                 event.event.includes('waiting') ? '⏸' :
                 event.event.includes('approved') ? '✓' :
                 event.event.includes('rejected') ? '✗' : '•';
    
    let details = '';
    if (event.taskId) details += ` task:${event.taskId}`;
    if (event.agent) details += ` agent:${event.agent}`;
    if (event.runId) details += ` run:${event.runId}`;
    if (event.durationMs) details += ` ${formatDuration(event.durationMs)}`;
    if (event.error) details += ` error:"${event.error.substring(0, 30)}..."`;
    
    console.log(`${icon} ${event.event.padEnd(20)}${details} (${formatTimestamp(event.ts)})`);
  }
  console.log('');
}

function showSlowestTasks(limit = 10) {
  const tasks = getSlowestTasks(limit);
  
  console.log(`\n🐢 Slowest Tasks (top ${tasks.length})\n`);
  
  if (tasks.length === 0) {
    console.log('   (no completed tasks yet)');
    return;
  }
  
  for (const task of tasks) {
    console.log(`   ${formatDuration(task.durationMs).padEnd(8)} ${task.agent.padEnd(12)} ${task.taskId} (${formatTimestamp(task.ts)})`);
  }
  console.log('');
}

function showRecentFailures(limit = 10) {
  const failures = getRecentFailures(limit);
  
  console.log(`\n❌ Recent Failures (last ${failures.length})\n`);
  
  if (failures.length === 0) {
    console.log('   (no failures - nice!)');
    return;
  }
  
  for (const f of failures) {
    console.log(`   ${f.agent.padEnd(12)} ${f.taskId} (${formatTimestamp(f.ts)})`);
    console.log(`      Error: ${f.error.substring(0, 70)}${f.error.length > 70 ? '...' : ''}`);
  }
  console.log('');
}

// ============ Exports ============

export {
  // Logging
  logEvent,
  logTaskStarted,
  logTaskCompleted,
  logTaskFailed,
  logCheckpointWaiting,
  logCheckpointApproved,
  logCheckpointRejected,
  logProcessStarted,
  logProcessCompleted,
  logFeedbackReceived,
  
  // Stats
  getAgentStats,
  updateAgentStats,
  getGlobalStats,
  updateGlobalStats,
  
  // Queries
  getRecentEvents,
  getSlowestTasks,
  getRecentFailures,
  getEventsByType,
  
  // Display
  showAuditDashboard,
  showAgentAudit,
  showAuditLog,
  showSlowestTasks,
  showRecentFailures,
  formatDuration,
  formatTimestamp,
  
  // Paths
  AUDIT_DIR,
  AGENTS_AUDIT_DIR,
  LOG_FILE,
  GLOBAL_STATS_FILE,
  
  // Setup
  ensureAuditDirs
};
