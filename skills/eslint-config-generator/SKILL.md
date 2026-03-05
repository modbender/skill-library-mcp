---
name: eslint-config-generator
description: 生成专业的 ESLint 配置，支持 React, Vue, TypeScript, Airbnb, Standard 等主流规范，一键配置代码规范。
metadata: {"clawdbot":{"emoji":"🔧","requires":{},"primaryEnv":""}}
---

# ESLint Config Generator

生成专业的 ESLint 配置文件，统一团队代码风格。

## 功能

- ⚡ 一键生成配置
- 🎯 多种规范预设
- 🔄 自动安装依赖
- 📝 支持多种框架

## 支持的规范

| 规范 | 说明 | 适用 |
|------|------|------|
| airbnb | Airbnb JavaScript 风格 | 主流项目 |
| standard | Standard JS 风格 | 简单项目 |
| prettier | Prettier 兼容配置 | 格式化优先 |
| react | React + Airbnb | React 项目 |
| vue | Vue 3 + ESLint | Vue 项目 |
| typescript | TypeScript 最佳实践 | TS 项目 |

## 使用方法

### 基本用法

```bash
# 使用 Airbnb 规范
eslint-config-generator --preset airbnb

# React + TypeScript
eslint-config-generator --preset react-typescript

# Vue 3
eslint-config-generator --preset vue
```

### 选项

| 选项 | 说明 |
|------|------|
| `--preset, -p` | 规范预设 |
| `--output, -o` | 输出文件 |
| `--install` | 自动安装依赖 |

## 输出文件

```json
{
  "extends": ["airbnb"],
  "rules": {
    "no-unused-vars": "warn",
    "react/react-in-jsx-scope": "off"
  },
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  }
}
```

## 安装依赖

```bash
npm install -D eslint eslint-config-airbnb eslint-plugin-react
```

## 变现思路

1. **预设配置销售** - 专业配置模板
2. **企业服务** - 定制代码规范
3. **培训** - 代码规范培训

## 安装

```bash
# 无需额外依赖
```
