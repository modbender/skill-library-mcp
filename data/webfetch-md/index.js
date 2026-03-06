/**
 * WebFetch MD - 抓取网页并转换为 Markdown
 * 保留图片链接，智能提取正文
 */

const TurndownService = require('turndown');
const cheerio = require('cheerio');

// 默认请求头（模拟浏览器）
const DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
};

/**
 * 智能提取正文内容
 * 优先级：article > main > [role="main"] > .content > .post > body
 */
function extractContent($) {
  // 移除不需要的元素
  const removeSelectors = [
    'script', 'style', 'nav', 'header', 'footer',
    '.sidebar', '.ads', '.advertisement', '.comments',
    '#sidebar', '#ads', '#comments', '#footer',
    '[class*="ad-"]', '[class*="advertisement"]'
  ];
  removeSelectors.forEach(sel => $(sel).remove());

  // 尝试找到主要内容区域
  const contentSelectors = [
    'article',
    'main',
    '[role="main"]',
    '.post-content',
    '.entry-content',
    '.article-content',
    '.content',
    '.post',
    '#content',
    '#main'
  ];

  for (const selector of contentSelectors) {
    const el = $(selector).first();
    if (el.length && el.text().trim().length > 200) {
      return el;
    }
  }

  //  fallback：返回 body
  return $('body');
}

/**
 * 将相对 URL 转为绝对 URL
 */
function toAbsoluteUrl(url, baseUrl) {
  if (!url) return url;
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  if (url.startsWith('//')) {
    return 'https:' + url;
  }
  
  const base = new URL(baseUrl);
  if (url.startsWith('/')) {
    return `${base.protocol}//${base.host}${url}`;
  }
  return `${base.protocol}//${base.host}/${url}`;
}

/**
 * 抓取网页并转换为 Markdown
 * @param {string} url - 目标 URL
 * @param {object} options - 选项
 * @returns {Promise<object>} - 结果对象
 */
async function fetchAsMarkdown(url, options = {}) {
  try {
    // 1. 抓取网页
    const response = await fetch(url, {
      headers: { ...DEFAULT_HEADERS, ...options.headers },
      ...options.fetchOptions
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);

    // 2. 提取标题
    const title = $('title').text().trim() || 
                  $('h1').first().text().trim() || 
                  $('h2').first().text().trim() ||
                  '无标题';

    // 3. 提取主要内容
    const $content = extractContent($);

    // 4. 处理图片（相对路径转绝对路径）
    const images = [];
    $content.find('img').each((i, el) => {
      const $img = $(el);
      const src = $img.attr('src');
      const alt = $img.attr('alt') || '';
      
      if (src) {
        const absoluteSrc = toAbsoluteUrl(src, url);
        $img.attr('src', absoluteSrc);
        images.push({ src: absoluteSrc, alt });
      }
    });

    // 5. 处理链接（相对转绝对）
    $content.find('a').each((i, el) => {
      const $a = $(el);
      const href = $a.attr('href');
      if (href && !href.startsWith('#')) {
        $a.attr('href', toAbsoluteUrl(href, url));
      }
    });

    // 6. 转换为 Markdown
    const turndownService = new TurndownService({
      headingStyle: 'atx',
      bulletListMarker: '-',
      codeBlockStyle: 'fenced',
      emDelimiter: '*',
      strongDelimiter: '**'
    });

    // 保留图片
    turndownService.addRule('image', {
      filter: 'img',
      replacement: (content, node) => {
        const alt = node.getAttribute('alt') || '';
        const src = node.getAttribute('src') || '';
        return src ? `![${alt}](${src})` : '';
      }
    });

    const markdown = turndownService.turndown($content.html());

    return {
      success: true,
      url,
      title,
      markdown,
      images,
      imageCount: images.length,
      contentLength: markdown.length
    };

  } catch (error) {
    return {
      success: false,
      url,
      error: error.message
    };
  }
}

/**
 * 批量抓取
 */
async function batchFetch(urls, options = {}) {
  const results = await Promise.all(
    urls.map(url => fetchAsMarkdown(url, options))
  );
  return results;
}

module.exports = {
  fetchAsMarkdown,
  batchFetch,
  extractContent,
  toAbsoluteUrl
};
