/**
 * Smart Router - 4D 压缩智能分发器
 * 
 * @version 1.0
 * @author Neo (宇宙神经系统)
 * @date 2026-02-24
 * 
 * 功能：根据输入文本特征，自动路由到最优 4D 压缩版本
 * 路由规则：基于 T1-T5 实验结论
 */

const fs = require('fs');
const path = require('path');

// 加载配置文件
const sniffRules = JSON.parse(fs.readFileSync(path.join(__dirname, 'sniff-rules.json'), 'utf8'));
const badgeConfig = JSON.parse(fs.readFileSync(path.join(__dirname, 'badge-config.json'), 'utf8'));

/**
 * 文本嗅探器 - 极速标签识别（配置驱动）
 * @param {string} text - 输入文本
 * @returns {object} 嗅探结果
 */
function sniffText(text) {
  const result = {
    length: text.length,
    hasQuestion: false,
    hasEmotion: false,
    hasStructure: false,
    hasKnowledge: false,
    hasNumberList: false,
    tags: []
  };

  // 长度检测
  if (result.length < sniffRules.versionA.maxLength) {
    result.tags.push('short');
  } else if (result.length < 10000) {
    result.tags.push('medium');
  } else {
    result.tags.push('long');
  }

  // 问号检测（对话特征）
  if (/[\?？]/.test(text)) {
    result.hasQuestion = true;
    result.tags.push('question');
  }

  // 情感检测（配置驱动）
  const emotionPattern = /[！!😊❤️😢😄😭😡🎉]/;
  const emotionKeywordsPattern = buildKeywordPattern(sniffRules.versionA.keywords);
  if (emotionPattern.test(text) || (emotionKeywordsPattern && emotionKeywordsPattern.test(text))) {
    result.hasEmotion = true;
    result.tags.push('emotion');
  }

  // 结构检测（配置驱动）
  const structureKeywordsPattern = buildKeywordPattern(sniffRules.versionB.structureWords);
  const numberListPattern = /\d+\./;
  if ((structureKeywordsPattern && structureKeywordsPattern.test(text)) || numberListPattern.test(text)) {
    result.hasStructure = true;
    result.tags.push('structure');
  }
  
  // 数字列表检测
  if (sniffRules.versionB.hasNumberList && numberListPattern.test(text)) {
    result.hasNumberList = true;
  }

  // 知识检测（配置驱动）
  const knowledgeKeywordsPattern = buildKeywordPattern(sniffRules.versionC.knowledgeWords);
  if (knowledgeKeywordsPattern && knowledgeKeywordsPattern.test(text)) {
    result.hasKnowledge = true;
    result.tags.push('knowledge');
  }

  return result;
}

/**
 * 从关键词数组构建正则表达式
 * @param {string[]} keywords - 关键词数组
 * @returns {RegExp|null} 正则表达式
 */
