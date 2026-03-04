#!/usr/bin/env node
/**
 * 通用验证码自动识别 Skill - 混合模式 v1.0.2
 * 策略：本地 OCR 优先 → 视觉模型降级 → 智能填写 → 失败则告知用户手动填写
 */

import { chromium } from 'playwright-core';
import { createWorker } from 'tesseract.js';
import fs from 'fs';
import os from 'os';
import path from 'path';

const HOME_DIR = os.homedir();
const CONFIG_PATH = path.join(HOME_DIR, '.openclaw', 'openclaw.json');
const WORKSPACE_DIR = path.join(HOME_DIR, '.openclaw', 'workspace');

function getChromePath() {
  const platform = os.platform();
  switch (platform) {
    case 'darwin':
      return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    case 'linux':
      const linuxPaths = ['/usr/bin/chromium-browser', '/usr/bin/chromium', '/usr/bin/google-chrome', '/snap/bin/chromium'];
      for (const p of linuxPaths) {
        if (fs.existsSync(p)) return p;
      }
      return linuxPaths[0];
    case 'win32':
      return 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    default:
      throw new Error(`不支持的操作系统：${platform}`);
  }
}

function loadConfig(overrides = {}) {
  if (overrides.apiKey) {
    return {
      baseUrl: overrides.baseUrl || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      apiKey: overrides.apiKey,
      model: overrides.model || 'qwen3-vl-plus'
    };
  }
  
  const envApiKey = process.env.VISION_API_KEY || process.env.QWEN_API_KEY;
  if (envApiKey) {
    return {
      baseUrl: process.env.VISION_BASE_URL || process.env.QWEN_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      apiKey: envApiKey,
      model: process.env.VISION_MODEL || process.env.QWEN_MODEL || 'qwen3-vl-plus'
    };
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    const visionConfig = 
      config.models?.providers?.bailian ||
      config.models?.providers?.aliyun ||
      config.models?.providers?.dashscope ||
      config.models?.providers?.openai;
    
    if (!visionConfig) {
      throw new Error('配置文件中缺少视觉模型配置');
    }
    
    return {
      baseUrl: visionConfig.baseUrl?.replace('/v1', '/compatible-mode/v1') || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      apiKey: visionConfig.apiKey,
      model: 'qwen3-vl-plus'
    };
  } catch (e) {
    throw new Error(`无法加载配置：${e.message}\n\n请通过以下方式之一配置:\n1. 环境变量：VISION_API_KEY, VISION_BASE_URL, VISION_MODEL\n2. OpenClaw 配置：${CONFIG_PATH}\n3. 命令行参数：--api-key, --base-url, --model`);
  }
}

async function recognizeWithTesseract(screenshotPath) {
  console.log('🔍 尝试本地 Tesseract OCR 识别...');
  
  const worker = await createWorker('eng', 1, {
    logger: m => {
      if (m.status === 'recognizing text') {
        console.log(`   识别进度：${(m.progress * 100).toFixed(0)}%`);
      }
    }
  });
  
  try {
    const { data: { text, confidence } } = await worker.recognize(screenshotPath);
    const cleanedText = text.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().trim();
    
    console.log(`   识别结果："${cleanedText}" (置信度：${confidence.toFixed(1)}%)`);
    await worker.terminate();
    
    if (confidence < 60 || cleanedText.length === 0) {
      console.log('   ⚠️ 本地 OCR 置信度过低，需要降级到视觉模型');
      return { success: false, text: null, confidence, method: 'tesseract' };
    }
    
    return { success: true, text: cleanedText, confidence, method: 'tesseract' };
    
  } catch (error) {
    console.log(`   ❌ 本地 OCR 失败：${error.message}`);
    await worker.terminate();
    return { success: false, text: null, error: error.message, method: 'tesseract' };
  }
}

