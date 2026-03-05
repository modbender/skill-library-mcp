#!/usr/bin/env node

/**
 * Memory Transfer - Transfer memory between OpenClaw agents
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE_BASE = '/home/node/.openclaw';

// Known agent workspaces
const AGENT_WORKSPACES = {
  'main': 'workspace-main',
  'coder': 'workspace-coder',
  'doc-analyst': 'workspace-doc',
  'daily-money': 'workspace-daily-money'
};

function getWorkspacePath(agentId) {
  // Check if it's a known agent
  const workspaceName = AGENT_WORKSPACES[agentId];
  if (workspaceName) {
    return path.join(WORKSPACE_BASE, workspaceName);
  }
  
  // Try to find workspace
  const workspacePath = path.join(WORKSPACE_BASE, `workspace-${agentId}`);
  if (fs.existsSync(workspacePath)) {
    return workspacePath;
  }
  
  // Direct path
  return path.join(WORKSPACE_BASE, agentId);
}

function listMemories(agentId) {
  const workspace = getWorkspacePath(agentId);
  
  console.log(`\n📁 Memories for agent: ${agentId}`);
  console.log(`   Workspace: ${workspace}\n`);
  
  if (!fs.existsSync(workspace)) {
    console.log(`❌ Workspace not found: ${workspace}`);
    return false;
  }
  
  const memories = [];
  
  // Check MEMORY.md
  const mainMemory = path.join(workspace, 'MEMORY.md');
  if (fs.existsSync(mainMemory)) {
    const stats = fs.statSync(mainMemory);
    memories.push({
      name: 'MEMORY.md',
      path: mainMemory,
      size: stats.size,
      type: 'long-term'
    });
  }
  
  // Check memory directory
  const memoryDir = path.join(workspace, 'memory');
  if (fs.existsSync(memoryDir)) {
    const files = fs.readdirSync(memoryDir)
      .filter(f => f.endsWith('.md'));
    
    files.forEach(f => {
      const filePath = path.join(memoryDir, f);
      const stats = fs.statSync(filePath);
      memories.push({
        name: f,
        path: filePath,
        size: stats.size,
        type: 'daily'
      });
    });
  }
  
  if (memories.length === 0) {
    console.log('   No memory files found.');
    return false;
  }
  
  memories.forEach(m => {
    const icon = m.type === 'long-term' ? '📌' : '📄';
    console.log(`   ${icon} ${m.name} (${m.size} bytes)`);
  });
  
  return memories;
}

function transferMemory(sourceId, targetId, specificFile = null, options = {}) {
  const sourceWorkspace = getWorkspacePath(sourceId);
  const targetWorkspace = getWorkspacePath(targetId);
  
  console.log(`\n🔄 Transferring memory: ${sourceId} → ${targetId}`);
  console.log(`   From: ${sourceWorkspace}`);
  console.log(`   To:   ${targetWorkspace}\n`);
  
  // Check source exists
  if (!fs.existsSync(sourceWorkspace)) {
    console.log(`❌ Source workspace not found: ${sourceWorkspace}`);
    return false;
  }
  
  // Check target exists
  if (!fs.existsSync(targetWorkspace)) {
    console.log(`❌ Target workspace not found: ${targetWorkspace}`);
    return false;
  }
  
  // Get source memories
  const sourceMemories = listMemories(sourceId);
  if (!sourceMemories) {
    console.log('❌ No memories to transfer');
    return false;
  }
  
  // Filter if specific file
  let toTransfer = sourceMemories;
  if (specificFile) {
    toTransfer = sourceMemories.filter(m => m.name === specificFile || m.name === specificFile);
    if (toTransfer.length === 0) {
      console.log(`❌ File not found: ${specificFile}`);
      return false;
    }
  }
  
  if (options.dryRun) {
    console.log('\n🔍 Dry run - following files would be transferred:\n');
    toTransfer.forEach(m => {
      console.log(`   ${m.name} (${m.size} bytes)`);
    });
    console.log('\n✅ Dry run complete (no files copied)');
    return true;
  }
  
  // Create target memory directory if needed
  const targetMemoryDir = path.join(targetWorkspace, 'memory');
  if (!fs.existsSync(targetMemoryDir)) {
    fs.mkdirSync(targetMemoryDir, { recursive: true });
  }
  
  // Transfer files
  let transferred = 0;
  toTransfer.forEach(m => {
    let targetPath;
    
    if (m.name === 'MEMORY.md') {
      targetPath = path.join(targetWorkspace, 'MEMORY.md');
    } else {
      targetPath = path.join(targetMemoryDir, m.name);
    }
    
    // Check if target already exists
    if (fs.existsSync(targetPath)) {
      const backupPath = targetPath + '.backup';
      fs.renameSync(targetPath, backupPath);
      console.log(`   ⚠️ Backed up existing: ${m.name} → ${m.name}.backup`);
    }
    
    // Copy file
    fs.copyFileSync(m.path, targetPath);
    console.log(`   ✅ Copied: ${m.name}`);
    transferred++;
  });
  
  console.log(`\n✅ Transferred ${transferred} file(s)`);
  return true;
}

function listAgents() {
  console.log('\n📋 Available agents:\n');
  
  Object.entries(AGENT_WORKSPACES).forEach(([id, workspace]) => {
    const workspacePath = path.join(WORKSPACE_BASE, workspace);
    const exists = fs.existsSync(workspacePath);
    const icon = exists ? '✅' : '❌';
    console.log(`   ${icon} ${id} → ${workspacePath}`);
  });
  
  console.log('');
  return AGENT_WORKSPACES;
}

// Main
const args = process.argv.slice(2);
const command = args[0];

console.log('📦 Memory Transfer Tool');
console.log('======================\n');

switch (command) {
  case 'list':
    if (args[1]) {
      listMemories(args[1]);
    } else {
      console.log('Usage: memory-transfer list <agent-id>');
    }
    break;
    
  case 'agents':
    listAgents();
    break;
    
  case 'transfer':
    const dryRun = args.includes('--dry-run');
    const mainArgs = args.slice(1).filter(a => a !== '--dry-run');
    const source = mainArgs[0];
    const target = mainArgs[1];
    const file = mainArgs[2];
    
    if (!source || !target) {
      console.log('Usage: memory-transfer transfer <source> <target> [file] [--dry-run]');
      console.log('\nExamples:');
      console.log('  memory-transfer transfer main coder');
      console.log('  memory-transfer transfer main coder 2026-03-01.md');
      console.log('  memory-transfer transfer main coder --dry-run');
    } else {
      transferMemory(source, target, file, { dryRun });
    }
    break;
    
  case 'help':
  default:
    console.log(`
📦 Memory Transfer - Transfer memory between OpenClaw agents

Usage:
  memory-transfer agents              List all available agents
  memory-transfer list <agent>      List memories for an agent
  memory-transfer transfer <src> <dst> [file]  Transfer memory
  memory-transfer transfer <src> <dst> --dry-run  Preview transfer

Examples:
  memory-transfer agents
  memory-transfer list main
  memory-transfer transfer main coder
  memory-transfer transfer main coder MEMORY.md
  memory-transfer transfer main coder --dry-run
`);
}
