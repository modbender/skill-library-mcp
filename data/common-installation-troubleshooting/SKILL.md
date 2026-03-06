---
name: "Skill: OpenClaw 插件安装常见问题排查"
description: 用于解决 OpenClaw 插件安装中遇到的常见问题。
---

# Skill: OpenClaw 插件安装常见问题排查

用于解决 OpenClaw 插件安装中遇到的常见问题。

## 问题分类

### 1. Tavily Search 安装问题

**问题现象：**
```
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/tavily-search
npm error 404 The requested resource 'tavily-search@*' could not be found
```

**原因：**
包名错误，正确的包名是 `tavily-mcp`（用于 MCP 服务器）

**解决方案：**
```bash
# 正确的安装命令
npm install -g tavily-mcp
```

---

### 2. Find-Skills 安装问题

**问题现象：**
```
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/find-skills
```

**原因：**
`find-skills` 不是 npm registry 中的标准包名，可能使用不同的名称

**解决方案：**
- 使用 `npm search find-skills` 搜索是否存在
- 检查是否需要 GitHub 仓库克隆
- 验证包的实际名称

---

### 3. Proactive-Agent-1-2-4 安装问题

**问题现象：**
```
npm error code E404
npm error 404 Not Found - GET https://registry.npmjs.org/proactive-agent-1-2-4
```

**原因：**
`proactive-agent-1-2-4` 不是 npm 包名

**解决方案：**
- 确认正确的包名或获取方式
- 可能需要从 GitHub 仓库安装
- 使用 `npm search` 查找可用版本

---

### 4. Imap-Smtp-Email 安装问题

**问题现象：**
安装时找不到对应包

**原因：**
包名描述性太强，可能不是 npm 包名

**解决方案：**
- 咨询用户提供正确的包名
- 使用 web search 搜索具体插件（如 `imap-smtp npm`）
- 验证是否需要其他安装方式

---

### 5. ClawHub CLI 安装问题

**问题现象：**
Windows 权限错误，无法完全删除旧文件

**原因：**
Windows 系统文件操作限制，临时文件占用

**解决方案：**
```bash
# 强制覆盖安装
npm i -g clawhub --force
```

**验证安装：**
Windows 下使用 `clawhub --cli-version`
或直接使用帮助命令查看版本：
```bash
npm run -g clawhub -- --help
```

---

# 🔍 通用排查步骤

## 步骤 1：搜索包名
```bash
npm search "关键词"
```

## 步骤 2：检查官方网站/文档
如果是特定插件，访问其官方网站或 GitHub 查看：
- README 文件
- 安装说明
- 依赖要求

## 步骤 3：使用 Web Search
使用内置的 `web_search` 工具搜索：
```
"插件名 npm" 或 "插件名 github"
```

## 步骤 4：检查包的权限
```bash
npm view 插件名
```

## 步骤 5：尝试不同安装方式
- 全局安装：`npm install -g 插件名`
- 本地安装：`npm install 插件名`
- 使用 --force 覆盖：`npm install -g 插件名 --force`

---

# 📝 经验总结

1. **包名很重要**：很多插件在 npm 上的名称与用户记忆的不同
2. **使用搜索工具**：遇到困惑时先搜索，不要瞎猜
3. **查看文档**：不要只依赖包名，查看官方文档的安装说明
4. **权限问题**：Windows 安装全局包时可能会遇到 EPERM 错误，使用 `--force`
5. **验证安装**：安装后立即验证版本和功能

---

# 🎯 最佳实践

- **安装前检查**：确认插件是否在 npm 注册表有对应的包
- **查看 README**：从官方仓库获取准确的安装命令
  - GitHub README 通常包含完整的安装指南
  - 注意不同的安装方式（npm/pip/git）
- **使用 --save-dev / -D**：开发环境使用，生产环境考虑 --save 或 -S
- **验证版本**：安装后立即测试，确保功能正常

---

# 📚 相关资源

- ClawHub 文档：https://docs.openclaw.ai/tools/clawhub
- npm Registry: https://www.npmjs.com/
- ClawHub 网站: https://clawhub.ai

---

_Last updated: 2026-02-10_