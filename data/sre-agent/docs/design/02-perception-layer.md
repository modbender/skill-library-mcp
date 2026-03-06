# 02 - 感知层（Perception Layer）设计

## 一、设计目标

感知层是 SRE Agent 的"眼睛和耳朵"，负责从现有可观测性基础设施中采集数据。
核心原则：**不重复采集，只做数据读取和标准化**。

---

## 二、数据源与采集器

### 2.1 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        感知层 (Perception Layer)                  │
│                                                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │ Metrics       │  │ Logs          │  │ Events            │   │
│  │ Collector     │  │ Collector     │  │ Collector         │   │
│  │               │  │               │  │                   │   │
│  │ • Prometheus  │  │ • Loki API    │  │ • K8s Events API  │   │
│  │   /Mimir API  │  │ • LogQL       │  │ • Kafka Consumer  │   │
│  │ • PromQL      │  │ • 错误日志    │  │ • 部署事件        │   │
│  │ • 核心指标    │  │ • 审计日志    │  │ • 配置变更事件    │   │
│  └───────┬───────┘  └───────┬───────┘  └─────────┬─────────┘   │
│          │                  │                     │              │
│  ┌───────────────┐  ┌──────────────────────────────────────┐   │
│  │ AWS           │  │ DataNormalizer (数据标准化)            │   │
│  │ Collector     │  │ • 统一时间戳格式                       │   │
│  │               │  │ • 统一标签体系                         │   │
│  │ • CloudWatch  │  │ • 数据质量校验                         │   │
│  │ • EC2 API     │  │ • 关联标记 (service, env, cluster)    │   │
│  │ • RDS API     │  └──────────────────────────────────────┘   │
│  │ • ELB API     │                                              │
│  └───────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、MetricsCollector - 指标采集器

### 3.1 数据源

- **主数据源**：Prometheus HTTP API（短期查询，< 2h）
- **长期数据源**：Mimir Query API（基线学习，7-30d 历史查询）
- **备选数据源**：n9e API（读取已配置的告警规则和当前告警状态）

> Mimir 提供 Prometheus 兼容的 Query API，查询接口相同，仅 URL 不同。

### 3.2 核心指标体系

针对加密货币交易系统，定义以下分层指标：

#### 3.2.1 交易业务指标（Trading Metrics）

```yaml
trading_metrics:
  # 撮合引擎
  matching_engine:
    - name: matching_engine_orders_per_second
      promql: 'rate(matching_engine_orders_total[1m])'
      description: 撮合引擎每秒处理订单数
      baseline_type: time_of_day  # 按交易时段有不同基线

    - name: matching_engine_latency_p99
      promql: 'histogram_quantile(0.99, rate(matching_engine_duration_seconds_bucket[5m]))'
      description: 撮合延迟 P99
      threshold_critical: 0.01  # 10ms
      threshold_warning: 0.005  # 5ms

    - name: order_book_depth
      promql: 'order_book_depth_total{side="bid"} + order_book_depth_total{side="ask"}'
      description: 订单簿深度

  # API 网关
  api_gateway:
    - name: api_request_rate
      promql: 'sum(rate(http_requests_total{service="trading-api"}[1m]))'
      description: API 总请求率

    - name: api_error_rate
      promql: 'sum(rate(http_requests_total{service="trading-api",code=~"5.."}[5m])) / sum(rate(http_requests_total{service="trading-api"}[5m]))'
      description: API 5xx 错误率
      threshold_critical: 0.05  # 5%
      threshold_warning: 0.01   # 1%

    - name: api_latency_p95
      promql: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service="trading-api"}[5m]))'
      description: API 延迟 P95

  # 钱包服务
  wallet:
    - name: wallet_transaction_queue_depth
      promql: 'wallet_pending_transactions_total'
      description: 待处理交易队列深度

    - name: wallet_hot_balance
      promql: 'wallet_balance{type="hot"}'
      description: 热钱包余额（仅监控，不自动操作）

  # WebSocket 行情推送
  market_data:
    - name: websocket_active_connections
      promql: 'websocket_connections_active'
      description: WebSocket 活跃连接数

    - name: market_data_feed_latency
      promql: 'market_data_publish_latency_seconds'
      description: 行情推送延迟
```

#### 3.2.2 基础设施指标（Infrastructure Metrics）

