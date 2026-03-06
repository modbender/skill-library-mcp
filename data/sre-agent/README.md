# SRE Agent 项目文档

## 目录
- [项目概述](#项目概述)
- [快速开始](#快速开始)
- [架构设计](#架构设计)
- [部署指南](#部署指南)
- [使用手册](#使用手册)
- [开发指南](#开发指南)
- [故障排查](#故障排查)
- [FAQ](#faq)

---

## 项目概述

### 什么是 SRE Agent？

SRE Agent 是一个基于 AI 的智能运维代理系统，旨在将传统的被动告警模式升级为主动预测、智能诊断和自动化治理的新一代 AIOps 平台。

### 核心价值

- **主动预警**：提前 1-3 小时发现潜在风险，而非等到故障发生
- **智能诊断**：自动化根因分析，减少人工排查时间 70%+
- **风险前置**：白天处理风险，减少凌晨告警 80%+
- **自动化治理**：支持自动修复和半自动化运维操作

### 核心功能

1. **多维度数据采集**
   - 指标采集（Prometheus）
   - 日志采集（Loki）
   - 事件采集（Kubernetes Events）
   - 链路追踪（可选）

2. **AI 驱动分析**
   - 基线学习：自动学习系统正常行为模式
   - 异常检测：多算法检测异常（统计、时序、机器学习）
   - 趋势预测：预测未来 1-6 小时的指标走势
   - 根因分析：基于 LLM 的智能根因分析
   - 知识库：RAG 技术支持的历史案例检索

3. **智能决策**
   - 风险评估：多维度评估风险等级
   - 行动规划：自动生成修复方案
   - 审批流程：关键操作需人工审批

4. **自动化执行**
   - 告警管理：智能降噪、路由、升级
   - 自动修复：支持重启、扩缩容、回滚等操作
   - 审计日志：完整的操作记录

---

## 快速开始

### 前置要求

- Python 3.11+
- Kubernetes 集群（可选，用于自动修复）
- Prometheus（指标数据源）
- Loki（日志数据源，可选）
- OpenAI API Key 或本地 LLM（用于根因分析）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/sre-agent.git
cd sre-agent
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Alert Configuration
SLACK_WEBHOOK_URL=your_slack_webhook_url
ALERT_FROM_EMAIL=sre-agent@example.com

# PagerDuty (可选)
PAGERDUTY_API_KEY=your_pagerduty_key
```

#### 5. 修改配置文件

编辑 `config/config.yaml`，配置 Prometheus 和 Loki 地址：

```yaml
prometheus:
  url: "http://your-prometheus:9090"

loki:
  url: "http://your-loki:3100"
```

#### 6. 启动 Agent

```bash
python -m src.agent.sre_agent
```

### 验证安装

访问 Agent 状态接口（如果启动了 API 服务）：

```bash
curl http://localhost:8000/status
```

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        SRE Agent 控制平面                        │
│                     (基于 OpenClaw 框架)                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────────┐
        │               │                   │
        ▼               ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  数据采集层   │  │  AI 分析层    │  │  执行治理层   │
│               │  │               │  │               │
│ • Prometheus  │  │ • 基线学习    │  │ • 工单系统    │
│ • Loki        │  │ • 异常检测    │  │ • Runbook     │
│ • K8s Events  │  │ • 趋势预测    │  │ • 自动修复    │
│ • Traces      │  │ • 根因分析    │  │ • 审批流程    │
│ • Cloud APIs  │  │ • RAG 知识库  │  │ • 回滚机制    │
└───────────────┘  └───────────────┘  └───────────────┘
```

### 四层架构详解

#### 1. 感知层（Perception Layer）

**职责**：从多个数据源采集系统运行数据

**组件**：
- `MetricsCollector`：采集 Prometheus 指标
- `LogsCollector`：采集 Loki 日志
- `EventsCollector`：采集 Kubernetes 事件

**数据流**：
```
Prometheus → MetricsCollector → 标准化指标数据
Loki → LogsCollector → 结构化日志数据
K8s API → EventsCollector → 事件数据
```

#### 2. 认知层（Cognition Layer）

**职责**：分析数据，识别异常，预测趋势，定位根因

**组件**：
- `BaselineEngine`：学习正常行为基线
- `AnomalyDetector`：检测异常
- `TrendPredictor`：预测未来趋势
- `RCAEngine`：根因分析
- `RAGKnowledgeBase`：知识库检索

**算法**：
- 统计方法：3-Sigma、MAD、IQR
- 时序方法：ARIMA、Prophet、LSTM
- 机器学习：Isolation Forest、One-Class SVM

#### 3. 决策层（Decision Layer）

**职责**：评估风险，规划行动方案

**组件**：
- `RiskAssessment`：风险评估
- `ActionPlanner`：行动规划

**决策逻辑**：
```
风险评分 < 0.6  → 自动处理（AUTO）
0.6 ≤ 风险评分 < 0.8 → 半自动（SEMI_AUTO，需审批）
风险评分 ≥ 0.8 → 人工处理（MANUAL）
```

#### 4. 执行层（Action Layer）

**职责**：执行修复操作，发送告警

**组件**：
- `AlertManager`：告警管理
- `AutoRemediation`：自动修复

**能力**：
- 重启 Pod
- 扩缩容
- 配置回滚
- 版本回滚
- 流量控制

### 数据流转

```
1. 数据采集
   Prometheus/Loki/K8s → Collectors → 原始数据

2. 基线学习（后台任务，每日执行）
   历史数据 → BaselineEngine → 基线模型

3. 实时监控（主循环，每分钟执行）
   当前指标 → AnomalyDetector + Baseline → 异常列表

4. 异常处理
   异常 → TrendPredictor → 预测结果
        → RCAEngine → 根因分析
        → RAGKnowledgeBase → 相似案例
        → RiskAssessment → 风险评估
        → ActionPlanner → 行动计划
        → AlertManager/AutoRemediation → 执行

5. 反馈学习
   处理结果 → KnowledgeBase → 更新知识库
```

---

## 部署指南

### 部署架构

#### 单机部署（开发/测试）

```
┌─────────────────────────────────────┐
│         单台服务器                   │
│                                     │
│  ┌──────────────┐                  │
│  │  SRE Agent   │                  │
│  └──────┬───────┘                  │
│         │                           │
│  ┌──────▼───────┐  ┌────────────┐ │
│  │ Prometheus   │  │   Loki     │ │
│  └──────────────┘  └────────────┘ │
│                                     │
│  ┌──────────────┐  ┌────────────┐ │
│  │  Vector DB   │  │   Redis    │ │
│  └──────────────┘  └────────────┘ │
└─────────────────────────────────────┘
```

**步骤**：

1. 安装 Docker 和 Docker Compose
2. 使用提供的 `docker-compose.yml`
3. 启动所有服务：`docker-compose up -d`

#### Kubernetes 部署（生产）

```
┌─────────────────────────────────────────────────┐
│              Kubernetes 集群                     │
│                                                  │
│  ┌────────────────────────────────────────┐    │
│  │         SRE Agent Deployment           │    │
│  │  ┌──────────┐  ┌──────────┐           │    │
│  │  │ Agent-1  │  │ Agent-2  │  (HA)     │    │
│  │  └──────────┘  └──────────┘           │    │
│  └────────────────────────────────────────┘    │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ Prometheus   │  │    Loki      │           │
│  │  (已有)      │  │   (已有)     │           │
│  └──────────────┘  └──────────────┘           │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Qdrant      │  │    Redis     │           │
│  │ (Vector DB)  │  │   (Cache)    │           │
│  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────┘
```

**步骤**：

1. 创建 Namespace：
```bash
kubectl create namespace sre-agent
```

2. 创建 ConfigMap：
```bash
kubectl create configmap sre-agent-config \
  --from-file=config/config.yaml \
  -n sre-agent
```

3. 创建 Secret：
```bash
kubectl create secret generic sre-agent-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=slack-webhook=$SLACK_WEBHOOK_URL \
  -n sre-agent
```

4. 部署 Agent：
```bash
kubectl apply -f k8s/deployment.yaml
```

5. 验证部署：
```bash
kubectl get pods -n sre-agent
kubectl logs -f deployment/sre-agent -n sre-agent
```

### 高可用配置

#### 1. Agent 高可用

- 部署多个 Agent 实例（建议 2-3 个）
- 使用 Leader Election 机制（只有一个 Leader 执行操作）
- 使用 Redis 作为分布式锁

#### 2. 数据存储高可用

- Prometheus：使用 Thanos 或 VictoriaMetrics 集群
- Vector DB：Qdrant 集群模式
- Redis：Redis Sentinel 或 Redis Cluster

#### 3. 监控 Agent 自身

- 暴露 Prometheus metrics
- 配置健康检查
- 设置告警规则

---

## 使用手册

### 基本使用流程

#### 1. 首次启动 - 基线学习

Agent 首次启动后，会自动进行基线学习：

```
[INFO] Starting baseline learning...
[INFO] Collecting 7 days of historical metrics...
[INFO] Learned baseline for cpu_usage from 10080 points
[INFO] Learned baseline for memory_usage from 10080 points
[INFO] Baseline learning completed for 15 metrics
```

**注意**：
- 基线学习需要至少 7 天的历史数据
- 学习过程可能需要 10-30 分钟
- 学习完成前，异常检测准确率较低

#### 2. 日常监控

Agent 会每分钟执行一次监控循环：

```
[INFO] Starting monitoring loop...
[DEBUG] Collecting all core metrics...
[DEBUG] Collected 15 metrics
[INFO] Detected 2 anomalies
[INFO] Handling anomaly: memory_usage_percent
```

#### 3. 异常处理流程

当检测到异常时，Agent 会自动执行以下流程：

```
异常检测 → 趋势预测 → 根因分析 → 风险评估 → 生成方案 → 执行/通知
```

**示例输出**：

```
[INFO] Anomaly detected:
  Metric: memory_usage_percent
  Current: 75%
  Expected: 50%
  Deviation: +50%
  Severity: HIGH

[INFO] Trend prediction:
  Estimated breach time: 2.5 hours
  Risk level: HIGH

[INFO] Root cause analysis:
  Cause: Memory leak in service-x (confidence: 0.89)
  Evidence: 
    - Memory continuously growing
    - No corresponding traffic increase
    - Recent deployment v2.3.1

[INFO] Action plan generated:
  Strategy: SEMI_AUTO (requires approval)
  Recommended: Rollback to v2.3.0

[INFO] Approval request sent to Slack
```

#### 4. 审批操作

对于需要审批的操作，SRE 会收到通知：

**Slack 消息示例**：
```
🚨 SRE Agent Alert

Severity: HIGH
Service: service-x
Metric: memory_usage_percent

Current Value: 75%
Expected Value: 50%
Deviation: +50%

Recommended Action: Rollback to v2.3.0
Estimated Time: 5 minutes
Success Rate: 95% (based on 8 similar cases)

⚠️ APPROVAL REQUIRED
Plan ID: PLAN-20260206143022

Reply with: APPROVE or REJECT
```

**审批方式**：
1. Slack 回复：`APPROVE PLAN-20260206143022`
2. API 调用：`POST /api/approvals/PLAN-20260206143022/approve`
3. Web UI：点击审批按钮

#### 5. 自动执行

审批通过后，Agent 自动执行修复操作：

```
[INFO] Approval received for PLAN-20260206143022
[INFO] Executing action plan...
[INFO] Step 1: Create incident ticket - DONE
[INFO] Step 2: Backup current configuration - DONE
[INFO] Step 3: Rollback deployment to v2.3.0 - IN PROGRESS
[INFO] Step 4: Verify service health - IN PROGRESS
[INFO] All steps completed successfully
[INFO] Sending completion notification
```

### 常用操作

#### 查看 Agent 状态

```bash
# 通过 API
curl http://localhost:8000/status

# 通过日志
tail -f logs/sre-agent.log
```

#### 手动触发基线学习

```bash
curl -X POST http://localhost:8000/api/baseline/learn
```

#### 查看当前基线

```bash
curl http://localhost:8000/api/baseline/metrics
```

#### 查看检测到的异常

```bash
curl http://localhost:8000/api/anomalies?hours=24
```

#### 查看待审批的操作

```bash
curl http://localhost:8000/api/approvals/pending
```

#### 审批操作

```bash
# 批准
curl -X POST http://localhost:8000/api/approvals/{plan_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approver": "john@example.com"}'

# 拒绝
curl -X POST http://localhost:8000/api/approvals/{plan_id}/reject \
  -H "Content-Type: application/json" \
  -d '{"approver": "john@example.com", "reason": "Need more investigation"}'
```

### 配置调优

#### 调整异常检测灵敏度

编辑 `config/config.yaml`：

```yaml
anomaly_detection:
  threshold: 0.7  # 降低到 0.6 会更敏感，提高到 0.8 会更保守
```

#### 调整预测时间窗口

```yaml
prediction:
  horizon_hours: 6  # 可以调整为 3-12 小时
```

#### 启用自动修复

```yaml
risk:
  auto_remediation_enabled: true  # 谨慎启用！
  approval_threshold: 0.8  # 只有低风险操作才自动执行
```

---

## 开发指南

### 项目结构

```
sre-agent/
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   └── sre_agent.py          # 主 Agent 逻辑
│   ├── perception/                # 感知层
│   │   ├── metrics_collector.py
│   │   ├── logs_collector.py
│   │   └── events_collector.py
│   ├── cognition/                 # 认知层
│   │   ├── baseline_engine.py
│   │   ├── anomaly_detector.py
│   │   ├── trend_predictor.py
│   │   ├── rca_engine.py
│   │   └── rag_knowledge_base.py
│   ├── decision/                  # 决策层
│   │   ├── risk_assessment.py
│   │   └── action_planner.py
│   └── action/                    # 执行层
│       ├── alert_manager.py
│       └── auto_remediation.py
├── config/
│   └── config.yaml               # 配置文件
├── tests/                        # 测试
├── docs/                         # 文档
├── requirements.txt              # 依赖
└── README.md
```

### 添加新的指标采集

1. 在 `MetricsCollector.CORE_METRICS` 中添加新指标：

```python
CORE_METRICS = {
    'your_new_metric': 'your_promql_query',
}
```

2. 如果需要特殊处理，重写 `collect_related` 方法

### 添加新的异常检测算法

1. 在 `AnomalyDetector` 中添加新方法：

```python
def _detect_your_algorithm(self, ...):
    # 实现你的算法
    pass
```

2. 在 `_detect_metric_anomalies` 中调用

### 添加新的修复操作

1. 在 `AutoRemediation` 中添加新方法：

```python
async def _your_remediation_action(self, action_plan):
    # 实现修复逻辑
    pass
```

2. 在 `_execute_step` 中添加路由逻辑

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_anomaly_detector.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 代码规范

- 使用 Black 格式化代码：`black src/`
- 使用 Flake8 检查代码：`flake8 src/`
- 使用 MyPy 类型检查：`mypy src/`

---

## 故障排查

### 常见问题

#### 1. Agent 无法连接 Prometheus

**症状**：
```
[ERROR] Error querying Prometheus: Connection refused
```

**解决方案**：
- 检查 Prometheus 地址配置
- 确认 Prometheus 服务正常运行
- 检查网络连接和防火墙规则

#### 2. 基线学习失败

**症状**：
```
[WARNING] No data for cpu_usage, skipping
[ERROR] Error learning baseline: insufficient data
```

**解决方案**：
- 确认 Prometheus 中有足够的历史数据（至少 7 天）
- 检查指标名称是否正确
- 降低 `baseline.learning_days` 配置

#### 3. LLM 调用失败

**症状**：
```
[ERROR] Error calling LLM: Authentication failed
```

**解决方案**：
- 检查 `OPENAI_API_KEY` 环境变量
- 确认 API Key 有效且有足够额度
- 考虑使用本地 LLM 作为备选

#### 4. 内存占用过高

**症状**：
Agent 进程内存持续增长

**解决方案**：
- 减少 `baseline.learning_days`
- 降低 `check_interval_seconds`
- 限制历史数据缓存大小
- 定期重启 Agent

#### 5. 告警风暴

**症状**：
短时间内收到大量告警

**解决方案**：
- 提高 `anomaly_detection.threshold`
- 启用告警聚合功能
- 配置告警抑制规则
- 检查是否有系统性问题

### 调试技巧

#### 启用 DEBUG 日志

```yaml
logging:
  level: "DEBUG"
```

#### 查看详细的异常信息

```bash
tail -f logs/sre-agent.log | grep -A 10 "ERROR"
```

#### 测试单个组件

```python
# 测试指标采集
from src.perception.metrics_collector import MetricsCollector
collector = MetricsCollector("http://localhost:9090")
metrics = await collector.collect_all()
print(metrics)
```

---

## FAQ

### Q1: SRE Agent 与传统监控告警的区别？

**传统监控**：
- 基于固定阈值（CPU > 80%）
- 被动响应，问题发生后才告警
- 单点指标，缺乏关联分析
- 需要人工排查根因

**SRE Agent**：
- 基于动态基线和趋势预测
- 主动预警，提前 1-3 小时发现风险
- 多维度关联分析（指标+日志+事件）
- AI 自动根因分析和修复建议

### Q2: 需要多少历史数据才能开始使用？

- **最少**：3 天（基本可用，但准确率较低）
- **推荐**：7 天（准确率较好）
- **最佳**：30 天（包含完整的周期性模式）

### Q3: 支持哪些数据源？

**当前支持**：
- Prometheus（指标）
- Loki（日志）
- Kubernetes Events

**计划支持**：
- Elasticsearch（日志）
- Jaeger/Tempo（链路追踪）
- AWS CloudWatch
- Azure Monitor
- 自定义数据源

### Q4: 自动修复安全吗？

**安全机制**：
1. 默认关闭自动修复，需手动启用
2. 高风险操作必须人工审批
3. 所有操作都有审计日志
4. 支持操作前备份和失败回滚
5. 可配置黑名单（如生产数据库）

**建议**：
- 先在测试环境验证
- 从低风险操作开始（如重启 Pod）
- 逐步扩大自动化范围
- 定期审查操作日志

### Q5: 如何评估 Agent 的效果？

**关键指标**：
1. **MTTD**（Mean Time To Detect）：平均检测时间
2. **MTTI**（Mean Time To Investigate）：平均调查时间
3. **MTTR**（Mean Time To Resolve）：平均恢复时间
4. **预警准确率**：真实问题 / 总告警数
5. **自动修复成功率**：成功修复 / 总修复尝试

**对比基准**：
- 传统监控：MTTD ~30min, MTTR ~2h
- SRE Agent 目标：MTTD <5min, MTTR <30min

### Q6: 成本如何？

**主要成本**：
1. **LLM API 调用**：
   - 每次根因分析 ~$0.01-0.05
   - 预计每天 10-50 次分析
   - 月成本：$10-100

2. **基础设施**：
   - Agent 服务器：2-4 核 CPU, 4-8GB 内存
   - Vector DB：根据知识库大小
   - 总计：$50-200/月

3. **人力成本节省**：
   - 减少 70% 人工排查时间
   - 减少 80% 凌晨告警
   - ROI 通常在 3-6 个月

### Q7: 如何贡献代码？

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交代码：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

**贡献指南**：
- 遵循代码规范
- 添加单元测试
- 更新文档
- 通过 CI 检查

---

## 联系我们

- **GitHub Issues**: https://github.com/your-org/sre-agent/issues
- **Slack**: #sre-agent
- **Email**: sre-team@example.com

---

## 许可证

MIT License

Copyright (c) 2026 SRE Team

---

**最后更新**: 2026-02-06
