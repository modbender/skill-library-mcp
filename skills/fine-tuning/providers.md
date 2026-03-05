# Provider Selection

## Quick Comparison

| Provider | Best For | Training Cost | Min Examples |
|----------|----------|---------------|--------------|
| OpenAI GPT-4o-mini | Cost-effective default | $3/M tokens | 50 |
| OpenAI GPT-4o | Max quality | $25/M tokens | 50 |
| Anthropic (Bedrock) | Claude-required projects | Per-hour | 1000+ |
| Llama + Unsloth | Privacy, budget | GPU hours | 100 |
| Mistral | Multilingual, EU | API or self-host | 100 |

## OpenAI Fine-Tuning

**Models available:**
- GPT-4o ($25/M training, $3.75/$15 inference)
- GPT-4o-mini ($3/M training, $0.30/$1.20 inference) — **default choice**
- GPT-4.1 / GPT-4.1-mini / GPT-4.1-nano (newest)
- o4-mini ($100/hour, reasoning fine-tuning)

**Strengths:**
- Best documentation and DX
- Results with as few as 50 examples
- Reinforcement Fine-Tuning (RFT) for reasoning
- 50% discount if you enable data sharing

**Process:**
```bash
# Validate format
openai api fine_tuning.jobs.validate_file -f training.jsonl

# Create job
openai api fine_tuning.jobs.create \
  -t "file-abc123" \
  -m "gpt-4o-mini-2024-07-18"
```

## Anthropic / Claude (via Bedrock)

**Status:** Only Claude 3 Haiku fine-tuning is GA (as of Nov 2024).

**Constraints:**
- Must use Amazon Bedrock (no direct API)
- Region: US West (Oregon) only
- No Claude 3.5 Sonnet or Opus fine-tuning

**Results:**
- +24.6% F1 improvement reported
- Fine-tuned Haiku outperforms base Sonnet by 9.9%

**When to use:** Only if Claude is mandatory AND Haiku quality is acceptable.

## Google / Gemini

**Available:** Gemini 1.5 Pro and Flash via Vertex AI.

**Notes:**
- Less community adoption
- Good for GCP-native teams
- Supports LoRA-style efficient tuning

## Open Source Stack

### Recommended Tooling

| Tool | Use Case | VRAM Required |
|------|----------|---------------|
| **Unsloth** | Fast LoRA/QLoRA, best for beginners | 3GB+ (QLoRA) |
| **Axolotl** | Complex configs, multi-method | 16GB+ |
| **PEFT** | HuggingFace ecosystem integration | Varies |
| **TorchTune** | Research, full control | 24GB+ |

### Base Models

| Model | Parameters | Strengths |
|-------|------------|-----------|
| Llama 3.1 8B | 8B | Best small model, fast training |
| Llama 3.1 70B | 70B | Near-GPT-4 quality |
| Mistral 7B | 7B | Multilingual, efficient |
| Qwen 2.5 | 7B-72B | Excellent multilingual |

### LoRA vs QLoRA

| Technique | Precision | VRAM Savings | Quality |
|-----------|-----------|--------------|---------|
| LoRA | 16-bit | ~50% | Higher |
| QLoRA | 4-bit | ~75% | Slightly lower |

**Recommendation:** Start with Unsloth Dynamic 4-bit QLoRA. Recovers most quality loss.

## Decision Matrix

| Constraint | Recommendation |
|------------|----------------|
| Default / best DX | OpenAI GPT-4o-mini |
| Budget <$50 | Unsloth + free Colab |
| Max quality | OpenAI GPT-4o with RFT |
| Privacy required | Llama + Axolotl locally |
| Claude required | Bedrock + Haiku |
| Multilingual | Qwen or Gemini |
