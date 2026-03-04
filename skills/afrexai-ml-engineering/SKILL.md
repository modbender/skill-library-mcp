# ML & AI Engineering System

Complete methodology for building, deploying, and operating production ML/AI systems — from experiment to scale.

---

## Phase 1: Problem Framing

Before writing any code, define the ML problem precisely.

### ML Problem Brief

```yaml
problem_brief:
  business_objective: ""          # What business metric improves?
  success_metric: ""              # Quantified target (e.g., "reduce churn 15%")
  baseline: ""                    # Current performance without ML
  ml_task_type: ""                # classification | regression | ranking | generation | clustering | anomaly_detection | recommendation
  prediction_target: ""           # What exactly are we predicting?
  prediction_consumer: ""         # Who/what uses the prediction? (API | dashboard | email | automated action)
  latency_requirement: ""         # real-time (<100ms) | near-real-time (<1s) | batch (minutes-hours)
  data_available: ""              # What data exists today?
  data_gaps: ""                   # What's missing?
  ethical_considerations: ""      # Bias risks, fairness requirements, privacy
  kill_criteria:                  # When to abandon the ML approach
    - "Baseline heuristic achieves >90% of ML performance"
    - "Data quality too poor after 2 weeks of cleaning"
    - "Model can't beat random by >10% on holdout set"
```

### ML vs Rules Decision

| Signal | Use Rules | Use ML |
|--------|-----------|--------|
| Logic is explainable in <10 rules | ✅ | ❌ |
| Pattern is too complex for humans | ❌ | ✅ |
| Training data >1,000 labeled examples | — | ✅ |
| Needs to adapt to new patterns | ❌ | ✅ |
| Must be 100% auditable/deterministic | ✅ | ❌ |
| Pattern changes faster than you can update rules | ❌ | ✅ |

**Rule of thumb:** Start with rules/heuristics. Only add ML when rules fail to capture the pattern.

---

## Phase 2: Data Engineering for ML

### Data Quality Assessment

Score each data source (0-5 per dimension):

| Dimension | 0 (Terrible) | 5 (Excellent) |
|-----------|--------------|----------------|
| **Completeness** | >50% missing | <1% missing |
| **Accuracy** | Known errors, no validation | Validated against source of truth |
| **Consistency** | Different formats, duplicates | Standardized, deduplicated |
| **Timeliness** | Months stale | Real-time or daily refresh |
| **Relevance** | Weak proxy for target | Direct signal for prediction |
| **Volume** | <100 samples | >10,000 samples per class |

**Minimum score to proceed:** 18/30. Below 18 → fix data first, don't build models.

### Feature Engineering Patterns

```yaml
feature_types:
  numerical:
    - raw_value           # Use as-is if normally distributed
    - log_transform       # Right-skewed distributions (revenue, counts)
    - standardize         # z-score for algorithms sensitive to scale (SVM, KNN, neural nets)
    - bin_to_categorical  # When relationship is non-linear and data is limited
  categorical:
    - one_hot             # <20 categories, tree-based models handle natively
    - target_encoding     # High-cardinality (>20 categories), use with K-fold to prevent leakage
    - embedding           # Very high-cardinality (user IDs, product IDs) with deep learning
  temporal:
    - lag_features        # Value at t-1, t-7, t-30
    - rolling_statistics  # Mean, std, min, max over windows
    - time_since_event    # Days since last purchase, hours since login
    - cyclical_encoding   # sin/cos for hour-of-day, day-of-week, month
  text:
    - tfidf               # Simple, interpretable, good baseline
    - sentence_embeddings # semantic similarity, modern NLP
    - llm_extraction      # Use LLM to extract structured fields from unstructured text
  interaction:
    - ratios              # Feature A / Feature B (e.g., clicks/impressions = CTR)
    - differences         # Feature A - Feature B (e.g., price - competitor_price)
    - polynomial          # A * B, A^2 (use sparingly, high-cardinality features)
```

### Feature Store Design

```yaml
feature_store:
  offline_store:         # For training — batch computed, stored in data warehouse
    storage: "BigQuery | Snowflake | S3+Parquet"
    compute: "Spark | dbt | SQL"
    refresh: "daily | hourly"
  online_store:          # For serving — low-latency lookups
    storage: "Redis | DynamoDB | Feast online"
    latency_target: "<10ms p99"
    refresh: "streaming | near-real-time"
  registry:              # Feature metadata
    naming: "{entity}_{feature_name}_{window}_{aggregation}"  # e.g., user_purchase_count_30d_sum
    documentation:
      - description
      - data_type
      - source_table
      - owner
      - created_date
      - known_issues
```

