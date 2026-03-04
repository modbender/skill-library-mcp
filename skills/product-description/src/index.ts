// Product Description Generator - Core Implementation

import OpenAI from 'openai';

const CONFIG = { model: 'gpt-4o', temperature: 0.7 };

interface DescriptionRequest {
  product: string;
  platform: 'taobao' | 'tmall' | 'jd' | 'xiaohongshu' | 'amazon' | 'shopify';
  tone: 'promotional' | 'emotional' | 'humor' | 'professional';
  highlights?: string[];
}

interface DescriptionResult {
  title: string;
  description: string;
  sellingPoints: string[];
  tags: string[];
}

const PLATFORM_STYLES: Record<string, { style: string; titleStyle: string; tags: string }> = {
  taobao: { style: '卖点突出、促销感强、口语化', titleStyle: '关键词堆砌+促销词', tags: '#淘宝#好物推荐' },
  tmall: { style: '品质感、专业、权威', titleStyle: '品牌感+卖点', tags: '#天猫#品质生活' },
  jd: { style: '参数导向、理性分析', titleStyle: '卖点直接', tags: '#京东#品质保障' },
  xiaohongshu: { style: '真实体验、种草感强、生活方式', titleStyle: '故事+卖点', tags: '#种草#好物分享' },
  amazon: { style: '简洁明了、功能导向', titleStyle: '关键词+核心卖点', tags: '#Amazon#Product' },
  shopify: { style: '品牌感、故事性', titleStyle: '品牌调性+卖点', tags: '#Shopify#Brand' },
};

export async function generateProductDescription(
  request: DescriptionRequest,
  apiKey?: string
): Promise<DescriptionResult> {
  if (!apiKey) throw new Error('OPENAI_API_KEY is required');
  const openai = new OpenAI({ apiKey });
  const platform = PLATFORM_STYLES[request.platform];
  
  const prompt = `生成电商产品描述。

平台：${request.platform}
风格：${platform.style}
语气：${request.tone}
产品：${request.product}
卖点：${request.highlights?.join('、') || '根据产品推理'}

输出JSON格式：{title, description, sellingPoints, tags}`;
  
  const response = await openai.chat.completions.create({
    model: CONFIG.model,
    messages: [{ role: 'user', content: prompt }],
    temperature: CONFIG.temperature,
    response_format: { type: 'json_object' },
  });
  
  return JSON.parse(response.choices[0]?.message?.content || '{}');
}

export default { generateProductDescription };
