---
name: saas-landing-page-generator
description: 生成现代 SaaS 产品的 Landing Page，支持多种风格，输出 HTML/CSS/React 代码，直接可部署。
metadata: {"clawdbot":{"emoji":"🚀","requires":{},"primaryEnv":""}}
---

# SaaS Landing Page Generator

生成专业的 SaaS 产品 Landing Page，一键生成可直接部署的代码。

## 功能

- 🎨 多种设计风格
- 📱 完全响应式
- ⚡ 性能优化
- 🧩 组件化代码
- 🎯 SEO 友好
- 📦 直接可部署

## 模板风格

| 风格 | 适用产品 |
|------|---------|
| `modern` | SaaS、Dashboard、AI 工具 |
| `minimal` | 简约工具、Chrome 插件 |
| `b2b` | 企业服务、API 产品 |
| `mobile-app` | iOS/Android 应用 |
| `developer` | 开发者工具、SDK |

## 使用方法

### 生成 Landing Page

```bash
# 基本用法
saas-landing-page "产品名称" "一句话描述"

# 指定风格
saas-landing-page "AI Writer" "AI-powered writing assistant" --template modern

# 指定技术栈
saas-landing-page "产品" "描述" --stack react --style tailwind
```

### 选项

| 选项 | 说明 |
|------|------|
| `--template, -t` | 模板风格 |
| `--stack, -s` | 技术栈 (html, react, vue, nextjs) |
| `--style, -st` | 样式 (tailwind, bootstrap, plain) |
| `--output, -o` | 输出目录 |
| `--color, -c` | 主色调 |

## 输出结构

```
my-saas-landing/
├── index.html          # 或 App.js (React)
├── styles.css         # 或 Tailwind 配置
├── components/
│   ├── Hero.jsx
│   ├── Features.jsx
│   ├── Pricing.jsx
│   ├── Testimonials.jsx
│   ├── CTA.jsx
│   └── Footer.jsx
├── assets/
└── package.json        # 如果是 React/Next.js
```

## 示例

### AI 产品

```bash
saas-landing-page "CodeGenius" "AI-powered code generator for developers" --template modern --stack nextjs --color purple
```

### B2B 产品

```bash
saas-landing-page "TeamSync" "Enterprise team collaboration platform" --template b2b --stack react --color blue
```

### 开发者工具

```bash
saas-landing-page "APIDoc" "Auto-generate API documentation" --template developer --stack nextjs
```

## 包含的组件

- ✅ Hero Section (带 CTA)
- ✅ Features Grid
- ✅ How It Works
- ✅ Pricing Tables
- ✅ Testimonials
- ✅ Logo Cloud
- ✅ FAQ Section
- ✅ CTA Banner
- ✅ Footer
- ✅ Mobile Menu
- ✅ Loading Animation

## SEO 优化

生成的页面包含：
- Meta 标签
- Open Graph 标签
- 结构化数据
- Semantic HTML
- 优化的图片占位符
- Sitemap 模板

## 变现思路

1. **模板市场** - 在 Gumroad/ThemeForest 销售
2. **定制服务** - 为客户定制 Landing Page
3. **SaaS 模板** - 构建一个 Landing Page 模板库网站
4. **Fiverr 服务** - 低价快速生成

## 安装

```bash
# 无需依赖
```

## 技术栈支持

- Plain HTML/CSS
- React + CSS Modules
- React + Tailwind CSS
- Next.js + Tailwind
- Vue 3 + Tailwind

## 示例输出

生成的页面包含专业的设计：

- 现代化的 UI
- 渐变和动画
- 响应式布局
- 交互式组件
- 优化的加载速度
