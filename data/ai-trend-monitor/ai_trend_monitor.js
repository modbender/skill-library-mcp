#!/usr/bin/env node
/**
 * AI Trend Monitor - v1.0 完整版
 * 
 * 功能：
 * 1. 实时监控多个渠道（GitHub、Reddit、Twitter/X、小红书、新闻）
 * 2. 提取具体帖子/文章URL（非首页）
 * 3. 重大新闻实时检测并直接推送
 * 4. 定时汇总推送（9:00、13:00、19:00）
 * 5. 飞书卡片格式：分渠道表格，完整文本，可跳转链接
 * 
 * 使用方法：
 * - node ai_trend_monitor.js realtime    # 启动实时监控（每10分钟）
 * - node ai_trend_monitor.js once        # 单次检测重大新闻
 * - node ai_trend_monitor.js scheduled   # 定时汇总推送
 */

const WEBHOOK_MARKET = process.env.WEBHOOK_MARKET || 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx';
const WEBHOOK_TECH = process.env.WEBHOOK_TECH || 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx';

// ==================== 配置 ====================

const CONFIG = {
  // 监控渠道
  channels: ['GitHub', 'Reddit', 'Twitter', '小红书', '新闻'],
  
  // 实时检测频率（毫秒）
  realtimeInterval: 10 * 60 * 1000, // 10分钟
  
  // 重大新闻判定标准
  majorNewsCriteria: {
    funding: 100000000,      // 1亿美元
    stockChange: 5,          // 股价涨跌5%
    keyPeople: ['sam altman', 'elon musk', '马斯克', 'andrej karpathy', '黄仁勋'],
    keyCompanies: ['openai', 'google', 'anthropic', 'meta', 'xai', 'deepseek', '英伟达', 'nvidia'],
    majorEvents: ['发布', '推出', '收购', '合并', '突破', '开源']
  }
};

// ==================== URL提取 ====================

/**
 * 从搜索结果中提取具体URL
 */
function extractSpecificUrl(result, channel) {
  switch (channel) {
    case 'GitHub':
      return extractGitHubSpecificUrl(result);
    case 'Reddit':
      return extractRedditSpecificUrl(result);
    case 'Twitter':
    case 'X':
      return extractTwitterSpecificUrl(result);
    case '小红书':
      return extractXiaohongshuSpecificUrl(result);
    default:
      return result.url || result.link;
  }
}

function extractGitHubSpecificUrl(result) {
  const baseUrl = result.url || result.link || '';
  
  if (baseUrl.includes('/releases/') || 
      baseUrl.includes('/commit/') || 
      baseUrl.includes('/issues/') ||
      baseUrl.includes('/pull/')) {
    return baseUrl;
  }
  
  const versionMatch = result.title?.match(/v?\d+\.\d+(?:\.\d+)?/) || 
                       result.summary?.match(/v?\d+\.\d+(?:\.\d+)?/);
  
  if (versionMatch) {
    const version = versionMatch[0];
    return `${baseUrl}/releases/tag/${version.startsWith('v') ? version : 'v' + version}`;
  }
  
  return baseUrl;
}

function extractRedditSpecificUrl(result) {
  if (result.url && result.url.includes('/comments/')) {
    return result.url;
  }
  
  const permalinkMatch = result.summary?.match(/\/r\/\w+\/comments\/[a-z0-9]+/);
  if (permalinkMatch) {
    return `https://www.reddit.com${permalinkMatch[0]}`;
  }
  
  return result.url || 'https://www.reddit.com/r/artificial/';
}

function extractTwitterSpecificUrl(result) {
  if (result.url && result.url.includes('/status/')) {
    return result.url;
  }
  
  const usernameMatch = result.title?.match(/@?(\w+)/);
  const username = usernameMatch ? usernameMatch[1] : 'elonmusk';
  return `https://twitter.com/${username}`;
}

function extractXiaohongshuSpecificUrl(result) {
  const noteIdMatch = result.url?.match(/explore\/([a-z0-9]{16,24})/) ||
                      result.summary?.match(/([a-z0-9]{16,24})/);
  
  if (noteIdMatch) {
    return `https://www.xiaohongshu.com/explore/${noteIdMatch[1]}`;
  }
  
  return result.url || 'https://www.xiaohongshu.com/';
}

// ==================== 搜索 ====================

/**
 * 搜索并提取具体URL
 * 实际部署时替换为真实搜索API（kimi_search）
 */
