# 06 - 技术栈选型与实施路线

## 一、技术栈全景

### 1.1 整体技术栈

```
┌──────────────────────────────────────────────────────────────────┐
│                         SRE Agent 技术栈                          │
│                                                                    │
│  ┌─── 应用层 ───────────────────────────────────────────────┐    │
│  │  Python 3.11+ │ FastAPI │ Celery │ APScheduler           │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌─── Agent / AI 层 ────────────────────────────────────────┐    │
│  │  LangChain / LangGraph    (Agent 编排)                    │    │
│  │  Claude API / OpenAI API  (LLM 推理)                     │    │
│  │  text-embedding-3-small   (向量化)                        │    │
│  │  scikit-learn / Prophet   (ML 模型)                       │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌─── 数据层 ───────────────────────────────────────────────┐    │
│  │  Prometheus + Mimir  (指标)     │ 已有，复用              │    │
│  │  Loki + Promtail     (日志)     │ 已有，复用              │    │
│  │  n9e / 夜莺           (告警)     │ 已有，复用              │    │
│  │  Grafana             (可视化)    │ 已有，复用              │    │
│  │  Kafka               (事件流)    │ 已有，复用              │    │
│  │  Redis / ElastiCache (缓存)     │ 已有，复用              │    │
│  │  RDS MySQL           (元数据)    │ 已有，复用              │    │
│  │  Qdrant              (向量DB)   │ 新增                    │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌─── 基础设施层 ───────────────────────────────────────────┐    │
│  │  AWS EKS │ EC2 │ S3 │ ALB │ IAM (IRSA)                  │    │
│  └───────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件选型决策

| 组件 | 选型 | 备选方案 | 选型理由 |
|------|------|----------|----------|
| **Agent 框架** | LangGraph | LangChain, AutoGen, CrewAI | LangGraph 支持有状态工作流和条件分支，适合 SRE 多步决策流程 |
| **LLM** | Claude API (主) | OpenAI GPT-4, 本地 Llama 3 | Claude 在长上下文分析和结构化输出方面表现好；本地模型做降级 |
| **向量数据库** | Qdrant | Milvus, Pinecone, Chroma | Qdrant 轻量、支持 K8s 部署、Rust 实现性能好、开源 |
| **任务队列** | Celery + Redis | Dramatiq, Huey | Celery 成熟稳定，Redis 已有，不引入新依赖 |
| **Web 框架** | FastAPI | Flask, Django | FastAPI 异步原生、自动生成 OpenAPI 文档、性能好 |
| **时序预测** | Prophet + statsmodels | TensorFlow, LSTM | Prophet 开箱即用、对周期性数据效果好；Phase 1 够用 |
| **异常检测 ML** | scikit-learn | PyTorch, TF | Isolation Forest / One-Class SVM 这些经典算法够用 |
| **Embedding** | text-embedding-3-small | Cohere, local models | 性价比高，1536 维，足够 SRE 知识库场景 |
| **告警管理** | 复用 n9e + 自建增强 | 替换为 Alertmanager | n9e 已有部署，MCP 支持好，告警路由功能完善 |

---

## 二、项目结构设计

```
sre-agent/
├── src/
│   ├── __init__.py
│   │
│   ├── agent/                          # Agent 核心
│   │   ├── __init__.py
│   │   ├── orchestrator.py             # 主编排器 (LangGraph workflow)
│   │   ├── tools.py                    # Agent 可调用的 Tools 定义
│   │   └── prompts.py                  # LLM Prompt 模板
│   │
│   ├── perception/                     # 感知层
│   │   ├── __init__.py
│   │   ├── metrics_collector.py        # Prometheus/Mimir 指标采集
│   │   ├── logs_collector.py           # Loki 日志采集
│   │   ├── events_collector.py         # K8s 事件 + Kafka 事件
│   │   ├── aws_collector.py            # AWS CloudWatch + API
│   │   └── normalizer.py              # 数据标准化
│   │
│   ├── cognition/                      # 认知层
│   │   ├── __init__.py
│   │   ├── baseline_engine.py          # 基线学习
│   │   ├── anomaly_detector.py         # 异常检测 (多算法集成)
│   │   ├── trend_predictor.py          # 趋势预测
│   │   ├── rca_engine.py              # 根因分析 (规则 + LLM)
│   │   ├── rca_rules.py              # RCA 规则定义
│   │   └── knowledge_base.py          # RAG 知识库
│   │
│   ├── decision/                       # 决策层
│   │   ├── __init__.py
│   │   ├── risk_assessment.py          # 风险评估
│   │   ├── action_planner.py           # 行动规划
│   │   ├── playbook_engine.py          # Playbook 引擎
│   │   └── approval_manager.py         # 审批管理
│   │
│   ├── action/                         # 执行层
│   │   ├── __init__.py
│   │   ├── alert_manager.py            # 告警管理 (n9e 集成)
│   │   ├── ticket_manager.py           # 工单管理
│   │   ├── auto_remediation.py         # 自愈执行引擎
│   │   ├── executors/                  # 具体执行器
│   │   │   ├── k8s_executor.py         # kubectl 操作
│   │   │   ├── aws_executor.py         # AWS CLI/SDK 操作
│   │   │   ├── helm_executor.py        # Helm 操作
│   │   │   └── redis_executor.py       # Redis 操作
│   │   └── audit_logger.py            # 审计日志
│   │
│   ├── integrations/                   # 外部集成
│   │   ├── __init__.py
│   │   ├── slack_integration.py        # Slack 通知 + 审批
│   │   ├── pagerduty_integration.py    # PagerDuty 集成
│   │   ├── jira_integration.py         # Jira 工单集成
│   │   ├── n9e_integration.py          # n9e MCP/API 集成
│   │   └── grafana_integration.py      # Grafana API 集成
│   │
│   ├── models/                         # 数据模型
│   │   ├── __init__.py
│   │   ├── metrics.py                  # 指标数据模型
│   │   ├── anomaly.py                  # 异常数据模型
│   │   ├── action_plan.py              # 行动计划模型
│   │   └── audit.py                    # 审计日志模型
│   │
│   ├── api/                            # API 接口
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app
│   │   ├── routes/
│   │   │   ├── health.py               # 健康检查
│   │   │   ├── anomalies.py            # 异常查询 API
│   │   │   ├── approvals.py            # 审批 API
│   │   │   ├── baselines.py            # 基线管理 API
│   │   │   └── audit.py                # 审计查询 API
│   │   └── webhooks/
│   │       ├── slack_webhook.py        # Slack 交互回调
│   │       └── n9e_webhook.py          # n9e 告警回调
│   │
│   └── config/                         # 配置
│       ├── __init__.py
│       ├── settings.py                 # 配置加载 (pydantic-settings)
│       └── constants.py                # 常量定义
│
├── config/
│   ├── config.yaml                     # 主配置文件
│   ├── promql_queries.yaml             # PromQL 查询定义
│   ├── rca_rules.yaml                  # 根因分析规则
│   └── playbooks/                      # 自愈 Playbook
│       ├── pod-restart.yaml
│       ├── service-rollback.yaml
│       ├── hpa-scale-up.yaml
│       ├── redis-memory.yaml
│       ├── kafka-lag.yaml
│       └── rds-connections.yaml
│
├── tests/
│   ├── unit/                           # 单元测试
│   │   ├── test_anomaly_detector.py
│   │   ├── test_baseline_engine.py
│   │   ├── test_risk_assessment.py
│   │   └── test_action_planner.py
│   ├── integration/                    # 集成测试
│   │   ├── test_prometheus_collector.py
│   │   ├── test_loki_collector.py
│   │   └── test_remediation_flow.py
│   └── fixtures/                       # 测试数据
│       ├── sample_metrics.json
│       └── sample_anomalies.json
│
├── k8s/                                # K8s 部署清单
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── rbac.yaml
│   ├── serviceaccount.yaml
│   └── cronjob-baseline.yaml
│
├── helm/                               # Helm Chart (可选)
│   └── sre-agent/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── docs/
│   └── design/                         # 设计文档 (本系列)
│
├── Dockerfile
├── docker-compose.yaml                 # 本地开发环境
├── pyproject.toml                      # 项目配置 (Poetry/PDM)
├── requirements.txt                    # pip 依赖
├── Makefile                            # 常用命令
├── CLAUDE.md                           # Claude Code 指引
└── README.md                           # 项目文档
```

---

## 三、核心依赖清单

```toml
# pyproject.toml (核心依赖)
[project]
name = "sre-agent"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Web Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",

    # Agent / LLM
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "anthropic>=0.40.0",          # Claude API
    "openai>=1.55.0",             # OpenAI API (embedding + fallback)

    # Task Queue
    "celery[redis]>=5.4.0",

    # Data Collection
    "prometheus-api-client>=0.5.0",  # Prometheus/Mimir 查询
    "boto3>=1.35.0",                 # AWS SDK
    "kubernetes>=31.0.0",            # K8s API
    "confluent-kafka>=2.6.0",        # Kafka consumer

    # ML / Analysis
    "numpy>=2.0.0",
    "pandas>=2.2.0",
    "scikit-learn>=1.5.0",        # Isolation Forest, One-Class SVM
    "statsmodels>=0.14.0",        # STL, ARIMA, Exponential Smoothing
    "prophet>=1.1.0",             # 时序预测 (Phase 2)

    # Vector DB / RAG
    "qdrant-client>=1.12.0",

    # Integrations
    "slack-sdk>=3.33.0",          # Slack
    "httpx>=0.28.0",              # HTTP client (n9e, Loki, Jira API)
    "redis>=5.2.0",

    # Utilities
    "pyyaml>=6.0",
    "structlog>=24.4.0",          # 结构化日志
    "tenacity>=9.0.0",            # 重试机制
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",                # Linter + Formatter
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
]
```

---

## 四、配置文件设计

```yaml
# config/config.yaml

