---
name: tech-solution-generator
version: 1.0.0
description: 技术方案文档自动生成器。根据需求自动生成完整的技术方案文档，包含架构设计、技术选型、风险评估、排期估算。
author: imgolye
metadata:
  clawdbot:
    emoji: 📋
    category: productivity
    tags: [tech, solution, architecture, documentation, design]
---

# 技术方案文档生成器

自动生成专业的技术方案文档，让架构设计变得简单高效！

## 核心功能

✅ **需求分析** - 自动分析业务需求
✅ **架构设计** - 生成系统架构图描述
✅ **技术选型** - 推荐合适的技术栈
✅ **风险评估** - 识别潜在风险和应对方案
✅ **排期估算** - 基于功能点的工时估算
✅ **接口设计** - 自动生成API接口定义

## 使用场景

- 产品需求评审前，快速生成技术方案
- 项目立项时，提供技术可行性分析
- 团队协作时，统一技术方案格式
- 技术分享时，生成标准化文档

## 文档结构

### 1. 项目概述

```markdown
## 项目背景
[自动生成项目背景描述]

## 业务目标
[提取核心业务目标]

## 技术目标
- 性能目标：响应时间 < 200ms
- 可用性目标：99.9%
- 扩展性目标：支持10倍流量增长
```

### 2. 系统架构

```markdown
## 整体架构
[生成架构图描述]

┌─────────────┐
│   前端层    │
├─────────────┤
│   网关层    │
├─────────────┤
│  服务层     │
├─────────────┤
│  数据层     │
└─────────────┘

## 技术选型
- 前端：Vue 3 + Vite
- 后端：Spring Boot 2.7
- 数据库：MySQL 8.0
- 缓存：Redis 6.0
```

### 3. 核心功能设计

```markdown
## 功能模块1：用户管理
### 功能描述
[详细功能描述]

### 接口设计
POST /api/v1/users/register
Request:
{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "userId": "string",
    "token": "string"
  }
}

### 数据库设计
Table: users
- id: BIGINT PRIMARY KEY
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(100) UNIQUE
- password: VARCHAR(255)
- created_at: DATETIME
- updated_at: DATETIME
```

### 4. 风险评估

```markdown
## 技术风险
| 风险项 | 影响 | 概率 | 应对方案 |
|--------|------|------|---------|
| 高并发性能 | 高 | 中 | 引入缓存、消息队列 |
| 数据一致性 | 高 | 低 | 分布式事务、最终一致性 |
| 第三方依赖 | 中 | 中 | 服务降级、熔断机制 |

## 业务风险
[自动识别业务风险]

## 进度风险
[基于历史数据的进度风险评估]
```

### 5. 排期估算

```markdown
## 工作量估算（人天）

### 后端开发
- 用户模块：3人天
- 订单模块：5人天
- 支付模块：4人天
- 总计：12人天

### 前端开发
- 页面开发：8人天
- 接口联调：3人天
- 总计：11人天

### 测试
- 单元测试：3人天
- 集成测试：2人天
- 总计：5人天

## 项目排期
- 需求评审：1天
- 技术方案：2天
- 开发阶段：15天
- 测试阶段：5天
- 上线部署：2天
- 总工期：25天
```

## 使用方式

### 方式一：提供需求文档

```
"根据这个PRD生成技术方案：
[粘贴需求文档内容]"
```

### 方式二：简单描述需求

```
"帮我生成一个电商系统的技术方案"
"设计一个积分管理系统的架构"
```

### 方式三：指定技术栈

```
"用Spring Boot + Vue生成一个CRM系统的技术方案"
```

## 输出格式

支持多种输出格式：

1. **Markdown** - 适合 GitHub/GitLab
2. **HTML** - 适合网页展示
3. **PDF** - 适合正式文档
4. **Word** - 适合企业内部

## 技术栈推荐

根据项目类型自动推荐：

| 项目类型 | 推荐技术栈 |
|---------|-----------|
| Web应用 | Spring Boot + Vue 3 |
| 移动应用 | Flutter / React Native |
| 微服务 | Spring Cloud + K8s |
| 数据平台 | Spark + Flink |
| AI应用 | FastAPI + PyTorch |

## 成功案例

### 案例1：积分联盟系统

**输入**：
```
华润万家积分联盟系统
功能：商家入驻、积分通兑、券码管理、结算对账
```

**输出**：
```markdown
## 系统架构

### 微服务拆分
1. merchant-manage（8085）- 商家入驻管理
2. exchange-manage（8084）- 通兑管理
3. voucher-manage（8081）- 券码管理
4. settlement（8089）- 结算对账
5. exchange-trade（8086）- 通兑交易
6. voucher-trade（8082）- 券码交易

### 技术选型
- 后端：Spring Boot 2.7.18 + MyBatis-Plus
- 前端：Vue 3 + Ant Design Vue
- 数据库：MySQL 8.0
- 缓存：Redis

### 数据库设计
[14张核心表，47+条测试数据]

### 排期估算
- 总工期：25天
- 后端开发：15人天
- 前端开发：10人天
```

---

### 案例2：电商秒杀系统

**输入**：
```
电商秒杀系统
支持10万QPS
库存扣减不能出错
```

**输出**：
```markdown
## 架构设计

### 高并发架构
1. CDN加速 - 静态资源
2. Redis集群 - 库存预热
3. 消息队列 - 削峰填谷
4. 分布式锁 - 防止超卖

### 核心流程
1. 用户请求 → 网关限流
2. 查询Redis库存 → 预扣减
3. 发送MQ消息 → 异步下单
4. MySQL最终扣减 → 保证一致性

### 技术选型
- 网关：Spring Cloud Gateway
- 缓存：Redis Cluster（3主3从）
- 消息队列：RocketMQ
- 数据库：MySQL（主从复制）

### 性能指标
- QPS：10万+
- 响应时间：<100ms
- 可用性：99.99%
```

---

## 定制化选项

### 可配置参数

```json
{
  "projectType": "web|mobile|microservice",
  "techStack": "spring-boot|django|express",
  "performance": {
    "qps": 10000,
    "responseTime": "200ms",
    "availability": "99.9%"
  },
  "team": {
    "backend": 3,
    "frontend": 2,
    "test": 1
  },
  "timeline": "1个月"
}
```

### 输出模板

支持自定义模板：
- 标准模板（默认）
- 简化模板（快速评审）
- 详细模板（正式立项）

---

## 快速开始

告诉我你的需求，我会立即生成完整的技术方案！

**示例**：
```
"帮我生成一个在线教育平台的技术方案"
```

我会生成：
1. ✅ 系统架构设计
2. ✅ 技术选型建议
3. ✅ 数据库设计
4. ✅ 接口设计
5. ✅ 风险评估
6. ✅ 排期估算

---

## 更新日志

### v1.0.0 (2026-03-01)
- ✨ 首次发布
- ✨ 自动架构设计
- ✨ 技术选型推荐
- ✅ 风险评估
- ✅ 排期估算
- ✅ 接口设计

---

**Keywords**: 技术方案, 架构设计, 技术选型, documentation, architecture, design
