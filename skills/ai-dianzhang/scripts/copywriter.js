#!/usr/bin/env node
/**
 * AI店长 - 爆款文案生成模块
 * 根据商品信息生成多平台适配的电商文案
 */

// 平台文案风格模板
const PLATFORM_STYLES = {
  taobao: {
    name: '淘宝/天猫',
    titleRules: [
      '标题上限60字符（30个汉字）',
      '核心关键词前置',
      '品牌词+品类词+属性词+场景词+促销词',
      '不要用特殊符号和emoji',
      '避免极限词（最好、第一、顶级）'
    ],
    descStyle: '专业详细，突出参数和卖点，适合搜索场景',
    example: '【品牌】露营折叠椅户外便携超轻铝合金靠背椅野餐钓鱼沙滩椅子'
  },
  pdd: {
    name: '拼多多',
    titleRules: [
      '标题上限120字符（60个汉字）',
      '价格优势词前置（特价/清仓/工厂直销）',
      '堆叠长尾关键词提高搜索覆盖',
      '突出性价比和实用性',
      '可以适当重复关键词'
    ],
    descStyle: '简单直接，突出便宜和实用，适合价格敏感用户',
    example: '露营折叠椅户外便携式超轻小型靠背椅子野餐钓鱼椅沙滩椅铝合金折叠椅子特价'
  },
  xiaohongshu: {
    name: '小红书',
    titleRules: [
      '标题上限20字',
      '用emoji开头吸引眼球',
      '制造好奇心或共鸣感',
      '口语化、生活化',
      '适当用感叹号和问号'
    ],
    descStyle: '种草风格，第一人称分享体验，多用emoji和换行，标签很重要',
    example: '🏕️ 这把露营椅也太绝了吧！轻到单手就能拎走'
  },
  douyin: {
    name: '抖音',
    titleRules: [
      '短视频标题15字以内',
      '制造冲突或悬念',
      '口语化，像跟朋友说话',
      '带话题标签 #露营 #好物推荐'
    ],
    descStyle: '短平快，前3秒抓住注意力，口播风格',
    example: '这椅子我吹爆！露营党必入 #露营装备 #好物分享'
  },
  alibaba: {
    name: '1688',
    titleRules: [
      '突出工厂/源头/批发属性',
      '标注起批量和价格优势',
      '材质+工艺+规格要详细',
      '适合B端采购搜索'
    ],
    descStyle: '专业B端风格，突出工厂实力、质检报告、定制能力',
    example: '户外折叠椅厂家直销 铝合金超轻便携靠背椅 支持定制LOGO 100把起批'
  }
};

// 文案类型模板
const COPY_TEMPLATES = {
  title: {
    name: '商品标题',
    prompt: (product, platform) => {
      const style = PLATFORM_STYLES[platform] || PLATFORM_STYLES.taobao;
      return `你是一个${style.name}平台的资深运营。请为以下商品生成5个优化标题。

商品信息：${product}

平台规则：
${style.titleRules.map(r => `- ${r}`).join('\n')}

参考示例：${style.example}

请生成5个标题方案，每个标题后标注核心关键词。格式：
1. [标题] — 关键词：xxx, xxx, xxx
2. ...`;
    }
  },

  detail: {
    name: '详情页文案',
    prompt: (product, platform) => `你是一个电商详情页文案专家。请为以下商品生成完整的详情页文案。

商品信息：${product}

请按以下结构输出：

## 一句话卖点
（20字以内，核心价值主张）

## 五大卖点
1. 【卖点标题】详细描述...
2. ...

## 使用场景
（3-4个具体使用场景，带画面感）

## 产品参数
（表格形式，列出关键参数）

## 常见问题FAQ
（5个买家最关心的问题和回答）

## 好评引导语
（引导买家晒图好评的温馨话术）

文案风格要求：专业但不生硬，有温度，突出差异化。`
  },

  xiaohongshu_note: {
    name: '小红书笔记',
    prompt: (product) => `你是一个小红书爆款笔记写手。请为以下商品写一篇种草笔记。

商品信息：${product}

要求：
- 标题：20字以内，emoji开头，制造好奇心
- 正文：第一人称分享，口语化，300-500字
- 多用emoji分隔段落
- 结尾带互动引导（"你们觉得呢？""有同款的姐妹吗？"）
- 生成10个相关标签（#xxx）
- 配图建议（描述应该拍什么样的图）

请输出完整笔记内容。`
  },

  live_script: {
    name: '直播话术',
    prompt: (product) => `你是一个直播带货话术专家。请为以下商品写一套完整的直播话术。

商品信息：${product}

请按以下环节输出：

## 1. 开场预热（30秒）
（制造期待，预告福利）

## 2. 产品展示（2分钟）
（边展示边讲解，突出卖点）

## 3. 痛点共鸣（1分钟）
（描述没有这个产品时的痛苦场景）

## 4. 价格锚定（30秒）
（对比其他渠道价格，突出直播间优势）

## 5. 逼单话术（1分钟）
（限时限量，制造紧迫感）

## 6. 售后承诺（15秒）
（打消顾虑，7天无理由等）

## 7. 感谢互动（15秒）
（引导关注、点赞、分享）

话术风格：自然口语化，像跟朋友聊天，有感染力。`
  },

  customer_service: {
    name: '客服话术库',
    prompt: (product) => `你是一个电商客服培训专家。请为以下商品生成完整的客服话术库。

商品信息：${product}

请生成以下类别的话术：

## 售前话术
### 欢迎语（3种风格）
### 商品咨询回复（针对常见问题）
### 尺寸/规格咨询
### 发货时间咨询
### 优惠活动咨询
### 催付话术（温柔不烦人，3种）

## 售后话术
### 物流查询
### 退换货处理
### 质量问题回复
### 差评挽回话术（3种场景）
### 好评引导（不违规）

## 特殊场景
### 砍价回复（委婉拒绝+引导下单）
### 竞品对比回复（不贬低对手）
### 缺货回复（推荐替代+预约）

每条话术要求：专业、温暖、高效，不用机器人腔调。`
  }
};

/**
 * 生成文案的 prompt
 * @param {string} product - 商品描述
 * @param {string} copyType - 文案类型 (title/detail/xiaohongshu_note/live_script/customer_service)
 * @param {string} platform - 平台 (taobao/pdd/xiaohongshu/douyin/alibaba)
 */
function buildCopyPrompt(product, copyType = 'title', platform = 'taobao') {
  const template = COPY_TEMPLATES[copyType];
  if (!template) {
    throw new Error(`未知文案类型: ${copyType}。可选: ${Object.keys(COPY_TEMPLATES).join(', ')}`);
  }
  return template.prompt(product, platform);
}

/**
 * 一键生成全平台文案的 prompt
 */
function buildAllPlatformPrompt(product) {
  const platforms = Object.entries(PLATFORM_STYLES)
    .map(([id, style]) => {
      return `### ${style.name}
规则：${style.titleRules.slice(0, 3).join('；')}
风格：${style.descStyle}`;
    })
    .join('\n\n');

  return `你是一个全平台电商运营专家。请为以下商品生成适配5个平台的标题和核心文案。

商品信息：${product}

${platforms}

请为每个平台分别输出：
1. 优化标题（1个最佳方案）
2. 一句话卖点
3. 3个核心关键词

最后给出一个【全平台通用卖点提炼】，不超过50字。`;
}

module.exports = {
  PLATFORM_STYLES,
  COPY_TEMPLATES,
  buildCopyPrompt,
  buildAllPlatformPrompt
};
