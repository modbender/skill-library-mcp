# 05 — 安全红线 + 验收

## 绝对不能 Vibe Code 的领域

```
🔴 认证和授权（Auth）
🔴 支付和金融
🔴 数据库 Schema 和 Migration
🔴 用户数据处理（GDPR/隐私）
🔴 API Key 和 Secret 管理
🔴 安全相关的中间件

这些必须人工逐行 Review。没有例外。
```

## 安全检查清单

```
每次 AI 生成代码后检查:
□ 没有硬编码的 API Key / Secret
□ 没有 console.log 输出敏感信息
□ SQL 查询使用参数化
□ 用户输入有验证和消毒
□ API 端点有认证检查
□ 文件操作有路径验证（防目录遍历）
□ 没有不必要的依赖
□ 没有 eval() 或 Function()
```

## 依赖管理

```
规则: AI 不能自行安装依赖

在规则文件中写：
"安装新依赖前必须告诉我包名、版本、用途，获得确认后再安装"
```

---

## 验收 Checklist

```
□ 功能验收
  □ 核心功能正常
  □ 边界条件（空值、超长输入）
  □ 错误状态有 UI 反馈
  □ 移动端 / 跨浏览器

□ 代码质量
  □ TypeScript 无错误
  □ Lint 通过
  □ 无 any 类型
  □ 关键函数有注释

□ 测试
  □ 单元测试通过
  □ 覆盖率 ≥ 80%（关键路径）

□ 安全
  □ 安全检查清单全部通过
  □ npm/pip audit 无高危

□ 性能
  □ 页面加载 < 3s
  □ API 响应 < 500ms
  □ 无内存泄漏

□ 文档
  □ README 更新
  □ CHANGELOG 记录
```

## AI 辅助验收 Prompt

```
"作为高级代码审查者，review 以下改动：
[git diff]

检查：
1. 逻辑正确性
2. 安全性
3. 性能
4. 可维护性
5. 测试覆盖

输出：
🔴 Critical: [必须修]
🟡 Warning: [建议修]
🟢 Good: [做得好]"
```

## 自动化验收脚本

**Bash 版：**
```bash
#!/bin/bash
echo "🔍 Running verification..."
npx tsc --noEmit || { echo "❌ TypeScript errors"; exit 1; }
npx eslint . --max-warnings 0 || { echo "❌ Lint errors"; exit 1; }
npm test || { echo "❌ Tests failed"; exit 1; }
npm run build || { echo "❌ Build failed"; exit 1; }
npm audit --audit-level=high || { echo "⚠️ Security issues"; }
echo "✅ All checks passed!"
```

**PowerShell 版（Win11 适配）：**
```powershell
# verify.ps1
Write-Host "🔍 Running verification..." -ForegroundColor Cyan

# TypeScript
Write-Host "→ TypeScript check..."
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { Write-Host "❌ TypeScript errors" -ForegroundColor Red; exit 1 }

# Lint
Write-Host "→ ESLint..."
npx eslint . --max-warnings 0
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Lint errors" -ForegroundColor Red; exit 1 }

# Tests
Write-Host "→ Running tests..."
npm test
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Tests failed" -ForegroundColor Red; exit 1 }

# Build
Write-Host "→ Building..."
npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Build failed" -ForegroundColor Red; exit 1 }

# Security
Write-Host "→ Security audit..."
npm audit --audit-level=high
if ($LASTEXITCODE -ne 0) { Write-Host "⚠️ Security issues" -ForegroundColor Yellow }

Write-Host "✅ All checks passed!" -ForegroundColor Green
```
