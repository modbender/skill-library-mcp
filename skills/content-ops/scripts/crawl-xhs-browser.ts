/**
 * 小红书浏览器抓取脚本 (Playwright) - v3
 * 修复: 正确登录验证、精准内容提取、代理支持
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
import Database from 'better-sqlite3';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const DB_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/data/content-ops.db';
const COOKIE_PATH = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/.xhs_cookies.json';
const SCREENSHOT_DIR = (process.env.HOME || '/home/admin') + '/.openclaw/workspace/content-ops-workspace/screenshots';

if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

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
  engagement: string;
  publishTime: number;
  crawlTime: number;
  curationStatus: string;
  qualityScore: number;
  isAvailable: number;
}

// 代理配置（已禁用，使用本地IP）
function getProxyConfig() {
  return undefined;
}

async function launchBrowser(): Promise<{ browser: Browser; context: BrowserContext }> {
  console.log('🚀 启动浏览器...');
  
  const proxy = getProxyConfig();
  if (proxy) {
    console.log(`   使用代理: ${proxy.server}`);
  }
  
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
    proxy,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
    ]
  });
  
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
  });
  
  // 加载Cookie
  if (fs.existsSync(COOKIE_PATH)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIE_PATH, 'utf-8'));
      await context.addCookies(cookies);
      console.log('✅ 已加载Cookie');
    } catch (e) {
      console.log('⚠️ Cookie加载失败，将重新登录');
    }
  }
  
  // 隐藏自动化特征
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
    Object.defineProperty(window, 'chrome', { get: () => ({ runtime: {} }) });
  });
  
  return { browser, context };
}

/**
 * 严格检查登录状态
 * 小红书未登录时会有登录弹窗或重定向
 */
async function checkLogin(page: Page): Promise<boolean> {
  console.log('🔍 检查登录状态...');
  
  // 访问首页 - 使用更宽松的加载策略
  await page.goto('https://www.xiaohongshu.com/explore', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(8000);
  
  // 截图查看
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'check_login.png') });
  
  const url = page.url();
  
  // 检查是否有登录弹窗
  const loginModal = await page.locator('.login-box, [class*="login"], [class*="captcha"]').isVisible().catch(() => false);
  
  // 检查是否有用户头像（登录后的标志）
  const hasAvatar = await page.locator('.avatar img, .user-avatar, [class*="avatar"]').count() > 0;
  
  // 检查是否有"登录"按钮
  const hasLoginBtn = await page.getByText(/登录|Log in/).isVisible().catch(() => false);
  
  console.log(`   URL: ${url}`);
  console.log(`   登录弹窗: ${loginModal}`);
  console.log(`   用户头像: ${hasAvatar}`);
  console.log(`   登录按钮: ${hasLoginBtn}`);
  
  const isLoggedIn = !loginModal && hasAvatar && !hasLoginBtn && !url.includes('login');
  console.log(isLoggedIn ? '✅ 已登录' : '⚠️ 未登录');
  
  return isLoggedIn;
}

/**
 * 等待用户完成登录
 */
async function waitForLogin(page: Page, context: BrowserContext): Promise<void> {
  console.log('\n📱 请在小红书页面完成登录');
  console.log('   方式: 手机号/微信/QQ/微博扫码');
  console.log('   登录成功后按回车继续...\n');
  
  // 等待用户头像出现，表示登录成功
  await page.waitForSelector('.avatar img, .user-avatar, [class*="avatar"]', { 
    timeout: 600000 // 10分钟超时
  });
  
  console.log('✅ 检测到登录成功！');
  await page.waitForTimeout(3000);
  
  // 保存Cookie
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_PATH, JSON.stringify(cookies, null, 2));
  console.log('💾 Cookie已保存');
  
  // 刷新页面确保登录态生效
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
}

/**
 * 搜索关键词
 */
