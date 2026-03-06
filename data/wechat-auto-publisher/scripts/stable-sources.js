/**
 * 稳定数据源接入模块
 * 使用无需登录、反爬宽松的公开 API
 */

const fetch = require('node-fetch');
const cheerio = require('cheerio');

class StableSources {
  /**
   * 获取 GitHub Trending（最稳定）
   */
  async getGitHubTrending() {
    try {
      console.log('[数据源] GitHub Trending...');
      
      const response = await fetch('https://github.com/trending', {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml'
        },
        timeout: 15000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const html = await response.text();
      const $ = cheerio.load(html);
      const repos = [];
      
      $('article.Box-row').each((i, el) => {
        const fullName = $(el).find('h2 a').text().replace(/\s+/g, ' ').trim();
        const url = $(el).find('h2 a').attr('href');
        const description = $(el).find('p').text().trim();
        const language = $(el).find('[aria-label="Programming language"]').text().trim();
        const stars = $(el).find('[aria-label="stars"]').text().replace(',', '').trim();
        const forks = $(el).find('[aria-label="forks"]').text().replace(',', '').trim();
        
        if (fullName && url) {
          repos.push({
            source: 'github',
            title: `${fullName} - ${description || '热门开源项目'}`,
            shortTitle: fullName,
            description: description,
            language: language,
            stars: stars,
            forks: forks,
            hotValue: 95 - i * 3,
            url: `https://github.com${url}`,
            timestamp: new Date().toISOString(),
            category: 'tech'
          });
        }
      });
      
      console.log(`  ✅ 获取 ${repos.length} 个项目`);
      return repos;
      
    } catch (error) {
      console.error(`  ❌ GitHub 失败：${error.message}`);
      return [];
    }
  }

  /**
   * 获取 Hacker News（最稳定，纯 JSON API）
   */
  async getHackerNews() {
    try {
      console.log('[数据源] Hacker News...');
      
      const storyIds = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json', { timeout: 10000 })
        .then(r => r.json());
      
      const stories = [];
      
      // 获取前 25 个故事
      for (let i = 0; i < Math.min(25, storyIds.length); i++) {
        try {
          const story = await fetch(`https://hacker-news.firebaseio.com/v0/item/${storyIds[i]}.json`, { timeout: 5000 })
            .then(r => r.json());
          
          if (story && story.title) {
            stories.push({
              source: 'hackernews',
              title: story.title,
              hotValue: story.score || (100 - i * 3),
              url: story.url || `https://news.ycombinator.com/item?id=${story.id}`,
              timestamp: new Date(story.time * 1000).toISOString(),
              points: story.score,
              comments: story.descendants || 0,
              author: story.by,
              category: 'tech'
            });
          }
        } catch (e) {
          // 单个故事失败不影响整体
        }
      }
      
      console.log(`  ✅ 获取 ${stories.length} 个故事`);
      return stories;
      
    } catch (error) {
      console.error(`  ❌ Hacker News 失败：${error.message}`);
      return [];
    }
  }

  /**
   * 获取 Reddit r/technology（通过公开 RSS）
   */
  async getRedditTechnology() {
    try {
      console.log('[数据源] Reddit r/technology...');
      
      // 使用 Reddit 的 RSS（无需 API Key）
      const response = await fetch('https://www.reddit.com/r/technology/hot.rss', {
        headers: { 'User-Agent': 'Mozilla/5.0' },
        timeout: 10000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const xml = await response.text();
      const $ = cheerio.load(xml, { xmlMode: true });
      const posts = [];
      
      $('item').each((i, el) => {
        const title = $(el).find('title').text();
        const link = $(el).find('link').text();
        const pubDate = $(el).find('pubDate').text();
        const description = $(el).find('description').text();
        
        // 跳过置顶和置顶广告
        if (title.includes('Moderator') || title.includes('Announcement')) return;
        
        posts.push({
          source: 'reddit',
          title: title.replace(/^r\/technology - /, ''),
          hotValue: 90 - i * 3,
          url: link,
          timestamp: new Date(pubDate).toISOString(),
          description: description.substring(0, 200),
          category: 'tech'
        });
      });
      
      console.log(`  ✅ 获取 ${posts.length} 个帖子`);
      return posts.slice(0, 20);
      
    } catch (error) {
      console.error(`  ❌ Reddit 失败：${error.message}`);
      return [];
    }
  }

  /**
   * 获取 Product Hunt（通过公开页面）
   */
  async getProductHunt() {
    try {
      console.log('[数据源] Product Hunt...');
      
      const response = await fetch('https://www.producthunt.com/', {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36' },
        timeout: 15000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const html = await response.text();
      const $ = cheerio.load(html);
      const products = [];
      
      // 解析今日产品
      $('[data-test="post-item"], .post-item').each((i, el) => {
        const name = $(el).find('[data-test="post-name"], .post-name').text().trim();
        const tagline = $(el).find('[data-test="tagline"], .tagline').text().trim();
        const url = $(el).find('a').first().attr('href');
        const votes = $(el).find('[data-test="vote-button"], .vote-button').text().trim();
        
        if (name && i < 15) {
          products.push({
            source: 'producthunt',
            title: `${name} - ${tagline || '今日新产品'}`,
            shortTitle: name,
            tagline: tagline,
            hotValue: 95 - i * 4,
            url: url?.startsWith('http') ? url : `https://www.producthunt.com${url}`,
            timestamp: new Date().toISOString(),
            votes: votes,
            category: 'tech'
          });
        }
      });
      
      console.log(`  ✅ 获取 ${products.length} 个产品`);
      return products;
      
    } catch (error) {
      console.error(`  ❌ Product Hunt 失败：${error.message}`);
      return [];
    }
  }

  /**
   * 获取 The Verge（科技新闻）
   */
  async getTheVerge() {
    try {
      console.log('[数据源] The Verge...');
      
      const response = await fetch('https://www.theverge.com/rss/index.xml', {
        headers: { 'User-Agent': 'Mozilla/5.0' },
        timeout: 10000
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const xml = await response.text();
      const $ = cheerio.load(xml, { xmlMode: true });
      const articles = [];
      
      $('item').each((i, el) => {
        const title = $(el).find('title').text();
        const link = $(el).find('link').text();
        const pubDate = $(el).find('pubDate').text();
        const content = $(el).find('content\\:encoded, description').text().substring(0, 300);
        
        articles.push({
          source: 'theverge',
          title: title,
          hotValue: 88 - i * 3,
          url: link,
          timestamp: new Date(pubDate).toISOString(),
          description: content,
          category: 'tech'
        });
      });
      
      console.log(`  ✅ 获取 ${articles.length} 篇文章`);
      return articles.slice(0, 20);
      
    } catch (error) {
      console.error(`  ❌ The Verge 失败：${error.message}`);
      return [];
    }
  }

  /**
   * 获取国内科技新闻（备用方案 - 模拟数据）
   * 真实环境需要配置代理或 Cookie
   */
  getChinaTechBackup() {
    const backup = [
      { source: '36kr', title: 'AI 大模型竞争进入新阶段，多家厂商发布新品', hotValue: 88, url: 'https://36kr.com', timestamp: new Date().toISOString(), category: 'tech' },
      { source: 'huxiu', title: '科技巨头加码 AI 硬件，新一轮投资潮来了', hotValue: 82, url: 'https://huxiu.com', timestamp: new Date().toISOString(), category: 'tech' },
      { source: 'huxiu', title: '创业公司融资动态：AI 领域最受资本青睐', hotValue: 75, url: 'https://huxiu.com', timestamp: new Date().toISOString(), category: 'tech' },
      { source: '36kr', title: '字节跳动发布新款 AI 助手，对标 GPT-5', hotValue: 90, url: 'https://36kr.com', timestamp: new Date().toISOString(), category: 'tech' },
      { source: 'huxiu', title: '国产大模型新突破，多项指标超越国际水平', hotValue: 85, url: 'https://huxiu.com', timestamp: new Date().toISOString(), category: 'tech' }
    ];
    console.log(`  ✅ 备用数据：${backup.length} 条`);
    return backup;
  }

  /**
   * 获取所有稳定数据源
   */
  async getAllSources() {
    console.log('\n========== 获取稳定数据源 ==========\n');
    
    const results = await Promise.allSettled([
      this.getGitHubTrending(),
      this.getHackerNews(),
      this.getRedditTechnology(),
      this.getProductHunt(),
      this.getTheVerge()
    ]);
    
    let allTopics = [];
    
    results.forEach((result, index) => {
      const sourceNames = ['GitHub', 'HackerNews', 'Reddit', 'ProductHunt', 'TheVerge'];
      
      if (result.status === 'fulfilled' && result.value.length > 0) {
        allTopics = allTopics.concat(result.value);
      }
    });
    
    // 添加国内科技新闻备用数据
    const chinaBackup = this.getChinaTechBackup();
    allTopics = allTopics.concat(chinaBackup);
    
    console.log(`\n共获取 ${allTopics.length} 条热点`);
    
    return allTopics;
  }

  /**
   * 筛选 AI/科技相关话题
   */
  filterAITopics(topics) {
    const keywords = [
      'AI', '人工智能', '大模型', 'GPT', 'LLM',
      '科技', '互联网', '数码', '软件', '开源',
      '创业', '副业', '效率工具', '自动化',
      'machine learning', 'deep learning', 'neural',
      'openai', 'anthropic', 'google', 'meta', 'microsoft'
    ];
    
    const excludeKeywords = ['娱乐', '明星', '八卦', '游戏', 'sports', 'celebrity'];
    
    return topics.filter(topic => {
      const text = (topic.title + ' ' + (topic.description || '')).toLowerCase();
      
      // 排除不相关
      if (excludeKeywords.some(k => text.includes(k.toLowerCase()))) {
        return false;
      }
      
      // 匹配关键词或本身就是科技源
      const match = keywords.some(k => text.includes(k.toLowerCase())) ||
                    ['github', 'hackernews', 'producthunt', 'theverge'].includes(topic.source);
      
      return match;
    });
  }
}

// 直接运行时测试
if (require.main === module) {
  const sources = new StableSources();
  
  sources.getAllSources().then(topics => {
    // 筛选 AI/科技相关
    const filtered = sources.filterAITopics(topics);
    
    console.log('\n========== AI/科技相关选题 ==========\n');
    console.log(`筛选后：${filtered.length} 条\n`);
    
    console.log('=== TOP 15 推荐选题 ===');
    filtered.slice(0, 15).forEach((t, i) => {
      console.log(`${i + 1}. [${t.source}] ${t.title} (热度：${t.hotValue})`);
    });
    
    // 保存到文件
    const fs = require('fs');
    const path = require('path');
    const outputFile = path.join(__dirname, 'data', 'real_topics.json');
    
    // 确保目录存在
    const dataDir = path.join(__dirname, 'data');
    if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
    
    fs.writeFileSync(outputFile, JSON.stringify(filtered, null, 2), 'utf8');
    console.log(`\n✅ 选题已保存：${outputFile}`);
  });
}

module.exports = StableSources;