async function analyzePageWithVision(screenshotPath, config) {
  console.log('🧠 降级到视觉模型识别...');
  
  const imageBuffer = fs.readFileSync(screenshotPath);
  const base64Image = imageBuffer.toString('base64');

  const response = await fetch(`${config.baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`
    },
    body: JSON.stringify({
      model: config.model,
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: `这是一个网页截图，请识别验证码图片中的文字。
只返回验证码文字本身（通常是 4-6 位字母数字），不要任何其他描述或解释。
如果看不到验证码或无法识别，返回"UNRECOGNIZABLE"。`
            },
            {
              type: 'image_url',
              image_url: { url: `data:image/png;base64,${base64Image}` }
            }
          ]
        }
      ],
      max_tokens: 20,
      temperature: 0.1
    })
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(`API 错误：${response.status} ${errorText}`);
  }

  const data = await response.json();
  const content = data.choices[0].message.content.trim();
  
  console.log(`   视觉模型原始响应："${content}"`);
  
  // 检查是否是无法识别
  if (content.toUpperCase() === 'UNRECOGNIZABLE' || content.length === 0) {
    throw new Error('视觉模型无法识别验证码');
  }
  
  // 尝试提取纯字母数字（去除可能的标点、空格等）
  const cleanedText = content.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
  
  if (cleanedText.length === 0) {
    throw new Error('视觉模型返回的内容不包含有效字符');
  }
  
  console.log(`   清洗后验证码："${cleanedText}"`);
  
  return { captchaText: cleanedText, rawResponse: content };
}

// 不再裁剪验证码区域，直接使用全屏截图
// Qwen VL 可以自行识别全屏截图中的验证码位置

