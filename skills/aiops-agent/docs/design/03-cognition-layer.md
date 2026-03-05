# 03 - 认知层（Cognition Layer）设计

## 一、设计目标

认知层是 SRE Agent 的"大脑"，负责将原始数据转化为可操作的洞察。核心能力包括：

1. **基线学习**：理解"什么是正常"
2. **异常检测**：发现"什么在偏离正常"
3. **趋势预测**：预判"未来会怎样"
4. **根因分析**：定位"为什么异常"
5. **知识检索**：检索"历史上类似问题怎么处理的"

---

## 二、组件交互关系

```
                    ┌──────────────────┐
  历史数据 ────────▶│  BaselineEngine   │
  (Mimir 7-30d)     │  基线学习引擎     │
                    └────────┬─────────┘
                             │ 基线模型
                             ▼
  实时数据 ────────▶┌──────────────────┐
  (Prometheus 5m)   │  AnomalyDetector  │──── 异常事件 ────┐
                    │  异常检测引擎     │                    │
                    └──────────────────┘                    │
                                                            ▼
                    ┌──────────────────┐          ┌──────────────────┐
  时序数据 ────────▶│  TrendPredictor   │────────▶│                  │
  (Mimir 24h)       │  趋势预测引擎     │ 预测结果  │   Anomaly        │
                    └──────────────────┘          │   Context        │
                                                  │   (异常上下文)    │
  日志 + 事件 ─────▶┌──────────────────┐          │                  │
  变更记录          │  RCAEngine        │◀─────────│                  │
                    │  根因分析引擎     │          └──────────────────┘
                    └────────┬─────────┘
                             │ 根因假设
                             ▼
                    ┌──────────────────┐
  向量知识库 ◀──────│  RAGKnowledgeBase │──── 相似案例 + 修复建议
                    │  RAG 知识库      │
                    └──────────────────┘
                             │
                             ▼
                        输出到决策层
```

---

## 三、BaselineEngine - 基线学习引擎

### 3.1 设计思路

基线 = "这个时间点，这个指标，正常范围应该是多少"。

交易系统的基线有明显的**时间模式**：
- 亚洲交易时段（UTC 0:00-8:00）vs 欧美时段（UTC 13:00-21:00）
- 周末 vs 工作日（加密货币市场不休市，但流量模式不同）
- 重大事件（如 BTC 减半、美联储议息）会打破基线

### 3.2 基线学习算法

#### 方案 A：STL 时序分解（推荐首选，简单有效）

```
原始时序 = 趋势分量(Trend) + 季节性分量(Seasonal) + 残差(Residual)

步骤：
1. 从 Mimir 查询 14-30 天历史数据
2. STL 分解，提取周期性模式（日周期 + 周周期）
3. 计算残差的均值和标准差
4. 基线值 = Trend + Seasonal
5. 正常范围 = 基线值 ± k × std(Residual)  (k=2 或 3)
```

**适用场景**：QPS、延迟、CPU、内存等有明显周期性的指标

#### 方案 B：滑动窗口分位数

```
步骤：
1. 按"星期几 + 小时"分桶 (7×24=168 个桶)
2. 每个桶内计算 P5, P50 (中位数), P95
3. 正常范围 = [P5, P95]
4. 基线值 = P50

优点：对异常值鲁棒，计算简单
缺点：需要较多历史数据（建议 >= 4 周）
```

**适用场景**：波动较大的指标（如 Kafka lag、WebSocket 连接数）

#### 方案 C：LSTM 时序预测（进阶，Phase 3 实现）

```
步骤：
1. 训练 LSTM 模型预测 "下一个时间点的期望值"
2. 基线值 = 模型预测值
3. 正常范围 = 预测值 ± 预测区间

优点：能捕获复杂的非线性模式
缺点：训练成本高，需要 GPU，需要更多数据
```

**适用场景**：复杂关联指标（如撮合引擎吞吐与市场波动率的关系）

### 3.3 基线更新策略

