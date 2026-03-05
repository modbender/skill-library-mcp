# News Aggregator Skill

全网科技/金融新闻聚合助手，支持AI 智能解读。

## ✨ 功能特性

- **多源聚合**：一站式覆盖硅谷科技、中国创投、开源社区及金融市场。
- **深度阅读**：支持 Deep Fetch 模式，自动获取正文并进行 AI 深度分析。
- **智能周报**：自动生成杂志级排版的中文日报/周报。
- **交互菜单**：可通过"news-aggregator-skill 如意如意"唤醒交互式菜单，指哪打哪。

## 📚 聚合信源

覆盖全球 8 大主流高价值信息渠道：

- **全球科技**：Hacker News, Product Hunt
- **开源社区**：GitHub Trending, V2EX
- **中国创投**：36Kr, 腾讯新闻科技频道
- **社会/金融**：微博热搜, 华尔街见闻

## 📥 安装指南

### 第一步：安装到 Code Agent

选择以下任一方式将 Skill 添加到您的 Agent：

#### 方法 A：使用 Openskills CLI (推荐)

会自动处理路径依赖和配置同步。

```bash
# 克隆仓库
git clone git@github.com:cclank/news-aggregator-skill.git

# 安装 skill
openskills install ./news-aggregator-skill

# 同步配置到 Agent
openskills sync
```

#### 方法 B：使用 NPX (推荐 2)

直接从远程仓库添加。

```bash
npx skills add https://github.com/cclank/news-aggregator-skill
```

#### 方法 C：Claude 标准安装 (手动)

手动将 Skill 集成到 Claude 项目的标准方式。

```bash
# 1. 克隆仓库
git clone git@github.com:cclank/news-aggregator-skill.git

# 2. 定位或创建项目的 skills 目录
mkdir -p YourProject/.claude/skills

# 3. 将整个文件夹复制过去
cp -r news-aggregator-skill YourProject/.claude/skills/

# 4. 验证：确保 SKILL.md 存在于目标目录
ls YourProject/.claude/skills/news-aggregator-skill/SKILL.md
```

### 第二步：安装 Python 依赖（如果你的agent足够聪明，可以跳过）

进入已安装的 Skill 目录，执行依赖安装：

```bash
# 进入 Skill 安装目录 (根据您选择的安装方式调整路径)
cd ~/.claude/skills/news-aggregator-skill  # 或 YourProject/.claude/skills/news-aggregator-skill

# 安装依赖
pip install -r requirements.txt
```

## 🚀 如何使用

### 1. 🔮 唤醒交互菜单 (推荐)

最简单的使用方式，来自岚叔的彩蛋--直接召唤智能菜单：

> **"news-aggregator-skill 如意如意"**

系统将为您展示功能列表（如：早安日报、硅谷热点、全网扫描等），回复数字即可执行。

### 2. 🗣️ 自然语言触发

您也可以直接说出您的需求：

- **看热点**："帮我看看 Hacker News 和 Product Hunt 最近有什么 AI 新闻？"
- **看国内**："36氪和腾讯新闻今天有什么科技大瓜？"
- **看开源**："GitHub 上最近火的项目是啥？"
- **全网扫**："全网扫描一下关于 Agent 和 LLM 的最新进展。"

> ⚠️ **全网扫描注意**: Global Scan 是基于各平台"热榜"进行关键词过滤，而非全文检索。如果关键词（如 Agent）在当天的全网热榜中未出现，可能返回较少结果。

## 📊 支持源列表

| Source Name | ID | Category |
|-------------|----|----------|
| **Hacker News** | `hackernews` | Global Tech |
| **GitHub Trending** | `github` | Open Source |
| **Product Hunt** | `producthunt` | New Products |
| **36Kr** | `36kr` | China VC |
| **Tencent News** | `tencent` | General Tech |
| **Weibo** | `weibo` | Social Trends |
| **WallStreetCN** | `wallstreetcn` | Finance |
| **V2EX** | `v2ex` | Dev Community |

