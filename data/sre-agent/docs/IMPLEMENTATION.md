# SRE Agent 实现文档

> AI 驱动的智能运维代理 - 面向加密货币交易系统的 AIOps 解决方案

**版本**: 0.1.0
**更新日期**: 2026-02-25
**状态**: 已完成实现

---

## 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [功能模块详解](#3-功能模块详解)
4. [技术栈](#4-技术栈)
5. [安装部署](#5-安装部署)
6. [使用指南](#6-使用指南)
7. [API 参考](#7-api-参考)
8. [配置说明](#8-配置说明)
9. [开发指南](#9-开发指南)
10. [运维手册](#10-运维手册)

---

## 1. 项目概述

### 1.1 背景与目标

SRE Agent 是一个基于 AI 的智能运维代理系统，专为加密货币交易平台设计。系统将传统的**被动告警**模式升级为**主动预测、智能诊断、自动化治理**的新一代 AIOps 平台。

### 1.2 核心价值

| 能力 | 传统方式 | SRE Agent |
|------|----------|-----------|
| **检测** | 固定阈值 (CPU > 80%) | 动态基线 + 多算法集成 |
| **响应** | 被动告警，人工排查 | 主动预警，AI 根因分析 |
| **处理** | 手动操作 | 自动/半自动修复 |
| **学习** | 无 | 知识库持续积累 |

### 1.3 关键指标目标

| 指标 | 目标值 |
|------|--------|
| MTTD (平均检测时间) | < 5 分钟 |
| MTTI (平均调查时间) | < 10 分钟 |
| MTTR (平均恢复时间) | < 30 分钟 |
| 预警提前量 | 2+ 小时 |
| 误报率 | < 10% |
| 自动修复成功率 | > 85% |

### 1.4 实现状态

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 基础框架 + 感知层 + 异常检测 + 通知 | ✅ 完成 |
| Phase 2 | 趋势预测 + 根因分析 + RAG 知识库 | ✅ 完成 |
| Phase 3 | 风险评估 + 自动修复 + 审批流程 | ✅ 完成 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            SRE Agent 系统架构                              │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │      Loki       │    │   Kubernetes    │
│   (Metrics)     │    │     (Logs)      │    │    (Events)     │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │      感知层 (Perception)     │
                    │  MetricsCollector          │
                    │  LogsCollector             │
                    │  EventsCollector           │
                    │  DataNormalizer            │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │      认知层 (Cognition)     │
                    │  BaselineEngine (基线学习)   │
                    │  AnomalyDetector (异常检测) │
                    │  TrendPredictor (趋势预测)  │
                    │  RCAEngine (根因分析)       │
                    │  KnowledgeBase (RAG)        │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │      决策层 (Decision)      │
                    │  RiskAssessor (风险评估)    │
                    │  PlaybookEngine (剧本引擎)  │
                    │  ActionPlanner (行动规划)   │
                    └───────────┬───────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
┌────────▼────────┐    ┌───────▼────────┐    ┌───────▼────────┐
│ NotificationMgr │    │ AutoRemediation│    │  AuditLogger   │
│   (Webhook)     │    │ (K8s/HTTP执行) │    │   (审计日志)   │
└─────────────────┘    └────────────────┘    └────────────────┘
```

### 2.2 四层架构详解

#### 2.2.1 感知层 (Perception Layer)

**职责**: 从多个数据源采集系统运行数据

| 组件 | 文件 | 功能 |
|------|------|------|
| MetricsCollector | `perception/metrics_collector.py` | Prometheus/Mimir 指标采集 |
| LogsCollector | `perception/logs_collector.py` | Loki 日志采集 |
| EventsCollector | `perception/events_collector.py` | K8s Events 采集 |
| DataNormalizer | `perception/normalizer.py` | 数据标准化、缺失值处理 |

**数据流**:
```
Prometheus → MetricsCollector → MetricSeries
Loki → LogsCollector → LogEntry
K8s API → EventsCollector → Event
```

#### 2.2.2 认知层 (Cognition Layer)

**职责**: AI/ML 分析，识别异常，预测趋势，定位根因

| 组件 | 文件 | 功能 |
|------|------|------|
| BaselineEngine | `cognition/baseline_engine.py` | STL 时序分解，学习正常行为基线 |
| AnomalyDetector | `cognition/anomaly_detector.py` | Z-Score + MAD + Isolation Forest 异常检测 |
| TrendPredictor | `cognition/trend_predictor.py` | Holt-Winters / Prophet 趋势预测 |
| RCAEngine | `cognition/rca_engine.py` | 规则 + Claude LLM 根因分析 |
| KnowledgeBase | `cognition/knowledge_base.py` | Qdrant 向量数据库 RAG 检索 |

**算法说明**:

| 算法 | 用途 | 特点 |
|------|------|------|
| Z-Score | 基线偏离检测 | 简单可解释，适合正态分布 |
| MAD | 稳健异常检测 | 对极端值鲁棒，适合偏斜分布 |
| Isolation Forest | 多维异常检测 | 发现关联异常 |
| Holt-Winters | 短期预测 | 快速，适合周期性数据 |
| Prophet | 中期预测 | 处理节假日效应 |
| STL | 时序分解 | 分离趋势、季节、残差 |

#### 2.2.3 决策层 (Decision Layer)

**职责**: 评估风险，规划行动方案

| 组件 | 文件 | 功能 |
|------|------|------|
| RiskAssessor | `decision/risk_assessment.py` | 多维度风险评分 |
| PlaybookEngine | `decision/playbook_engine.py` | YAML Playbook 解析 |
| ActionPlanner | `decision/action_planner.py` | 生成行动计划 |

**风险分级策略**:

| 风险评分 | 级别 | 策略 | 示例操作 |
|----------|------|------|----------|
| < 0.4 | AUTO | 自动执行 | Pod 重启、HPA 扩容 |
| 0.4-0.6 | SEMI_AUTO | 单人审批 | 服务回滚、配置变更 |
| 0.6-0.8 | MANUAL | 多人审批 | 数据库 Failover |
| ≥ 0.8 | CRITICAL | 仅诊断 | 钱包操作、资金相关 |

#### 2.2.4 执行层 (Action Layer)

**职责**: 执行修复操作，发送通知，记录审计

| 组件 | 文件 | 功能 |
|------|------|------|
| NotificationManager | `action/notification_manager.py` | HTTP Webhook 通知 |
| AutoRemediation | `action/auto_remediation.py` | 自愈执行引擎 |
| KubernetesExecutor | `action/executors/k8s_executor.py` | K8s 操作 (重启/扩容/回滚) |
| HTTPExecutor | `action/executors/http_executor.py` | 自定义 Webhook 调用 |
| AuditLogger | `action/audit_logger.py` | 操作审计日志 |

### 2.3 数据流转

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              主循环 (每分钟执行)                          │
└─────────────────────────────────────────────────────────────────────────┘

1. 数据采集
   Prometheus/Loki/K8s → Collectors → 原始数据 → Normalizer → 标准化数据

2. 基线比对
   当前指标 + 历史基线 → AnomalyDetector → 异常列表

3. 深度分析 (仅对异常执行)
   异常 → TrendPredictor → 趋势预测
        → RCAEngine → 根因分析
        → KnowledgeBase → 相似案例

4. 决策规划
   异常 + 分析结果 → RiskAssessor → 风险评分
                   → PlaybookEngine → 匹配剧本
                   → ActionPlanner → 行动计划

5. 执行/通知
   低风险计划 → AutoRemediation → 自动执行 → AuditLogger
   中高风险计划 → NotificationManager → 审批请求 → 等待审批

6. 反馈学习 (异步)
   执行结果 → KnowledgeBase → 更新知识库
```

### 2.4 项目结构

```
sre-agent/
├── src/
│   ├── __init__.py
│   ├── agent/                    # Agent 核心
│   │   ├── orchestrator.py       # 主循环编排器
│   │   └── prompts.py            # LLM Prompt 模板
│   ├── perception/               # 感知层
│   │   ├── base_collector.py     # 采集器基类
│   │   ├── metrics_collector.py  # Prometheus 采集
│   │   ├── logs_collector.py     # Loki 采集
│   │   ├── events_collector.py   # K8s Events 采集
│   │   └── normalizer.py         # 数据标准化
│   ├── cognition/                # 认知层
│   │   ├── baseline_engine.py    # 基线学习 (STL)
│   │   ├── anomaly_detector.py   # 异常检测 (Z-Score/MAD/IF)
│   │   ├── trend_predictor.py    # 趋势预测 (Holt-Winters)
│   │   ├── rca_engine.py         # 根因分析 (规则+LLM)
│   │   ├── rca_rules.py          # RCA 规则引擎
│   │   └── knowledge_base.py     # RAG 知识库 (Qdrant)
│   ├── decision/                 # 决策层
│   │   ├── risk_assessment.py    # 风险评估
│   │   ├── playbook_engine.py    # Playbook 解析
│   │   └── action_planner.py     # 行动规划
│   ├── action/                   # 执行层
│   │   ├── notification_manager.py # 通知管理
│   │   ├── auto_remediation.py   # 自愈引擎
│   │   ├── audit_logger.py       # 审计日志
│   │   └── executors/
│   │       ├── k8s_executor.py   # K8s 执行器
│   │       └── http_executor.py  # HTTP 执行器
│   ├── models/                   # 数据模型
│   │   ├── metrics.py            # 指标数据模型
│   │   ├── baseline.py           # 基线数据模型
│   │   ├── anomaly.py            # 异常数据模型
│   │   ├── action_plan.py        # 行动计划模型
│   │   └── audit.py              # 审计日志模型
│   ├── config/                   # 配置管理
│   │   ├── settings.py           # Pydantic Settings
│   │   └── constants.py          # 常量定义
│   └── api/                      # REST API
│       ├── main.py               # FastAPI 应用
│       └── routes/
│           ├── health.py         # 健康检查
│           ├── anomalies.py      # 异常 API
│           ├── approvals.py      # 审批 API
│           └── baselines.py      # 基线 API
├── config/                       # 配置文件
│   ├── config.yaml               # 主配置
│   ├── promql_queries.yaml       # PromQL 查询定义
│   ├── rca_rules.yaml            # RCA 规则
│   └── playbooks/                # 修复剧本
│       ├── pod-restart.yaml
│       ├── hpa-scale-up.yaml
│       └── service-rollback.yaml
├── k8s/                          # Kubernetes 部署
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── rbac.yaml
├── tests/                        # 测试
│   ├── conftest.py
│   ├── test_baseline_engine.py
│   ├── test_anomaly_detector.py
│   ├── test_risk_assessment.py
│   └── test_api.py
├── pyproject.toml                # 项目配置
├── requirements.txt              # 依赖
├── Dockerfile                    # 容器镜像
├── docker-compose.yaml           # 本地开发环境
└── Makefile                      # 构建命令
```

---

## 3. 功能模块详解

### 3.1 指标采集 (MetricsCollector)

**支持的加密货币交易系统指标**:

| 类别 | 指标 | 说明 |
|------|------|------|
| **交易引擎** | order_latency_p99 | 订单处理延迟 |
| | order_qps | 订单吞吐量 |
| | order_error_rate | 订单错误率 |
| **撮合引擎** | matching_latency_p99 | 撮合延迟 |
| | orderbook_depth | 订单簿深度 |
| **风控** | margin_utilization | 保证金使用率 |
| | risk_limit_breaches | 风控限额突破 |
| **钱包** | balance_sync_latency | 余额同步延迟 |
| | pending_transactions | 待处理交易 |
| **API** | api_latency_p99 | API 延迟 |
| | api_error_rate | API 错误率 |
| **基础设施** | cpu_usage | CPU 使用率 |
| | memory_usage | 内存使用率 |
| | pod_restarts | Pod 重启次数 |

### 3.2 异常检测 (AnomalyDetector)

**检测流程**:
```python
for metric in metrics:
    scores = []

    # 1. Z-Score 检测 (基线偏离)
    zscore = (current - baseline_mean) / baseline_std
    if zscore > 3.0:
        scores.append(("zscore", zscore))

    # 2. MAD 检测 (稳健统计)
    mad_score = 0.6745 * |current - median| / mad
    if mad_score > 3.5:
        scores.append(("mad", mad_score))

    # 3. 集成投票
    if len(scores) >= 2:
        create_anomaly(metric, scores)
```

**严重程度分级**:
```
deviation < 3σ  → LOW
3σ ≤ deviation < 4σ → MEDIUM
4σ ≤ deviation < 5σ → HIGH
deviation ≥ 5σ → CRITICAL
```

### 3.3 趋势预测 (TrendPredictor)

**预测功能**:
- 支持 1/3/6 小时预测窗口
- Holt-Winters 指数平滑 (默认)
- Prophet 时序预测 (可选)
- 阈值突破预警

**使用示例**:
```python
predictor = TrendPredictor()
prediction = predictor.predict(metric_series, horizon_hours=6)

# 检查是否会突破阈值
will_breach, breach_time, value = prediction.will_breach_threshold(
    threshold=0.9,
    direction="above"
)
```

### 3.4 根因分析 (RCAEngine)

**分析流程**:

1. **规则匹配**: 基于 `rca_rules.yaml` 匹配已知模式
2. **关联分析**: 检查相关指标是否同时异常
3. **日志分析**: 提取错误模式 (timeout, OOM, etc.)
4. **事件关联**: 检查近期部署、配置变更
5. **LLM 分析**: 复杂场景使用 Claude 分析

**规则示例**:
```yaml
- id: high_latency_cpu
  condition:
    primary_metric: "api_latency_p99"
    primary_threshold: 0.5
    correlated_metrics:
      - metric: "cpu_usage"
        threshold: 0.85
  root_cause: "CPU 饱和导致延迟升高"
  remediation:
    - action: hpa_scale
      target: deployment
```

### 3.5 风险评估 (RiskAssessor)

**四维风险模型**:

| 维度 | 权重 | 计算依据 |
|------|------|----------|
| Severity (严重性) | 35% | 异常严重程度、指标类别 |
| Urgency (紧迫性) | 25% | 持续时间、趋势 |
| Impact (影响范围) | 25% | 命名空间、操作类型、业务类别 |
| Complexity (复杂度) | 15% | 操作类型固有复杂度 |

**计算公式**:
```python
risk_score = (
    0.35 * severity +
    0.25 * urgency +
    0.25 * impact +
    0.15 * complexity
)
```

### 3.6 自动修复 (AutoRemediation)

**支持的操作**:

| 操作类型 | 风险级别 | 说明 |
|----------|----------|------|
| pod_restart | 低 | 重启 Pod |
| hpa_scale | 低 | HPA 扩容 |
| deployment_rollback | 中 | 部署回滚 |
| config_rollback | 中 | 配置回滚 |
| circuit_breaker | 中 | 熔断 |
| database_failover | 高 | 数据库切换 |

**安全机制**:
- 黑名单保护 (kube-system, 关键命名空间)
- 冷却时间 (同目标 5 分钟内不重复操作)
- 并发限制 (最多 3 个并发操作)
- 自动回滚 (失败时回滚已执行步骤)
- 完整审计日志

---

## 4. 技术栈

### 4.1 核心框架

| 组件 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.11+ |
| Web 框架 | FastAPI | 0.115+ |
| 配置管理 | Pydantic Settings | 2.6+ |
| 日志 | structlog | 24.4+ |
| 重试 | tenacity | 9.0+ |

### 4.2 数据采集

| 数据源 | 客户端 | 用途 |
|--------|--------|------|
| Prometheus | prometheus-api-client | 指标采集 |
| Loki | httpx | 日志采集 |
| Kubernetes | kubernetes-client | 事件采集、操作执行 |

### 4.3 AI/ML

| 功能 | 库 | 说明 |
|------|-----|------|
| 基线学习 | statsmodels | STL 分解 |
| 异常检测 | scikit-learn | Isolation Forest |
| 趋势预测 | statsmodels | Holt-Winters |
| 趋势预测 | prophet | Prophet (可选) |
| 根因分析 | anthropic | Claude API |
| 向量搜索 | qdrant-client | RAG 知识库 |

### 4.4 基础设施

| 组件 | 用途 |
|------|------|
| Prometheus | 指标存储 |
| Loki | 日志存储 |
| Qdrant | 向量数据库 |
| Kubernetes | 容器编排 |

---

## 5. 安装部署

### 5.1 前置要求

- Python 3.11+
- Docker & Docker Compose (本地开发)
- Kubernetes 集群 (生产部署)
- Prometheus (已部署)
- Loki (可选)
- Claude API Key

### 5.2 本地开发部署

```bash
# 1. 克隆项目
git clone <repo-url>
cd sre-agent

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
make dev-install

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 设置 ANTHROPIC_API_KEY 等

# 5. 启动依赖服务 (Prometheus, Loki, Qdrant)
docker-compose up -d prometheus loki qdrant

# 6. 运行测试
make test

# 7. 启动 Agent (开发模式)
make run-api
```

### 5.3 Docker Compose 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f sre-agent

# 检查健康状态
curl http://localhost:8000/health
```

### 5.4 Kubernetes 部署

```bash
# 1. 创建 Namespace
kubectl apply -f k8s/namespace.yaml

# 2. 创建 RBAC
kubectl apply -f k8s/rbac.yaml

# 3. 创建 ConfigMap
kubectl apply -f k8s/configmap.yaml

# 4. 创建 Secret (先编辑 k8s/service.yaml 中的 Secret)
kubectl apply -f k8s/service.yaml

# 5. 部署 Agent
kubectl apply -f k8s/deployment.yaml

# 6. 验证部署
kubectl get pods -n sre-agent
kubectl logs -f deployment/sre-agent -n sre-agent
```

### 5.5 生产环境配置

**关键配置项**:

```yaml
# config/config.yaml
app:
  environment: production

auto_remediation:
  enabled: true
  dry_run: false  # 生产环境设为 false
  blacklist:
    namespaces:
      - kube-system
      - production-critical
      - wallet-service  # 钱包服务禁止自动操作

llm:
  model: claude-sonnet-4-20250514
  temperature: 0.1  # 低温度保证输出稳定

baseline:
  min_history_days: 7
  optimal_history_days: 30
```

---

## 6. 使用指南

### 6.1 首次启动

Agent 首次启动会自动进行基线学习：

```
[INFO] Starting SRE Agent v0.1.0
[INFO] Initializing components...
[INFO] Connected to Prometheus
[INFO] Connected to Loki
[INFO] Updating baselines...
[INFO] Learned baseline for order_latency_p99 (samples: 10080, quality: 0.85)
[INFO] Baselines updated (count: 15)
[INFO] Starting main loop (interval: 60s)
```

**注意事项**:
- 基线学习需要至少 7 天历史数据
- 数据不足时使用静态阈值
- 学习完成前异常检测准确率较低

### 6.2 监控循环

Agent 每分钟执行监控循环：

```
[INFO] Detection cycle complete
       metrics_checked=15
       anomalies_detected=2
       critical_anomalies=0
       duration_seconds=1.23
```

### 6.3 异常处理流程

当检测到异常时：

```
[INFO] Anomaly detected
       id=ANO-a1b2c3d4
       metric=order_latency_p99
       current=0.523
       baseline=0.180
       deviation=5.7σ
       severity=high

[INFO] RCA analysis complete
       root_causes=["CPU saturation", "Recent deployment"]
       confidence=0.85

[INFO] Action plan created
       plan_id=PLAN-x1y2z3
       risk_level=semi_auto
       requires_approval=true
       steps=2

[INFO] Approval request sent via webhook
```

### 6.4 审批操作

**查看待审批**:
```bash
curl http://localhost:8000/api/v1/approvals
```

**批准**:
```bash
curl -X POST http://localhost:8000/api/v1/approvals/PLAN-x1y2z3/approve \
  -H "Content-Type: application/json" \
  -d '{"approver": "sre@company.com"}'
```

**拒绝**:
```bash
curl -X POST http://localhost:8000/api/v1/approvals/PLAN-x1y2z3/reject \
  -H "Content-Type: application/json" \
  -d '{"rejector": "sre@company.com", "reason": "需要更多调查"}'
```

### 6.5 Dry Run 模式

生产环境建议先启用 dry-run 模式验证：

```yaml
auto_remediation:
  enabled: true
  dry_run: true  # 不实际执行，仅记录日志
```

日志输出：
```
[INFO] DRY RUN: Would execute step
       step_id=STEP-abc123
       action=pod_restart
       target=trading-engine-pod-xyz
```

---

## 7. API 参考

### 7.1 健康检查

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/ready` | GET | 就绪检查 (K8s) |
| `/live` | GET | 存活检查 (K8s) |

### 7.2 状态查询

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/status` | GET | Agent 状态 |
| `/api/v1/metrics` | GET | 配置的指标列表 |

**响应示例**:
```json
{
  "running": true,
  "active_anomalies": 2,
  "baselines_loaded": 15,
  "last_baseline_update": "2026-02-25T10:30:00Z",
  "metrics_collector_connected": true,
  "logs_collector_connected": true
}
```

### 7.3 异常管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/anomalies` | GET | 列出异常 |
| `/api/v1/anomalies/{id}` | GET | 异常详情 |
| `/api/v1/anomalies/{id}/acknowledge` | POST | 确认异常 |

**查询参数**:
- `category`: 按类别过滤 (trading, api, infrastructure...)
- `severity`: 按严重程度过滤 (low, medium, high, critical)
- `active_only`: 仅返回活跃异常 (默认 true)

### 7.4 基线管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/baselines` | GET | 列出基线 |

### 7.5 审批管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/approvals` | GET | 待审批列表 |
| `/api/v1/approvals/{plan_id}` | GET | 计划详情 |
| `/api/v1/approvals/{plan_id}/approve` | POST | 批准 |
| `/api/v1/approvals/{plan_id}/reject` | POST | 拒绝 |
| `/api/v1/plans` | GET | 所有计划列表 |

---

## 8. 配置说明

### 8.1 主配置 (config/config.yaml)

```yaml
# 应用配置
app:
  name: sre-agent
  version: "0.1.0"
  environment: development  # development/staging/production
  log_level: INFO

# Prometheus 配置
prometheus:
  url: ${PROMETHEUS_URL:-http://localhost:9090}
  timeout_seconds: 30
  retry_attempts: 3

# Loki 配置
loki:
  url: ${LOKI_URL:-http://localhost:3100}
  timeout_seconds: 30

# LLM 配置
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  api_key: ${ANTHROPIC_API_KEY}
  max_tokens: 4096
  temperature: 0.1

# 基线学习配置
baseline:
  min_history_days: 7       # 最少历史数据天数
  optimal_history_days: 30  # 最佳历史数据天数
  learning_interval_hours: 24  # 更新间隔

# 异常检测配置
anomaly_detection:
  check_interval_seconds: 60  # 检测间隔
  zscore_threshold: 3.0       # Z-Score 阈值
  mad_threshold: 3.5          # MAD 阈值
  ensemble_min_votes: 2       # 最少算法投票数

# 风险评估配置
risk_assessment:
  weights:
    severity: 0.35
    urgency: 0.25
    impact: 0.25
    complexity: 0.15
  thresholds:
    auto: 0.4       # < 0.4 自动执行
    semi_auto: 0.6  # 0.4-0.6 单人审批
    manual: 0.8     # 0.6-0.8 多人审批

# 自动修复配置
auto_remediation:
  enabled: true
  dry_run: false
  max_concurrent_actions: 3
  cooldown_minutes: 5
  blacklist:
    namespaces:
      - kube-system
    labels:
      - "do-not-remediate=true"

# 通知配置
notification:
  webhook:
    url: ${WEBHOOK_URL}
    timeout_seconds: 10

# API 配置
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
```

### 8.2 环境变量

```bash
# 必需
ANTHROPIC_API_KEY=sk-ant-...

# 数据源
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
QDRANT_URL=http://qdrant:6333

# 通知
WEBHOOK_URL=https://hooks.slack.com/...

# Kubernetes (集群内部署时)
K8S_IN_CLUSTER=true

# 日志
LOG_LEVEL=INFO
```

### 8.3 PromQL 查询 (config/promql_queries.yaml)

```yaml
trading:
  order_latency_p99:
    query: 'histogram_quantile(0.99, sum(rate(trading_order_latency_seconds_bucket[5m])) by (le, service))'
    unit: seconds
    description: P99 order processing latency

api:
  api_error_rate:
    query: 'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))'
    unit: ratio
    description: API 5xx error rate
```

### 8.4 Playbook (config/playbooks/*.yaml)

```yaml
id: pod-restart
name: Pod Restart
description: Restart a pod by deleting it

trigger_conditions:
  - "memory_usage > 0.9"
  - "OOMKilled"

risk_override: 0.25  # 低风险

steps:
  - name: Restart Pod
    action: pod_restart
    target: "{{ target_pod }}"
    parameters:
      grace_period: 30
    timeout_seconds: 120
```

---

## 9. 开发指南

### 9.1 添加新指标

1. 在 `config/promql_queries.yaml` 添加查询：

```yaml
your_category:
  your_metric:
    query: 'your_promql_query'
    unit: seconds
    description: Your description
```

2. 指标会自动被采集和监控

### 9.2 添加新检测算法

1. 在 `AnomalyDetector` 添加方法：

```python
def _your_algorithm_detect(self, value, baseline, timestamp):
    # 实现检测逻辑
    score = ...
    is_anomaly = score > threshold
    return AnomalyScore(
        algorithm="your_algorithm",
        score=score,
        threshold=threshold,
        is_anomaly=is_anomaly,
    )
```

2. 在 `_detect_metric_anomaly` 中调用

3. 在配置中启用：
```yaml
anomaly_detection:
  algorithms:
    - zscore
    - mad
    - your_algorithm
```

### 9.3 添加新修复操作

1. 在 `KubernetesExecutor` 或创建新执行器：

```python
async def your_action(self, target, namespace, parameters):
    # 实现操作逻辑
    return {
        "success": True,
        "state_before": {...},
        "rollback_data": {...},
    }
```

2. 在 `AutoRemediation._dispatch_action` 添加路由

3. 创建 Playbook：
```yaml
id: your-playbook
steps:
  - action: your_action
    target: "{{ target }}"
```

### 9.4 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_anomaly_detector.py -v

# 生成覆盖率报告
make coverage
```

### 9.5 代码规范

```bash
# 格式化
make format

# 检查
make lint
```

---

## 10. 运维手册

### 10.1 监控 Agent 自身

**关键指标**:
- `sre_agent_detection_duration_seconds`: 检测循环耗时
- `sre_agent_anomalies_active`: 活跃异常数
- `sre_agent_remediation_total`: 修复操作计数

**告警规则示例**:
```yaml
- alert: SREAgentDown
  expr: up{job="sre-agent"} == 0
  for: 5m

- alert: SREAgentHighLatency
  expr: sre_agent_detection_duration_seconds > 30
  for: 10m
```

### 10.2 日志排查

```bash
# 查看错误
kubectl logs deployment/sre-agent -n sre-agent | grep ERROR

# 查看异常检测详情
kubectl logs deployment/sre-agent -n sre-agent | grep "Anomaly detected"

# 查看审计日志
kubectl exec deployment/sre-agent -n sre-agent -- cat /var/log/sre-agent/audit.log
```

### 10.3 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 无法连接 Prometheus | 网络/配置问题 | 检查 PROMETHEUS_URL |
| 基线学习失败 | 历史数据不足 | 等待积累 7 天数据 |
| LLM 调用失败 | API Key 无效 | 检查 ANTHROPIC_API_KEY |
| 内存占用高 | 缓存过大 | 减少 baseline.optimal_history_days |
| 告警风暴 | 阈值过低 | 提高 zscore_threshold |

### 10.4 备份恢复

**基线备份**:
```bash
# 导出基线
curl http://localhost:8000/api/v1/baselines > baselines_backup.json

# 恢复基线 (需要实现导入接口)
```

**审计日志备份**:
```bash
# 定期备份审计日志
kubectl cp sre-agent/sre-agent-xxx:/var/log/sre-agent/audit.log ./audit_backup.log
```

---

## 附录

### A. 文件清单

共 **62** 个文件实现：

- 项目配置: 7 个
- 源代码: 35 个
- 配置文件: 9 个
- K8s 部署: 5 个
- 测试: 5 个
- 文档: 1 个

### B. 依赖列表

核心依赖见 `requirements.txt`，主要包括：
- fastapi, uvicorn (API)
- pydantic, pydantic-settings (配置)
- anthropic (LLM)
- prometheus-api-client (指标)
- kubernetes (K8s 操作)
- numpy, pandas, scikit-learn (数据处理)
- statsmodels, prophet (时序分析)
- qdrant-client (向量数据库)
- structlog (日志)
- tenacity (重试)

### C. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.0 | 2026-02-25 | 初始实现，完成全部三个阶段 |

---

**文档结束**
