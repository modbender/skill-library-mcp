---
name: auto-skill-builder
description: 自动构建 Claude AI Skills，结合 skill-seekers 自动生成和 skill-creator 最佳实践。支持从文档、GitHub 仓库、PDF 一键生成专业 Skill。
---

# Auto Skill Builder - 自动技能构建器

## 功能

整合 skill-seekers + skill-creator 的完整工作流：

1. **自动抓取** - 从文档/仓库/PDF 生成基础内容
2. **AI 增强** - 自动生成优质 SKILL.md
3. **质量优化** - 应用 skill-creator 最佳实践
4. **打包发布** - 生成可部署的 Skill

## 使用场景

| 场景 | 命令 |
|------|------|
| 从文档创建 Skill | `auto-skill-builder create --type docs --url https://react.dev --name react` |
| 从 GitHub 创建 Skill | `auto-skill-builder create --type github --repo facebook/react --name react` |
| 从 PDF 创建 Skill | `auto-skill-builder create --type pdf --file docs/manual.pdf --name myskill` |
| 统一抓取 (含冲突检测) | `auto-skill-builder create --type unified --config configs/react_unified.json` |

## 快速开始

### 方式 1: 从文档创建

```bash
# 基本用法
auto-skill-builder create --type docs --url https://react.dev --name react

# 带 AI 增强
auto-skill-builder create --type docs --url https://react.dev --name react --enhance

# 自定义描述
auto-skill-builder create --type docs --url https://vuejs.org --name vue \
  --description "Vue.js 3 渐进式框架"
```

### 方式 2: 从 GitHub 创建

```bash
# 基本抓取
auto-skill-builder create --type github --repo facebook/react --name react

# 包含 Issues 和代码分析
auto-skill-builder create --type github --repo django/django --name django \
  --include-issues \
  --include-code \
  --enhance

# 需要认证
export GITHUB_TOKEN=ghp_your_token
auto-skill-builder create --type github --repo mycompany/private-repo --name internal-tool
```

### 方式 3: 从 PDF 创建

```bash
# 基本提取
auto-skill-builder create --type pdf --file docs/manual.pdf --name myskill

# 提取表格
auto-skill-builder create --type pdf --file docs/manual.pdf --name myskill \
  --extract-tables

# OCR 扫描 PDF
auto-skill-builder create --type pdf --file docs/scanned.pdf --name myskill --ocr
```

### 方式 4: 统一抓取 (文档+代码)

```bash
# 使用预设统一配置
auto-skill-builder create --type unified --config configs/react_unified.json

# 查看冲突检测结果
auto-skill-builder analyze --directory output/react/
```

## 完整工作流示例

```bash
# 1. 创建基础 Skill (使用 skill-seekers)
auto-skill-builder create --type docs \
  --url https://react.dev \
  --name react \
  --enhance

# 2. 检查生成质量
auto-skill-builder quality --directory output/react/

# 3. 优化 (应用 skill-creator 最佳实践)
auto-skill-builder optimize --directory output/react/ \
  --remove-redundancy \
  --add-examples

# 4. 打包
auto-skill-builder package --directory output/react/

# 5. 安装到 OpenClaw
auto-skill-builder install --path output/react.zip --to openclaw
```

## 子命令

### create - 创建 Skill

```bash
auto-skill-builder create --type <docs|github|pdf|unified> [options]

# 选项
--type          类型: docs, github, pdf, unified
--url           文档 URL (docs)
--repo          GitHub 仓库 (github)
--file          PDF 文件路径 (pdf)
--config        配置文件路径 (unified)
--name          Skill 名称
--description   Skill 描述
--enhance       AI 增强
--enhance-local 本地增强 (推荐)
--output        输出目录 (默认: output/)
--async         异步模式 (3x 更快)
--workers       并行数 (默认: 8)
```

### analyze - 分析 Skill

```bash
auto-skill-builder analyze --directory <path>

# 分析内容
- 检查 SKILL.md 结构
- 检测缺失的字段
- 代码示例完整性
- 冲突检测 (统一抓取)
```

### optimize - 优化 Skill

```bash
auto-skill-builder optimize --directory <path> [options]

# 选项
--remove-redundancy  移除冗余内容
--add-examples       添加代码示例
--fix-frontmatter    修复 YAML frontmatter
--add-references     添加参考文档
--enhance-redirect   增强导航指引
```

### quality - 质量检查

```bash
auto-skill-builder quality --directory <path>

# 检查项目
✅ SKILL.md 结构完整性
✅ YAML frontmatter 格式
✅ 代码示例覆盖率
✅ 文档链接有效性
✅ 引用文件存在性
```

### package - 打包 Skill

```bash
auto-skill-builder package --directory <path> [options]

# 选项
--format     格式: zip (默认), tar.gz
--upload     上传到 Claude (需要 API key)
--validate   打包前验证
```

### install - 安装 Skill

```bash
# 安装到 OpenClaw
auto-skill-builder install --path <skill-path> --to openclaw

# 安装到特定目录
auto-skill-builder install --path output/react/ --to /path/to/skills/
```

## 应用 skill-creator 最佳实践

### 1. 简洁原则

自动优化：
- 移除重复内容
- 精简冗长描述
- 保留核心信息

### 2. 渐进式披露

自动组织：
```
skill-name/
├── SKILL.md (核心流程)
└── references/
    ├── quick-start.md
    ├── api-reference.md
    ├── examples.md
    └── troubleshooting.md
```

### 3. 适当自由度

根据场景选择：
- **低自由度**: 固定流程的命令 (如 `create --type docs`)
- **中自由度**: 可配置的参数 (如 `--enhance-local`)
- **高自由度**: 手动编辑 (优化后的 SKILL.md)

## 预设配置

| 预设 | 命令 |
|------|------|
| React | `auto-skill-builder create --type docs --url https://react.dev --name react` |
| Vue | `auto-skill-builder create --type docs --url https://vuejs.org --name vue` |
| Godot | `auto-skill-builder create --type docs --url https://docs.godotengine.org --name godot` |
| Django | `auto-skill-builder create --type docs --url https://docs.djangoproject.com --name django` |
| FastAPI | `auto-skill-builder create --type docs --url https://fastapi.tiangolo.com --name fastapi` |

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 抓取超时 | `--async --workers 8` |
| 速率限制 | `auto-skill-builder config --github` |
| AI 增强失败 | `--enhance-local` 本地增强 |
| 打包失败 | `auto-skill-builder quality` 先检查 |
| 安装失败 | 检查路径和权限 |

## 依赖工具

| 工具 | 用途 |
|------|------|
| skill-seekers | 文档抓取、代码分析、冲突检测 |
| Claude Code | 本地 AI 增强 |
| tar/zip | 打包 Skill |

## 相关文档

- skill-seekers: https://github.com/yusufkaraaslan/Skill_Seekers
- skill-creator: OpenClaw 内置
- OpenClaw Skills: https://clawhub.com
