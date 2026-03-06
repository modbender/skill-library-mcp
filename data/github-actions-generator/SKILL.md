---
name: github-actions-generator
description: 生成 GitHub Actions 工作流，支持 CI/CD、测试、部署等多种场景。
metadata: {"clawdbot":{"emoji":"⚡","requires":{},"primaryEnv":""}}
---

# GitHub Actions Generator

自动生成 GitHub Actions 工作流文件。

## 支持的场景

- ✅ Node.js CI/CD
- ✅ Python CI/CD
- ✅ Go CI/CD
- ✅ Docker 构建推送
- ✅ 自动发布 Release
- ✅ Dependabot 自动更新
- ✅ 定时任务

## 使用方法

```bash
github-actions-generator ci --lang node
github-actions-generator deploy --target vercel
github-actions-generator docker --registry ghcr
```
