#!/usr/bin/env node
/**
 * Cross-Agent Memory Sync
 * 跨 Agent 记忆同步工具
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || process.cwd();
const SHARED_REPO = process.env.SHARED_MEMORY_REPO || 'https://github.com/weidadong2359/agent-memory-shared.git';
const AGENT_ID = process.env.AGENT_ID || 'lobster-alpha';

// 初始化共享 repo
function initSharedRepo() {
  const sharedDir = path.join(WORKSPACE, '.shared-memory');
  
  if (!fs.existsSync(sharedDir)) {
    console.log('📥 Cloning shared memory repo...');
    execSync(`git clone ${SHARED_REPO} ${sharedDir}`, { stdio: 'inherit' });
  } else {
    console.log('✅ Shared memory repo exists');
  }
  
  return sharedDir;
}

// 拉取更新
function pullUpdates(sharedDir) {
  console.log('🔄 Pulling updates from shared memory...');
  try {
    execSync('git pull --rebase', { cwd: sharedDir, stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error('❌ Pull failed, may have conflicts');
    return false;
  }
}

// 推送更新
function pushUpdates(sharedDir, message) {
  console.log('📤 Pushing updates to shared memory...');
  try {
    execSync('git add .', { cwd: sharedDir });
    execSync(`git commit -m "${AGENT_ID}: ${message}"`, { cwd: sharedDir });
    execSync('git push', { cwd: sharedDir, stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error('❌ Push failed');
    return false;
  }
}

// 导出本地记忆到共享库
function exportMemory(sharedDir) {
  const localMemory = path.join(WORKSPACE, 'MEMORY.md');
  const sharedMemory = path.join(sharedDir, `${AGENT_ID}-memory.md`);
  
  if (fs.existsSync(localMemory)) {
    const content = fs.readFileSync(localMemory, 'utf-8');
    const exported = {
      agentId: AGENT_ID,
      timestamp: new Date().toISOString(),
      content
    };
    
    fs.writeFileSync(sharedMemory, JSON.stringify(exported, null, 2));
    console.log(`✅ Exported memory to ${sharedMemory}`);
    return true;
  }
  
  return false;
}

// 导入共享记忆
function importMemory(sharedDir) {
  const files = fs.readdirSync(sharedDir).filter(f => f.endsWith('-memory.md'));
  const imported = [];
  
  files.forEach(file => {
    if (file === `${AGENT_ID}-memory.md`) return; // 跳过自己的
    
    const filePath = path.join(sharedDir, file);
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      imported.push({
        agentId: data.agentId,
        timestamp: data.timestamp,
        content: data.content
      });
    } catch (error) {
      console.warn(`⚠️  Failed to parse ${file}`);
    }
  });
  
  console.log(`📥 Imported ${imported.length} agent memories`);
  return imported;
}

// 主函数
const command = process.argv[2] || 'sync';

const sharedDir = initSharedRepo();

switch (command) {
  case 'pull':
    pullUpdates(sharedDir);
    break;
    
  case 'push':
    const message = process.argv[3] || 'Update memory';
    exportMemory(sharedDir);
    pushUpdates(sharedDir, message);
    break;
    
  case 'sync':
    pullUpdates(sharedDir);
    exportMemory(sharedDir);
    pushUpdates(sharedDir, 'Sync memory');
    break;
    
  case 'import':
    pullUpdates(sharedDir);
    const memories = importMemory(sharedDir);
    console.log(JSON.stringify(memories, null, 2));
    break;
    
  default:
    console.log('Usage: sync.mjs [pull|push|sync|import]');
}
