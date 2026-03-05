---
name: cli-scaffold-generator
description: 生成专业 CLI 脚手架，支持 Commander.js, yargs, oclif 等主流 CLI 框架，一键生成完整项目结构。
metadata: {"clawdbot":{"emoji":"🖥️","requires":{},"primaryEnv":""}}
---

# CLI Scaffold Generator

快速生成专业的 CLI 应用程序脚手架。

## 功能

- ⚡ 快速生成项目结构
- 📝 支持多种 CLI 框架
- 🎯 完整的命令模板
- 📖 自动生成帮助文档
- 🧪 测试模板
- 📦 发布到 npm

## 支持的框架

| 框架 | 说明 | 流行度 |
|------|------|--------|
| Commander.js | Node.js CLI 标准 | ⭐⭐⭐⭐⭐ |
| yargs | 参数解析强大 | ⭐⭐⭐⭐ |
| oclif | Salesforce 出品 | ⭐⭐⭐⭐ |
| Ink | React-based CLI | ⭐⭐⭐ |

## 使用方法

### 基本用法

```bash
# 使用 Commander 生成 CLI
cli-scaffold-generator my-cli --framework commander

# 使用 yargs
cli-scaffold-generator my-tool --framework yargs

# 指定描述
cli-scaffold-generator my-app --framework commander --description "My awesome CLI tool"
```

### 选项

| 选项 | 说明 |
|------|------|
| `--framework, -f` | CLI 框架 (commander/yargs/oclif/ink) |
| `--description, -d` | 项目描述 |
| `--author` | 作者名称 |
| `--output, -o` | 输出目录 |

## 生成的项目结构

```
my-cli/
├── bin/
│   └── my-cli.js       # 入口文件
├── lib/
│   └── command.js       # 命令实现
├── test/
│   └── index.test.js   # 测试文件
├── package.json
├── README.md
└── .gitignore
```

## 包含的功能

- ✅ 命令行参数解析
- ✅ 帮助信息自动生成
- ✅ 子命令支持
- ✅ 选项和标志
- ✅ 错误处理
- ✅ 彩色输出

## 示例输出

### package.json

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "description": "My awesome CLI tool",
  "bin": {
    "my-cli": "./bin/my-cli.js"
  },
  "scripts": {
    "test": "jest"
  }
}
```

### 入口文件

```javascript
#!/usr/bin/env node
const { Command } = require('commander');
const program = new Command();

program
  .name('my-cli')
  .description('My awesome CLI tool')
  .version('1.0.0');

program
  .command('greet')
  .description('Greet someone')
  .argument('<name>', 'Name to greet')
  .action((name) => {
    console.log(`Hello, ${name}!`);
  });

program.parse();
```

## 本地测试

```bash
cd my-cli
npm link
my-cli greet World
```

## 发布到 npm

```bash
npm login
npm publish
```

## 变现思路

1. **CLI 工具模板** - 销售专业 CLI 模板
2. **定制开发** - 为企业定制 CLI 工具
3. **培训课程** - CLI 开发教程
4. **工具库** - 收集常用 CLI 工具打包出售

## 安装

```bash
# 无需额外依赖
```
