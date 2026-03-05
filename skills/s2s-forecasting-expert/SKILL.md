---
name: s2s-model-builder
description: End-to-end builder for AI-based Subseasonal-to-Seasonal (S2S) forecasting systems. Generates runnable PyTorch code for FuXi-style, FengWu-style, and AIFS-inspired models including CRPS-based probabilistic training.
metadata:
  clawdbot:
    emoji: "🌎"
    requires:
      env: []
    files: []
---

# S2S Model Builder (Subseasonal-to-Seasonal Forecasting)

This skill actively helps you **design, implement, and train S2S forecasting models from scratch**.

It generates:

- PyTorch model architectures
- Training loops
- CRPS loss implementations
- Data preprocessing pipelines (ERA5-style)
- Evaluation scripts
- Multi-GPU training configurations
- Inference pipelines

Supported paradigms include:

- FuXi-style transformer architectures
- FengWu-style Earth system transformers
- AIFS-inspired probabilistic models
- Ensemble neural forecasting
- Multi-lead-time forecasting heads

---

# What This Skill Can Build

## 1. Model Architecture Code
- 3D spatiotemporal transformers
- Global grid attention models
- Multi-variable input pipelines (Z500, T2M, winds, SST)
- Lead-time conditioned decoders
- Ensemble output heads

## 2. Training Infrastructure
- PyTorch training loops
- Distributed training (FSDP-ready structure)
- Mixed precision support
- Gradient accumulation
- Checkpoint saving

## 3. Probabilistic Forecasting
- CRPS loss (Gaussian & ensemble forms)
- Quantile regression heads
- Spread-skill diagnostics
- Reliability calibration utilities

## 4. Evaluation Code
- CRPS computation
- ACC metric implementation
- RMSE across forecast horizons
- Skill vs climatology baseline

## 5. Deployment-Ready Inference
- Batched inference scripts
- Memory-optimized forward passes
- Model export patterns

---

# Example Prompts

- “Generate a FuXi-style transformer in PyTorch for 30-day Z500 forecasting.”
- “Build a CRPS loss function for ensemble S2S outputs.”
- “Create a full ERA5 training pipeline scaffold.”
- “Design a multi-lead-time S2S forecasting head.”
- “Implement distributed training for global 1° resolution data.”

---

# External Endpoints

This skill does not call external APIs.

| Endpoint | Purpose | Data Sent |
|----------|---------|-----------|
| None     | N/A     | None      |

All generated code runs locally within the user’s environment.

---

# Security & Privacy

- No external API calls
- No automatic dataset downloads
- No remote execution
- No hidden scripts
- All code is generated transparently

Users are responsible for lawful dataset usage (e.g., ERA5 licensing).

---

# Model Invocation Note

This skill may be automatically invoked when user queries involve:

- Building S2S models
- FuXi / FengWu / AIFS implementations
- CRPS training
- AI weather model architecture
- ERA5 training pipelines

Users may opt out by disabling the skill.

---

# Trust Statement

By using this skill, you acknowledge it generates code for AI-based climate forecasting systems. No data is transmitted externally. All execution occurs within your own environment.

---

# Version

v1.0.0  
Last updated: Feb 16, 2026
