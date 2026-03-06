/**
 * Markdown Fetch - Cloudflare Markdown for Agents 优化
 * 
 * 使用方法：
 * const { optimizedFetch } = require('./index');
 * const result = await optimizedFetch('https://example.com');
 */

const DEFAULT_HEADERS = {
  'Accept': 'text/markdown, text/html'
};

/**
 * 优化的网页抓取函数
 * @param {string} url - 目标 URL
 * @param {object} options - fetch 选项
 * @returns {Promise<object>} - 包含 markdown/html 和元数据
 */
async function optimizedFetch(url, options = {}) {
  const headers = {
    ...DEFAULT_HEADERS,
    ...options.headers
  };

  const fetchOptions = {
    ...options,
    headers
  };

  try {
    const response = await fetch(url, fetchOptions);
    
    const contentType = response.headers.get('content-type') || '';
    const xMarkdownTokens = response.headers.get('x-markdown-tokens');
    
    const result = {
      url,
      ok: response.ok,
      status: response.status,
      contentType,
      format: null,
      content: null,
      tokensSaved: xMarkdownTokens ? parseInt(xMarkdownTokens) : null,
      raw: {
        headers: Object.fromEntries(response.headers.entries())
      }
    };
    
    if (contentType.includes('text/markdown')) {
      result.format = 'markdown';
      result.content = await response.text();
      result.markdown = result.content;
    } else {
      result.format = 'html';
      result.content = await response.text();
      result.html = result.content;
    }
    
    // 可选：日志记录 token 节省
    if (result.tokensSaved) {
      console.log(`[Markdown Fetch] Token 节省: ${result.tokensSaved} | URL: ${url}`);
    }
    
    return result;
    
  } catch (error) {
    return {
      url,
      ok: false,
      error: error.message,
      format: 'error'
    };
  }
}

/**
 * 从 HTML 提取内容（备用方案）
 * @param {string} html - HTML 内容
 * @returns {string} - 提取的文本
 */
function extractTextFromHTML(html) {
  // 简单的 HTML 标签去除
  return html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * 批量抓取多个 URL
 * @param {string[]} urls - URL 数组
 * @param {object} options - fetch 选项
 * @returns {Promise<object[]>} - 结果数组
 */
async function batchFetch(urls, options = {}) {
  const results = await Promise.all(
    urls.map(url => optimizedFetch(url, options))
  );
  return results;
}

module.exports = {
  optimizedFetch,
  extractTextFromHTML,
  batchFetch,
  DEFAULT_HEADERS
};