```yaml
baseline_update:
  # 增量更新：每天 UTC 03:00（亚洲早盘前低峰）
  incremental:
    schedule: "0 3 * * *"
    lookback: 1d       # 新增 1 天数据
    method: exponential_moving  # 指数加权，近期数据权重更高
    anomaly_filter: true        # 剔除已标记的异常时段数据

  # 全量重训练：每周日 UTC 04:00
  full_retrain:
    schedule: "0 4 * * 0"
    lookback: 30d
    method: stl_decompose
    anomaly_filter: true

  # 冷启动：首次部署或新增指标
  cold_start:
    minimum_data: 7d    # 至少需要 7 天数据
    fallback: static_threshold  # 数据不足时使用静态阈值
```

### 3.4 基线输出格式

```python
@dataclass
class Baseline:
    metric_name: str
    time_key: str          # 如 "monday_14:00" 或 "weekday_14:00"
    expected_value: float
    lower_bound: float     # 正常下界
    upper_bound: float     # 正常上界
    std_deviation: float   # 残差标准差
    confidence: float      # 基线置信度 (0-1, 数据越多越高)
    growth_rate: float     # 该时段的正常增长率 (per hour)
    last_updated: datetime
    data_points_count: int # 训练使用的数据点数
```

---

## 四、AnomalyDetector - 异常检测引擎

### 4.1 检测策略：多算法集成

不依赖单一算法，而是**多算法投票 + 加权融合**：

```
┌──────────────────────────────────────────────────┐
│          AnomalyDetector 多算法集成                │
│                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ Statistical  │  │ ML-Based    │  │ Baseline  │ │
│  │ Detectors   │  │ Detectors   │  │ Deviation │ │
│  │             │  │             │  │           │ │
│  │ • Z-Score   │  │ • Isolation │  │ • 基线偏离│ │
│  │ • MAD       │  │   Forest    │  │   检测    │ │
│  │ • IQR       │  │ • One-Class │  │ • 增长率  │ │
│  │             │  │   SVM       │  │   突变    │ │
│  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘ │
│         │                │               │        │
│         └────────────────┼───────────────┘        │
│                          ▼                         │
│              ┌─────────────────────┐              │
│              │  Ensemble Scorer    │              │
│              │  加权融合评分        │              │
│              │                     │              │
│              │  score = Σ(wi × si) │              │
│              └──────────┬──────────┘              │
│                         ▼                          │
│              ┌─────────────────────┐              │
│              │  Anomaly Filter     │              │
│              │  降噪 & 去重        │              │
│              │  • 持续时间过滤     │              │
│              │  • 重复抑制         │              │
│              │  • 已知问题过滤     │              │
│              └─────────────────────┘              │
└──────────────────────────────────────────────────┘
```

### 4.2 检测算法详解

#### 4.2.1 Z-Score / 基线偏离检测（首选，Phase 1 实现）

```python
"""最基础但最实用的异常检测"""

def detect_baseline_deviation(current_value, baseline):
    z_score = (current_value - baseline.expected_value) / baseline.std_deviation

    if abs(z_score) > 3.0:
        severity = "CRITICAL"
    elif abs(z_score) > 2.5:
        severity = "HIGH"
    elif abs(z_score) > 2.0:
        severity = "MEDIUM"
    else:
        return None  # 正常

    return Anomaly(
        severity=severity,
        deviation_percent=(current_value - baseline.expected_value) / baseline.expected_value,
        z_score=z_score,
    )

# 适用：有良好基线的指标 (CPU, Memory, QPS, Latency)
# 优点：简单、可解释、计算快
# 缺点：假设正态分布，对尖峰指标不友好
```

#### 4.2.2 MAD (Median Absolute Deviation)

```python
"""对异常值更鲁棒的检测方法"""

def detect_mad(values, current_value, threshold=3.5):
    median = np.median(values)
    mad = np.median(np.abs(values - median))
    modified_z_score = 0.6745 * (current_value - median) / mad

    if abs(modified_z_score) > threshold:
        return Anomaly(...)
    return None

# 适用：存在偏斜分布的指标 (Kafka lag, 请求队列深度)
# 优点：对极端值鲁棒
# 缺点：计算需要历史窗口数据
```

