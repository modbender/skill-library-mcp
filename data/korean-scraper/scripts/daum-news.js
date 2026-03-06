#!/usr/bin/env node
/**
 * daum-news.js - 다음 뉴스 스크래퍼
 * 
 * Usage:
 *   node daum-news.js search "경제" --limit 10
 *   node daum-news.js extract "https://v.daum.net/..."
 */

const {
  createStealthBrowser,
  humanDelay,
  cleanText,
  outputSuccess,
  outputError,
  rateLimit,
  getDomain,
  parseKoreanDate
} = require('../lib/common.js');

const SELECTORS = {
  // 검색 결과
  searchItem: '.c-item-doc, .news-item',
  searchTitle: '.tit-g, .item-title a',
  searchMedia: '.info-cp, .source',
  searchDate: '.date, .info-time',
  searchSnippet: '.desc, .item-contents',
  
  // 기사 본문
  articleTitle: 'h3.tit_view, .news_title',
  articleMedia: '.info_view .txt_info:first-child, .head_view .txt_info',
  articleAuthor: '.link_txt, .txt_info .link_txt',
  articleDate: '.num_date, .txt_info .num_date',
  articleContent: '#harmonyContainer, .article_view',
  articleImages: '#harmonyContainer img, .article_view img',
  articleCategory: '.link_txt, .head_view .link_txt'
};

async function searchNews(query, limit = 10) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    const searchUrl = `https://search.daum.net/search?w=news&q=${encodeURIComponent(query)}`;
    
    await rateLimit('daum.net');
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // 검색 결과 추출
    const results = await page.$$eval(SELECTORS.searchItem, (items, selectors, limit) => {
      return items.slice(0, limit).map(item => {
        const titleEl = item.querySelector(selectors.searchTitle);
        const mediaEl = item.querySelector(selectors.searchMedia);
        const dateEl = item.querySelector(selectors.searchDate);
        const snippetEl = item.querySelector(selectors.searchSnippet);
        
        return {
          title: titleEl?.textContent?.trim() || '',
          url: titleEl?.href || '',
          media: mediaEl?.textContent?.trim() || '',
          date: dateEl?.textContent?.trim() || '',
          snippet: snippetEl?.textContent?.trim() || ''
        };
      }).filter(item => item.title);
    }, SELECTORS, limit);
    
    // 날짜 파싱
    results.forEach(item => {
      item.date = parseKoreanDate(item.date);
    });
    
    await browser.close();
    
    outputSuccess({
      query,
      count: results.length,
      results
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to search news: ${error.message}`, { query });
    process.exit(1);
  }
}

async function extractArticle(url) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    
    await rateLimit(getDomain(url));
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // 기사 본문 추출
    const data = await page.evaluate((selectors) => {
      const getText = (selector) => {
        const el = document.querySelector(selector);
        return el?.textContent?.trim() || '';
      };
      
      return {
        title: getText(selectors.articleTitle),
        media: getText(selectors.articleMedia),
        author: getText(selectors.articleAuthor),
        date: getText(selectors.articleDate),
        content: getText(selectors.articleContent),
        images: Array.from(document.querySelectorAll(selectors.articleImages))
          .map(img => img.src)
          .filter(src => src && !src.includes('icon') && !src.includes('logo')),
        category: getText(selectors.articleCategory)
      };
    }, SELECTORS);
    
    // 본문에서 불필요한 텍스트 제거
    let content = data.content;
    content = content.replace(/무단\s*전재\s*및?\s*재배포\s*금지/gi, '');
    content = content.replace(/ⓒ\s*.*?무단\s*전재.*?\n/gi, '');
    content = content.replace(/\[.*?기자.*?\]/g, '');
    
    await browser.close();
    
    outputSuccess({
      url,
      title: data.title,
      media: data.media,
      author: data.author,
      date: parseKoreanDate(data.date),
      content: cleanText(content),
      category: data.category,
      images: data.images
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to extract article: ${error.message}`, { url });
    process.exit(1);
  }
}

// CLI 파싱
const args = process.argv.slice(2);
const command = args[0];
const target = args[1];

if (!command || !target) {
  console.error('Usage:');
  console.error('  node daum-news.js search "query" [--limit N]');
  console.error('  node daum-news.js extract "article_url"');
  process.exit(1);
}

const limitIndex = args.indexOf('--limit');
const limit = limitIndex !== -1 ? parseInt(args[limitIndex + 1]) : 10;

if (command === 'search') {
  searchNews(target, limit);
} else if (command === 'extract') {
  extractArticle(target);
} else {
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}