async function fillInContext(context, captchaText, contextName = '主页面') {
  // ========== 策略 1: 精确选择器匹配（按优先级排序）==========
  // 高优先级：id/name 包含 captcha（更可靠）
  const highPrioritySelectors = [
    'input[id*="captcha" i]',
    'input[name*="captcha" i]',
    'input[aria-label*="captcha" i]'
  ];
  
  // 中优先级：placeholder 包含验证码相关词（但不包含 search/query）
  const mediumPrioritySelectors = [
    'input[placeholder*="验证码"]',
    'input[placeholder*="verification code" i]',
    'input[placeholder*="security code" i]'
  ];

  console.log('   尝试高优先级选择器（id/name 包含 captcha）...');
  for (const selector of highPrioritySelectors) {
    const inputs = await context.locator(selector).all();
    if (inputs.length > 0) {
      console.log(`   选择器 "${selector}" 找到 ${inputs.length} 个元素`);
    }
    for (const input of inputs) {
      try {
        if (await input.isVisible()) {
          await input.fill(captchaText);
          const id = await input.getAttribute('id');
          const name = await input.getAttribute('name');
          console.log(`✅ 已填写到输入框 (${contextName}, ${selector}) - id="${id || ''}", name="${name || ''}"`);
          return true;
        }
      } catch (e) {}
    }
  }
  
  console.log('   高优先级未找到，尝试中优先级选择器（placeholder）...');
  for (const selector of mediumPrioritySelectors) {
    const inputs = await context.locator(selector).all();
    for (const input of inputs) {
      try {
        if (await input.isVisible()) {
          await input.fill(captchaText);
          const id = await input.getAttribute('id');
          const name = await input.getAttribute('name');
          console.log(`✅ 已填写到输入框 (${contextName}, ${selector}) - id="${id || ''}", name="${name || ''}"`);
          return true;
        }
      } catch (e) {}
    }
  }

  // ========== 策略 2: 获取所有输入框，用 accessibility 信息判断 ==========
  console.log(`   ⚠️ 精确匹配失败，尝试 accessibility 分析...`);
  
  // 获取页面上所有 input 元素（不限制 type）
  const allInputs = await context.locator('input').all();
  
  // 排除关键词
  const excludeKeywords = ['search', 'query', 'email', 'username', 'password', 'phone', 'tel', 'hidden'];
  
  // 验证码相关关键词（用于加分）
  const captchaKeywords = ['captcha', '验证码', 'image', 'code', 'verify', 'answer'];
  
  let bestCandidate = null;
  let bestScore = 0;
  
  for (const input of allInputs) {
    try {
      // 检查是否可见
      if (!await input.isVisible()) continue;
      
      // 获取边界框
      const box = await input.boundingBox();
      if (!box || box.width < 50 || box.width > 400 || box.height < 15 || box.height > 100) continue;
      
      // 跳过 hidden 类型
      const type = await input.getAttribute('type');
      if (type === 'hidden' || type === 'submit' || type === 'button') continue;
      
      // 收集 accessibility 信息
      const placeholder = (await input.getAttribute('placeholder')) || '';
      const name = (await input.getAttribute('name')) || '';
      const id = (await input.getAttribute('id')) || '';
      const ariaLabel = (await input.getAttribute('aria-label')) || '';
      const role = await input.getAttribute('role') || '';
      
      const allText = (placeholder + ' ' + name + ' ' + id + ' ' + ariaLabel + ' ' + role).toLowerCase();
      
      // 排除明显不是验证码的
      const isExcluded = excludeKeywords.some(kw => allText.includes(kw));
      if (isExcluded) continue;
      
      // 计算匹配分数
      let score = 0;
      
      // 尺寸加分（验证码输入框通常较小）
      if (box.width >= 80 && box.width <= 250) score += 10;
      if (box.height >= 30 && box.height <= 60) score += 5;
      
      // 关键词加分
      for (const kw of captchaKeywords) {
        if (allText.includes(kw)) score += 20;
      }
      
      // placeholder 存在加分
      if (placeholder) score += 5;
      
      // aria-label 存在加分（说明有无障碍标识）
      if (ariaLabel) score += 10;
      
      console.log(`   候选输入框：id="${id || ''}", placeholder="${placeholder.substring(0, 30)}", score=${score}`);
      
      if (score > bestScore) {
        bestScore = score;
        bestCandidate = input;
      }
      
    } catch (e) {
      // 跳过无法访问的元素
    }
  }
  
  // 如果找到最佳候选，填写它
  if (bestCandidate && bestScore > 0) {
    try {
      await bestCandidate.fill(captchaText);
      console.log(`✅ 已填写到输入框 (accessibility 评分：${bestScore})`);
      return true;
    } catch (e) {
      console.log(`   ⚠️ 填写失败：${e.message}`);
    }
  }
  
  // ========== 策略 3: 位置启发式 - 找验证码图片附近的输入框 ==========
  console.log(`   ⚠️ accessibility 分析未找到，尝试基于位置查找...`);
  try {
    const captchaImgSelectors = [
      'img[alt*="captcha" i]',
      'img[id*="captcha" i]',
      'img[class*="captcha" i]',
      'img[src*="captcha" i]'
    ];
    
    for (const selector of captchaImgSelectors) {
      const captchaImg = context.locator(selector).first();
      if (await captchaImg.count() > 0) {
        const captchaBox = await captchaImg.boundingBox();
        if (captchaBox) {
          for (const input of allInputs) {
            try {
              const box = await input.boundingBox();
              if (box && await input.isVisible()) {
                const verticalDist = Math.abs((box.y + box.height/2) - (captchaBox.y + captchaBox.height/2));
                const horizontalDist = Math.abs((box.x + box.width/2) - (captchaBox.x + captchaBox.width/2));
                
                // 如果在附近，很可能是验证码输入框
                if (verticalDist < 150 && horizontalDist < 400) {
                  await input.fill(captchaText);
                  console.log(`✅ 基于位置找到输入框 (距离验证码：垂直${verticalDist.toFixed(0)}px, 水平${horizontalDist.toFixed(0)}px)`);
                  return true;
                }
              }
            } catch (e) {}
          }
        }
        break; // 找到验证码图片后只处理一次
      }
    }
  } catch (e) {
    console.log(`   ⚠️ 位置查找失败：${e.message}`);
  }
  
  // ========== 策略 4: 最后手段 - 填写第一个合适的可见输入框 ==========
  console.log(`   ⚠️ 位置查找失败，尝试第一个可见输入框...`);
  for (const input of allInputs) {
    try {
      if (await input.isVisible()) {
        const type = await input.getAttribute('type');
        if (type === 'hidden' || type === 'submit' || type === 'button') continue;
        
        const box = await input.boundingBox();
        if (box && box.width > 50 && box.width < 400) {
          await input.fill(captchaText);
          console.log(`✅ 已填写到第一个可见输入框`);
          return true;
        }
      }
    } catch (e) {}
  }
  
  return false;
}