function buildKeywordPattern(keywords) {
  if (!keywords || keywords.length === 0) {
    return null;
  }
  // 转义特殊字符并构建正则
  const escaped = keywords.map(kw => kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  return new RegExp(escaped.join('|'));
}

/**
 * 路由决策 - 根据嗅探结果选择最优版本
 * @param {object} sniffResult - 嗅探结果
 * @returns {string} 路由版本 (A/B/C)
 */
function decideRoute(sniffResult) {
  const { length, hasQuestion, hasEmotion, hasStructure, hasKnowledge, tags } = sniffResult;

  try {
    // 规则 1: 短文本 + 对话/情感 → 版本 A
    if (length < sniffRules.versionA.maxLength && (hasQuestion || hasEmotion)) {
      return 'A';
    }

    // 规则 2: 有结构词 → 版本 B
    if (hasStructure) {
      return 'B';
    }

    // 规则 3: 知识类文本 → 版本 C（默认）
    if (hasKnowledge || sniffRules.versionC.default) {
      return 'C';
    }

    // 规则 4: 中长文本默认 → 版本 C
    if (length >= sniffRules.versionA.maxLength) {
      return 'C';
    }

    // 🛡️ 降级保护：无法识别时强制回退到版本 C
    // 宁可多花 Token，也要保证知识不丢失
    return 'C';
    
  } catch (error) {
    // ⚠️ 异常捕获：任何错误都回退到版本 C
    console.error('[Smart Router Error]', error);
    return 'C';
  }
}

/**
 * 获取徽章信息
 * @param {string} version - 版本 (A/B/C)
 * @returns {object} 徽章配置
 */
function getBadge(version) {
  const versionMap = {
    'A': 'versionA',
    'B': 'versionB',
    'C': 'versionC'
  };
  return badgeConfig[versionMap[version]];
}

/**
 * 主路由函数
 * @param {string} text - 输入文本
 * @returns {object} 路由结果
 */
function routeCompression(text) {
  const startTime = Date.now();
  
  // Step 1: 嗅探
  const sniffResult = sniffText(text);
  
  // Step 2: 决策
  const version = decideRoute(sniffResult);
  
  // Step 3: 获取徽章
  const badge = getBadge(version);
  
  // Step 4: 记录日志
  const processingTime = Date.now() - startTime;
  logRoute(text.length, sniffResult.tags, version, processingTime);
  
  return {
    version,
    badge,
    sniffResult,
    processingTime,
    versionName: getVersionName(version)
  };
}

/**
 * 获取版本名称
 * @param {string} version - 版本 (A/B/C)
 * @returns {string} 版本名称
 */
function getVersionName(version) {
  const nameMap = {
    'A': '原版四力',
    'B': 'S-E-I-T 涌现版',
    'C': '混合版'
  };
  return nameMap[version] || '未知版本';
}

/**
 * 记录路由日志
 * @param {number} length - 输入长度
 * @param {array} tags - 嗅探标签
 * @param {string} version - 路由版本
 * @param {number} time - 处理时间 (ms)
 */
function logRoute(length, tags, version, time) {
  const logDir = path.join(__dirname, 'logs');
  const logFile = path.join(logDir, `router-${new Date().toISOString().split('T')[0]}.log`);
  
  const logEntry = `[${new Date().toISOString()}] ${length} chars | ${tags.join('+')} | Version ${version} | ${time}ms\n`;
  
  // 确保日志目录存在
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  
  // 追加日志
  fs.appendFileSync(logFile, logEntry);
}

/**
 * 格式化输出徽章（含温度反馈）
 * @param {object} badge - 徽章配置
 * @returns {string} 格式化徽章字符串
 */
function formatBadge(badge) {
  return `[${badge.icon} ${badge.name}]`;
}

/**
 * 生成路由报告（含温度反馈）
 * @param {object} routeResult - 路由结果
 * @param {string} originalText - 原始文本
 * @returns {string} 格式化报告
 */
function generateRouteReport(routeResult, originalText) {
  const { version, badge, sniffResult, processingTime, versionName } = routeResult;
  
  return `
${formatBadge(badge)} | 版本：${versionName} | 处理时间：${processingTime}ms

💡 ${badge.warmMessage || '智能路由已激活'}

📊 嗅探分析：
- 文本长度：${sniffResult.length} 字符
- 文本标签：${sniffResult.tags.join(', ') || '无特殊标签'}
- 路由版本：${version} (${versionName})

🎯 路由理由：
${getRouteReason(version, sniffResult)}

---
`.trim();
}

/**
 * 获取路由理由
 * @param {string} version - 路由版本
 * @param {object} sniffResult - 嗅探结果
 * @returns {string} 路由理由说明
 */
function getRouteReason(version, sniffResult) {
  const reasons = {
    'A': '检测到对话/情感特征（短文本 + 问号/情感词），使用原版四力保持流动感',
    'B': '检测到结构/数据特征，使用 S-E-I-T 结构便于快速定位',
    'C': '检测到知识/理论特征或中长文本，使用混合版保证语义保留 97%+'
  };
  
  let reason = reasons[version] || '默认使用混合版（质量优先）';
  
  if (sniffResult.tags.includes('emotion')) {
    reason += '（情感表达）';
  } else if (sniffResult.tags.includes('structure')) {
    reason += '（结构化数据）';
  } else if (sniffResult.tags.includes('knowledge')) {
    reason += '（知识内容）';
  }
  
  return reason;
}

// 导出模块
module.exports = {
  sniffText,
  decideRoute,
  routeCompression,
  getBadge,
  formatBadge,
  generateRouteReport,
  getVersionName
};

// 命令行测试（可选）
if (require.main === module) {
  const testText = process.argv.slice(2).join(' ');
  if (testText) {
    const result = routeCompression(testText);
    console.log(generateRouteReport(result, testText));
  } else {
    console.log('用法：node router.js [测试文本]');
  }
}