### Data Leakage Prevention Checklist

- [ ] No future information in features (time-travel check)
- [ ] Train/val/test split done BEFORE feature engineering
- [ ] Target encoding uses only training fold statistics
- [ ] No features derived from the target variable
- [ ] Temporal splits for time-series (no random shuffle)
- [ ] Holdout set created BEFORE any EDA
- [ ] Duplicates removed BEFORE splitting (same entity not in train AND test)
- [ ] Normalization/scaling fit on train, applied to val/test

---

## Phase 3: Experiment Management

### Experiment Tracking Template

```yaml
experiment:
  id: "EXP-{YYYY-MM-DD}-{NNN}"
  hypothesis: ""                 # "Adding user tenure features will improve churn prediction AUC by >2%"
  dataset_version: ""            # Hash or version of training data
  features_used: []              # List of feature names
  model_type: ""                 # Algorithm name
  hyperparameters: {}            # All hyperparams logged
  training_time: ""              # Wall clock
  metrics:
    primary: {}                  # The one metric that matters
    secondary: {}                # Supporting metrics
  baseline_comparison: ""        # Delta vs baseline
  verdict: "promoted | archived | iterate"
  notes: ""
  artifacts:
    - model_path: ""
    - notebook_path: ""
    - confusion_matrix: ""
```

### Model Selection Guide

| Task | Start With | Scale To | Avoid |
|------|-----------|----------|-------|
| Tabular classification | XGBoost/LightGBM | Neural nets only if >100K samples | Deep learning on <10K samples |
| Tabular regression | XGBoost/LightGBM | CatBoost for high-cardinality cats | Linear regression without feature engineering |
| Image classification | Fine-tune ResNet/EfficientNet | Vision Transformer if >100K images | Training from scratch |
| Text classification | Fine-tune BERT/RoBERTa | LLM few-shot if labeled data scarce | Bag-of-words for nuanced tasks |
| Text generation | GPT-4/Claude API | Fine-tuned Llama/Mistral for cost | Training from scratch |
| Time series | Prophet/ARIMA baseline → LightGBM | Temporal Fusion Transformer | LSTM without strong reason |
| Recommendation | Collaborative filtering baseline | Two-tower neural | Complex models on <1K users |
| Anomaly detection | Isolation Forest | Autoencoder if high-dimensional | Supervised methods without labeled anomalies |
| Search/ranking | BM25 baseline → Learning to Rank | Cross-encoder reranking | Pure keyword without semantic |

### Hyperparameter Tuning Strategy

1. **Manual first** — understand 3-5 most impactful parameters
2. **Bayesian optimization** (Optuna) — 50-100 trials for production models
3. **Grid search** — only for final fine-tuning of 2-3 parameters
4. **Random search** — better than grid for >4 parameters

**Key hyperparameters by model:**

| Model | Critical Params | Typical Range |
|-------|----------------|---------------|
| XGBoost | learning_rate, max_depth, n_estimators, min_child_weight | 0.01-0.3, 3-10, 100-1000, 1-10 |
| LightGBM | learning_rate, num_leaves, feature_fraction, min_data_in_leaf | 0.01-0.3, 15-255, 0.5-1.0, 5-100 |
| Neural Net | learning_rate, batch_size, hidden_dims, dropout | 1e-5 to 1e-2, 32-512, arch-dependent, 0.1-0.5 |
| Random Forest | n_estimators, max_depth, min_samples_leaf | 100-1000, 5-30, 1-20 |

---

## Phase 4: Model Evaluation

### Metric Selection by Task

| Task | Primary Metric | When to Use | Watch Out For |
|------|---------------|-------------|---------------|
| Binary classification (balanced) | F1-score | Equal importance of precision/recall | — |
| Binary classification (imbalanced) | PR-AUC | Rare positive class (<5%) | ROC-AUC hides poor performance on minority |
| Multi-class | Macro F1 | All classes equally important | Micro F1 if class frequency = importance |
| Regression | MAE | Outliers should not dominate | RMSE penalizes large errors more |
| Ranking | NDCG@K | Top-K results matter most | MAP if binary relevance |
| Generation | Human eval + automated | Quality is subjective | BLEU/ROUGE alone are insufficient |
| Anomaly detection | Precision@K | False positives are expensive | Recall if missing anomalies is dangerous |

