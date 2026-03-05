#!/usr/bin/env node
/**
 * Agent Wrapper - Template for sub-agent execution
 * 
 * This script wraps sub-agent execution to:
 * 1. Load agent role definition from agents.yaml
 * 2. Load agent memory and global context
 * 3. Execute the task
 * 4. Write output to colony/context/<task-id>.md
 * 5. Update tasks.json on completion/failure
 * 6. Update audit stats
 * 7. Optionally prompt for reflection
 * 
 * Usage: node agent-wrapper.mjs <agent-name> <task-id> "<task-description>"
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { execSync } from 'child_process';
import yaml from 'js-yaml';

// Import audit and learning modules
import {
  logTaskStarted, logTaskCompleted, logTaskFailed,
  ensureAuditDirs
} from './audit.mjs';

import {
  getAgentMemory, addToAgentMemory,
  getGlobalContext,
  ensureMemoryDir
} from './learning.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const COLONY_DIR = join(__dirname, '..', 'colony');
const AGENTS_FILE = join(COLONY_DIR, 'agents.yaml');
const TASKS_FILE = join(COLONY_DIR, 'tasks.json');
const CONTEXT_DIR = join(COLONY_DIR, 'context');

// Atomic read/write for tasks.json
function readTasks() {
  try {
    return JSON.parse(readFileSync(TASKS_FILE, 'utf-8'));
  } catch (e) {
    return { queue: [], active: {}, completed: [], failed: [] };
  }
}

function writeTasks(tasks) {
  const tmp = TASKS_FILE + '.tmp';
  writeFileSync(tmp, JSON.stringify(tasks, null, 2));
  execSync(`mv ${tmp} ${TASKS_FILE}`);
}

// Load agent definitions
function loadAgents() {
  const content = readFileSync(AGENTS_FILE, 'utf-8');
  return yaml.load(content);
}

// Write context file for a task
function writeContext(taskId, content, runId = null) {
  const contextDir = runId ? join(CONTEXT_DIR, runId) : CONTEXT_DIR;
  if (!existsSync(contextDir)) {
    mkdirSync(contextDir, { recursive: true });
  }
  const contextFile = join(contextDir, `${taskId}.md`);
  writeFileSync(contextFile, content);
  return contextFile;
}

// Mark task as completed with audit logging
function completeTask(agentName, taskId, result, durationMs = null) {
  const tasks = readTasks();
  const task = tasks.active[agentName];
  
  if (!task || task.id !== taskId) {
    console.error(`Task ${taskId} not found in active tasks for ${agentName}`);
    return false;
  }
  
  // Calculate duration if not provided
  const duration = durationMs || (Date.now() - new Date(task.startedAt).getTime());
  
  // Move from active to completed
  delete tasks.active[agentName];
  task.status = 'completed';
  task.completedAt = new Date().toISOString();
  task.durationMs = duration;
  task.result = result;
  tasks.completed.push(task);
  
  // Trim completed to last 100
  if (tasks.completed.length > 100) {
    tasks.completed = tasks.completed.slice(-100);
  }
  
  writeTasks(tasks);
  
  // Log to audit system
  logTaskCompleted(taskId, agentName, duration, {}, true);
  
  return true;
}

// Mark task as failed with audit logging
function failTask(agentName, taskId, error, durationMs = null) {
  const tasks = readTasks();
  const task = tasks.active[agentName];
  
  if (!task || task.id !== taskId) {
    // Try to find in queue
    const queueIdx = tasks.queue.findIndex(t => t.id === taskId);
    if (queueIdx !== -1) {
      const queuedTask = tasks.queue.splice(queueIdx, 1)[0];
      queuedTask.status = 'failed';
      queuedTask.completedAt = new Date().toISOString();
      queuedTask.result = error;
      tasks.failed.push(queuedTask);
      writeTasks(tasks);
      return true;
    }
    console.error(`Task ${taskId} not found`);
    return false;
  }
  
  // Calculate duration if not provided
  const duration = durationMs || (Date.now() - new Date(task.startedAt).getTime());
  
  // Move from active to failed
  delete tasks.active[agentName];
  task.status = 'failed';
  task.completedAt = new Date().toISOString();
  task.durationMs = duration;
  task.result = error;
  tasks.failed.push(task);
  
  // Trim failed to last 50
  if (tasks.failed.length > 50) {
    tasks.failed = tasks.failed.slice(-50);
  }
  
  writeTasks(tasks);
  
  // Log to audit system
  logTaskFailed(taskId, agentName, duration, error);
  
  return true;
}

// Get agent info
function getAgentInfo(agentName) {
  const config = loadAgents();
  const agent = config.agents[agentName];
  if (!agent) {
    throw new Error(`Unknown agent: ${agentName}`);
  }
  return agent;
}

// Build context for agent prompt including memory and global context
function buildAgentContext(agentName) {
  const agent = getAgentInfo(agentName);
  const memory = getAgentMemory(agentName);
  const globalContext = getGlobalContext();
  
  let context = {
    agent,
    memory: null,
    globalContext: null
  };
  
  // Parse memory for relevant lessons (exclude empty placeholders and separator)
  if (memory) {
    const memoryLines = memory.split('\n').filter(l => 
      l.startsWith('- ') && 
      !l.includes('(populated') && 
      !l.includes('(document') && 
      !l.includes('(learn from') && 
      !l.includes('(any discovered')
    );
    if (memoryLines.length > 0) {
      context.memory = memoryLines.join('\n');
    }
  }
  
  // Include relevant global context
  if (globalContext.activeFacts?.length > 0 || globalContext.currentProjects?.length > 0) {
    context.globalContext = globalContext;
  }
  
  return context;
}

// Add reflection to agent memory after task completion
function addReflection(agentName, reflection, section = 'Lessons Learned') {
  if (reflection && reflection.trim().length > 10) {
    return addToAgentMemory(agentName, reflection.trim(), section);
  }
  return false;
}

// Export utilities for use by sub-agents
export {
  readTasks,
  writeTasks,
  loadAgents,
  writeContext,
  completeTask,
  failTask,
  getAgentInfo,
  buildAgentContext,
  addReflection,
  getAgentMemory,
  getGlobalContext,
  COLONY_DIR,
  CONTEXT_DIR
};

// CLI mode
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [agentName, taskId, action, ...rest] = process.argv.slice(2);
  
  // Ensure directories exist
  ensureAuditDirs();
  ensureMemoryDir();
  
  if (!agentName || !taskId || !action) {
    console.log(`Agent Wrapper - Task lifecycle management with learning

Usage:
  agent-wrapper.mjs <agent> <task-id> complete "<result>"
  agent-wrapper.mjs <agent> <task-id> fail "<error>"
  agent-wrapper.mjs <agent> <task-id> context "<content>"
  agent-wrapper.mjs <agent> <task-id> info
  agent-wrapper.mjs <agent> <task-id> build-context
  agent-wrapper.mjs <agent> <task-id> reflect "<lesson>" [--section <name>]

Examples:
  node agent-wrapper.mjs scuttle abc123 complete "Found 5 databases..."
  node agent-wrapper.mjs pincer def456 fail "Could not parse file"
  node agent-wrapper.mjs shell ghi789 context "# Deployment Log\\n..."
  node agent-wrapper.mjs scout xyz789 build-context
  node agent-wrapper.mjs scout xyz789 reflect "Always verify dates in sources"
`);
    process.exit(1);
  }
  
  try {
    switch (action) {
      case 'complete': {
        const result = rest.join(' ');
        const durationIdx = rest.indexOf('--duration');
        const duration = durationIdx !== -1 ? parseInt(rest[durationIdx + 1], 10) : null;
        const resultText = durationIdx !== -1 ? rest.slice(0, durationIdx).join(' ') : result;
        
        if (completeTask(agentName, taskId, resultText, duration)) {
          console.log(`✓ Task ${taskId} completed`);
        }
        break;
      }
        
      case 'fail': {
        const error = rest.join(' ');
        const durationIdx = rest.indexOf('--duration');
        const duration = durationIdx !== -1 ? parseInt(rest[durationIdx + 1], 10) : null;
        const errorText = durationIdx !== -1 ? rest.slice(0, durationIdx).join(' ') : error;
        
        if (failTask(agentName, taskId, errorText, duration)) {
          console.log(`✗ Task ${taskId} failed`);
        }
        break;
      }
        
      case 'context': {
        const runIdIdx = rest.indexOf('--run');
        const runId = runIdIdx !== -1 ? rest[runIdIdx + 1] : null;
        const content = runIdIdx !== -1 ? rest.slice(0, runIdIdx).join(' ') : rest.join(' ');
        
        const file = writeContext(taskId, content, runId);
        console.log(`Wrote context to ${file}`);
        break;
      }
        
      case 'info': {
        const agent = getAgentInfo(agentName);
        console.log(`Agent: ${agentName}`);
        console.log(`Role: ${agent.role}`);
        console.log(`Description: ${agent.description.trim()}`);
        console.log(`Model: ${agent.model}`);
        break;
      }
      
      case 'build-context': {
        const context = buildAgentContext(agentName);
        console.log('\n=== Agent Context ===');
        console.log(`Agent: ${agentName} (${context.agent.role})`);
        
        if (context.memory) {
          console.log('\n--- Memory ---');
          console.log(context.memory);
        } else {
          console.log('\n(no memory yet)');
        }
        
        if (context.globalContext) {
          console.log('\n--- Global Context ---');
          if (context.globalContext.currentProjects?.length > 0) {
            console.log(`Projects: ${context.globalContext.currentProjects.join(', ')}`);
          }
          if (context.globalContext.activeFacts?.length > 0) {
            console.log(`Facts: ${context.globalContext.activeFacts.join('; ')}`);
          }
        }
        break;
      }
      
      case 'reflect': {
        const sectionIdx = rest.indexOf('--section');
        const section = sectionIdx !== -1 ? rest[sectionIdx + 1] : 'Lessons Learned';
        const lesson = sectionIdx !== -1 ? rest.slice(0, sectionIdx).join(' ') : rest.join(' ');
        
        if (addReflection(agentName, lesson, section)) {
          console.log(`✓ Added reflection to ${agentName}'s "${section}"`);
        } else {
          console.log('Reflection too short or already exists');
        }
        break;
      }
        
      default:
        console.error(`Unknown action: ${action}`);
        process.exit(1);
    }
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  }
}
