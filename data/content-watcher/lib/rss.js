const Parser = require('rss-parser');

class RSS {
  constructor() {
    this.parser = new Parser({
      timeout: 10000,
      headers: {
        'User-Agent': 'ContentWatcher/1.0'
      }
    });
  }

  async parse(url, limit = 10) {
    try {
      const feed = await this.parser.parseURL(url);
      return (feed.items || []).slice(0, limit).map(item => ({
        title: item.title || 'Untitled',
        link: item.link || item.guid || '',
        contentSnippet: item.contentSnippet || item.content || '',
        pubDate: item.pubDate || item.isoDate || new Date().toISOString(),
        author: item.author || item.creator || 'Unknown'
      }));
    } catch (error) {
      throw new Error(`RSS parse failed: ${error.message}`);
    }
  }
}

module.exports = RSS;
