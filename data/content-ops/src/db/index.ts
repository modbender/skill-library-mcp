/**
 * 数据库连接和查询工具
 * 
 * 使用示例:
 * ```typescript
 * import { db, queries } from './db';
 * 
 * // 查询所有活跃的被运营账号
 * const accounts = await queries.getActiveTargetAccounts();
 * 
 * // 创建新账号
 * const newAccount = await queries.createTargetAccount({
 *   platform: 'reddit',
 *   accountName: 'MyBrandUS',
 *   // ...
 * });
 * ```
 */

import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import { eq, and, desc, asc, sql, inArray } from 'drizzle-orm';
import path from 'path';
import fs from 'fs';
import { 
  targetAccounts, 
  sourceAccounts, 
  crawlTasks, 
  crawlResults,
  publishTasks,
  publishMetricsDaily,
  targetAccountsMetricsDaily
} from './schema';

// ============================================================================
// 数据库连接
// ============================================================================

const DB_DIR = path.join(process.env.HOME || '/home/admin', '.openclaw/workspace/content-ops-workspace/data');
const DB_PATH = process.env.CONTENT_OPS_DB || path.join(DB_DIR, 'content-ops.db');

// 确保目录存在
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true });
}

// 创建数据库连接
const sqlite = new Database(DB_PATH);
export const db = drizzle(sqlite);

// ============================================================================
// 查询工具函数
// ============================================================================

