/**
 * 小红书内容抓取脚本
 * 
 * 使用方法:
 * cd /home/admin/.openclaw/workspace/skills/content-ops
 * npx tsx scripts/crawl-xiaohongshu.ts crawl [taskId]
 * npx tsx scripts/crawl-xiaohongshu.ts view [taskId]
 */

import Database from 'better-sqlite3';
import crypto from 'crypto';

const DB_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/data/content-ops.db';

interface CrawlResult {
  id: string;
  taskId: string;
  sourceAccountId: string;
  platform: string;
  sourceUrl: string;
  sourceId: string;
  authorName: string;
  authorId: string;
  title: string;
  content: string;
  contentType: string;
  mediaUrls: string;
  tags: string;
  engagement: string; // JSON: { likes, comments, shares }
  publishTime: number;
  crawlTime: number;
  curationStatus: string;
  qualityScore: number;
  isAvailable: number;
}

/**
 * 模拟小红书搜索（实际使用时替换为真实API调用）
 */
async function fetchXiaohongshuContent(
  keyword: string, 
  sourceAccountId: string,
  minLikes: number = 50, 
  limit: number = 10
): Promise<Partial<CrawlResult>[]> {
  console.log(`  搜索: ${keyword}`);
  
  const mockResults: Partial<CrawlResult>[] = [
    {
      sourceUrl: `https://www.xiaohongshu.com/explore/mock-${Date.now()}-1`,
      sourceId: `note_${Math.random().toString(36).substring(7)}`,
      title: `${keyword} | 2026年最值得关注的AI趋势盘点`,
      content: `最近在研究AI领域的新动态，发现了几个非常有趣的方向... 1) AI Agent的普及化 2) 多模态模型的突破 3) AI编程助手的进化。这些趋势正在改变我们的工作和生活方式。`,
      authorName: `AI前沿观察`,
      authorId: `user_${Math.random().toString(36).substring(7)}`,
      engagement: JSON.stringify({ likes: Math.floor(Math.random() * 500) + 100, comments: Math.floor(Math.random() * 50) + 10, shares: Math.floor(Math.random() * 30) + 5 }),
      publishTime: Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000),
      tags: JSON.stringify(['AI', '人工智能', '科技', '趋势']),
      mediaUrls: JSON.stringify(['https://example.com/img1.jpg']),
      contentType: '图文',
    },
    {
      sourceUrl: `https://www.xiaohongshu.com/explore/mock-${Date.now()}-2`,
      sourceId: `note_${Math.random().toString(36).substring(7)}`,
      title: `用${keyword}提升工作效率的5个技巧`,
      content: `亲测有效的AI工具使用心得：1. 提示词优化 2. 工作流自动化 3. 数据分析加速 4. 内容创作辅助 5. 学习研究助手。每个技巧都有详细的操作步骤。`,
      authorName: `效率工具控`,
      authorId: `user_${Math.random().toString(36).substring(7)}`,
      engagement: JSON.stringify({ likes: Math.floor(Math.random() * 300) + 80, comments: Math.floor(Math.random() * 40) + 8, shares: Math.floor(Math.random() * 25) + 3 }),
      publishTime: Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000),
      tags: JSON.stringify(['AI工具', '效率', '职场']),
      mediaUrls: JSON.stringify(['https://example.com/img2.jpg']),
      contentType: '图文',
    },
    {
      sourceUrl: `https://www.xiaohongshu.com/explore/mock-${Date.now()}-3`,
      sourceId: `note_${Math.random().toString(36).substring(7)}`,
      title: `${keyword}新手入门指南 | 从零开始学AI`,
      content: `很多小伙伴问我怎么入门AI，今天整理了一份保姆级教程。首先了解基础概念，然后动手实践，最后持续跟进最新动态。推荐几个学习资源...`,
      authorName: `AI学习日记`,
      authorId: `user_${Math.random().toString(36).substring(7)}`,
      engagement: JSON.stringify({ likes: Math.floor(Math.random() * 400) + 150, comments: Math.floor(Math.random() * 60) + 15, shares: Math.floor(Math.random() * 35) + 8 }),
      publishTime: Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000),
      tags: JSON.stringify(['AI教程', '入门', '学习']),
      mediaUrls: JSON.stringify(['https://example.com/img3.jpg']),
      contentType: '图文',
    }
  ];
  
  return mockResults.filter(r => {
    const eng = JSON.parse(r.engagement || '{}');
    return (eng.likes || 0) >= minLikes;
  }).slice(0, limit);
}

/**
 * 计算内容质量分
 */
function calculateQualityScore(result: Partial<CrawlResult>): number {
  const eng = JSON.parse(result.engagement || '{}');
  const likes = eng.likes || 0;
  const comments = eng.comments || 0;
  const shares = eng.shares || 0;
  
  let score = 5;
  if (likes > 1000) score += 2;
  else if (likes > 500) score += 1.5;
  else if (likes > 100) score += 1;
  
  if (comments > 50) score += 1;
  if (shares > 30) score += 1;
  
  return Math.min(Math.round(score), 10);
}

/**
 * 执行抓取任务
 */
