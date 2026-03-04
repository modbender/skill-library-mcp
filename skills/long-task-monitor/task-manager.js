#!/usr/bin/env node
/**
 * Long Task Manager
 * 
 * 管理 long-task 文件夹下的任务
 * 
 * Usage:
 *   node task-manager.js create <description> [workerTask]
 *   node task-manager.js get <taskId>
 *   node task-manager.js update <taskId> <field> <value>
 *   node task-manager.js list
 *   node task-manager.js add-round <taskId> <roundData>
 *   node task-manager.js complete <taskId> <result>
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const HOME = os.homedir();
const TASKS_DIR = path.join(HOME, '.openclaw', 'workspace', 'long-tasks');

// Ensure directory exists
function ensureDir(dir = TASKS_DIR) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// Generate task ID
function generateTaskId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).slice(2, 6);
  return `task-${timestamp}-${random}`;
}

// Create a new task
function createTask(description, workerTask) {
  ensureDir();
  const taskId = generateTaskId();
  const taskDir = path.join(TASKS_DIR, taskId);
  fs.mkdirSync(taskDir, { recursive: true });
  fs.mkdirSync(path.join(taskDir, 'monitor-rounds'), { recursive: true });
  
  const task = {
    taskId,
    description,
    workerTask: workerTask || description,
    createdAt: new Date().toISOString(),
    status: 'created',
    monitorRound: 0,
    workerRestartCount: 0
  };
  
  fs.writeFileSync(
    path.join(taskDir, 'task.json'),
    JSON.stringify(task, null, 2)
  );
  
  console.log(`✅ Task created: ${taskId}`);
  return task;
}

// Get task by ID
function getTask(taskId) {
  const taskPath = path.join(TASKS_DIR, taskId, 'task.json');
  if (!fs.existsSync(taskPath)) {
    console.log(`❌ Task not found: ${taskId}`);
    return null;
  }
  return JSON.parse(fs.readFileSync(taskPath, 'utf-8'));
}

// Update task field
function updateTask(taskId, updates) {
  const task = getTask(taskId);
  if (!task) return null;
  
  const updated = { ...task, ...updates };
  const taskPath = path.join(TASKS_DIR, taskId, 'task.json');
  fs.writeFileSync(taskPath, JSON.stringify(updated, null, 2));
  
  console.log(`✅ Task updated: ${taskId}`);
  return updated;
}

// List all tasks
function listTasks() {
  ensureDir();
  const dirs = fs.readdirSync(TASKS_DIR).filter(f => {
    const dirPath = path.join(TASKS_DIR, f);
    // Only include directories that have a task.json file
    return fs.statSync(dirPath).isDirectory() && 
           fs.existsSync(path.join(dirPath, 'task.json'));
  });
  
  if (dirs.length === 0) {
    console.log('📭 No tasks found');
    return [];
  }
  
  const tasks = [];
  for (const dir of dirs) {
    const task = getTask(dir);
    if (task) tasks.push(task);
  }
  
  console.log(`📋 ${tasks.length} task(s):\n`);
  for (const task of tasks) {
    console.log(`  [${task.taskId}]`);
    console.log(`    描述: ${task.description}`);
    console.log(`    状态: ${task.status}`);
    console.log(`    轮次: ${task.monitorRound}`);
    console.log(`    重启: ${task.workerRestartCount}`);
    console.log();
  }
  return tasks;
}

// Add monitor round
function addMonitorRound(taskId, roundData) {
  const task = getTask(taskId);
  if (!task) return null;
  
  const roundNum = task.monitorRound + 1;
  const roundPath = path.join(TASKS_DIR, taskId, 'monitor-rounds', `round-${roundNum}.json`);
  
  const round = {
    round: roundNum,
    ...roundData,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync(roundPath, JSON.stringify(round, null, 2));
  
  // Update task monitorRound
  updateTask(taskId, { monitorRound: roundNum });
  
  console.log(`✅ Round ${roundNum} added to task ${taskId}`);
  return round;
}

// Complete task
function completeTask(taskId, result) {
  const task = getTask(taskId);
  if (!task) return null;
  
  const endedAt = new Date().toISOString();
  const startedAt = task.createdAt;
  const durationMs = new Date(endedAt) - new Date(startedAt);
  const durationMinutes = Math.round(durationMs / 60000);
  
  const status = {
    taskId,
    status: 'completed',
    startedAt,
    endedAt,
    durationMinutes,
    totalMonitorRounds: task.monitorRound,
    workerRestartCount: task.workerRestartCount,
    result
  };
  
  const statusPath = path.join(TASKS_DIR, taskId, 'status.json');
  fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
  
  // Update task status
  updateTask(taskId, { status: 'completed', endedAt });
  
  console.log(`✅ Task ${taskId} completed in ${durationMinutes} minutes`);
  return status;
}

// Get task folder path
function getTaskFolderPath(taskId) {
  return path.join(TASKS_DIR, taskId);
}

// Parse command
const cmd = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];
const arg3 = process.argv[5];

switch (cmd) {
  case 'create':
    if (!arg1) {
      console.error('Usage: node task-manager.js create <description> [workerTask]');
      process.exit(1);
    }
    createTask(arg1, arg2);
    break;
    
  case 'get':
    if (!arg1) {
      console.error('Usage: node task-manager.js get <taskId>');
      process.exit(1);
    }
    const task = getTask(arg1);
    if (task) console.log(JSON.stringify(task, null, 2));
    break;
    
  case 'update':
    if (!arg1 || !arg2) {
      console.error('Usage: node task-manager.js update <taskId> <field> <value>');
      process.exit(1);
    }
    updateTask(arg1, { [arg2]: arg3 });
    break;
    
  case 'list':
    listTasks();
    break;
    
  case 'add-round':
    if (!arg1 || !arg2) {
      console.error('Usage: node task-manager.js add-round <taskId> <roundJson>');
      process.exit(1);
    }
    try {
      const roundData = JSON.parse(arg2);
      addMonitorRound(arg1, roundData);
    } catch (e) {
      console.error('Invalid JSON:', e.message);
    }
    break;
    
  case 'complete':
    if (!arg1 || !arg2) {
      console.error('Usage: node task-manager.js complete <taskId> <result>');
      process.exit(1);
    }
    completeTask(arg1, arg2);
    break;
    
  case 'folder':
    if (!arg1) {
      console.error('Usage: node task-manager.js folder <taskId>');
      process.exit(1);
    }
    console.log(getTaskFolderPath(arg1));
    break;
    
  default:
    console.log('Usage:');
    console.log('  node task-manager.js create <description> [workerTask]');
    console.log('  node task-manager.js get <taskId>');
    console.log('  node task-manager.js update <taskId> <field> <value>');
    console.log('  node task-manager.js list');
    console.log('  node task-manager.js add-round <taskId> <roundJson>');
    console.log('  node task-manager.js complete <taskId> <result>');
    console.log('  node task-manager.js folder <taskId>');
}
