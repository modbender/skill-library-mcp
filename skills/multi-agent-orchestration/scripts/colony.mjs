#!/usr/bin/env node
/**
 * Colony CLI - Multi-agent task orchestration with process support
 * 
 * Task Commands:
 *   dispatch "<task>"        Auto-route to best agent
 *   assign <agent> "<task>"  Manually assign to agent
 *   status                   Show agent status
 *   queue                    Show pending tasks
 *   results [task-id]        Show task results
 *   history [--limit N]      Show completed/failed tasks
 * 
 * Process Commands:
 *   processes                List available processes
 *   process <name> --context "..."  Start a process
 *   process-status [run-id]  Show process run status
 *   runs [--limit N]         Show process run history
 *   approve <run-id>         Approve checkpoint to continue
 *   cancel <run-id>          Cancel a running process
 * 
 * Audit Commands:
 *   audit                    Summary dashboard
 *   audit agent <name>       Detailed stats for one agent
 *   audit log [--limit N]    Recent events
 *   audit slow [--limit N]   Slowest tasks
 *   audit failures [--limit N]  Recent failures
 * 
 * Learning Commands:
 *   feedback <task-id> "text"   Record feedback for a task
 *   memory <agent>              View agent's memory
 *   memory <agent> add "lesson" Add to agent's memory
 *   learn                       Show shared learnings
 *   learn add "lesson" --category <cat>  Add shared learning
 *   context                     Show global context
 *   context set <key> <value>   Update global context
 *   context add-fact "fact"     Add to activeFacts
 *   context add-decision "dec" --project <name>  Add decision
 *   retro [--days N]            Review recent tasks
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { execSync, spawn } from 'child_process';
import yaml from 'js-yaml';

// Import audit and learning modules
import {
  logTaskStarted, logTaskCompleted, logTaskFailed,
  logCheckpointWaiting, logCheckpointApproved,
  logProcessStarted, logProcessCompleted,
  showAuditDashboard, showAgentAudit, showAuditLog,
  showSlowestTasks, showRecentFailures,
  ensureAuditDirs
} from './audit.mjs';

import {
  logFeedbackReceived
} from './audit.mjs';

import {
  getAgentMemory, addToAgentMemory,
  addFeedback,
  getLearnings, addLearning,
  getGlobalContext, setContextValue, addActiveFact, addDecision,
  showAgentMemory, showLearnings, showGlobalContext, showRetro,
  ensureMemoryDir
} from './learning.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const COLONY_DIR = join(__dirname, '..', 'colony');
const AGENTS_FILE = join(COLONY_DIR, 'agents.yaml');
const TASKS_FILE = join(COLONY_DIR, 'tasks.json');
const PROCESSES_FILE = join(COLONY_DIR, 'processes.yaml');
const RUNS_FILE = join(COLONY_DIR, 'runs.json');
const CONTEXT_DIR = join(COLONY_DIR, 'context');
const CONFIG_FILE = join(COLONY_DIR, 'config.yaml');

// ============ Config & Notifications ============

function loadConfig() {
  try {
    if (existsSync(CONFIG_FILE)) {
      return yaml.load(readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {
    console.error('Error loading config:', e.message);
  }
  // Default config
  return { 
    notifications: { 
      enabled: true, 
      on_checkpoint: true, 
      on_complete: true, 
      on_failure: true 
    } 
  };
}

function writeConfig(config) {
  const tmp = CONFIG_FILE + '.tmp';
  writeFileSync(tmp, yaml.dump(config, { indent: 2 }));
  execSync(`mv ${tmp} ${CONFIG_FILE}`);
}

function notify(message) {
  const config = loadConfig();
  if (!config.notifications?.enabled) {
    console.log('[notify] Notifications disabled');
    return;
  }
  
  try {
    // Send message via openclaw message send to the configured target
    const target = config.notifications?.target || 'YOUR_PHONE_NUMBER';
    // Escape for shell
    const escapedMessage = message.replace(/'/g, "'\\''");
    const cmd = `openclaw message send --channel telegram --target '${target}' --message '${escapedMessage}'`;
    console.log('[notify] Sending notification...');
    execSync(cmd, {
      timeout: 15000,
      stdio: 'inherit'
    });
    console.log('[notify] Notification sent');
  } catch (e) {
    console.error('[notify] Notification failed:', e.message);
  }
}

function notifyCheckpoint(runId, stage, processName) {
  const config = loadConfig();
  if (!config.notifications?.on_checkpoint) return;
  notify(`🛑 Colony checkpoint: Process "${processName}" paused after stage "${stage}". To continue: colony approve ${runId}`);
}

function notifyComplete(runId, processName, durationMs) {
  const config = loadConfig();
  if (!config.notifications?.on_complete) return;
  const duration = (durationMs / 1000).toFixed(0);
  notify(`✅ Colony complete: Process "${processName}" finished in ${duration}s. Run ID: ${runId}`);
}

function notifyFailure(runId, processName, stage, error) {
  const config = loadConfig();
  if (!config.notifications?.on_failure) return;
  // Truncate error message if too long
  const shortError = error && error.length > 100 ? error.substring(0, 100) + '...' : error;
  notify(`❌ Colony failed: Process "${processName}" failed at stage "${stage}". Error: ${shortError}. Run ID: ${runId}`);
}

// ============ Utilities ============

function generateId() {
  return Math.random().toString(36).substring(2, 10);
}

function timeSince(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

// ============ File I/O ============

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

function readRuns() {
  try {
    return JSON.parse(readFileSync(RUNS_FILE, 'utf-8'));
  } catch (e) {
    return { active: {}, paused: [], completed: [] };
  }
}

function writeRuns(runs) {
  const tmp = RUNS_FILE + '.tmp';
  writeFileSync(tmp, JSON.stringify(runs, null, 2));
  execSync(`mv ${tmp} ${RUNS_FILE}`);
}

function loadAgents() {
  try {
    const content = readFileSync(AGENTS_FILE, 'utf-8');
    return yaml.load(content);
  } catch (e) {
    console.error('Error loading agents.yaml:', e.message);
    process.exit(1);
  }
}

function loadProcesses() {
  try {
    const content = readFileSync(PROCESSES_FILE, 'utf-8');
    return yaml.load(content);
  } catch (e) {
    console.error('Error loading processes.yaml:', e.message);
    process.exit(1);
  }
}

// ============ Task Operations ============

function findBestAgent(taskDescription, agentConfig) {
  const desc = taskDescription.toLowerCase();
  let bestAgent = null;
  let bestScore = 0;

  for (const [name, agent] of Object.entries(agentConfig.agents)) {
    const triggers = agent.triggers || [];
    let score = 0;
    for (const trigger of triggers) {
      if (desc.includes(trigger.toLowerCase())) {
        score += trigger.length;
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestAgent = name;
    }
  }

  return bestAgent || agentConfig.default_agent || 'scuttle';
}

async function spawnAgent(agentName, task, agentConfig, options = {}) {
  const agent = agentConfig.agents[agentName];
  if (!agent) {
    console.error(`Unknown agent: ${agentName}`);
    process.exit(1);
  }

  const taskId = options.taskId || generateId();
  const now = new Date().toISOString();
  const startTime = Date.now();

  const taskRecord = {
    id: taskId,
    type: agent.role,
    description: task,
    agent: agentName,
    status: 'active',
    createdAt: now,
    startedAt: now,
    completedAt: null,
    result: null,
    runId: options.runId || null,
    stageId: options.stageId || null
  };

  // Update tasks.json
  const tasks = readTasks();
  tasks.active[agentName] = taskRecord;
  writeTasks(tasks);

  // Log task started event
  logTaskStarted(taskId, agentName, {
    runId: options.runId,
    stageId: options.stageId
  });

  // Build input context from previous stage outputs
  let inputContext = '';
  if (options.inputs && options.runId) {
    const runContextDir = join(CONTEXT_DIR, options.runId);
    for (const inputFile of options.inputs) {
      const inputPath = join(runContextDir, inputFile);
      if (existsSync(inputPath)) {
        inputContext += `\n\n## Input: ${inputFile}\n\n${readFileSync(inputPath, 'utf-8')}`;
      }
    }
  }

  // Load agent memory and global context
  const agentMemory = getAgentMemory(agentName);
  const globalContext = getGlobalContext();
  
  let memorySection = '';
  if (agentMemory) {
    // Filter for actual lessons (exclude placeholders and separator)
    const memoryLines = agentMemory.split('\n').filter(l => 
      l.startsWith('- ') && !l.includes('(populated') && !l.includes('(document') && !l.includes('(learn from') && !l.includes('(any discovered')
    );
    if (memoryLines.length > 0) {
      memorySection = `\n\n## Your Memory (lessons from past tasks)\n${memoryLines.join('\n')}`;
    }
  }
  
  let contextSection = '';
  if (globalContext.activeFacts?.length > 0 || globalContext.currentProjects?.length > 0) {
    contextSection = '\n\n## Global Context';
    if (globalContext.currentProjects?.length > 0) {
      contextSection += `\nProjects: ${globalContext.currentProjects.join(', ')}`;
    }
    if (globalContext.activeFacts?.length > 0) {
      contextSection += `\nFacts: ${globalContext.activeFacts.join('; ')}`;
    }
    if (globalContext.preferences) {
      contextSection += `\nPreferences: ${Object.entries(globalContext.preferences).map(([k,v]) => `${k}=${v}`).join(', ')}`;
    }
  }

  const prompt = `# Task Assignment

You are **${agentName}**, the ${agent.role} agent.

## Your Role
${agent.description}
${memorySection}${contextSection}

## Task
${task}
${inputContext ? `\n## Context from Previous Stages${inputContext}` : ''}

## Instructions
1. Complete this task thoroughly
2. Write your findings/output clearly
3. Be concise but comprehensive
${options.outputs ? `\n## Expected Outputs\nYour main output should be suitable for: ${options.outputs.join(', ')}` : ''}

## Output
When done, summarize what you accomplished. Your response will be saved as the task result.

Task ID: ${taskId}${options.runId ? `\nProcess Run: ${options.runId}` : ''}${options.stageId ? `\nStage: ${options.stageId}` : ''}
`;

  const model = agent.model || 'anthropic/claude-sonnet-4';
  const sessionId = `colony-${agentName}-${taskId}`;
  
  if (!options.silent) {
    console.log(`→ Agent: ${agentName} (${agent.role})`);
    console.log(`→ Model: ${model}`);
    console.log(`→ Task ID: ${taskId}`);
    if (options.runId) console.log(`→ Process Run: ${options.runId}`);
  }
  
  // Determine spawn mode: 'blocking' for process stages, 'async' for dispatch/assign
  const spawnMode = options.blocking ? 'blocking' : 'async';
  
  // Write prompt to temp file to avoid shell escaping issues
  const promptFile = join(CONTEXT_DIR, `${taskId}-prompt.txt`);
  ensureDir(CONTEXT_DIR);
  writeFileSync(promptFile, prompt);
  
  // Write task metadata for the worker script
  const taskMeta = {
    taskId,
    agentName,
    agentRole: agent.role,
    sessionId,
    promptFile,
    tasksFile: TASKS_FILE,
    contextDir: options.runId ? join(CONTEXT_DIR, options.runId) : CONTEXT_DIR,
    startTime,
    outputs: options.outputs || [],
    runId: options.runId || null,
    stageId: options.stageId || null,
    taskDescription: task,
    createdAt: now
  };
  const metaFile = join(CONTEXT_DIR, `${taskId}-meta.json`);
  writeFileSync(metaFile, JSON.stringify(taskMeta, null, 2));
  
  if (!options.silent) console.log(`→ Spawning agent (${spawnMode} mode)...`);
  
  if (spawnMode === 'async') {
    // Non-blocking: spawn detached worker process and return immediately
    const workerScript = join(__dirname, 'colony-worker.mjs');
    
    const child = spawn('node', [workerScript, metaFile], {
      detached: true,
      stdio: 'ignore',
      cwd: COLONY_DIR
    });
    child.unref();
    
    if (!options.silent) {
      console.log(`→ Task ${taskId} dispatched (running in background)`);
      console.log(`→ Check status: colony status`);
      console.log(`→ View results: colony results ${taskId}`);
    }
    
    return { success: true, taskId, status: 'dispatched', durationMs: 0 };
    
  } else {
    // Blocking mode: wait for completion (used by process stages)
    // Uses spawn instead of execSync to avoid timeout issues with long-running agents
    return await runBlockingAgent({
      promptFile,
      metaFile,
      sessionId,
      taskId,
      task,
      agentName,
      taskRecord,
      startTime,
      options,
      CONTEXT_DIR,
      TASKS_FILE
    });
  }
}

/**
 * Run an agent in blocking mode using spawn (no timeout)
 * This is used by process stages that need to wait for completion
 */
