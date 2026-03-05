# Zadig DevOps Platform Skill

Zadig 是一个面向云原生应用的 DevOps 平台。这个 Skill 提供了 Zadig OpenAPI 的完整客户端实现。

## 快速开始

### 1. 配置环境变量

在 `~/.openclaw/workspace/.env` 中添加：

```bash
ZADIG_API_URL=https://your-zadig.example.com/api
ZADIG_API_KEY=your-jwt-token-here
ZADIG_DEFAULT_PROJECT=yaml
ZADIG_DEFAULT_ENV=dev
```

### 2. 获取 API Token

1. 登录 Zadig 平台
2. 点击右上角用户头像
3. 选择 `账号设置`
4. 复制 API Token

### 3. 测试连接

```bash
cd ~/project/workspace/skills/zadig
node scripts/list-projects.js
```

## 主要功能

| 模块 | 功能 |
|------|------|
| 项目 | 创建/查询/删除项目 |
| 工作流 | 触发/查询/取消/重试/审批工作流 |
| 环境 | 管理测试/生产环境、服务、镜像 |
| 服务 | 查询服务配置和状态 |
| 构建 | 管理构建配置和执行 |
| 测试 | 执行测试并获取报告 |
| 发布 | 版本管理和发布计划 |
| 集群 | 管理 Kubernetes 集群 |
| 仓库 | 集成镜像仓库 |
| 权限 | 用户、角色、成员管理 |
| 统计 | 效能洞察数据 |
| 日志 | 查看容器和工作流日志 |

## 常用命令

```bash
# 项目
node scripts/list-projects.js

# 工作流
node scripts/list-workflows.js --project=yaml
node scripts/trigger-workflow.js --project=yaml --workflow=build-deploy
node scripts/workflow-status.js --project=yaml --workflow=build-deploy --task=12345

# 环境
node scripts/list-envs.js --project=yaml

# 更新镜像
node scripts/update-image.js --project=yaml --env=dev --workload=myapp --image=nginx:1.22
```

## 文档

- [SKILL.md](./SKILL.md) - Agent 使用说明
- [OpenAPI 规范](https://docs.koderover.com) - Zadig 官方文档

## 版本

- Skill 版本：2.0.0
