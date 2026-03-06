# 05 - 加密货币交易系统专项场景设计

## 一、交易系统特殊性分析

### 1.1 与传统 Web 应用的关键差异

| 维度 | 传统 Web 应用 | 加密货币交易系统 |
|------|---------------|-----------------|
| 运营时间 | 通常有低峰期 | 7×24h 无休市 |
| 延迟要求 | P99 < 500ms | 撮合 < 10ms, API < 50ms |
| 数据一致性 | 最终一致即可 | 资金强一致性，不容许差错 |
| 流量模式 | 相对平稳 | 行情驱动，可能瞬间 100 倍 |
| 故障影响 | 用户体验下降 | 直接经济损失 + 合规风险 |
| 回滚风险 | 通常安全 | 可能导致订单状态不一致 |
| 安全要求 | 标准安全 | 资金安全是生命线 |

### 1.2 关键服务依赖链

```
用户请求
    │
    ▼
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  ALB     │────▶│ Trading  │────▶│  Matching    │
│          │     │ API      │     │  Engine      │
└──────────┘     └────┬─────┘     └──────┬───────┘
                      │                   │
                 ┌────┴────┐        ┌────┴────┐
                 ▼         ▼        ▼         ▼
           ┌─────────┐ ┌────────┐ ┌───────┐ ┌─────────┐
           │ Redis   │ │ Kafka  │ │ RDS   │ │ Market  │
           │(Cache/  │ │(Event  │ │(Order │ │ Data    │
           │ Session)│ │ Bus)   │ │ Book) │ │ Feed    │
           └─────────┘ └────────┘ └───────┘ └─────────┘
                           │
                      ┌────┴────┐
                      ▼         ▼
                ┌─────────┐ ┌──────────┐
                │ Wallet  │ │Settlement│
                │ Service │ │ Service  │
                └─────────┘ └──────────┘
```

---

## 二、核心场景 Playbook

### 场景 1：行情剧变导致流量飙升

**触发条件**：
- API QPS 突增 > 基线 300%
- WebSocket 连接数快速攀升
- 撮合引擎队列深度上升

**检测指标**：
```yaml
detection:
  primary:
    - api_request_rate > baseline * 3
    - websocket_connections > baseline * 2
  secondary:
    - matching_engine_queue_depth > 10000
    - api_latency_p99 > 200ms
```

**分析维度**：
```
1. 是外部流量还是内部问题？
   → 检查 ALB 连接数 vs Pod CPU
   → 如果 ALB 流量增大但 CPU 正常 → 流量激增
   → 如果 ALB 流量正常但 CPU 飙高 → 内部问题

2. 是全局还是局部？
   → 检查所有交易对的 QPS 分布
   → 如果 BTC/USDT 单一交易对飙升 → 行情驱动
   → 如果全部交易对均上升 → 全局性事件

3. 当前容量是否足够？
   → HPA 状态、Node 可分配资源
   → 是否接近 HPA 上限
```

**自愈方案**：
```yaml
playbook: traffic-surge
risk: LOW-MEDIUM
steps:
  # 第一步：扩容（自动，低风险）
  - name: scale_up_trading_api
    action: patch_hpa_max
    params:
      deployment: trading-api
      new_max: "current_max * 2"
    risk: LOW
    auto_execute: true

  - name: scale_up_market_data
    action: patch_hpa_max
    params:
      deployment: market-data-ws
      new_max: "current_max * 2"
    risk: LOW
    auto_execute: true

  # 第二步：如果扩容后仍有压力，启用限流（需审批）
  - name: enable_rate_limiting
    condition: "latency_p99 still > 200ms after 3min"
    action: update_config
    params:
      service: trading-api
      config: rate_limit_enabled=true
      rate_limit: "1000 req/s per user"
    risk: MEDIUM
    requires_approval: true
    approval_message: |
      流量飙升且扩容未完全缓解，建议启用 per-user 限流。
      当前 QPS: {{current_qps}}, 延迟 P99: {{current_p99}}

  # 第三步：如果持续恶化，降级非核心功能（需审批）
  - name: degrade_non_critical
    condition: "latency_p99 still > 500ms after 5min"
    action: feature_flags
    params:
      disable:
        - market_history_api     # 关闭历史K线查询
        - leaderboard_api        # 关闭排行榜
        - notification_service   # 延迟通知推送
    risk: MEDIUM
    requires_approval: true
```

