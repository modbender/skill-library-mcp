#!/usr/bin/env node
/**
 * AI店长 - 竞品监控模块
 * 搜索电商平台公开数据，分析竞品情况
 */

const { searchWeb, fetchPage, extractProducts } = require('./utils');

// 平台搜索模板
const PLATFORM_SEARCH = {
  taobao: {
    name: '淘宝/天猫',
    searchUrl: (q) => `${q} site:taobao.com OR site:tmall.com`,
    pricePattern: /¥[\d.]+/g
  },
  pdd: {
    name: '拼多多',
    searchUrl: (q) => `${q} site:pinduoduo.com OR site:yangkeduo.com`,
    pricePattern: /¥[\d.]+/g
  },
  alibaba: {
    name: '1688',
    searchUrl: (q) => `${q} site:1688.com 批发`,
    pricePattern: /¥[\d.]+/g
  },
  xiaohongshu: {
    name: '小红书',
    searchUrl: (q) => `${q} site:xiaohongshu.com OR site:xhslink.com`,
    pricePattern: null
  },
  douyin: {
    name: '抖音电商',
    searchUrl: (q) => `${q} 抖音 电商 销量`,
    pricePattern: /¥[\d.]+/g
  }
};

/**
 * 竞品搜索
 * @param {string} keyword - 商品关键词
 * @param {string[]} platforms - 要搜索的平台 ['taobao','pdd','alibaba']
 * @param {object} options - 额外选项
 */
async function searchCompetitors(keyword, platforms = ['taobao', 'pdd'], options = {}) {
  const results = {};

  for (const platform of platforms) {
    const config = PLATFORM_SEARCH[platform];
    if (!config) continue;

    try {
      const query = config.searchUrl(keyword);
      const searchResults = await searchWeb(query, { count: 10 });

      results[platform] = {
        platform: config.name,
        keyword,
        results: searchResults.map(r => ({
          title: r.title,
          url: r.url,
          snippet: r.description,
          prices: r.description ? (r.description.match(config.pricePattern) || []) : []
        })),
        searchedAt: new Date().toISOString()
      };
    } catch (err) {
      results[platform] = { platform: config.name, error: err.message };
    }
  }

  return results;
}

/**
 * 分析竞品数据，生成报告
 */
function analyzeCompetitors(searchData) {
  const report = {
    summary: {},
    priceRange: {},
    keywords: [],
    opportunities: []
  };

  for (const [platform, data] of Object.entries(searchData)) {
    if (data.error) continue;

    // 提取所有价格
    const allPrices = data.results
      .flatMap(r => r.prices)
      .map(p => parseFloat(p.replace('¥', '')))
      .filter(p => !isNaN(p) && p > 0)
      .sort((a, b) => a - b);

    if (allPrices.length > 0) {
      report.priceRange[platform] = {
        min: allPrices[0],
        max: allPrices[allPrices.length - 1],
        median: allPrices[Math.floor(allPrices.length / 2)],
        count: allPrices.length
      };
    }

    // 提取高频关键词
    const titleWords = data.results
      .map(r => r.title)
      .join(' ')
      .replace(/[^\u4e00-\u9fa5a-zA-Z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length >= 2);

    const wordFreq = {};
    titleWords.forEach(w => { wordFreq[w] = (wordFreq[w] || 0) + 1; });

    const topWords = Object.entries(wordFreq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([word, count]) => ({ word, count }));

    report.keywords.push({ platform: data.platform, topWords });

    report.summary[platform] = {
      platform: data.platform,
      resultCount: data.results.length,
      priceRange: report.priceRange[platform] || null
    };
  }

  return report;
}

/**
 * 生成竞品监控的 LLM 分析 prompt
 */
function buildAnalysisPrompt(keyword, searchData, analysisReport) {
  const platformSummaries = Object.entries(searchData)
    .filter(([_, d]) => !d.error)
    .map(([platform, data]) => {
      const prices = analysisReport.priceRange[platform];
      const priceStr = prices
        ? `价格区间 ¥${prices.min}-${prices.max}，中位数 ¥${prices.median}`
        : '价格数据不足';

      const titles = data.results.slice(0, 5).map(r => `  - ${r.title}`).join('\n');

      return `【${data.platform}】${priceStr}\n热门商品标题：\n${titles}`;
    })
    .join('\n\n');

  const keywordStr = analysisReport.keywords
    .map(k => `${k.platform}: ${k.topWords.slice(0, 10).map(w => w.word).join('、')}`)
    .join('\n');

  return `你是一个资深电商运营专家。请根据以下竞品数据，为关键词"${keyword}"生成竞品分析报告。

## 搜索数据

${platformSummaries}

## 高频关键词
${keywordStr}

## 请分析以下内容：

1. **市场概况**：这个品类的整体竞争程度、价格带分布
2. **头部竞品分析**：排名靠前的商品有什么共同特点
3. **差异化机会**：从标题和价格中发现的市场空白点
4. **定价建议**：建议的价格区间和定价策略
5. **关键词建议**：标题中应该包含的核心关键词
6. **风险提示**：需要注意的竞争风险

请用简洁的中文回答，适合电商卖家阅读。`;
}

module.exports = {
  PLATFORM_SEARCH,
  searchCompetitors,
  analyzeCompetitors,
  buildAnalysisPrompt
};
