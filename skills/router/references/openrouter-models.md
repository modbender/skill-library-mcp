# OpenRouter Models Reference

*Generated: February 2026*

*Total models: 340*

This file contains OpenRouter-specific model information for cost-optimized routing decisions.

## Pricing Format

All prices in USD per million tokens.

## Quick Picks by Use Case

### Cheapest for Routine Tasks (Tier 1)
- **File I/O, simple Q&A:** google/gemini-2.0-flash-lite-001 ($0.07/M)
- **Code snippets:** deepseek/deepseek-chat ($0.30/M)
- **Quick responses:** openai/gpt-4o-mini ($0.15/M)
- **Tool use:** anthropic/claude-3-haiku ($0.25/M)

### Balanced Performance (Tier 2)
- **General work:** anthropic/claude-sonnet-4 ($3.00/M)
- **Multimodal:** openai/gpt-4o ($2.50/M)
- **Long context:** google/gemini-2.5-pro ($1.25/M)

### Complex Reasoning (Tier 3)
- **Budget reasoning:** openai/o3-mini ($1.10/M input)
- **Best reasoning:** anthropic/claude-opus-4 ($15.00/M)
- **Frontier:** openai/gpt-4.5-preview ($75.00/M)

## Free Models

| Model ID | Input | Output | Context |
|----------|-------|--------|----------|
| openrouter/aurora-alpha | $0.00 | $0.00 | 128,000 |
| openrouter/free | $0.00 | $0.00 | 200,000 |
| stepfun/step-3.5-flash:free | $0.00 | $0.00 | 256,000 |
| ... and 28 more |

## Tier 1: Budget Models (<$0.50/M tokens)

| Model ID | Input | Output | Context |
|----------|-------|--------|----------|
| liquid/lfm2-8b-a1b | $0.01 | $0.02 | 32,768 |
| google/gemma-3-4b-it | $0.02 | $0.07 | 96,000 |
| meta-llama/llama-3.2-3b-instruct | $0.02 | $0.02 | 131,072 |
| deepseek/deepseek-r1-distill-llama-70b | $0.03 | $0.11 | 131,072 |
| openai/gpt-oss-120b | $0.04 | $0.19 | 131,072 |
| google/gemma-3-27b-it | $0.04 | $0.15 | 128,000 |
| meta-llama/llama-3.2-11b-vision-instruct | $0.05 | $0.05 | 131,072 |
| qwen/qwen-turbo | $0.05 | $0.20 | 131,072 |
| google/gemini-2.0-flash-lite-001 | $0.07 | $0.30 | 1,048,576 |
| meta-llama/llama-4-scout | $0.08 | $0.30 | 327,680 |
| stepfun/step-3.5-flash | $0.10 | $0.30 | 256,000 |
| google/gemini-2.0-flash-001 | $0.10 | $0.40 | 1,048,576 |
| meta-llama/llama-3.3-70b-instruct | $0.10 | $0.32 | 131,072 |
| deepseek/deepseek-chat-v3.1 | $0.15 | $0.75 | 32,768 |
| openai/gpt-4o-mini | $0.15 | $0.60 | 128,000 |
| deepseek/deepseek-chat | $0.30 | $1.20 | 163,840 |
| ... and 100+ more |

## Tier 2: Mid-Range Models ($0.50-5/M tokens)

| Model ID | Input | Output | Context |
|----------|-------|--------|----------|
| google/gemini-2.5-pro | $1.25 | $10.00 | 1,048,576 |
| openai/gpt-4o | $2.50 | $10.00 | 128,000 |
| anthropic/claude-sonnet-4 | $3.00 | $15.00 | 1,000,000 |
| openai/o3-mini | $1.10 | $4.40 | 200,000 |
| x-ai/grok-3 | $3.00 | $15.00 | 131,072 |
| ... and 80+ more |

## Tier 3: Premium Models ($5+/M tokens)

| Model ID | Input | Output | Context |
|----------|-------|--------|----------|
| anthropic/claude-3.5-sonnet | $6.00 | $30.00 | 200,000 |
| openai/o1 | $15.00 | $60.00 | 200,000 |
| anthropic/claude-opus-4 | $15.00 | $75.00 | 200,000 |
| openai/gpt-4.5-preview | $75.00 | $150.00 | 128,000 |
| openai/o1-pro | $150.00 | $600.00 | 200,000 |
| ... and 20+ more |

---

*For the complete list of all 340 models, see the accompanying `openrouter-models.json` file.*

*Prices per million tokens. Verify current rates at https://openrouter.ai/docs#models*
