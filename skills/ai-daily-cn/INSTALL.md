# AI Daily Skill - 安装与配置指南

## ✅ 安装完成确认

Skill 已成功安装在：
```
/home/admin/.openclaw/workspace/skills/ai-daily/
```

## 📁 目录结构

```
ai-daily/
├── SKILL.md                    # Skill 定义
├── README.md                   # 使用文档
├── INSTALL.md                  # 本文件
├── config/
│   ├── sources.json           # 数据源配置
│   ├── prompts.md             # LLM Prompt 模板
│   └── cron-example.json      # Cron 配置示例
├── scripts/
│   ├── ai_daily.py            # 主程序 (Python)
│   ├── generate.sh            # 生成脚本
│   ├── view.sh                # 查看脚本
│   └── test.sh                # 测试脚本
└── output/                     # 输出目录
    └── AI-Daily-YYYY-MM-DD.md # 每日报告
```

## 🚀 快速开始

### 1. 测试安装

```bash
cd /home/admin/.openclaw/workspace/skills/ai-daily
bash scripts/test.sh
```

### 2. 生成今日日报

```bash
bash scripts/generate.sh
```

### 3. 查看日报

```bash
# 查看今日
bash scripts/view.sh today

# 或直接打开
cat output/AI-Daily-$(date +%Y-%m-%d).md
```

## ⚙️ 配置步骤

### 步骤 1: 配置环境变量（推荐）

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
# Tavily API Key - 用于 X/Twitter 搜索
export TAVILY_API_KEY="tvly-xxxxxxxxxxxxxxxxxxxx"

# Alibaba Cloud API Key - 用于 LLM 处理（可选）
export ALIBABA_CLOUD_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"

# GitHub Token - 用于提高限流（可选）
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

使配置生效：
```bash
source ~/.bashrc
```

获取 API Key：
- **Tavily**: https://app.tavily.com (免费 1000 次/月)
- **Alibaba Cloud**: https://dashscope.console.aliyun.com
- **GitHub**: https://github.com/settings/tokens

### 步骤 2: 自定义数据源

编辑 `config/sources.json`：

```json
{
  "rssFeeds": {
    "official": [
      {
        "name": "你的自定义源",
        "url": "https://example.com/feed.xml",
        "priority": 5
      }
    ]
  },
  "tavilySearch": {
    "kolQueries": [
      {
        "name": "你的 KOL",
        "query": "site:x.com username keyword",
        "priority": 5
      }
    ]
  }
}
```

### 步骤 3: 配置定时任务

#### 选项 A: 使用 Cron

```bash
crontab -e

# 添加每日 8:00 执行
0 8 * * * cd /home/admin/.openclaw/workspace/skills/ai-daily && bash scripts/generate.sh >> /var/log/ai-daily.log 2>&1
```

#### 选项 B: 使用 OpenClaw Cron

```bash
# 查看示例配置
cat config/cron-example.json

# 使用 openclaw cron 命令添加（需要配置）
```

#### 选项 C: 使用 systemd Timer

```bash
# 创建 service
sudo tee /etc/systemd/system/ai-daily.service > /dev/null <<EOF
[Unit]
Description=AI Daily Report Generator

[Service]
Type=oneshot
ExecStart=/bin/bash /home/admin/.openclaw/workspace/skills/ai-daily/scripts/generate.sh
WorkingDirectory=/home/admin/.openclaw/workspace/skills/ai-daily
EOF

# 创建 timer
sudo tee /etc/systemd/system/ai-daily.timer > /dev/null <<EOF
[Unit]
Description=Run AI Daily every day at 8:00

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 启用
sudo systemctl enable ai-daily.timer
sudo systemctl start ai-daily.timer
```

## 📊 输出示例

生成的日报包含四个板块：

1. **📌 核心大事件总结** - 5 星重要性内容
2. **🏢 官方框架更新** - 官方实验室发布
3. **💬 KOL 前沿观点** - 社交媒体动态
4. **📚 必读硬核论文** - arXiv 精选论文

## 🔧 故障排查

### 问题 1: RSS 抓取失败

```
[WARN] Failed to fetch https://example.com/feed: HTTP Error 403
```

**解决**：
- 检查 URL 是否正确
- 某些网站需要网页抓取而非 RSS
- 添加 User-Agent 或使用 web-reader-mcp

### 问题 2: Tavily Search 失败

```
[WARN] Tavily search failed: API key invalid
```

**解决**：
```bash
export TAVILY_API_KEY="your_key"
```

### 问题 3: 输出为空

**解决**：
1. 使用 `--debug` 模式查看详细日志
2. 检查网络连接
3. 验证 API Key 是否有效
4. 检查数据源是否可用

### 问题 4: Python 版本过旧

```
Python 3.6.8 不支持某些特性
```

**解决**：升级到 Python 3.8+
```bash
# Ubuntu/Debian
sudo apt install python3.8

# 或使用 pyenv
curl https://pyenv.run | bash
pyenv install 3.8.10
pyenv global 3.8.10
```

## 📈 性能优化

### 当前限制
- 顺序执行（可改为并发）
- 无缓存机制
- 全量抓取（非增量）

### 改进建议
1. 使用 `asyncio` 并发抓取
2. 添加 URL 缓存（Redis/SQLite）
3. 实现增量更新（记录已处理 ID）
4. 分布式部署（多机器并行）

## 🤝 集成到 OpenClaw

### 作为 Skill 使用

在 OpenClaw 中触发：
```
/ai-daily generate
```

### 自动推送

修改 `scripts/generate.sh` 添加推送逻辑：

```bash
# 生成后推送到聊天
openclaw message send --channel telegram \
  "📰 AI 日报已生成：output/AI-Daily-$(date +%Y-%m-%d).md"
```

## 📝 更新日志

### v1.0.0 (2026-02-26)
- ✅ 初始版本
- ✅ RSS/Feed 抓取
- ✅ Tavily Search 集成
- ✅ arXiv 论文检索
- ✅ LLM 内容过滤
- ✅ Markdown 输出
- ✅ 定时任务支持

## 📞 支持

- 文档：`README.md`
- 配置：`config/sources.json`
- Prompt：`config/prompts.md`
- 测试：`scripts/test.sh`

---

**祝使用愉快！** 🎉
