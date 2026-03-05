# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the SRE Agent project - an AI-powered intelligent operations agent system based on the OpenClaw framework. The system transforms traditional reactive alerting into proactive prediction, intelligent diagnosis, and automated remediation for AIOps.

**Current Status**: Active development - core modules implemented with recent feature additions.

## Architecture

The system follows a four-layer architecture:

### 1. Perception Layer (感知层)
- **MetricsCollector**: Collects metrics from Prometheus (QPS, latency, error rates, resource usage)
- **LogsCollector**: Collects structured logs from Loki
- **EventsCollector**: Collects Kubernetes events and configuration changes
- **TraceCollector**: Collects distributed tracing data (optional)

### 2. Cognition Layer (认知层)
- **BaselineEngine**: Learns normal system behavior patterns from historical data
  - Time-series decomposition (STL)
  - Moving averages with standard deviation
  - LSTM time-series prediction
- **AnomalyDetector**: Real-time anomaly detection using multiple algorithms
  - Statistical: 3-Sigma, MAD, IQR
  - ML: Isolation Forest, One-Class SVM, Autoencoder
  - Time-series: ARIMA residual analysis, Prophet, LSTM
- **TrendPredictor**: Predicts metrics 1-6 hours ahead
  - Short-term: ARIMA, Exponential Smoothing
  - Mid-term: Prophet, LSTM, GRU
- **RCAEngine**: Root cause analysis with causal inference
  - Granger Causality for time-series
  - Dependency graph analysis
  - Change correlation analysis
- **RAGKnowledgeBase**: Historical incident knowledge base with vector search
  - Stores past incidents, runbooks, best practices
  - Uses embeddings (text-embedding-3) and vector DB (Qdrant/Milvus)
- **LearningEngine**: Execution feedback and continuous improvement
  - Tracks playbook execution statistics (success rate, duration)
  - Automatic risk score adjustment based on historical performance
  - Stores execution cases in knowledge base for similarity search
  - Extracts lessons learned from failures

### 3. Decision Layer (决策层)
- **RiskAssessment**: Multi-dimensional risk scoring
  - Severity, urgency, impact, complexity
  - Risk score determines automation level
- **ActionPlanner**: Generates remediation action plans
  - AUTO: risk < 0.6 - direct execution
  - SEMI_AUTO: 0.6 ≤ risk < 0.8 - requires approval
  - MANUAL: risk ≥ 0.8 - human intervention
- **ApprovalManager**: Handles approval workflows for sensitive operations

### 4. Action Layer (执行层)
- **AlertManager**: Intelligent alert routing, deduplication, escalation
- **TicketManager**: Integration with ticketing systems
- **AutoRemediation**: Automated fixes
  - Pod restarts, scaling, configuration rollback, version rollback, traffic control
- **AuditLogger**: Complete audit trail of all operations
- **Notifiers**: Multi-channel notification support
  - **WebhookNotifier**: Generic HTTP webhook notifications (Slack, Discord, etc.)
  - **LarkNotifier**: Lark (Feishu) with interactive approval cards
- **Executors**: Multiple execution backends
  - **KubernetesExecutor**: Pod/Deployment level operations
  - **K8sClusterExecutor**: Node-level operations (cordon, drain, uncordon), PVC operations, NetworkPolicy
  - **AnsibleExecutor**: Ansible playbook and role execution
  - **HTTPExecutor**: Custom webhook calls

## Project Structure

