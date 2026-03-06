---
name: magicbox-node-dev规范
description: Node.js + TypeScript 项目开发规范和最佳实践指南。用于指导 MagicBox Node 服务的开发、代码风格、目录结构、配置管理、容器部署等方面的规范。
---

# MagicBox Node 项目开发规范

## 项目结构

### 目录结构

```
magicbox-node/
├── src/             # 源代码目录
│   ├── config/      # 配置文件
│   ├── controllers/ # 控制器
│   ├── middleware/  # 中间件
│   ├── migrations/  # 数据库迁移
│   ├── models/      # 数据模型
│   ├── routes/      # 路由
│   ├── services/    # 业务逻辑
│   ├── utils/       # 工具函数
│   └── app.ts       # 应用入口
├── scripts/         # 脚本文件
├── servers/         # 服务器配置
├── .env.example     # 环境变量示例
├── .eslintrc.js     # ESLint 配置
├── .prettierrc      # Prettier 配置
├── Dockerfile.base  # Docker 基础镜像
├── package.json     # 项目配置
└── tsconfig.json    # TypeScript 配置
```

## 代码规范

### TypeScript 规范

1. **类型定义**：使用强类型，避免 `any` 类型
2. **接口命名**：使用 PascalCase，如 `UserInterface`
3. **类命名**：使用 PascalCase，如 `UserService`
4. **函数命名**：使用 camelCase，如 `getUser`
5. **变量命名**：使用 camelCase，如 `userName`
6. **常量命名**：使用 UPPER_CASE，如 `MAX_RETRY_COUNT`

### ESLint 配置

项目使用 ESLint 进行代码质量检查，配置文件：`.eslintrc.js`

### Prettier 配置

项目使用 Prettier 进行代码格式化，配置文件：`.prettierrc`

## 配置管理

### 环境变量

- **开发环境**：使用 `.env.develop` 文件
- **生产环境**：使用 `/etc/magicbox-node/env.config.json` 文件
- **环境变量优先级**：系统环境变量 > 配置文件 > 默认值

### 配置文件结构

```json
{
  "NODE_ENV": "production",
  "PORT": "3000",
  "HOST": "0.0.0.0",
  "DB_HOST": "database-host",
  "DB_PORT": "3306",
  "DB_DATABASE": "magicbox",
  "DB_USERNAME": "username",
  "DB_PASSWORD": "password"
}
```

## 数据库规范

### 数据模型

- 使用 TypeORM 进行数据库操作
- 模型文件放在 `src/models/` 目录
- 实体命名使用 PascalCase，如 `UserEntity.ts`

### 数据库迁移

- 迁移文件放在 `src/migrations/` 目录
- 迁移文件命名格式：`YYYYMMDDHHmmss-description.ts`

## 容器部署

### Docker 配置

- 使用 `Dockerfile.base` 构建基础镜像
- 容器运行时环境变量通过 Kubernetes 配置
- 确保容器启动时目录存在：`/export/Data`

### 启动脚本

- `start.sh`：容器启动脚本
- `scripts/deploy-manual.sh`：部署时版本管理脚本

## 版本管理

- 使用 `version.json` 文件管理版本信息
- 版本号格式：`major.minor.patch`
- 部署时自动更新版本信息

## API 规范

### 路由结构

- 健康检查：`/health`
- API 路由：`/api/{resource}`
- 遵循 RESTful 设计原则

### 响应格式

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

## 日志规范

- 使用 `src/utils/logger.ts` 进行日志记录
- 日志级别：debug, info, warn, error
- 生产环境使用 info 级别

## 错误处理

- 使用统一的错误处理中间件
- 生产环境不返回详细错误信息
- 记录错误日志

## 安全规范

- 敏感配置使用环境变量
- 密码等敏感信息不硬编码
- 使用 HTTPS 协议
- 实现 CORS 配置

## 部署流程

1. 代码提交到 Git 仓库
2. 运行 `scripts/deploy-manual.sh` 更新版本
3. 构建 Docker 镜像
4. 部署到 Kubernetes 集群
5. 验证服务健康状态

## 开发工具

- **IDE**：推荐使用 VS Code
- **插件**：ESLint, Prettier, TypeScript
- **包管理器**：npm
- **构建工具**：TypeScript compiler (tsc)

## 代码审查

- 提交代码前运行 `npm run lint`
- 提交代码前运行 `npm run build`
- 代码审查关注：类型定义、错误处理、安全隐患

## 性能优化

- 使用 TypeScript 编译优化
- 数据库查询优化
- 缓存策略
- 合理使用中间件

## 监控与告警

- 实现健康检查端点
- 监控服务运行状态
- 配置适当的告警机制

## 最佳实践

1. **模块化**：将功能拆分为小模块
2. **可测试性**：编写可测试的代码
3. **文档**：为关键功能添加注释
4. **一致性**：保持代码风格一致
5. **安全性**：优先考虑安全问题
6. **性能**：关注代码性能
7. **可维护性**：编写易于维护的代码