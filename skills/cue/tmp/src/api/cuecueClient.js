/**
 * CueCue API 客户端
 * 基于原生 https 模块，无需额外依赖
 */

import https from 'https';
import { randomUUID } from 'crypto';
import { createLogger } from '../core/logger.js';

const logger = createLogger('CueCueClient');

const BASE_URL = 'https://cuecue.cn';

/**
 * 角色模式配置
 */
const MODE_CONFIGS = {
  trader: {
    role: '短线交易分析师',
    focus: '资金流向、席位动向、市场情绪、技术形态、游资博弈',
    framework: '市场微观结构与资金流向分析框架（Timeline Reconstruction）',
    method: '追踪龙虎榜席位动向，分析大单资金流向，识别市场情绪拐点，研判技术形态支撑压力位',
    sources: '交易所龙虎榜、Level-2 行情数据、东方财富/同花顺资金数据、游资席位追踪、实时财经快讯'
  },
  'fund-manager': {
    role: '基金经理',
    focus: '估值模型、财务分析、投资决策、风险收益比',
    framework: '基本面分析与估值模型框架',
    method: '深度分析财务报表，构建估值模型（DCF/PE/PB 等），评估内在价值与市场价格偏离度',
    sources: '上市公司财报、交易所公告、Wind/同花顺数据、券商深度研报、管理层访谈纪要'
  },
  researcher: {
    role: '行业研究员',
    focus: '产业链分析、竞争格局、技术趋势、市场空间',
    framework: '产业链拆解与竞争力评估框架（Peer Benchmarking）',
    method: '梳理上下游产业链结构，对比主要竞争对手的核心能力，研判技术演进趋势',
    sources: '上市公司公告、券商研报、行业协会数据、专利数据库、技术白皮书'
  },
  advisor: {
    role: '资深理财顾问',
    focus: '投资建议、资产配置、风险控制、收益预期',
    framework: '资产配置与风险收益评估框架',
    method: '根据用户财务状况，提供个性化的投资组合建议，分析各类资产的风险收益特征',
    sources: '公募基金报告、保险产品说明书、银行理财公告、权威财经媒体'
  }
};

/**
 * 构建 rewritten_mandate 格式的提示词
 * @param {string} topic - 研究主题
 * @param {string} mode - 研究模式
 * @returns {string}
 */
export function buildPrompt(topic, mode = 'default') {
  const config = MODE_CONFIGS[mode];
  
  if (!config) {
    return topic;
  }
  
  return `**【调研目标】**
以${config.role}的专业视角，针对"${topic}"进行全网深度信息搜集与分析，旨在回答该主题下的核心投资/交易问题。

**【信息搜集与整合框架】**
1. **${config.framework}**：${config.method}。
2. **关键证据锚定**：针对核心争议点或关键数据，查找并引用权威信源（如官方公告、交易所数据、权威研报）的原始信息。
3. **多维视角交叉**：汇总不同利益相关方（如买方机构、卖方分析师、产业从业者）的观点差异与共识。

**【信源与边界】**
- 优先信源：${config.sources}。
- 时间窗口：结合当前日期，优先近 6 个月内的最新动态与数据。
- 排除信源：无明确来源的小道消息、未经证实的社交媒体传言。

**【核心关注】**
${config.focus}`;
}

/**
 * 自动检测研究模式
 * @param {string} topic - 研究主题
 * @returns {string}
 */
export function autoDetectMode(topic) {
  const topicLower = topic.toLowerCase();
  
  // 短线交易
  if (/龙虎榜 | 涨停 | 游资 | 资金流向 | 短线 | 打板 | 连板 | 换手率 | 主力资金/.test(topicLower)) {
    return 'trader';
  }
  
  // 基金经理
  if (/财报 | 估值 | 业绩 | 年报 | 季报 | 投资 | 财务|ROE|PE|PB| 现金流 | 盈利/.test(topicLower)) {
    return 'fund-manager';
  }
  
  // 研究员
  if (/产业链 | 竞争格局 | 技术路线 | 市场格局 | 行业分析 | 市场份额 | 供应链 | 上下游/.test(topicLower)) {
    return 'researcher';
  }
  
  // 理财顾问
  if (/投资建议 | 资产配置 | 风险控制 | 适合买 | 怎么买 | 定投 | 组合/.test(topicLower)) {
    return 'advisor';
  }
  
  // 默认研究员
  return 'researcher';
}

/**
 * 启动深度研究
 * @param {Object} options - 选项
 * @param {string} options.topic - 研究主题
 * @param {string} options.mode - 研究模式
 * @param {string} options.chatId - 聊天 ID
 * @param {string} options.apiKey - API Key
 * @returns {Promise<Object>}
 */
export async function startResearch({ topic, mode, chatId, apiKey }) {
  const conversationId = `conv_${randomUUID().replace(/-/g, '')}`;
  const messageId = `msg_${randomUUID().replace(/-/g, '')}`;
  const reportUrl = `${BASE_URL}/c/${conversationId}`;
  
  // 自动检测模式
  if (!mode || mode === 'default') {
    mode = autoDetectMode(topic);
  }
  
  // 构建提示词
  const prompt = buildPrompt(topic, mode);
  
  logger.info(`Starting research: ${topic} (mode: ${mode})`);
  
  const requestData = {
    messages: [
      {
        role: 'user',
        content: prompt,
        id: messageId,
        type: 'text'
      }
    ],
    chat_id: chatId,
    conversation_id: conversationId,
    need_confirm: false,
    need_analysis: false,
    need_underlying: false,
    need_recommend: false
  };
  
  try {
    const result = await makeRequest('/api/v1/chat/completions', requestData, apiKey);
    
    return {
      conversationId,
      chatId,
      reportUrl,
      topic,
      mode,
      ...result
    };
  } catch (error) {
    logger.error('Failed to start research', error);
    throw error;
  }
}

/**
 * 发送 HTTPS 请求
 * @param {string} path - API 路径
 * @param {Object} data - 请求数据
 * @param {string} apiKey - API Key
 * @returns {Promise<Object>}
 */
function makeRequest(path, data, apiKey) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const body = JSON.stringify(data);
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname + url.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'Authorization': `Bearer ${apiKey}`
      }
    };
    
    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(responseData);
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.write(body);
    req.end();
  });
}
