#!/usr/bin/env node
/**
 * Long Task Monitor - Main Script
 * 
 * 启动长任务监控流程
 * 
 * Security: Uses execFile with argument arrays to prevent command injection
 * 
 * Usage:
 *   node long-task.js start <task_description> <worker_task>
 *   node long-task.js status [task_id]
 *   node long-task.js stop [task_id>
 *   node long-task.js complete <task_id> <result>
 * 
 * Examples:
 *   node long-task.js start "训练图像分类模型" "python train.py --epochs 100"
 *   node long-task.js status
 *   node long-task.js stop
 *   node long-task.js complete <task_id> "任务完成"
 */

import { execFile } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const HOME = os.homedir();
const SKILL_DIR = path.join(HOME, '.openclaw', 'workspace', 'skills', 'long-task-monitor');
const TASK_MANAGER = path.join(SKILL_DIR, 'task-manager.js');
const MONITOR_PROMPT = path.join(SKILL_DIR, 'monitor-prompt.txt');
const TASKS_DIR = path.join(HOME, '.openclaw', 'workspace', 'long-tasks');

// Helper: validate input - only allow safe characters
// Note: Allow ':' for session keys like 'agent:main:subagent:xxx'
function sanitizeInput(input, maxLen = 200) {
  if (!input) return '';
  // Allow alphanumeric, Chinese, basic punctuation, spaces, hyphens, colons (for session keys)
  return input.replace(/[^\w\u4e00-\u9fa5\s\-_.,，！？、:]/g, '').slice(0, maxLen);
}

// Helper to run command safely with argument arrays
function run(cmd, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    execFile(cmd, args, { encoding: 'utf-8', ...options }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(stderr || error.message));
      } else {
        resolve(stdout);
      }
    });
  });
}

// Read monitor prompt template
function getMonitorPrompt(taskId, workerSessionKey, taskDescription, workerTask, round, taskFolder) {
  let prompt = fs.readFileSync(MONITOR_PROMPT, 'utf-8');
  
  prompt = prompt.replace(/{task_id}/g, sanitizeInput(taskId))
    .replace(/{worker_session_key}/g, sanitizeInput(workerSessionKey, 500))
    .replace(/{task_description}/g, sanitizeInput(taskDescription, 500))
    .replace(/{worker_task}/g, sanitizeInput(workerTask, 1000))
    .replace(/{round}/g, round.toString())
    .replace(/{task_folder}/g, taskFolder);
  
  return prompt;
}

// Get task info
function getTask(taskId) {
  const safeTaskId = sanitizeInput(taskId);
  const taskPath = path.join(TASKS_DIR, safeTaskId, 'task.json');
  if (!fs.existsSync(taskPath)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(taskPath, 'utf-8'));
}

// Update task session keys safely
async function updateSessionKeys(taskId, workerSessionKey, monitorSessionKey) {
  const safeTaskId = sanitizeInput(taskId);
  if (workerSessionKey) {
    const safeKey = sanitizeInput(workerSessionKey, 500);
    await run('node', [TASK_MANAGER, 'update', safeTaskId, 'workerSessionKey', safeKey]);
  }
  if (monitorSessionKey) {
    const safeKey = sanitizeInput(monitorSessionKey, 500);
    await run('node', [TASK_MANAGER, 'update', safeTaskId, 'monitorSessionKey', safeKey]);
  }
}

// Generate Worker spawn command
function generateWorkerSpawnCommand(taskId, workerTask) {
  const safeTaskId = sanitizeInput(taskId);
  const safeWorkerTask = sanitizeInput(workerTask, 1000);
  const workerLabel = `worker-${safeTaskId}`;
  
  const workerPrompt = `你是 Worker Agent，负责执行以下任务：

${safeWorkerTask}

## 重要规则
1. 正常执行任务，不需要汇报进度
2. 如果任务需要多轮交互，继续执行直到完成
3. 任务完成后返回最终结果`;

  const escapedPrompt = workerPrompt.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  return {
    command: `sessions_spawn(task="${escapedPrompt}", label="${workerLabel}", cleanup="keep")`,
    label: workerLabel
  };
}

