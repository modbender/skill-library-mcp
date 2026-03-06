# Cue v1.0.4 - Node.js 重构版

## 📦 架构概述

Cue v1.0.4 是基于 **Node.js + ES Module** 重构的深度研究工具，采用模块化设计，提供更好的可维护性和跨平台支持。

### 技术栈
- **Runtime**: Node.js >= 18.0.0
- **Module**: ES Module (type: "module")
- **CLI**: Commander.js
- **Dependencies**: 10+ npm 包 (chalk, ora, inquirer, node-cron, fs-extra 等)

## 📂 文件结构

```
cue/
├── manifest.json              # 技能清单
├── SKILL.md                   # 技能描述（双语）
├── SECURITY.md                # 安全说明
├── README.md                  # 本文件
├── package.json               # npm 配置
├── src/                       # 源代码目录
│   ├── index.js              # 主入口（模块导出）
│   ├── cli.js                # CLI 入口（Commander）
│   ├── core/                 # 核心业务逻辑
│   │   ├── logger.js         # 统一日志系统
│   │   ├── userState.js      # 用户状态管理
│   │   ├── taskManager.js    # 任务管理
│   │   └── monitorManager.js # 监控管理
│   ├── api/
│   │   └── cuecueClient.js   # API 客户端
│   ├── commands/             # 命令处理器
│   ├── utils/                # 工具函数
│   │   ├── fileUtils.js      # 文件操作
│   │   ├── envUtils.js       # 环境变量（安全存储）
│   │   └── validators.js     # 验证工具
│   └── executors/            # 执行引擎
├── tests/                    # 测试文件
└── backups/                  # 旧版本备份
    └── scripts-v1.0.3/       # v1.0.3 Bash 脚本备份
```

## 🚀 部署步骤

### 步骤 1：环境要求

**必需**: Node.js >= 18.0.0

```bash
# 检查 Node.js 版本
node --version  # 应 >= v18.0.0

# 如未安装，请访问 https://nodejs.org/
```

### 步骤 2：安装依赖

```bash
cd cue
npm install
```

**依赖列表**:
- `commander` - CLI 框架
- `chalk` - 终端颜色
- `ora` - 加载动画
- `inquirer` - 交互提示
- `node-cron` - 定时任务（不修改系统 crontab）
- `fs-extra` - 增强文件操作

### 步骤 3：配置环境变量

**必需**:
```bash
export CUECUE_API_KEY="your-cuecue-api-key"
```

**可选**:
```bash
export TAVILY_API_KEY="your-tavily-api-key"  # 用于监控功能
export CHAT_ID="your-chat-id"                # 通知目标
```

**安全说明**: API Key 存储在 `~/.cuecue/.env.secure`，权限 600

### 步骤 4：启动

```bash
# CLI 模式
npm run cli

# 或直接使用
node src/cli.js
```

## 🎯 核心功能

### 1. 深度研究 / Deep Research
- **常见耗时**: 5-30 分钟
- **超时**: 3600 秒（60分钟）
- **进度推送**: 每 5 分钟

```javascript
// 启动研究
await handleCue(['宁德时代2024财报']);
```

### 2. 研究视角模式

| 模式 | 自动匹配关键词 | 框架 |
|------|--------------|------|
| trader | 龙虎榜、涨停、游资 | Timeline Reconstruction |
| fund-manager | 财报、估值、ROE | 基本面分析 |
| researcher | 产业链、竞争格局 | Peer Benchmarking |
| advisor | 投资建议、资产配置 | 风险收益评估 |

### 3. 智能监控

**后台调度**: 使用 `node-cron` 内部调度，**不修改系统 crontab**

```javascript
// 监控守护进程（每30分钟）
cron.schedule('*/30 * * * *', async () => {
  await checkMonitors();
});
```

## 📋 可用命令

| 命令 | 功能 | 耗时 |
|------|------|------|
| `/cue <主题>` | 智能调研 | 40-60 分钟 |
| `/ct` | 查看任务状态 | 即时 |
| `/cm` | 查看监控项 | 即时 |
| `/cn [天数]` | 查看监控通知 | 即时 |
| `/key <api-key>` | 配置 API Key | 即时 |
| `/ch` | 显示帮助 | 即时 |

## ✅ 功能验证

```bash
# 1. 检查 Node.js 版本
node --version

# 2. 安装依赖
npm install

# 3. 运行测试
npm test

# 4. CLI 测试
npm run cli cue "测试主题"
```

## 🔧 关键配置

### 核心参数
| 参数 | 值 | 说明 |
|------|-----|------|
| 研究超时 | 3600秒 | 60分钟上限 |
| 进度推送 | 300秒 | 每5分钟更新 |
| 监控调度 | */30 * * * * | 每30分钟检查 |
| BASE_URL | https://cuecue.cn | 硬编码 |

### 数据存储
```
~/.cuecue/
├── users/
│   └── ${chat_id}/
│       ├── .initialized
│       ├── tasks/           # 任务数据
│       └── monitors/        # 监控配置
├── logs/
│   ├── cue-YYYYMMDD.log
│   ├── error-YYYYMM.log
│   └── info-YYYYMM.log
└── .env.secure              # API Key (权限 600)
```

## 🆚 v1.0.4 vs v1.0.3

| 维度 | v1.0.3 (Bash) | v1.0.4 (Node.js) |
|------|---------------|------------------|
| 架构 | Bash 脚本 | Node.js ES Module |
| 文件数 | 11 个 .sh | 10 个 .js 模块 |
| 依赖 | 系统工具 (jq, curl) | npm 包 |
| 调度 | 系统 crontab | node-cron (内部) |
| 可维护性 | 中 | 高 |
| 跨平台 | Linux/Mac | Windows/Mac/Linux |
| 启动速度 | 快 | 稍慢 |
| 扩展性 | 低 | 高 |

## 📝 更新日志

### v1.0.4 (2026-02-25)

**架构重构**:
- ✨ 全面迁移到 Node.js ES Module
- ✨ 模块化设计 (core/api/commands/utils)
- ✨ 使用 npm 依赖管理
- ✨ 内部定时任务调度（不修改系统 crontab）

**安全改进**:
- 🔒 隔离存储 `~/.cuecue/.env.secure` (权限 600)
- 🔒 目录权限 700
- 🔒 最小权限原则

**开发体验**:
- 🧪 Jest 测试框架
- 📝 JSDoc 类型注解
- 🔄 nodemon 热重载

## 🔍 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `Cannot find module` | 未安装依赖 | `npm install` |
| `node: bad option` | Node.js 版本过低 | 升级到 >= 18 |
| `Permission denied` | 文件权限 | `chmod 600 ~/.cuecue/.env.secure` |
| `API Key not found` | 未配置 | `export CUECUE_API_KEY=xxx` |

---

*Cue v1.0.4 - Node.js 重构版 - 让 AI 成为你的调研助理*
