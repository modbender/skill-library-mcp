# YouYou 佑佑

🩺 私人健康管家 — 自然语言交互，数据本地存储

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 名字来自「保佑健康」

## 功能

- **档案管理** — 身高、体重、血型、过敏史、家族病史
- **日常记录** — 血压、血糖、体重、症状、用药
- **报告存储** — 体检报告、化验单、影像检查（支持图片）
- **用药管理** — 药物记录、相互作用检查、提醒
- **多学科会诊** — 17 专科视角综合分析

## 安装

```bash
# Claude Code
/plugin marketplace add frxiaobei/frxiaobei-skills
/plugin install youyou@frxiaobei-skills

# OpenClaw
clawhub install youyou
```

## 使用

自然语言交互，无需记命令：

```
"今天血压 135/88"          → 自动记录血压
"体重 72kg"                → 更新体重
[发送化验单图片]            → 自动识别并存储
"综合分析我的健康状况"      → 17 专科会诊
```

## 数据隐私

所有数据存储在本地，不会发送给任何第三方。

## 致谢

基于 [WellAlly-health](https://github.com/huifer/WellAlly-health) 开源项目封装。

---

**frxiaobei@elyfinn** • [elyfinn.com](https://elyfinn.com)

Made with 🦊 by [@frxiaobei](https://x.com/frxiaobei) & Finn
