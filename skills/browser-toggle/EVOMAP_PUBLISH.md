# 🗺️ EvoMap 发布指南

## 📦 关于 EvoMap

EvoMap 是 OpenClaw 的技能发现和分享平台。

---

## 🚀 发布到 EvoMap

### 方法 1：通过 ClawHub 自动同步

EvoMap 通常从 ClawHub 同步技能，所以：

```bash
# 1. 先发布到 ClawHub
clawhub publish

# 2. 等待同步（通常 24 小时内）
# 3. 在 EvoMap 搜索 browser-toggle
```

### 方法 2：直接提交到 EvoMap

1. 访问：https://evomap.ai/skills/submit
2. 填写提交表单：
   - **Skill 名称：** browser-toggle
   - **版本：** 1.0.0
   - **GitHub 仓库：** https://github.com/your-username/browser-toggle
   - **ClawHub 链接：** https://clawhub.com/skills/browser-toggle
   - **描述：** 一键启用/禁用 OpenClaw 内置浏览器
   - **分类：** Tools > Automation
   - **标签：** browser, toggle, automation, utility

3. 上传材料：
   - 截图（可选）
   - 演示视频（可选）
   - 文档链接

4. 提交审核

---

## 📋 EvoMap 元数据

创建 `evomap.yaml`：

```yaml
name: browser-toggle
version: 1.0.0
title: "Browser Toggle - 内置浏览器一键切换"
description: "一键启用/禁用 OpenClaw 内置浏览器，无需手动修改配置文件"
author: AI Assistant
license: MIT
homepage: https://github.com/your-username/browser-toggle
repository: https://github.com/your-username/browser-toggle
documentation: https://github.com/your-username/browser-toggle/blob/main/README.md
category: tools
subcategory: automation
tags:
  - browser
  - automation
  - utility
  - toggle
platforms:
  - linux
  - macos
  - windows
requirements:
  - python >= 3.8
  - openclaw >= 2026.2.26
  - chrome/chromium
featured: false
screenshots: []
video_url: ""
changelog:
  - version: 1.0.0
    date: 2026-02-28
    changes:
      - 首次发布
      - 一键启用/禁用内置浏览器
      - 自动备份配置
      - 失败自动恢复
      - 支持可视化/无头模式
```

---

## 📊 发布后验证

```bash
# 在 EvoMap 搜索
# https://evomap.ai/search?q=browser-toggle

# 或直接访问
# https://evomap.ai/skills/browser-toggle
```

---

## 🔗 分享链接

发布成功后：
- **EvoMap 页面：** https://evomap.ai/skills/browser-toggle
- **安装命令：** `openclaw skill install browser-toggle`

---

## 📝 审核注意事项

1. **代码质量**
   - ✅ 代码清晰
   - ✅ 有注释
   - ✅ 无安全隐患

2. **文档完整性**
   - ✅ README.md
   - ✅ 安装指南
   - ✅ 使用示例

3. **功能测试**
   - ✅ 功能正常
   - ✅ 无严重 bug
   - ✅ 错误处理完善

4. **兼容性**
   - ✅ 支持多平台
   - ✅ 版本要求明确

---

*EvoMap 发布指南 v1.0*
