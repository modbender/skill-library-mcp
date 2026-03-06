#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// --- Configuration ---
// ⚠️ PLEASE EDIT THESE IDs BEFORE USE ⚠️
const USERS = {
  'Mark': process.env.TODO_ADMIN_ID || 'REPLACE_WITH_YOUR_ID', 
  'Jane': process.env.TODO_PARTNER_ID || 'REPLACE_WITH_PARTNER_ID',
  'Shared': process.env.TODO_GROUP_ID || 'REPLACE_WITH_GROUP_ID' // Family shared tasks
};

// Default storage location (relative to cwd)
const TODO_FILE = path.join(process.cwd(), 'memory/todo.json');

// --- Helper Functions ---

function loadTodos() {
  if (!fs.existsSync(TODO_FILE)) {
    return { tasks: [] };
  }
  try {
    return JSON.parse(fs.readFileSync(TODO_FILE, 'utf8'));
  } catch (e) {
    console.error("Error reading todo.json:", e);
    return { tasks: [] };
  }
}

function saveTodos(data) {
  // Ensure directory exists
  const dir = path.dirname(TODO_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  fs.writeFileSync(TODO_FILE, JSON.stringify(data, null, 2));
}

function generateId() {
  // Use timestamp + short random suffix to guarantee uniqueness
  // Example: 1707316080123-ab3d
  return Date.now().toString() + '-' + crypto.randomBytes(2).toString('hex');
}

function formatDate(isoString) {
  if (!isoString) return '';
  // Adjust locale/timezone as needed
  const date = new Date(isoString);
  return date.toLocaleString(); 
}

// --- Commands ---

function listTodos(owner, showAll) {
  const data = loadTodos();
  let tasks = data.tasks.filter(t => t.status !== 'done');

  // Filter logic:
  // If owner is specified, show tasks for that owner + 'Family' tasks
  // If showAll is true, ignore owner filter
  if (!showAll && owner) {
    tasks = tasks.filter(t => t.owner === owner || t.owner === 'Family' || USERS[owner] === t.owner);
  }
  
  // Sort by dueDate (asc), then by createdAt (desc)
  tasks.sort((a, b) => {
      if (a.dueDate && b.dueDate) return new Date(a.dueDate) - new Date(b.dueDate);
      if (a.dueDate) return -1;
      if (b.dueDate) return 1;
      return new Date(b.createdAt) - new Date(a.createdAt);
  });

  if (tasks.length === 0) {
    console.log("📭 No pending tasks.");
    return;
  }

  console.log(`📋 **Todo List** (${owner ? owner : 'All'}):\n`);
  tasks.forEach(t => {
    let line = `- [${t.id}] **${t.content}**`;
    if (t.owner === 'Family') line += ` (👨‍👩‍👧‍👦 Family)`;
    else if (t.owner && t.owner !== owner && showAll) line += ` (👤 ${t.owner})`;
    
    if (t.dueDate) line += ` ⏰ ${formatDate(t.dueDate)}`;
    console.log(line);
  });
}

function addTodo(content, owner, dueDate) {
  const data = loadTodos();
  const newTask = {
    id: generateId(),
    content,
    owner: owner || 'Admin', // Default to Admin
    status: 'pending',
    dueDate: dueDate || null,
    createdAt: new Date().toISOString()
  };
  
  data.tasks.push(newTask);
  saveTodos(data);
  
  console.log(`✅ Task Added [${newTask.id}]: "${content}" (${newTask.owner})`);
}

function completeTodo(idOrContent) {
  const data = loadTodos();
  const taskIndex = data.tasks.findIndex(t => t.id === idOrContent || t.content.includes(idOrContent));
  
  if (taskIndex === -1) {
    console.log(`❌ Task not found: "${idOrContent}"`);
    return;
  }
  
  const task = data.tasks[taskIndex];
  if (task.status === 'done') {
      console.log(`ℹ️ Task already completed: "${task.content}"`);
      return;
  }

  task.status = 'done';
  task.completedAt = new Date().toISOString();
  saveTodos(data);
  
  console.log(`🎉 Task Completed: "${task.content}"`);
}

function deleteTodo(id) {
    const data = loadTodos();
    const initialLength = data.tasks.length;
    data.tasks = data.tasks.filter(t => t.id !== id);
    
    if (data.tasks.length === initialLength) {
        console.log(`❌ Task ID ${id} not found.`);
    } else {
        saveTodos(data);
        console.log(`🗑️ Task [${id}] deleted.`);
    }
}


function dailyBrief() {
    console.log("☀️ Good Morning! Here are today's tasks:");
    listTodos(null, true); 
}

function eveningReview() {
    console.log("🌙 Good Evening! Review of pending tasks:");
    listTodos(null, true);
}


// --- CLI Entry Point ---

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'list':
    listTodos(args[1], args[2] === 'true');
    break;
  case 'add':
    addTodo(args[1], args[2], args[3]);
    break;
  case 'done':
    completeTodo(args[1]);
    break;
  case 'delete':
    deleteTodo(args[1]);
    break;
  case 'brief':
    dailyBrief();
    break;
  case 'review':
    eveningReview();
    break;
  default:
    console.log("Usage: node todo.js [list|add|done|delete|brief|review] ...");
}