// Generate Monitor spawn command
function generateMonitorSpawnCommand(taskId, workerSessionKey, taskDescription, workerTask, round) {
  const safeTaskId = sanitizeInput(taskId);
  const safeWorkerKey = sanitizeInput(workerSessionKey, 500);
  const safeDesc = sanitizeInput(taskDescription, 500);
  const safeTask = sanitizeInput(workerTask, 1000);
  const taskFolder = path.join(TASKS_DIR, safeTaskId);
  const monitorLabel = `monitor-${safeTaskId}`;
  
  const prompt = getMonitorPrompt(safeTaskId, safeWorkerKey, safeDesc, safeTask, round, taskFolder);
  const escapedPrompt = prompt.replace(/"/g, '\\"').replace(/\n/g, '\\n');
  
  return {
    command: `sessions_spawn(task="${escapedPrompt}", label="${monitorLabel}", cleanup="delete")`,
    label: monitorLabel
  };
}

// Complete task and cleanup sessions
async function completeTask(taskId, result) {
  const safeTaskId = sanitizeInput(taskId);
  const safeResult = sanitizeInput(result, 500);
  
  console.log(`✅ Completing task: ${safeTaskId}`);
  
  const task = getTask(safeTaskId);
  if (!task) {
    console.log('❌ Task not found');
    return;
  }
  
  // Update task status
  const endedAt = new Date().toISOString();
  const startedAt = task.createdAt;
  const durationMs = new Date(endedAt) - new Date(startedAt);
  const durationMinutes = Math.round(durationMs / 60000);
  
  const status = {
    taskId: safeTaskId,
    status: 'completed',
    startedAt,
    endedAt,
    durationMinutes,
    totalMonitorRounds: task.monitorRound,
    workerRestartCount: task.workerRestartCount,
    result: safeResult
  };
  
  const statusPath = path.join(TASKS_DIR, safeTaskId, 'status.json');
  fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
  
  // Update task status
  const taskPath = path.join(TASKS_DIR, safeTaskId, 'task.json');
  const updatedTask = { ...task, status: 'completed', endedAt };
  fs.writeFileSync(taskPath, JSON.stringify(updatedTask, null, 2));
  
  console.log(`✅ Task completed in ${durationMinutes} minutes`);
  console.log(`   Result: ${safeResult}`);
  
  // Cleanup sessions if they exist
  if (task.workerSessionKey) {
    const safeWorkerKey = sanitizeInput(task.workerSessionKey, 500);
    console.log(`\n🧹 Cleanup sessions:`);
    console.log(`   Worker: ${safeWorkerKey}`);
    
    try {
      await run('openclaw', ['sessions', 'kill', safeWorkerKey]);
      console.log(`   ✅ Worker session killed`);
    } catch (e) {
      console.log(`   ⚠️ Failed to kill Worker: ${e.message}`);
    }
  }
  
  if (task.monitorSessionKey) {
    const safeMonitorKey = sanitizeInput(task.monitorSessionKey, 500);
    console.log(`   Monitor: ${safeMonitorKey}`);
    
    try {
      await run('openclaw', ['sessions', 'kill', safeMonitorKey]);
      console.log(`   ✅ Monitor session killed`);
    } catch (e) {
      console.log(`   ⚠️ Failed to kill Monitor: ${e.message}`);
    }
  }
}

// Show task status
async function showStatus() {
  console.log('📋 Current Tasks:\n');
  await run('node', [TASK_MANAGER, 'list']);
}

// Show usage
function showUsage() {
  console.log(`
Long Task Monitor - 启动和管理长任务

Usage:
  node long-task.js start <description> <worker_task>
    启动新的长任务
  
  node long-task.js status
    查看当前任务状态
  
  node long-task.js update <task_id> worker <sessionKey>
    更新 Worker Session Key
  
  node long-task.js update <task_id> monitor <sessionKey>
    更新 Monitor Session Key
  
  node long-task.js complete <task_id> <result>
    标记任务完成并清理 sessions
  
  node long-task.js worker-command <task_id> <worker_task>
    生成 Worker 启动命令
  
  node long-task.js monitor-command <task_id> <worker_session_key> [round]
    生成 Monitor 启动命令
  
  node long-task.js folder <task_id>
    获取任务文件夹路径

Examples:
  node long-task.js start "训练图像分类模型" "python train.py --epochs 100"
  node long-task.js status
  node long-task.js update task-xxx worker agent:main:subagent:yyy
  node long-task.js complete task-xxx "任务成功完成"
`);
}

// Parse command
const cmd = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];
const arg3 = process.argv[5];

