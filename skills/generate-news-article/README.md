# Generate News Article Skill

自动从 SerpAPI Google 搜索结果生成多篇独立的 Markdown 文章。

## 功能特点

- 📰 使用 Google 搜索获取内容（不是新闻源）
- 📄 为每条结果生成独立文章
- 🖼️ 自动下载缩略图到 assets 目录
- 📅 按日期组织文章目录
- ✏️ 生成标准 Markdown 格式
- 📝 文件名使用搜索标题

## 安装

```bash
# 克隆或复制此 skill 到 skills 目录
cp -r generate_news_article ~/.openclaw/skills/
```

## 使用方法

### 基本使用（默认关键词）

```bash
generate.sh
```

### 指定关键词

```bash
generate.sh "AI大模型"
```

### 指定关键词和结果数量

```bash
generate.sh "ChatGPT" 10
```

## 输出示例

生成的文章保存在 `output/YYYY-MM-DD/` 目录下，每个搜索结果生成一个独立文件。

### Markdown 格式

每篇文章格式如下：

```markdown
---
title: OpenAI 发布新模型
cover: ./assets/abc123.jpg
---

# OpenAI 发布新模型

OpenAI 今日发布了最新的大语言模型，性能提升显著...

[原文链接](https://example.com/news1)
```

## 目录结构

**Skill 目录：**
```
generate_news_article/
├── SKILL.md              # Skill 文档
├── README.md             # 说明文档
├── _meta.json            # 元数据
├── scripts/
│   └── generate.sh       # 生成脚本
└── .clawhub/
    └── package.json      # ClawHub 配置
```

**输出目录（在 agent 根目录）：**
```
/Users/lihaijian/.openclaw/workspace-wechat-publisher/output/
└── 2026-02-22/
    ├── OpenAI_发布新模型.md
    ├── Google_DeepMind_重大突破.md
    ├── ChatGPT_新功能.md
    ├── AI_行业报告.md
    └── assets/
        ├── abc123.jpg
        ├── def456.jpg
        └── ...
```

## 依赖

- **SerpAPI skill**：必须已安装并配置
- **Python 3**：用于 JSON 解析和图片下载
- **bash**：脚本执行环境

## 配置

确保已设置 SerpAPI API key：

```bash
export SERPAPI_API_KEY=your-api-key
```

## 特性说明

### 自动图片下载

- 如果搜索结果包含缩略图，会自动下载到 `assets/` 目录
- 图片文件名自动从 URL 提取或生成
- 如果下载失败，会在控制台显示警告

### 文件名处理

- 文件名使用搜索标题
- 自动清理特殊字符（<>:"/\\|?*）
- 空格替换为下划线
- 限制最大长度为 100 字符

### 搜索引擎

使用 `serp.py google` 命令，不是 `google_news`，可以获取更广泛的内容。

## 注意事项

1. 确保 SerpAPI skill 已正确安装
2. 检查 API key 是否有效
3. 搜索结果数量受 SerpAPI 限制
4. 图片下载可能因网络或权限原因失败
5. 文章内容仅包含摘要，如需完整内容需要额外处理

## License

MIT