# ============================================
# SRE Agent 配置
# ============================================

agent:
  name: "sre-agent-trading"
  environment: "production"  # production / staging / development
  log_level: "INFO"
  check_interval_seconds: 60  # 主循环间隔

# ============================================
# 数据源配置
# ============================================

prometheus:
  url: "http://prometheus:9090"
  timeout: 30
  # 长期查询走 Mimir
  mimir_url: "http://mimir-query-frontend:8080/prometheus"
  mimir_tenant_id: "trading"

loki:
  url: "http://loki:3100"
  timeout: 30

n9e:
  url: "http://n9e-server:17000"
  api_token: "${N9E_API_TOKEN}"

kafka:
  bootstrap_servers: "kafka-1:9092,kafka-2:9092,kafka-3:9092"
  consumer_group: "sre-agent"
  topics:
    deploy_events: "deploy-events"
    trading_alerts: "trading-alerts"
    config_changes: "config-changes"
  # Agent 产生的审计事件
  producer_topic: "sre-agent-audit"

kubernetes:
  in_cluster: true  # 使用 ServiceAccount
  namespaces:
    - trading
    - matching
    - wallet
    - infra

aws:
  region: "ap-southeast-1"
  # 使用 IRSA，不需要 access key
  resources:
    rds_instances:
      - trading-db-primary
      - trading-db-replica
    elasticache_clusters:
      - trading-redis-001
      - trading-redis-002
    alb:
      - app/trading-alb/xxxxxxxxxx

