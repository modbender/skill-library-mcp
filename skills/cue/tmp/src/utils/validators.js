/**
 * 验证工具
 * 提供输入验证和格式检查
 */

/**
 * 验证 API Key 格式
 * @param {string} apiKey - API Key
 * @returns {{valid: boolean, error?: string}}
 */
export function validateApiKey(apiKey) {
  if (!apiKey) {
    return { valid: false, error: 'API Key 不能为空' };
  }
  
  if (apiKey.length < 10) {
    return { valid: false, error: 'API Key 长度至少 10 个字符' };
  }
  
  // 检查格式
  const patterns = [
    { name: 'Tavily', pattern: /^tvly-/ },
    { name: 'CueCue', pattern: /^skb/ },
    { name: 'CueCue/QVeris', pattern: /^sk-/ }
  ];
  
  for (const { name, pattern } of patterns) {
    if (pattern.test(apiKey)) {
      return { valid: true };
    }
  }
  
  return { 
    valid: false, 
    error: '无法识别 API Key 格式，请检查是否为 tvly-xxx, skb-xxx 或 sk-xxx 格式' 
  };
}

/**
 * 验证主题格式
 * @param {string} topic - 研究主题
 * @returns {{valid: boolean, error?: string}}
 */
export function validateTopic(topic) {
  if (!topic || topic.trim().length === 0) {
    return { valid: false, error: '研究主题不能为空' };
  }
  
  if (topic.length < 2) {
    return { valid: false, error: '研究主题太短' };
  }
  
  if (topic.length > 500) {
    return { valid: false, error: '研究主题太长（最多 500 字符）' };
  }
  
  return { valid: true };
}

/**
 * 验证监控 ID 格式
 * @param {string} monitorId - 监控 ID
 * @returns {boolean}
 */
export function isValidMonitorId(monitorId) {
  return /^[a-zA-Z0-9_-]+$/.test(monitorId);
}

/**
 * 验证任务 ID 格式
 * @param {string} taskId - 任务 ID
 * @returns {boolean}
 */
export function isValidTaskId(taskId) {
  return /^cuecue_\d+$/.test(taskId);
}

/**
 * 验证天数参数
 * @param {string|number} days - 天数
 * @returns {{valid: boolean, value?: number, error?: string}}
 */
export function validateDays(days) {
  const num = parseInt(days, 10);
  
  if (isNaN(num)) {
    return { valid: false, error: '天数必须是数字' };
  }
  
  if (num < 1 || num > 365) {
    return { valid: false, error: '天数必须在 1-365 之间' };
  }
  
  return { valid: true, value: num };
}

/**
 * 验证模式参数
 * @param {string} mode - 模式
 * @returns {{valid: boolean, normalized?: string}}
 */
export function validateMode(mode) {
  const modeMap = {
    'trader': 'trader',
    '短线': 'trader',
    '短线交易': 'trader',
    'fund-manager': 'fund-manager',
    '基金经理': 'fund-manager',
    'researcher': 'researcher',
    '研究员': 'researcher',
    'advisor': 'advisor',
    '理财顾问': 'advisor'
  };
  
  const normalized = modeMap[mode?.toLowerCase()];
  
  if (normalized) {
    return { valid: true, normalized };
  }
  
  return { valid: false };
}
