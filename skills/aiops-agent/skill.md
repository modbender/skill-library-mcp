---
name: aiops-agent
description: AI-driven intelligent operations system for proactive monitoring, intelligent diagnosis, and automated remediation. Use for AIOps tasks, SRE automation, or intelligent operations.
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
pip install fastapi uvicorn kubernetes anthropic scikit-learn pandas numpy
```

### Testing Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
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
- Added missing dependencies documentation

### v1.0.0 (2026-02-24)
- Initial release
- Complete AIOps framework
- Multi-layer architecture (Perception → Cognition → Decision → Action)
