# URL Reader - 智能网页内容读取器

一键读取任意URL的内容，自动识别平台类型，智能选择最佳读取策略，自动保存内容和图片到本地。

## 功能特点

- 🔍 **智能平台识别**：自动识别微信公众号、小红书、今日头条、抖音、淘宝、天猫、京东、百度、知乎、微博、B站等平台
- 🔄 **三层读取策略**：Firecrawl → Jina → Playwright 自动降级
- 📝 **Markdown输出**：干净的Markdown格式输出
- 💾 **自动保存**：自动保存内容和图片到本地

## 技术架构

```
用户输入 URL
     ↓
┌─────────────┐
│ 平台识别器   │ → 识别URL所属平台
└─────────────┘
     ↓
┌─────────────────────────────────────┐
│           策略选择器                 │
│  Firecrawl → Jina → Playwright      │
│  (首选)     (备选)   (兜底)          │
└─────────────────────────────────────┘
     ↓
┌─────────────┐
│ 内容提取器   │ → 提取标题、正文、作者等
└─────────────┘
     ↓
┌─────────────┐
│ 格式化输出   │ → Markdown 格式
└─────────────┘
```

## 安装

```bash
cd ~/.claude/skills/url-reader
python3 -m venv .venv
source .venv/bin/activate

# 核心依赖
pip install firecrawl-py requests

# Playwright（可选，用于需要登录的平台）
pip install playwright
playwright install chromium
```

## 配置

### Firecrawl API Key

1. 访问 https://www.firecrawl.dev/ 注册账号
2. 获取 API Key
3. 配置环境变量：
   ```bash
   export FIRECRAWL_API_KEY="fc-YOUR_API_KEY"
   ```

## 使用方式

### Claude Code 中使用

```
用户：帮我读取这个链接 https://mp.weixin.qq.com/s/xxxxx
用户：看看这个小红书 https://www.xiaohongshu.com/explore/xxxxx
```

### 命令行调用

```bash
/url-reader https://example.com/article
```

## 支持的平台

| 平台 | 域名 | 推荐策略 |
|------|------|----------|
| 微信公众号 | mp.weixin.qq.com | Firecrawl → Playwright |
| 小红书 | xiaohongshu.com | Firecrawl → Jina |
| 今日头条 | toutiao.com | Firecrawl → Jina |
| 抖音 | douyin.com | Firecrawl |
| 淘宝 | taobao.com | Firecrawl → Playwright |
| 天猫 | tmall.com | Firecrawl → Playwright |
| 京东 | jd.com | Firecrawl → Jina |
| 百度 | baidu.com | Firecrawl → Jina |
| 知乎 | zhihu.com | Firecrawl → Jina |
| 微博 | weibo.com | Firecrawl → Playwright |
| B站 | bilibili.com | Firecrawl → Jina |
| 通用网站 | * | Firecrawl → Jina |

## 目录结构

```
url-reader/
├── skill.md              # Skill文档
├── metadata.json         # 元数据
├── scripts/
│   ├── url_reader.py     # 主读取器
│   ├── url_identifier.py # URL平台识别器
│   ├── save_content.py   # 内容保存
│   └── wechat_reader.py  # 微信读取器
└── data/                 # 数据目录（不上传）
```

## License

MIT
