/**
 * 热点数据源 Pro 版
 * 使用稳定、免登录、反反爬的数据源
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// 超时设置
const TIMEOUT = 15000;

// 请求封装
function fetch(url, options = {}) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        ...(options.headers || {})
      },
      timeout: TIMEOUT
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data);
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('timeout'));
    });
  });
}

// 数据源 1: GitHub Trending（官方页面，相对稳定）
async function fetchGitHubTrending() {
  try {
    console.log('[数据源] GitHub Trending...');
    const html = await fetch('https://github.com/trending?spoken_language_code=zh');
    
    // 简单解析 HTML 提取 repo 信息
    const repos = [];
    const repoRegex = /<a href="\/([^"]+)" class="text-normal">([^<]+)<\/a>/g;
    const descRegex = /<p class="col-9 color-fg-muted my-1 pr-4">([^<]*)/g;
    const starRegex = /<a[^>]*href="\/[^"]+\/stargazers"[^>]*>([\d,]+) stargazers/g;
    
    let match;
    let index = 0;
    while ((match = repoRegex.exec(html)) !== null && index < 15) {
      const fullName = match[1];
      const name = match[2].trim();
      repos.push({
        source: 'github',
        repo: fullName,
        title: name,
        url: `https://github.com/${fullName}`,
        hotValue: 100 - index * 5
      });
      index++;
    }
    
    console.log(`  ✅ GitHub: ${repos.length} 个项目`);
    return repos;
  } catch (e) {
    console.log(`  ❌ GitHub 失败：${e.message}`);
    return [];
  }
}

// 数据源 2: Hacker News（官方 API，稳定）
async function fetchHackerNews() {
  try {
    console.log('[数据源] Hacker News...');
    const topStories = await fetch('https://hacker-news.firebaseio.com/v0/topstories.json');
    const storyIds = JSON.parse(topStories).slice(0, 30);
    
    const stories = await Promise.all(
      storyIds.map(id => 
        fetch(`https://hacker-news.firebaseio.com/v0/item/${id}.json`)
          .then(d => JSON.parse(d))
          .catch(() => null)
      )
    );
    
    const result = stories
      .filter(s => s && s.title && s.url)
      .map((s, i) => ({
        source: 'hackernews',
        title: s.title,
        url: s.url,
        score: s.score || 0,
        hotValue: Math.max(10, 100 - i * 3)
      }));
    
    console.log(`  ✅ Hacker News: ${result.length} 个故事`);
    return result;
  } catch (e) {
    console.log(`  ❌ Hacker News 失败：${e.message}`);
    return [];
  }
}

// 数据源 3: Product Hunt（RSS 源，免登录）
async function fetchProductHunt() {
  try {
    console.log('[数据源] Product Hunt (RSS)...');
    const xml = await fetch('https://www.producthunt.com/feed');
    
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    const titleRegex = /<title><!\[CDATA\[(.*?)\]\]><\/title>/;
    const linkRegex = /<link>(.*?)<\/link>/;
    
    let match;
    let count = 0;
    while ((match = itemRegex.exec(xml)) !== null && count < 10) {
      const content = match[1];
      const titleMatch = titleRegex.exec(content);
      const linkMatch = linkRegex.exec(content);
      
      if (titleMatch && linkMatch) {
        items.push({
          source: 'producthunt',
          title: titleMatch[1].replace('Product Hunt - ', ''),
          url: linkMatch[1],
          hotValue: 80 - count * 5
        });
        count++;
      }
    }
    
    console.log(`  ✅ Product Hunt: ${items.length} 个项目`);
    return items;
  } catch (e) {
    console.log(`  ❌ Product Hunt 失败：${e.message}`);
    return [];
  }
}

// 数据源 4: 36 氪（RSS 源）
async function fetch36Kr() {
  try {
    console.log('[数据源] 36 氪 (RSS)...');
    const xml = await fetch('https://36kr.com/feed');
    
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    const titleRegex = /<title><!\[CDATA\[(.*?)\]\]><\/title>/;
    const linkRegex = /<link>(.*?)<\/link>/;
    
    let match;
    let count = 0;
    while ((match = itemRegex.exec(xml)) !== null && count < 10) {
      const content = match[1];
      const titleMatch = titleRegex.exec(content);
      const linkMatch = linkRegex.exec(content);
      
      if (titleMatch && linkMatch) {
        items.push({
          source: '36kr',
          title: titleMatch[1],
          url: linkMatch[1],
          hotValue: 85 - count * 5
        });
        count++;
      }
    }
    
    console.log(`  ✅ 36 氪：${items.length} 篇文章`);
    return items;
  } catch (e) {
    console.log(`  ❌ 36 氪失败：${e.message}`);
    return [];
  }
}

// 数据源 5: 虎嗅（RSS 源）
async function fetchHuxiu() {
  try {
    console.log('[数据源] 虎嗅 (RSS)...');
    const xml = await fetch('https://www.huxiu.com/article/rss.xml');
    
    const items = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    const titleRegex = /<title><!\[CDATA\[(.*?)\]\]><\/title>/;
    const linkRegex = /<link>(.*?)<\/link>/;
    
    let match;
    let count = 0;
    while ((match = itemRegex.exec(xml)) !== null && count < 10) {
      const content = match[1];
      const titleMatch = titleRegex.exec(content);
      const linkMatch = linkRegex.exec(content);
      
      if (titleMatch && linkMatch) {
        items.push({
          source: 'huxiu',
          title: titleMatch[1],
          url: linkMatch[1],
          hotValue: 80 - count * 5
        });
        count++;
      }
    }
    
    console.log(`  ✅ 虎嗅：${items.length} 篇文章`);
    return items;
  } catch (e) {
    console.log(`  ❌ 虎嗅失败：${e.message}`);
    return [];
  }
}

// 数据源 6: 知乎热榜（第三方 API，免登录）
async function fetchZhihu() {
  try {
    console.log('[数据源] 知乎热榜 (第三方 API)...');
    const data = await fetch('https://api.zhihu.com/topstory/hot-list?limit=20', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
      }
    });
    const json = JSON.parse(data);
    
    const items = (json.data || []).map((item, i) => ({
      source: 'zhihu',
      title: item.target.title,
      url: `https://www.zhihu.com/question/${item.target.id}`,
      hotValue: 95 - i * 4,
      detail: item.target.excerpt
    }));
    
    console.log(`  ✅ 知乎：${items.length} 个话题`);
    return items;
  } catch (e) {
    console.log(`  ❌ 知乎失败：${e.message}`);
    return [];
  }
}

// 数据源 7: 微博热搜（第三方 API）
async function fetchWeibo() {
  try {
    console.log('[数据源] 微博热搜 (第三方 API)...');
    const data = await fetch('https://weibo.com/ajax/side/hotSearch');
    const json = JSON.parse(data);
    
    const items = (json.data.realtime || []).slice(0, 20).map((item, i) => ({
      source: 'weibo',
      title: item.word,
      url: `https://s.weibo.com/weibo?q=${encodeURIComponent(item.word)}`,
      hotValue: 100 - i * 5,
      num: item.num
    }));
    
    console.log(`  ✅ 微博：${items.length} 个热搜`);
    return items;
  } catch (e) {
    console.log(`  ❌ 微博失败：${e.message}`);
    return [];
  }
}

// 筛选 AI/科技相关
function filterTechTopics(topics) {
  const keywords = [
    'AI', '人工智能', '大模型', 'LLM', 'GPT', 'Claude', 'Gemini',
    '代码', '编程', '开发', 'GitHub', '开源', '软件',
    '科技', '互联网', '数字', '智能', '算法', '数据',
    'Agent', '代理', '自动化', '机器人', 'RPA',
    '创业', '融资', '投资', '产品', '上线', '发布'
  ];
  
  return topics.filter(t => {
    const text = (t.title + ' ' + (t.detail || '')).toLowerCase();
    return keywords.some(k => text.includes(k.toLowerCase()) || text.includes(k));
  });
}

// 主函数
async function main() {
  console.log('========== 热点数据源 Pro 版 ==========');
  console.log(`时间：${new Date().toISOString()}`);
  console.log('');
  
  const allTopics = [];
  
  // 并行获取所有数据源
  const results = await Promise.allSettled([
    fetchGitHubTrending(),
    fetchHackerNews(),
    fetchProductHunt(),
    fetch36Kr(),
    fetchHuxiu(),
    fetchZhihu(),
    fetchWeibo()
  ]);
  
  results.forEach(r => {
    if (r.status === 'fulfilled' && Array.isArray(r.value)) {
      allTopics.push(...r.value);
    }
  });
  
  console.log('');
  console.log(`共获取 ${allTopics.length} 条热点`);
  
  // 筛选科技相关
  const techTopics = filterTechTopics(allTopics);
  console.log(`筛选后：${techTopics.length} 条 AI/科技相关`);
  console.log('');
  
  // 排序
  techTopics.sort((a, b) => b.hotValue - a.hotValue);
  
  // 显示 TOP 15
  console.log('=== TOP 15 推荐选题 ===');
  techTopics.slice(0, 15).forEach((t, i) => {
    console.log(`${i + 1}. [${t.source}] ${t.title} (热度：${t.hotValue})`);
  });
  
  // 保存到文件
  const dataDir = path.join(__dirname, 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filePath = path.join(dataDir, `topics_${timestamp}.json`);
  
  fs.writeFileSync(filePath, JSON.stringify({
    fetchedAt: new Date().toISOString(),
    total: allTopics.length,
    techCount: techTopics.length,
    topics: techTopics
  }, null, 2), 'utf8');
  
  // 同时更新 latest_topics.json（方便其他脚本读取）
  const latestPath = path.join(dataDir, 'latest_topics.json');
  fs.writeFileSync(latestPath, JSON.stringify({
    fetchedAt: new Date().toISOString(),
    total: allTopics.length,
    techCount: techTopics.length,
    topics: techTopics
  }, null, 2), 'utf8');
  
  console.log('');
  console.log(`✅ 选题已保存：${filePath}`);
  console.log(`✅ 最新数据：${latestPath}`);
  
  return techTopics;
}

// 运行
main().catch(console.error);