### Evaluation Rigor Checklist

- [ ] Metrics computed on TRUE holdout (never seen during training OR tuning)
- [ ] Cross-validation for small datasets (<10K samples)
- [ ] Stratified splits for imbalanced classes
- [ ] Temporal split for time-dependent data
- [ ] Confidence intervals reported (bootstrap or cross-val)
- [ ] Performance broken down by important segments (geography, user cohort, etc.)
- [ ] Fairness metrics across protected groups
- [ ] Comparison against simple baseline (majority class, mean prediction, rules)
- [ ] Error analysis: examined top 50 worst predictions manually
- [ ] Calibration plot for probabilistic predictions

### Offline-to-Online Gap Analysis

Before deploying, verify these don't cause train-serving skew:

| Check | Offline | Online | Action |
|-------|---------|--------|--------|
| Feature computation | Batch SQL | Real-time API | Verify same logic, test with replay |
| Data freshness | Point-in-time snapshot | Latest value | Document acceptable staleness |
| Missing values | Imputed in pipeline | May be truly missing | Handle gracefully in serving |
| Feature distributions | Training period | Current period | Monitor drift post-deploy |

---

## Phase 5: Model Deployment

### Deployment Pattern Decision Tree

```
Is latency < 100ms required?
├── Yes → Is model < 500MB?
│   ├── Yes → Embedded serving (FastAPI + model in memory)
│   └── No → Model server (Triton, TorchServe, vLLM)
└── No → Is it a batch prediction?
    ├── Yes → Batch pipeline (Spark, Airflow + offline inference)
    └── No → Async queue (Celery/SQS → worker → result store)
```

### Production Serving Checklist

```yaml
serving_config:
  model:
    format: ""                    # ONNX | TorchScript | SavedModel | safetensors
    version: ""                   # Semantic version
    size_mb: null
    load_time_seconds: null
  infrastructure:
    compute: ""                   # CPU | GPU (T4/A10/A100/H100)
    instances: null               # Min/max for autoscaling
    autoscale_metric: ""          # RPS | latency_p99 | GPU_utilization
    autoscale_target: null
  api:
    endpoint: ""
    input_schema: {}              # Pydantic model or JSON schema
    output_schema: {}
    timeout_ms: null
    rate_limit: null
  reliability:
    health_check: "/health"
    readiness_check: "/ready"     # Model loaded and warm
    graceful_shutdown: true
    circuit_breaker: true
    fallback: ""                  # Rules-based fallback when model is down
```

### Containerization Template

```dockerfile
# Multi-stage build for minimal image
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY model/ ./model/
COPY src/ ./src/

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080"]
```

### A/B Testing for Models

```yaml
ab_test:
  name: ""
  hypothesis: ""
  primary_metric: ""              # Business metric (revenue, engagement, etc.)
  guardrail_metrics: []           # Metrics that must NOT degrade
  traffic_split:
    control: 50                   # Current model
    treatment: 50                 # New model
  minimum_sample_size: null       # Power analysis: use statsmodels or online calculator
  minimum_runtime_days: null      # At least 1 full business cycle (7 days min)
  decision_criteria:
    ship: "Treatment > control by >X% with p<0.05 AND no guardrail regression"
    iterate: "Promising signal but not significant — extend test or refine model"
    kill: "No improvement after 2x minimum runtime OR guardrail breach"
```

---

## Phase 6: LLM Engineering

### LLM Application Architecture

```
┌─────────────────────────────────────────────┐
│              Application Layer               │
│  (Prompt templates, chains, output parsers)  │
├─────────────────────────────────────────────┤
│              Orchestration Layer              │
│  (Routing, fallback, retry, caching)         │
├─────────────────────────────────────────────┤
│              Model Layer                     │
│  (API calls, fine-tuned models, embeddings)  │
├─────────────────────────────────────────────┤
│              Data Layer                      │
│  (Vector store, context retrieval, memory)   │
└─────────────────────────────────────────────┘
```

### Model Selection for LLM Tasks

| Task | Best Option | Cost-Effective Option | When to Fine-Tune |
|------|------------|----------------------|-------------------|
| General reasoning | Claude Opus / GPT-4o | Claude Sonnet / GPT-4o-mini | Never for general reasoning |
| Classification | Fine-tuned small model | Few-shot with Sonnet | >1,000 labeled examples + high volume |
| Extraction | Structured output API | Regex + LLM fallback | Consistent format needed at scale |
| Summarization | Claude Sonnet | GPT-4o-mini | Domain-specific style needed |
| Code generation | Claude Sonnet | Codestral / DeepSeek | Internal codebase conventions |
| Embeddings | text-embedding-3-large | text-embedding-3-small | Domain-specific vocab (medical, legal) |

