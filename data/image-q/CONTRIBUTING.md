# Contributing Guide

本文档说明如何参与 `image-gen` Skill 的开发与迭代。

## 项目结构

```
image-gen-skill/
├── SKILL.md          # Skill 核心定义文件（OpenClaw 读取此文件）
├── generate.js       # 图片生成核心脚本（Node.js ESM）
├── package.json      # 依赖声明（@fal-ai/client）
├── .gitignore
├── CONTRIBUTING.md   # 本文件
└── CHANGELOG.md      # 版本更新记录
```

## 开发环境准备

```bash
# 1. 克隆仓库
git clone https://github.com/wells1137/image-gen-skill.git
cd image-gen-skill

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Keys：
# FAL_KEY=your_fal_key
# TTAPI_KEY=your_ttapi_key
```

## 本地测试

```bash
# 测试 Flux Dev（最快，无需 TTAPI_KEY）
FAL_KEY=your_key node generate.js \
  --model flux-dev \
  --prompt "a cute cat, photorealistic" \
  --aspect-ratio 1:1

# 测试 Midjourney（需要 TTAPI_KEY）
TTAPI_KEY=your_key node generate.js \
  --model midjourney \
  --prompt "a majestic snow leopard, cinematic" \
  --aspect-ratio 16:9
```

## 支持的模型

| Model Key | 供应商 | 说明 |
|---|---|---|
| `midjourney` | TTAPI | 艺术感最强，需要 TTAPI_KEY |
| `flux-pro` | fal.ai | 最高质量写实图 |
| `flux-dev` | fal.ai | 通用高质量 |
| `flux-schnell` | fal.ai | 最快，适合草稿 |
| `sdxl` | fal.ai | SDXL Lightning 4步 |
| `nano-banana` | fal.ai | Gemini 驱动 |
| `ideogram` | fal.ai | 最强文字排版 |
| `recraft` | fal.ai | 矢量/图标风格 |

## 开发规范

- **分支命名**：`feature/xxx`、`fix/xxx`、`chore/xxx`
- **提交规范**：使用 [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat: 新增 xxx 模型支持`
  - `fix: 修复 Midjourney 轮询超时问题`
  - `docs: 更新 SKILL.md 使用说明`
- **PR 流程**：从 `feature` 分支发起 PR 到 `main`，需至少 1 人 Review

## 发布新版本到 ClawHub

```bash
# 安装 clawhub CLI（如未安装）
npm i -g clawhub

# 登录（使用 Token）
clawhub login --token <your_clawhub_token>

# 发布新版本
clawhub publish . \
  --slug image-gen \
  --name "Image Gen" \
  --version 1.x.x \
  --changelog "本次更新内容..." \
  --tags "latest,image,midjourney,flux,sdxl,fal,generation,ai"
```

## 常见问题

**Q: FAL_KEY 从哪里获取？**
A: 访问 [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) 创建 API Key。

**Q: TTAPI_KEY 从哪里获取？**
A: 访问 [ttapi.io/dashboard](https://ttapi.io/dashboard) 获取 API Key。

**Q: 如何新增一个模型？**
A: 在 `generate.js` 的 `FAL_MODELS` 对象中添加新的模型 ID，然后在对应的 `generateFal()` 函数中添加 input 构建逻辑，最后更新 `SKILL.md` 的模型选择指南。
