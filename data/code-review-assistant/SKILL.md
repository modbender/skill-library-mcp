---
name: code-review-assistant
description: 自动化代码审查助手，支持 PR 审查、代码质量分析、潜在 bug 检测、安全漏洞扫描。
metadata: {"clawdbot":{"emoji":"🔍","requires":{},"primaryEnv":""}}
---

# Code Review Assistant

自动化代码审查助手，帮助开发者快速审查代码，提高代码质量。

## 功能

- 🔍 自动代码审查
- 🐛 Bug 检测
- 🔒 安全漏洞扫描
- 📝 代码风格建议
- 📊 复杂度分析
- ✅ 最佳实践检查

## 支持的语言

| 语言 | 支持 |
|------|------|
| JavaScript/TypeScript | ✅ |
| Python | ✅ |
| Go | ✅ |
| Rust | ✅ |
| Java | ✅ |
| C/C++ | ✅ |

## 使用方法

### 审查单个文件

```bash
code-review-assistant review path/to/file.js

# 指定语言
code-review-assistant review path/to/file.py --language python
```

### 审查 Git Diff

```bash
# 审查当前的 git diff
code-review-assistant diff

# 审查特定分支
code-review-assistant diff main..feature-branch
```

### 审查 PR

```bash
code-review-assistant pr --owner username --repo reponame --pr-number 123
```

## 输出示例

```markdown
# Code Review Report

## File: src/utils.js

### Issues Found: 3

#### 🔴 High Priority (1)

1. **Line 45: Potential SQL Injection**
   ```javascript
   const query = `SELECT * FROM users WHERE id = ${userId}`;
   ```
   → Use parameterized queries instead

#### 🟡 Medium Priority (2)

2. **Line 23: Missing Error Handling**
   ```javascript
   const data = JSON.parse(response);
   ```
   → Add try-catch block

3. **Line 67: Hardcoded API Key**
   ```javascript
   const API_KEY = "sk-1234567890";
   ```
   → Use environment variables

#### 🟢 Suggestions (5)

- Consider using const instead of let
- Add JSDoc comments
- Extract function at line 100
- ...

---

### Summary

| Category | Count |
|----------|-------|
| Security | 1 |
| Performance | 0 |
| Best Practices | 3 |
| Code Style | 2 |

**Recommendation**: Fix high priority issues before merging
```

## 配置

### 规则配置

```bash
# 启用/禁用特定规则
code-review-assistant config --enable security,performance --disable style

# 设置严重级别
code-review-assistant config --severity high
```

### 忽略文件

创建 `.codereviewignore` 文件：

```
# Ignore node_modules
node_modules/

# Ignore build output
dist/
build/
```

## 安装

```bash
# 无需额外依赖
# 使用内置代码分析
```

## CI/CD 集成

### GitHub Actions

```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Code Review
        run: |
          code-review-assistant review . --output report.md
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: code-review-report
          path: report.md
```

## 变现思路

1. **GitHub Marketplace** - 发布 GitHub Action
2. **付费规则集** - 提供专业版规则
3. **企业版** - 自托管版本
4. **代码质量服务** - 为企业提供代码审查服务
