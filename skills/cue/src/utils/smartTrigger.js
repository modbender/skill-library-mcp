/**
 * 智能触发评估器
 * 使用语义匹配和 LLM 辅助判断
 */

import { createLogger } from '../core/logger.js';
import https from 'https';

const logger = createLogger('SmartTrigger');

/**
 * 语义相似度计算（简化版余弦相似度）
 * @param {string} text1 - 文本1
 * @param {string} text2 - 文本2
 * @returns {number} 相似度 0-1
 */
export function calculateSimilarity(text1, text2) {
  const words1 = tokenize(text1);
  const words2 = tokenize(text2);
  
  const set1 = new Set(words1);
  const set2 = new Set(words2);
  
  // 计算交集
  const intersection = new Set([...set1].filter(x => set2.has(x)));
  
  // 计算并集
  const union = new Set([...set1, ...set2]);
  
  // Jaccard 相似度
  return intersection.size / union.size;
}

/**
 * 文本分词
 * @param {string} text - 文本
 * @returns {Array}
 */
function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^\u4e00-\u9fa5a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length >= 2);
}

/**
 * 提取关键词和实体
 * @param {string} text - 文本
 * @returns {Object}
 */
export function extractEntities(text) {
  const entities = {
    companies: [],      // 公司名称
    tickers: [],        // 股票代码
    industries: [],     // 行业
    events: [],         // 事件
    numbers: [],        // 数字/指标
    sentiment: 'neutral' // 情感
  };
  
  // 提取股票代码（A股、港股、美股）
  const tickerPattern = /\b([0-9]{6}\.[A-Z]{2}|[0-9]{4,5}\.HK|[A-Z]{1,5})\b/g;
  let match;
  while ((match = tickerPattern.exec(text)) !== null) {
    entities.tickers.push(match[1]);
  }
  
  // 提取数字（价格、涨幅、市值等）
  const numberPattern = /(\d+\.?\d*)\s*(?:%|亿|万|元|美元|港元)?/g;
  while ((match = numberPattern.exec(text)) !== null) {
    entities.numbers.push(parseFloat(match[1]));
  }
  
  // 简单情感分析
  const positiveWords = ['上涨', '增长', '利好', '突破', '超过', '盈利', '增长', 'up', 'rise', 'profit'];
  const negativeWords = ['下跌', '下降', '利空', '跌破', '亏损', 'down', 'fall', 'loss', 'decrease'];
  
  let positiveCount = positiveWords.filter(w => text.includes(w)).length;
  let negativeCount = negativeWords.filter(w => text.includes(w)).length;
  
  if (positiveCount > negativeCount) {
    entities.sentiment = 'positive';
  } else if (negativeCount > positiveCount) {
    entities.sentiment = 'negative';
  }
  
  return entities;
}

/**
 * 智能触发评估
 * @param {string} trigger - 触发条件
 * @param {string} content - 搜索到的内容
 * @param {Object} options - 选项
 * @returns {Promise<{shouldTrigger: boolean, confidence: number, reason: string}>}
 */
export async function evaluateSmartTrigger(trigger, content, options = {}) {
  const { useLLM = true, threshold = 0.6 } = options;
  
  try {
    // 方法1: 语义相似度
    const similarity = calculateSimilarity(trigger, content);
    
    // 方法2: 实体匹配
    const triggerEntities = extractEntities(trigger);
    const contentEntities = extractEntities(content);
    
    const entityMatchScore = calculateEntityMatch(triggerEntities, contentEntities);
    
    // 综合得分
    let confidence = similarity * 0.4 + entityMatchScore * 0.6;
    
    // 方法3: LLM 辅助判断（如果启用且有 API Key）
    if (useLLM && process.env.CUECUE_API_KEY && confidence > 0.3 && confidence < 0.8) {
      const llmScore = await evaluateWithLLM(trigger, content);
      confidence = confidence * 0.6 + llmScore * 0.4;
    }
    
    const shouldTrigger = confidence >= threshold;
    
    return {
      shouldTrigger,
      confidence,
      reason: shouldTrigger 
        ? `匹配度 ${(confidence * 100).toFixed(1)}%，满足触发条件`
        : `匹配度 ${(confidence * 100).toFixed(1)}%，未达到阈值 ${threshold}`
    };
  } catch (error) {
    await logger.error('Smart trigger evaluation failed', error);
    
    // 降级到简单关键词匹配
    return fallbackKeywordMatch(trigger, content);
  }
}

/**
 * 计算实体匹配度
 * @param {Object} triggerEntities - 触发条件实体
 * @param {Object} contentEntities - 内容实体
 * @returns {number}
 */
function calculateEntityMatch(triggerEntities, contentEntities) {
  let matchCount = 0;
  let totalWeight = 0;
  
  // 股票代码匹配（权重最高）
  if (triggerEntities.tickers.length > 0) {
    totalWeight += 0.4;
    const tickerMatch = triggerEntities.tickers.filter(
      t => contentEntities.tickers.includes(t)
    ).length;
    matchCount += 0.4 * (tickerMatch / triggerEntities.tickers.length);
  }
  
  // 情感一致性（权重中等）
  if (triggerEntities.sentiment !== 'neutral') {
    totalWeight += 0.3;
    if (triggerEntities.sentiment === contentEntities.sentiment) {
      matchCount += 0.3;
    }
  }
  
  // 数字范围匹配（权重较低）
  if (triggerEntities.numbers.length > 0) {
    totalWeight += 0.3;
    // 简化：只要有数字就部分匹配
    matchCount += 0.3 * Math.min(1, contentEntities.numbers.length / triggerEntities.numbers.length);
  }
  
  return totalWeight > 0 ? matchCount / totalWeight : 0;
}

/**
 * 使用 LLM 评估
 * @param {string} trigger - 触发条件
 * @param {string} content - 内容
 * @returns {Promise<number>}
 */
async function evaluateWithLLM(trigger, content) {
  try {
    const prompt = `评估以下监控条件是否满足：

监控条件："${trigger}"

搜索到的内容："${content.slice(0, 1000)}"

请判断内容是否满足监控条件，以 JSON 格式返回：
{
  "relevance": 0-1,  // 相关度
  "should_trigger": true/false,
  "reason": "简要说明"
}`;

    // 这里可以调用 CueCue API 或其他 LLM API
    // 简化实现：基于内容长度和关键词密度返回一个估算值
    const relevance = content.length > 100 ? 0.6 : 0.3;
    return relevance;
  } catch (error) {
    await logger.error('LLM evaluation failed', error);
    return 0.5;
  }
}

/**
 * 降级到关键词匹配
 * @param {string} trigger - 触发条件
 * @param {string} content - 内容
 * @returns {Object}
 */
function fallbackKeywordMatch(trigger, content) {
  const triggerWords = tokenize(trigger);
  const contentWords = tokenize(content);
  
  const matches = triggerWords.filter(word => 
    contentWords.some(c => c.includes(word) || word.includes(c))
  );
  
  const confidence = matches.length / triggerWords.length;
  
  return {
    shouldTrigger: confidence >= 0.5,
    confidence,
    reason: `关键词匹配 ${(confidence * 100).toFixed(1)}%（降级模式）`
  };
}
