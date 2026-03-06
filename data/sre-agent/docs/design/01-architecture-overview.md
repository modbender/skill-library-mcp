# 01 - SRE Agent 总体架构设计

## 文档信息

| 项目 | 内容 |
|------|------|
| 项目名称 | SRE Agent - Crypto Trading AIOps |
| 文档版本 | v2.0 |
| 业务场景 | 加密货币交易系统（7×24h） |
| 基础设施 | AWS EC2 / EKS / ALB / RDS / ElastiCache |
| 可观测性栈 | Prometheus + Mimir, Grafana, n9e, Loki + Promtail, Kafka |
| 最后更新 | 2026-02-09 |

---

## 一、设计背景与目标

### 1.1 现状痛点

加密货币交易系统具有以下特殊性：

- **7×24h 不间断运营**：市场永不休市，任何停机都意味着交易损失
- **极低延迟要求**：撮合引擎延迟需 < 10ms，API 响应需 < 50ms
- **资金安全至上**：钱包、订单、余额的一致性零容忍
- **流量剧烈波动**：行情剧变时 QPS 可瞬间飙升 10-100 倍
- **告警风暴频发**：凌晨告警多、重复告警多、人工排查效率低

### 1.2 核心目标

| 目标 | 描述 | 量化指标 |
|------|------|----------|
| **预防为主** | 提前发现风险，避免转化为故障 | 提前 1-3h 预警，误报率 < 10% |
| **智能诊断** | 自动根因分析，减少人工排查 | 根因准确率 > 80%，MTTI < 10min |
| **工单 & 告警** | 自动生成事件工单、分级告警通知 | 告警降噪 70%+，工单自动创建 |
| **自愈执行** | 低风险自动修复，高风险人工审批 | 自愈成功率 > 85%，MTTR < 30min |

### 1.3 设计原则

1. **安全第一**：交易系统的自动化操作必须有严格的安全边界，涉及资金的操作绝不自动执行
2. **渐进式自动化**：从只读诊断 → 低风险自愈 → 高风险审批执行，分阶段推进
3. **可观测性驱动**：充分利用现有 Prometheus + Mimir / Loki / n9e 技术栈，不重复造轮子
4. **人机协同**：Agent 辅助决策，关键操作由人类审批，而非完全自主
5. **持续学习**：从每次事件处理中积累经验，持续优化检测和诊断能力

---

## 二、总体架构

### 2.1 四层架构全景

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          SRE Agent 控制平面                                   │
│                    (Agent Orchestrator / FastAPI)                             │
│                                                                              │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  感知层      │  │  认知层          │  │  决策层       │  │  执行层       │  │
│  │ Perception  │  │  Cognition      │  │  Decision    │  │  Action      │  │
│  │             │  │                 │  │              │  │              │  │
│  │ • Metrics   │  │ • Baseline      │  │ • Risk       │  │ • Alert      │  │
│  │   Collector │──▶│   Engine       │──▶│   Assessment│──▶│   Manager   │  │
│  │ • Logs      │  │ • Anomaly       │  │ • Action     │  │ • Ticket     │  │
│  │   Collector │  │   Detector     │  │   Planner   │  │   Manager   │  │
│  │ • Events    │  │ • Trend         │  │ • Approval   │  │ • Auto       │  │
│  │   Collector │  │   Predictor    │  │   Manager   │  │   Remediation│  │
│  │ • AWS       │  │ • RCA Engine    │  │              │  │ • Audit      │  │
│  │   Collector │  │ • RAG Knowledge │  │              │  │   Logger    │  │
│  └─────────────┘  └─────────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                   │                  │          │
│         └──────────────────┴───────────────────┴──────────────────┘          │
│                                    │                                         │
│                         ┌──────────▼──────────┐                             │
│                         │    统一数据层        │                             │
│                         │ • Mimir (长期指标)   │                             │
│                         │ • Loki (日志)        │                             │
│                         │ • Redis (缓存/队列)  │                             │
│                         │ • RDS MySQL (元数据) │                             │
│                         │ • Qdrant (向量/RAG)  │                             │
│                         │ • Kafka (事件流)     │                             │
│                         └─────────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 与现有基础设施的集成关系

