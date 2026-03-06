import { defineConfig } from 'drizzle-kit';
import path from 'path';

/**
 * Drizzle Kit 配置文件
 * 
 * 用于:
 * - 生成数据库迁移 (npx drizzle-kit generate)
 * - 执行迁移 (npx drizzle-kit migrate)
 * - 查看数据库结构 (npx drizzle-kit studio)
 */

// 数据库文件路径 - 存储在工作区标准位置
const DB_PATH = process.env.CONTENT_OPS_DB || 
  path.join(process.env.HOME || '/home/admin', '.openclaw/workspace/content-ops-workspace/data/content-ops.db');

export default defineConfig({
  dialect: 'sqlite',
  schema: './src/db/schema.ts',
  out: './src/db/migrations',
  dbCredentials: {
    url: DB_PATH,
  },
  // 迁移表名
  migrationsTable: '__drizzle_migrations',
  // 启用严格模式
  strict: true,
  // 详细日志
  verbose: true,
});