switch (cmd) {
  case 'start':
    if (!arg1) {
      showUsage();
      process.exit(1);
    }
    const safeDesc = sanitizeInput(arg1, 200);
    const safeWorkerTask = sanitizeInput(arg2 || arg1, 1000);
    console.log(`🚀 Starting Long Task: ${safeDesc}`);
    console.log(`   Worker Task: ${safeWorkerTask}\n`);
    
    // Create task
    await run('node', [TASK_MANAGER, 'create', safeDesc, safeWorkerTask]);
    
    // Get latest task
    const tasks = await run('node', [TASK_MANAGER, 'list']);
    const match = tasks.match(/\[(task-[^\]]+)\]/);
    if (!match) {
      console.log('❌ Failed to create task');
      process.exit(1);
    }
    const taskId = match[1];
    const taskFolder = path.join(TASKS_DIR, taskId);
    
    console.log(`\n📁 Task Folder: ${taskFolder}`);
    console.log(`\n⚙️  Step 1: Generate Worker spawn command:`);
    const workerCmd = generateWorkerSpawnCommand(taskId, safeWorkerTask);
    console.log(workerCmd.command);
    console.log(`\n📝 ⚠️ 获取 Worker Session Key 后，运行以下命令保存:`);
    console.log(`   node "${TASK_MANAGER}" update ${taskId} workerSessionKey "<Worker Session Key>"`);
    console.log(`\n📝 然后告诉我 Worker Session Key，我会帮你启动 Monitor。`);
    break;
    
  case 'worker-command':
    if (!arg1 || !arg2) {
      console.error('Usage: node long-task.js worker-command <task_id> <worker_task>');
      process.exit(1);
    }
    console.log(generateWorkerSpawnCommand(arg1, arg2).command);
    break;
    
  case 'monitor-command':
    if (!arg1 || !arg2) {
      console.error('Usage: node long-task.js monitor-command <task_id> <worker_session_key> [round]');
      process.exit(1);
    }
    const taskInfo = getTask(arg1);
    if (!taskInfo) {
      console.error(`Task not found: ${arg1}`);
      process.exit(1);
    }
    const round = parseInt(process.argv[5]) || 1;
    console.log(generateMonitorSpawnCommand(
      arg1,
      arg2,
      taskInfo.description,
      taskInfo.workerTask,
      round
    ).command);
    break;
    
  case 'status':
    showStatus();
    break;
    
  case 'complete':
    if (!arg1 || !arg2) {
      console.error('Usage: node long-task.js complete <task_id> <result>');
      process.exit(1);
    }
    completeTask(arg1, arg2).catch(console.error);
    break;
    
  case 'folder':
    if (!arg1) {
      console.error('Usage: node long-task.js folder <task_id>');
      process.exit(1);
    }
    console.log(path.join(TASKS_DIR, sanitizeInput(arg1)));
    break;
    
  case 'update':
    const updateTaskId = sanitizeInput(arg1);
    const updateType = arg2;
    const updateSessionKey = sanitizeInput(arg3, 500);
    if (!updateTaskId || !updateType || !updateSessionKey) {
      console.error('Usage: node long-task.js update <task_id> worker|monitor <sessionKey>');
      process.exit(1);
    }
    const updateField = updateType === 'worker' ? 'workerSessionKey' : updateType === 'monitor' ? 'monitorSessionKey' : null;
    if (!updateField) {
      console.error('Usage: node long-task.js update <task_id> worker|monitor <sessionKey>');
      process.exit(1);
    }
    run('node', [TASK_MANAGER, 'update', updateTaskId, updateField, updateSessionKey]).then(() => {
      console.log(`✅ Updated ${updateField} for task ${updateTaskId}`);
    }).catch(console.error);
    break;
    
  default:
    showUsage();
}
