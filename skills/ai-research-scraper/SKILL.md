---
name: ai-research-scraper
description: 用于抓取AI领域最新研究信息的技能，重点关注AI产品发展。从知名AI网站获取信息，提供简洁概括和链接，限制数据量以便快速阅读。
---

# AI Research Scraper

## 概述

这个技能专门用于从知名AI领域网站抓取最新研究信息，重点关注AI产品发展方面。它会限制抓取的数据量和token使用，提供简洁的信息概括，并包含原始网页链接，方便用户进一步查阅详细内容。

## 使用场景

- 当您需要快速了解AI领域最新产品动态时
- 当您想跟踪特定AI产品的发展信息时
- 当您需要获取AI技术发展的最新研究成果摘要时

## 支持的网站

当前支持的AI领域知名网站包括：
- TechCrunch AI板块
- VentureBeat AI板块
- MIT Technology Review AI板块
- Google AI Blog
- Microsoft AI Blog
- NVIDIA Blog

## 功能特点

- **数据量控制**：限制摘要长度，确保信息简洁
- **重点突出**：聚焦AI产品发展信息
- **链接完整**：每个摘要都包含原始网页链接
- **定时更新**：支持定期抓取最新信息
- **可配置性**：支持添加或修改目标网站
- **网络优化**：增加超时时间和重试机制，提高抓取成功率
- **缓存机制**：添加1小时缓存，避免重复抓取相同内容
- **稳定源**：优化网站列表，使用更稳定的AI领域网站源
- **备用搜索**：支持使用tavily-search技能替代，避免网络超时问题
- **简化处理**：暂时移除翻译功能，避免API错误和网络超时问题

## 使用方法

### 快速开始

使用默认配置抓取AI产品发展相关信息：

```bash
python3 /root/.openclaw/workspace/skills/ai-research-scraper/scripts/scraper.py
```

### 配置选项

#### 自定义网站列表

编辑 `references/websites.txt` 文件，添加或删除目标网站。每行格式：

```
网站名称|网站URL|RSS/Feed URL（可选）
```

#### 控制摘要长度

```bash
python3 /root/.openclaw/workspace/skills/ai-research-scraper/scripts/scraper.py --max-tokens 500
```

#### 指定时间范围

```bash
python3 /root/.openclaw/workspace/skills/ai-research-scraper/scripts/scraper.py --days 7
```

#### 指定主题重点

```bash
python3 /root/.openclaw/workspace/skills/ai-research-scraper/scripts/scraper.py --topic product-development
```

## 脚本和资源

### Scripts

- `scripts/scraper.py`: 主要的网页抓取和信息提取脚本
- `scripts/example.py`: 示例脚本（可删除或修改）

### References

- `references/websites.txt`: 包含要抓取的网站列表
- `references/api_reference.md`: API参考文档（待完善）

### Assets

- `assets/`: 资源文件夹（可用于存放模板或其他静态资源）