#### 4.2.3 Isolation Forest（Phase 2 实现）

```python
"""无监督多维异常检测"""

# 训练：使用近 7 天正常数据
features = [cpu, memory, qps, latency, error_rate, connections]
model = IsolationForest(contamination=0.05, n_estimators=100)
model.fit(normal_data)

# 检测：对当前多维特征向量打分
score = model.decision_function(current_features)
is_anomaly = model.predict(current_features) == -1

# 适用：多指标联动异常（如 CPU 和 QPS 同时异常但单个看都正常）
# 优点：能发现多维度关联异常
# 缺点：不可解释，需要定期重训练
```

### 4.3 异常评分机制

```python
def compute_anomaly_score(anomaly, context):
    """多维度加权评分"""
    score = (
        0.35 * deviation_score(anomaly)    +  # 偏离基线的程度
        0.25 * duration_score(anomaly)     +  # 异常持续时间
        0.20 * trend_score(anomaly)        +  # 趋势是否在恶化
        0.10 * correlation_score(anomaly)  +  # 是否有关联异常
        0.10 * business_impact(anomaly)       # 业务影响 (交易相关指标加权)
    )
    return score

# 评分区间:
#   score > 0.8  → CRITICAL
#   score > 0.6  → HIGH
#   score > 0.4  → MEDIUM
#   score <= 0.4 → LOW
```

### 4.4 异常降噪

```yaml
noise_reduction:
  # 持续时间过滤：异常必须持续 N 个检测周期才触发
  min_duration:
    CRITICAL: 1m    # 1 个周期就触发
    HIGH: 2m        # 持续 2 分钟
    MEDIUM: 5m      # 持续 5 分钟
    LOW: 10m        # 持续 10 分钟

  # 重复抑制：同一指标同一 Pod 的异常在恢复前不重复触发
  dedup:
    window: 30m
    key: "{metric_name}:{service}:{pod}"

  # 维护窗口：预定义的维护时段内降级告警
  maintenance_windows:
    - name: weekly_deploy
      cron: "0 10 * * 2"  # 每周二 10:00
      duration: 2h
      action: suppress_medium_and_low

  # 已知问题抑制：对已创建工单的异常不重复告警
  known_issues:
    check_ticket_system: true
    suppress_if_open_ticket: true
```

### 4.5 异常输出格式

```python
@dataclass
class Anomaly:
    anomaly_id: str               # 唯一 ID
    metric_name: str              # 异常指标
    service: str                  # 受影响服务
    namespace: str                # K8s namespace
    severity: str                 # CRITICAL / HIGH / MEDIUM / LOW
    score: float                  # 综合评分 0-1

    current_value: float          # 当前值
    expected_value: float         # 基线期望值
    deviation_percent: float      # 偏离百分比

    start_time: datetime          # 异常开始时间
    duration: timedelta           # 已持续时间

    detection_methods: List[str]  # 触发的检测算法
    related_anomalies: List[str]  # 关联异常 ID

    context: Dict                 # 附加上下文
```

---

## 五、TrendPredictor - 趋势预测引擎

### 5.1 设计目标

预测未来 1-6 小时内指标的走势，回答两个关键问题：
1. **指标是否会达到危险阈值？什么时候？**
2. **当前异常趋势是在恶化还是趋于稳定？**

### 5.2 预测算法

#### 短期预测（1-2 小时）：线性外推 + 指数平滑

```python
"""简单有效，Phase 1 首选"""

def predict_short_term(metric_values, horizon_minutes=120):
    """
    使用最近 2 小时数据进行线性回归 + Holt-Winters 指数平滑
    """
    # 方案 1: 线性回归 (捕捉趋势)
    slope, intercept = linear_regression(metric_values[-120:])
    linear_prediction = [intercept + slope * (len(metric_values) + i)
                         for i in range(horizon_minutes)]

    # 方案 2: Holt-Winters 指数平滑 (捕捉趋势 + 季节性)
    hw_model = ExponentialSmoothing(
        metric_values,
        trend='add',
        seasonal='add',
        seasonal_periods=60  # 1 小时周期
    )
    hw_prediction = hw_model.forecast(horizon_minutes)

    # 加权融合
    prediction = 0.4 * linear_prediction + 0.6 * hw_prediction

    return prediction
```

