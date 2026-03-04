/**
 * 简化的权限控制
 * 两级：Owner vs 其他用户
 * 不依赖 SOUL.md，代码层硬编码
 */

// Owner 配置
const OWNER_CONFIG = {
  id: 'ou_5facd87f11cb35d651c435a4c1c7c4bc',
  model: 'minimax/MiniMax-M2.5-highspeed',
  fallbackModel: 'moonshot/kimi-k2.5',
  limits: null  // 无限制
};

// 普通用户配置
const USER_CONFIG = {
  model: 'sensedeal-ai/qwen3.5-plus',
  fallbackModel: 'ark/ark-code-latest',
  limits: {
    dailyResearch: 3,      // 每日研究3次
    maxMonitors: 10,       // 最多10个监控
    dailyMessages: 100     // 每日100条消息
  }
};

/**
 * 获取用户权限
 * @param {string} userId - 用户ID
 * @returns {object} - 权限配置
 */
export function getUserPermission(userId) {
  if (userId === OWNER_CONFIG.id) {
    return {
      role: 'owner',
      ...OWNER_CONFIG
    };
  }
  
  return {
    role: 'user',
    ...USER_CONFIG
  };
}

/**
 * 检查是否为 Owner
 */
export function isOwner(userId) {
  return userId === OWNER_CONFIG.id;
}

/**
 * 检查研究限制
 */
export async function checkResearchLimit(userId, usageCount) {
  const perms = getUserPermission(userId);
  
  // Owner 无限制
  if (perms.role === 'owner') {
    return { allowed: true, remaining: Infinity };
  }
  
  // 检查限制
  if (usageCount >= perms.limits.dailyResearch) {
    return {
      allowed: false,
      message: `今日研究次数已达上限（${perms.limits.dailyResearch}次）`,
      suggestion: '请明日再试，或联系管理员'
    };
  }
  
  return {
    allowed: true,
    remaining: perms.limits.dailyResearch - usageCount
  };
}

/**
 * 检查监控限制
 */
export async function checkMonitorLimit(userId, currentMonitors) {
  const perms = getUserPermission(userId);
  
  if (perms.role === 'owner') {
    return { allowed: true };
  }
  
  if (currentMonitors >= perms.limits.maxMonitors) {
    return {
      allowed: false,
      message: `监控数量已达上限（${perms.limits.maxMonitors}个）`,
      suggestion: '请删除部分监控后再创建'
    };
  }
  
  return { allowed: true };
}

/**
 * 获取默认模型
 */
export function getDefaultModel(userId) {
  const perms = getUserPermission(userId);
  return perms.model;
}