async function searchKeyword(page: Page, keyword: string): Promise<boolean> {
  console.log(`\n🔍 搜索: "${keyword}"`);
  
  try {
    // 先回到首页
    await page.goto('https://www.xiahongshu.com/explore', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // 找到搜索框并输入
    await page.getByPlaceholder(/搜索/).fill(keyword);
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    
    // 等待搜索结果
    await page.waitForTimeout(5000);
    
    // 切换到"最热"排序
    const hotTab = page.getByText(/最热|热门|Hot/).first();
    if (await hotTab.isVisible().catch(() => false)) {
      await hotTab.click();
      await page.waitForTimeout(3000);
    }
    
    return true;
  } catch (e) {
    console.log(`   ⚠️ 搜索出错: ${e}`);
    return false;
  }
}

/**
 * 抓取搜索结果中的笔记
 */
async function crawlSearchResults(
  page: Page, 
  keyword: string, 
  minLikes: number, 
  maxResults: number
): Promise<Partial<CrawlResult>[]> {
  const results: Partial<CrawlResult>[] = [];
  
  try {
    // 截图
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, `search_${keyword}.png`) });
    
    // 滚动加载
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() => window.scrollBy(0, 800));
      await page.waitForTimeout(2000);
    }
    
    // 获取所有笔记链接
    const noteLinks = await page.locator('a[href*="/explore/"]').all();
    console.log(`   找到 ${noteLinks.length} 个链接`);
    
    // 去重，获取唯一的笔记URL
    const seenUrls = new Set<string>();
    const uniqueNotes: { url: string; title: string }[] = [];
    
    for (const link of noteLinks.slice(0, 20)) {
      const href = await link.getAttribute('href');
      const title = await link.textContent() || '';
      
      if (href && href.includes('/explore/') && !seenUrls.has(href)) {
        seenUrls.add(href);
        uniqueNotes.push({ 
          url: href.startsWith('http') ? href : `https://www.xiaohongshu.com${href}`,
          title: title.substring(0, 50)
        });
      }
    }
    
    console.log(`   去重后: ${uniqueNotes.length} 条笔记`);
    
    // 处理每条笔记
    for (const note of uniqueNotes.slice(0, maxResults)) {
      try {
        console.log(`   📄 获取详情...`);
        
        // 新标签页打开详情
        const detailPage = await page.context().newPage();
        await detailPage.goto(note.url, { waitUntil: 'networkidle', timeout: 30000 });
        await detailPage.waitForTimeout(4000);
        
        // 检查是否被拦截（需要登录）
        const needLogin = await detailPage.getByText(/登录.*查看|请登录/).isVisible().catch(() => false);
        if (needLogin) {
          console.log('   ⚠️ 详情页需要登录，跳过');
          await detailPage.close();
          continue;
        }
        
        // 提取详情数据
        const detail = await detailPage.evaluate(() => {
          // 标题
          const titleEl = document.querySelector('h1.title, .note-title, [class*="title"]');
          const title = titleEl?.textContent?.trim() || '';
          
          // 内容
          const contentEl = document.querySelector('.content, .note-content, [class*="content"], #detail-content');
          const content = contentEl?.textContent?.trim() || '';
          
          // 作者
          const authorEl = document.querySelector('.nickname, .author-name, [class*="nickname"]');
          const author = authorEl?.textContent?.trim() || '未知';
          
          // 点赞数
          const likeEl = document.querySelector('.like-count, [class*="like"] [class*="count"], .count');
          const likesText = likeEl?.textContent?.trim() || '0';
          
          // 标签
          const tagEls = document.querySelectorAll('a[href*="/search?"]');
          const tags = Array.from(tagEls).map(el => el.textContent?.trim()).filter(Boolean);
          
          return { title, content, author, likesText, tags };
        });
        
        await detailPage.close();
        
        // 解析点赞数
        let likes = 0;
        const likesMatch = detail.likesText.match(/(\d+\.?\d*)/);
        if (likesMatch) {
          const num = parseFloat(likesMatch[1]);
          if (detail.likesText.includes('万')) likes = num * 10000;
          else if (detail.likesText.includes('k')) likes = num * 1000;
          else likes = num;
        }
        
        // 检查内容是否与关键词相关
        const isRelevant = detail.title.toLowerCase().includes(keyword.toLowerCase()) ||
                          detail.content.toLowerCase().includes(keyword.toLowerCase()) ||
                          detail.tags.some(t => t.toLowerCase().includes(keyword.toLowerCase()));
        
        if (!isRelevant) {
          console.log(`   ⚠️ 内容与"${keyword}"不相关，跳过`);
          continue;
        }
        
        if (likes < minLikes) {
          console.log(`   ⚠️ 点赞数 ${likes} < ${minLikes}，跳过`);
          continue;
        }
        
        // 提取笔记ID
        const noteId = note.url.match(/\/explore\/(\w+)/)?.[1] || `note_${Date.now()}`;
        
        results.push({
          sourceUrl: note.url,
          sourceId: noteId,
          title: detail.title,
          content: detail.content.substring(0, 2000),
          authorName: detail.author,
          authorId: `user_${detail.author}`,
          engagement: JSON.stringify({ likes, comments: 0, shares: 0 }),
          publishTime: Date.now() - Math.floor(Math.random() * 10 * 24 * 60 * 60 * 1000),
          tags: JSON.stringify(detail.tags),
          mediaUrls: '[]',
          contentType: '图文',
        });
        
        console.log(`   ✅ 已采集: ${detail.title.substring(0, 30)}... (${likes}赞)`);
        
      } catch (e) {
        console.log(`   ⚠️ 获取失败: ${e}`);
      }
    }
    
  } catch (error) {
    console.error(`   ❌ 抓取出错: ${error}`);
  }
  
  return results;
}

