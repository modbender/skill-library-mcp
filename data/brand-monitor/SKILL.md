---
name: brand-monitor
version: 1.2.0
description: 新能源汽车品牌舆情监控 - 自动搜索、分析国内平台的品牌提及情况
author: OpenClaw Community
license: MIT
keywords:
  - brand
  - monitoring
  - sentiment
  - social-media
  - new-energy-vehicle
  - automotive
allowed-tools:
  - shell
  - web_fetch
  - message
compatibility:
  - openclaw >= 2026.2.0
---

# 新能源汽车品牌舆情监控 Skill

专为新能源汽车品牌打造的零代码舆情监控解决方案。自动监控小红书、微博、汽车之家、懂车帝、易车网、知乎、百度贴吧、抖音/快手等国内平台的品牌提及。

## 何时使用此 Skill

当用户提到以下内容时，激活此 skill：

- "执行品牌监控"
- "检查品牌提及"
- "分析品牌趋势"
- "检查品牌警报"
- "舆情监控"
- "品牌声誉"
- 提到具体品牌名称 + "监控"、"分析"、"趋势"

## 核心功能

### 1. 每日监控 (monitor)

搜索国内各平台的品牌提及，分析情感和影响力，生成结构化报告。

**监控平台：**
- 📕 小红书 (xiaohongshu.com) - 用户真实体验
- 🔴 微博 (weibo.com) - 实时热点
- 🚗 汽车之家 (autohome.com.cn) - 专业评测
- 🎬 懂车帝 (dongchedi.com) - 视频评测
- 🚙 易车网 (yiche.com) - 新车资讯
- 🤔 知乎 (zhihu.com) - 深度讨论
- 💬 百度贴吧 (tieba.baidu.com) - 车友交流
- 🎵 抖音/快手 - 短视频

### 2. 实时警报 (alert)

每小时检测需要关注的提及：
- 🚨 负面提及（情感 < -0.5，影响力 > 100）
- 🔥 病毒式传播（互动数 > 5000）
- ⚠️ 危机信号（安全、召回、自燃、维权等）
- 👥 群体性投诉
- 📰 汽车媒体报道

### 3. 趋势分析 (analyze-trend)

分析历史数据，生成趋势报告：
- 📈 提及数量趋势
- 😊 情感变化趋势
- 📱 平台分布变化
- 💪 影响力趋势
- 🔥 热门话题演变

## 配置要求

在使用前，需要配置以下参数（通过 config.json 或对话中提供）：

- `brand_name` (必需): 要监控的品牌名称
- `brand_aliases` (可选): 品牌别名列表，如车型名称
- `platforms` (可选): 监控平台列表，默认全部国内平台
- `monitor_hours` (可选): 监控时间范围（小时），默认 24
- `feishu_webhook` (必需): 飞书机器人 Webhook URL

**新能源汽车行业配置：**
- `industry_specific.focus_keywords`: 关注关键词（续航、充电、智驾等）
- `industry_specific.kol_min_followers`: KOL 最小粉丝数阈值
- `industry_specific.media_accounts`: 重点汽车媒体账号列表

## Prompts

此 skill 包含三个主要 prompt 文件：

1. **prompts/monitor.md** - 每日监控流程
2. **prompts/alert.md** - 实时警报流程
3. **prompts/analyze-trend.md** - 趋势分析流程

详细的执行指令请参考各 prompt 文件。

## 使用示例

### 执行每日监控

```
执行品牌监控
```

或

```
搜索过去 24 小时关于"理想汽车"的所有提及并分析
```

### 检查实时警报

```
检查品牌警报
```

或

```
立即检查是否有需要关注的负面提及
```

### 分析趋势

```
分析过去 7 天的品牌趋势
```

或

```
生成本周的品牌监控周报
```

## 报告格式

报告将通过飞书推送，包含：

- 📊 总览统计（总数、情感分布）
- 🔥 热门提及 Top 5（标注汽车媒体大V）
- 📱 平台分布
- 🔥 热门话题（续航、充电、智驾等）
- 💡 关键洞察
- 🎯 建议行动

## 汽车媒体识别

系统会自动识别并标注汽车媒体：

- ⭐ 官方媒体（汽车之家、懂车帝、易车网等）
- 🎖️ 认证编辑（媒体认证账号）
- 👑 行业 KOL（粉丝数 > 10万的汽车博主）

## 新能源汽车特定问题识别

系统会特别关注新能源汽车行业的常见问题：

- 续航虚标、续航焦虑
- 充电故障、充电速度慢
- 电池衰减、电池安全
- 自燃、断轴、异响
- 智驾故障、OTA 问题
- 售后服务、维权

## 技术实现

此 skill 使用自定义 Python 爬虫实现搜索功能：
- ✅ 不依赖第三方搜索 API（无需 Brave/Perplexity API Key）
- ✅ 直接访问各平台获取数据
- ✅ 支持代理配置，适合国内外用户
- ✅ 可扩展，易于添加新平台
- ✅ 所有数据处理在本地完成

## 安全性

此 skill：
- ✅ 使用本地 Python 爬虫（crawler/search_crawler.py）
- ✅ 只执行受控的爬虫脚本
- ✅ 不发送数据到第三方服务器（除了配置的飞书 Webhook）
- ✅ 遵守平台的使用规则和反爬虫策略

## 依赖

- OpenClaw v2026.2.0+
- 已配置的 LLM（Claude/GPT/Gemini）
- 飞书账号（用于接收报告）

## 文档

- [新能源汽车品牌监控-完整指南](新能源汽车品牌监控-完整指南.md)
- [一键配置定时任务](一键配置定时任务.md)
- [快速开始](快速开始.md)
- [部署指南](部署指南.md)
- [使用指南](使用指南.md)
- [更新说明](更新说明.md)

## 故障排查

如果遇到问题：

1. 检查 OpenClaw 是否正常运行：`openclaw doctor`
2. 验证 skill 已加载：`openclaw skills list | grep brand-monitor`
3. 检查配置文件：`cat config.json`
4. 查看日志：`tail -f ~/.openclaw/logs/gateway.log`

## 贡献

欢迎贡献！请查看 [README.md](README.md) 了解贡献指南。

## 许可证

MIT License

---

**Made with ❤️ for New Energy Vehicle Brands**
