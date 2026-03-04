---
name: docker-compose-generator
description: 生成 Docker Compose 配置，支持 MySQL, PostgreSQL, Redis, MongoDB, Elasticsearch 等常用服务。
metadata: {"clawdbot":{"emoji":"🐙","requires":{},"primaryEnv":""}}
---

# Docker Compose Generator

生成 Docker Compose 配置，快速搭建开发环境。

## 支持的服务

- MySQL
- PostgreSQL
- Redis
- MongoDB
- Elasticsearch
- RabbitMQ
- Nginx
- Node.js

## 使用方法

```bash
docker-compose-generator --db mysql --cache redis
docker-compose-generator full-stack
```

## 功能

- 一键生成 docker-compose.yml
- 网络配置
- 数据持久化
- 环境变量模板
