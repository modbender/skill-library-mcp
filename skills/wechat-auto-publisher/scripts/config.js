/**
 * 微信公众号全自动发布系统 - 配置文件
 */

module.exports = {
  // ========== 公众号配置 ==========
  // 填写你的公众号信息（从公众号后台获取）
  wechat: {
    // 公众号 AppID
    appId: '',
    // 公众号 AppSecret
    appSecret: '',
    // 公众号名称（用于日志）
    name: 'AI 科技日报'
  },

  // ========== 大模型 API 配置 ==========
  // 百炼 API（通义千问）
  llm: {
    // API 地址（百炼兼容 OpenAI 格式）
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    // 模型选择
    model: 'qwen-plus',
    // 生成温度（0-1，越高越有创意）
    temperature: 0.7,
    // 最大生成长度
    maxTokens: 2000
  },

  // ========== 选题配置 ==========
  topics: {
    // 赛道关键词（AI/科技）
    keywords: [
      'AI', '人工智能', '大模型', 'GPT',
      '科技', '互联网', '数码', '软件',
      '创业', '副业', '效率工具', '自动化'
    ],
    // 排除关键词
    excludeKeywords: [
      '娱乐', '明星', '八卦', '游戏'
    ],
    // 最低热度阈值
    minHotValue: 50
  },

  // ========== 内容生成配置 ==========
  content: {
    // 文章风格
    style: '专业但不失幽默，用通俗易懂的语言讲解技术',
    // 目标读者
    audience: '25-40 岁，对科技感兴趣的职场人士',
    // 文章长度（字数）
    targetLength: 1500,
    // 是否自动生成标题（3 个备选）
    autoGenerateTitles: true
  },

  // ========== 发布配置 ==========
  publish: {
    // 是否自动发布（false=生成后人工审核）
    autoPublish: false,
    // 发布时间（24 小时制，如 "09:00"）
    publishTime: '09:00',
    // 发布频率（每天几篇）
    postsPerDay: 2
  },

  // ========== 数据源配置 ==========
  sources: {
    // 微博热搜
    weibo: {
      enabled: true,
      url: 'https://weibo.com/ajax/side/hotSearch'
    },
    // 知乎热榜
    zhihu: {
      enabled: true,
      url: 'https://www.zhihu.com/api/v3/feed/topstory/hot-list'
    },
    // 36 氪
    huxiu: {
      enabled: true,
      url: 'https://www.huxiu.com/article/'
    },
    // Product Hunt（科技产品）
    productHunt: {
      enabled: false,
      url: 'https://api.producthunt.com/v2/api/graphql'
    }
  },

  // ========== 存储配置 ==========
  storage: {
    // 数据存放目录
    dataDir: './data',
    // 文章草稿目录
    draftsDir: './drafts',
    // 日志目录
    logsDir: './logs'
  }
};
