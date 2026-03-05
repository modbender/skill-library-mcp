# SRE Agent 配置中心指南

本文档介绍如何配置 SRE Agent 连接到你现有的基础设施。

---

## 目录

1. [配置优先级](#1-配置优先级)
2. [快速配置](#2-快速配置)
3. [各组件配置详解](#3-各组件配置详解)
4. [自动创建功能](#4-自动创建功能)
5. [配置示例](#5-配置示例)
6. [API 查询](#6-api-查询)

---

## 1. 配置优先级

SRE Agent 配置中心支持三层配置，按优先级从高到低：

```
环境变量 > 配置文件 > 自动创建
```

### 1.1 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                      配置加载流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 读取环境变量 (.env)                                      │
│     ↓                                                       │
│  2. 读取配置文件 (config/infrastructure.yaml)               │
│     ↓                                                       │
│  3. 检查每个服务的连接                                        │
│     ↓                                                       │
│  4. 如果服务未配置且启用自动创建:                              │
│     → 使用 docker-compose 启动本地服务                        │
│     ↓                                                       │
│  5. 更新服务状态                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 服务状态

| 状态 | 说明 |
|------|------|
| `connected` | 已配置且连接成功 |
| `auto_created` | 未配置，但自动创建成功 |
| `failed` | 已配置但连接失败 |
| `not_configured` | 未配置且未自动创建 |

---

## 2. 快速配置

### 2.1 使用环境变量 (推荐)

最简单的方式是通过环境变量配置你现有的服务：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，填入你的服务地址
vim .env
```

**.env 示例**:
```bash
# LLM (必需)
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# 你现有的 Prometheus
PROMETHEUS_URL=http://your-prometheus:9090

# 你现有的 Loki
LOKI_URL=http://your-loki:3100

# 你现有的 Redis
REDIS_URL=redis://your-redis:6379

# 你现有的 Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092

# 你现有的 MySQL
MYSQL_HOST=your-mysql-host
MYSQL_PASSWORD=your-password
```

### 2.2 使用配置文件

也可以通过 `config/infrastructure.yaml` 配置：

```yaml
prometheus:
  enabled: true
  url: http://your-prometheus:9090

loki:
  enabled: true
  url: http://your-loki:3100

kafka:
  enabled: true
  bootstrap_servers: kafka1:9092,kafka2:9092
```

### 2.3 混合配置

你可以混合使用环境变量和配置文件：

```bash
# 敏感信息用环境变量
export MYSQL_PASSWORD=secret123
export KAFKA_SASL_PASSWORD=kafka_secret

# 其他配置用 infrastructure.yaml
```

---

## 3. 各组件配置详解

### 3.1 Prometheus / Mimir

**环境变量**:
```bash
# 标准 Prometheus
PROMETHEUS_URL=http://your-prometheus:9090

# 使用 Mimir (长期存储)
MIMIR_URL=http://your-mimir:9009
```

**配置文件**:
```yaml
prometheus:
  enabled: true
  url: http://your-prometheus:9090
  timeout_seconds: 30
  retry_attempts: 3

  # 使用 Mimir
  use_mimir: true
  mimir_url: http://your-mimir:9009

  # 认证 (可选)
  username: admin
  password: secret
  # 或 Bearer Token
  bearer_token: your-token
```

### 3.2 Loki

**环境变量**:
```bash
LOKI_URL=http://your-loki:3100
```

**配置文件**:
```yaml
loki:
  enabled: true
  url: http://your-loki:3100
  timeout_seconds: 30

  # 多租户 (可选)
  tenant_id: your-tenant

  # 认证 (可选)
  username: admin
  password: secret
```

### 3.3 Grafana

**环境变量**:
```bash
GRAFANA_URL=http://your-grafana:3000
GRAFANA_API_KEY=eyJr...
```

**配置文件**:
```yaml
grafana:
  enabled: true
  url: http://your-grafana:3000
  api_key: your-api-key
  org_id: 1
```

### 3.4 SkyWalking

**环境变量**:
```bash
SKYWALKING_URL=http://your-skywalking-oap:12800
```

**配置文件**:
```yaml
skywalking:
  enabled: true
  oap_url: http://your-skywalking-oap:12800
  ui_url: http://your-skywalking-ui:8080
  username: admin
  password: secret
```

### 3.5 Kafka

**环境变量**:
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092
KAFKA_SASL_USERNAME=user
KAFKA_SASL_PASSWORD=secret
```

**配置文件**:
```yaml
kafka:
  enabled: true
  bootstrap_servers: kafka1:9092,kafka2:9092

  # 安全配置
  security_protocol: SASL_SSL  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
  sasl_mechanism: SCRAM-SHA-256
  sasl_username: user
  sasl_password: secret

  # Topic 配置
  anomaly_topic: sre-agent-anomalies
  action_topic: sre-agent-actions
  audit_topic: sre-agent-audit
```

### 3.6 MySQL

**环境变量**:
```bash
MYSQL_HOST=your-mysql-host
MYSQL_PORT=3306
MYSQL_DATABASE=sre_agent
MYSQL_USERNAME=root
MYSQL_PASSWORD=secret
```

**配置文件**:
```yaml
mysql:
  enabled: true
  host: your-mysql-host
  port: 3306
  database: sre_agent
  username: root
  password: secret
  pool_size: 5

  # 或使用连接字符串
  connection_string: mysql://user:password@host:3306/database
```

### 3.7 Redis

**环境变量**:
```bash
# 简单模式
REDIS_URL=redis://:password@your-redis:6379/0

# 集群模式
REDIS_CLUSTER_NODES=node1:6379,node2:6379,node3:6379

# Sentinel 模式
REDIS_SENTINEL_MASTER=mymaster
REDIS_SENTINEL_NODES=sentinel1:26379,sentinel2:26379
```

**配置文件**:
```yaml
redis:
  enabled: true

  # 简单模式
  url: redis://:password@your-redis:6379/0
  # 或分开配置
  host: your-redis
  port: 6379
  password: secret
  db: 0

  # 集群模式
  cluster_mode: true
  cluster_nodes:
    - node1:6379
    - node2:6379
    - node3:6379

  # Sentinel 模式 (HA)
  sentinel_mode: true
  sentinel_master: mymaster
  sentinel_nodes:
    - sentinel1:26379
    - sentinel2:26379
```

### 3.8 Vector Database (Qdrant / Milvus)

**环境变量**:
```bash
# Qdrant
QDRANT_URL=http://your-qdrant:6333
QDRANT_API_KEY=your-api-key

# 或 Milvus
MILVUS_HOST=your-milvus
MILVUS_PORT=19530
MILVUS_USERNAME=user
MILVUS_PASSWORD=secret
```

**配置文件**:
```yaml
vector_db:
  enabled: true
  provider: qdrant  # 或 milvus

  # Qdrant 配置
  qdrant_url: http://your-qdrant:6333
  qdrant_api_key: your-api-key

  # Milvus 配置
  milvus_host: your-milvus
  milvus_port: 19530
  milvus_username: user
  milvus_password: secret

  # 通用配置
  collection_name: sre_incidents
```

---

## 4. 自动创建功能

当服务未配置时，SRE Agent 可以自动使用 docker-compose 创建本地服务。

### 4.1 配置自动创建

```yaml
# config/infrastructure.yaml
auto_create:
  enabled: true
  docker_compose_file: docker-compose.yaml
  timeout_seconds: 60

  # 指定要自动创建的服务
  services_to_create:
    - prometheus
    - loki
    - qdrant
    # - grafana  # 取消注释以启用
    # - redis
```

### 4.2 工作原理

```
1. 检查 PROMETHEUS_URL 环境变量
   ↓ 未设置
2. 检查 infrastructure.yaml 中的 prometheus.url
   ↓ 未设置
3. 检查 auto_create.services_to_create 是否包含 "prometheus"
   ↓ 包含
4. 运行: docker-compose up -d prometheus
   ↓ 成功
5. 设置 prometheus.url = http://localhost:9090
6. 标记状态为 auto_created
```

### 4.3 禁用自动创建

```yaml
auto_create:
  enabled: false
```

或使用环境变量：
```bash
AUTO_CREATE_ENABLED=false
```

---

## 5. 配置示例

### 5.1 生产环境 (全部使用现有服务)

**.env**:
```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# 监控栈
PROMETHEUS_URL=http://prometheus.monitoring.svc:9090
LOKI_URL=http://loki.monitoring.svc:3100
GRAFANA_URL=http://grafana.monitoring.svc:3000
GRAFANA_API_KEY=eyJr...

# 链路追踪
SKYWALKING_URL=http://skywalking-oap.tracing.svc:12800

# 消息队列
KAFKA_BOOTSTRAP_SERVERS=kafka-0.kafka.svc:9092,kafka-1.kafka.svc:9092
KAFKA_SASL_USERNAME=sre-agent
KAFKA_SASL_PASSWORD=xxx

# 数据库
MYSQL_HOST=mysql.database.svc
MYSQL_PASSWORD=xxx

# 缓存
REDIS_URL=redis://:xxx@redis-master.cache.svc:6379/0

# 向量数据库
QDRANT_URL=http://qdrant.ai.svc:6333

# 通知
WEBHOOK_URL=https://hooks.slack.com/services/xxx

# K8s
K8S_IN_CLUSTER=true

# 禁用自动创建
AUTO_CREATE_ENABLED=false
```

### 5.2 开发环境 (混合配置)

**.env**:
```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# 使用公司共享的 Prometheus/Loki
PROMETHEUS_URL=http://dev-prometheus.company.com:9090
LOKI_URL=http://dev-loki.company.com:3100

# 本地 Redis (将自动创建)
# REDIS_URL=  # 不设置，自动创建

# 本地 Qdrant (将自动创建)
# QDRANT_URL=  # 不设置，自动创建

# 启用自动创建
AUTO_CREATE_ENABLED=true
```

**config/infrastructure.yaml**:
```yaml
auto_create:
  enabled: true
  services_to_create:
    - qdrant
    - redis
```

### 5.3 本地全栈开发

```bash
# 启动所有本地服务
docker-compose --profile local up -d

# 或启动完整栈 (包含 Kafka, MySQL)
docker-compose --profile full up -d
```

---

## 6. API 查询

### 6.1 查看基础设施状态

```bash
curl http://localhost:8000/api/v1/infrastructure
```

**响应示例**:
```json
{
  "prometheus": {
    "status": "connected",
    "url": "http://your-prometheus:9090",
    "auto_created": false,
    "error": ""
  },
  "loki": {
    "status": "connected",
    "url": "http://your-loki:3100",
    "auto_created": false,
    "error": ""
  },
  "qdrant": {
    "status": "auto_created",
    "url": "http://localhost:6333",
    "auto_created": true,
    "error": ""
  },
  "redis": {
    "status": "not_configured",
    "url": "",
    "auto_created": false,
    "error": ""
  },
  "kafka": {
    "status": "failed",
    "url": "kafka:9092",
    "auto_created": false,
    "error": "Connection refused"
  }
}
```

### 6.2 查看完整状态

```bash
curl http://localhost:8000/api/v1/status
```

**响应示例**:
```json
{
  "running": true,
  "active_anomalies": 2,
  "baselines_loaded": 15,
  "last_baseline_update": "2026-02-25T10:30:00Z",
  "metrics_collector_connected": true,
  "logs_collector_connected": true,
  "infrastructure": {
    "prometheus": {"status": "connected", "...": "..."},
    "loki": {"status": "connected", "...": "..."},
    "...": "..."
  }
}
```

---

## 常见问题

### Q: 如何只使用 Prometheus，不使用其他服务？

只配置 Prometheus，其他服务会显示为 `not_configured`：

```bash
PROMETHEUS_URL=http://your-prometheus:9090
AUTO_CREATE_ENABLED=false
```

### Q: 如何切换从 Qdrant 到 Milvus？

```bash
# 禁用 Qdrant
# QDRANT_URL=

# 启用 Milvus
MILVUS_HOST=your-milvus
MILVUS_PORT=19530
```

或在配置文件中：
```yaml
vector_db:
  provider: milvus
  milvus_host: your-milvus
  milvus_port: 19530
```

### Q: 自动创建的服务数据存储在哪里？

数据存储在 Docker volumes 中：
- `prometheus-data`
- `loki-data`
- `qdrant-data`
- etc.

清除数据：
```bash
docker-compose down -v  # 删除所有 volumes
```

### Q: 如何使用 Mimir 替代 Prometheus？

```bash
MIMIR_URL=http://your-mimir:9009
# 不设置 PROMETHEUS_URL
```

或：
```yaml
prometheus:
  use_mimir: true
  mimir_url: http://your-mimir:9009
```

---

**文档结束**
