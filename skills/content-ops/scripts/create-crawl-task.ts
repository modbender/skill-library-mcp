import { db, mutations } from '../src/db/index.js';
import { randomUUID } from 'crypto';

// 创建 AI 相关内容抓取任务
const task = await mutations.createCrawlTask({
  id: randomUUID(),
  taskName: 'AI人工智能内容抓取',
  sourceAccountId: '08705bf4-86a2-4a3d-a865-37e206bbc65b', // 小红书账号ID
  status: 'pending',
  queryList: ['AI人工智能', 'AI工具', '人工智能', 'ChatGPT', 'AI应用'],
  targetCount: 20,
  filters: {
    sort_by: '最多点赞',
    publish_time: '一周内'
  }
});

console.log('✅ 抓取任务已创建:');
console.log(`  任务ID: ${task[0].id}`);
console.log(`  名称: ${task[0].taskName}`);
console.log(`  关键词: ${task[0].queryList.join(', ')}`);
console.log(`  状态: ${task[0].status}`);
