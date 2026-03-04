# Bilibili Analytics 使用示例

## 场景1：搜索特定关键词并生成报告

### 用户请求
"帮我搜索B站上关于'原神'的视频，并生成统计报告"

### 执行步骤

1. 搜索视频
```bash
agent-browser open "https://search.bilibili.com/all?keyword=原神" --timeout 15000
```

2. 抓取数据（多页）
```bash
# 第1页
agent-browser eval '抓取脚本' > data_page1.json

# 第2页
agent-browser open "https://search.bilibili.com/all?keyword=原神&page=2"
agent-browser eval '抓取脚本' > data_page2.json
```

3. 分析数据并生成报告

## 场景2：追踪竞争对手

### 用户请求
"帮我分析'李子柒'在B站的视频表现"

### 执行步骤

1. 搜索用户视频
2. 分析数据特征
3. 生成对比报告

## 场景3：行业趋势分析

### 用户请求
"分析B站上'AI绘画'话题的热度趋势"

### 执行步骤

1. 抓取关键词数据
2. 分析时间分布
3. 识别热门作者
4. 生成趋势报告

## 数据字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| title | 视频标题 | "【原神】4.0版本前瞻直播回顾" |
| author | 作者名称 | "原神" |
| date | 发布日期 | "· 02-28" 或 "· 2025-04-05" |
| playCount | 播放量 | "3.8万" 或 "1234" |
| commentCount | 评论数 | "88" 或 "0" |

## 常见问题

### 1. 浏览器启动失败
- 检查 agent-browser 是否正确安装
- 运行 `agent-browser install` 安装依赖

### 2. 数据抓取为空
- 检查页面是否完全加载
- 增加 `--timeout` 参数值

### 3. 反爬虫机制
- 控制抓取频率，添加延迟
- 避免短时间内大量请求

## 输出报告示例

见 SKILL.md 中的模板。
