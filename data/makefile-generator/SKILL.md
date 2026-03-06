---
name: makefile-generator
description: 生成专业的 Makefile，支持 Node.js、Python、Go 项目，提供开发、测试、构建、部署等常用命令。
metadata: {"clawdbot":{"emoji":"🔨","requires":{},"primaryEnv":""}}
---

# Makefile Generator

生成专业的 Makefile，统一项目构建命令。

## 功能

- ⚡ 一键生成
- 📝 多语言支持
- 🎯 常用命令
- 🔧 自定义目标

## 支持的语言

| 语言 | 命令 |
|------|------|
| Node.js | install, test, build, dev, clean |
| Python | install, test, run, clean |
| Go | build, test, run, clean |

## 使用方法

### Node.js 项目

```bash
makefile-generator --lang node
```

### Python 项目

```bash
makefile-generator --lang python
```

### Go 项目

```bash
makefile-generator --lang go
```

## 输出示例

```makefile
# Makefile for Node.js Project

.PHONY: help install dev build test clean lint format deploy

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make dev      - Start development server"
	@echo "  make build    - Build for production"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean build artifacts"

install:
	npm install

dev:
	npm run dev

build:
	npm run build

test:
	npm test

lint:
	npm run lint

format:
	npm run format

clean:
	rm -rf node_modules dist build
```

## 高级用法

### 添加自定义目标

```bash
makefile-generator --lang node --custom "docker,docker-build,docker-run"
```

### 指定包管理器

```bash
makefile-generator --lang node --pm yarn
makefile-generator --lang node --pm pnpm
```

## 安装

```bash
# 无需额外依赖
```

## 变现思路

1. **项目模板** - 销售项目模板
2. **开发服务** - 为企业配置开发环境

## 使用 Makefile 的好处

- 统一团队开发命令
- 减少记忆成本
- 自动化重复任务
- 跨平台兼容
