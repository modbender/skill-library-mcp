# Media News Digest 🎬

> 自动化影视娱乐资讯汇总 — 44 个数据源，4 层管道，一句话安装。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 💬 一句话安装

跟你的 [OpenClaw](https://openclaw.ai) AI 助手说：

> **"安装 media-news-digest，每天早上 7 点发影视日报到 #news-media 频道"**

搞定。Bot 会自动安装、配置、定时、推送——全程对话完成。

更多示例：

> 🗣️ "配置一个每周好莱坞周报，只要票房和颁奖季板块，每周一发到 Discord #awards"

> 🗣️ "安装 media-news-digest，加上我的 RSS 源，电影节新闻发到邮箱"

> 🗣️ "现在就给我生成一份影视日报，重点关注流媒体动态"

或通过 CLI 安装：
```bash
clawhub install media-news-digest
```

## 📊 你会得到什么

基于 **44 个数据源** 的质量评分、去重影视行业日报：

| 层级 | 数量 | 内容 |
|------|------|------|
| 📡 RSS | 24 个订阅源 | THR、Deadline、Variety、IndieWire、The Wrap、Collider… |
| 🐦 Twitter/X | 14 个 KOL | @THR、@DEADLINE、@Variety、@BoxOfficeMojo、@MattBelloni… |
| 🔍 Web 搜索 | 7 个主题 | Brave Search API + 时效过滤 |
| 🗣️ Reddit | 6 个子版块 | r/movies、r/boxoffice、r/television、r/Oscars… |

### 数据管道

```
RSS + Twitter + Web + Reddit
           ↓
     run-pipeline.py（并行 ~30s）
           ↓
   质量评分 → 去重 → 主题分组
           ↓
   Discord / 邮件 输出
```

**质量评分**：优先级源 (+3)、多源交叉验证 (+5)、时效性 (+2)、互动度 (+1)、Reddit 热度加分 (+1/+3/+5)、已报道过 (-5)。

## 🎯 7 大板块

| # | 板块 | 覆盖内容 |
|---|------|----------|
| 🎬 | 制作动态 | 新项目、选角、拍摄进展 |
| 💰 | 行业交易 | 并购、版权交易、人才签约 |
| 🎟️ | 票房 | 北美/全球票房、首周末数据 |
| 📺 | 流媒体 | Netflix、Disney+、Apple TV+、收视数据 |
| 🏆 | 颁奖季 | 奥斯卡、金球奖、艾美奖、公关战 |
| 🎪 | 电影节 | 戛纳、威尼斯、多伦多、圣丹斯、柏林 |
| ⭐ | 影评口碑 | 专业评价、RT/Metacritic 评分 |

## ⚙️ 配置

- `config/defaults/sources.json` — 44 个内置数据源
- `config/defaults/topics.json` — 7 个主题，含搜索查询和 Twitter 查询
- 用户自定义配置放 `workspace/config/`，优先级更高

## 🔧 环境要求

```bash
export X_BEARER_TOKEN="..."      # Twitter API（推荐）
export TWITTERAPI_IO_KEY="..."   # twitterapi.io 备选后端
export BRAVE_API_KEY="..."       # Web 搜索（可选）
```

## 🚀 快速开始

```bash
# 统一管道（并行跑全部数据源）
python3 scripts/run-pipeline.py \
  --defaults config/defaults \
  --hours 48 --freshness pd \
  --output /tmp/md-merged.json --verbose --force
```

## 📂 仓库地址

**GitHub**: [github.com/draco-agent/media-news-digest](https://github.com/draco-agent/media-news-digest)

## 📄 开源协议

MIT License — 详见 [LICENSE](LICENSE)