```yaml
infrastructure_metrics:
  # EKS / K8s
  kubernetes:
    - name: pod_cpu_usage
      promql: 'sum(rate(container_cpu_usage_seconds_total{namespace=~"trading|matching|wallet"}[5m])) by (pod)'
      description: Pod CPU 使用率

    - name: pod_memory_usage_percent
      promql: 'sum(container_memory_working_set_bytes{namespace=~"trading|matching|wallet"}) by (pod) / sum(kube_pod_container_resource_limits{resource="memory"}) by (pod)'
      description: Pod 内存使用率

    - name: pod_restart_count
      promql: 'increase(kube_pod_container_status_restarts_total[1h])'
      description: Pod 1小时内重启次数
      threshold_warning: 3

    - name: pod_oom_killed
      promql: 'kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}'
      description: OOMKilled 事件

    - name: hpa_current_vs_desired
      promql: 'kube_horizontalpodautoscaler_status_current_replicas / kube_horizontalpodautoscaler_spec_max_replicas'
      description: HPA 当前副本数占比（接近 100% 说明需要扩容上限）

  # Node 级别
  node:
    - name: node_cpu_usage
      promql: '1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)'

    - name: node_memory_usage
      promql: '1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)'

    - name: node_disk_usage
      promql: '1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})'
      threshold_critical: 0.9
      threshold_warning: 0.8
```

#### 3.2.3 中间件指标（Middleware Metrics）

```yaml
middleware_metrics:
  # RDS (MySQL)
  rds:
    - name: rds_cpu_utilization
      source: cloudwatch  # 通过 AWS CloudWatch 采集
      metric: CPUUtilization
      dimensions: {DBInstanceIdentifier: "trading-db"}
      threshold_critical: 90
      threshold_warning: 75

    - name: rds_connections
      promql: 'mysql_global_status_threads_connected'
      description: 当前连接数

    - name: rds_slow_queries
      promql: 'rate(mysql_global_status_slow_queries[5m])'
      description: 慢查询速率

    - name: rds_replication_lag
      source: cloudwatch
      metric: ReplicaLag
      threshold_critical: 10  # 10 秒
      threshold_warning: 5

  # ElastiCache (Redis)
  redis:
    - name: redis_memory_usage
      promql: 'redis_memory_used_bytes / redis_memory_max_bytes'
      threshold_critical: 0.9
      threshold_warning: 0.75

    - name: redis_connected_clients
      promql: 'redis_connected_clients'

    - name: redis_evicted_keys
      promql: 'rate(redis_evicted_keys_total[5m])'
      threshold_warning: 0  # 任何 eviction 都告警

    - name: redis_hit_rate
      promql: 'redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)'
      threshold_warning: 0.9  # 命中率低于 90% 告警

    - name: redis_command_latency_p99
      promql: 'histogram_quantile(0.99, rate(redis_command_duration_seconds_bucket[5m]))'

  # Kafka
  kafka:
    - name: kafka_consumer_lag
      promql: 'kafka_consumergroup_lag_sum'
      description: 消费者组积压量
      threshold_critical: 100000
      threshold_warning: 10000

    - name: kafka_partition_under_replicated
      promql: 'kafka_server_replicamanager_underreplicatedpartitions'
      threshold_warning: 0  # 任何 under-replicated 都告警

    - name: kafka_broker_message_rate
      promql: 'sum(rate(kafka_server_brokertopicmetrics_messagesin_total[5m])) by (topic)'

  # ALB (Application Load Balancer)
  alb:
    - name: alb_5xx_count
      source: cloudwatch
      metric: HTTPCode_ELB_5XX_Count
      threshold_warning: 10  # per minute

    - name: alb_target_response_time
      source: cloudwatch
      metric: TargetResponseTime
      statistic: p99
      threshold_warning: 1.0  # 1 秒

    - name: alb_healthy_host_count
      source: cloudwatch
      metric: HealthyHostCount
```

### 3.3 采集策略

```yaml
collection_strategy:
  # 实时监控指标 - 每分钟采集
  realtime:
    interval: 60s
    metrics:
      - trading_metrics.*
      - kubernetes.pod_restart_count
      - kubernetes.pod_oom_killed
      - redis.redis_evicted_keys
      - kafka.kafka_consumer_lag
    query_range: 5m  # 查询最近 5 分钟数据

  # 常规指标 - 每 5 分钟采集
  regular:
    interval: 300s
    metrics:
      - infrastructure_metrics.*
      - middleware_metrics.*
    query_range: 15m

  # 基线查询 - 按需 (异常检测和趋势预测时)
  on_demand:
    source: mimir  # 长期查询走 Mimir
    lookback: 7d   # 默认查看 7 天历史
    step: 1m       # 数据点粒度
```

---

## 四、LogsCollector - 日志采集器

