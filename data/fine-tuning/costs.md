# Cost Estimation & ROI

## Training Cost Calculation

### OpenAI Formula

```
Training Cost = (tokens_in_dataset × epochs × cost_per_M_tokens) / 1,000,000
```

### Example: 1M Token Dataset

| Model | Training Cost |
|-------|---------------|
| GPT-4o | $25 × 3 epochs = $75 |
| GPT-4o-mini | $3 × 3 epochs = $9 |
| GPT-4.1-nano | $1.50 × 3 epochs = $4.50 |

### Open Source (Cloud GPU)

| GPU | Cost/Hour | Typical Training |
|-----|-----------|------------------|
| A100 80GB | $1.50-2.00 | 2-8 hours |
| RTX 4090 | $0.40-0.70 | 4-12 hours |
| Free Colab | $0 | Limited to small models |

## Inference Cost Comparison

### Per-Request Cost

| Setup | Cost per 1K tokens |
|-------|-------------------|
| GPT-4o base | $2.50 (in) + $10 (out) |
| GPT-4o fine-tuned | $3.75 (in) + $15 (out) |
| GPT-4o-mini base | $0.15 (in) + $0.60 (out) |
| GPT-4o-mini fine-tuned | $0.30 (in) + $1.20 (out) |
| Self-hosted Llama 8B | ~$0.01 (GPU amortized) |

**Note:** Fine-tuned models on OpenAI cost MORE per token. ROI comes from shorter prompts or using smaller models effectively.

## Break-Even Analysis

### When Fine-Tuning Saves Money

Fine-tuning pays off when:
1. **Shorter prompts** — No need for long system prompts or examples
2. **Smaller model works** — Fine-tuned mini matches base large
3. **High volume** — Fixed training cost amortized over many requests

### Example Calculation

**Scenario:** 100K requests/month, 500 tokens average

**Option A: GPT-4o with long prompt (2000 token context)**
- Input: 100K × 2500 tokens × $2.50/1M = $625
- Output: 100K × 500 tokens × $10/1M = $500
- Monthly: $1,125

**Option B: Fine-tuned GPT-4o-mini (500 token context)**
- Training: $10 (one-time)
- Input: 100K × 1000 tokens × $0.30/1M = $30
- Output: 100K × 500 tokens × $1.20/1M = $60
- Monthly: $90

**Savings:** $1,035/month after first month

### Break-Even Calculator

```python
def calculate_breakeven(
    training_cost,
    base_cost_per_request,
    finetuned_cost_per_request,
    requests_per_month
):
    savings_per_request = base_cost_per_request - finetuned_cost_per_request
    
    if savings_per_request <= 0:
        return "Fine-tuning increases costs"
    
    requests_to_breakeven = training_cost / savings_per_request
    months_to_breakeven = requests_to_breakeven / requests_per_month
    
    return {
        "requests_to_breakeven": requests_to_breakeven,
        "months_to_breakeven": months_to_breakeven,
        "monthly_savings_after": savings_per_request * requests_per_month
    }
```

## Cost Optimization Strategies

### 1. Start Small
- Begin with GPT-4o-mini or Llama 8B
- Only upgrade if quality insufficient
- Test quality-per-dollar before committing

### 2. Use Batch API
- OpenAI Batch API: 50% discount
- Trade latency (24h window) for cost
- Good for non-real-time processing

### 3. Enable Data Sharing
- OpenAI offers 50% inference discount
- Trade privacy for cost
- Not suitable for sensitive data

### 4. Right-Size Your Model
| Volume | Recommendation |
|--------|----------------|
| <10K/month | Use base model with prompting |
| 10K-100K/month | Consider fine-tuning mini |
| 100K+/month | Fine-tuning ROI strong |

### 5. Self-Host at Scale
- Break-even vs API: typically 500K-1M requests/month
- Consider: GPU cost, maintenance, reliability
- Use QLoRA to minimize GPU requirements

## Hidden Costs to Consider

| Cost | Impact |
|------|--------|
| Data preparation | Engineering time |
| Iteration cycles | 2-3 training runs typical |
| Evaluation infrastructure | Compute for evals |
| Monitoring | Ongoing quality tracking |
| Retraining | When data distribution shifts |
| Expertise | Learning curve, debugging |