```
┌─ AWS 基础设施 ──────────────────────────────────────────────────────┐
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  EKS     │  │  EC2     │  │  RDS     │  │  ElastiCache     │   │
│  │ (K8s)    │  │          │  │ (MySQL)  │  │  (Redis)         │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────────────┘   │
│       │              │              │              │                  │
│       ▼              ▼              ▼              ▼                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              可观测性技术栈 (已有)                            │    │
│  │                                                             │    │
│  │  Prometheus ──remote_write──▶ Mimir (S3 长期存储)           │    │
│  │  Promtail ──push──▶ Loki                                   │    │
│  │  Grafana (可视化 Dashboard)                                 │    │
│  │  n9e / 夜莺 (告警规则 & 通知路由)                            │    │
│  │  Kafka (业务事件流 / 交易事件)                               │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              SRE Agent (新增)                                │    │
│  │                                                             │    │
│  │  读取: Prometheus API / Mimir API / Loki API / n9e API     │    │
│  │  读取: K8s API / AWS API (CloudWatch, EC2, RDS, ELB)       │    │
│  │  消费: Kafka (交易事件 / 部署事件)                           │    │
│  │  写入: n9e (告警事件) / Slack / PagerDuty                   │    │
│  │  写入: Jira / 内部工单系统                                   │    │
│  │  执行: kubectl / AWS CLI / Helm (自愈操作)                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 关键设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| Agent 框架 | LangChain / LangGraph | 成熟的 Agent 编排框架，支持 Tool Use 和多步推理 |
| 告警引擎 | 复用 n9e | 已有 n9e 部署，支持 MCP 协议可与 Agent 集成 |
| 长期指标存储 | 复用 Mimir | 已有部署，Prometheus 兼容 API，支持长时间查询 |
| 日志查询 | 复用 Loki | 已有部署，LogQL 查询能力满足根因分析需求 |
| 向量数据库 | Qdrant | 开源、轻量、支持 K8s 部署，适合 RAG 知识库 |
| 事件总线 | 复用 Kafka | 已有部署，用于解耦事件流和异步处理 |
| 审批通道 | Slack + API | 交易团队已用 Slack，支持交互式审批按钮 |
| LLM 选型 | Claude API + 本地 Fallback | Claude 用于根因分析和方案生成，本地模型做降级 |

---

## 三、核心数据流

### 3.1 主循环：实时监控与异常检测

```
Every 60s:
  ┌─────────────────────────┐
  │ 1. 数据采集              │
  │    Prometheus → 核心指标  │
  │    Loki → 错误日志        │
  │    K8s API → Pod 状态     │
  │    AWS API → 资源状态     │
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 2. 异常检测              │
  │    当前值 vs 动态基线     │
  │    多算法集成评分         │
  │    过滤噪声和已知异常     │
  └───────────┬─────────────┘
              ▼
         检测到异常？
          ╱      ╲
        Yes       No → 记录正常状态 → 结束
          │
          ▼
  ┌─────────────────────────┐
  │ 3. 深度分析              │
  │    趋势预测 (将来走势)    │
  │    根因分析 (LLM + 规则)  │
  │    知识库检索 (相似案例)   │
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 4. 风险评估 & 决策       │
  │    计算风险评分           │
  │    确定处理策略:          │
  │    AUTO / SEMI_AUTO /    │
  │    MANUAL / CRITICAL     │
  └───────────┬─────────────┘
              ▼
  ┌─────────────────────────┐
  │ 5. 执行                  │
  │    发送告警通知           │
  │    创建/更新事件工单      │
  │    执行自愈 or 等待审批   │
  │    记录审计日志           │
  └─────────────────────────┘
```

### 3.2 后台任务：基线学习

```
Daily at 03:00 UTC (交易低峰期):
  历史指标 (7-30天) → STL 分解 → 基线模型更新
  历史日志 → 错误模式统计 → 日志基线更新

Weekly:
  全量重训练 → 更新异常检测模型
  知识库增量索引 → 更新 RAG 向量
