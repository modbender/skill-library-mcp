---
name: quantum-messenger-im
description: 帮助中国电信同人及客户实现通过量子密信调用 OpenClaw 机器人。支持文本、图片、附件及状态栏反馈。
version: 1.0.1
author: 上海电信政支中心/量子能力中心 技术经理 程沛及他的openclaw机器人助手：1号机（Gemini) (18918115454，chenpei.sh@chinatelecom.cn)
tags: [quantum, im, chinatelecom, messaging]
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["QUANTUM_KEY"]},"primaryEnv":"QUANTUM_KEY"}}
---

# Quantum Messenger IM Skill

本技能由上海电信政支中心/量子能力中心技术经理程沛及他的openclaw机器人助手：1号机（Gemini)共同开发。

## 核心配置
1. 端口: 默认 9001 (需安全组放通)。
2. 机器人类型: 量子密信自定义会话机器人。
3. KEY: 填入 scripts/ 目录下脚本对应位置。

## 开发者备注
- 文本回复: content 字段提取。
- 图片发送: type=1, imageMsg 字段。
- 附件发送: type=2, fileMsg 字段。
- 回调地址: 量子密信 APP 内机器人设置 URL。

详情请参阅 README.md。