---

### 场景 2：撮合引擎延迟飙升

**触发条件**：
- matching_engine_latency_p99 > 10ms
- 或 matching_engine_latency_p99 持续上升趋势

**这是交易系统最敏感的场景**，直接影响用户交易体验和资金安全。

**检测与分析**：
```yaml
detection:
  primary:
    - matching_engine_latency_p99 > 10ms
    - matching_engine_latency_p99_trend: increasing

analysis:
  # 1. 是否与部署相关？
  check_recent_deploys:
    services: [matching-engine, order-service]
    time_window: 30m

  # 2. 是否资源瓶颈？
  check_resources:
    - matching_engine_cpu_usage
    - matching_engine_memory_usage
    - matching_engine_gc_pause_duration  # GC 暂停时间
    - matching_engine_thread_count

  # 3. 是否依赖问题？
  check_dependencies:
    - rds_query_latency
    - redis_command_latency
    - kafka_produce_latency

  # 4. 是否流量问题？
  check_traffic:
    - order_rate_per_second
    - order_book_depth_per_symbol
```

**自愈方案**：
```yaml
playbook: matching-engine-latency
risk: HIGH  # 撮合引擎操作风险高
steps:
  # 第一步：诊断（自动，只读）
  - name: collect_diagnostics
    action: collect_thread_dump_and_metrics
    auto_execute: true

  # 第二步：如果是 GC 问题
  - name: trigger_manual_gc
    condition: "gc_pause_duration > 100ms"
    action: api_call
    params:
      endpoint: "matching-engine:8080/admin/gc"
    risk: MEDIUM
    requires_approval: true  # 即使低风险，撮合引擎也需审批

  # 第三步：如果是部署导致
  - name: rollback_matching_engine
    condition: "recent_deploy detected and confidence > 0.7"
    action: kubectl_rollout_undo
    params:
      deployment: matching-engine
    risk: HIGH
    requires_approval: true
    approvers: ["oncall_sre", "matching_engine_owner"]

  # 第四步：如果持续恶化 - 紧急措施
  - name: emergency_notification
    condition: "matching_engine_latency_p99 > 100ms for 5min"
    action: send_alert
    params:
      severity: CRITICAL
      channels: [pagerduty, slack, phone]
      message: "撮合引擎延迟严重异常，可能需要紧急介入"
    auto_execute: true  # 通知类操作自动发送
```

---

### 场景 3：数据库连接池耗尽

**触发条件**：
- rds_connections > max_connections * 0.8
- 或 rds_connections 快速上升趋势
- 应用层出现 "too many connections" 错误日志

**检测与分析**：
```yaml
detection:
  primary:
    - rds_connections > max_connections * 0.8
  secondary:
    - log_pattern: "too many connections|connection refused|connection timeout"
    - api_error_rate increasing

analysis:
  # 定位连接泄漏
  steps:
    - query_per_service_connections  # 按服务拆分连接数
    - check_slow_queries             # 是否有长事务占用连接
    - check_connection_pool_config   # 连接池配置是否合理
    - correlate_with_deploys         # 是否部署导致泄漏
```

**自愈方案**：
```yaml
playbook: rds-connection-exhaustion
risk: MEDIUM-HIGH
steps:
  # 第一步：Kill 空闲连接（自动）
  - name: kill_idle_connections
    action: rds_query
    params:
      query: |
        SELECT id, time, info
        FROM information_schema.processlist
        WHERE command = 'Sleep' AND time > 300
      follow_up: "KILL {id}"
      max_kills: 50  # 安全限制
    risk: LOW
    auto_execute: true

  # 第二步：如果是连接泄漏 - 重启泄漏服务的 Pod
  - name: restart_leaking_pods
    condition: "identified_leaking_service is not None"
    action: rolling_restart
    params:
      deployment: "{{leaking_service}}"
      strategy: one_at_a_time  # 逐个重启
    risk: MEDIUM
    requires_approval: true

  # 第三步：临时调整连接限制（需 DBA 审批）
  - name: increase_max_connections
    condition: "connections still > 0.9 * max after step 1"
    action: rds_parameter_change
    params:
      parameter: max_connections
      new_value: "current * 1.5"
    risk: HIGH
    requires_approval: true
    approvers: ["oncall_sre", "dba"]
```

