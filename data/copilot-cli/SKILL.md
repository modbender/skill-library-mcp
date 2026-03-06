---
name: Copilot CLI - AI 代码分析助手
description: 使用 GitHub Copilot CLI 分析代码、探索项目、生成代码和自动化开发任务。
---

# Copilot CLI - AI 代码分析助手

## 功能

使用 GitHub Copilot CLI 分析代码、探索项目、生成代码和自动化开发任务。

## 前置条件

1. **安装 Copilot CLI**
   ```bash
   brew install copilot-cli
   ```

2. **设置 GitHub Personal Access Token**
   - 访问 https://github.com/settings/personal-access-tokens/new
   - 创建 fine-grained token，权限：Copilot Requests
   - Token 保存到 `~/.copilot/github_token.txt`

## 使用方法

### 基本命令

```bash
# 进入项目目录
cd /path/to/project

# 使用 Copilot CLI（使用保存的 token）
COPILOT_GITHUB_TOKEN=$(cat ~/.copilot/github_token.txt) copilot -p "你的问题"
```

### 常用探索问题

**项目概览：**
```
"这个项目是做什么的？请简要说明。"
```

**架构分析：**
```
"分析这个项目的架构和主要模块。"
```

**技术栈：**
```
"这个项目使用了哪些主要技术栈和依赖？"
```

**代码查找：**
```
"找到处理用户认证的代码。"
```

**文档生成：**
```
"为这个模块生成文档。"
```

**代码审查：**
```
"审查这个文件，找出潜在问题。"
```

### 高级用法

**指定文件：**
```bash
copilot -p "解释 @src/main.js 的功能"
```

**交互式会话：**
```bash
COPILOT_GITHUB_TOKEN=$(cat ~/.copilot/github_token.txt) copilot
```

**自动执行（需要权限）：**
```bash
copilot --yolo -p "为这个功能编写单元测试"
```

## 注意事项

- Copilot CLI 使用 GitHub Copilot API 分析代码
- 代码存储位置不影响分析（可以是 GitLab、GitHub 等）
- 一次性查询使用 `-p` 参数
- 复杂任务使用交互式会话

## 配置文件

- **Token 存储**：`~/.copilot/github_token.txt`
- **配置目录**：`~/.copilot/`
- **日志目录**：`~/.copilot/logs/`

## 故障排查

### 策略限制错误

如果遇到 "Access denied by policy settings"：
1. 检查 https://github.com/settings/copilot
2. 确认 Copilot CLI 功能已启用
3. 确认组织策略允许第三方 MCP 服务器

### Token 过期

创建新的 Personal Access Token 并更新：
```bash
echo "新 token" > ~/.copilot/github_token.txt
```

## 示例使用

```bash
# 分析 base-auto 项目
cd /Users/agent/workspace/base-auto

# 快速提问
COPILOT_GITHUB_TOKEN=$(cat ~/.copilot/github_token.txt) copilot -p "这个项目有什么核心功能？"

# 深度分析
COPILOT_GITHUB_TOKEN=$(cat ~/.copilot/github_token.txt) copilot -p "分析项目的数据库设计，列出主要的表和关系。"
```

## 资源

- 官方文档：https://docs.github.com/en/copilot
- 命令参考：https://docs.github.com/en/copilot/reference/cli-command-reference
