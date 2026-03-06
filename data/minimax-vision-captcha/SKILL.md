---
name: minimax-vision-captcha
description: 使用MiniMax视觉模型识别图片中的验证码、滑块位置、文字内容等。适用于需要AI视觉分析的场景，如微信验证码识别、网页截图分析、图片文字提取。当需要识别图片内容、分析验证码、提取截图信息时使用此技能。
---

# MiniMax Vision Captcha Skill

使用MiniMax MCP的视觉理解能力识别图片中的内容，解决验证码、滑块分析等问题。

## 快速开始

### 1. 截图

使用OpenClaw浏览器截图：

```bash
browser action=screenshot targetId=<页面ID>
```

或使用OpenClaw的snapshot获取页面结构后分析。

### 2. 调用MiniMax视觉识别

```bash
mcporter call minimax-coding-plan.understand_image prompt="描述图片内容" image_source="/path/to/screenshot.png"
```

### 3. 分析结果

根据返回结果进行下一步操作。

## 典型使用场景

### 场景1：微信滑块验证码

1. 访问微信页面，触发验证码
2. 截图：`browser action=screenshot`
3. 发送给视觉模型分析
4. 获取滑块位置描述

### 场景2：图片文字识别

1. 截图或获取图片路径
2. 调用视觉模型识别文字
3. 返回文字内容

### 场景3：网页元素分析

1. 使用snapshot获取页面结构
2. 分析特定元素的可见内容和属性

## 注意事项

- 确保MiniMax MCP已配置
- 图片路径需要是服务器可访问的绝对路径
- 滑块验证码需要描述缺口位置（左侧/右侧/距离）

## 依赖

- minimax-coding-plan MCP
- OpenClaw浏览器工具