async function fillAndSubmit(page, captchaText, outputPrefix) {
  console.log('\n🔍 查找验证码输入框...');
  
  let inputFound = await fillInContext(page, captchaText, '主页面');
  
  if (!inputFound) {
    console.log('⚠️ 主页面未找到输入框，检查 iframe...');
    const frames = page.frames();
    console.log(`   找到 ${frames.length} 个 frame`);
    
    for (const frame of frames) {
      if (frame === page.mainFrame()) continue;
      
      console.log(`   尝试 iframe: ${frame.name() || frame.url().substring(0, 50)}`);
      inputFound = await fillInContext(frame, captchaText, 'iframe');
      if (inputFound) {
        console.log('✅ 在 iframe 中找到并填写输入框');
        break;
      }
    }
    
    if (!inputFound) {
      console.log('⚠️ iframe 中也未找到输入框');
    }
  }

  const filledPath = path.join(WORKSPACE_DIR, `${outputPrefix}_filled.png`);
  await page.screenshot({ path: filledPath, fullPage: true });
  if (inputFound) {
    console.log(`✅ 填写后截图：${outputPrefix}_filled.png`);
  } else {
    console.log(`⚠️ 未找到输入框，已截图：${outputPrefix}_filled.png`);
    console.log(`💡 验证码已识别，请手动填写并提交`);
  }

  // ========== 查找并点击提交按钮 ==========
  console.log('\n🔍 查找验证按钮...');
  
  // 策略 1: 文本匹配按钮
  const buttonSelectors = [
    'button:has-text("Validate")',
    'button:has-text("Submit")',
    'button:has-text("验证")',
    'button:has-text("提交")',
    'button:has-text("Check")',
    'input[type="submit"]',
    'button[type="submit"]'
  ];

  let buttonFound = false;
  for (const selector of buttonSelectors) {
    const buttons = await page.locator(selector).all();
    for (const btn of buttons) {
      try {
        const text = await btn.textContent().catch(() => '');
        const value = await btn.getAttribute('value').catch(() => '');
        
        if (/validate|submit|verify|check|确认 | 提交 | 验证 | 登录/i.test(text + value)) {
          await btn.click();
          console.log(`✅ 已点击：${selector} (${text || value})`);
          buttonFound = true;
          break;
        }
      } catch (e) {}
    }
    if (buttonFound) break;
  }

  // 策略 2: accessibility 分析找按钮
  if (!buttonFound) {
    console.log('⚠️ 文本匹配失败，尝试 accessibility 分析...');
    
    const allButtons = await page.locator('button, input[type="submit"], input[type="button"]').all();
    
    // 按钮相关关键词
    const buttonKeywords = ['submit', 'validate', 'verify', 'check', '确认', '提交', '验证', '登录', 'ok', 'go'];
    const excludeKeywords = ['menu', 'header', 'nav', 'open', 'close', 'toggle', 'cancel', 'back'];
    
    let bestBtn = null;
    let bestScore = 0;
    
    for (const btn of allButtons) {
      try {
        if (!await btn.isVisible()) continue;
        
        const box = await btn.boundingBox();
        if (!box || box.width < 40 || box.width > 250 || box.height < 25 || box.height > 100) continue;
        
        const text = (await btn.textContent().catch(() => '')).toLowerCase();
        const ariaLabel = (await btn.getAttribute('aria-label')) || '';
        const name = (await btn.getAttribute('name')) || '';
        const value = (await btn.getAttribute('value')) || '';
        
        const allText = (text + ' ' + ariaLabel + ' ' + name + ' ' + value).toLowerCase();
        
        // 排除明显不是提交按钮的
        const isExcluded = excludeKeywords.some(kw => allText.includes(kw));
        if (isExcluded) continue;
        
        // 计算分数
        let score = 0;
        
        // 关键词加分
        for (const kw of buttonKeywords) {
          if (allText.includes(kw)) score += 20;
        }
        
        // 按钮位置加分（验证码按钮通常在输入框下方）
        if (inputFound) {
          const inputs = await page.locator('input').all();
          for (const input of inputs) {
            try {
              const inputBox = await input.boundingBox();
              if (inputBox) {
                const verticalDist = box.y - (inputBox.y + inputBox.height);
                if (verticalDist >= 0 && verticalDist < 100) {
                  score += 15; // 在输入框下方附近
                }
              }
            } catch (e) {}
          }
        }
        
        // 尺寸适中加分
        if (box.width >= 60 && box.width <= 150) score += 5;
        if (box.height >= 30 && box.height <= 60) score += 5;
        
        console.log(`   候选按钮：text="${text.substring(0, 20)}", score=${score}`);
        
        if (score > bestScore) {
          bestScore = score;
          bestBtn = btn;
        }
        
      } catch (e) {}
    }
    
    if (bestBtn && bestScore > 0) {
      try {
        await bestBtn.click();
        console.log(`✅ 已点击最佳候选按钮 (accessibility 评分：${bestScore})`);
        buttonFound = true;
      } catch (e) {
        console.log(`   ⚠️ 点击失败：${e.message}`);
      }
    }
  }

  // 策略 3: 位置启发式 - 找输入框附近的按钮
  if (!buttonFound && inputFound) {
    console.log('⚠️ accessibility 分析未找到，尝试基于位置查找...');
    try {
      const inputs = await page.locator('input').all();
      for (const input of inputs) {
        try {
          const inputBox = await input.boundingBox();
          if (inputBox) {
            const buttons = await page.locator('button').all();
            for (const btn of buttons) {
              try {
                const box = await btn.boundingBox();
                if (box && await btn.isVisible()) {
                  const verticalDist = Math.abs((box.y + box.height/2) - (inputBox.y + inputBox.height/2));
                  const horizontalDist = Math.abs((box.x + box.width/2) - (inputBox.x + inputBox.width/2));
                  
                  if (verticalDist < 100 && horizontalDist < 300) {
                    await btn.click();
                    console.log(`✅ 基于位置点击按钮 (距离输入框：垂直${verticalDist.toFixed(0)}px, 水平${horizontalDist.toFixed(0)}px)`);
                    buttonFound = true;
                    break;
                  }
                }
              } catch (e) {}
            }
            if (buttonFound) break;
          }
        } catch (e) {}
      }
    } catch (e) {
      console.log(`   ⚠️ 位置查找失败：${e.message}`);
    }
  }

  if (!buttonFound) {
    console.log('⚠️ 未找到合适的提交按钮');
  }

  return { inputFound, buttonFound };
}

