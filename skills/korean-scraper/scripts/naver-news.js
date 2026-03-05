#!/usr/bin/env node
/**
 * naver-news.js - 네이버 뉴스 스크래퍼
 * 
 * Usage:
 *   node naver-news.js search "AI" --limit 10
 *   node naver-news.js extract "https://n.news.naver.com/..."
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
  searchItem: '.list_news > li, .news_area',
  searchTitle: '.news_tit, a.news_tit',
  searchMedia: '.info.press, .info_group .press',
  searchDate: '.info, .info_group span',
  searchSnippet: '.news_dsc, .dsc_txt_wrap',
  
  // 기사 본문
  articleTitle: '#title_area span, #articleTitle',
  articleMedia: '.media_end_head_top_logo img, .press_logo img',
  articleAuthor: '.byline_s, .journalist_list .journalist',
  articleDate: '.media_end_head_info_datestamp_time, #ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span',
  articleContent: '#dic_area, #articleBodyContents, .article_body',
  articleImages: '#dic_area img, #articleBodyContents img',
  articleCategory: '.media_end_categorize_item, .article_categorize li'
};

async function searchNews(query, limit = 10) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    const searchUrl = `https://search.naver.com/search.naver?where=news&query=${encodeURIComponent(query)}`;
    
    await rateLimit('naver.com');
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
      // "언론사명 날짜" 형식에서 날짜만 추출
      const dateMatch = item.date.match(/\d+\.\d+\.\d+\.?|[전후]\s*\d+/);
      item.date = dateMatch ? parseKoreanDate(dateMatch[0]) : item.date;
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
        media: document.querySelector(selectors.articleMedia)?.alt || getText(selectors.articleMedia),
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
      date: data.date,
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
  console.error('  node naver-news.js search "query" [--limit N]');
  console.error('  node naver-news.js extract "article_url"');
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
