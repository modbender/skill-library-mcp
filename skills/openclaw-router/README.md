# OpenClaw Router Skill v3.0

**Intelligent Model Routing System - Save 60% on AI Costs**

[中文文档](README_zh.md) | [English](README.md)

---

## 🚀 Quick Start

### Installation

```bash
# Install via ClawHub
clawhub install openclaw-router

# Or manual installation
git clone https://github.com/pepsiboy87/openclaw-router.git
cd openclaw-router
bash install_router.sh
```

### Configuration

After installation, the configuration wizard runs automatically:

```bash
# Or run manually
openclaw router config --init
```

### Enable

```bash
openclaw router enable
```

---

## ✨ Features

### 🎯 Intelligent Model Selection

- ✅ 5-dimension self-assessment (Knowledge/Reasoning/Context/Quality/Tools)
- ✅ Task type recognition (Code/Creative/Analysis/Strategic/Learning/Daily)
- ✅ User preference learning
- ✅ Cost budget management

### 💰 Cost Optimization

- ✅ Local model priority (Free)
- ✅ Boundary case verification (L2)
- ✅ Complex task expert (L3)
- ✅ **Save 60% on costs**

### 🌍 Global Support

- ✅ Pure local deployment
- ✅ Pure cloud deployment
- ✅ Hybrid deployment
- ✅ Multi-cloud deployment
- ✅ Enterprise private deployment

### 📊 Transparent Tracking

- ✅ Token usage display
- ✅ Real-time cost tracking
- ✅ Budget quota monitoring
- ✅ Budget alerts

---

## 📋 Supported Models

### Local Models (Ollama)

| Model | Use Case | Cost |
|-------|----------|------|
| qwen2.5:7b | Simple Q&A | $0 |
| qwen2.5:14b | Daily Development | $0 |
| qwen2.5:72b | Complex Tasks | $0 |
| llama3:8b/70b | General Tasks | $0 |
| mistral:7b | Balanced | $0 |

### Cloud Models

| Provider | Model | Use Case | Cost/1k tokens |
|----------|-------|----------|---------------|
| Alibaba Cloud | qwen3.5-plus | Daily主力 | $0.002 |
| Alibaba Cloud | qwen3-max | Complex Reasoning | $0.04 |
| Alibaba Cloud | kimi-k2.5 | Long Text 262k | $0.04 |
| OpenAI | gpt-4 | Creative/English | $0.03 |
| OpenAI | gpt-4o | Multi-modal | $0.005 |
| Anthropic | claude-3-opus | Strongest Reasoning | $0.015 |
| Anthropic | claude-3-sonnet | Balanced | $0.003 |
| AWS Bedrock | Various | Global | Varies |
| Azure OpenAI | GPT-4 | Enterprise | Varies |

---

## ⚙️ Configuration

### Config File Location

```
~/.openclaw/router_config.yaml
```

### Example Configuration

```yaml
version: "1.0.0"

models:
  primary:
    id: "qwen2.5:14b-32k"
    location: "local"
  
  verifier:
    id: "dashscope/qwen3.5-plus"
    location: "cloud"
  
  expert:
    id: "dashscope/qwen3-max"
    location: "cloud"

thresholds:
  mode: "balanced"
  auto_pass: 3.5
  verify_min: 3.0
  verify_max: 3.5
  escalate_below: 3.0

budget:
  monthly: 50
  currency: "USD"
  alert_at: [50, 80, 95]
```

---

## 💰 Pricing

### Free Tier

- ✅ Basic routing
- ✅ Token tracking
- ✅ 1000 requests/month

### Premium ($9.99/month)

- ✅ Unlimited requests
- ✅ User preference learning
- ✅ Budget management
- ✅ Time optimization
- ✅ Priority support

### Enterprise ($29.99/month)

- ✅ All premium features
- ✅ Multi-user management
- ✅ Custom model pool
- ✅ API access
- ✅ Dedicated support
- ✅ SLA guarantee

---

## 🌍 Global Cloud Providers

### Auto-Detected Providers

| Provider | Environment Variable | Region |
|----------|---------------------|--------|
| **Alibaba Cloud** | `DASHSCOPE_API_KEY` | China/Global |
| **OpenAI** | `OPENAI_API_KEY` | Global |
| **Anthropic** | `ANTHROPIC_API_KEY` | Global |
| **AWS Bedrock** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Global |
| **Azure OpenAI** | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | Global |
| **Google Vertex AI** | `GOOGLE_APPLICATION_CREDENTIALS` | Global |

---

## 🧪 Testing

### Run Test Suite

```bash
bash run_tests.sh
```

### Expected Output

```
╔══════════════════════════════════════════════════════════╗
║          OpenClaw Router Skill v3.0 Test Suite           ║
╚══════════════════════════════════════════════════════════╝

Test 1: Module Import...
✅ All modules imported successfully

Test 2: Environment Detection...
   Ollama: ✅ Installed (2 models)
   Alibaba Cloud: ✅ Configured
   OpenAI: ✅ Configured
   System: 16.0GB RAM, 8 cores

Test 3: Configuration Recommendation...
   ✅ Primary: qwen2.5:14b-32k (local)
   ✅ Verifier: dashscope/qwen3.5-plus (cloud)
   ✅ Expert: dashscope/qwen3-max (cloud)

Test 4: Model Routing...
   5.0 score → qwen2.5:14b
   3.2 score → qwen2.5:14b + verification
   2.0 score → dashscope/qwen3-max

Test 5: Configuration Management...
   ✅ Save successful
   ✅ Load successful
   ✅ Validation passed

All tests passed! Router Skill is ready.
```

---

## 📖 Documentation

- [Configuration Guide](docs/CONFIGURATION.md)
- [API Documentation](docs/API.md)
- [Usage Examples](docs/EXAMPLES.md)
- [FAQ](docs/FAQ.md)

---

## 🤝 Contributing

Welcome to contribute!

```bash
# Fork the project
git fork https://github.com/pepsiboy87/openclaw-router

# Clone to local
git clone git@github.com:your-username/openclaw-router.git

# Create branch
git checkout -b feature/your-feature

# Commit changes
git commit -m "Add your feature"

# Push
git push origin feature/your-feature

# Create Pull Request
```

---

## 📄 License

MIT License

---

## 📞 Support

- **Documentation:** https://github.com/pepsiboy87/openclaw-router
- **Issues:** https://github.com/pepsiboy87/openclaw-router/issues
- **Email:** pepsiboy87@example.com

---

_Empower every AI assistant with intelligent routing!_