export const queries = {
  // -------------------------------------------------------------------------
  // 被运营账号查询
  // -------------------------------------------------------------------------
  
  /**
   * 获取所有活跃的被运营账号
   * 用途: 每日任务规划时获取需要运营的账号列表
   */
  getActiveTargetAccounts: async () => {
    return await db.query.targetAccounts.findMany({
      where: eq(targetAccounts.status, 'active'),
      orderBy: [asc(targetAccounts.platform), asc(targetAccounts.accountName)]
    });
  },

  /**
   * 按平台获取账号
   * @param platform - 平台名称: reddit, pinterest, discord
   */
  getTargetAccountsByPlatform: async (platform: string) => {
    return await db.query.targetAccounts.findMany({
      where: and(
        eq(targetAccounts.platform, platform),
        eq(targetAccounts.status, 'active')
      )
    });
  },

  /**
   * 获取账号详情（含关联数据）
   * @param accountId - 账号UUID
   */
  getTargetAccountWithMetrics: async (accountId: string) => {
    return await db.query.targetAccounts.findFirst({
      where: eq(targetAccounts.id, accountId),
      with: {
        // 关联最新7天的数据
        metrics: {
          orderBy: [desc(targetAccountsMetricsDaily.metricDate)],
          limit: 7
        }
      }
    });
  },

  // -------------------------------------------------------------------------
  // 信息源账号查询
  // -------------------------------------------------------------------------

  /**
   * 获取所有可用的抓取账号
   * 用途: 创建抓取任务时选择可用的信息源
   */
  getAvailableSourceAccounts: async () => {
    return await db.query.sourceAccounts.findMany({
      where: eq(sourceAccounts.loginStatus, 'active'),
      orderBy: [asc(sourceAccounts.platform), asc(sourceAccounts.accountName)]
    });
  },

  /**
   * 获取今日还有配额的账号
   * 用途: 自动分配抓取任务时选择有配额的账号
   */
  getSourceAccountsWithQuota: async () => {
    return await db.query.sourceAccounts.findMany({
      where: and(
        eq(sourceAccounts.loginStatus, 'active'),
        sql`${sourceAccounts.quotaUsedToday} < ${sourceAccounts.dailyQuota}`
      )
    });
  },

  // -------------------------------------------------------------------------
  // 抓取任务查询
  // -------------------------------------------------------------------------

  /**
   * 获取待执行的任务
   * 用途: 定时任务扫描并执行 pending 状态的抓取
   */
  getPendingCrawlTasks: async () => {
    return await db.query.crawlTasks.findMany({
      where: and(
        eq(crawlTasks.status, 'pending'),
        sql`${crawlTasks.scheduledAt} IS NULL OR ${crawlTasks.scheduledAt} <= CURRENT_TIMESTAMP`
      ),
      orderBy: [asc(crawlTasks.scheduledAt)]
    });
  },

  /**
   * 获取任务执行统计
   * @param taskId - 任务UUID
   */
  getCrawlTaskStats: async (taskId: string) => {
    const task = await db.query.crawlTasks.findFirst({
      where: eq(crawlTasks.id, taskId)
    });
    
    const resultStats = await db.select({
      total: sql<number>`COUNT(*)`,
      approved: sql<number>`SUM(CASE WHEN ${crawlResults.curationStatus} = 'approved' THEN 1 ELSE 0 END)`,
      rejected: sql<number>`SUM(CASE WHEN ${crawlResults.curationStatus} = 'rejected' THEN 1 ELSE 0 END)`,
      avgQuality: sql<number>`AVG(${crawlResults.qualityScore})`
    }).from(crawlResults).where(eq(crawlResults.taskId, taskId));

    return { task, stats: resultStats[0] };
  },

  // -------------------------------------------------------------------------
  // 抓取结果查询
  // -------------------------------------------------------------------------

  /**
   * 获取待审核的抓取结果
   * 用途: 人工审核页面展示待审核内容
   * @param limit - 返回数量限制
   */
  getPendingCrawlResults: async (limit: number = 20) => {
    return await db.query.crawlResults.findMany({
      where: eq(crawlResults.curationStatus, 'raw'),
      orderBy: [desc(crawlResults.engagement)], // 按互动数据排序，优先展示热门内容
      limit
    });
  },

  /**
   * 获取可用的语料（已审核通过）
   * 用途: 生成内容时选择可用的语料
   * @param topic - 可选的主题筛选
   * @param minQuality - 最低质量分
   */
  getAvailableCorpus: async (topic?: string, minQuality: number = 7) => {
    let whereClause = and(
      eq(crawlResults.curationStatus, 'approved'),
      eq(crawlResults.isAvailable, true),
      sql`${crawlResults.qualityScore} >= ${minQuality}`
    );

    if (topic) {
      whereClause = and(
        whereClause,
        sql`${crawlResults.title} LIKE ${`%${topic}%`} OR ${crawlResults.tags} LIKE ${`%${topic}%`}`
      );
    }

    return await db.query.crawlResults.findMany({
      where: whereClause,
      orderBy: [desc(crawlResults.qualityScore), desc(crawlResults.engagement)]
    });
  },

  /**
   * 搜索语料
   * @param keywords - 关键词列表
   */
  searchCorpus: async (keywords: string[]) => {
    const conditions = keywords.map(kw => 
      sql`${crawlResults.title} LIKE ${`%${kw}%`} OR ${crawlResults.content} LIKE ${`%${kw}%`}`
    );

    return await db.query.crawlResults.findMany({
      where: and(
        eq(crawlResults.curationStatus, 'approved'),
        eq(crawlResults.isAvailable, true),
        sql`(${sql.join(conditions, sql` OR `)})`
      ),
      orderBy: [desc(crawlResults.qualityScore)]
    });
  },

  // -------------------------------------------------------------------------
  // 发布任务查询
  // -------------------------------------------------------------------------

  /**
   * 获取今日待发布任务
   * 用途: 定时任务检查今日需要发布的内容
   */
  getTodayScheduledTasks: async () => {
    const today = new Date().toISOString().split('T')[0];
    
    return await db.query.publishTasks.findMany({
      where: and(
        eq(publishTasks.status, 'scheduled'),
        sql`DATE(${publishTasks.scheduledAt}) = ${today}`
      ),
      orderBy: [asc(publishTasks.scheduledAt)]
    });
  },

  /**
   * 获取待审核的发布任务
   * 用途: 内容审核页面展示待审核的发布任务
   */
  getPendingReviewTasks: async () => {
    return await db.query.publishTasks.findMany({
      where: eq(publishTasks.status, 'pending_review'),
      orderBy: [desc(publishTasks.createdAt)]
    });
  },

  /**
   * 获取账号的发布历史
   * @param accountId - 被运营账号ID
   * @param limit - 返回数量
   */
  getAccountPublishHistory: async (accountId: string, limit: number = 10) => {
    return await db.query.publishTasks.findMany({
      where: and(
        eq(publishTasks.targetAccountId, accountId),
        eq(publishTasks.status, 'published')
      ),
      orderBy: [desc(publishTasks.publishedAt)],
      limit
    });
  },

  // -------------------------------------------------------------------------
  // 数据指标查询（用于看板）
  // -------------------------------------------------------------------------

  /**
   * 获取账号近期数据趋势
   * @param accountId - 账号UUID
   * @param days - 查询天数
   * 用途: 绘制粉丝增长曲线、互动趋势图
   */
  getAccountTrend: async (accountId: string, days: number = 7) => {
    return await db.query.targetAccountsMetricsDaily.findMany({
      where: eq(targetAccountsMetricsDaily.targetAccountId, accountId),
      orderBy: [asc(targetAccountsMetricsDaily.metricDate)],
      limit: days
    });
  },

  /**
   * 获取内容表现排行
   * @param accountId - 账号UUID
   * @param days - 查询最近N天的内容
   * @param limit - 返回条数
   * 用途: 找出表现最好的内容，优化后续策略
   */
  getTopPerformingContent: async (accountId: string, days: number = 30, limit: number = 10) => {
    const dateFrom = new Date();
    dateFrom.setDate(dateFrom.getDate() - days);

    return await db.select({
      taskId: publishTasks.id,
      taskName: publishTasks.taskName,
      publishedAt: publishTasks.publishedAt,
      totalEngagement: sql<number>`SUM(
        COALESCE(${publishMetricsDaily.redditScore}, 0) + 
        COALESCE(${publishMetricsDaily.pinterestSaves}, 0) +
        COALESCE(${publishMetricsDaily.discordReplies}, 0)
      )`
    })
    .from(publishTasks)
    .leftJoin(publishMetricsDaily, eq(publishTasks.id, publishMetricsDaily.publishTaskId))
    .where(and(
      eq(publishTasks.targetAccountId, accountId),
      eq(publishTasks.status, 'published'),
      sql`${publishTasks.publishedAt} >= ${dateFrom.toISOString()}`
    ))
    .groupBy(publishTasks.id)
    .orderBy(desc(sql`totalEngagement`))
    .limit(limit);
  },

  /**
   * 获取多账号数据对比
   * @param accountIds - 账号ID列表
   * @param date - 对比日期
   * 用途: 对比不同账号的表现，资源分配决策
   */
  getMultiAccountComparison: async (accountIds: string[], date?: string) => {
    const compareDate = date || new Date().toISOString().split('T')[0];

    return await db.select({
      accountId: targetAccountsMetricsDaily.targetAccountId,
      platform: targetAccountsMetricsDaily.platform,
      followers: targetAccountsMetricsDaily.followers,
      followersChange: targetAccountsMetricsDaily.followersChange,
      engagementRate: targetAccountsMetricsDaily.engagementRate,
      growthRate: targetAccountsMetricsDaily.growthRate
    })
    .from(targetAccountsMetricsDaily)
    .where(and(
      inArray(targetAccountsMetricsDaily.targetAccountId, accountIds),
      eq(targetAccountsMetricsDaily.metricDate, compareDate)
    ));
  },

  /**
   * 获取运营概览统计数据
   * 用途: 首页看板展示整体运营情况
   */
  getOverviewStats: async () => {
    const today = new Date().toISOString().split('T')[0];

    // 活跃账号数
    const activeAccounts = await db.select({ count: sql<number>`COUNT(*)` })
      .from(targetAccounts)
      .where(eq(targetAccounts.status, 'active'));

    // 今日待发布数
    const todayTasks = await db.select({ count: sql<number>`COUNT(*)` })
      .from(publishTasks)
      .where(and(
        eq(publishTasks.status, 'scheduled'),
        sql`DATE(${publishTasks.scheduledAt}) = ${today}`
      ));

    // 待审核语料数
    const pendingCorpus = await db.select({ count: sql<number>`COUNT(*)` })
      .from(crawlResults)
      .where(eq(crawlResults.curationStatus, 'raw'));

    // 可用语料数
    const availableCorpus = await db.select({ count: sql<number>`COUNT(*)` })
      .from(crawlResults)
      .where(and(
        eq(crawlResults.curationStatus, 'approved'),
        eq(crawlResults.isAvailable, true)
      ));

    // 近7天发布数
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weeklyPublished = await db.select({ count: sql<number>`COUNT(*)` })
      .from(publishTasks)
      .where(and(
        eq(publishTasks.status, 'published'),
        sql`${publishTasks.publishedAt} >= ${weekAgo.toISOString()}`
      ));

    return {
      activeAccounts: activeAccounts[0].count,
      todayScheduledTasks: todayTasks[0].count,
      pendingCorpus: pendingCorpus[0].count,
      availableCorpus: availableCorpus[0].count,
      weeklyPublished: weeklyPublished[0].count
    };
  }
};