### RAG System Architecture

```yaml
rag_pipeline:
  ingestion:
    chunking:
      strategy: "semantic"         # semantic | fixed_size | recursive
      chunk_size: 512              # tokens (512-1024 for most use cases)
      overlap: 50                  # tokens overlap between chunks
      metadata_to_preserve:
        - source_document
        - page_number
        - section_heading
        - date_created
    embedding:
      model: "text-embedding-3-large"
      dimensions: 1536             # Or 256/512 with Matryoshka for cost savings
    vector_store: "Pinecone | Weaviate | pgvector | Qdrant"
  retrieval:
    strategy: "hybrid"             # dense | sparse | hybrid (recommended)
    top_k: 10                      # Retrieve more, then rerank
    reranking:
      model: "Cohere rerank | cross-encoder"
      top_n: 3                     # Final context chunks
    filters: []                    # Metadata filters (date range, source, etc.)
  generation:
    model: ""
    system_prompt: |
      Answer based ONLY on the provided context.
      If the context doesn't contain the answer, say "I don't have enough information."
      Cite sources using [Source: document_name, page X].
    temperature: 0.1               # Low for factual, higher for creative
    max_tokens: null
```

### RAG Quality Checklist

- [ ] Chunking preserves semantic meaning (not cutting mid-sentence)
- [ ] Metadata enables filtering (dates, sources, categories)
- [ ] Retrieval returns relevant chunks (test with 50+ queries manually)
- [ ] Reranking improves precision (compare with/without)
- [ ] System prompt prevents hallucination (tested with adversarial queries)
- [ ] Sources are cited and verifiable
- [ ] Handles "I don't know" gracefully
- [ ] Latency acceptable (<3s for interactive, <30s for complex)
- [ ] Cost per query tracked and within budget

### LLM Cost Optimization

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| Prompt caching | 50-90% on repeated prefixes | Requires cache-friendly prompt design |
| Model routing (small → large) | 40-70% | Slightly higher latency, need router logic |
| Batch API | 50% | Hours of delay, batch-only workloads |
| Shorter prompts | Linear with token reduction | May reduce quality |
| Fine-tuned small model | 80-95% vs large model API | Training cost + maintenance |
| Semantic caching | 50-80% for similar queries | May return stale/wrong cached result |
| Output token limits | Proportional | May truncate useful information |

---

## Phase 7: Model Monitoring

### Monitoring Dashboard

```yaml
monitoring:
  model_performance:
    metrics:
      - name: "primary_metric"         # Same as offline evaluation
        threshold: null                 # Alert if below
        window: "1h | 1d | 7d"
      - name: "prediction_distribution"
        alert: "KL divergence > 0.1 from training distribution"
    latency:
      p50_ms: null
      p95_ms: null
      p99_ms: null
      alert_threshold_ms: null
    throughput:
      requests_per_second: null
      error_rate_threshold: 0.01       # Alert if >1% errors
  data_drift:
    method: "PSI | KS-test | JS-divergence"
    features_to_monitor: []            # Top 10 most important features
    check_frequency: "hourly | daily"
    alert_threshold: null              # PSI > 0.2 = significant drift
  concept_drift:
    method: "performance_degradation"
    ground_truth_delay: ""             # How long until we get labels?
    proxy_metrics: []                  # Metrics available before ground truth
    retraining_trigger: ""             # When to retrain
```

### Drift Response Playbook

| Drift Type | Detection | Severity | Response |
|------------|-----------|----------|----------|
| **Feature drift** (input distribution shifts) | PSI > 0.1 | Warning | Investigate cause, monitor performance |
| **Feature drift** (PSI > 0.25) | PSI > 0.25 | Critical | Retrain on recent data within 24h |
| **Concept drift** (relationship changes) | Performance drop >5% | Critical | Retrain with new labels, review features |
| **Label drift** (target distribution changes) | Chi-square test | Warning | Verify label quality, check for data issues |
| **Prediction drift** (output distribution shifts) | KL divergence | Warning | May indicate upstream data issue |

### Automated Retraining Pipeline

