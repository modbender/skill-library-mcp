#!/usr/bin/env node
/**
 * Captcha Auto Skill v1.0.2 - 标准入口
 * OpenClaw 统一调用接口
 */

import { recognizeCaptcha } from '../index.mjs';

// 解析命令行参数
const args = process.argv.slice(2);
const options = {};

for (const arg of args) {
  if (arg.startsWith('--url=')) {
    options.url = arg.substring(6);
  }
  if (arg.startsWith('--prefix=')) {
    options.outputPrefix = arg.substring(9);
  }
  if (arg.startsWith('--api-key=')) {
    options.apiKey = arg.substring(10);
  }
  if (arg.startsWith('--base-url=')) {
    options.baseUrl = arg.substring(11);
  }
  if (arg.startsWith('--model=')) {
    options.model = arg.substring(8);
  }
  if (arg === '--skip-local') {
    options.skipLocal = true;
  }
  if (arg === '--json') {
    options.json = true;
  }
}

// 如果没有 URL，显示帮助
if (!options.url) {
  console.log(`
Captcha Auto Skill v1.0.2 - 混合模式

用法:
  node scripts/run.mjs --url="<url>" [选项]

选项:
  --url=<url>         目标页面 URL（必需）
  --prefix=<prefix>   输出文件前缀（可选，默认：smart_captcha）
  --api-key=<key>     视觉模型 API Key（可选）
  --base-url=<url>    API 服务端点（可选）
  --model=<model>     模型名称（可选，默认：qwen-vl-plus）
  --skip-local        跳过本地 OCR，直接使用视觉模型
  --json              输出 JSON 格式（方便程序解析）

示例:
  node scripts/run.mjs --url="https://example.com/login"
  node scripts/run.mjs --url="https://example.com" --prefix="my_test" --json
  node scripts/run.mjs --url="https://example.com" --skip-local

必需配置（三选一）:
  1. 环境变量：VISION_API_KEY, VISION_BASE_URL, VISION_MODEL
  2. OpenClaw 配置：~/.openclaw/openclaw.json
  3. 命令行参数：--api-key, --base-url, --model

识别策略:
  - 默认：本地 Tesseract OCR 优先 → 失败降级视觉模型
  - --skip-local: 直接使用视觉模型
`);
  process.exit(0);
}

// 执行识别
async function main() {
  const useJson = options.json || process.env.JSON_OUTPUT === '1';
  
  if (!useJson) {
    console.log('🤖 Captcha Auto Skill v1.0.2 (混合模式)');
    console.log('=' .repeat(60));
  }
  
  try {
    const result = await recognizeCaptcha(options);
    
    if (useJson) {
      // JSON 输出 - 方便 Agent 解析
      console.log(JSON.stringify(result, null, 2));
    } else {
      // 人类可读输出
      console.log('');
      console.log('='.repeat(60));
      if (result.success) {
        console.log(`✅ 完成！验证码：${result.text}`);
        console.log(`识别方式：${result.method === 'tesseract' ? '本地 Tesseract OCR' : '视觉模型'}`);
        console.log('');
        console.log('📊 截图文件:');
        if (result.screenshots.page) console.log(`   - ${result.screenshots.page}`);
        if (result.screenshots.filled) console.log(`   - ${result.screenshots.filled}`);
        if (result.screenshots.result) console.log(`   - ${result.screenshots.result}`);
      } else {
        console.log(`❌ 失败：${result.error}`);
        console.log('');
        console.log('📊 截图文件:');
        if (result.screenshots.page) console.log(`   - ${result.screenshots.page}`);
        if (result.screenshots.error) console.log(`   - ${result.screenshots.error}`);
      }
    }
    
    process.exit(result.success ? 0 : 1);
    
  } catch (error) {
    if (useJson) {
      console.log(JSON.stringify({ success: false, error: error.message }));
    } else {
      console.error('❌ 异常:', error.message);
    }
    process.exit(1);
  }
}

main();
