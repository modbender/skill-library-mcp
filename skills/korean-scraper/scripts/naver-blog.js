#!/usr/bin/env node
/**
 * naver-blog.js - 네이버 블로그 스크래퍼
 * 
 * Usage:
 *   node naver-blog.js search "맛집" --limit 10
 *   node naver-blog.js extract "https://blog.naver.com/..."
 */

const path = require('path');
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
  // 검색 결과 페이지
  searchItem: '.view_wrap',
  searchTitle: '.title_link',
  searchBlogger: '.name',
  searchDate: '.sub_time',
  searchSnippet: '.dsc_link',
  
  // 블로그 본문
  blogTitle: '.se-title-text, .pcol1',
  blogDate: '.se_publishDate, .se_date',
  blogContent: '.se-main-container, #postViewArea',
  blogImages: '.se-image-resource, #postViewArea img',
  blogTags: '.tag_list a'
};

async function searchBlog(query, limit = 10) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    const searchUrl = `https://search.naver.com/search.naver?where=blog&query=${encodeURIComponent(query)}`;
    
    await rateLimit('naver.com');
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // 검색 결과 추출
    const results = await page.$$eval(SELECTORS.searchItem, (items, selectors, limit) => {
      return items.slice(0, limit).map(item => {
        const titleEl = item.querySelector(selectors.searchTitle);
        const bloggerEl = item.querySelector(selectors.searchBlogger);
        const dateEl = item.querySelector(selectors.searchDate);
        const snippetEl = item.querySelector(selectors.searchSnippet);
        
        return {
          title: titleEl?.textContent?.trim() || '',
          url: titleEl?.href || '',
          blogger: bloggerEl?.textContent?.trim() || '',
          date: dateEl?.textContent?.trim() || '',
          snippet: snippetEl?.textContent?.trim() || ''
        };
      });
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
    outputError(`Failed to search blog: ${error.message}`, { query });
    process.exit(1);
  }
}

async function extractBlog(url) {
  const { browser, context } = await createStealthBrowser();
  
  try {
    const page = await context.newPage();
    
    await rateLimit(getDomain(url));
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await humanDelay(2000, 4000);
    
    // iframe 처리 (네이버 블로그는 iframe 사용)
    let targetFrame = page;
    const frames = page.frames();
    const mainFrame = frames.find(f => f.url().includes('blog.naver.com'));
    if (mainFrame) {
      targetFrame = mainFrame;
    }
    
    // 본문 추출
    const data = await targetFrame.evaluate((selectors) => {
      const titleEl = document.querySelector(selectors.blogTitle);
      const dateEl = document.querySelector(selectors.blogDate);
      const contentEl = document.querySelector(selectors.blogContent);
      const imageEls = document.querySelectorAll(selectors.blogImages);
      const tagEls = document.querySelectorAll(selectors.blogTags);
      
      return {
        title: titleEl?.textContent?.trim() || '',
        date: dateEl?.textContent?.trim() || '',
        content: contentEl?.textContent?.trim() || '',
        images: Array.from(imageEls).map(img => img.src || img.dataset.src).filter(Boolean),
        tags: Array.from(tagEls).map(tag => tag.textContent?.trim()).filter(Boolean)
      };
    }, SELECTORS);
    
    // 작성자 추출 (URL에서)
    const authorMatch = url.match(/blog\.naver\.com\/([^\/\?]+)/);
    const author = authorMatch ? authorMatch[1] : '';
    
    await browser.close();
    
    outputSuccess({
      url,
      title: data.title,
      author,
      date: parseKoreanDate(data.date),
      content: cleanText(data.content),
      images: data.images,
      tags: data.tags
    });
    
  } catch (error) {
    await browser.close();
    outputError(`Failed to extract blog: ${error.message}`, { url });
    process.exit(1);
  }
}

// CLI 파싱
const args = process.argv.slice(2);
const command = args[0];
const target = args[1];

if (!command || !target) {
  console.error('Usage:');
  console.error('  node naver-blog.js search "query" [--limit N]');
  console.error('  node naver-blog.js extract "url"');
  process.exit(1);
}

const limitIndex = args.indexOf('--limit');
const limit = limitIndex !== -1 ? parseInt(args[limitIndex + 1]) : 10;

if (command === 'search') {
  searchBlog(target, limit);
} else if (command === 'extract') {
  extractBlog(target);
} else {
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}