```yaml
retraining:
  triggers:
    - type: "scheduled"
      frequency: "weekly | monthly"
    - type: "performance"
      condition: "primary_metric < threshold for 24h"
    - type: "drift"
      condition: "PSI > 0.2 on any top-10 feature"
  pipeline:
    1_data_validation:
      - check_completeness
      - check_distribution_shift
      - check_label_quality
    2_training:
      - use_latest_N_months_data
      - same_hyperparameters_as_production   # Unless scheduled tuning
      - log_all_metrics
    3_evaluation:
      - compare_vs_production_model
      - must_beat_production_on_primary_metric
      - must_not_regress_on_guardrail_metrics
      - evaluate_on_golden_test_set
    4_deployment:
      - canary_deployment: 5%
      - monitor_for: "4h minimum"
      - auto_rollback_if: "error_rate > 2x baseline"
      - gradual_rollout: "5% → 25% → 50% → 100%"
    5_notification:
      - log_retraining_event
      - notify_team_on_failure
      - update_model_registry
```

---

## Phase 8: MLOps Infrastructure

### ML Platform Components

| Component | Purpose | Tools |
|-----------|---------|-------|
| Experiment tracking | Log runs, compare results | MLflow, W&B, Neptune |
| Feature store | Centralized feature management | Feast, Tecton, Hopsworks |
| Model registry | Version, stage, approve models | MLflow Registry, SageMaker |
| Pipeline orchestration | DAG-based ML workflows | Airflow, Prefect, Dagster, Kubeflow |
| Model serving | Low-latency inference | Triton, TorchServe, vLLM, BentoML |
| Monitoring | Drift, performance, data quality | Evidently, Whylogs, Great Expectations |
| Vector store | Embedding storage for RAG | Pinecone, Weaviate, pgvector, Qdrant |
| GPU management | Training and inference compute | K8s + GPU operator, RunPod, Modal |

### CI/CD for ML

```yaml
ml_cicd:
  on_code_change:
    - lint_and_type_check
    - unit_tests (data transforms, feature logic)
    - integration_tests (pipeline end-to-end on sample data)
  on_data_change:
    - data_validation (Great Expectations / custom)
    - feature_pipeline_run
    - smoke_test_predictions
  on_model_change:
    - full_evaluation_suite
    - bias_and_fairness_check
    - performance_regression_test
    - model_size_and_latency_check
    - security_scan (model file, dependencies)
    - staging_deployment
    - integration_test_in_staging
    - approval_gate (manual for major versions)
    - canary_deployment
```

### Model Registry Workflow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Development │ ───→ │   Staging    │ ───→ │  Production  │
│              │      │              │      │              │
│ - Experiment │      │ - Eval suite │      │ - Canary     │
│ - Log metrics│      │ - Load test  │      │ - Monitor    │
│ - Compare    │      │ - Approval   │      │ - Rollback   │
└──────────────┘      └──────────────┘      └──────────────┘
```

**Promotion criteria:**
- Dev → Staging: Beats current production on offline metrics
- Staging → Production: Passes load test + integration test + human approval
- Auto-rollback: Error rate >2x OR latency >2x OR primary metric drops >5%

---

## Phase 9: Responsible AI

### Bias Detection Checklist

- [ ] Training data represents all demographic groups proportionally
- [ ] Performance metrics broken down by protected attributes
- [ ] Equal opportunity: similar true positive rates across groups
- [ ] Calibration: predicted probabilities match actual rates per group
- [ ] No proxy features for protected attributes (ZIP code → race)
- [ ] Fairness metric selected and threshold defined BEFORE training
- [ ] Disparate impact ratio >0.8 (80% rule)
- [ ] Edge cases tested: what happens with unusual inputs?

### Model Card Template

```yaml
model_card:
  model_name: ""
  version: ""
  date: ""
  owner: ""
  description: ""
  intended_use: ""
  out_of_scope_uses: ""
  training_data:
    source: ""
    size: ""
    date_range: ""
    known_biases: ""
  evaluation:
    metrics: {}
    datasets: []
    sliced_metrics: {}             # Performance by subgroup
  limitations: []
  ethical_considerations: []
  maintenance:
    retraining_schedule: ""
    monitoring: ""
    contact: ""
