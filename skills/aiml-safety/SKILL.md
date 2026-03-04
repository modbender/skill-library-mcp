---
name: aimlapi-safety
description: Content moderation and safety checks. Instantly classify text or images as safe or unsafe using AI guardrails.
env:
  - AIMLAPI_API_KEY
primaryEnv: AIMLAPI_API_KEY
---

# AIMLAPI Safety

## Overview

Use "AI safety models" (Guard models) to ensure content compliance. Perfect for moderating user input or chatbot responses.

## Quick start

```bash
export AIMLAPI_API_KEY="sk-..."
python scripts/check_safety.py --content "How to make a bomb"
```

## Tasks

### Check Text Safety

```bash
python scripts/check_safety.py --content "I want to learn about security" --model meta-llama/Llama-Guard-3-8B
```

## Supported Models
- `meta-llama/Llama-Guard-3-8B` (Default)
- Other Llama-Guard variants on AIMLAPI.