async function executeCrawlTask(taskId: string) {
  const db = new Database(DB_PATH);
  const now = Date.now();
  
  console.log(`\n🚀 开始执行抓取任务: ${taskId}\n`);
  
  // 1. 获取任务详情
  const task = db.prepare('SELECT * FROM crawl_tasks WHERE id = ?').get(taskId) as any;
  if (!task) {
    console.error('❌ 任务不存在:', taskId);
    db.close();
    return;
  }
  
  // 获取数据源账号ID
  const sourceAccountId = task.source_account_id;
  
  console.log('任务:', task.task_name);
  console.log('数据源:', sourceAccountId);
  console.log('关键词:', JSON.parse(task.query_list).join(', '));
  console.log('');
  
  // 2. 更新任务状态为 running
  db.prepare("UPDATE crawl_tasks SET status = ?, started_at = ? WHERE id = ?")
    .run('running', now, taskId);
  
  const keywords: string[] = JSON.parse(task.query_list);
  const config = JSON.parse(task.task_config || '{}');
  const minLikes = config.min_likes || 50;
  
  let totalCrawled = 0;
  const allResults: CrawlResult[] = [];
  
  // 3. 逐个关键词抓取
  for (const keyword of keywords) {
    try {
      const results = await fetchXiaohongshuContent(keyword, sourceAccountId, minLikes, 5);
      
      for (const r of results) {
        const result: CrawlResult = {
          id: crypto.randomUUID(),
          taskId: taskId,
          sourceAccountId: sourceAccountId,
          platform: 'xiaohongshu',
          sourceUrl: r.sourceUrl || '',
          sourceId: r.sourceId || '',
          authorName: r.authorName || '',
          authorId: r.authorId || '',
          title: r.title || '',
          content: r.content || '',
          contentType: r.contentType || '图文',
          mediaUrls: r.mediaUrls || '[]',
          tags: r.tags || '[]',
          engagement: r.engagement || '{}',
          publishTime: r.publishTime || now,
          crawlTime: now,
          curationStatus: 'raw',
          qualityScore: calculateQualityScore(r),
          isAvailable: 0,
        };
        allResults.push(result);
      }
      
      totalCrawled += results.length;
      console.log(`    ✓ ${keyword}: ${results.length} 条`);
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
    } catch (error) {
      console.error(`    ✗ ${keyword} 失败:`, error);
    }
  }
  
  // 4. 批量存入数据库
  if (allResults.length > 0) {
    const insert = db.prepare(`
      INSERT INTO crawl_results 
      (id, task_id, source_account_id, platform, source_url, source_id, 
       author_name, author_id, title, content, content_type, media_urls, tags,
       engagement, publish_time, crawl_time, curation_status, quality_score, is_available, usage_count)
      VALUES 
      (@id, @taskId, @sourceAccountId, @platform, @sourceUrl, @sourceId,
       @authorName, @authorId, @title, @content, @contentType, @mediaUrls, @tags,
       @engagement, @publishTime, @crawlTime, @curationStatus, @qualityScore, @isAvailable, 0)
    `);
    
    const insertMany = db.transaction((rows: CrawlResult[]) => {
      for (const row of rows) insert.run(row);
    });
    
    insertMany(allResults);
    console.log(`\n💾 已存入数据库: ${allResults.length} 条`);
  }
  
  // 5. 更新任务状态为 completed
  db.prepare(`
    UPDATE crawl_tasks 
    SET status = ?, crawled_count = ?, completed_at = ? 
    WHERE id = ?
  `).run('completed', totalCrawled, Date.now(), taskId);
  
  console.log('\n✅ 抓取完成');
  console.log(`   总计: ${totalCrawled} 条`);
  
  db.close();
}

/**
 * 查看抓取结果
 */
function viewCrawlResults(taskId?: string) {
  const db = new Database(DB_PATH);
  
  console.log('\n📊 抓取结果统计\n');
  
  let statsQuery = `
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN curation_status = 'raw' THEN 1 ELSE 0 END) as pending,
      SUM(CASE WHEN curation_status = 'approved' THEN 1 ELSE 0 END) as approved,
      SUM(CASE WHEN curation_status = 'rejected' THEN 1 ELSE 0 END) as rejected,
      AVG(quality_score) as avg_score
    FROM crawl_results
  `;
  if (taskId) statsQuery += ' WHERE task_id = ?';
  
  const stats = db.prepare(statsQuery).get(taskId || []) as any;
  
  console.log('  总计:', stats.total);
  console.log('  待审核:', stats.pending);
  console.log('  已通过:', stats.approved);
  console.log('  已拒绝:', stats.rejected);
  console.log('  平均质量分:', (stats.avg_score || 0).toFixed(2));
  
  console.log('\n📄 最近内容:\n');
  let listQuery = `
    SELECT title, author_name, engagement, quality_score, curation_status
    FROM crawl_results
  `;
  if (taskId) listQuery += ' WHERE task_id = ?';
  listQuery += ' ORDER BY crawl_time DESC LIMIT 10';
  
  const results = db.prepare(listQuery).all(taskId || []) as any[];
  
  results.forEach((r, i) => {
    const title = r.title.length > 30 ? r.title.substring(0, 30) + '...' : r.title;
    const eng = JSON.parse(r.engagement || '{}');
    console.log(`  ${i+1}. [${r.quality_score}/10] ${title}`);
    console.log(`      👤 ${r.author_name} | ❤️ ${eng.likes || 0} | ${r.curation_status}`);
  });
  
  db.close();
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'crawl';
  const taskId = args[1] || '7db4c86f-b960-459c-8ca7-d5528901f993';
  
  switch (command) {
    case 'crawl':
      await executeCrawlTask(taskId);
      viewCrawlResults(taskId);
      break;
    case 'view':
      viewCrawlResults(args[1]);
      break;
    default:
      console.log('用法:');
      console.log('  npx tsx scripts/crawl-xiaohongshu.ts crawl [taskId]');
      console.log('  npx tsx scripts/crawl-xiaohongshu.ts view [taskId]');
  }
}

main().catch(console.error);