# ============================================
# AI / ML 配置
# ============================================

llm:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"
    api_key: "${ANTHROPIC_API_KEY}"
    max_tokens: 4096
    temperature: 0.1  # 低温度，更确定性的输出
  fallback:
    provider: "openai"
    model: "gpt-4o-mini"
    api_key: "${OPENAI_API_KEY}"

embedding:
  provider: "openai"
  model: "text-embedding-3-small"
  api_key: "${OPENAI_API_KEY}"

vector_db:
  engine: "qdrant"
  url: "http://qdrant:6333"
  collection: "sre_knowledge"

# ============================================
# 基线 & 异常检测配置
# ============================================

baseline:
  learning_days: 14           # 基线学习使用 14 天数据
  minimum_days: 7             # 最少需要 7 天
  update_schedule: "0 3 * * *"  # 每天 UTC 03:00 更新
  full_retrain_schedule: "0 4 * * 0"  # 每周日重训练
  anomaly_filter: true        # 剔除异常数据

anomaly_detection:
  # Z-Score 阈值
  z_score_thresholds:
    critical: 3.0
    high: 2.5
    medium: 2.0
  # 降噪
  min_duration_seconds:
    critical: 60
    high: 120
    medium: 300
    low: 600
  # 去重
  dedup_window_minutes: 30

prediction:
  horizon_hours: 6
  short_term_model: "holt_winters"
  medium_term_model: "prophet"