### 4.1 数据源

- **Loki API**：通过 LogQL 查询结构化日志
- **采集模式**：Agent 不直接采集日志，而是按需查询 Loki

### 4.2 查询策略

```yaml
log_queries:
  # 错误日志 - 每分钟查询
  error_logs:
    interval: 60s
    query: '{namespace=~"trading|matching|wallet"} |= "ERROR" | json | line_format "{{.message}}"'
    limit: 100

  # 关键业务日志 - 每分钟查询
  critical_business:
    interval: 60s
    queries:
      - '{service="matching-engine"} |= "order_failed"'
      - '{service="wallet-service"} |= "transaction_failed"'
      - '{service="trading-api"} |= "circuit_breaker"'

  # 异常时深度查询 - 按需 (检测到异常后触发)
  deep_investigation:
    trigger: on_anomaly
    time_window: "-15m to +5m"  # 异常时间前后的日志
    queries:
      - '{namespace="{{affected_namespace}}"} | json'  # 全量日志
      - '{namespace="{{affected_namespace}}"} |= "panic" or |= "fatal"'
      - '{namespace="{{affected_namespace}}"} | json | level="WARN" or level="ERROR"'
```

### 4.3 日志标准化

```python
# 标准化后的日志格式
StandardizedLog = {
    "timestamp": "2026-02-09T14:30:00.000Z",
    "level": "ERROR",
    "service": "trading-api",
    "namespace": "trading",
    "pod": "trading-api-7d8f9b6c5-x2kl4",
    "message": "Failed to process order: timeout connecting to matching engine",
    "labels": {
        "trace_id": "abc123",
        "order_id": "ORD-20260209-001",
        "error_type": "ConnectionTimeout"
    },
    "raw": "... 原始日志内容 ..."
}
```

---

## 五、EventsCollector - 事件采集器

### 5.1 Kubernetes Events

```yaml
k8s_events:
  watch_namespaces:
    - trading
    - matching
    - wallet
    - infra
    - sre-agent

  watch_event_types:
    - Warning           # 所有 Warning 事件
    - type: Normal
      reasons:          # 只关注特定 Normal 事件
        - Killing
        - Pulled
        - Scheduled
        - ScalingReplicaSet
        - SuccessfulRescale  # HPA 扩缩容

  # 关注的关键事件
  critical_events:
    - reason: OOMKilling
      severity: HIGH
    - reason: BackOff        # CrashLoopBackOff
      severity: HIGH
    - reason: FailedScheduling
      severity: MEDIUM
    - reason: Unhealthy      # Probe 失败
      severity: MEDIUM
    - reason: EvictionThresholdMet
      severity: HIGH
```

### 5.2 Kafka 事件流

```yaml
kafka_events:
  topics:
    # 部署事件 (由 CI/CD 发布)
    - topic: deploy-events
      format: json
      schema:
        service: string
        version: string
        environment: string
        deployer: string
        timestamp: datetime
        change_type: enum(deploy, rollback, config_change, scale)
        details: object

    # 交易异常事件 (由交易系统发布)
    - topic: trading-alerts
      format: json
      schema:
        alert_type: enum(order_timeout, balance_mismatch, feed_stale, circuit_break)
        service: string
        details: object
        timestamp: datetime

    # 配置变更事件
    - topic: config-changes
      format: json
```

### 5.3 变更事件关联

变更追踪是根因分析的关键输入。Agent 维护一个**变更时间线**：

```
变更时间线 (Change Timeline):
  ┌───────────────────────────────────────────────┐
  │ T-30min  | Deploy trading-api v2.3.1          │
  │ T-25min  | ConfigMap update: redis pool size  │
  │ T-20min  | HPA scale-up: matching-engine 3→5  │
  │ T-15min  | [异常开始] API latency spike        │ ← 关联点
  │ T-10min  | Error logs: "connection refused"   │
  │ T-5min   | Pod restart: trading-api-xxx       │
  └───────────────────────────────────────────────┘

  根因分析引擎会自动关联: 异常发生前 30 分钟内的所有变更事件
```

---

## 六、AWSCollector - AWS 资源采集器

### 6.1 CloudWatch 指标

