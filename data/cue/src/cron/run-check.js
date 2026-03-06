#!/usr/bin/env node
/**
 * 监控检查运行脚本
 * 由 cron 调用执行单次检查
 */

import { runMonitorCheck } from './monitor-daemon.js';

const chatId = process.argv[2] || process.env.CHAT_ID || 'default';

runMonitorCheck(chatId)
  .then(() => {
    console.log('Monitor check completed');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Monitor check failed:', error);
    process.exit(1);
  });