---

### 场景 4：Redis 内存告急 / Eviction

**触发条件**：
- redis_memory_usage > 85%
- redis_evicted_keys > 0

**自愈方案**：
```yaml
playbook: redis-memory-pressure
risk: LOW-MEDIUM
steps:
  # 第一步：分析大 Key 和过期 Key（自动）
  - name: analyze_redis_keys
    action: redis_analysis
    params:
      commands:
        - "INFO memory"
        - "DBSIZE"
        - "redis-cli --bigkeys --memkeys"  # 大 Key 分析
    auto_execute: true

  # 第二步：清理过期 Key（自动）
  - name: flush_expired_keys
    action: redis_command
    params:
      command: "redis-cli --scan --pattern 'cache:*' | xargs redis-cli UNLINK"
      description: "清理 cache 前缀的过期数据"
    risk: LOW
    auto_execute: true

  # 第三步：如果内存仍然高 - 扩容（需审批）
  - name: scale_redis_cluster
    condition: "redis_memory_usage still > 85% after cleanup"
    action: elasticache_modify
    params:
      action: modify_replication_group
      node_type: "upgrade_one_tier"  # 如 r6g.large → r6g.xlarge
    risk: HIGH
    requires_approval: true
    approvers: ["oncall_sre", "team_lead"]
    note: "ElastiCache 扩容会有短暂的 failover"
```

---

### 场景 5：Kafka 消费积压

**触发条件**：
- kafka_consumer_lag > 10000 且持续增长

**自愈方案**：
```yaml
playbook: kafka-consumer-lag
risk: LOW-MEDIUM
steps:
  # 第一步：诊断消费者状态
  - name: diagnose_consumers
    action: kafka_admin
    params:
      commands:
        - describe_consumer_group
        - check_consumer_health
        - check_partition_assignment
    auto_execute: true

  # 第二步：如果消费者健康但处理慢 - 扩容消费者
  - name: scale_consumer
    condition: "consumers_healthy and lag_increasing"
    action: kubectl_scale
    params:
      deployment: "{{consumer_deployment}}"
      replicas: "current * 2"
    risk: LOW
    auto_execute: true

  # 第三步：如果是消费者异常 - 重启消费者
  - name: restart_consumers
    condition: "consumer_has_errors"
    action: rolling_restart
    params:
      deployment: "{{consumer_deployment}}"
    risk: MEDIUM
    requires_approval: true
```

---

### 场景 6：Pod OOMKilled 频繁发生

**触发条件**：
- kube_pod_container_status_last_terminated_reason == "OOMKilled"
- pod_restart_count_1h > 3

**自愈方案**：
```yaml
playbook: pod-oom-killed
risk: MEDIUM
steps:
  # 第一步：收集内存 Profile（自动）
  - name: capture_heap_dump
    action: kubectl_exec
    params:
      command: "jmap -dump:format=b,file=/tmp/heap.hprof 1"
      description: "Java 应用抓取堆转储"
    auto_execute: true
    on_fail: skip  # 如果 Pod 已经被 Kill 则跳过

  # 第二步：临时增大内存 Limits
  - name: increase_memory_limit
    action: kubectl_patch
    params:
      resource: deployment/{{deployment}}
      patch: |
        spec.template.spec.containers[0].resources.limits.memory: "{{current_limit * 1.5}}"
    risk: MEDIUM
    requires_approval: true

  # 第三步：创建跟进工单
  - name: create_followup_ticket
    action: create_ticket
    params:
      title: "{{service}} OOMKilled - 需要排查内存泄漏"
      priority: HIGH
      description: |
        Pod 频繁 OOMKilled，已临时增大内存限制。
        需要开发团队排查是否存在内存泄漏。
        堆转储已保存: {{heap_dump_path}}
    auto_execute: true
```

