# ai-news-daily

AI新闻日报 Skill - 每日自动抓取国内AI领域重要新闻

## 功能

- 自动从量子位、机器之心、InfoQ、36氪、雷锋网、钛媒体、新智元等科技媒体抓取AI新闻
- 智能过滤非AI内容，只保留核心AI新闻
- 抓取正文生成真实摘要（非RSS摘要）
- 按重要性排序，精选Top 10
- 支持定时任务自动推送

## 安装

```bash
clawhub install ai-news-daily
```

## 使用

### 手动运行

```bash
# 抓取今日AI新闻
openclaw skills run ai-news-daily

# 或指定日期
openclaw skills run ai-news-daily --date 2026-02-27
```

### 设置定时任务

```bash
# 每天早上9点自动推送
openclaw skills cron ai-news-daily --schedule "0 9 * * *"
```

### 在对话中使用

```
/ai-news 获取今日AI新闻
/ai-news 3 获取最近3天的AI新闻
```

## 配置

在 `config.yaml` 中可配置：

```yaml
sources:
  - qbitai      # 量子位
  - jiqizhixin  # 机器之心
  - infoq       # InfoQ
  - 36kr        # 36氪
  - leiphone    # 雷锋网
  - tmtpost     # 钛媒体
  - aiera       # 新智元

keywords:
  core: ["AI", "人工智能", "大模型", "DeepSeek", "OpenAI"]
  
schedule:
  enabled: true
  cron: "0 9 * * *"
```

## 输出格式

Markdown格式，包含：
- 新闻标题
- 来源媒体
- 200-300字摘要
- 原文链接

## 依赖

- Python 3.8+
- feedparser
- beautifulsoup4
- requests

## License

MIT