async function recognizeCaptcha(options = {}) {
  const {
    url,
    outputPrefix = 'smart_captcha',
    apiKey,
    baseUrl,
    model,
    skipLocal = false
  } = options;

  const config = loadConfig({ apiKey, baseUrl, model });

  console.log('⚠️  安全提示：本技能会截取网页截图并发送到阿里云 API');
  console.log('   请勿在包含敏感信息的页面使用');
  console.log('');
  console.log('🤖 Captcha Auto Skill v1.0.2 (混合模式)');
  console.log('=' .repeat(60));
  console.log('🚀 智能验证码识别 - 本地 OCR + 视觉模型降级');
  console.log('=' .repeat(60));
  console.log(`目标：${url}`);
  console.log(`系统：${os.platform()}`);
  console.log(`视觉模型：${config.model}`);
  console.log('=' .repeat(60));

  const executablePath = getChromePath();
  console.log(`浏览器：${executablePath}`);

  if (!fs.existsSync(executablePath)) {
    console.error(`❌ 未找到 Chrome: ${executablePath}`);
    return { success: false, error: 'Chrome not found', screenshots: {} };
  }

  if (!fs.existsSync(WORKSPACE_DIR)) {
    fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: true,
    executablePath,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  const screenshots = {};
  let recognitionMethod = null;

  try {
    console.log('\n📄 打开页面...');
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    console.log('\n📸 截图页面...');
    screenshots.page = path.join(WORKSPACE_DIR, `${outputPrefix}_page.png`);
    await page.screenshot({ path: screenshots.page, fullPage: true });
    console.log(`✅ 页面已截图：${outputPrefix}_page.png`);

    let captchaText = null;
    let analysis = null;

    // 策略 1：本地 Tesseract OCR（仅当截图较小且清晰时有效）
    // 注意：全屏截图会导致 Tesseract 识别所有页面文字，所以跳过
    if (!skipLocal) {
      console.log('⚠️ 全屏截图模式下跳过本地 OCR（会识别整个页面文字）');
    }

    // 策略 2：视觉模型识别（使用全屏截图）
    try {
      // 重新截图确保验证码未刷新
      console.log('📸 重新截图（确保验证码未刷新）...');
      await page.waitForTimeout(1000);
      screenshots.page = path.join(WORKSPACE_DIR, `${outputPrefix}_page.png`);
      await page.screenshot({ path: screenshots.page, fullPage: true });
      
      analysis = await analyzePageWithVision(screenshots.page, config);
      captchaText = analysis.captchaText || '';
      
      if (!captchaText) {
        throw new Error('视觉模型未能识别验证码文字');
      }
      
      recognitionMethod = 'vision';
      console.log(`✅ 视觉模型识别成功：${captchaText}`);
      
    } catch (visionError) {
      throw new Error(`视觉模型识别失败：${visionError.message}`);
    }

    const { inputFound, buttonFound } = await fillAndSubmit(page, captchaText, outputPrefix);

    console.log('\n⏳ 等待结果...');
    await page.waitForTimeout(4000);

    screenshots.result = path.join(WORKSPACE_DIR, `${outputPrefix}_result.png`);
    await page.screenshot({ path: screenshots.result, fullPage: true });
    console.log(`✅ 结果截图：${outputPrefix}_result.png`);

    console.log('');
    console.log('='.repeat(60));
    console.log('🎉 智能验证码识别完成！');
    console.log(`识别内容：${captchaText}`);
    console.log(`识别方式：${recognitionMethod === 'tesseract' ? '本地 Tesseract OCR' : '视觉模型'}`);
    
    if (!inputFound) {
      console.log('⚠️ 自动填写失败，请手动填写验证码');
    }
    console.log('='.repeat(60));

    return { 
      success: true, 
      text: captchaText, 
      method: recognitionMethod,
      inputFilled: inputFound,
      buttonClicked: buttonFound,
      analysis,
      screenshots,
      metadata: {
        url,
        model: config.model,
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    screenshots.error = path.join(WORKSPACE_DIR, `${outputPrefix}_error.png`);
    await page.screenshot({
      path: screenshots.error,
      fullPage: true
    });
    return { success: false, error: error.message, screenshots };
  } finally {
    await browser.close();
  }
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
智能验证码自动识别 Skill v1.0.2 (混合模式)

用法:
  node scripts/run.mjs --url="<url>" [选项]

选项:
  --url=<url>         目标页面 URL（必需）
  --prefix=<prefix>   输出文件前缀（可选，默认：smart_captcha）
  --api-key=<key>     视觉模型 API Key（可选，覆盖环境变量）
  --base-url=<url>    API 服务端点（可选）
  --model=<model>     模型名称（可选，默认：qwen3-vl-plus）
  --skip-local        跳过本地 OCR，直接使用视觉模型
  --json              输出 JSON 格式（方便程序解析）
  --help              显示帮助

识别策略:
  1. 本地 Tesseract OCR（快速、零成本）- 仅识别，不提交
  2. 置信度 < 60% → 重新截图 → 视觉模型降级
  3. 智能填写（主页面 → iframe）
  4. 填写失败 → 告知用户手动填写

必需配置:
  - 环境变量：VISION_API_KEY, VISION_BASE_URL, VISION_MODEL
  - 或 OpenClaw 配置：~/.openclaw/openclaw.json
  - 或命令行参数：--api-key, --base-url, --model
`);
    return;
  }

  const options = {};
  for (const arg of args) {
    if (arg.startsWith('--url=')) options.url = arg.substring(6);
    if (arg.startsWith('--prefix=')) options.outputPrefix = arg.substring(9);
    if (arg.startsWith('--api-key=')) options.apiKey = arg.substring(10);
    if (arg.startsWith('--base-url=')) options.baseUrl = arg.substring(11);
    if (arg.startsWith('--model=')) options.model = arg.substring(8);
    if (arg === '--skip-local') options.skipLocal = true;
    if (arg === '--json') options.json = true;
  }

  if (!options.url) {
    console.error('❌ 错误：缺少必需参数 --url');
    console.error('使用 --help 查看帮助');
    process.exit(1);
  }

  const useJson = options.json || process.env.JSON_OUTPUT === '1';
  
  if (!useJson) {
    console.log('🤖 Captcha Auto Skill v1.0.2 (混合模式)');
  }
  
  try {
    const result = await recognizeCaptcha(options);
    
    if (useJson) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log('');
      console.log('='.repeat(60));
      if (result.success) {
        console.log(`✅ 完成！验证码：${result.text}`);
        console.log(`识别方式：${result.method === 'tesseract' ? '本地 Tesseract OCR' : '视觉模型'}`);
        if (!result.inputFilled) {
          console.log('⚠️ 自动填写失败，请手动填写验证码');
        }
      } else {
        console.log(`❌ 失败：${result.error}`);
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

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { recognizeCaptcha };
