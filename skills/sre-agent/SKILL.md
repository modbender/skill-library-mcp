---
name: aiops-agent
description: AI驱动的智能运维系统，实现主动预警、智能诊断和自动化治理
author: James Mei
contact:
  email: meijinmeng@126.com
  blog: https://www.cnblogs.com/Jame-mei
metadata:
  openclaw:
    emoji: 🤖
---

# AIOps Agent

AI-driven intelligent operations system for proactive monitoring, intelligent diagnosis, and automated remediation.

## ✅ v1.0.1 Update

**What's New:**
- 🐛 Fixed syntax errors (18/18 tests passing)
- 📦 Added missing dependencies documentation
- 🧪 Improved test coverage

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd sre-agent
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Start services
make up

# Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📦 Dependencies

### Core Dependencies
```bash
pip install fastapi uvicorn
pip install kubernetes
pip install anthropic  # or openai
pip install scikit-learn
pip install pandas numpy
```

### Testing Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Optional Dependencies
```bash
pip install prometheus-client
pip install langchain
pip install prophet  # for time series prediction
```

## Features

- ⚡ Proactive alerting (1-3 hours ahead)
- 🔍 Automated root cause analysis
- 🤖 Self-healing automation
- 📊 Multi-dimensional monitoring
- 🧠 LLM-powered insights

## Architecture

- **Perception**: Metrics, logs, events collection
- **Cognition**: Anomaly detection, prediction, RCA
- **Decision**: Risk assessment, action planning
- **Action**: Automated remediation

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Test results: 18/18 passing ✅
```

## 📝 Changelog

### v1.0.1 (2026-02-25)
- Fixed syntax errors in core modules
- All 18 tests passing
- Added missing dependencies:
  - pytest, pytest-asyncio, pytest-cov
  - scikit-learn
  - fastapi
  - kubernetes
  - anthropic
- Improved documentation

### v1.0.0 (2026-02-25)
- Initial release
- Core AIOps architecture
- Basic anomaly detection
- Prediction engine
- Root cause analysis
