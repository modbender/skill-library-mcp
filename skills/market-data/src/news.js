import https from 'https';

/**
 * Fetches recent news headlines for a specific query using Google News RSS.
 * @param {Object} params
 * @param {string} params.query - The search query (e.g., "Apple Stock", "Bitcoin").
 * @returns {Promise<string>} A formatted string of news headlines.
 */
export async function get_news_headlines({ query }) {
  return new Promise((resolve, reject) => {
    // Encode query for URL
    const encodedQuery = encodeURIComponent(query);
    const url = `https://news.google.com/rss/search?q=${encodedQuery}&hl=en-US&gl=US&ceid=US:en`;

    https.get(url, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          // Simple XML parsing using Regex to extract items
          const items = [];
          const itemRegex = /<item>([\s\S]*?)<\/item>/g;
          let match;

          while ((match = itemRegex.exec(data)) !== null) {
            const itemBlock = match[1];
            
            const getTag = (tag) => {
              const m = new RegExp(`<${tag}.*?>(.*?)<\/${tag}>`).exec(itemBlock);
              return m ? m[1] : '';
            };

            const title = getTag('title').replace(/<!\[CDATA\[|\]\]>/g, '').trim();
            const pubDate = getTag('pubDate');
            const source = getTag('source');

            items.push({ title, pubDate, source });
          }

          if (items.length === 0) {
            resolve(`No news found for "${query}".`);
            return;
          }

          let output = `📰 News Headlines for "${query}" (Top 50):\n\n`;

          items.slice(0, 50).forEach((item, index) => {
            // Clean up title (Google News often adds "- SourceName" at the end)
            const cleanTitle = item.title.split(' - ').slice(0, -1).join(' - ') || item.title;
            
            // Format Date (Simple truncation if needed)
            const dateStr = item.pubDate ? new Date(item.pubDate).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A';

            output += `${index + 1}. [${dateStr}] ${cleanTitle} (${item.source})\n`;
          });

          resolve(output);

        } catch (error) {
          resolve(`Error parsing news feed: ${error.message}`);
        }
      });

    }).on('error', (err) => {
      resolve(`Network error fetching news: ${err.message}`);
    });
  });
}
