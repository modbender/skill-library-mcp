/**
 * 数据库初始化脚本
 * 
 * 运行方式:
 *   npm run db:init
 * 
 * 功能:
 * 1. 创建工作目录
 * 2. 生成并执行迁移
 * 3. 创建必要索引
 */

import { db } from './index.js';
import fs from 'fs';
import path from 'path';

console.log('🚀 Content Ops 数据库初始化\n');

// 创建工作目录结构
const workspaceDir = path.join(process.env.HOME || '/home/admin', '.openclaw/workspace/content-ops-workspace');
const dirs = [
  'data',
  'accounts',
  'strategies',
  'corpus/raw',
  'corpus/curated',
  'corpus/published',
  'schedules',
  'reports',
  'assets/images',
  'assets/videos'
];

console.log('📁 创建目录结构...');
for (const dir of dirs) {
  const fullPath = path.join(workspaceDir, dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`  ✓ ${dir}`);
  }
}

// 验证数据库连接
console.log('\n🔄 验证数据库连接...');
try {
  const result = db.get(sql`SELECT 1 as test`);
  console.log('  ✓ 数据库连接正常');
} catch (error) {
  console.error('  ✗ 数据库连接失败:', error);
  process.exit(1);
}

// 生成迁移提示
console.log('\n💡 下一步操作:');
console.log('  1. 生成迁移: npm run db:generate');
console.log('  2. 执行迁移: npm run db:migrate');
console.log('  3. 查看数据: npm run db:studio');
console.log('\n✅ 初始化完成！');
