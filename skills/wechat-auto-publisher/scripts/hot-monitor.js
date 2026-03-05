/**
 * 热点监控模块
 * 监控各大平台热榜，筛选出 AI/科技相关话题
 */

const fetch = require('node-fetch');
const config = require('./config');
const fs = require('fs');
const path = require('path');
const RealSources = require('./real-sources');

class HotMonitor {
  constructor() {
    this.topics = [];
    this.dataDir = path.join(__dirname, config.storage.dataDir);
    
    // 确保数据目录存在
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
  }

  /**
   * 获取微博热搜
   */
  async getWeiboHot() {
    try {
      console.log('[监控] 获取微博热搜...');
      // 注意：微博热搜需要处理反爬，这里用简化版
      // 实际使用可能需要代理或 Cookie
      const response = await fetch(config.sources.weibo.url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      
      if (!response.ok) {
        throw new Error(`微博热搜 HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // 解析热搜数据
      const hotList = data.data?.realtime || [];
      
      return hotList.slice(0, 20).map((item, index) => ({
        source: 'weibo',
        title: item.note || item.word,
        hotValue: item.num || (100 - index * 5),
        url: `https://s.weibo.com/weibo?q=${encodeURIComponent(item.note || item.word)}`,
        timestamp: new Date().toISOString()
      }));
      
    } catch (error) {
      console.error('[监控] 微博热搜获取失败:', error.message);
      // 返回模拟数据用于测试
      return this.getMockWeiboHot();
    }
  }

  /**
   * 获取知乎热榜
   */
  async getZhihuHot() {
    try {
      console.log('[监控] 获取知乎热榜...');
      
      const response = await fetch(config.sources.zhihu.url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      
      if (!response.ok) {
        throw new Error(`知乎热榜 HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      return data.data?.slice(0, 20).map((item, index) => ({
        source: 'zhihu',
        title: item.target?.title || item.title,
        hotValue: item.target?.answer_count || (100 - index * 5),
        url: item.target?.url || item.url,
        timestamp: new Date().toISOString()
      }));
      
    } catch (error) {
      console.error('[监控] 知乎热榜获取失败:', error.message);
      return this.getMockZhihuHot();
    }
  }

  /**
   * 获取虎嗅科技新闻
   */
  async getHuxiuNews() {
    try {
      console.log('[监控] 获取虎嗅新闻...');
      // 虎嗅需要解析 HTML，这里简化处理
      return this.getMockHuxiuNews();
    } catch (error) {
      console.error('[监控] 虎嗅新闻获取失败:', error.message);
      return this.getMockHuxiuNews();
    }
  }

  /**
   * 筛选相关话题
   */
  filterTopics(allTopics) {
    const { keywords, excludeKeywords, minHotValue } = config.topics;
    
    return allTopics.filter(topic => {
      const title = topic.title.toLowerCase();
      
      // 排除不相关的话题
      if (excludeKeywords.some(k => title.includes(k.toLowerCase()))) {
        return false;
      }
      
      // 匹配关键词
      const match = keywords.some(k => title.includes(k.toLowerCase()));
      
      // 热度过滤
      const hotEnough = topic.hotValue >= minHotValue;
      
      return match && hotEnough;
    });
  }

  /**
   * 主监控流程
   */
  async monitor(useRealSources = true) {
    console.log('\n========== 热点监控开始 ==========');
    console.log(`时间：${new Date().toLocaleString('zh-CN')}`);
    console.log(`模式：${useRealSources ? '真实数据源' : '模拟数据'}\n`);
    console.log('================================\n');
    
    let allTopics = [];
    
    if (useRealSources) {
      // 使用真实数据源
      const realSources = new RealSources();
      allTopics = await realSources.getAllSources();
    }
    
    // 如果真实数据源失败或用户选择模拟数据
    if (!useRealSources || allTopics.length === 0) {
      console.log('[监控] 真实数据源获取失败，使用模拟数据...\n');
      
      if (config.sources.weibo.enabled) {
        const weiboTopics = await this.getWeiboHot();
        allTopics.push(...weiboTopics);
      }
      
      if (config.sources.zhihu.enabled) {
        const zhihuTopics = await this.getZhihuHot();
        allTopics.push(...zhihuTopics);
      }
      
      if (config.sources.huxiu.enabled) {
        const huxiuTopics = await this.getHuxiuNews();
        allTopics.push(...huxiuTopics);
      }
    }
    
    console.log(`\n[监控] 共获取 ${allTopics.length} 个热点话题`);
    
    // 筛选相关话题
    const filteredTopics = this.filterTopics(allTopics);
    console.log(`[监控] 筛选后剩余 ${filteredTopics.length} 个相关话题\n`);
    
    // 保存结果
    this.topics = filteredTopics;
    this.saveTopics(filteredTopics);
    
    // 显示前 10 个
    console.log('=== 推荐选题 TOP 10 ===');
    filteredTopics.slice(0, 10).forEach((topic, i) => {
      console.log(`${i + 1}. [${topic.source}] ${topic.title} (热度：${topic.hotValue})`);
    });
    
    return filteredTopics;
  }

  /**
   * 保存选题到文件
   */
  saveTopics(topics) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filePath = path.join(this.dataDir, `topics_${timestamp}.json`);
    fs.writeFileSync(filePath, JSON.stringify(topics, null, 2), 'utf8');
    console.log(`[监控] 选题已保存：${filePath}`);
  }

  /**
   * 加载最新选题
   */
  loadLatestTopics() {
    const files = fs.readdirSync(this.dataDir)
      .filter(f => f.startsWith('topics_') && f.endsWith('.json'))
      .sort()
      .reverse();
    
    if (files.length === 0) {
      return [];
    }
    
    const filePath = path.join(this.dataDir, files[0]);
    const content = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(content);
  }

  // ========== 模拟数据（用于测试）==========
  
  getMockWeiboHot() {
    return [
      { source: 'weibo', title: 'GPT-5 发布，性能大幅提升', hotValue: 95, url: '#', timestamp: new Date().toISOString() },
      { source: 'weibo', title: 'AI 写代码效率超过程序员', hotValue: 88, url: '#', timestamp: new Date().toISOString() },
      { source: 'weibo', title: '某明星离婚', hotValue: 99, url: '#', timestamp: new Date().toISOString() },
      { source: 'weibo', title: '国产大模型新突破', hotValue: 76, url: '#', timestamp: new Date().toISOString() }
    ];
  }

  getMockZhihuHot() {
    return [
      { source: 'zhihu', title: '如何评价最新的大语言模型？', hotValue: 92, url: '#', timestamp: new Date().toISOString() },
      { source: 'zhihu', title: 'AI 会取代哪些工作？', hotValue: 85, url: '#', timestamp: new Date().toISOString() },
      { source: 'zhihu', title: '2026 年有哪些值得关注的科技趋势？', hotValue: 78, url: '#', timestamp: new Date().toISOString() }
    ];
  }

  getMockHuxiuNews() {
    return [
      { source: 'huxiu', title: 'OpenAI 发布新模型，多模态能力再升级', hotValue: 90, url: '#', timestamp: new Date().toISOString() },
      { source: 'huxiu', title: '字节跳动布局 AI 硬件', hotValue: 82, url: '#', timestamp: new Date().toISOString() },
      { source: 'huxiu', title: 'AI 创业公司融资热潮', hotValue: 70, url: '#', timestamp: new Date().toISOString() }
    ];
  }
}

// 直接运行时执行监控
if (require.main === module) {
  const monitor = new HotMonitor();
  monitor.monitor().then(topics => {
    console.log('\n监控完成！');
  });
}

module.exports = HotMonitor;