---

### 场景 7：证书/密钥即将过期

**触发条件**（预防性检查）：
- TLS 证书到期时间 < 30 天
- AWS IAM 密钥最后轮换 > 90 天

**方案**：
```yaml
playbook: certificate-expiry-warning
risk: LOW
trigger: daily_check  # 每日检查

steps:
  - name: check_tls_certificates
    action: check_certificates
    params:
      sources:
        - kubernetes_secrets  # K8s TLS secrets
        - alb_certificates    # ALB 上绑定的 ACM 证书
        - external_domains    # 交易所域名证书
      warning_threshold: 30d
      critical_threshold: 7d

  - name: create_renewal_ticket
    condition: "expiring_certs found"
    action: create_ticket
    params:
      title: "证书即将到期: {{cert_name}} ({{days_remaining}} 天)"
      priority: "{{HIGH if days < 7 else MEDIUM}}"
      assignee: "infra-team"
```

---

## 三、交易系统安全红线

### 3.1 绝对禁止自动执行的操作

```yaml
absolute_blacklist:
  description: "以下操作无论风险评分如何，SRE Agent 绝不自动执行"

  operations:
    # 资金操作
    - category: wallet_operations
      examples:
        - "修改钱包余额"
        - "触发提币/充币"
        - "热钱包 → 冷钱包转移"
        - "修改交易手续费"

    # 撮合引擎核心
    - category: matching_engine_core
      examples:
        - "修改撮合算法参数"
        - "暂停/恢复交易对"
        - "修改订单簿"

    # 数据库写操作
    - category: database_writes
      examples:
        - "修改用户余额表"
        - "修改订单状态"
        - "删除任何生产数据"
        - "RDS Failover"

    # 全局性操作
    - category: global_operations
      examples:
        - "全站停服"
        - "DNS 切换"
        - "跨区域 Failover"

  agent_can_do:
    description: "对于以上场景，Agent 可以做的是："
    actions:
      - "生成详细诊断报告"
      - "创建事件工单"
      - "通知对应负责人"
      - "提供修复建议（但不执行）"
      - "收集相关日志和指标"
```

### 3.2 交易系统断路器

```yaml
circuit_breakers:
  description: "当以下条件触发时，SRE Agent 自动暂停所有自愈操作"

  global_circuit_breaker:
    conditions:
      # 多服务同时异常 - 可能是基础设施问题
      - "count(active_anomalies where severity >= HIGH) > 5"

      # 自愈操作连续失败
      - "consecutive_remediation_failures >= 3"

      # 数据采集中断（Agent 可能判断不准）
      - "data_collection_failure_rate > 0.5"

    action:
      - "暂停所有自动执行操作"
      - "切换为纯诊断模式"
      - "立即通知 On-call SRE + Team Lead"
      - "继续采集数据和生成诊断报告"

  per_service_circuit_breaker:
    conditions:
      # 同一服务 1 小时内操作 3 次未恢复
      - "remediation_attempts(service, 1h) >= 3 and not recovered"

    action:
      - "停止该服务的自愈操作"
      - "升级工单优先级"
      - "通知服务 Owner"
```

---

## 四、On-Call 与升级策略

### 4.1 告警升级链路