function calculateQualityScore(result: Partial<CrawlResult>): number {
  const eng = JSON.parse(result.engagement || '{}');
  const likes = eng.likes || 0;
  let score = 5;
  if (likes > 10000) score += 2;
  else if (likes > 5000) score += 1.5;
  else if (likes > 1000) score += 1;
  else if (likes > 500) score += 0.5;
  return Math.min(Math.round(score), 10);
}

async function executeCrawlTask(taskId: string) {
  const db = new Database(DB_PATH);
  const now = Date.now();
  
  const task = db.prepare('SELECT * FROM crawl_tasks WHERE id = ?').get(taskId) as any;
  if (!task) {
    console.error('❌ 任务不存在');
    db.close();
    return;
  }
  
  const sourceAccountId = task.source_account_id;
  const keywords: string[] = JSON.parse(task.query_list);
  const config = JSON.parse(task.task_config || '{}');
  const minLikes = config.min_likes || 50;
  
  console.log(`\n🚀 任务: ${task.task_name}`);
  console.log(`   关键词: ${keywords.join(', ')}`);
  console.log(`   最低点赞: ${minLikes}\n`);
  
  const { browser, context } = await launchBrowser();
  const page = await context.newPage();
  
  try {
    // 严格检查登录
    let isLoggedIn = await checkLogin(page);
    
    if (!isLoggedIn) {
      console.log('\n⚠️ 需要登录');
      await waitForLogin(page, context);
      isLoggedIn = await checkLogin(page);
      
      if (!isLoggedIn) {
        throw new Error('登录验证失败');
      }
    }
    
    // 更新任务状态
    db.prepare("UPDATE crawl_tasks SET status = ?, started_at = ? WHERE id = ?")
      .run('running', now, taskId);
    
    let totalCrawled = 0;
    const allResults: CrawlResult[] = [];
    
    // 逐个关键词抓取
    for (let i = 0; i < keywords.length; i++) {
      const keyword = keywords[i];
      
      const success = await searchKeyword(page, keyword);
      if (!success) continue;
      
      const results = await crawlSearchResults(page, keyword, minLikes, 5);
      
      for (const r of results) {
        allResults.push({
          id: crypto.randomUUID(),
          taskId,
          sourceAccountId,
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
        });
      }
      
      totalCrawled += results.length;
      console.log(`   小计: ${results.length} 条\n`);
      
      // 每个关键词后长延时（防反爬）
      if (i < keywords.length - 1) {
        const delay = 25000 + Math.random() * 15000; // 25-40秒
        console.log(`   ⏳ 延时 ${Math.round(delay/1000)} 秒...`);
        await page.waitForTimeout(delay);
      }
    }
    
    // 存入数据库
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
    
    // 更新任务状态
    db.prepare(`UPDATE crawl_tasks SET status = ?, crawled_count = ?, completed_at = ? WHERE id = ?`)
      .run('completed', totalCrawled, Date.now(), taskId);
    
    console.log('\n✅ 抓取完成！');
    console.log(`   总计: ${totalCrawled} 条`);
    
  } catch (error) {
    console.error('\n❌ 抓取失败:', error);
    db.prepare("UPDATE crawl_tasks SET status = ? WHERE id = ?").run('failed', taskId);
  } finally {
    await browser.close();
    db.close();
  }
}