async function runBlockingAgent(params) {
  const {
    promptFile,
    metaFile,
    sessionId,
    taskId,
    task,
    agentName,
    taskRecord,
    startTime,
    options,
    CONTEXT_DIR,
    TASKS_FILE
  } = params;

  return new Promise((resolve) => {
    // Read prompt from file
    const promptContent = readFileSync(promptFile, 'utf-8');
    
    // Spawn openclaw agent with a very long timeout (24 hours)
    // This allows complex multi-stage processes to complete without interruption
    const child = spawn('openclaw', [
      'agent',
      '--session-id', sessionId,
      '--message', promptContent,
      '--json',
      '--timeout', '86400'  // 24 hours - effectively no timeout for process stages
    ], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: COLONY_DIR
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('error', (err) => {
      const durationMs = Date.now() - startTime;
      handleAgentFailure({
        taskId, agentName, taskRecord, durationMs,
        error: `Spawn error: ${err.message}`,
        promptFile, metaFile, silent: options.silent,
        TASKS_FILE
      });
      resolve({ success: false, taskId, error: err.message, durationMs });
    });
    
    child.on('close', (code) => {
      const durationMs = Date.now() - startTime;
      
      if (code !== 0) {
        const errorMsg = stderr || `Agent exited with code ${code}`;
        handleAgentFailure({
          taskId, agentName, taskRecord, durationMs,
          error: errorMsg,
          promptFile, metaFile, silent: options.silent,
          TASKS_FILE
        });
        resolve({ success: false, taskId, error: errorMsg, durationMs });
        return;
      }
      
      // Parse the JSON response
      let response;
      try {
        response = JSON.parse(stdout.trim());
      } catch {
        response = { content: stdout.trim() };
      }
      
      const output = response.content || response.message || stdout.trim();
      
      // Extract token usage if available
      const tokens = {
        in: response.usage?.input_tokens || 0,
        out: response.usage?.output_tokens || 0
      };
      
      // Write context file
      const contextDir = options.runId ? join(CONTEXT_DIR, options.runId) : CONTEXT_DIR;
      ensureDir(contextDir);
      
      // Write main task output
      const contextFile = join(contextDir, `${taskId}.md`);
      writeFileSync(contextFile, `# Task: ${task}\n\nAgent: ${agentName}\nCompleted: ${new Date().toISOString()}\nDuration: ${durationMs}ms\n\n---\n\n${output}`);
      
      // Also write to expected output files for process stages
      if (options.outputs && options.runId) {
        for (const outputFile of options.outputs) {
          if (!outputFile.endsWith('/')) { // Skip directory outputs
            const outputPath = join(contextDir, outputFile);
            writeFileSync(outputPath, output);
          }
        }
      }
      
      // Mark complete
      const updatedTasks = readTasks();
      delete updatedTasks.active[agentName];
      taskRecord.status = 'completed';
      taskRecord.completedAt = new Date().toISOString();
      taskRecord.durationMs = durationMs;
      taskRecord.result = output.substring(0, 500) + (output.length > 500 ? '...' : '');
      updatedTasks.completed.push(taskRecord);
      
      // Trim to last 100
      if (updatedTasks.completed.length > 100) {
        updatedTasks.completed = updatedTasks.completed.slice(-100);
      }
      
      writeTasks(updatedTasks);
      
      // Log completion event and update stats
      logTaskCompleted(taskId, agentName, durationMs, tokens, true);
      
      // Cleanup temp files
      try { execSync(`rm -f "${promptFile}" "${metaFile}"`); } catch {}
      
      if (!options.silent) {
        console.log(`→ Task ${taskId} completed (${durationMs}ms)`);
      }
      
      resolve({ success: true, taskId, output, durationMs });
    });
  });
}

/**
 * Handle agent failure - update task state and cleanup
 */
function handleAgentFailure(params) {
  const {
    taskId, agentName, taskRecord, durationMs, error,
    promptFile, metaFile, silent, TASKS_FILE
  } = params;
  
  const updatedTasks = readTasks();
  delete updatedTasks.active[agentName];
  taskRecord.status = 'failed';
  taskRecord.completedAt = new Date().toISOString();
  taskRecord.durationMs = durationMs;
  taskRecord.result = `Agent error: ${error}`;
  updatedTasks.failed.push(taskRecord);
  writeTasks(updatedTasks);
  
  // Log failure event and update stats
  logTaskFailed(taskId, agentName, durationMs, error);
  
  // Cleanup temp files
  try { execSync(`rm -f "${promptFile}" "${metaFile}"`); } catch {}
  
  if (!silent) {
    console.error(`→ Task failed: ${error}`);
  }
}

// ============ Process Operations ============

function listProcesses() {
  const processConfig = loadProcesses();
  
  console.log('Available Processes\n');
  
  for (const [name, proc] of Object.entries(processConfig.processes)) {
    const stageCount = proc.stages?.length || 0;
    const checkpoints = proc.checkpoints || [];
    const checkpointCount = checkpoints.length + proc.stages?.filter(s => s.checkpoint)?.length || 0;
    
    console.log(`  ${name}`);
    console.log(`    ${proc.description}`);
    console.log(`    Stages: ${stageCount} | Checkpoints: ${checkpointCount}`);
    console.log(`    Triggers: ${(proc.triggers || []).join(', ')}`);
    console.log('');
  }
}

async function startProcess(processName, context) {
  const processConfig = loadProcesses();
  const agentConfig = loadAgents();
  const proc = processConfig.processes[processName];
  
  if (!proc) {
    console.error(`Unknown process: ${processName}`);
    console.log('\nAvailable processes:');
    Object.keys(processConfig.processes).forEach(p => console.log(`  - ${p}`));
    process.exit(1);
  }
  
  const runId = generateId();
  const now = new Date().toISOString();
  
  // Create run record
  const run = {
    id: runId,
    processId: processName,
    context: context,
    currentStageIndex: 0,
    currentStage: proc.stages[0]?.id || null,
    stageResults: {},
    startedAt: now,
    updatedAt: now,
    status: 'running'
  };
  
  // Create context directory
  const runContextDir = join(CONTEXT_DIR, runId);
  ensureDir(runContextDir);
  
  // Save initial context
  writeFileSync(join(runContextDir, 'context.md'), `# Process: ${processName}\n\nContext: ${context}\n\nStarted: ${now}\n`);
  
  // Save run
  const runs = readRuns();
  runs.active[runId] = run;
  writeRuns(runs);
  
  // Log process started
  logProcessStarted(runId, processName, context);
  
  console.log(`\n🚀 Starting process: ${processName}`);
  console.log(`   Run ID: ${runId}`);
  console.log(`   Context: ${context}`);
  console.log(`   Stages: ${proc.stages.length}\n`);
  
  // Execute stages
  await executeNextStage(runId, proc, agentConfig);
}

async function executeNextStage(runId, procDef, agentConfig) {
  const runs = readRuns();
  const run = runs.active[runId];
  
  if (!run) {
    console.error(`Run ${runId} not found in active runs`);
    return;
  }
  
  const proc = procDef || loadProcesses().processes[run.processId];
  const agents = agentConfig || loadAgents();
  
  const stageIndex = run.currentStageIndex;
  
  if (stageIndex >= proc.stages.length) {
    // Process complete
    const startTime = new Date(run.startedAt);
    const durationMs = Date.now() - startTime.getTime();
    
    run.status = 'completed';
    run.completedAt = new Date().toISOString();
    run.durationMs = durationMs;
    delete runs.active[runId];
    runs.completed.push(run);
    
    // Trim to last 50
    if (runs.completed.length > 50) {
      runs.completed = runs.completed.slice(-50);
    }
    
    writeRuns(runs);
    
    // Log process completed
    logProcessCompleted(runId, run.processId, durationMs);
    
    // Send completion notification
    notifyComplete(runId, run.processId, durationMs);
    
    console.log(`\n✅ Process ${run.processId} completed!`);
    console.log(`   Run ID: ${runId}`);
    console.log(`   Duration: ${timeSince(new Date(run.startedAt))}`);
    return;
  }
  
  const stage = proc.stages[stageIndex];
  const checkpoints = proc.checkpoints || [];
  
  // Check if this is a checkpoint-only stage
  if (stage.checkpoint && !stage.agent) {
    console.log(`\n--- Stage ${stageIndex + 1}/${proc.stages.length}: ${stage.id} ---`);
    
    run.status = 'paused';
    run.pausedAt = new Date().toISOString();
    run.pauseReason = stage.description || 'Checkpoint requires approval';
    run.updatedAt = new Date().toISOString();
    
    // Move to paused
    delete runs.active[runId];
    runs.paused.push(run);
    writeRuns(runs);
    
    // Log checkpoint
    logCheckpointWaiting(runId, stage.id);
    
    // Send checkpoint notification
    notifyCheckpoint(runId, stage.id, run.processId);
    
    console.log(`\n⏸️  Process paused at checkpoint: ${stage.id}`);
    console.log(`   Reason: ${stage.description || 'Human review required'}`);
    console.log(`   To continue: colony approve ${runId}`);
    return;
  }
  
  // Check for parallel group - collect all consecutive stages with same parallel_group
  if (stage.parallel_group) {
    const parallelGroup = stage.parallel_group;
    const parallelStages = [];
    let j = stageIndex;
    
    // Collect all consecutive stages with the same parallel_group
    while (j < proc.stages.length && proc.stages[j].parallel_group === parallelGroup) {
      parallelStages.push({ stage: proc.stages[j], index: j });
      j++;
    }
    
    if (parallelStages.length > 1) {
      console.log(`\n═══ Parallel Group: ${parallelGroup} (${parallelStages.length} stages) ═══`);
      parallelStages.forEach(({ stage: s, index: idx }) => {
        console.log(`    → Stage ${idx + 1}: ${s.id} (${s.agent})`);
      });
      console.log('');
      
      // Run all stages in parallel
      const parallelPromises = parallelStages.map(({ stage: s, index: idx }) => {
        const task = (s.task || '').replace('{context}', run.context);
        console.log(`\n--- [PARALLEL] Stage ${idx + 1}/${proc.stages.length}: ${s.id} ---`);
        
        return spawnAgent(s.agent, task, agents, {
          runId,
          stageId: s.id,
          inputs: s.inputs || [],
          outputs: s.outputs || [],
          silent: false,
          blocking: true
        }).then(result => ({ stage: s, index: idx, result }));
      });
      
      const parallelResults = await Promise.all(parallelPromises);
      
      // Process results
      let anyFailed = false;
      let failedStage = null;
      let failedError = null;
      
      for (const { stage: s, index: idx, result } of parallelResults) {
        run.stageResults[s.id] = {
          success: result.success,
          taskId: result.taskId,
          completedAt: new Date().toISOString(),
          durationMs: result.durationMs,
          error: result.error || null
        };
        
        if (!result.success && !anyFailed) {
          anyFailed = true;
          failedStage = s.id;
          failedError = result.error;
        }
      }
      
      run.updatedAt = new Date().toISOString();
      
      if (anyFailed) {
        run.status = 'failed';
        run.failedAt = new Date().toISOString();
        run.failedStage = failedStage;
        
        delete runs.active[runId];
        runs.paused.push(run);
        writeRuns(runs);
        
        // Send failure notification
        notifyFailure(runId, run.processId, failedStage, failedError);
        
        console.log(`\n❌ Process failed in parallel group at stage: ${failedStage}`);
        console.log(`   Error: ${failedError}`);
        console.log(`   To retry: colony approve ${runId}`);
        return;
      }
      
      console.log(`\n═══ Parallel Group: ${parallelGroup} completed ═══`);
      
      // Check if any parallel stage is a checkpoint
      const parallelCheckpoint = parallelStages.find(({ stage: s }) => checkpoints.includes(s.id));
      if (parallelCheckpoint) {
        run.status = 'paused';
        run.pausedAt = new Date().toISOString();
        run.pauseReason = `Checkpoint after parallel group ${parallelGroup}`;
        run.currentStageIndex = j;
        run.currentStage = proc.stages[j]?.id || null;
        
        delete runs.active[runId];
        runs.paused.push(run);
        writeRuns(runs);
        
        logCheckpointWaiting(runId, parallelCheckpoint.stage.id);
        
        // Send checkpoint notification
        notifyCheckpoint(runId, parallelCheckpoint.stage.id, run.processId);
        
        console.log(`\n⏸️  Process paused at checkpoint after parallel group: ${parallelGroup}`);
        console.log(`   To continue: colony approve ${runId}`);
        return;
      }
      
      // Move past all parallel stages
      run.currentStageIndex = j;
      run.currentStage = proc.stages[j]?.id || null;
      runs.active[runId] = run;
      writeRuns(runs);
      
      // Continue to next stage
      await executeNextStage(runId, proc, agents);
      return;
    }
  }
  
  // Single stage execution (no parallel group or only one stage in group)
  console.log(`\n--- Stage ${stageIndex + 1}/${proc.stages.length}: ${stage.id} ---`);
  
  // Replace {context} in task
  const task = (stage.task || '').replace('{context}', run.context);
  
  // Execute the stage (blocking mode for sequential process execution)
  const result = await spawnAgent(stage.agent, task, agents, {
    runId,
    stageId: stage.id,
    inputs: stage.inputs || [],
    outputs: stage.outputs || [],
    silent: false,
    blocking: true  // Process stages must wait for completion
  });
  
  // Update run with result
  run.stageResults[stage.id] = {
    success: result.success,
    taskId: result.taskId,
    completedAt: new Date().toISOString(),
    durationMs: result.durationMs,
    error: result.error || null
  };
  run.updatedAt = new Date().toISOString();
  
  if (!result.success) {
    run.status = 'failed';
    run.failedAt = new Date().toISOString();
    run.failedStage = stage.id;
    
    delete runs.active[runId];
    runs.paused.push(run); // Put in paused so it can be retried
    writeRuns(runs);
    
    // Send failure notification
    notifyFailure(runId, run.processId, stage.id, result.error);
    
    console.log(`\n❌ Process failed at stage: ${stage.id}`);
    console.log(`   Error: ${result.error}`);
    console.log(`   To retry: colony approve ${runId}`);
    return;
  }
  
  // Check if this stage is a checkpoint
  if (checkpoints.includes(stage.id)) {
    run.status = 'paused';
    run.pausedAt = new Date().toISOString();
    run.pauseReason = `Checkpoint after ${stage.id}`;
    run.currentStageIndex = stageIndex + 1;
    run.currentStage = proc.stages[stageIndex + 1]?.id || null;
    
    delete runs.active[runId];
    runs.paused.push(run);
    writeRuns(runs);
    
    // Log checkpoint
    logCheckpointWaiting(runId, stage.id);
    
    // Send checkpoint notification
    notifyCheckpoint(runId, stage.id, run.processId);
    
    console.log(`\n⏸️  Process paused at checkpoint after: ${stage.id}`);
    console.log(`   To continue: colony approve ${runId}`);
    return;
  }
  
  // Move to next stage
  run.currentStageIndex = stageIndex + 1;
  run.currentStage = proc.stages[stageIndex + 1]?.id || null;
  runs.active[runId] = run;
  writeRuns(runs);
  
  // Continue to next stage
  await executeNextStage(runId, proc, agents);
}

function showProcessStatus(runId) {
  const runs = readRuns();
  
  let run;
  if (runId) {
    run = runs.active[runId] || 
          runs.paused.find(r => r.id === runId) ||
          runs.completed.find(r => r.id === runId);
  } else {
    // Show latest active or paused
    const activeIds = Object.keys(runs.active);
    if (activeIds.length > 0) {
      run = runs.active[activeIds[0]];
    } else if (runs.paused.length > 0) {
      run = runs.paused[runs.paused.length - 1];
    } else if (runs.completed.length > 0) {
      run = runs.completed[runs.completed.length - 1];
    }
  }
  
  if (!run) {
    console.log('No process runs found');
    return;
  }
  
  const processConfig = loadProcesses();
  const proc = processConfig.processes[run.processId];
  
  console.log(`\nProcess Run: ${run.id}`);
  console.log(`Process: ${run.processId}`);
  console.log(`Context: ${run.context}`);
  console.log(`Status: ${run.status}`);
  console.log(`Started: ${run.startedAt}`);
  if (run.completedAt) console.log(`Completed: ${run.completedAt}`);
  if (run.pausedAt) console.log(`Paused: ${run.pausedAt}`);
  if (run.pauseReason) console.log(`Pause Reason: ${run.pauseReason}`);
  if (run.durationMs) console.log(`Duration: ${run.durationMs}ms`);
  
  console.log(`\nStages:`);
  for (let i = 0; i < proc.stages.length; i++) {
    const stage = proc.stages[i];
    const result = run.stageResults[stage.id];
    
    let status = '○'; // pending
    let extra = '';
    
    if (result) {
      status = result.success ? '✓' : '✗';
      if (result.durationMs) extra += ` (${result.durationMs}ms)`;
      if (result.error) extra += ` error: ${result.error}`;
    } else if (i === run.currentStageIndex && run.status === 'running') {
      status = '▶';
    } else if (i === run.currentStageIndex && run.status === 'paused') {
      status = '⏸';
    }
    
    const checkpoints = proc.checkpoints || [];
    const isCheckpoint = checkpoints.includes(stage.id) || stage.checkpoint;
    const checkpointMark = isCheckpoint ? ' 🔒' : '';
    
    console.log(`  ${status} ${stage.id}${checkpointMark}${extra}`);
  }
  
  // Show context files
  const runContextDir = join(CONTEXT_DIR, run.id);
  if (existsSync(runContextDir)) {
    const files = readdirSync(runContextDir);
    if (files.length > 0) {
      console.log(`\nOutput Files: ${runContextDir}/`);
      files.forEach(f => console.log(`  - ${f}`));
    }
  }
}

async function approveRun(runId) {
  const runs = readRuns();
  
  const pausedIndex = runs.paused.findIndex(r => r.id === runId);
  if (pausedIndex === -1) {
    console.error(`Run ${runId} not found in paused runs`);
    return;
  }
  
  const run = runs.paused[pausedIndex];
  runs.paused.splice(pausedIndex, 1);
  
  // Log checkpoint approved
  logCheckpointApproved(runId, run.currentStage || run.failedStage);
  
  // Handle failed runs - retry the failed stage
  if (run.status === 'failed') {
    console.log(`\n🔄 Retrying failed stage: ${run.failedStage}`);
    run.status = 'running';
    delete run.failedAt;
    delete run.failedStage;
    runs.active[runId] = run;
    writeRuns(runs);
  } else {
    // Normal checkpoint approval - move to next stage
    run.status = 'running';
    delete run.pausedAt;
    delete run.pauseReason;
    runs.active[runId] = run;
    writeRuns(runs);
    console.log(`\n▶️  Resuming process: ${runId}`);
  }
  
  const processConfig = loadProcesses();
  const proc = processConfig.processes[run.processId];
  
  await executeNextStage(runId, proc);
}

function cancelRun(runId) {
  const runs = readRuns();
  
  let run = runs.active[runId];
  let source = 'active';
  
  if (!run) {
    const pausedIndex = runs.paused.findIndex(r => r.id === runId);
    if (pausedIndex !== -1) {
      run = runs.paused[pausedIndex];
      runs.paused.splice(pausedIndex, 1);
      source = 'paused';
    }
  } else {
    delete runs.active[runId];
  }
  
  if (!run) {
    console.error(`Run ${runId} not found`);
    return;
  }
  
  run.status = 'cancelled';
  run.cancelledAt = new Date().toISOString();
  runs.completed.push(run);
  writeRuns(runs);
  
  console.log(`\n🛑 Cancelled process run: ${runId}`);
}

function showRuns(limit = 10) {
  const runs = readRuns();
  
  const activeList = Object.values(runs.active);
  const pausedList = runs.paused || [];
  const completedList = runs.completed || [];
  
  if (activeList.length === 0 && pausedList.length === 0 && completedList.length === 0) {
    console.log('No process runs');
    return;
  }
  
  if (activeList.length > 0) {
    console.log('\n🏃 Active Runs:');
    for (const run of activeList) {
      console.log(`  [${run.id}] ${run.processId} - Stage: ${run.currentStage} (${timeSince(new Date(run.startedAt))})`);
    }
  }
  
  if (pausedList.length > 0) {
    console.log('\n⏸️  Paused Runs:');
    for (const run of pausedList.slice(-limit)) {
      const reason = run.pauseReason || (run.status === 'failed' ? 'Failed' : 'Checkpoint');
      console.log(`  [${run.id}] ${run.processId} - ${reason}`);
    }
  }
  
  if (completedList.length > 0) {
    console.log('\n✅ Recent Completed:');
    for (const run of completedList.slice(-limit)) {
      const status = run.status === 'cancelled' ? '🛑' : '✅';
      console.log(`  ${status} [${run.id}] ${run.processId} (${timeSince(new Date(run.completedAt || run.cancelledAt))})`);
    }
  }
}

// ============ Display Commands ============

function showStatus() {
  const agentConfig = loadAgents();
  const tasks = readTasks();
  
  console.log('Colony Status\n');
  
  for (const [name, agent] of Object.entries(agentConfig.agents)) {
    const activeTask = tasks.active[name];
    if (activeTask) {
      const elapsed = timeSince(new Date(activeTask.startedAt));
      const shortDesc = activeTask.description.substring(0, 40) + (activeTask.description.length > 40 ? '...' : '');
      console.log(`${name}: ${agent.role} "${shortDesc}" (${elapsed})`);
    } else {
      console.log(`${name}: idle`);
    }
  }
}

function showQueue() {
  const tasks = readTasks();
  
  if (tasks.queue.length === 0) {
    console.log('Queue is empty');
    return;
  }
  
  console.log(`Pending Tasks (${tasks.queue.length})\n`);
  for (const task of tasks.queue) {
    console.log(`[${task.id}] ${task.agent}: ${task.description}`);
  }
}

function showResults(taskId) {
  const tasks = readTasks();
  
  let task;
  if (taskId) {
    task = tasks.completed.find(t => t.id === taskId) ||
           tasks.failed.find(t => t.id === taskId) ||
           Object.values(tasks.active).find(t => t.id === taskId);
  } else {
    task = tasks.completed[tasks.completed.length - 1];
  }
  
  if (!task) {
    console.log(taskId ? `Task ${taskId} not found` : 'No completed tasks');
    return;
  }
  
  console.log(`Task: ${task.id}`);
  console.log(`Agent: ${task.agent} (${task.type})`);
  console.log(`Status: ${task.status}`);
  console.log(`Description: ${task.description}`);
  console.log(`Created: ${task.createdAt}`);
  if (task.completedAt) console.log(`Completed: ${task.completedAt}`);
  if (task.durationMs) console.log(`Duration: ${task.durationMs}ms`);
  if (task.runId) console.log(`Process Run: ${task.runId}`);
  if (task.stageId) console.log(`Stage: ${task.stageId}`);
  console.log(`\n--- Result ---\n`);
  console.log(task.result || '(no result yet)');
  
  // Check for context file
  const contextDir = task.runId ? join(CONTEXT_DIR, task.runId) : CONTEXT_DIR;
  const contextFile = join(contextDir, `${task.id}.md`);
  if (existsSync(contextFile)) {
    console.log(`\n--- Full Context: ${contextFile} ---`);
  }
}

function showHistory(limit = 10) {
  const tasks = readTasks();
  
  const history = [...tasks.completed, ...tasks.failed]
    .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
    .slice(0, limit);
  
  if (history.length === 0) {
    console.log('No task history');
    return;
  }
  
  console.log(`Recent Tasks (${history.length})\n`);
  for (const task of history) {
    const status = task.status === 'completed' ? '✓' : '✗';
    const shortDesc = task.description.substring(0, 50) + (task.description.length > 50 ? '...' : '');
    const processInfo = task.runId ? ` [${task.runId.substring(0,6)}]` : '';
    const duration = task.durationMs ? ` ${task.durationMs}ms` : '';
    console.log(`${status} [${task.id}] ${task.agent}: ${shortDesc}${processInfo}${duration}`);
  }
}

function showHelp() {
  console.log(`Colony CLI - Multi-agent orchestration with processes

Task Commands:
  dispatch "<task>"           Auto-route to best agent
  assign <agent> "<task>"     Manually assign to agent  
  status                      Show agent status
  queue                       Show pending tasks
  results [task-id]           Show task results
  history [--limit N]         Show completed/failed tasks

Process Commands:
  processes                   List available processes
  process <name> --context "..."  Start a process
  process-status [run-id]     Show process run status
  runs [--limit N]            Show process run history
  approve <run-id>            Approve checkpoint/retry failed
  cancel <run-id>             Cancel a running process

Config Commands:
  config                      Show current config
  config set <key> <value>    Update config (e.g., notifications.enabled false)

Audit Commands:
  audit                       Summary dashboard
  audit agent <name>          Detailed stats for one agent
  audit log [--limit N]       Recent events (default 20)
  audit slow [--limit N]      Slowest tasks
  audit failures [--limit N]  Recent failures

Learning Commands:
  feedback <task-id> "text"   Record feedback for a task
  memory <agent>              View agent's memory
  memory <agent> add "lesson" Add to agent's memory
  learn                       Show shared learnings
  learn add "lesson" --category <cat>  Add shared learning
  context                     Show global context
  context set <key> <value>   Update global context
  context add-fact "fact"     Add to activeFacts
  context add-decision "dec" --project <name>  Add decision
  retro [--days N]            Review recent tasks

Agents:
  Research: scuttle, scout, forecast
  Code: pincer
  Ops: shell
  Product: forge, ledger
  Content: muse, scribe, quill, echo
  QA: sentry

Examples:
  colony dispatch "find top 5 vector databases"
  colony process validate-idea --context "AI meal planning for parents"
  colony approve abc123
  colony audit
  colony memory scout add "Always check competitor pricing"
`);
}

// ============ Main CLI ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // Ensure directories exist
  ensureAuditDirs();
  ensureMemoryDir();

  switch (command) {
    // Task commands
    case 'dispatch': {
      const task = args[1];
      if (!task) {
        console.error('Usage: colony dispatch "<task description>"');
        process.exit(1);
      }
      const agentConfig = loadAgents();
      const agent = findBestAgent(task, agentConfig);
      await spawnAgent(agent, task, agentConfig);
      break;
    }

    case 'assign': {
      const agent = args[1];
      const task = args[2];
      if (!agent || !task) {
        console.error('Usage: colony assign <agent> "<task description>"');
        process.exit(1);
      }
      const agentConfig = loadAgents();
      await spawnAgent(agent, task, agentConfig);
      break;
    }

    case 'status':
      showStatus();
      break;

    case 'queue':
      showQueue();
      break;

    case 'results':
      showResults(args[1]);
      break;

    case 'history': {
      let limit = 10;
      const limitIdx = args.indexOf('--limit');
      if (limitIdx !== -1 && args[limitIdx + 1]) {
        limit = parseInt(args[limitIdx + 1], 10);
      }
      showHistory(limit);
      break;
    }

    // Process commands
    case 'processes':
      listProcesses();
      break;

    case 'process': {
      const processName = args[1];
      if (!processName) {
        console.error('Usage: colony process <process-name> --context "description"');
        process.exit(1);
      }
      
      const contextIdx = args.indexOf('--context');
      const context = contextIdx !== -1 ? args[contextIdx + 1] : '';
      
      if (!context) {
        console.error('Context required. Usage: colony process <name> --context "description"');
        process.exit(1);
      }
      
      await startProcess(processName, context);
      break;
    }

    case 'process-status':
      showProcessStatus(args[1]);
      break;

    case 'runs': {
      let limit = 10;
      const limitIdx = args.indexOf('--limit');
      if (limitIdx !== -1 && args[limitIdx + 1]) {
        limit = parseInt(args[limitIdx + 1], 10);
      }
      showRuns(limit);
      break;
    }

    case 'approve': {
      const runId = args[1];
      if (!runId) {
        console.error('Usage: colony approve <run-id>');
        process.exit(1);
      }
      await approveRun(runId);
      break;
    }

    case 'cancel': {
      const runId = args[1];
      if (!runId) {
        console.error('Usage: colony cancel <run-id>');
        process.exit(1);
      }
      cancelRun(runId);
      break;
    }

    // Config commands
    case 'config': {
      const subCmd = args[1];
      
      if (!subCmd) {
        // Show current config
        const config = loadConfig();
        console.log('Colony Configuration\n');
        console.log(yaml.dump(config, { indent: 2 }));
      } else if (subCmd === 'set') {
        const key = args[2];
        const value = args[3];
        if (!key || value === undefined) {
          console.error('Usage: colony config set <key> <value>');
          console.error('Examples:');
          console.error('  colony config set notifications.enabled false');
          console.error('  colony config set notifications.on_checkpoint true');
          process.exit(1);
        }
        
        const config = loadConfig();
        
        // Parse nested keys (e.g., "notifications.enabled")
        const keys = key.split('.');
        let target = config;
        for (let i = 0; i < keys.length - 1; i++) {
          if (!target[keys[i]]) target[keys[i]] = {};
          target = target[keys[i]];
        }
        
        // Parse value (boolean, number, or string)
        let parsedValue = value;
        if (value === 'true') parsedValue = true;
        else if (value === 'false') parsedValue = false;
        else if (!isNaN(value)) parsedValue = Number(value);
        
        target[keys[keys.length - 1]] = parsedValue;
        writeConfig(config);
        console.log(`✓ Set ${key} = ${parsedValue}`);
      } else {
        console.error(`Unknown config subcommand: ${subCmd}`);
        console.log('Available: set <key> <value>');
      }
      break;
    }

    // Audit commands
    case 'audit': {
      const subCmd = args[1];
      
      if (!subCmd) {
        showAuditDashboard();
      } else if (subCmd === 'agent') {
        const agentName = args[2];
        if (!agentName) {
          console.error('Usage: colony audit agent <agent-name>');
          process.exit(1);
        }
        showAgentAudit(agentName);
      } else if (subCmd === 'log') {
        let limit = 20;
        const limitIdx = args.indexOf('--limit');
        if (limitIdx !== -1 && args[limitIdx + 1]) {
          limit = parseInt(args[limitIdx + 1], 10);
        }
        showAuditLog(limit);
      } else if (subCmd === 'slow') {
        let limit = 10;
        const limitIdx = args.indexOf('--limit');
        if (limitIdx !== -1 && args[limitIdx + 1]) {
          limit = parseInt(args[limitIdx + 1], 10);
        }
        showSlowestTasks(limit);
      } else if (subCmd === 'failures') {
        let limit = 10;
        const limitIdx = args.indexOf('--limit');
        if (limitIdx !== -1 && args[limitIdx + 1]) {
          limit = parseInt(args[limitIdx + 1], 10);
        }
        showRecentFailures(limit);
      } else {
        console.error(`Unknown audit subcommand: ${subCmd}`);
        console.log('Available: agent <name>, log, slow, failures');
      }
      break;
    }

    // Learning commands
    case 'feedback': {
      const taskId = args[1];
      const feedbackText = args[2];
      if (!taskId || !feedbackText) {
        console.error('Usage: colony feedback <task-id> "feedback text"');
        process.exit(1);
      }
      
      // Find the task to get agent info
      const tasks = readTasks();
      const task = tasks.completed.find(t => t.id === taskId) ||
                   tasks.failed.find(t => t.id === taskId);
      
      if (!task) {
        console.error(`Task ${taskId} not found`);
        process.exit(1);
      }
      
      const entry = addFeedback(taskId, task.agent, feedbackText);
      logFeedbackReceived(taskId, task.agent, feedbackText);
      console.log(`✓ Feedback recorded for ${task.agent} task ${taskId}`);
      break;
    }

    case 'memory': {
      const agentName = args[1];
      if (!agentName) {
        console.error('Usage: colony memory <agent> [add "lesson"]');
        process.exit(1);
      }
      
      const subCmd = args[2];
      if (subCmd === 'add') {
        const lesson = args[3];
        if (!lesson) {
          console.error('Usage: colony memory <agent> add "lesson text"');
          process.exit(1);
        }
        
        // Determine section from flags
        let section = 'Lessons Learned';
        if (args.includes('--pattern')) section = 'Patterns That Work';
        if (args.includes('--mistake')) section = 'Mistakes Made';
        if (args.includes('--pref')) section = 'Preferences';
        
        if (addToAgentMemory(agentName, lesson, section)) {
          console.log(`✓ Added to ${agentName}'s "${section}"`);
        } else {
          console.log('Lesson already exists or section not found');
        }
      } else {
        showAgentMemory(agentName);
      }
      break;
    }

    case 'learn': {
      const subCmd = args[1];
      
      if (!subCmd) {
        showLearnings();
      } else if (subCmd === 'add') {
        const lesson = args[2];
        if (!lesson) {
          console.error('Usage: colony learn add "lesson" --category <category>');
          process.exit(1);
        }
        
        const catIdx = args.indexOf('--category');
        const category = catIdx !== -1 ? args[catIdx + 1] : 'general';
        
        const sourceIdx = args.indexOf('--source');
        const source = sourceIdx !== -1 ? args[sourceIdx + 1] : null;
        
        addLearning(lesson, category, source);
        console.log(`✓ Added shared learning to category: ${category}`);
      } else {
        console.error(`Unknown learn subcommand: ${subCmd}`);
        console.log('Available: add "lesson" --category <cat>');
      }
      break;
    }

    case 'context': {
      const subCmd = args[1];
      
      if (!subCmd) {
        showGlobalContext();
      } else if (subCmd === 'set') {
        const key = args[2];
        const value = args[3];
        if (!key || !value) {
          console.error('Usage: colony context set <key> <value>');
          process.exit(1);
        }
        setContextValue(key, value);
        console.log(`✓ Set ${key} = ${value}`);
      } else if (subCmd === 'add-fact') {
        const fact = args[2];
        if (!fact) {
          console.error('Usage: colony context add-fact "fact text"');
          process.exit(1);
        }
        addActiveFact(fact);
        console.log(`✓ Added active fact`);
      } else if (subCmd === 'add-decision') {
        const decision = args[2];
        if (!decision) {
          console.error('Usage: colony context add-decision "decision" --project <name>');
          process.exit(1);
        }
        const projIdx = args.indexOf('--project');
        const project = projIdx !== -1 ? args[projIdx + 1] : null;
        addDecision(decision, project);
        console.log(`✓ Added decision${project ? ` to project: ${project}` : ''}`);
      } else if (subCmd === 'add-project') {
        const project = args[2];
        if (!project) {
          console.error('Usage: colony context add-project "project name"');
          process.exit(1);
        }
        const ctx = getGlobalContext();
        if (!ctx.currentProjects.includes(project)) {
          ctx.currentProjects.push(project);
          writeGlobalContext(ctx);
        }
        console.log(`✓ Added project: ${project}`);
      } else {
        console.error(`Unknown context subcommand: ${subCmd}`);
        console.log('Available: set <key> <value>, add-fact "fact", add-decision "dec", add-project "name"');
      }
      break;
    }

    case 'retro': {
      let days = 7;
      const daysIdx = args.indexOf('--days');
      if (daysIdx !== -1 && args[daysIdx + 1]) {
        days = parseInt(args[daysIdx + 1], 10);
      }
      showRetro(days);
      break;
    }

    default:
      showHelp();
  }
}

// Import writeGlobalContext for context add-project
import { writeGlobalContext } from './learning.mjs';

main().catch(console.error);