```
┌──────────────────────────────────────────────────────────────────┐
│                       告警升级路径                                 │
│                                                                    │
│  Level 1: SRE Agent 自愈 (0-5 min)                               │
│  ├── 自动检测异常                                                  │
│  ├── 执行自愈操作                                                  │
│  └── 如果成功 → 记录 & 通知 → 结束                                │
│                                                                    │
│  Level 2: On-Call SRE (5-15 min)                                 │
│  ├── Agent 发送审批请求 / 告警通知                                 │
│  ├── SRE 审批执行 or 手动处理                                     │
│  └── 如果 15 分钟未响应 → 升级                                    │
│                                                                    │
│  Level 3: Team Lead / Senior SRE (15-30 min)                     │
│  ├── 二次通知 (电话 + Slack + PagerDuty)                          │
│  ├── 协调多团队响应                                                │
│  └── 如果 30 分钟未解决 → 升级                                    │
│                                                                    │
│  Level 4: Engineering Director + CTO (30+ min)                   │
│  ├── 紧急决策（如：全站停服、交易暂停）                             │
│  ├── 启动战争室 (War Room)                                        │
│  └── 对外公告（状态页更新）                                        │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 On-Call 排班集成

```yaml
oncall_integration:
  # PagerDuty 集成
  pagerduty:
    api_key: "${PAGERDUTY_API_KEY}"
    schedules:
      - name: sre-primary
        escalation_policy: "sre-trading"
      - name: sre-secondary
        escalation_policy: "sre-trading-backup"

  # 或者自定义排班
  custom_schedule:
    source: "google_calendar"  # 或从配置文件读取
    calendar_id: "sre-oncall@company.com"

  # Agent 获取当前 On-Call
  get_oncall:
    primary: pagerduty.get_oncall("sre-primary")
    secondary: pagerduty.get_oncall("sre-secondary")
```

---

## 五、事后复盘自动化

### 5.1 事件时间线自动生成

每次事件处理完成后，Agent 自动生成时间线报告：

```markdown
## 事件报告: INC-20260209-001

### 概况
- **服务**: trading-api
- **严重度**: HIGH
- **持续时间**: 23 分钟 (14:15 - 14:38 UTC)
- **影响**: API P99 延迟从 50ms 上升到 350ms，影响约 3000 活跃用户

### 时间线
| 时间 (UTC) | 事件 |
|------------|------|
| 14:00 | CI/CD 部署 trading-api v2.3.1 |
| 14:15 | SRE Agent 检测到 API latency P99 异常 (偏离基线 +400%) |
| 14:16 | 趋势预测: 延迟将在 30 分钟内达到 500ms |
| 14:16 | 根因分析: 部署 v2.3.1 后异常开始 (置信度 85%) |
| 14:17 | 风险评估: MEDIUM (0.55), 建议回滚 |
| 14:17 | 审批请求发送至 On-Call SRE @john |
| 14:19 | @john 批准回滚操作 |
| 14:20 | 开始执行回滚: v2.3.1 → v2.3.0 |
| 14:25 | 回滚完成，所有 Pod Ready |
| 14:30 | 验证: 延迟恢复至基线范围 |
| 14:38 | 确认恢复，关闭事件 |

### 根因
部署 v2.3.1 引入的 Redis 连接池配置变更导致连接频繁创建/销毁，增加了 API 响应延迟。

### 修复措施
- 回滚至 v2.3.0
- 创建跟进工单: 修复 v2.3.1 中的 Redis 连接池配置

### 指标
- MTTD (检测时间): 15 分钟
- MTTI (调查时间): 1 分钟 (Agent 自动分析)
- MTTR (恢复时间): 23 分钟
- 人工介入时间: 2 分钟 (审批)
```

### 5.2 知识库自动更新

事件关闭后自动将经验写入 RAG 知识库：

```python
def auto_update_knowledge_base(incident):
    """事件处理完毕后自动更新知识库"""

    knowledge_entry = {
        "incident_id": incident.id,
        "timestamp": incident.created_at,
        "service": incident.service,
        "severity": incident.severity,

        # 用于向量化检索的文本
        "searchable_text": f"""
            服务 {incident.service} 出现 {incident.anomaly_description}。
            根因是 {incident.root_cause}。
            通过 {incident.resolution_steps} 解决。
            关键指标: {incident.key_metrics}。
        """,

        # 结构化数据
        "root_cause": incident.root_cause,
        "resolution_steps": incident.resolution_steps,
        "resolution_duration": incident.duration,
        "playbook_used": incident.playbook_name,
        "was_auto_remediated": incident.auto_remediated,
        "success": incident.resolved_successfully,
    }

    # 向量化并写入 Qdrant
    embedding = embed(knowledge_entry["searchable_text"])
    qdrant_client.upsert(
        collection="sre_knowledge",
        points=[{
            "id": incident.id,
            "vector": embedding,
            "payload": knowledge_entry,
        }]
    )
```