```
sre-agent/
├── src/
│   ├── agent/
│   │   ├── orchestrator.py       # Main agent orchestration
│   │   └── prompts.py            # LLM prompts
│   ├── perception/                # Data collection layer
│   │   ├── metrics_collector.py
│   │   ├── logs_collector.py
│   │   ├── events_collector.py
│   │   └── normalizer.py
│   ├── cognition/                 # AI analysis layer
│   │   ├── baseline_engine.py
│   │   ├── anomaly_detector.py
│   │   ├── trend_predictor.py
│   │   ├── rca_engine.py
│   │   ├── knowledge_base.py     # RAG knowledge base
│   │   └── learning_engine.py    # Execution learning (NEW)
│   ├── decision/                  # Decision layer
│   │   ├── risk_assessment.py
│   │   ├── action_planner.py
│   │   └── playbook_engine.py
│   ├── action/                    # Execution layer
│   │   ├── auto_remediation.py
│   │   ├── audit_logger.py
│   │   ├── notification_manager.py
│   │   ├── notifiers/            # Multi-channel notifications (NEW)
│   │   │   ├── base_notifier.py
│   │   │   ├── webhook_notifier.py
│   │   │   └── lark_notifier.py  # Lark with interactive cards
│   │   └── executors/
│   │       ├── k8s_executor.py
│   │       ├── k8s_cluster_executor.py  # Node/PVC/NetworkPolicy (NEW)
│   │       ├── ansible_executor.py      # Ansible playbooks (NEW)
│   │       └── http_executor.py
│   ├── api/                       # REST API
│   │   ├── main.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── anomalies.py
│   │       ├── approvals.py
│   │       └── callbacks.py      # Lark callback handler (NEW)
│   ├── models/                    # Data models
│   │   ├── anomaly.py
│   │   ├── baseline.py
│   │   ├── action_plan.py
│   │   ├── audit.py
│   │   └── playbook_stats.py     # Execution statistics (NEW)
│   └── config/
│       ├── constants.py
│       └── settings.py
├── config/
│   └── config.yaml               # Main configuration
├── tests/                        # Test files
├── requirements.txt              # Python dependencies
└── README.md
```

## Development Commands

**Note**: Implementation not started yet. The following are planned commands:

### Setup
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Running
```bash
# Start the agent
python -m src.agent.sre_agent
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_anomaly_detector.py

# Generate coverage report
pytest --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## Key Design Concepts

### Data Flow
1. **Collection**: Prometheus/Loki/K8s → Collectors → Raw data
2. **Baseline Learning**: Historical data → BaselineEngine → Baseline models (daily background task)
3. **Real-time Monitoring**: Current metrics → AnomalyDetector + Baseline → Anomalies (every minute)
4. **Anomaly Handling**:
   - Anomaly → TrendPredictor → Predictions
   - → RCAEngine → Root cause analysis
   - → RAGKnowledgeBase → Similar cases
   - → RiskAssessment → Risk score
   - → ActionPlanner → Action plan
   - → AlertManager/AutoRemediation → Execution
5. **Feedback Loop**: Results → KnowledgeBase → Model improvement

### Risk-Based Automation
- **Low Risk (< 0.6)**: Auto-execute (e.g., pod restart)
- **Medium Risk (0.6-0.8)**: Require approval (e.g., rollback)
- **High Risk (≥ 0.8)**: Manual intervention (e.g., database operations)

### Safety Mechanisms
- Pre-execution validation and backups
- Operation audit logs
- Automatic rollback on failure
- Rate limiting on operations
- Blacklist protection for critical resources (production databases)

## Configuration

Main configuration in `config/config.yaml` (planned):
- Prometheus/Loki connection details
- Anomaly detection thresholds
- Prediction time horizons
- Risk assessment parameters
- Auto-remediation settings
- Alert routing rules

Environment variables (.env):
- `OPENAI_API_KEY`: For LLM-based root cause analysis
- `SLACK_WEBHOOK_URL`: For alert notifications
- `PAGERDUTY_API_KEY`: For incident management (optional)

## Technology Stack

### Core
- Python 3.11+
- OpenClaw/LangChain/AutoGen (agent framework)
- FastAPI (API service)
- Celery (async tasks)

### Data Storage
- Prometheus (metrics)
- Loki (logs)
- Qdrant/Milvus/Pinecone (vector DB for RAG)
- MySQL (metadata, tickets)
- Redis (cache, queues)

### AI/ML
- scikit-learn (traditional ML)
- Prophet (time-series forecasting)
- TensorFlow/PyTorch (deep learning)
- OpenAI GPT-4 / Claude / Llama 3 (LLM)
- text-embedding-3 (embeddings)

### Infrastructure
- Kubernetes (container orchestration)
- Prometheus + Grafana (monitoring)
- Jaeger/Tempo (tracing, optional)

## Implementation Phases

1. **Phase 1** (Week 1-2): Infrastructure setup, Prometheus/Loki deployment
2. **Phase 2** (Week 3-4): Data collection modules, baseline learning
3. **Phase 3** (Week 5-7): AI analysis engines (anomaly detection, prediction, RCA)
4. **Phase 4** (Week 8-9): Decision and execution layers
5. **Phase 5** (Week 10-11): Testing and optimization
6. **Phase 6** (Week 12+): Production deployment and iteration

## Key Metrics (KPIs)

- **MTTD** (Mean Time To Detect): < 5 minutes
- **MTTI** (Mean Time To Investigate): < 10 minutes
- **MTTR** (Mean Time To Resolve): < 30 minutes
- **Early Warning Lead Time**: 2+ hours average
- **False Positive Rate**: < 10%
- **False Negative Rate**: < 5%
- **Root Cause Accuracy**: > 80%
- **Auto-remediation Success Rate**: > 85%

## Important Notes

### Baseline Learning
- Requires minimum 7 days of historical data (30 days optimal)
- Learning process may take 10-30 minutes
- Updates incrementally daily, full retraining weekly
- Automatically filters out anomalous data from training set

### Anomaly Detection
- Multi-algorithm ensemble approach
- Considers point anomalies, trend anomalies, periodic anomalies, correlation anomalies
- Scoring based on deviation, duration, trend severity, and correlation impact

### Auto-remediation Safety
- Default: auto-remediation disabled
- High-risk operations always require approval
- All operations logged for audit
- Pre-operation backup and post-operation validation
- Automatic rollback on failure

## Adding New Capabilities

### Adding New Metrics
1. Add to `MetricsCollector.CORE_METRICS` dictionary with PromQL query
2. Override `collect_related()` method if special handling needed

### Adding New Anomaly Detection Algorithms
1. Add new method to `AnomalyDetector` class
2. Integrate into `_detect_metric_anomalies()` pipeline

### Adding New Remediation Actions
1. Add new method to `AutoRemediation` class
2. Add routing logic in `_execute_step()` method
3. Ensure proper validation and rollback handling

## Recent Feature Additions

### Lark (飞书) Approval Integration
Interactive approval workflow via Lark cards:
- **Approval Cards**: Rich cards with Approve/Reject buttons
- **Card Updates**: Automatic card update after user action
- **Callback API**: `/api/v1/callbacks/lark` endpoint for Lark callbacks
- **Signature Verification**: Secure callback verification

Configuration:
```yaml
lark:
  enabled: true
  app_id: ${LARK_APP_ID}
  app_secret: ${LARK_APP_SECRET}
  webhook_url: ${LARK_WEBHOOK_URL}
  verification_token: ${LARK_VERIFICATION_TOKEN}