```

---

## Phase 10: Cost & Performance Optimization

### GPU Selection Guide

| Use Case | GPU | VRAM | Cost/hr (cloud) | Best For |
|----------|-----|------|-----------------|----------|
| Fine-tune 7B model | A10G | 24GB | ~$1 | LoRA/QLoRA fine-tuning |
| Fine-tune 70B model | A100 80GB | 80GB | ~$4 | Full fine-tuning medium models |
| Serve 7B model | T4 | 16GB | ~$0.50 | Inference at scale |
| Serve 70B model | A100 40GB | 40GB | ~$2 | Large model inference |
| Train from scratch | H100 | 80GB | ~$8 | Pre-training, large-scale training |

### Inference Optimization Techniques

| Technique | Speedup | Quality Impact | Complexity |
|-----------|---------|---------------|------------|
| Quantization (INT8) | 2-3x | <1% degradation | Low |
| Quantization (INT4/GPTQ) | 3-4x | 1-3% degradation | Medium |
| Batching | 2-10x throughput | None | Low |
| KV-cache optimization | 20-40% memory savings | None | Medium |
| Speculative decoding | 2-3x for LLMs | None (mathematically exact) | High |
| Model distillation | 5-10x smaller model | 2-5% degradation | High |
| ONNX Runtime | 1.5-3x | None | Low |
| TensorRT | 2-5x | <1% | Medium |
| vLLM (PagedAttention) | 2-4x throughput for LLMs | None | Low |

### Cost Tracking Template

```yaml
ml_costs:
  training:
    compute_cost_per_run: null
    runs_per_month: null
    data_storage_monthly: null
    experiment_tracking: null
  inference:
    cost_per_1k_predictions: null
    daily_volume: null
    monthly_cost: null
    cost_per_query_breakdown:
      compute: null
      model_api_calls: null
      vector_db: null
      data_transfer: null
  optimization_targets:
    cost_per_prediction: null      # Target
    monthly_budget: null
    cost_reduction_goal: ""
```

---

## Phase 11: ML System Quality Rubric

Score your ML system (0-100):

| Dimension | Weight | 0-2 (Poor) | 3-4 (Good) | 5 (Excellent) |
|-----------|--------|-----------|------------|----------------|
| **Problem framing** | 15% | No clear business metric | Defined success metric | Kill criteria + baseline + ROI estimate |
| **Data quality** | 15% | Ad-hoc data, no validation | Automated quality checks | Feature store + lineage + versioning |
| **Experiment rigor** | 15% | No tracking, one-off notebooks | MLflow/W&B tracking | Reproducible pipelines + proper evaluation |
| **Model performance** | 15% | Barely beats baseline | Significant improvement | Calibrated, fair, robust to edge cases |
| **Deployment** | 10% | Manual deployment | CI/CD for models | Canary + auto-rollback + A/B testing |
| **Monitoring** | 15% | No monitoring | Basic metrics dashboard | Drift detection + auto-retraining + alerts |
| **Documentation** | 5% | Nothing documented | Model card exists | Full model card + runbooks + decision log |
| **Cost efficiency** | 10% | No cost tracking | Budget exists | Optimized inference + cost-per-prediction tracking |

**Scoring:**
- 80-100: Production-grade ML system
- 60-79: Good foundations, missing operational maturity
- 40-59: Prototype quality, not ready for production
- <40: Science project, needs fundamental rework

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Optimizing model before fixing data | Data quality > model complexity. Always. |
| Using accuracy on imbalanced data | Use PR-AUC, F1, or domain-specific metric |
| No baseline comparison | Always start with simple heuristic baseline |
| Training on future data | Temporal splits for time-series, strict leakage checks |
| Deploying without monitoring | No model in production without drift detection |
| Fine-tuning when prompting works | Try few-shot prompting first — fine-tune only for scale/cost |
| GPU for everything | CPU inference is often sufficient and 10x cheaper |
| Ignoring calibration | If probabilities matter (risk scoring), calibrate |
| One-time model deployment | ML is a continuous system — plan for retraining from day 1 |
| Premature scaling | Prove value with batch predictions before building real-time serving |

---

## Quick Commands

- "Frame ML problem" → Phase 1 brief
- "Assess data quality" → Phase 2 scoring
- "Select model" → Phase 3 guide
- "Evaluate model" → Phase 4 checklist
- "Deploy model" → Phase 5 serving config
- "Build RAG" → Phase 6 RAG architecture
- "Set up monitoring" → Phase 7 dashboard
- "Optimize costs" → Phase 10 tracking
- "Score ML system" → Phase 11 rubric
- "Detect drift" → Phase 7 playbook
- "A/B test model" → Phase 5 template
- "Create model card" → Phase 9 template
