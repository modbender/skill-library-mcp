# 🔒 安全扫描功能使用指南

## 概述

`clawhub-manager` 技能的 `publish.sh` 现已内置**自动安全扫描**功能，在发布技能到 ClawHub 之前会自动检查是否存在密钥泄露风险。

---

## ✨ 功能特性

### 自动检测以下安全问题：

- 🔑 **硬编码 API 密钥**
  - Tavily (tvly-...)
  - OpenAI (sk-...)
  - GitHub (ghp_, gho_, ghu_, ghs_)
  - Perplexity (pplx-...)
  - Exa AI (exa_...)
  - 通用 API Key 模式

- 🔐 **硬编码 Secret**
  - App Secret
  - 其他 Secret 模式

- 🎫 **硬编码 Token**
  - Access Token
  - 其他 Token 模式

- 📁 **敏感文件**
  - .env 文件
  - .secrets 文件
  - *.key, *.pem 文件

- 🔧 **环境变量硬编码**
  - `export API_KEY=...`
  - `export SECRET=...`

---

## 📖 使用方法

### 1. 发布时自动扫描（推荐）

```bash
# 正常发布，会自动执行安全扫描
bash publish.sh /path/to/skill --version 1.0.0

# 带更新日志
bash publish.sh /path/to/skill --version 1.0.0 --changelog "首次发布"
```

**工作流程**：
1. 执行安全扫描
2. 如果发现问题，阻止发布并显示详细报告
3. 如果通过，继续发布

### 2. 跳过安全扫描（不推荐）

```bash
# ⚠️ 仅在测试环境使用
bash publish.sh /path/to/skill --version 1.0.0 --skip-security
```

### 3. 手动安全检查

在发布前，可以先手动运行安全检查：

```bash
# 使用独立的安全检查脚本
bash security-check.sh /path/to/skill
```

**输出示例**：
```
🔒 ClawHub 技能安全检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 技能路径: /path/to/skill
━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 检查硬编码密钥...
  Tavily API Key (tvly-)... ✅ 未发现
  OpenAI API Key (sk-)... ✅ 未发现
  ...

✅ 安全检查通过！
```

---

## 🧪 测试安全扫描

使用测试脚本验证安全扫描功能：

```bash
# 运行测试脚本
bash test-security-scan.sh
```

测试脚本会：
1. 创建一个安全的测试技能（应该通过）
2. 创建一个不安全的测试技能（应该失败）
3. 验证扫描功能是否正常工作

---

## 📋 安全检查清单

发布前请确认：

- ✅ 所有 API Key、Secret、Token 使用环境变量
- ✅ 不在代码中硬编码任何密钥
- ✅ 使用占位符（如 `YOUR_API_KEY_HERE`）
- ✅ .env 文件在 .gitignore 中
- ✅ 运行安全检查并通过

### 正确示例

```bash
# ✅ 正确：从环境变量读取
API_KEY="${API_KEY}"
SECRET="${SECRET}"

# ✅ 正确：使用占位符
API_KEY="${API_KEY:-YOUR_API_KEY_HERE}"
```

### 错误示例

```bash
# ❌ 错误：硬编码密钥
API_KEY="tvly-YOUR_REAL_KEY_HERE"

# ❌ 错误：硬编码密钥
export API_KEY="tvly-YOUR_REAL_KEY_HERE"
```

---

## 🚨 如果发现密钥泄露

1. **立即撤销**已泄露的密钥
2. **重新生成**新的密钥
3. **替换为占位符**
4. **从 Git 历史中清除**（如果已提交）

```bash
# 从 Git 历史中清除敏感信息
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch FILE_WITH_KEY" \
  --prune-empty --tag-name-filter cat -- --all
```

---

## 📚 相关文档

- [SKILL.md](SKILL.md) - 技能完整文档
- [README.md](README.md) - 项目说明
- [EXAMPLES.md](EXAMPLES.md) - 使用示例

---

## 🤝 贡献

如果发现新的密钥格式需要添加，请：
1. 在 `publish.sh` 的 `security_scan()` 函数中添加检测规则
2. 在 `security-check.sh` 中添加对应的检查
3. 更新本文档

---

**维护者**: franklu0819-lang
**最后更新**: 2026-02-22