```

### Learning Engine (学习闭环)
Automatic learning from execution outcomes:
- **Playbook Statistics**: Tracks success rate, duration, failure patterns
- **Risk Adjustment**: Automatically suggests risk score adjustments based on historical performance
- **Execution Cases**: Stores cases in knowledge base for similarity search
- **Lessons Learned**: Extracts insights from failures

API Endpoints:
- `GET /api/v1/learning/stats` - Learning engine statistics
- `GET /api/v1/playbooks/stats` - All playbook statistics
- `GET /api/v1/playbooks/stats/{id}` - Specific playbook statistics
- `GET /api/v1/playbooks/executions/{id}` - Playbook execution history

Configuration:
```yaml
learning:
  enabled: true
  min_executions_for_learning: 3
  success_rate_threshold: 0.8
  auto_risk_adjustment: true
  max_risk_reduction: 0.2
```

### New Executors

#### Ansible Executor
Execute Ansible playbooks and roles:
```python
ActionType.ANSIBLE_PLAYBOOK  # Run playbook
ActionType.ANSIBLE_ROLE      # Run role via temp playbook
```

Configuration:
```yaml
ansible:
  enabled: true
  playbooks_dir: /etc/sre-agent/ansible/playbooks
  roles_dir: /etc/sre-agent/ansible/roles
  inventory_file: /etc/sre-agent/ansible/inventory
  timeout_seconds: 600
```

#### K8s Cluster Executor
Node and cluster-level operations:
```python
ActionType.NODE_CORDON           # Mark node unschedulable
ActionType.NODE_DRAIN            # Evict pods and cordon
ActionType.NODE_UNCORDON         # Mark node schedulable
ActionType.PVC_EXPAND            # Expand PVC size
ActionType.PVC_SNAPSHOT          # Create VolumeSnapshot
ActionType.NETWORK_POLICY_APPLY  # Apply NetworkPolicy
ActionType.NETWORK_POLICY_REMOVE # Remove NetworkPolicy
```

Configuration:
```yaml
k8s_cluster:
  drain_timeout_seconds: 300
  drain_grace_period: 30
  ignore_daemonsets: true
```
