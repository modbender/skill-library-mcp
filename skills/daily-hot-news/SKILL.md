---
name: daily-hot-news
description: 每日热榜技能 - 查询微博、知乎、B站、抖音等54个平台的热榜数据，支持定时推送和分类浏览。
categories:
  - information-aggregation
  - daily-utility
  - news
emoji: 🔥
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    install:
      - id: python-deps
        kind: exec
        command: "cd /root/.openclaw/workspace/skills/daily-hot-news && python3 -m pip install requests aiohttp"
        label: "安装Python依赖"
---

# 🔥 每日热榜

## 🎯 概述

提供 **54 个热榜源** 的本地化查询服务，基于 [DailyHotApi](https://github.com/imsyy/DailyHotApi) 项目。

**核心功能**：
- 📊 热榜查询 - 查询任意平台的热榜数据
- 📋 分类浏览 - 列出所有支持的热榜源
- 💾 历史记录 - 自动保存每日热榜数据
- ⏰ 定时推送 - 自动推送热榜到飞书

---

## 🏗️ 架构设计

```
用户请求 → DailyHotApi Skill → 本地 DailyHotApi 服务 → 返回格式化结果
```

### 组件说明
| 组件 | 职责 |
|------|------|
| **DailyHotApi 服务** | 独立运行，抓取/聚合热榜数据 |
| **DailyHotApi Skill** | OpenClaw 插件，处理用户请求 |

---

## 📡 支持的热榜源（54个）

### 🎬 视频/直播平台
| 接口 | 名称 |
|------|------|
| bilibili | 哔哩哔哩 |
| acfun | AcFun |
| douyin | 抖音 |
| kuaishou | 快手 |
| coolapk | 酷安 |

### 💬 社交媒体
| 接口 | 名称 |
|------|------|
| weibo | 微博 |
| zhihu | 知乎 |
| zhihu-daily | 知乎日报 |
| tieba | 百度贴吧 |
| douban-group | 豆瓣讨论小组 |
| v2ex | V2EX |
| ngabbs | NGA |
| hupu | 虎扑 |

### 📰 新闻资讯
| 接口 | 名称 |
|------|------|
| baidu | 百度热搜 |
| thepaper | 澎湃新闻 |
| toutiao | 今日头条 |
| 36kr | 36氪 |
| qq-news | 腾讯新闻 |
| sina | 新浪网 |
| sina-news | 新浪新闻 |
| netease-news | 网易新闻 |
| huxiu | 虎嗅 |
| ifanr | 爱范儿 |

### 💻 科技/技术社区
| 接口 | 名称 |
|------|------|
| ithome | IT之家 |
| ithome-xijiayi | IT之家「喜加一」 |
| sspai | 少数派 |
| csdn | CSDN |
| juejin | 稀土掘金 |
| 51cto | 51CTO |
| nodeseek | NodeSeek |
| hellogithub | HelloGitHub |

### 🎮 游戏/ACG
| 接口 | 名称 |
|------|------|
| genshin | 原神 |
| miyoushe | 米游社 |
| honkai | 崩坏3 |
| starrail | 崩坏：星穹铁道 |
| lol | 英雄联盟 |

### 📚 阅读/文化
| 接口 | 名称 |
|------|------|
| jianshu | 简书 |
| guokr | 果壳 |
| weread | 微信读书 |
| douban-movie | 豆瓣电影 |

### 🔧 工具/其他
| 接口 | 名称 |
|------|------|
| 52pojie | 吾爱破解 |
| hostloc | 全球主机交流 |
| weatheralarm | 中央气象台 |
| earthquake | 中国地震台 |
| history | 历史上的今天 |

---

## 🚀 部署说明

### 1. PM2 方式管理（推荐）

DailyHotApi 服务使用 PM2 管理，确保稳定运行。

```bash
cd /root/.openclaw/workspace/skills/daily-hot-api

# 部署并启动服务
./deploy.sh

# 查看状态
./deploy.sh status

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 查看日志
./deploy.sh logs
```

**服务地址**: `http://localhost:6688`

### 2. 配置环境变量

```bash
export DAILY_HOT_API_URL=http://localhost:6688
```

### 3. 安装 Skill 依赖

```bash
cd /root/.openclaw/workspace/skills/daily-hot-news
pip install requests aiohttp
```

---

## 🎮 使用示例

### 查询热榜
```
用户: 微博热搜
Skill: 调用 /weibo → 返回 Top 10 热榜
```

### 查看所有热榜
```
用户: 有什么热榜
Skill: 返回 54 个热榜源列表
```

### 查询历史热榜
```
用户: 微博历史
Skill: 显示之前保存的微博热榜记录
```

### 查看已保存数据
```
用户: 已保存了哪些数据
Skill: 返回所有已保存的热榜数据统计
```

### 定时推送
```
用户: 每天早上8点推送B站热门
Skill: 设置 cron 任务 → 每日调用 /bilibili → 推送到飞书
```

---

## 💾 数据存储

### 存储位置
所有热榜数据保存在：
```
/root/.openclaw/workspace/skills/daily-hot-news/data/
```

### 文件结构
```
data/
├── weibo/
│   ├── 2026-02-05.json
│   └── 2026-02-04.json
├── zhihu/
│   └── 2026-02-05.json
└── ...
```

### 配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DAILY_HOT_DATA_DIR` | data/ | 数据存储目录 |
| `DAILY_HOT_AUTO_SAVE` | true | 是否自动保存热榜数据 |

### 管理命令
```bash
# 查看已保存的数据统计
python3 storage.py

# 清理 30 天前的旧数据
python3 storage.py --clear 30
```

---

## 📊 响应格式

### 热榜列表响应
```json
{
  "platform": "微博",
  "updateTime": "2026-02-05 17:00:00",
  "data": [
    {
      "rank": 1,
      "title": "热搜标题",
      "hot": "1234万",
      "url": "https://..."
    }
  ]
}
```

---

## ⚙️ 配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DAILY_HOT_API_URL` | http://localhost:6688 | DailyHotApi 服务地址 |
| `DAILY_HOT_CACHE_TTL` | 3600 | 缓存时间（秒） |
| `DAILY_HOT_MAX_ITEMS` | 20 | 返回最大条数 |

---

## 📊 资源占用

| 组件 | 内存 | CPU |
|------|------|-----|
| DailyHotApi 服务 | ~200MB | 极低 |
| DailyHotApi Skill | <10MB | 可忽略 |

**总计**: <250MB，对服务器无压力

---

## 🔧 故障排查

### 问题: 服务无法连接
```bash
# 检查 PM2 状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 重启服务
./deploy.sh restart
```

---

## 📁 文件结构

```
daily-hot-news/
├── SKILL.md              # 本说明书
├── daily_hot_news.py     # 核心 Skill 脚本
├── api_client.py         # API 客户端封装
├── formatter.py          # 响应格式化
├── config.py             # 配置管理
├── storage.py            # 数据存储模块
├── data/                 # 热榜数据存储目录
├── README.md             # 快速开始
└── requirements.txt       # 依赖列表
```

---

## 📝 更新日志

**v1.1.0** (2026-02-05)
- ✨ 新增数据存储功能
- ✨ 支持自动保存每日热榜
- ✨ 支持查询历史记录
- ✨ 新增数据统计命令

**v1.0.0** (2026-02-05)
- 初始版本
- 支持 54 个热榜源
- 基础查询和定时推送功能
