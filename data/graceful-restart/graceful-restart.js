#!/usr/bin/env node
/**
 * Gateway Restart with Self-Wakeup
 * 
 * Usage:
 *   node graceful-restart.js [--task "任务描述"] [--delay seconds]
 * 
 * Examples:
 *   node graceful-restart.js
 *   node graceful-restart.js --task "继续安装 Python 包"
 *   node graceful-restart.js --task "继续安装 Python包" --delay 60
 * 
 * Security: Uses execFile with argument arrays to prevent command injection
 */

import { execFileSync } from 'node:child_process';
import os from 'node:os';

const HOME = os.homedir();

// Parse arguments
const args = process.argv.slice(2);
let taskDescription = null;
let delaySeconds = 10;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--task' && args[i + 1]) {
    taskDescription = args[i + 1];
    i++;
  } else if (args[i] === '--delay' && args[i + 1]) {
    delaySeconds = parseInt(args[i + 1], 10);
    i++;
  }
}

// If no task specified, use default
if (!taskDescription) {
  taskDescription = "继续之前的任务";
}

// Validate task description - only allow safe characters
const safeTaskDesc = taskDescription.replace(/[^\w\u4e00-\u9fa5\s\d\-_,，。！？、]/g, '').slice(0, 200);

console.log('🔄 Gateway Restart with Self-Wakeup');
console.log('================================');
console.log(`📝 Task: ${safeTaskDesc}`);
console.log(`⏱️  Delay: ${delaySeconds} seconds`);
console.log('');

// Step 1: Calculate cron time
console.log('⏰ Setting up cron job...');
const futureTime = new Date(Date.now() + delaySeconds * 1000);
const cronTime = futureTime.toISOString().replace('.000Z', 'Z');

// Step 2: Create cron job with system-event (using execFile to prevent injection)
console.log('🔄 Restarting Gateway...');
try {
  execFileSync('openclaw', [
    'cron', 'add',
    '--at', cronTime,
    '--session', 'main',
    '--system-event', `🔔 Gateway 已重启！有待处理任务：${safeTaskDesc}`,
    '--name', 'auto-wakeup',
    '--delete-after-run'
  ], { encoding: 'utf-8' });
  console.log('   ✅ Cron job created');
} catch (error) {
  console.error('   ❌ Failed to create cron job:', error.message);
  process.exit(1);
}

// Step 3: Restart Gateway (using execFile)
try {
  execFileSync('openclaw', ['gateway', 'restart'], { encoding: 'utf-8', timeout: 30000 });
  console.log('   ✅ Gateway restart initiated');
} catch (error) {
  console.error('   ❌ Failed to restart Gateway:', error.message);
  process.exit(1);
}

console.log('');
console.log('================================');
console.log('✅ All done! Gateway will restart and notify you after wakeup.');