```

### 3.3 事件驱动流：部署变更追踪

```
Kafka (deploy-events topic):
  ┌──────────────────────────────┐
  │ ArgoCD / Helm / CI-CD        │
  │ 发布部署事件                  │
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐
  │ SRE Agent 消费事件            │
  │ 记录: 什么服务、什么版本、谁部署│
  │ 关联: 后续异常是否与此变更相关  │
  └──────────────────────────────┘
```

---

## 四、组件职责概览

| 层 | 组件 | 职责 | 输入 | 输出 |
|----|------|------|------|------|
| **感知** | MetricsCollector | 采集 Prometheus / Mimir 指标 | PromQL 查询 | 标准化指标数据 |
| **感知** | LogsCollector | 采集 Loki 错误日志 | LogQL 查询 | 结构化日志 |
| **感知** | EventsCollector | 采集 K8s 事件 / 部署事件 | K8s API, Kafka | 事件流 |
| **感知** | AWSCollector | 采集 AWS 资源状态 | CloudWatch, EC2 API | 云资源状态 |
| **认知** | BaselineEngine | 学习正常行为基线 | 历史指标 | 基线模型 |
| **认知** | AnomalyDetector | 检测偏离基线的异常 | 当前指标 + 基线 | 异常事件列表 |
| **认知** | TrendPredictor | 预测未来 1-6h 走势 | 时序数据 | 预测值 + 置信度 |
| **认知** | RCAEngine | 根因分析 | 异常 + 日志 + 事件 | 根因假设 + 证据链 |
| **认知** | RAGKnowledgeBase | 检索历史相似案例 | 异常描述 | 相似案例 + 建议 |
| **决策** | RiskAssessment | 多维度风险评分 | 异常 + 预测 + RCA | 风险等级 + 评分 |
| **决策** | ActionPlanner | 生成修复方案 | 风险评估 + 知识库建议 | 行动计划 |
| **决策** | ApprovalManager | 审批流程管理 | 行动计划 | 审批状态 |
| **执行** | AlertManager | 告警降噪、路由、通知 | 异常事件 | Slack/PagerDuty 通知 |
| **执行** | TicketManager | 创建/更新事件工单 | 异常 + RCA | Jira/内部工单 |
| **执行** | AutoRemediation | 执行自愈操作 | 已审批的行动计划 | 执行结果 |
| **执行** | AuditLogger | 全链路审计记录 | 所有操作 | 审计日志 |

---

## 五、风险等级与自动化策略（交易系统专属）

针对加密货币交易系统，设计 **四级风险分层**：

| 等级 | 风险评分 | 策略 | 示例操作 | 审批要求 |
|------|----------|------|----------|----------|
| **LOW** | < 0.4 | AUTO 自动执行 | Pod 重启、HPA 扩容、缓存清理 | 无需审批，事后通知 |
| **MEDIUM** | 0.4 - 0.6 | SEMI_AUTO 单人审批 | 服务回滚、配置变更回退、限流启用 | 1 名 On-call SRE 审批 |
| **HIGH** | 0.6 - 0.8 | MANUAL 多人审批 | 数据库 Failover、跨 AZ 切换、撮合引擎重启 | 2 名 SRE + 1 名 Tech Lead |
| **CRITICAL** | ≥ 0.8 | BLOCKED 仅诊断 | 钱包操作、交易暂停、资金相关操作 | 禁止自动执行，仅提供诊断报告 |

**铁律**：涉及资金流转的操作（钱包转账、余额调整、订单修正）**永远不进入自动执行**，只提供诊断信息和操作建议。

---

## 六、与业界方案对比

### 6.1 参考的开源项目

| 项目 | 参考点 | 本设计的借鉴 |
|------|--------|-------------|
| **K8sGPT** (CNCF) | K8s 资源状态分析 + LLM 诊断 | 借鉴其 Analyzer 模式，对 K8s 资源状态做规则检查 |
| **Robusta** | Playbook 自愈 + 告警增强 | 借鉴其 YAML Playbook 机制定义自愈操作 |
| **HolmesGPT** (CNCF) | Agentic RCA + 只读安全 | 借鉴其多数据源调查循环和只读设计 |
| **n9e / 夜莺** | 告警管理 + MCP Server | 直接集成，作为告警引擎和 AI 交互桥梁 |

### 6.2 参考的云厂商方案

| 方案 | 参考点 | 本设计的借鉴 |
|------|--------|-------------|
| **AWS DevOps Guru** | 零配置 ML 基线 + Proactive Insights | 借鉴其自动基线学习和预测性洞察的产品思路 |
| **Azure Dynamic Thresholds** | ML 动态阈值替代固定阈值 | 借鉴其动态基线方法，替代 n9e 中的固定阈值规则 |
| **Shoreline.io** | Alarm → Action → Bot 闭环 | 借鉴其闭环自愈架构：检测 → 诊断 → 修复 → 验证 |
| **Kubiya** | 确定性执行 + 知识图谱 | 借鉴其 "确定性执行优于 LLM 直接操作" 的安全理念 |

---

## 七、部署架构

### 7.1 EKS 部署拓扑

```
Namespace: sre-agent
├── Deployment: sre-agent-server (2 replicas, leader election)
│   ├── Container: agent-main (主循环 + API 服务)
│   └── Container: agent-worker (Celery worker, 异步任务)
│
├── Deployment: sre-agent-scheduler (1 replica)
│   └── Container: celery-beat (定时任务调度: 基线学习等)
│
├── StatefulSet: qdrant (1-3 replicas)
│   └── 向量数据库，持久化到 EBS
│
├── ConfigMap: sre-agent-config
│   └── config.yaml, promql-queries.yaml, playbooks.yaml
│
├── Secret: sre-agent-secrets
│   └── LLM API Key, Slack Token, DB 密码
│
├── ServiceAccount: sre-agent
│   └── RBAC: 读取 Pod/Deployment/Event, 执行 rollout/scale
│
└── CronJob: baseline-retrainer (Weekly)
    └── 全量基线重训练
