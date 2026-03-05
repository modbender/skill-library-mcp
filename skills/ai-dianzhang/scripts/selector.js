#!/usr/bin/env node
/**
 * AI店长 - 选品分析模块
 * 分析市场趋势，发现蓝海品类
 */

// 热门品类数据源
const TREND_SOURCES = {
  taobao_hot: {
    name: '淘宝热搜',
    query: (category) => `${category} 淘宝 热卖 2026 趋势 销量排行`
  },
  pdd_hot: {
    name: '拼多多爆款',
    query: (category) => `${category} 拼多多 爆款 热销 排行`
  },
  xiaohongshu_trend: {
    name: '小红书趋势',
    query: (category) => `${category} 小红书 种草 热门 趋势 2026`
  },
  alibaba_supply: {
    name: '1688货源',
    query: (category) => `${category} 1688 工厂 批发 货源 利润`
  },
  seasonal: {
    name: '季节性分析',
    query: (category) => `${category} 季节 旺季 淡季 销售周期`
  }
};

// 季节性品类参考
const SEASONAL_CATEGORIES = {
  spring: ['春装', '防晒', '踏青装备', '清洁用品', '收纳', '健身器材'],
  summer: ['防晒', '冰丝', '露营', '泳装', '驱蚊', '小风扇', '冰箱收纳'],
  autumn: ['秋装', '保温杯', '护肤', '月饼', '开学用品', '围巾'],
  winter: ['羽绒服', '暖手宝', '加绒', '年货', '圣诞', '滑雪装备', '电热毯']
};

/**
 * 生成选品分析 prompt
 * @param {string} category - 品类或方向描述
 * @param {object} options - 预算、经验等
 */
function buildSelectionPrompt(category, options = {}) {
  const budget = options.budget || '不限';
  const experience = options.experience || '新手';
  const currentMonth = new Date().getMonth() + 1;

  // 判断当前季节
  let season;
  if (currentMonth >= 3 && currentMonth <= 5) season = 'spring';
  else if (currentMonth >= 6 && currentMonth <= 8) season = 'summer';
  else if (currentMonth >= 9 && currentMonth <= 11) season = 'autumn';
  else season = 'winter';

  const seasonalItems = SEASONAL_CATEGORIES[season].join('、');

  return `你是一个资深电商选品专家，帮助卖家发现赚钱的品类。

用户情况：
- 关注方向：${category || '不确定，需要推荐'}
- 预算：${budget}
- 经验：${experience}
- 当前月份：${currentMonth}月（${season === 'spring' ? '春季' : season === 'summer' ? '夏季' : season === 'autumn' ? '秋季' : '冬季'}）

当前季节热门品类参考：${seasonalItems}

请从以下维度分析并推荐：

## 1. 市场分析
- 这个品类/方向的整体市场规模
- 竞争激烈程度（红海/蓝海）
- 利润空间预估

## 2. 推荐选品（3-5个具体产品方向）
每个推荐包含：
- 产品名称和描述
- 预估售价区间
- 预估利润率
- 目标人群
- 推荐理由
- 风险提示

## 3. 货源建议
- 1688 搜索关键词
- 预估拿货价
- 起批量建议
- 质检要点

## 4. 运营建议
- 推荐首发平台
- 定价策略
- 推广方式
- 预估回本周期

## 5. 避坑指南
- 这个品类常见的坑
- 需要注意的资质/认证
- 季节性风险

请用大白话回答，适合${experience}卖家理解。给出具体可执行的建议，不要空泛的理论。`;
}

/**
 * 生成趋势分析 prompt
 */
function buildTrendPrompt(searchResults) {
  return `你是一个电商数据分析师。根据以下搜索数据，分析当前电商市场趋势。

搜索数据：
${JSON.stringify(searchResults, null, 2)}

请分析：
1. 当前最热门的品类/产品是什么
2. 有哪些正在上升的新趋势
3. 哪些品类竞争相对较小但需求在增长（蓝海机会）
4. 近期有什么值得关注的消费趋势变化
5. 给出3个具体的选品建议

用简洁的中文回答，重点突出可操作的信息。`;
}

/**
 * 生成数据日报 prompt
 */
function buildDailyReportPrompt(keyword, todayData, yesterdayData) {
  return `你是AI店长，请生成今日的竞品监控日报。

监控关键词：${keyword}
今日数据：${JSON.stringify(todayData, null, 2)}
${yesterdayData ? `昨日数据：${JSON.stringify(yesterdayData, null, 2)}` : '（首次监控，无历史数据）'}

请生成简洁的日报，包含：

📊 **${keyword} 日报** — ${new Date().toLocaleDateString('zh-CN')}

1. **价格变动**：有无明显涨跌
2. **新品上架**：发现的新竞品
3. **热搜词变化**：关键词趋势
4. **值得关注**：任何异常或机会
5. **行动建议**：今天应该做什么

保持简洁，重点突出变化和行动项。如果没有明显变化，简单说"今日无重大变化"即可。`;
}

module.exports = {
  TREND_SOURCES,
  SEASONAL_CATEGORIES,
  buildSelectionPrompt,
  buildTrendPrompt,
  buildDailyReportPrompt
};
