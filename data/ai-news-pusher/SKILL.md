---
name: ai-news-pusher-v2
description: AI新闻自动获取与推送Skill v2.1。支持Tavily、Brave、RSS多新闻源聚合，无需API Key即可使用RSS源。修复了v2.0的所有实现问题，支持真正的Feishu webhook推送。当用户需要获取AI行业最新动态、自动化新闻推送、多源新闻聚合时触发此Skill。
---

# AI News Pusher v2.1 - AI新闻推送

## 🎉 v2.1 重大更新（修复v2.0所有问题）

**v2.0修复了v1.0的所有问题：**
- ✅ **Tavily API Key现在是可选的** - 没有Key时自动使用RSS源
- ✅ **新增Brave Search API支持** - 更多新闻源选择
- ✅ **RSS源无需API Key** - 始终可用
- ✅ **移除所有硬编码路径** - 使用相对路径
- ✅ **支持真正的Feishu推送** - 需要配置webhook

## 概述

本Skill提供AI新闻的自动获取和推送功能，支持多新闻源聚合：
- **Tavily API** - 高质量AI新闻搜索（可选，需要API Key）
- **Brave Search API** - 额外的新闻源选择（可选，需要API Key）
- **RSS订阅源** - TechCrunch、MIT Tech Review等（无需API Key）

## 🚀 快速开始

### 1. 仅使用RSS源（无需任何API Key）

```bash
# 获取AI新闻（仅RSS源）
python3 scripts/fetch_ai_news.py --source rss --limit 10
```

### 2. 使用Tavily + RSS（推荐）

```bash
# 设置Tavily API Key（可选）
export TAVILY_API_KEY=your_api_key_here

# 获取新闻（Tavily + RSS聚合）
python3 scripts/fetch_ai_news.py --source all --limit 10
```

### 3. 使用Brave Search

```bash
# 设置Brave API Key
export BRAVE_API_KEY=your_brave_api_key

# 使用Brave搜索
python3 scripts/fetch_ai_news.py --source brave --limit 10
```

## 📖 详细使用说明

### 获取AI新闻

```bash
python3 scripts/fetch_ai_news.py [选项]

选项:
  --limit N           返回N条新闻 (默认10)
  --days N            搜索最近N天的新闻 (默认3)
  --source SOURCE     新闻源: tavily|brave|rss|all (默认all)
  --format FORMAT     输出格式: json|text|markdown (默认json)
  --output FILE       输出到文件
  --query QUERY       搜索关键词 (默认: AI artificial intelligence)
```

### 多源新闻聚合

```python
from scripts.news_sources import get_default_aggregator

# 获取聚合器（自动检测可用的API Key）
aggregator = get_default_aggregator(
    include_tavily=True,   # 如果有TAVILY_API_KEY则包含
    include_brave=True,    # 如果有BRAVE_API_KEY则包含
    include_rss=True       # 始终包含RSS
)

# 获取新闻
news = aggregator.fetch_all(
    query="AI artificial intelligence",
    limit=10,
    days=3
)

print(f"共获取 {len(news)} 条新闻")
```

### 推送到Feishu

#### 配置Feishu Webhook

1. 在Feishu群聊中添加"自定义机器人"
2. 获取Webhook URL
3. 设置环境变量：`export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx`

#### 推送新闻

```bash
# 获取并推送新闻
python3 scripts/push_to_feishu.py --limit 8

# 使用多源聚合推送
python3 scripts/push_to_feishu.py --limit 10 --multi-source

# 干运行模式（仅预览，不发送）
python3 scripts/push_to_feishu.py --limit 5 --dry-run
```

### 配置定时推送任务

```bash
# 创建每天9点推送的任务
python3 scripts/schedule_push.py create --time "0 9 * * *" --limit 8

# 使用简写时间格式
python3 scripts/schedule_push.py create --time "09:00" --limit 10

# 测试推送
python3 scripts/schedule_push.py test --limit 5

# 列出所有任务
python3 scripts/schedule_push.py list

# 删除任务
python3 scripts/schedule_push.py delete --job-id <任务ID>
```

## 🔧 环境变量配置

### 可选的API Key（至少需要一个，否则只能使用RSS源）

```bash
# Tavily API Key（可选，推荐）
export TAVILY_API_KEY=your_tavily_api_key

# Brave Search API Key（可选）
export BRAVE_API_KEY=your_brave_api_key
```

### Feishu推送配置（可选）

```bash
# Feishu Webhook URL（用于推送消息到Feishu）
export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
```

### OpenClaw Gateway配置（用于定时任务，可选）

```bash
# OpenClaw Gateway地址（用于定时任务）
export OPENCLAW_GATEWAY_URL=http://localhost:8080

# OpenClaw Gateway令牌（可选）
export OPENCLAW_GATEWAY_TOKEN=your_gateway_token
```

## 📦 依赖项

- Python 3.8+
- tavily-python（可选，仅使用Tavily时需要）
- feedparser（RSS订阅需要）
- requests

安装依赖：

```bash
pip install tavily-python feedparser requests
```

## 🔒 安全注意事项

1. **API Key安全**：不要将API Key硬编码在代码中，使用环境变量
2. **Feishu Webhook**：保护好Webhook URL，不要泄露给他人
3. **网络连接**：RSS源和API调用需要访问外网，请确保网络畅通
4. **定时任务**：使用OpenClaw Cron系统时需要配置Gateway URL

## 🐛 故障排除

### Tavily API错误

- 检查 `TAVILY_API_KEY` 是否正确设置
- 确认API Key是否过期或额度用完
- 如果没有Tavily Key，使用 `--source rss` 仅使用RSS源

### Brave Search错误

- 检查 `BRAVE_API_KEY` 是否正确设置
- 确认API Key是否有搜索额度

### RSS源获取失败

- 检查网络连接
- 确认RSS URL是否有效（可在浏览器中打开测试）
- 某些RSS源可能有访问频率限制

### Feishu推送失败

- 检查 `FEISHU_WEBHOOK_URL` 是否正确设置
- 确认Webhook URL是否有效
- 检查Feishu机器人是否有发送消息权限

### 定时任务不执行

- 检查 `OPENCLAW_GATEWAY_URL` 配置
- 确认Gateway服务是否运行
- 查看Gateway日志排查问题

## 📚 版本历史

### v1.0.0 (2026-03-02)

- 初始版本
- 支持Tavily API和RSS源
- 支持定时任务配置
- 支持推送到Feishu（占位符实现）

### v2.0.0 (2026-03-02)

- **重大改进**：修复了v1.0的所有问题
- Tavily API Key现在是可选的
- 新增Brave Search API支持
- RSS源无需API Key，始终可用
- 移除所有硬编码路径
- 支持真正的Feishu推送（需要配置webhook）
- 改进错误处理和用户提示

## 📞 获取帮助

如果在使用过程中遇到问题，可以：

1. 查看上述故障排除指南
2. 检查环境变量配置
3. 查看脚本输出错误信息
4. 联系Skill作者获取支持

---

**🎉 感谢使用 AI News Pusher v2.0！**