#### 中期预测（2-6 小时）：Prophet（Phase 2）

```python
"""Facebook Prophet 用于带周期性的时序预测"""

def predict_medium_term(metric_name, horizon_hours=6):
    # 从 Mimir 获取 14 天历史数据
    history = mimir_client.query_range(
        metric_name,
        start=now - timedelta(days=14),
        end=now,
        step="1m"
    )

    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_mode='multiplicative',
        daily_seasonality=True,
        weekly_seasonality=True,
    )
    model.fit(history)

    future = model.make_future_dataframe(periods=horizon_hours * 60, freq='min')
    forecast = model.predict(future)

    return {
        "predictions": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
        "confidence_interval": 0.95
    }
```

### 5.3 阈值穿越预测

```python
def predict_threshold_breach(metric_name, current_trend, threshold):
    """预测指标什么时候会达到阈值"""

    predictions = predict_short_term(current_trend, horizon_minutes=360)

    for i, predicted_value in enumerate(predictions):
        if predicted_value >= threshold:
            breach_time = now + timedelta(minutes=i)
            return {
                "will_breach": True,
                "estimated_breach_time": breach_time,
                "minutes_until_breach": i,
                "confidence": calculate_confidence(i),  # 越远置信度越低
                "current_value": current_trend[-1],
                "threshold": threshold,
                "predicted_value_at_breach": predicted_value,
            }

    return {"will_breach": False}

# 触发规则:
#   预计 1 小时内达到阈值 → CRITICAL 预警
#   预计 3 小时内达到阈值 → HIGH 预警
#   预计 6 小时内达到阈值 → MEDIUM 预警 (白天处理)
```

### 5.4 预测输出

```python
@dataclass
class Prediction:
    metric_name: str
    current_value: float
    predictions: List[PredictionPoint]  # (time, value, confidence)

    will_breach_threshold: bool
    estimated_breach_time: Optional[datetime]
    minutes_until_breach: Optional[int]

    trend_direction: str    # "increasing", "decreasing", "stable", "oscillating"
    trend_strength: float   # 趋势强度 0-1

    model_used: str         # "linear", "holt_winters", "prophet", "lstm"
    confidence: float       # 整体置信度
```

---

## 六、RCAEngine - 根因分析引擎

### 6.1 设计思路

根因分析采用**规则引擎 + LLM 混合方案**：
- **规则引擎**处理已知模式（快速、确定性高）
- **LLM** 处理未知模式（灵活、需要推理）

```
异常事件
    │
    ▼
┌──────────────────┐     匹配已知模式？
│ Rule-Based RCA   │────── Yes ──▶ 返回确定性根因
│ (规则引擎)       │
└────────┬─────────┘
         │ No
         ▼
┌──────────────────┐
│ Data Collection  │ 收集关联数据:
│ (数据收集)       │ • 关联指标 (同服务其他指标)
│                  │ • 错误日志 (Loki)
│                  │ • 变更事件 (最近部署/配置变更)
│                  │ • K8s 事件 (Pod 状态变化)
│                  │ • 依赖服务状态
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM-Based RCA    │ 将所有上下文提交给 LLM:
│ (LLM 推理)       │ • 结构化 Prompt
│                  │ • 要求输出 JSON 格式的根因分析
│                  │ • 包含置信度评分
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ RAG Enhancement  │ 用知识库增强分析:
│ (知识库增强)     │ • 检索相似历史案例
│                  │ • 补充修复建议
└──────────────────┘
```

### 6.2 规则引擎：已知模式匹配