# ============================================
# 风险评估 & 自愈配置
# ============================================

risk:
  auto_threshold: 0.4         # < 0.4 自动执行
  semi_auto_threshold: 0.6    # 0.4-0.6 单人审批
  manual_threshold: 0.8       # 0.6-0.8 多人审批
  # >= 0.8 仅诊断

  # 交易系统特殊加权
  critical_services:
    - matching-engine
    - wallet-service
    - settlement-service
    - risk-engine

remediation:
  enabled: false              # 默认关闭，需手动启用
  playbook_dir: "config/playbooks"
  rate_limit:
    per_resource: 3           # 每个资源 1 小时最多 3 次
    per_namespace: 10
    global: 20
    window_minutes: 60

  blacklist:
    namespaces: ["kube-system", "monitoring"]
    deployments: ["matching-engine-core", "wallet-signer"]

# ============================================
# 通知 & 工单配置
# ============================================

notifications:
  slack:
    bot_token: "${SLACK_BOT_TOKEN}"
    channels:
      critical: "#sre-alerts-critical"
      high: "#sre-alerts"
      medium: "#sre-alerts"
      low: "#sre-alerts-low"
    approval_channel: "#sre-approvals"

  pagerduty:
    api_key: "${PAGERDUTY_API_KEY}"
    service_keys:
      critical: "trading-critical-service-key"
      high: "infra-high-service-key"

ticket:
  system: "jira"  # jira / internal
  jira:
    url: "https://company.atlassian.net"
    api_token: "${JIRA_API_TOKEN}"
    project: "SRE"
    issue_type: "Incident"

approval:
  default_timeout_minutes: 15
  escalation_timeout_minutes: 30

# ============================================
# 存储配置
# ============================================

database:
  url: "mysql+asyncmy://${DB_USER}:${DB_PASS}@${DB_HOST}:3306/sre_agent"
  pool_size: 10

redis:
  url: "redis://${REDIS_HOST}:6379/0"
  # Celery broker
  celery_broker_url: "redis://${REDIS_HOST}:6379/1"
```

---

## 五、实施路线图

### Phase 0: 项目初始化 (Week 0)

```
目标: 搭建项目骨架和开发环境

工作项:
  □ 初始化 Git 仓库，配置 CI/CD (GitHub Actions)
  □ 创建项目结构 (src/, tests/, config/, k8s/)
  □ 配置 Python 项目 (pyproject.toml, ruff, mypy, pre-commit)
  □ 编写 Dockerfile 和 docker-compose.yaml (本地开发)
  □ 配置 K8s RBAC 和 ServiceAccount
  □ 部署 Qdrant (dev 环境)

交付物:
  ✓ 可运行的项目骨架
  ✓ 本地开发环境 (docker-compose up)
  ✓ CI pipeline (lint + test + build)
```

### Phase 1: 感知层 + 基础异常检测 (Week 1-3)

```
目标: 能够采集数据并检测基本异常

工作项:
  Week 1:
    □ MetricsCollector: Prometheus/Mimir 查询 (核心指标)
    □ LogsCollector: Loki 查询 (错误日志)
    □ DataNormalizer: 数据标准化
    □ 单元测试

  Week 2:
    □ BaselineEngine: STL 基线学习 (方案A)
    □ AnomalyDetector: Z-Score 基线偏离检测
    □ 异常降噪 (持续时间过滤 + 去重)
    □ 单元测试

  Week 3:
    □ 主循环 (Orchestrator): 每分钟采集 → 检测 → 输出
    □ FastAPI: 健康检查 + 异常查询 API
    □ Slack 通知: 异常检测结果发送到 Slack
    □ 集成测试
    □ 部署到 dev EKS 集群

交付物:
  ✓ Agent 能每分钟检测异常并通知到 Slack
  ✓ Grafana Dashboard: Agent 自身监控
  ✓ 异常检测覆盖核心交易指标
```

### Phase 2: 认知增强 (Week 4-6)

```
目标: 增强分析能力 - 趋势预测 + 根因分析 + 知识库