async function searchAndExtract(channel, keyword) {
  // 模拟数据 - 实际部署时替换为真实搜索
  const mockResults = {
    'GitHub': [
      {
        title: 'github-weekly-rank',
        url: 'https://github.com/OpenGithubs/github-weekly-rank',
        summary: '每周飙升榜top20，系统性整理如何搭建个人AI基础设施，涵盖模型部署、向量数据库、Agent编排与隐私控制',
        time: new Date().toISOString()
      }
    ],
    'Reddit': [
      {
        title: 'AI发布史上最伟大月份',
        url: 'https://www.reddit.com/r/artificial/comments/1xyz234/2026_february_ai_releases/',
        summary: '社区热议2月多模态系统、万亿参数模型、数字孪生等技术突破集中爆发',
        time: new Date().toISOString()
      }
    ],
    'Twitter': [
      {
        title: '@elonmusk: AI编程预言',
        url: '',
        summary: '马斯克称2026年底AI将实现直接编写二进制代码，人类对编程语言依赖大幅减弱',
        time: new Date().toISOString()
      }
    ],
    '小红书': [
      {
        title: 'AI副业月入3万教程',
        url: '',
        summary: '用户分享使用Claude+Midjourney组合做电商主图，单月收入破3万',
        time: new Date().toISOString()
      }
    ],
    '新闻': [
      {
        title: '英伟达GTC大会预告',
        url: 'https://finance.sina.com.cn/roll/2026-02-19/doc-inhninfp0450502.shtml',
        summary: '黄仁勋称将在GTC大会发布世界前所未见的产品，已准备好多款全球首见新芯片',
        time: new Date().toISOString()
      }
    ]
  };
  
  const results = mockResults[channel] || [];
  
  return results.map(r => ({
    ...r,
    specificUrl: extractSpecificUrl(r, channel)
  }));
}

// ==================== 重大新闻判定 ====================

function isMajorNews(result) {
  const text = `${result.title} ${result.summary}`.toLowerCase();
  const criteria = CONFIG.majorNewsCriteria;
  
  // 1. 融资金额
  const fundingMatch = text.match(/(\d+(?:\.\d+)?)\s*亿(?:美元|美金|usd)/);
  if (fundingMatch && parseFloat(fundingMatch[1]) >= criteria.funding / 100000000) {
    return { isMajor: true, reason: `融资 ${fundingMatch[1]} 亿美元` };
  }
  
  // 2. 关键人物
  for (const person of criteria.keyPeople) {
    if (text.includes(person.toLowerCase())) {
      return { isMajor: true, reason: `关键人物: ${person}` };
    }
  }
  
  // 3. 关键公司 + 重大事件
  for (const company of criteria.keyCompanies) {
    if (text.includes(company.toLowerCase())) {
      for (const event of criteria.majorEvents) {
        if (text.includes(event)) {
          return { isMajor: true, reason: `${company} ${event}` };
        }
      }
    }
  }
  
  // 4. 股价波动
  const stockMatch = text.match(/(?:涨|跌)(\d+(?:\.\d+)?)%/);
  if (stockMatch && parseFloat(stockMatch[1]) >= criteria.stockChange) {
    return { isMajor: true, reason: `股价波动 ${stockMatch[1]}%` };
  }
  
  return { isMajor: false, reason: '' };
}

// ==================== 消息发送 ====================

/**
 * 发送重大新闻实时推送 - 直接发送，不区分渠道
 */
async function sendMajorNewsDirect(majorNewsList) {
  if (majorNewsList.length === 0) return;
  
  let message = `🔥🔥🔥 重大新闻实时推送\n\n`;
  
  for (let i = 0; i < majorNewsList.length; i++) {
    const news = majorNewsList[i];
    message += `${i + 1}. **${news.title}**\n`;
    message += `   📝 概述：${news.summary}\n`;
    message += `   🕐 时间：${news.time}\n`;
    message += `   💡 影响：${news.impact}\n`;
    message += `   🔗 链接：${news.url}\n\n`;
  }
  
  message += `推送时间：${new Date().toLocaleString('zh-CN')}`;
  
  // 实际部署时调用OpenClaw消息发送API
  // 示例: await openclaw.message.send({ text: message });
  console.log('\n========== 重大新闻实时推送 ==========');
  console.log(message);
  console.log('=====================================\n');
  
  return message;
}

/**
 * 发送定时汇总 - 通过webhook，分渠道表格
 */