```

### 7.2 高可用设计

- **Leader Election**：使用 K8s Lease 实现，只有 Leader 执行写操作和自愈
- **Follower**：热备，读取数据、更新缓存，随时可接管
- **Celery Worker**：多实例，通过 Redis 做任务队列分发
- **Qdrant**：单节点起步，数据量增长后切换到集群模式
- **Agent 自身监控**：暴露 `/metrics` 端点，接入 Prometheus 自监控

---

## 八、安全设计

### 8.1 权限最小化

```yaml
# SRE Agent 的 K8s RBAC
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: sre-agent-role
rules:
  # 只读权限 (始终允许)
  - apiGroups: [""]
    resources: ["pods", "services", "events", "configmaps", "nodes"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets"]
    verbs: ["get", "list", "watch"]
  # 执行权限 (受审批控制)
  - apiGroups: ["apps"]
    resources: ["deployments/scale", "deployments/rollback"]
    verbs: ["update", "patch"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["delete"]  # 用于 Pod 重启
```

### 8.2 操作安全

- 所有自愈操作前必须创建操作快照（当前状态备份）
- 操作频率限制：同一资源 1 小时内最多操作 3 次
- 操作黑名单：生产 RDS、钱包服务、撮合引擎核心 Pod 禁止自动操作
- 所有操作记录到审计日志（RDS + Kafka），不可篡改
- LLM 调用时脱敏处理：不发送 IP、密码、密钥等敏感信息

---

## 九、文档导航

| 文档 | 内容 |
|------|------|
| [01 - 总体架构](01-architecture-overview.md) | 本文档 |
| [02 - 感知层设计](02-perception-layer.md) | 数据采集层详细设计 |
| [03 - 认知层设计](03-cognition-layer.md) | AI 分析层详细设计 |
| [04 - 决策与执行层设计](04-decision-action-layer.md) | 决策、执行、审批流程设计 |
| [05 - 交易系统专项场景](05-trading-scenarios.md) | 加密货币交易特有的场景和 Playbook |
| [06 - 技术栈与实施路线](06-tech-stack-roadmap.md) | 技术选型细节和分阶段实施计划 |
