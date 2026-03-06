import { db, mutations } from '../src/db/index.js';
import { randomUUID } from 'crypto';
import fs from 'fs';
import os from 'os';

// 读取 cookie 文件
const cookiePath = os.homedir() + '/.openclaw/workspace/bin/cookies.json';
const cookieData = JSON.parse(fs.readFileSync(cookiePath, 'utf8'));

const result = await mutations.createSourceAccount({
  id: randomUUID(),
  accountType: 'source',
  platform: 'xiaohongshu',
  accountName: '小红书主号',
  loginStatus: 'active',
  sessionData: cookieData,
  dailyQuota: 50,
  quotaUsedToday: 0,
  crawlConfig: {
    search_limit: 50,
    request_interval: [3, 5],
    retry_times: 3
  }
});

const sourceAccount = result[0];
console.log('✅ 小红书账号已添加:');
console.log(`  ID: ${sourceAccount.id}`);
console.log(`  平台: ${sourceAccount.platform}`);
console.log(`  账号: ${sourceAccount.accountName}`);
console.log(`  状态: ${sourceAccount.loginStatus}`);
console.log(`  每日限额: ${sourceAccount.dailyQuota}`);
