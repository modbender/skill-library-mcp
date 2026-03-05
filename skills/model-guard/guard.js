#!/usr/bin/env node

import { execSync } from 'child_process';

// 配置
const THRESHOLD = 20; // 20%
const FALLBACK_MODEL = 'google/gemini-3-flash-preview';
const AG_PREFIX = 'google-antigravity/';

// 允许切换的 AG 模型候选列表
const CANDIDATES = [
  'google-antigravity/claude-opus-4-5-thinking',
  'google-antigravity/claude-sonnet-4-5',
  'google-antigravity/claude-sonnet-4-5-thinking',
  'google-antigravity/gemini-3-flash',
  'google-antigravity/gemini-3-pro-high',
  'google-antigravity/gemini-3-pro-low',
  'google-antigravity/gpt-oss-120b-medium'
];

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch (e) {
    return null;
  }
}

function main() {
  // 1. 获取当前状态 (plain text 解析更可靠)
  const statusText = run('openclaw models status');
  if (!statusText) {
    console.error('Error: Could not fetch models status.');
    process.exit(1);
  }

  // 获取当前默认模型
  let currentModel = '';
  // 尝试从 json 获取 current model，如果失败则尝试解析 text
  // 简单起见，这里假设我们只为了决策切换
  // 为了准确获取 currentModel，还是调一次 json
  const statusJson = run('openclaw models status --json');
  if (statusJson) {
     try {
       currentModel = JSON.parse(statusJson).defaults?.model?.primary || '';
     } catch (e) {}
  }

  // 2. 解析 AG 配额
  const usageMap = {};
  const lines = statusText.split('\n');
  
  // 默认给 Geminis 100% (如果它们没显示在 Usage 里)
  // 因为 Anti-Gravity 通常只对 Claude 系列显示配额条
  // 我们默认 Gemini 系列是 "Infinite" 除非 explicit 0%
  for (const cand of CANDIDATES) {
      if (cand.includes('gemini')) {
          usageMap[cand] = 100; 
      }
  }

  for (const line of lines) {
    if (line.includes('google-antigravity usage:')) {
      // 提取所有 "modelName XX% left"
      // 匹配: "claude-opus... 80% left"
      const regex = /([a-zA-Z0-9-.]+) (\d+)% left/g;
      let match;
      while ((match = regex.exec(line)) !== null) {
        let modelName = match[1];
        const percent = parseInt(match[2], 10);
        
        // 补全前缀
        if (!modelName.startsWith(AG_PREFIX)) {
            modelName = AG_PREFIX + modelName;
        }
        usageMap[modelName] = percent;
      }
    }
  }

  // 3. 评估最佳模型
  let bestModel = null;
  let maxPercent = -1;

  for (const model of CANDIDATES) {
    const p = usageMap[model] !== undefined ? usageMap[model] : 0; // 未知模型视为 0，除了上面默认的 gemini
    if (p > maxPercent) {
      maxPercent = p;
      bestModel = model;
    }
  }

  // 4. 决策
  if (bestModel && maxPercent >= THRESHOLD) {
    if (currentModel !== bestModel) {
      console.log(`[ModelGuard] Switching to rich model: ${bestModel} (${maxPercent}%)`);
      run(`openclaw models set ${bestModel}`);
    } else {
      // 状态健康，不输出以保持安静
      // console.log(`[ModelGuard] Healthy: ${currentModel} (${maxPercent}%)`);
    }
  } else {
    // 危机模式
    if (currentModel !== FALLBACK_MODEL) {
      console.log(`[ModelGuard] Critical AG quota (Max: ${maxPercent}%). Fallback to: ${FALLBACK_MODEL}`);
      run(`openclaw models set ${FALLBACK_MODEL}`);
    }
  }
}

main();