工作项:
  Week 4:
    □ TrendPredictor: 线性外推 + Holt-Winters (短期预测)
    □ 阈值穿越预测 (预计什么时候达到危险值)
    □ EventsCollector: K8s Events + Kafka 部署事件
    □ 变更时间线追踪

  Week 5:
    □ RCAEngine: 规则引擎 (已知模式匹配)
    □ RCAEngine: LLM 根因分析 (Claude API)
    □ Prompt 设计和优化
    □ RAGKnowledgeBase: Qdrant 写入 + 检索

  Week 6:
    □ AnomalyDetector 增强: MAD 算法
    □ AWSCollector: CloudWatch 指标 + 资源状态
    □ n9e 集成: 读取 n9e 告警状态
    □ 集成测试
    □ 导入历史事件数据到知识库

交付物:
  ✓ Agent 能预测指标趋势并提前预警
  ✓ Agent 能自动进行根因分析
  ✓ Agent 能检索历史相似案例
  ✓ 告警消息包含根因分析和修复建议
```

### Phase 3: 决策 + 执行层 (Week 7-9)

```
目标: 实现完整的决策和自愈闭环

工作项:
  Week 7:
    □ RiskAssessment: 多维度风险评估
    □ ActionPlanner: Playbook 引擎
    □ 编写核心 Playbook (pod-restart, hpa-scale-up)
    □ ApprovalManager: Slack 审批交互

  Week 8:
    □ AutoRemediation: K8s 执行器 (kubectl)
    □ AutoRemediation: 安全机制 (黑名单、频率限制、快照)
    □ TicketManager: Jira 工单集成
    □ AuditLogger: 审计日志写入

  Week 9:
    □ 编写更多 Playbook (rollback, redis, kafka, rds)
    □ 事后报告自动生成
    □ 知识库自动更新
    □ 端到端集成测试
    □ 部署到 staging 环境

交付物:
  ✓ 完整的检测 → 分析 → 决策 → 执行闭环
  ✓ 低风险操作可自动执行
  ✓ 中高风险操作走审批流程
  ✓ 所有操作有审计日志
```

### Phase 4: 加固与优化 (Week 10-11)

```
目标: 提高准确率、降低误报、增强稳定性

工作项:
  Week 10:
    □ 异常检测算法优化 (调参、增加 Isolation Forest)
    □ 趋势预测优化 (增加 Prophet 中期预测)
    □ RCA 准确率评估和 Prompt 优化
    □ 告警降噪优化 (聚合、抑制、静默)
    □ 性能测试和优化

  Week 11:
    □ 混沌测试: 模拟各种故障场景验证 Agent 表现
    □ 安全审计: 权限检查、操作安全验证
    □ 文档完善: 运维手册、Playbook 文档
    □ Grafana Dashboard: 完整的 Agent 效果监控
    □ Runbook 编写: Agent 自身的故障排查手册

交付物:
  ✓ 误报率 < 15% (目标 < 10%)
  ✓ 根因准确率 > 70% (目标 > 80%)
  ✓ 自愈成功率 > 80% (目标 > 85%)
  ✓ 完整的运维文档
```

### Phase 5: 生产上线 (Week 12+)

```
目标: 灰度上线，逐步放开自动化

工作项:
  灰度阶段 (Week 12-13):
    □ 生产环境部署 (只读模式: 检测 + 通知，不执行自愈)
    □ 与现有告警并行运行，对比效果
    □ 收集误报/漏报数据，持续优化
    □ 团队培训

  放开自愈 (Week 14+):
    □ 启用低风险自愈 (Pod 重启、HPA 扩容)
    □ 观察 2 周，确认稳定后
    □ 启用中风险自愈 (需审批)
    □ 持续迭代优化

交付物:
  ✓ 生产环境稳定运行
  ✓ MTTD < 5 分钟
  ✓ MTTR < 30 分钟 (含自愈场景)
  ✓ 凌晨人工告警减少 50%+