// ============================================================================
// 插入/更新工具函数
// ============================================================================

export const mutations = {
  // 创建被运营账号
  createTargetAccount: async (data: typeof targetAccounts.$inferInsert) => {
    return await db.insert(targetAccounts).values(data).returning();
  },

  // 创建信息源账号
  createSourceAccount: async (data: typeof sourceAccounts.$inferInsert) => {
    return await db.insert(sourceAccounts).values(data).returning();
  },

  // 创建抓取任务
  createCrawlTask: async (data: typeof crawlTasks.$inferInsert) => {
    return await db.insert(crawlTasks).values(data).returning();
  },

  // 批量插入抓取结果
  batchInsertCrawlResults: async (data: typeof crawlResults.$inferInsert[]) => {
    return await db.insert(crawlResults).values(data).returning();
  },

  // 更新抓取结果审核状态
  updateCrawlResultCuration: async (
    resultId: string, 
    status: string, 
    notes?: string, 
    qualityScore?: number,
    curatedBy?: string
  ) => {
    return await db.update(crawlResults)
      .set({
        curationStatus: status,
        curationNotes: notes,
        qualityScore,
        curatedBy,
        curatedAt: new Date(),
        isAvailable: status === 'approved'
      })
      .where(eq(crawlResults.id, resultId))
      .returning();
  },

  // 创建发布任务
  createPublishTask: async (data: typeof publishTasks.$inferInsert) => {
    return await db.insert(publishTasks).values(data).returning();
  },

  // 更新发布任务状态
  updatePublishTaskStatus: async (taskId: string, status: string, notes?: string) => {
    const updateData: any = { status };
    if (notes) updateData.reviewNotes = notes;
    if (status === 'published') updateData.publishedAt = new Date();

    return await db.update(publishTasks)
      .set(updateData)
      .where(eq(publishTasks.id, taskId))
      .returning();
  },

  // 插入每日指标数据
  insertDailyMetrics: async (data: typeof targetAccountsMetricsDaily.$inferInsert) => {
    return await db.insert(targetAccountsMetricsDaily).values(data).returning();
  },

  // 插入发布内容每日数据
  insertPublishMetrics: async (data: typeof publishMetricsDaily.$inferInsert) => {
    return await db.insert(publishMetricsDaily).values(data).returning();
  }
};

// 导出所有表，便于直接查询
export { 
  targetAccounts, 
  sourceAccounts, 
  crawlTasks, 
  crawlResults,
  publishTasks,
  publishMetricsDaily,
  targetAccountsMetricsDaily
};
