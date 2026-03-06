#!/usr/bin/env node
/**
 * naver-cafe.js - 네이버 카페 스크래퍼
 * 
 * Usage:
 *   node naver-cafe.js popular "https://cafe.naver.com/..." --limit 20
 *   node naver-cafe.js recent "https://cafe.naver.com/..." --limit 20
 */

const {
  createStealthBrowser,
  humanDelay,
  cleanText,
  outputSuccess,
  outputError,
  rateLimit,
  getDomain,
  parseKoreanDate,
  parseKoreanNumber
} = require('../lib/common.js');

const SELECTORS = {
  // 게시글 목록
  articleList: '.article-board tbody tr, .board-list tbody tr',
  articleTitle: '.article-title a, .board-list .inner_list a.article',
  articleAuthor: '.p-nick, .board-list .board-nick',
  articleDate: '.td_date, .board-list .td_date',
  articleViews: '.td_view, .board-list .td_view',
  articleComments: '.num, .board-list .list-i-count'
};

async function scrapeCafe(cafeUrl, type = 'popular', limit = 20) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    
    // 카페 메인으로 이동
    await rateLimit(getDomain(cafeUrl));
    await page.goto(cafeUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // iframe 처리 (네이버 카페는 iframe 사용)
    let targetFrame = page;
    const frames = page.frames();
    const mainFrame = frames.find(f => f.url().includes('cafe.naver.com'));
    if (mainFrame) {
      targetFrame = mainFrame;
    }
    
    // 인기글/최신글 탭 클릭
    if (type === 'popular') {
      try {
        await targetFrame.click('a[href*="MenuId=1"], .menu-popular a', { timeout: 5000 });
        await humanDelay(1000, 2000);
      } catch (e) {
        console.error('Popular tab not found, using default view');
      }
    }
    
    // 게시글 목록 추출
    const posts = await targetFrame.$$eval(SELECTORS.articleList, (rows, selectors, limit) => {
      return rows.slice(0, limit).map(row => {
        const titleEl = row.querySelector(selectors.articleTitle);
        const authorEl = row.querySelector(selectors.articleAuthor);
        const dateEl = row.querySelector(selectors.articleDate);
        const viewsEl = row.querySelector(selectors.articleViews);
        const commentsEl = row.querySelector(selectors.articleComments);
        
        return {
          title: titleEl?.textContent?.trim() || '',
          url: titleEl?.href || '',
          author: authorEl?.textContent?.trim() || '',
          date: dateEl?.textContent?.trim() || '',
          views: viewsEl?.textContent?.trim() || '0',
          comments: commentsEl?.textContent?.trim() || '0'
        };
      }).filter(post => post.title); // 빈 행 제거
    }, SELECTORS, limit);
    
    // 데이터 정제
    posts.forEach(post => {
      post.date = parseKoreanDate(post.date);
      post.views = parseKoreanNumber(post.views);
      post.comments = parseKoreanNumber(post.comments);
      
      // 상대 URL → 절대 URL 변환
      if (post.url && !post.url.startsWith('http')) {
        const baseUrl = new URL(cafeUrl);
        post.url = `${baseUrl.origin}${post.url}`;
      }
    });
    
    await browser.close();
    
    outputSuccess({
      cafeUrl,
      type,
      count: posts.length,
      posts
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to scrape cafe: ${error.message}`, { cafeUrl, type });
    process.exit(1);
  }
}

// CLI 파싱
const args = process.argv.slice(2);
const command = args[0]; // popular | recent
const cafeUrl = args[1];

if (!command || !cafeUrl) {
  console.error('Usage:');
  console.error('  node naver-cafe.js popular "cafe_url" [--limit N]');
  console.error('  node naver-cafe.js recent "cafe_url" [--limit N]');
  process.exit(1);
}

const limitIndex = args.indexOf('--limit');
const limit = limitIndex !== -1 ? parseInt(args[limitIndex + 1]) : 20;

if (command === 'popular' || command === 'recent') {
  scrapeCafe(cafeUrl, command, limit);
} else {
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}
