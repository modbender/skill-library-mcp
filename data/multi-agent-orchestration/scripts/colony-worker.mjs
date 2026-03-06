#!/usr/bin/env node
/**
 * Colony Worker - Background agent execution handler
 * 
 * Spawned by colony.mjs to run agents without blocking the CLI.
 * Reads task metadata from a JSON file, runs the agent, and updates results.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync } from 'fs';
import { execSync } from 'child_process';
import { dirname, join } from 'path';

const metaFile = process.argv[2];

if (!metaFile || !existsSync(metaFile)) {
  console.error('Usage: colony-worker.mjs <meta-file.json>');
  process.exit(1);
}

const meta = JSON.parse(readFileSync(metaFile, 'utf-8'));
const {
  taskId,
  agentName,
  agentRole,
  sessionId,
  promptFile,
  tasksFile,
  contextDir,
  startTime,
  outputs,
  runId,
  stageId,
  taskDescription,
  createdAt
} = meta;

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function cleanup() {
  try { unlinkSync(promptFile); } catch {}
  try { unlinkSync(metaFile); } catch {}
}

try {
  // Read prompt and execute agent
  const promptContent = readFileSync(promptFile, 'utf-8');
  const promptB64 = Buffer.from(promptContent).toString('base64');
  
  // Use base64 + subshell to avoid escaping issues
  const cmd = `echo "${promptB64}" | base64 -d | openclaw agent --session-id "${sessionId}" --message "$(cat)" --json --timeout 1800`;
  
  const result = execSync(cmd, {
    encoding: 'utf-8',
    timeout: 1800000, // 30 minutes
    maxBuffer: 10 * 1024 * 1024,
    shell: '/bin/bash'
  });
  
  const durationMs = Date.now() - startTime;
  
  let response;
  try {
    response = JSON.parse(result);
  } catch {
    response = { content: result };
  }
  
  const output = response.content || response.message || result;
  
  // Write context file
  ensureDir(contextDir);
  const contextFile = join(contextDir, `${taskId}.md`);
  writeFileSync(contextFile, `# Task: ${taskDescription}\n\nAgent: ${agentName}\nCompleted: ${new Date().toISOString()}\nDuration: ${durationMs}ms\n\n---\n\n${output}`);
  
  // Write output files for process stages
  for (const outputFile of outputs) {
    if (!outputFile.endsWith('/')) {
      writeFileSync(join(contextDir, outputFile), output);
    }
  }
  
  // Update tasks.json
  const tasks = JSON.parse(readFileSync(tasksFile, 'utf-8'));
  delete tasks.active[agentName];
  
  const taskRecord = {
    id: taskId,
    type: agentRole,
    description: taskDescription,
    agent: agentName,
    status: 'completed',
    createdAt: createdAt,
    startedAt: createdAt,
    completedAt: new Date().toISOString(),
    durationMs: durationMs,
    result: output.substring(0, 500) + (output.length > 500 ? '...' : ''),
    runId: runId,
    stageId: stageId
  };
  
  tasks.completed.push(taskRecord);
  if (tasks.completed.length > 100) {
    tasks.completed = tasks.completed.slice(-100);
  }
  
  writeFileSync(tasksFile, JSON.stringify(tasks, null, 2));
  
  cleanup();
  console.log(`✓ Task ${taskId} completed (${durationMs}ms)`);
  
} catch (e) {
  const durationMs = Date.now() - startTime;
  
  // Update tasks.json with failure
  try {
    const tasks = JSON.parse(readFileSync(tasksFile, 'utf-8'));
    delete tasks.active[agentName];
    
    const taskRecord = {
      id: taskId,
      type: agentRole,
      description: taskDescription,
      agent: agentName,
      status: 'failed',
      createdAt: createdAt,
      startedAt: createdAt,
      completedAt: new Date().toISOString(),
      durationMs: durationMs,
      result: `Agent error: ${e.message}`,
      runId: runId,
      stageId: stageId
    };
    
    tasks.failed.push(taskRecord);
    writeFileSync(tasksFile, JSON.stringify(tasks, null, 2));
  } catch (writeErr) {
    console.error(`Failed to update tasks.json: ${writeErr.message}`);
  }
  
  cleanup();
  console.error(`✗ Task ${taskId} failed: ${e.message}`);
  process.exit(1);
}
