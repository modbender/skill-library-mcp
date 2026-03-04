# Cue v1.0.3 安全改进报告

针对 ClawHub 安全扫描结果的分析和改进措施。

---

## 原始安全问题 / Original Security Issues

### 1. 元数据不一致 / Metadata Inconsistencies
- **问题**: 注册表摘要显示 "Required env vars: none" 和 "instruction-only"
- **实际**: 需要 CUECUE_API_KEY（必需）和 TAVILY_API_KEY（可选）
- **状态**: ✅ 已修复

### 2. 权限和行为未明确说明 / Unclear Permissions & Behaviors
- **问题**: 未说明会创建 ~/.cuecue 持久化存储
- **问题**: 未说明会安装 cron 定时任务
- **问题**: 未说明会复用 OpenClaw 渠道令牌
- **状态**: ✅ 已修复

### 3. 安装类型不一致 / Install Type Inconsistency
- **问题**: 标记为 "instruction-only" 但包含大量脚本
- **状态**: ✅ 已修复

### 4. 环境变量未完整声明 / Incomplete Environment Variable Declaration
- **问题**: 未声明 FEISHU_APP_ID、FEISHU_APP_SECRET、OPENCLAW_CHANNEL、CHAT_ID
- **状态**: ✅ 已修复

---

## 修复措施 / Fixes Applied

### 1. 更新 manifest.json

```json
{
  "description": "Cue - 你的专属调研助理... (详细说明持久化行为和权限要求)",
  "requiredEnvVars": ["CUECUE_API_KEY"],
  "optionalEnvVars": [
    "TAVILY_API_KEY",
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "OPENCLAW_CHANNEL",
    "CHAT_ID"
  ],
  "persistentStorage": ["$HOME/.cuecue"],
  "backgroundJobs": ["monitor-daemon (every 30 minutes via cron)"],
  "installType": "script-package",
  "source": "https://github.com/openclaw/skills/cue",
  "warnings": [
    "Creates persistent local storage at ~/.cuecue",
    "Installs cron job for periodic monitoring",
    "Requires external API credentials",
    "May reuse OpenClaw channel tokens for notifications"
  ]
}
```

### 2. 添加安全声明到 SKILL.md

在文档开头添加 **⚠️ 安全声明 / Security Notice** 章节：
- 本地存储说明
- 后台任务说明
- 外部 API 访问说明
- 环境变量说明
- 通知权限说明

### 3. 创建 SECURITY.md

新建详细的安全指南文档，包含：
- 权限和行为详细说明
- 本地存储风险
- 后台任务风险
- 外部 API 访问风险
- 安全建议（安装前、运行时、卸载）
- 数据隐私说明
- 漏洞报告方式

### 4. 更新 package.json

```json
{
  "description": "详细说明安全注意事项...",
  "optionalDependencies": {
    "@playwright/test": "^1.40.0"
  },
  "files": [
    "manifest.json",
    "SKILL.md",
    "SECURITY.md",
    "README.md",
    "scripts/",
    "package.json"
  ]
}
```

### 5. 更新 .clawhubignore

确保开发文档不包含在发布包中：
- dev/ 目录
- RELEASE_*.md
- FILE_CHANGES_*.md
- TEST_PLAN_*.md

---

## 改进后的元数据 / Improved Metadata

### manifest.json
- ✅ 明确声明所有必需和可选环境变量
- ✅ 明确声明持久化存储位置
- ✅ 明确声明后台任务（cron）
- ✅ 明确声明外部 API 端点
- ✅ 添加 warnings 数组列出所有风险
- ✅ 设置 installType 为 "script-package"
- ✅ 添加 source 字段指向源码仓库

### SKILL.md
- ✅ 开头添加安全声明
- ✅ 详细说明环境变量和权限
- ✅ 添加权限说明章节

### SECURITY.md (新增)
- ✅ 完整的安全指南
- ✅ 详细的权限说明
- ✅ 风险分析
- ✅ 安全建议
- ✅ 卸载指南

### package.json
- ✅ description 包含安全提示
- ✅ 明确 Playwright 为 optionalDependencies
- ✅ files 字段明确列出发布文件

---

## 验证结果 / Verification Results

### 发布包内容
```
cue-v1.0.3.tar.gz (24个文件)
├── manifest.json          ✅ 完整元数据
├── SKILL.md              ✅ 包含安全声明
├── SECURITY.md           ✅ 新增安全指南
├── README.md
├── package.json          ✅ 更新描述
└── scripts/              ✅ 核心脚本
```

### 排除的内容
```
❌ scripts/dev/          开发工具
❌ RELEASE_*.md          发布文档
❌ FILE_CHANGES_*.md     改动清单
❌ TEST_PLAN_*.md        测试计划
❌ .tar.gz              旧版本包
```

---

## 建议的 ClawHub 注册表信息 / Recommended Registry Metadata

```yaml
name: Cue
version: 1.0.3
description: |
  Cue - 你的专属调研助理。多 Agent 深度研究工具，具有持久化监控功能。
  
  ⚠️ 安全提示：
  - 创建本地存储 ~/.cuecue
  - 安装 cron 定时任务（每30分钟）
  - 需要外部 API 访问 (cuecue.cn, api.tavily.com)
  - 需要 CUECUE_API_KEY
  
  安装前请查阅 SECURITY.md

install_type: script-package
required_env_vars:
  - CUECUE_API_KEY
optional_env_vars:
  - TAVILY_API_KEY
  - FEISHU_APP_ID
  - FEISHU_APP_SECRET
  - OPENCLAW_CHANNEL
  - CHAT_ID

external_endpoints:
  - https://cuecue.cn
  - https://api.tavily.com

persistent_storage:
  - $HOME/.cuecue

background_jobs:
  - "monitor-daemon (cron, every 30 minutes)"

source: https://github.com/openclaw/skills/cue
```

---

## 待办事项 / TODO

- [x] 更新 manifest.json 元数据
- [x] 添加安全声明到 SKILL.md
- [x] 创建 SECURITY.md
- [x] 更新 package.json
- [x] 更新 .clawhubignore
- [ ] 在 ClawHub 注册时正确填写元数据
- [ ] 考虑添加安装前确认提示
- [ ] 考虑添加 `--dry-run` 模式用于预览安装行为

---

## 总结 / Summary

v1.0.3 解决了所有 v1.0.2 的安全扫描问题：

1. ✅ **元数据完整**: 所有必需/可选环境变量已声明
2. ✅ **权限透明**: 所有持久化行为和后台任务已说明
3. ✅ **安装类型正确**: 标记为 script-package
4. ✅ **安全文档**: 添加 SECURITY.md 详细安全指南
5. ✅ **用户知情**: SKILL.md 开头明确安全声明

现在用户可以在完全了解权限和行为的情况下做出明智的安装决策。