```yaml
rca_rules:
  # 规则 1: OOMKilled → 内存不足
  - name: oom_killed
    conditions:
      - event.reason == "OOMKilled"
    root_cause:
      category: "资源不足"
      cause: "Pod 内存超出 limits 被 OOMKilled"
      confidence: 0.95
    suggestions:
      - "检查是否存在内存泄漏"
      - "考虑增大 memory limits"
      - "检查最近是否有代码变更引入内存问题"

  # 规则 2: 部署后异常
  - name: post_deploy_anomaly
    conditions:
      - anomaly.start_time - last_deploy.time < 30m
      - anomaly.service == last_deploy.service
    root_cause:
      category: "部署变更"
      cause: "异常发生在部署 {{last_deploy.version}} 后 {{time_diff}} 分钟"
      confidence: 0.80
    suggestions:
      - "考虑回滚到 {{last_deploy.previous_version}}"
      - "检查 {{last_deploy.version}} 的变更内容"

  # 规则 3: Redis Eviction → 内存不足
  - name: redis_eviction
    conditions:
      - metric.redis_evicted_keys > 0
      - metric.redis_memory_usage > 0.85
    root_cause:
      category: "中间件瓶颈"
      cause: "Redis 内存接近上限，正在驱逐 Key"
      confidence: 0.90
    suggestions:
      - "清理过期/无用 Key"
      - "增大 Redis 内存或扩容节点"
      - "检查是否有大 Key 异常写入"

  # 规则 4: Kafka 消费积压
  - name: kafka_lag_spike
    conditions:
      - metric.kafka_consumer_lag > threshold.warning
      - metric.kafka_consumer_lag.trend == "increasing"
    root_cause:
      category: "消费能力不足"
      cause: "Kafka 消费者组积压量持续增长，当前 lag: {{lag}}"
      confidence: 0.75
    suggestions:
      - "检查消费者是否有处理异常"
      - "考虑增加消费者实例数"
      - "检查是否有慢消费导致的阻塞"

  # 规则 5: RDS 连接数飙升
  - name: rds_connection_spike
    conditions:
      - metric.rds_connections > baseline.upper_bound * 1.5
      - metric.rds_connections.trend == "increasing"
    root_cause:
      category: "数据库瓶颈"
      cause: "RDS 连接数异常增长，可能存在连接泄漏"
      confidence: 0.70
    suggestions:
      - "检查应用连接池配置"
      - "查看是否有长事务或慢查询占用连接"
      - "检查最近是否有代码变更影响连接管理"
```

### 6.3 LLM 根因分析 Prompt 设计

```python
RCA_SYSTEM_PROMPT = """你是一个资深的 SRE 工程师，负责对加密货币交易系统的异常进行根因分析。

你的分析必须基于提供的数据证据，不要猜测。
如果证据不足以确定根因，请明确说明并给出较低的置信度。

输出格式必须为 JSON:
{
  "root_causes": [
    {
      "cause": "简要描述根因",
      "category": "部署变更|资源不足|中间件瓶颈|依赖故障|流量突增|配置错误|代码Bug|外部因素",
      "confidence": 0.0-1.0,
      "evidence": ["证据1", "证据2"],
      "affected_services": ["service1"],
      "timeline": [
        {"time": "HH:MM", "event": "发生了什么"}
      ]
    }
  ],
  "immediate_risk": "当前最紧急的风险是什么",
  "recommended_actions": [
    {
      "action": "建议操作",
      "priority": "HIGH|MEDIUM|LOW",
      "risk_level": "描述操作风险",
      "expected_outcome": "预期效果"
    }
  ]
}
"""

RCA_USER_PROMPT_TEMPLATE = """
## 异常概况
- 异常指标: {anomaly.metric_name}
- 当前值: {anomaly.current_value} (基线: {anomaly.expected_value}, 偏离: {anomaly.deviation_percent}%)
- 严重度: {anomaly.severity}
- 开始时间: {anomaly.start_time}
- 持续时间: {anomaly.duration}
- 受影响服务: {anomaly.service} ({anomaly.namespace})

## 关联指标（同一服务最近 15 分钟）
{related_metrics_table}

## 错误日志（最近 15 分钟，Loki 查询结果）
{error_logs}

## 最近变更事件
{recent_changes}

## Kubernetes 事件
{k8s_events}

## 趋势预测
{trend_prediction}

## 类似历史案例（RAG 检索结果）
{similar_cases}

请分析以上数据，给出根因分析。
"""
```