```yaml
aws_cloudwatch:
  # 通过 boto3 SDK 采集 CloudWatch 指标
  polling_interval: 300s  # 5 分钟 (CloudWatch 最小粒度 1min，但避免 API 限流)

  metrics:
    # RDS
    - namespace: AWS/RDS
      metrics:
        - CPUUtilization
        - FreeableMemory
        - ReadIOPS
        - WriteIOPS
        - DatabaseConnections
        - ReplicaLag
        - FreeStorageSpace
      dimensions:
        DBInstanceIdentifier:
          - trading-db-primary
          - trading-db-replica

    # ElastiCache
    - namespace: AWS/ElastiCache
      metrics:
        - CPUUtilization
        - EngineCPUUtilization
        - CurrConnections
        - Evictions
        - CacheHitRate
        - ReplicationLag
      dimensions:
        CacheClusterId:
          - trading-redis-001
          - trading-redis-002

    # ALB
    - namespace: AWS/ApplicationELB
      metrics:
        - RequestCount
        - TargetResponseTime
        - HTTPCode_ELB_5XX_Count
        - HTTPCode_Target_5XX_Count
        - HealthyHostCount
        - UnHealthyHostCount
      dimensions:
        LoadBalancer:
          - app/trading-alb/xxxxxxxxxx

    # EKS (通过 Container Insights)
    - namespace: ContainerInsights
      metrics:
        - node_cpu_utilization
        - node_memory_utilization
        - pod_cpu_utilization
        - pod_memory_utilization
```

### 6.2 AWS 资源状态检查

```yaml
aws_resource_checks:
  interval: 300s

  checks:
    # EC2 实例状态
    - type: ec2_status
      action: describe_instance_status
      alert_on:
        - status != "ok"

    # RDS 事件
    - type: rds_events
      action: describe_events
      event_categories:
        - failover
        - failure
        - maintenance

    # EKS 集群状态
    - type: eks_cluster
      action: describe_cluster
      alert_on:
        - status != "ACTIVE"

    # EKS Node Group
    - type: eks_nodegroup
      action: describe_nodegroup
      alert_on:
        - status != "ACTIVE"
        - desiredSize > currentSize  # 扩容卡住
```

---

## 七、DataNormalizer - 数据标准化

### 7.1 统一数据模型

所有采集器的输出都经过标准化，转换为统一的内部数据模型：

```python
@dataclass
class MetricDataPoint:
    """标准化的指标数据点"""
    metric_name: str           # 标准指标名称
    value: float               # 当前值
    timestamp: datetime        # UTC 时间戳
    labels: Dict[str, str]     # 标签 (service, namespace, instance, etc.)
    source: str                # 数据来源 (prometheus, cloudwatch, etc.)
    unit: str                  # 单位 (percent, bytes, seconds, count, etc.)

@dataclass
class LogEntry:
    """标准化的日志条目"""
    timestamp: datetime
    level: str                 # ERROR, WARN, INFO
    service: str
    namespace: str
    pod: str
    message: str
    labels: Dict[str, str]
    raw: str

@dataclass
class Event:
    """标准化的事件"""
    timestamp: datetime
    event_type: str            # deploy, config_change, k8s_event, alert, etc.
    source: str                # kubernetes, kafka, cloudwatch, etc.
    severity: str              # CRITICAL, HIGH, MEDIUM, LOW, INFO
    service: str
    details: Dict[str, Any]
    related_metrics: List[str] # 关联的指标名称
```

### 7.2 标签标准化

确保来自不同数据源的数据可以通过统一标签关联：

```yaml
label_mapping:
  # 服务名统一
  service_name:
    prometheus_label: service
    loki_label: service_name
    k8s_label: app.kubernetes.io/name
    cloudwatch_dimension: ServiceName
    standard: service  # 统一为 service

  # 环境统一
  environment:
    prometheus_label: env
    loki_label: environment
    k8s_label: app.kubernetes.io/env
    standard: env  # 统一为 env

  # 命名空间
  namespace:
    prometheus_label: namespace
    loki_label: namespace
    k8s: metadata.namespace
    standard: namespace
```

---

## 八、采集器健康监控

Agent 自身需要监控数据采集的健康状态：

```yaml
self_monitoring:
  metrics:
    # 采集成功率
    - sre_agent_collection_success_total{collector, target}
    - sre_agent_collection_errors_total{collector, target, error_type}

    # 采集延迟
    - sre_agent_collection_duration_seconds{collector}

    # 数据新鲜度
    - sre_agent_last_successful_collection_timestamp{collector}

  alerts:
    # 数据源不可达
    - name: collector_unreachable
      condition: 'sre_agent_collection_errors_total{error_type="connection_refused"} > 3'
      action: 降级运行，使用缓存数据，告警通知

    # 数据过期
    - name: stale_data
      condition: 'time() - sre_agent_last_successful_collection_timestamp > 300'
      action: 标记数据不可信，异常检测结果加 confidence penalty
```