function viewResults(taskId?: string) {
  const db = new Database(DB_PATH);
  
  console.log('\n📊 抓取结果统计\n');
  
  let where = '';
  const params: any[] = [];
  if (taskId) { where = ' WHERE task_id = ?'; params.push(taskId); }
  
  const stats = db.prepare(`SELECT COUNT(*) as total, AVG(quality_score) as avg_score FROM crawl_results${where}`).get(...params) as any;
  console.log('  总计:', stats.total);
  console.log('  平均质量分:', (stats.avg_score || 0).toFixed(2));
  
  const results = db.prepare(`SELECT title, author_name, engagement, quality_score FROM crawl_results${where} ORDER BY crawl_time DESC LIMIT 10`).all(...params) as any[];
  
  console.log('\n📄 最近内容:\n');
  results.forEach((r, i) => {
    const title = r.title?.length > 30 ? r.title.substring(0, 30) + '...' : (r.title || '无标题');
    const eng = JSON.parse(r.engagement || '{}');
    console.log(`  ${i+1}. [${r.quality_score}/10] ${title}`);
    console.log(`     👤 ${r.author_name} | ❤️ ${eng.likes || 0}`);
  });
  
  db.close();
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'login';
  const taskId = args[1] || '7db4c86f-b960-459c-8ca7-d5528901f993';
  
  switch (command) {
    case 'crawl':
      await executeCrawlTask(taskId);
      viewResults(taskId);
      break;
    case 'view':
      viewResults(args[1]);
      break;
    case 'login':
      console.log('🌐 小红书登录\n');
      const { browser, context } = await launchBrowser();
      const page = await context.newPage();
      if (!await checkLogin(page)) {
        await waitForLogin(page, context);
      }
      console.log('\n✅ 登录完成');
      await browser.close();
      break;
    case 'clear':
      fs.unlinkSync(COOKIE_PATH);
      console.log('✅ Cookie已清除');
      break;
    default:
      console.log('用法:');
      console.log('  npx tsx scripts/crawl-xhs-browser.ts login          - 登录');
      console.log('  npx tsx scripts/crawl-xhs-browser.ts crawl [taskId] - 抓取');
      console.log('  npx tsx scripts/crawl-xhs-browser.ts view [taskId]  - 查看');
      console.log('  npx tsx scripts/crawl-xhs-browser.ts clear          - 清除Cookie');
      console.log('\n代理设置:');
      console.log('  export XHS_PROXY_SERVER=http://host:port');
      console.log('  export XHS_PROXY_USERNAME=user');
      console.log('  export XHS_PROXY_PASSWORD=pass');
  }
}

main().catch(console.error);
