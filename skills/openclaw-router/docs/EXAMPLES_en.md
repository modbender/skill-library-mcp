# OpenClaw Router Skill - Usage Examples

**Version:** 1.0.0  
**Purpose:** Real-world usage scenarios

---

## 🚀 Quick Start Examples

### Example 1: First Installation

```bash
# Install Router Skill
bash install_router.sh

# Auto-run configuration wizard
🔍 Detecting environment...
✅ Ollama installed, found 2 models
   • qwen2.5:14b-32k
   • qwen2.5:7b-32k
✅ Alibaba Cloud configured (Key: sk-5d5ca...)

📋 Recommended Config:
  Primary: qwen2.5:14b-32k (local, free)
  Verifier: dashscope/qwen3.5-plus (cloud, $0.002/1k)
  Expert: dashscope/qwen3-max (cloud, $0.04/1k)
  
  Threshold mode: balanced
  Budget suggestion: $50/month

[1] Use Recommended Config
[2] Custom Configuration
[4] Setup Later

Enter choice [1-4]: 1

✅ Configuration complete!
```

---

### Example 2: Simple Q&A (Local Processing)

```
User: What's the date today?

Assistant: Today is March 2, 2026, Monday.

---
【Usage This Time】
- Model: qwen2.5:14b-32k (local)
- Token Estimate: Input~10 / Output~30 = Total~40
- Cost: $0 (local free)

【Quota Remaining】
- Monthly Budget: $50 (28 days left)
- Estimated Used: ~0%
- Daily Average: $1.79
- Status: ✅ Sufficient quota
---
```

---

### Example 3: Code Generation (Local Processing)

```
User: Write a Python function to calculate Fibonacci sequence

Assistant:
```python
def fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

# Test
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

---
【Usage This Time】
- Model: qwen2.5:14b-32k (local)
- Token Estimate: Input~50 / Output~400 = Total~450
- Cost: $0 (local free)

【Quota Remaining】
- Monthly Budget: $50 (28 days left)
- Estimated Used: ~0%
- Status: ✅ Sufficient quota
---
```

---

### Example 4: Complex Strategy (Cloud L3)

```
User: [BEST] Help me design a 3-year technology strategy for my company

Assistant: (Detects complex task, automatically uses L3 expert model)

# 3-Year Technology Strategy

## I. Current Situation Analysis
...

## II. Strategic Goals
...

## III. Implementation Path
...

## IV. Risk Assessment
...

---
【Usage This Time】
- Model: dashscope/qwen3-max (cloud L3)
- Token Estimate: Input~200 / Output~3000 = Total~3200
- Cost: $0.128 (monthly quota)

【Quota Remaining】
- Monthly Budget: $50 (28 days left)
- Estimated Used: ~1%
- Daily Average: $1.79
- Status: ✅ Sufficient quota
---
```

---

### Example 5: Boundary Case (Local + Verification)

```
User: Design a database architecture for an e-commerce platform

Assistant: (Local 14b completes, self-assessment 3.2, triggers verification)

【Local Model Answer】
```sql
CREATE TABLE users (...);
CREATE TABLE products (...);
CREATE TABLE orders (...);
```

【Verification Report】
- Verifier: dashscope/qwen3.5-plus
- Accuracy: ⭐⭐⭐⭐ (4/5)
- Completeness: ⭐⭐⭐ (3/5)
- Suggestion: Add indexes and audit fields

【Final Answer】
(Integrates local answer and verification suggestions)
```

---

## 🎯 Different Scenarios

### Scenario 1: Pure Local Deployment

```yaml
Environment:
  - Ollama: ✅ qwen2.5:14b, qwen2.5:72b
  - Cloud API: ❌

Recommended Config:
  Primary: qwen2.5:14b
  Expert: qwen2.5:72b
  Threshold: auto_pass=3.5

Suitable for:
  - Users with high-performance local machines
  - Privacy-focused users
  - Limited budget
```

---

### Scenario 2: Hybrid Deployment (Recommended)

```yaml
Environment:
  - Ollama: ✅ qwen2.5:14b
  - Cloud API: ✅ Alibaba Cloud

