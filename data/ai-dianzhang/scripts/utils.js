#!/usr/bin/env node
/**
 * AI店长 - 工具函数
 * 封装搜索和数据提取的通用方法
 */

/**
 * 模拟 web_search（实际由 OpenClaw 的 web_search 工具执行）
 * 这里提供搜索查询的构建逻辑
 */
function buildSearchQueries(keyword, options = {}) {
  const queries = [];
  const platforms = options.platforms || ['taobao', 'pdd'];

  // 竞品搜索
  if (platforms.includes('taobao')) {
    queries.push({
      platform: 'taobao',
      query: `${keyword} site:taobao.com OR site:tmall.com 销量 价格`,
      purpose: '淘宝/天猫竞品'
    });
  }

  if (platforms.includes('pdd')) {
    queries.push({
      platform: 'pdd',
      query: `${keyword} 拼多多 热销 价格 销量`,
      purpose: '拼多多竞品'
    });
  }

  if (platforms.includes('alibaba')) {
    queries.push({
      platform: 'alibaba',
      query: `${keyword} site:1688.com 工厂 批发价`,
      purpose: '1688货源'
    });
  }

  if (platforms.includes('xiaohongshu')) {
    queries.push({
      platform: 'xiaohongshu',
      query: `${keyword} 小红书 种草 推荐 测评`,
      purpose: '小红书口碑'
    });
  }

  // 趋势搜索
  if (options.includeTrend) {
    queries.push({
      platform: 'trend',
      query: `${keyword} 2026 趋势 市场规模 增长`,
      purpose: '市场趋势'
    });
  }

  // 差评分析
  if (options.includeReviews) {
    queries.push({
      platform: 'reviews',
      query: `${keyword} 差评 缺点 问题 吐槽`,
      purpose: '差评痛点'
    });
  }

  return queries;
}

/**
 * 从搜索结果中提取价格信息
 */
function extractPrices(text) {
  if (!text) return [];
  const patterns = [
    /¥\s*([\d,]+\.?\d*)/g,
    /(\d+\.?\d*)\s*元/g,
    /价格[：:]\s*([\d,]+\.?\d*)/g,
    /售价[：:]\s*([\d,]+\.?\d*)/g
  ];

  const prices = new Set();
  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const price = parseFloat(match[1].replace(',', ''));
      if (price > 0 && price < 1000000) {
        prices.add(price);
      }
    }
  }

  return [...prices].sort((a, b) => a - b);
}

/**
 * 从文本中提取关键词频率
 */
function extractKeywords(texts, minLength = 2, topN = 20) {
  // 停用词
  const stopWords = new Set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
    '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
    '自己', '这', '他', '她', '它', '们', '那', '些', '什么', '怎么', '如何',
    '可以', '这个', '那个', '还是', '或者', '但是', '因为', '所以', '如果',
    '包邮', '正品', '新款', '热卖', '特价', '促销', '官方', '旗舰店'
  ]);

  const wordFreq = {};
  const combined = texts.join(' ');

  // 简单分词（按非中文字符分割 + 按2-4字滑窗）
  const segments = combined
    .replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length >= minLength && !stopWords.has(w));

  segments.forEach(w => {
    wordFreq[w] = (wordFreq[w] || 0) + 1;
  });

  return Object.entries(wordFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([word, count]) => ({ word, count }));
}

/**
 * 格式化价格区间
 */
function formatPriceRange(prices) {
  if (!prices || prices.length === 0) return '暂无价格数据';
  if (prices.length === 1) return `¥${prices[0]}`;

  const min = prices[0];
  const max = prices[prices.length - 1];
  const median = prices[Math.floor(prices.length / 2)];

  return `¥${min} - ¥${max}（中位数 ¥${median}）`;
}

/**
 * 生成监控任务的 cron 配置建议
 */
function suggestCronSchedule(monitorType) {
  const schedules = {
    daily: {
      desc: '每天早上9点',
      cron: '0 9 * * *',
      tz: 'Asia/Shanghai'
    },
    twice_daily: {
      desc: '每天9点和18点',
      cron: '0 9,18 * * *',
      tz: 'Asia/Shanghai'
    },
    weekly: {
      desc: '每周一早上9点',
      cron: '0 9 * * 1',
      tz: 'Asia/Shanghai'
    },
    realtime: {
      desc: '每2小时',
      cron: '0 */2 * * *',
      tz: 'Asia/Shanghai'
    }
  };

  return schedules[monitorType] || schedules.daily;
}

module.exports = {
  buildSearchQueries,
  extractPrices,
  extractKeywords,
  formatPriceRange,
  suggestCronSchedule
};
