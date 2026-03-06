---
name: bilibili-analytics
description: "Bilibili视频搜索与数据分析。抓取指定关键词的搜索结果，生成统计报告。支持多页面抓取、数据分析和可视化报告。适用于：(1) 搜索B站视频 (2) 分析视频数据 (3) 生成统计报告 (4) 追踪热门趋势"
---

# Bilibili Analytics

搜索和分析B站视频数据，生成统计报告。

## 快速开始

```bash
# 搜索关键词并抓取数据
agent-browser open "https://search.bilibili.com/all?keyword=你的关键词"

# 获取数据
agent-browser eval '抓取脚本'

# 生成报告
# 分析数据并输出统计
```

## 完整工作流程

### 1. 搜索视频

```bash
agent-browser open "https://search.bilibili.com/all?keyword={关键词}" --timeout 15000
```

### 2. 抓取数据

使用 `scripts/scrape_videos.sh` 或手动执行：

```bash
agent-browser eval '
const videos = [];
document.querySelectorAll(".bili-video-card").forEach((card) => {
  const title = card.querySelector(".bili-video-card__info--tit")?.textContent.trim() || "";
  const author = card.querySelector(".bili-video-card__info--author")?.textContent.trim() || "";
  const date = card.querySelector(".bili-video-card__info--date")?.textContent.trim() || "";
  const stats = card.querySelectorAll(".bili-video-card__stats--item");
  const playCount = stats[0]?.textContent.trim() || "0";
  const commentCount = stats[1]?.textContent.trim() || "0";
  videos.push({title, author, date, playCount, commentCount});
});
JSON.stringify(videos, null, 2);
'
```

### 3. 多页面抓取

```bash
# 翻页抓取
for page in 1 2 3 4 5; do
  agent-browser open "https://search.bilibili.com/all?keyword={关键词}&page=$page"
  agent-browser eval '抓取脚本' >> data.json
done
```

### 4. 数据分析

使用 `scripts/analyze_data.py` 或手动分析：

- 时间分布统计
- 作者活跃度排名
- 评论数分布
- 播放量分布
- 关键发现和建议

## 脚本说明

### scripts/scrape_videos.sh

一键抓取脚本，支持指定关键词和页数。

```bash
./scripts/scrape_videos.sh "关键词" 页数
```

### scripts/analyze_data.py

数据分析脚本，生成统计报告。

```bash
python scripts/analyze_data.py data.json
```

## 输出格式

### 统计报告模板

```markdown
## 📊 Bilibili "{关键词}" 搜索结果统计报告

### 📈 总体数据
- 数据范围: 前N页搜索结果
- 视频总数: X个
- 采集时间: YYYY-MM-DD HH:MM

### 🕐 发帖时间分布
| 时间段 | 数量 | 占比 |
|--------|------|------|

### 👥 活跃作者 TOP 10
| 排名 | 作者 | 视频数 |
|------|------|--------|

### 💬 评论数分布
| 评论数范围 | 视频数 | 占比 |
|------------|--------|------|

### 👁️ 播放量分布
| 播放量范围 | 视频数 | 占比 |
|------------|--------|------|

### 🎯 关键发现
1. ...
2. ...

### 📝 建议
- ...
```

## 注意事项

1. **反爬虫**: B站有反爬虫机制，建议控制抓取频率
2. **数据准确性**: 数据实时变化，报告仅代表抓取时刻状态
3. **隐私合规**: 仅抓取公开数据，不涉及用户隐私

## 错误处理

- 浏览器启动失败：检查 agent-browser 安装
- 数据抓取失败：检查页面是否加载完成
- 分析脚本错误：检查数据格式是否正确