Recommended Config:
  Primary: qwen2.5:14b (local)
  Verifier: qwen3.5-plus (cloud)
  Expert: qwen3-max (cloud)
  Threshold: auto_pass=3.5, verify=3.0-3.5

Suitable for:
  - Most users
  - Balance cost and quality
  - Daily development
```

---

### Scenario 3: Pure Cloud Deployment

```yaml
Environment:
  - Ollama: ❌
  - Cloud API: ✅ Alibaba + OpenAI

Recommended Config:
  Primary: qwen3.5-plus
  Expert: qwen3-max / gpt-4
  Threshold: auto_pass=4.0 (conservative)

Suitable for:
  - No local machine
  - Laptop users
  - Need strongest capability
```

---

## 📊 Cost Comparison Examples

### Task: 100 Requests

| Solution | Local | L2 | L3 | Total Cost |
|----------|-------|----|----|------------|
| **Traditional** | 0 | 0 | 100 | $4.00 |
| **Router v3.0** | 80 | 15 | 5 | $1.60 |
| **Savings** | - | - | - | **60%** |

---

### Monthly Estimate (Based on Similar Users)

| User Type | Traditional | Router v3.0 | Savings |
|-----------|-------------|-------------|---------|
| Individual | $50/month | $20/month | 60% |
| Small Business | $150/month | $60/month | 60% |
| AI Studio | $600/month | $240/month | 60% |

---

## 🔧 Advanced Usage

### 1. Force Model with Tags

```
User: [L3] This is critical, use expert model

Assistant: (Forces L3, even if self-assessment score is high)
```

```
User: [FAST] Quick answer, no verification

Assistant: (Skips verification, answers directly with local model)
```

```
User: [VERIFY] Help me verify this code

Assistant: (Forces verification flow)
```

---

### 2. Custom Thresholds

```yaml
# Edit configuration file
~/.openclaw/router_config.yaml

thresholds:
  mode: "custom"
  auto_pass: 4.0      # Higher threshold, more conservative
  verify_min: 3.5
  verify_max: 4.0
  escalate_below: 3.5
```

---

### 3. Budget Alerts

```yaml
budget:
  monthly: 100
  alert_at: [50, 80, 95]  # Alert at 50%/80%/95%
```

---

## 🌍 Global Cloud Providers

### Auto-Detected Providers

```bash
# Environment variables
export DASHSCOPE_API_KEY="sk-..."      # Alibaba Cloud
export OPENAI_API_KEY="sk-..."         # OpenAI
export ANTHROPIC_API_KEY="sk-..."      # Anthropic
export AWS_ACCESS_KEY_ID="..."         # AWS
export AWS_SECRET_ACCESS_KEY="..."     # AWS
export AZURE_OPENAI_API_KEY="..."      # Azure
```

### Detection Results

```
🔍 Environment Detection Results
============================================================

📦 Local Models (Ollama):
   ✅ Installed, found 5 models
      • qwen2.5:14b-32k (recommended primary)
      • qwen2.5:7b-32k
      • llama3:8b
      • mistral:7b
      • gemma:7b

☁️  Cloud APIs:
   ✅ Alibaba Cloud (Key: sk-5d5ca...)
      Supports: qwen3.5-plus, qwen3-max, kimi-k2.5...
   ✅ OpenAI (Key: sk-proj-...)
      Supports: gpt-4, gpt-4o, gpt-3.5-turbo...
   ✅ Anthropic (Key: sk-ant-...)
      Supports: claude-3-opus, claude-3-sonnet...

💻 System Resources:
   Memory: 16.0 GB
   CPU: 8 cores
   Disk: 500.0 GB

============================================================
📋 Recommended Config
============================================================

Primary: qwen2.5:14b-32k (local, free)
Verifier: dashscope/qwen3.5-plus (cloud, $0.002/1k)
Expert: dashscope/qwen3-max (cloud, $0.04/1k)

Threshold mode: balanced
Budget suggestion: $50/month
```

---

## 📞 Need Help?

- **Documentation:** https://github.com/pepsiboy87/openclaw-router
- **Issues:** https://github.com/pepsiboy87/openclaw-router/issues
- **Email:** pepsiboy87@example.com

---

_Empower every AI assistant with intelligent routing!_