async function sendScheduledSummary(webhook, title, channelData, isMajor = false) {
  const template = isMajor ? 'red' : 'blue';
  const elements = [];
  
  for (const [channelName, rows] of Object.entries(channelData)) {
    if (rows.length === 0) continue;
    
    elements.push({
      tag: 'div',
      text: { tag: 'lark_md', content: `**📡 ${channelName}**` }
    });
    
    elements.push({
      tag: 'column_set',
      flex_mode: 'none',
      background_style: 'grey',
      columns: [
        { tag: 'column', width: '120px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: '**标题**' } }] },
        { tag: 'column', width: '250px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: '**概述**' } }] },
        { tag: 'column', width: '110px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: '**时间**' } }] },
        { tag: 'column', width: '200px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: '**影响分析**' } }] },
        { tag: 'column', width: '90px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: '**链接**' } }] }
      ]
    });
    
    for (const row of rows) {
      elements.push({
        tag: 'column_set',
        flex_mode: 'none',
        background_style: 'default',
        columns: [
          { tag: 'column', width: '120px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: row.title } }] },
          { tag: 'column', width: '250px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: row.summary } }] },
          { tag: 'column', width: '110px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: row.time } }] },
          { tag: 'column', width: '200px', elements: [{ tag: 'div', text: { tag: 'lark_md', content: row.impact } }] },
          { tag: 'column', width: '90px', elements: [{ tag: 'button', text: { tag: 'plain_text', content: '查看' }, type: 'primary', url: row.url }] }
        ]
      });
    }
    
    elements.push({ tag: 'hr' });
  }
  
  elements.push({
    tag: 'note',
    elements: [{ tag: 'plain_text', content: `推送时间：${new Date().toLocaleString('zh-CN')}` }]
  });

  const card = {
    msg_type: 'interactive',
    card: { header: { title: { tag: 'plain_text', content: title }, template: template }, elements: elements }
  };

  try {
    const response = await fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(card)
    });
    return await response.json();
  } catch (error) {
    console.error('发送失败:', error);
    return null;
  }
}

// ==================== 主逻辑 ====================

/**
 * 实时重大新闻检测
 */
async function monitorMajorNews() {
  console.log('开始实时重大新闻监控...\n');
  
  const majorNewsList = [];
  
  for (const channel of CONFIG.channels) {
    console.log(`检测 ${channel}...`);
    const results = await searchAndExtract(channel, 'AI');
    
    for (const result of results) {
      const check = isMajorNews(result);
      if (check.isMajor) {
        majorNewsList.push({
          title: result.title,
          summary: result.summary,
          time: new Date().toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
          impact: `【重大】${check.reason}`,
          url: result.specificUrl || result.url
        });
        console.log(`  🔥 发现重大新闻: ${result.title} (${check.reason})`);
      }
    }
  }
  
  if (majorNewsList.length > 0) {
    console.log(`\n发现 ${majorNewsList.length} 条重大新闻，立即推送...`);
    await sendMajorNewsDirect(majorNewsList);
    console.log('重大新闻推送完成');
  } else {
    console.log('未发现重大新闻');
  }
  
  return majorNewsList.length;
}

/**
 * 定时汇总推送
 */
async function runScheduledPush() {
  console.log('开始定时汇总推送...\n');
  
  const allData = {};
  
  for (const channel of CONFIG.channels) {
    console.log(`搜索 ${channel}...`);
    const results = await searchAndExtract(channel, 'AI');
    
    allData[channel] = results.map(r => ({
      title: r.title.substring(0, 30),
      summary: r.summary,
      time: new Date(r.time).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
      impact: '待分析',
      url: r.specificUrl || r.url
    }));
    
    console.log(`  找到 ${results.length} 条`);
  }
  
  // 发送市场趋势
  await sendScheduledSummary(
    WEBHOOK_MARKET,
    '📊 市场趋势监控 | 定时汇总',
    allData,
    false
  );
  
  console.log('\n定时汇总推送完成');
}

/**
 * 启动实时监控
 */
async function startRealtimeMonitor() {
  console.log('启动 AI Trend Monitor 实时监控系统');
  console.log(`检测频率: 每${CONFIG.realtimeInterval / 60000}分钟\n`);
  
  await monitorMajorNews();
  
  setInterval(async () => {
    console.log('\n--- 定时检测 ---');
    await monitorMajorNews();
  }, CONFIG.realtimeInterval);
}

// ==================== 入口 ====================

async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'realtime';
  
  switch (mode) {
    case 'realtime':
      await startRealtimeMonitor();
      break;
    case 'once':
      const count = await monitorMajorNews();
      console.log(`\n检测完成，发现 ${count} 条重大新闻`);
      process.exit(0);
      break;
    case 'scheduled':
      await runScheduledPush();
      process.exit(0);
      break;
    default:
      console.log('AI Trend Monitor v1.0');
      console.log('用法: node ai_trend_monitor.js [realtime|once|scheduled]');
      console.log('  realtime   - 启动实时监控（每10分钟）');
      console.log('  once       - 单次检测重大新闻');
      console.log('  scheduled  - 定时汇总推送');
      process.exit(0);
  }
}

// 导出模块
module.exports = {
  CONFIG,
  extractSpecificUrl,
  isMajorNews,
  monitorMajorNews,
  runScheduledPush,
  sendMajorNewsDirect,
  sendScheduledSummary
};

// 运行
if (require.main === module) {
  main().catch(console.error);
}
