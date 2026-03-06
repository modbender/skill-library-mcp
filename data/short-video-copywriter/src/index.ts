// Short Video Copywriter Skill - Core Implementation

import OpenAI from 'openai';
import { z } from 'zod';

// ============ Configuration ============

const CONFIG = {
  model: 'gpt-4o',
  temperature: 0.8,
} as const;

// ============ Types ============

interface CopyRequest {
  topic: string;
  platform: 'douyin' | 'xiaohongshu' | 'kuaishou' | 'bilibili';
  tone: 'professional' | 'casual' | 'humor' | 'heartwarming';
  length: 'short' | 'medium' | 'long';
}

interface CopyResult {
  hook: string;      // 开头金句
  body: string;      // 正文内容
  hashtags: string[]; // 标签
  tips: string;      // 发布建议
}

// ============ Platform Styles ============

const PLATFORM_STYLES = {
  douyin: {
    style: '节奏快、情绪化、追求爆款、口语化',
    hashtagStyle: '热门挑战、流行梗、#推荐',
    length: '15-30秒口语稿，约50-80字',
  },
  xiaohongshu: {
    style: '真实感、生活方式种草、个人体验分享',
    hashtagStyle: '生活方式标签、#推荐、#种草',
    length: '200-500字，包含个人故事',
  },
  kuaishou: {
    style: '接地气、真诚、接地气、东北话/方言',
    hashtagStyle: '生活标签、#记录生活',
    length: '30-60秒，口语化',
  },
  bilibili: {
    style: '深度、二次元、玩梗、弹幕文化',
    hashtagStyle: '分区标签、#梗、#经典',
    length: '灵活，取决于内容深度',
  },
} as const;

// ============ Tone Mapping ============

const TONE_MAP = {
  professional: '专业、干货输出、权威感',
  casual: '轻松、日常、朋友聊天',
  humor: '搞笑、段子、反转、玩梗',
  heartwarming: '温暖、治愈、情感共鸣',
} as const;

// ============ Prompt Builder ============

function buildPrompt(request: CopyRequest): string {
  const platform = PLATFORM_STYLES[request.platform];
  
  return `你是一个专业的短视频文案专家。

## 任务
根据以下信息，生成适合${request.platform}平台的短视频文案。

## 平台特点
- 文案风格：${platform.style}
- 标签风格：${platform.hashtagStyle}
- 长度要求：${platform.length}
- 语气要求：${TONE_MAP[request.tone]}

## 长度控制
- short: ${request.platform === 'xiaohongshu' ? '100-200字' : '15-30秒'}
- medium: ${request.platform === 'xiaohongshu' ? '300-500字' : '30-60秒'}
- long: ${request.platform === 'xiaohongshu' ? '500-800字' : '60-90秒'}

## 用户需求
主题：${request.topic}

## 输出格式（JSON）
{
  "hook": "开头金句（3秒抓住观众）",
  "body": "正文内容",
  "hashtags": ["标签1", "标签2", "标签3"],
  "tips": "1-2条发布建议"
}

要求：
1. hook 要有冲击力，能抓住眼球
2. body 要围绕主题展开，不要废话
3. hashtags 要选择平台热门标签
4. tips 要有实操性

只输出JSON，不要其他内容。`;
}

// ============ Main Function ============

export async function generateShortVideoCopy(
  request: CopyRequest,
  apiKey?: string
): Promise<CopyResult> {
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is required');
  }

  const openai = new OpenAI({ apiKey });
  
  const prompt = buildPrompt(request);

  try {
    const response = await openai.chat.completions.create({
      model: CONFIG.model,
      messages: [
        {
          role: 'system',
          content: '你是一个专业的短视频文案专家，擅长生成各平台的爆款文案。'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: CONFIG.temperature,
      response_format: { type: 'json_object' },
    });

    const content = response.choices[0]?.message?.content || '{}';
    const result = JSON.parse(content);

    return {
      hook: result.hook || '生成的文案',
      body: result.body || '',
      hashtags: Array.isArray(result.hashtags) ? result.hashtags : [],
      tips: result.tips || '按时发布，保持互动',
    };
  } catch (error) {
    throw new Error(`Failed to generate copy: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// ============ CLI Mode ============

if (require.main === module) {
  const readline = require('readline');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  async function interactive() {
    console.log('\n🎬 短视频文案生成器\n');
    
    const topic = await ask('📝 请输入视频主题: ');
    const platform = await choose('📱 选择平台: ', ['douyin', 'xiaohongshu', 'kuaishou', 'bilibili']);
    const tone = await choose('🎨 选择风格: ', ['professional', 'casual', 'humor', 'heartwarming']);
    const length = await choose('📏 选择长度: ', ['short', 'medium', 'long']);

    console.log('\n✨ 正在生成...\n');

    const result = await generateShortVideoCopy({
      topic,
      platform: platform as CopyRequest['platform'],
      tone: tone as CopyRequest['tone'],
      length: length as CopyRequest['length'],
    });

    console.log('='.repeat(50));
    console.log('\n🎯 开头金句：');
    console.log(result.hook);
    console.log('\n📝 正文内容：');
    console.log(result.body);
    console.log('\n🏷️ 推荐标签：');
    console.log(result.hashtags.join(' '));
    console.log('\n💡 发布建议：');
    console.log(result.tips);
    console.log('\n' + '='.repeat(50));

    rl.close();
  }

  function ask(question: string): Promise<string> {
    return new Promise(resolve => rl.question(question, resolve));
  }

  function choose(question: string, options: string[]): Promise<string> {
    return new Promise(resolve => {
      console.log(question);
      options.forEach((opt, i) => console.log(`  ${i + 1}. ${opt}`));
      rl.question('> ', (answer: string) => {
        const idx = parseInt(answer) - 1;
        resolve(options[idx] || options[0]);
      });
    });
  }

  interactive().catch(console.error);
}

export default { generateShortVideoCopy };