```

---

## 六、关键指标看板

### 6.1 Agent 效果指标

```yaml
agent_effectiveness_dashboard:
  # 检测效果
  detection:
    - name: "异常检测数量 (按严重度)"
      query: 'sum(sre_agent_anomalies_detected_total) by (severity)'
    - name: "误报率"
      query: 'sre_agent_false_positive_total / sre_agent_anomalies_detected_total'
    - name: "漏报数 (人工补充的事件)"
      query: 'sre_agent_missed_anomalies_total'
    - name: "MTTD (平均检测时间)"
      query: 'avg(sre_agent_detection_latency_seconds)'

  # 分析效果
  analysis:
    - name: "根因分析准确率"
      query: 'sre_agent_rca_correct_total / sre_agent_rca_total'
    - name: "预测准确率"
      query: 'sre_agent_prediction_correct_total / sre_agent_prediction_total'

  # 自愈效果
  remediation:
    - name: "自愈操作总数"
      query: 'sum(sre_agent_remediation_total) by (playbook, result)'
    - name: "自愈成功率"
      query: 'sre_agent_remediation_success_total / sre_agent_remediation_total'
    - name: "MTTR (平均恢复时间)"
      query: 'avg(sre_agent_mttr_seconds)'
    - name: "审批平均响应时间"
      query: 'avg(sre_agent_approval_response_seconds)'

  # 业务影响
  business:
    - name: "凌晨告警减少量"
      query: 'decrease in alerts during 00:00-08:00 UTC'
    - name: "人工干预减少量"
      query: 'sre_agent_auto_resolved_total / sre_agent_incidents_total'
```

### 6.2 Agent 自身健康指标

```yaml
agent_health_dashboard:
  # 运行状态
  runtime:
    - sre_agent_uptime_seconds
    - sre_agent_leader_election_status
    - sre_agent_monitoring_loop_duration_seconds
    - sre_agent_monitoring_loop_errors_total

  # 数据采集
  collection:
    - sre_agent_collection_success_total{collector}
    - sre_agent_collection_errors_total{collector}
    - sre_agent_collection_duration_seconds{collector}

  # LLM 调用
  llm:
    - sre_agent_llm_requests_total{model, purpose}
    - sre_agent_llm_errors_total{model, error_type}
    - sre_agent_llm_latency_seconds{model}
    - sre_agent_llm_tokens_used_total{model}
    - sre_agent_llm_cost_dollars_total{model}

  # 资源使用
  resources:
    - container_cpu_usage_seconds_total{pod=~"sre-agent.*"}
    - container_memory_working_set_bytes{pod=~"sre-agent.*"}
```

---

## 七、成本估算

### 7.1 基础设施成本

| 组件 | 规格 | 月成本估算 (USD) |
|------|------|-----------------|
| SRE Agent (EKS Pod ×2) | 2 vCPU, 4GB RAM | ~$100 (EC2 share) |
| Celery Worker (EKS Pod ×2) | 1 vCPU, 2GB RAM | ~$50 |
| Qdrant (EKS Pod ×1) | 2 vCPU, 4GB RAM, 20GB EBS | ~$80 |
| Redis (已有 ElastiCache) | 共用现有 | $0 (已有) |
| MySQL (已有 RDS) | 共用现有 | $0 (已有) |
| S3 (知识库备份) | < 1GB | < $1 |
| **基础设施小计** | | **~$230/月** |

### 7.2 AI/API 成本

| 服务 | 用量估算 | 月成本估算 (USD) |
|------|----------|-----------------|
| Claude API (RCA) | ~50 次/天, ~2K tokens/次 | ~$30-80 |
| OpenAI Embedding | ~100 次/天, ~500 tokens/次 | ~$5 |
| **AI 小计** | | **~$35-85/月** |

### 7.3 总计

- **预计月成本**: $265 - $315
- **预计年成本**: $3,180 - $3,780
- **对比**: 一个 SRE 工程师年薪远高于此，Agent 能减少 70% 人工排查时间

---

## 八、风险与缓解

| 风险 | 影响 | 可能性 | 缓解措施 |
|------|------|--------|----------|
| LLM API 不可用 | RCA 降级为规则引擎 | 低 | 本地模型 Fallback + 规则引擎兜底 |
| 误报导致告警疲劳 | 团队忽略 Agent 告警 | 中 | 持续优化阈值 + 误报反馈机制 |
| 自愈操作引入新问题 | 影响交易系统稳定性 | 低 | 灰度启用 + 回滚机制 + 黑名单 |
| 数据源中断 | Agent 无法检测异常 | 低 | 多数据源冗余 + 自身健康监控 |
| 知识库数据质量 | RCA 建议不准确 | 中 | 人工审核机制 + 定期清理 |
| Qdrant 单点故障 | RAG 检索不可用 | 低 | 本地缓存 + 后续升级集群模式 |