### 6.4 根因分析输出

```python
@dataclass
class RCAResult:
    anomaly_id: str
    analysis_method: str          # "rule_based", "llm", "hybrid"

    root_causes: List[RootCause]  # 按置信度排序
    timeline: List[TimelineEvent] # 事件时间线

    immediate_risk: str           # 当前最紧急的风险描述
    recommended_actions: List[Action]
    similar_incidents: List[str]  # 相似历史事件 ID

    analysis_duration: float      # 分析耗时 (秒)
    llm_model_used: Optional[str] # 使用的 LLM 模型
    llm_tokens_used: Optional[int]

@dataclass
class RootCause:
    cause: str
    category: str
    confidence: float
    evidence: List[str]
    affected_services: List[str]
```

---

## 七、RAGKnowledgeBase - RAG 知识库

### 7.1 知识库内容

```yaml
knowledge_sources:
  # 1. 历史事件记录 (自动积累)
  incidents:
    source: 事件处理后自动写入
    fields:
      - incident_id
      - timestamp
      - affected_services
      - anomaly_description
      - root_cause
      - resolution_steps
      - resolution_duration
      - lessons_learned
    embedding_field: "anomaly_description + root_cause + resolution_steps"

  # 2. Runbook 文档 (人工维护)
  runbooks:
    source: Git 仓库中的 Markdown 文件
    fields:
      - title
      - service
      - scenario (什么情况下使用)
      - steps (操作步骤)
      - rollback (回滚方案)
    embedding_field: "title + scenario + steps"

  # 3. 架构文档 (人工维护)
  architecture:
    source: Confluence / Git
    fields:
      - service_name
      - dependencies
      - sla_requirements
      - known_issues
      - contact_person

  # 4. 告警处理经验 (半自动积累)
  alert_resolutions:
    source: Slack 告警频道中的处理记录 (提取)
    fields:
      - alert_description
      - resolution_summary
      - responder
```

### 7.2 向量化和检索

```yaml
vector_db:
  engine: qdrant
  collection: sre_knowledge

  embedding:
    model: text-embedding-3-small  # OpenAI embedding
    dimensions: 1536
    batch_size: 100

  indexing:
    # 新事件处理完成后，自动索引
    trigger: on_incident_resolved
    # 每周重建索引 (处理文档更新)
    rebuild: weekly

  retrieval:
    # 混合检索: 向量相似度 + 关键词匹配
    strategy: hybrid
    vector_weight: 0.7
    keyword_weight: 0.3
    top_k: 5

    # 元数据过滤
    filters:
      - service: 优先匹配同一服务的案例
      - severity: 优先匹配相同或更高严重度的案例
      - recency: 最近 6 个月的案例权重更高
```

### 7.3 知识反馈循环

```
事件处理完成
      │
      ▼
┌─────────────────────┐
│ Post-Incident Review │
│ • 确认根因           │
│ • 记录实际处理步骤   │
│ • 标记是否有效       │
│ • 提取 Lessons       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Knowledge Indexing   │
│ • 向量化事件记录     │
│ • 写入 Qdrant       │
│ • 更新相似案例关联   │
└──────────┬──────────┘
           │
           ▼
  下次类似异常时可检索到
```

---

## 八、认知层性能要求

| 组件 | 延迟要求 | 频率 | 资源消耗 |
|------|----------|------|----------|
| BaselineEngine | < 30min（后台任务） | 每天 1 次 | CPU 密集，可接受 |
| AnomalyDetector | < 5s（单轮检测） | 每分钟 | 低，主要是数值计算 |
| TrendPredictor | < 10s | 按需（异常触发） | 中，涉及模型预测 |
| RCAEngine (规则) | < 1s | 按需 | 低 |
| RCAEngine (LLM) | < 30s | 按需 | 依赖 LLM API 延迟 |
| RAGKnowledgeBase | < 3s | 按需 | 低，向量检索很快 |
