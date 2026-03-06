# AI Daily - AI 大模型日报

自动从多个异构信息源抓取、筛选、提炼大模型（LLM）和智能体（Agent）领域的 Top 级热点信息与核心论文，生成结构化中文简报。

## 📋 功能特点

- 🔄 **自动化**：定时执行，每日自动生成
- 📰 **多源整合**：RSS + Tavily Search + arXiv
- 🤖 **LLM 降噪**：智能过滤低质量内容
- ⭐ **重要性评级**：1-5 星排序
- 📁 **结构化输出**：四个板块清晰呈现
- 💾 **本地存储**：按日期保存，支持重跑覆盖

## 🚀 快速开始

### 1. 安装

Skill 已位于：
```
/home/admin/.openclaw/workspace/skills/ai-daily/
```

### 2. 配置环境变量（可选但推荐）

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
export TAVILY_API_KEY="your_tavily_api_key"  # 用于 X/Twitter 搜索
export ALIBABA_CLOUD_API_KEY="your_alibaba_key"  # 用于 LLM 处理

# 使配置生效
source ~/.bashrc
```

获取 API Key：
- Tavily: https://app.tavily.com (免费 1000 次/月)
- Alibaba Cloud: https://dashscope.console.aliyun.com

### 3. 生成今日日报

```bash
cd /home/admin/.openclaw/workspace/skills/ai-daily
bash scripts/generate.sh
```

### 4. 查看日报

```bash
# 查看今日
bash scripts/view.sh today

# 查看指定日期
bash scripts/view.sh 2026-02-26

# 直接打开文件
cat output/AI-Daily-2026-02-26.md
```

## 📊 输出示例

```markdown
# 📰 AI 大模型日报 | 2026-02-26

*生成时间：2026-02-26 08:00:00 | 共收录 45 条信息*

---

## 📌 核心大事件总结

### 1. OpenAI 发布 GPT-5 架构细节 ⭐⭐⭐⭐⭐
**来源**: OpenAI Blog | **时间**: 2026-02-25

核心突破：提出新的混合注意力机制，推理速度提升 3 倍...

🔗 [阅读原文](https://openai.com/blog/gpt5-architecture)

...

## 🏢 官方框架更新

- **Anthropic 发布 Claude 3.5 微调 API** (Anthropic)
  - 支持 LoRA 和全参数微调...
  - [链接](https://anthropic.com/...)

...

## 💬 KOL 前沿观点

- **@Andrej Karpathy**: 未来的 LLM 将更多采用 MoE 架构...
  - [链接](https://x.com/...)

...

## 📚 必读硬核论文

### 1. AgentFormer: Agent-Aware Transformers for Multi-Agent Learning ⭐⭐⭐⭐⭐
**作者**: Yuanhan Zhang, Jinming Wu, ...
**分类**: cs.AI, cs.LG
**时间**: 2026-02-25

提出新型多智能体 Transformer 架构...

📄 [PDF](https://arxiv.org/pdf/...) | 📋 [arXiv](https://arxiv.org/abs/...)
```

## ⚙️ 配置说明

### 数据源配置

编辑 `config/sources.json`：

```json
{
  "rssFeeds": {
    "official": [
      {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss",
        "priority": 5  // 1-5，越高越重要
      }
    ]
  },
  "tavilySearch": {
    "kolQueries": [
      {
        "name": "Andrej Karpathy",
        "query": "site:x.com karpathy LLM",
        "priority": 5
      }
    ]
  },
  "arxiv": {
    "categories": ["cs.CL", "cs.AI", "cs.LG"],
    "keywords": ["LLM", "Agent", "Reasoning"]
  }
}
```

### LLM Prompt 配置

编辑 `config/prompts.md` 自定义 AI 处理逻辑。

## ⏰ 定时任务配置

### 方法 1: Cron

```bash
# 编辑 crontab
crontab -e

# 添加每日 8:00 执行
0 8 * * * cd /home/admin/.openclaw/workspace/skills/ai-daily && bash scripts/generate.sh >> /var/log/ai-daily.log 2>&1
```

### 方法 2: OpenClaw Cron Skill

使用 OpenClaw 的 cron 功能设置提醒和自动执行。

### 方法 3: systemd Timer

创建 `/etc/systemd/system/ai-daily.service`：

```ini
[Unit]
Description=AI Daily Report Generator

[Service]
Type=oneshot
ExecStart=/bin/bash /home/admin/.openclaw/workspace/skills/ai-daily/scripts/generate.sh
WorkingDirectory=/home/admin/.openclaw/workspace/skills/ai-daily
```

创建 `/etc/systemd/system/ai-daily.timer`：

```ini
[Unit]
Description=Run AI Daily every day at 8:00

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：
```bash
sudo systemctl enable ai-daily.timer
sudo systemctl start ai-daily.timer
```

## 📁 目录结构

```
ai-daily/
├── SKILL.md           # Skill 定义
├── README.md          # 本文件
├── config/
│   ├── sources.json   # 数据源配置
│   └── prompts.md     # LLM Prompt 模板
├── scripts/
│   ├── ai_daily.py    # 主程序
│   ├── generate.sh    # 生成脚本
│   └── view.sh        # 查看脚本
└── output/            # 输出目录
    ├── AI-Daily-2026-02-26.md
    └── ...
```

## 🔧 命令行参数

```bash
# 生成指定日期
bash scripts/generate.sh --date 2026-02-25

# 指定输出目录
bash scripts/generate.sh --output-dir /path/to/output

# 调试模式（显示详细信息）
bash scripts/generate.sh --debug

# 组合使用
bash scripts/generate.sh --date 2026-02-25 --output-dir ./output --debug
```

## 📈 性能优化建议

1. **并发抓取**：当前为顺序执行，可改为 `asyncio` 并发
2. **缓存机制**：对相同 URL 的内容进行缓存
3. **增量更新**：只抓取新内容，跳过已处理的
4. **分布式**：多数据源可分布到不同机器

## 🐛 故障排查

### 问题：Tavily Search 失败

```
[WARN] TAVILY_API_KEY not set, skipping Tavily search
```

**解决**：设置环境变量
```bash
export TAVILY_API_KEY="your_key"
```

### 问题：RSS 解析失败

```
[WARN] RSS parse error for URL
```

**解决**：检查 URL 是否正确，或该网站是否提供 RSS

### 问题：输出为空

**解决**：
1. 检查网络连接
2. 使用 `--debug` 查看详细信息
3. 检查 `config/sources.json` 配置

## 📝 更新日志

### v1.0.0 (2026-02-26)
- ✅ 初始版本
- ✅ 支持 RSS、Tavily、arXiv 数据源
- ✅ LLM 内容过滤和总结
- ✅ Markdown 格式输出
- ✅ 定时任务支持

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
