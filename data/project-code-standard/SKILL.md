---
name: project-code-standard
description: >
  此 skill 用于检查、执行和修复项目代码规范。当用户需要为项目建立代码风格标准、
  检查代码是否符合规范、自动修复格式问题、生成代码质量报告，或在 Code Review 
  中验证提交是否满足团队规范时激活。支持 Python (PEP8/black/ruff)、JavaScript/
  TypeScript (ESLint/Prettier)、通用项目规范（命名、注释、文件结构）等。
version: 1.0.0
author: ForestAgentLab
tags:
  - code-quality
  - standards
  - linting
  - formatting
  - code-review
---

# Project Code Standard

## 目标

帮助开发者为项目建立、检查和执行统一的代码规范，确保代码库的一致性、可读性和可维护性。

## 何时使用

激活此 skill 的场景：

- 用户要求「检查代码规范」「lint 代码」「格式化代码」
- 用户要求「建立代码标准」「设置代码风格」
- 在 Code Review 前验证代码质量
- 用户询问「这段代码符合规范吗？」
- 新项目初始化时配置代码质量工具链
- CI/CD 集成代码检查流程

## 前置条件

根据项目类型，需要以下工具之一：

- **Python 项目**：Python >= 3.8，可选安装 `ruff`、`black`、`pylint`
- **JS/TS 项目**：Node.js >= 16，可选安装 `eslint`、`prettier`
- **通用**：无特殊依赖，使用内置检查逻辑

## 执行步骤

### 步骤 1：识别项目类型

首先检查项目根目录，识别技术栈：

```bash
# 检查关键配置文件
ls package.json pyproject.toml setup.py Cargo.toml go.mod 2>/dev/null
```

根据识别结果选择对应的规范检查流程。

### 步骤 2：运行规范检查

**Python 项目**：

```bash
# 使用 ruff 进行快速全面检查（推荐）
python scripts/check_python.py <target_path> --output markdown

# 或者逐步检查
ruff check .               # 代码规范
ruff format --check .      # 格式检查
```

**JavaScript / TypeScript 项目**：

```bash
python scripts/check_js.py <target_path> --output markdown
```

**通用规范检查**（命名、注释、文件结构）：

```bash
python scripts/check_general.py <target_path> --output markdown
```

### 步骤 3：呈现检查结果

将检查结果组织为以下格式汇报给用户：

```markdown
## 代码规范检查报告

### 总览
- 检查文件数：N
- 发现问题：X 个（严重：A，警告：B，提示：C）

### 问题列表
| 文件 | 行号 | 类型 | 描述 |
|------|------|------|------|
| ... | ... | ... | ... |

### 建议修复方案
...
```

### 步骤 4：自动修复（可选）

如果用户同意自动修复，执行：

```bash
# Python
python scripts/check_python.py <target_path> --fix

# JS/TS  
python scripts/check_js.py <target_path> --fix
```

修复后重新运行步骤 2 验证结果。

### 步骤 5：生成规范配置文件（新项目）

如果项目尚无规范配置，从 `assets/` 目录复制对应模板：

- Python：`assets/ruff.toml` → 项目根目录
- JS/TS：`assets/.eslintrc.json` + `assets/.prettierrc` → 项目根目录
- 通用：`assets/.editorconfig` → 项目根目录

## 输出格式

以 Markdown 表格格式汇报检查结果，包含：

1. **总览统计**：文件数、问题数、按严重级别分类
2. **问题列表**：文件路径、行号、问题类型、描述
3. **修复建议**：针对高频问题给出具体修复方案

## 注意事项

- 优先使用项目中已有的 lint 配置（`.eslintrc`、`ruff.toml` 等），不要覆盖用户已有配置
- 自动修复前**必须**获得用户确认，不要直接修改文件
- 检查范围默认排除 `node_modules/`、`.venv/`、`dist/`、`build/` 等目录
- 如果项目没有安装 lint 工具，仅做语法层面和通用规范检查，并建议安装工具
