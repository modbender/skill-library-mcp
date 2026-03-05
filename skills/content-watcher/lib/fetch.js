const axios = require('axios');
const cheerio = require('cheerio');

class Fetcher {
  constructor(options = {}) {
    this.timeout = options.timeout || 15000;
    this.maxRedirects = options.maxRedirects || 5;
  }

  async extract(url) {
    try {
      const response = await axios.get(url, {
        timeout: this.timeout,
        maxRedirects: this.maxRedirects,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      const $ = cheerio.load(response.data);
      
      // Remove non-content elements
      $('script, style, nav, header, footer, aside, .ads, .comments').remove();
      
      // Try to find main content
      const selectors = [
        'article',
        '[role="main"]',
        '.post-content',
        '.entry-content',
        '.article-content',
        'main',
        '.content',
        '#content'
      ];
      
      let content = '';
      for (const selector of selectors) {
        const el = $(selector);
        if (el.length > 0) {
          content = el.text();
          break;
        }
      }
      
      if (!content) {
        content = $('body').text();
      }
      
      return this.cleanText(content);
    } catch (error) {
      console.error(`Fetch error for ${url}:`, error.message);
      return null;
    }
  }

  cleanText(text) {
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim()
      .substring(0, 8000); // Limit for API
  }
}

module.exports = Fetcher;
