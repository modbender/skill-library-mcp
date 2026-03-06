# 目录结构指南

## 项目根目录

```
magicbox-node/
├── src/             # 源代码目录
├── scripts/         # 脚本文件
├── servers/         # 服务器配置
├── .env.example     # 环境变量示例
├── .eslintrc.js     # ESLint 配置
├── .prettierrc      # Prettier 配置
├── Dockerfile.base  # Docker 基础镜像
├── package.json     # 项目配置
└── tsconfig.json    # TypeScript 配置
```

## src 目录

### config

存放配置文件，如数据库配置、环境配置等。

```
src/config/
├── database.config.ts  # 数据库配置
└── env.config.ts       # 环境配置
```

### controllers

存放控制器，处理 HTTP 请求和响应。

```
src/controllers/
├── ai.controller.ts       # AI 相关控制器
├── message.controller.ts  # 消息相关控制器
└── session.controller.ts  # 会话相关控制器
```

### middleware

存放中间件，如认证、日志等。

```
src/middleware/
└── auth.middleware.ts  # 认证中间件
```

### migrations

存放数据库迁移文件。

```
src/migrations/
└── create-tables.ts  # 创建表结构
```

### models

存放数据模型，定义数据库表结构。

```
src/models/
├── message.entity.ts  # 消息模型
└── session.entity.ts  # 会话模型
```

### routes

存放路由配置，定义 API 端点。

```
src/routes/
├── ai.routes.ts       # AI 相关路由
├── index.ts           # 路由入口
├── message.routes.ts  # 消息相关路由
└── session.routes.ts  # 会话相关路由
```

### services

存放业务逻辑，处理核心业务流程。

```
src/services/
├── database.service.ts  # 数据库服务
├── message.service.ts   # 消息服务
└── session.service.ts   # 会话服务
```

### utils

存放工具函数，如日志、工具方法等。

```
src/utils/
└── logger.ts  # 日志工具
```

### app.ts

应用入口文件，初始化 Express 应用。

## scripts 目录

存放脚本文件，如部署脚本、版本管理脚本等。

```
scripts/
├── deploy-manual.sh     # 手动部署脚本
├── local-test.js        # 本地测试脚本
└── version-manager.sh   # 版本管理脚本
```

## servers 目录

存放服务器配置文件，如启动脚本等。

```
servers/
└── start.sh  # 服务器启动脚本
```

## 环境变量文件

### .env.example

环境变量示例文件，包含所有必要的环境变量。

### .env.develop

开发环境的环境变量文件。

## 配置文件

### .eslintrc.js

ESLint 配置文件，定义代码质量规则。

### .prettierrc

Prettier 配置文件，定义代码格式化规则。

### tsconfig.json

TypeScript 配置文件，定义编译选项。

### package.json

项目配置文件，定义依赖、脚本等。

## Docker 配置

### Dockerfile.base

Docker 基础镜像配置文件，定义容器构建步骤。

## 最佳实践

1. **模块化**：将功能拆分为小模块
2. **单一职责**：每个文件只负责一个功能
3. **命名规范**：使用一致的命名规范
4. **目录结构**：保持目录结构清晰
5. **配置管理**：使用环境变量管理配置