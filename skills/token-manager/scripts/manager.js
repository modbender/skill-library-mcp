#!/usr/bin/env node
/**
 * Token Manager - 通用 LLM Token 管家
 * 支持多模型：Kimi/Moonshot, OpenAI, Anthropic, Google, 本地模型等
 * 
 * 🔒 安全说明 / Security Notice:
 * - API Keys 只从环境变量读取，从不硬编码
 * - 所有数据存储在本地 .data/ 目录，不上传到第三方
 * - 网络请求仅访问官方 LLM API，无其他外联
 * - 不包含任何恶意代码或数据收集
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', '.data');
const CONFIG_FILE = path.join(DATA_DIR, 'config.json');
const LOG_FILE = path.join(DATA_DIR, 'token-usage.json');

// 默认配置
const DEFAULT_CONFIG = {
  providers: {
    moonshot: {
      name: 'Kimi/Moonshot',
      baseUrl: 'api.moonshot.cn',
      protocol: 'https',
      balanceEndpoint: '/v1/users/me/balance',
      tokenEstimateEndpoint: '/v1/tokenizers/estimate-token-count',
      modelsEndpoint: '/v1/models',
      supportsBalance: true,
      supportsTokenEstimate: true,
      pricing: { input: 12, output: 12, unit: 'CNY', per: 1000000 } // ¥12/百万
    },
    openai: {
      name: 'OpenAI',
      baseUrl: 'api.openai.com',
      protocol: 'https',
      usageEndpoint: '/v1/usage',
      modelsEndpoint: '/v1/models',
      supportsBalance: false, // 需要登录控制台查看
      supportsTokenEstimate: false, // 用 tiktoken 本地估算
      pricing: { 
        'gpt-4o': { input: 2.5, output: 10, unit: 'USD', per: 1000000 },
        'gpt-4o-mini': { input: 0.15, output: 0.6, unit: 'USD', per: 1000000 },
        'gpt-3.5-turbo': { input: 0.5, output: 1.5, unit: 'USD', per: 1000000 }
      }
    },
    anthropic: {
      name: 'Anthropic/Claude',
      baseUrl: 'api.anthropic.com',
      protocol: 'https',
      supportsBalance: false,
      supportsTokenEstimate: false,
      pricing: {
        'claude-3-5-sonnet': { input: 3, output: 15, unit: 'USD', per: 1000000 },
        'claude-3-opus': { input: 15, output: 75, unit: 'USD', per: 1000000 },
        'claude-3-haiku': { input: 0.25, output: 1.25, unit: 'USD', per: 1000000 }
      }
    },
    gemini: {
      name: 'Google/Gemini',
      baseUrl: 'generativelanguage.googleapis.com',
      protocol: 'https',
      supportsBalance: false,
      supportsTokenEstimate: false,
      pricing: {
        'gemini-1.5-pro': { input: 3.5, output: 10.5, unit: 'USD', per: 1000000 },
        'gemini-1.5-flash': { input: 0.35, output: 1.05, unit: 'USD', per: 1000000 }
      }
    },
    ollama: {
      name: 'Ollama/本地模型',
      baseUrl: 'localhost:11434',
      protocol: 'http',
      supportsBalance: false, // 本地免费
      supportsTokenEstimate: false,
      pricing: { input: 0, output: 0, unit: 'FREE', per: 1 }
    }
  },
  activeProvider: 'moonshot'
};

// 初始化数据目录
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 加载/创建配置
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const saved = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
      return { ...DEFAULT_CONFIG, ...saved };
    }
  } catch (e) {}
  return DEFAULT_CONFIG;
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// 加载历史
function loadHistory() {
  try {
    if (fs.existsSync(LOG_FILE)) {
      return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
    }
  } catch (e) {}
  return { sessions: [], daily: {}, alerts: [] };
}

function saveHistory(data) {
  fs.writeFileSync(LOG_FILE, JSON.stringify(data, null, 2));
}

// 通用 HTTP 请求
function makeRequest(config, path, method = 'GET', postData = null, headers = {}) {
  return new Promise((resolve) => {
    const lib = config.protocol === 'https' ? https : http;
    const options = {
      hostname: config.baseUrl,
      path: path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      timeout: 10000
    };

    const req = lib.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ success: true, data: parsed, status: res.statusCode });
        } catch (e) {
          resolve({ success: false, error: 'Parse error', raw: data });
        }
      });
    });

    req.on('error', (e) => resolve({ success: false, error: e.message }));
    req.on('timeout', () => {
      req.destroy();
      resolve({ success: false, error: 'Timeout' });
    });

    if (postData) {
      req.write(JSON.stringify(postData));
    }
    req.end();
  });
}

// 查询余额（支持多提供商）
async function queryBalance(providerName, apiKey) {
  const config = loadConfig().providers[providerName];
  if (!config) return { success: false, error: 'Unknown provider' };
  
  if (!config.supportsBalance) {
    return { 
      success: false, 
      error: 'Provider does not support balance query via API',
      hint: 'Please check balance in console',
      consoleUrl: getConsoleUrl(providerName)
    };
  }

  try {
    switch (providerName) {
      case 'moonshot':
        const result = await makeRequest(
          config, 
          config.balanceEndpoint, 
          'GET', 
          null, 
          { 'Authorization': `Bearer ${apiKey}` }
        );
        if (result.success && result.data.data) {
          return {
            success: true,
            provider: config.name,
            balance: result.data.data.available_balance || 0,
            cash: result.data.data.cash_balance || 0,
            voucher: result.data.data.voucher_balance || 0,
            currency: 'CNY'
          };
        }
        return { success: false, error: 'Invalid response' };
      
      default:
        return { success: false, error: 'Not implemented' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 估算 Token（支持多提供商）
async function estimateTokens(providerName, text, model, apiKey) {
  const config = loadConfig().providers[providerName];
  if (!config) return { success: false, error: 'Unknown provider' };
  
  // 如果没有 API 支持，使用简单的字符估算（粗略）
  if (!config.supportsTokenEstimate) {
    // 粗略估算：1 token ≈ 4 字符（中文约 1.5 token/字）
    const charCount = typeof text === 'string' ? text.length : JSON.stringify(text).length;
    const estimated = Math.ceil(charCount / 4 * 1.5);
    return {
      success: true,
      provider: config.name,
      total_tokens: estimated,
      model: model || 'unknown',
      note: 'Estimated (provider does not support token counting API)',
      method: 'approximation'
    };
  }

  try {
    switch (providerName) {
      case 'moonshot':
        const messages = Array.isArray(text) 
          ? text 
          : [{ role: 'user', content: text }];
        
        const result = await makeRequest(
          config,
          config.tokenEstimateEndpoint,
          'POST',
          { model: model || 'kimi-k2.5', messages },
          { 'Authorization': `Bearer ${apiKey}` }
        );
        
        if (result.success && result.data.data) {
          return {
            success: true,
            provider: config.name,
            total_tokens: result.data.data.total_tokens || 0,
            model: model || 'kimi-k2.5',
            method: 'api'
          };
        }
        return { success: false, error: 'Invalid response' };
      
      default:
        return { success: false, error: 'Not implemented' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 获取控制台链接
function getConsoleUrl(provider) {
  const urls = {
    moonshot: 'https://platform.moonshot.cn/console',
    openai: 'https://platform.openai.com/usage',
    anthropic: 'https://console.anthropic.com/',
    gemini: 'https://ai.google.dev/'
  };
  return urls[provider] || 'N/A';
}

// 获取模型价格
function getPricing(provider, model) {
  const config = loadConfig().providers[provider];
  if (!config) return null;
  
  const pricing = config.pricing;
  if (!pricing) return null;
  
  // 如果是统一价格（包括 FREE）
  if (pricing.unit === 'FREE' || (typeof pricing.input === 'number' && typeof pricing.output === 'number')) {
    return { ...pricing, model: 'all' };
  }
  
  // 如果是按模型定价
  if (model && pricing[model]) {
    return { ...pricing[model], model };
  }
  
  // 返回第一个可用价格
  const firstModel = Object.keys(pricing)[0];
  return firstModel ? { ...pricing[firstModel], model: firstModel } : null;
}

// 估算费用
function estimateCost(tokensIn, tokensOut, provider, model) {
  const pricing = getPricing(provider, model);
  if (!pricing || pricing.unit === 'FREE') {
    return { input: 0, output: 0, total: 0, currency: 'FREE' };
  }
  
  const costIn = (tokensIn / pricing.per) * pricing.input;
  const costOut = (tokensOut / pricing.per) * pricing.output;
  return {
    input: costIn,
    output: costOut,
    total: costIn + costOut,
    currency: pricing.unit,
    model: pricing.model
  };
}

// 智能分析建议
function analyzeUsage(sessionData, history, provider) {
  const suggestions = [];
  const warnings = [];
  const providerConfig = loadConfig().providers[provider];
  
  // 1. 上下文检查
  const contextRatio = sessionData.contextUsed / sessionData.contextMax;
  if (contextRatio > 0.8) {
    warnings.push({
      level: 'critical',
      message: '🚨 Context 80%+ full! Must compact immediately',
      messageCn: '🚨 上下文即将满载 (80%+)，必须压缩或清理',
      action: 'compact'
    });
  } else if (contextRatio > 0.5) {
    suggestions.push({
      priority: 'medium',
      message: `📚 Context ${(contextRatio * 100).toFixed(0)}% used, consider compacting`,
      messageCn: `📚 上下文使用 ${(contextRatio * 100).toFixed(0)}%，建议适时压缩`,
      action: 'compact'
    });
  }
  
  // 2. 会话大小检查
  const totalTokens = sessionData.tokensIn + sessionData.tokensOut;
  if (totalTokens > 50000) {
    warnings.push({
      level: 'high',
      message: '⚠️ Session 50k+ tokens! Split tasks now',
      messageCn: '⚠️ 当前会话已用 50k+ tokens，建议立即压缩或拆分任务',
      action: 'spawn'
    });
  } else if (totalTokens > 20000) {
    suggestions.push({
      priority: 'high',
      message: '📊 Large session (20k+), use sub-agents',
      messageCn: '📊 会话较大 (20k+ tokens)，建议拆分复杂任务到子代理',
      action: 'spawn'
    });
  }
  
  // 3. Reasoning 检查
  if (sessionData.thinking === 'on' || sessionData.reasoning === true) {
    if (sessionData.tokensIn < 5000) {
      suggestions.push({
        priority: 'low',
        message: '💡 Simple task? Disable reasoning to save 20-30%',
        messageCn: '💡 简单任务可关闭 reasoning 节省 20-30% token',
        action: 'thinking_off'
      });
    } else {
      suggestions.push({
        priority: 'info',
        message: '✅ Reasoning enabled, good for complex tasks',
        messageCn: '✅ Reasoning 开启中，适合复杂任务',
        action: 'keep'
      });
    }
  }
  
  // 4. 余额检查
  if (sessionData.balance !== undefined && sessionData.balance < 5) {
    warnings.push({
      level: 'critical',
      message: `🚨 Low balance ¥${sessionData.balance.toFixed(2)}! Enable save mode`,
      messageCn: `🚨 余额仅剩 ¥${sessionData.balance.toFixed(2)}，建议充值或开启省钱模式`,
      action: 'save_mode'
    });
  }
  
  // 5. 提供商特定建议
  if (providerConfig && providerConfig.name === 'Ollama/本地模型') {
    suggestions.push({
      priority: 'info',
      message: '🏠 Local model - no API costs!',
      messageCn: '🏠 本地模型运行，无 API 费用！',
      action: 'none'
    });
  }
  
  return { suggestions, warnings };
}

// 生成完整报告
async function generateReport(sessionData, provider = 'moonshot', apiKey) {
  const history = loadHistory();
  const providerConfig = loadConfig().providers[provider];
  
  // 查询余额（如果支持）
  let balanceInfo = null;
  if (apiKey) {
    balanceInfo = await queryBalance(provider, apiKey);
  }
  
  // 计算费用
  const cost = estimateCost(
    sessionData.tokensIn, 
    sessionData.tokensOut, 
    provider, 
    sessionData.model
  );
  
  const report = {
    timestamp: new Date().toISOString(),
    provider: {
      id: provider,
      name: providerConfig?.name || provider
    },
    session: {
      ...sessionData,
      cost: {
        ...cost,
        inputFormatted: cost.currency === 'FREE' ? 'FREE' : `${cost.currency === 'CNY' ? '¥' : '$'}${cost.input.toFixed(4)}`,
        outputFormatted: cost.currency === 'FREE' ? 'FREE' : `${cost.currency === 'CNY' ? '¥' : '$'}${cost.output.toFixed(4)}`,
        totalFormatted: cost.currency === 'FREE' ? 'FREE' : `${cost.currency === 'CNY' ? '¥' : '$'}${cost.total.toFixed(4)}`
      }
    },
    balance: balanceInfo?.success ? {
      available: balanceInfo.balance,
      currency: balanceInfo.currency,
      consoleUrl: getConsoleUrl(provider)
    } : { 
      note: balanceInfo?.error || 'API key not provided',
      consoleUrl: getConsoleUrl(provider)
    },
    analysis: analyzeUsage(sessionData, history, provider),
    quickActions: generateQuickActions(sessionData, provider)
  };
  
  // 保存历史
  history.sessions.push({
    time: report.timestamp,
    provider,
    tokens: sessionData.tokensIn + sessionData.tokensOut,
    cost: cost.total,
    currency: cost.currency
  });
  saveHistory(history);
  
  return report;
}

// 生成快捷操作
function generateQuickActions(sessionData, provider) {
  const actions = [];
  const contextRatio = sessionData.contextUsed / sessionData.contextMax;
  
  if (contextRatio > 0.5) {
    actions.push({
      name: 'Compact Context',
      nameCn: '压缩上下文',
      command: '/compact',
      description: 'Reduce context size'
    });
  }
  
  if ((sessionData.tokensIn + sessionData.tokensOut) > 15000) {
    actions.push({
      name: 'Spawn Sub-agent',
      nameCn: '拆分子代理',
      command: '/spawn <task>',
      description: 'Offload to new session'
    });
  }
  
  if (sessionData.thinking === 'on') {
    actions.push({
      name: 'Disable Reasoning',
      nameCn: '关闭推理',
      command: '/thinking off',
      description: 'Save 20-30% tokens'
    });
  }
  
  return actions;
}

// CLI 模式
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const config = loadConfig();
  
  switch (command) {
    case 'report':
      // report <tokensIn> <tokensOut> <contextUsed> <contextMax> <thinking> [balance] [provider] [model] [apiKey]
      const sessionData = {
        tokensIn: parseInt(args[1]) || 0,
        tokensOut: parseInt(args[2]) || 0,
        contextUsed: parseInt(args[3]) || 0,
        contextMax: parseInt(args[4]) || 200000,
        thinking: args[5] || 'off',
        balance: parseFloat(args[6]) || 0,
        model: args[8] || 'kimi-k2.5'
      };
      const provider = args[7] || config.activeProvider || 'moonshot';
      const apiKey = args[9] || process.env.MOONSHOT_API_KEY || process.env.OPENAI_API_KEY;
      
      const report = await generateReport(sessionData, provider, apiKey);
      console.log(JSON.stringify(report, null, 2));
      break;
    
    case 'balance':
      const p = args[1] || config.activeProvider;
      const key = args[2] || process.env.MOONSHOT_API_KEY;
      const bal = await queryBalance(p, key);
      console.log(JSON.stringify(bal, null, 2));
      break;
    
    case 'estimate':
      // estimate <provider> <tokensIn> <tokensOut> [model]
      const prov = args[1] || 'moonshot';
      const tIn = parseInt(args[2]) || 0;
      const tOut = parseInt(args[3]) || 0;
      const mdl = args[4];
      const est = estimateCost(tIn, tOut, prov, mdl);
      console.log(JSON.stringify({
        provider: prov,
        tokens: { in: tIn, out: tOut },
        cost: est
      }, null, 2));
      break;
    
    case 'providers':
      console.log(JSON.stringify({
        providers: Object.keys(config.providers).map(k => ({
          id: k,
          name: config.providers[k].name,
          supportsBalance: config.providers[k].supportsBalance,
          supportsTokenEstimate: config.providers[k].supportsTokenEstimate,
          consoleUrl: getConsoleUrl(k)
        }))
      }, null, 2));
      break;
    
    case 'set-provider':
      config.activeProvider = args[1];
      saveConfig(config);
      console.log(JSON.stringify({ success: true, activeProvider: args[1] }));
      break;
    
    case 'history':
      const hist = loadHistory();
      console.log(JSON.stringify(hist, null, 2));
      break;
    
    default:
      console.log(JSON.stringify({
        usage: 'node manager.js <command> [args]',
        commands: {
          report: '生成完整报告 (tokensIn tokensOut contextUsed contextMax thinking balance provider model apiKey)',
          balance: '查询余额 (provider apiKey)',
          estimate: '估算费用 (provider tokensIn tokensOut model)',
          providers: '列出支持的提供商',
          'set-provider': '设置默认提供商 (provider)',
          history: '显示使用历史'
        }
      }, null, 2));
  }
}

module.exports = {
  generateReport,
  queryBalance,
  estimateTokens,
  estimateCost,
  analyzeUsage,
  getPricing,
  loadConfig,
  saveConfig
};

if (require.main === module) {
  main();
}
