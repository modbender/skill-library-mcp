# GPU Cost Optimization

Spend less, compute more.

## GPU Pricing (2025)

### Consumer/Prosumer
| GPU | VRAM | $/hr |
|-----|------|------|
| RTX 4070 Ti | 12GB | $0.25 |
| RTX 4080 | 16GB | $0.35 |
| RTX 3090 | 24GB | $0.22 |
| RTX 4090 | 24GB | $0.44 |

### Professional
| GPU | VRAM | $/hr |
|-----|------|------|
| RTX A4000 | 16GB | $0.30 |
| RTX A5000 | 24GB | $0.40 |
| L4 | 24GB | $0.35 |
| RTX A6000 | 48GB | $0.80 |
| L40S | 48GB | $0.95 |

### Datacenter
| GPU | VRAM | $/hr |
|-----|------|------|
| A100 40GB | 40GB | $1.29 |
| A100 80GB PCIe | 80GB | $1.79 |
| H100 PCIe | 80GB | $2.49 |
| H100 SXM | 80GB | $3.19 |
| H200 | 141GB | $4.99 |

## VRAM Requirements

### LLM Inference
| Model Size | FP16 | INT4 |
|------------|------|------|
| 7B | 14GB | 5GB |
| 13B | 26GB | 8GB |
| 70B | 140GB | 40GB |

### Image Models
| Model | Inference | Training |
|-------|-----------|----------|
| SD 1.5 | 6GB | 12GB |
| SDXL | 10GB | 24GB |
| FLUX | 24GB | 48GB |

## Optimization Strategies

### 1. Use Smallest GPU That Works

```jsonc
// BAD: Over-provisioned
{ "gpu_types": [{ "type": "A100 PCIe 80GB" }] }  // $1.79/hr for SDXL?

// GOOD: Right-sized
{ "gpu_types": [{ "type": "RTX 4090" }], "min_vram": 12 }  // $0.44/hr
```

### 2. Use Quantization

INT4 reduces VRAM 4x with minimal quality loss:
```python
from transformers import BitsAndBytesConfig
config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=config)
```

**Savings**: Llama 70B on 1x A100 ($1.79/hr) vs 2x A100 ($3.58/hr)

### 3. Tune Cooldown

```jsonc
// Batch jobs - stop quickly
{ "keep_alive_minutes": 3 }

// Interactive work - stay warm
{ "keep_alive_minutes": 10 }

// API servers - longer
{ "keep_alive_minutes": 30 }
```

### 4. Pre-download Models

Avoid re-downloading on each run:
```jsonc
{
  "download": [
    { "strategy": "hf", "source": "model-name", "timeout": 7200 }
  ]
}
```

### 5. Batch Processing

```bash
# BAD: Pod startup per item
for f in files; do gpu run process $f; done

# GOOD: One pod, all items
gpu run python process_batch.py
```

## Decision Trees

### LLM Inference
```
7-8B model?
├── INT4 → RTX 4070 Ti ($0.25/hr)
└── FP16 → RTX 4090 ($0.44/hr) ✓ best value

70B model?
├── INT4 → A100 80GB ($1.79/hr)
└── FP16 → 2x A100 ($3.58/hr)
```

### Training
```
LoRA SDXL → RTX 4090 ($0.44/hr)
LoRA FLUX → A100 80GB ($1.79/hr)
Full fine-tune 7B → A100 40GB ($1.29/hr)
Full fine-tune 70B → 8x A100 ($14/hr)
```

## Common Mistakes

| Mistake | Waste | Fix |
|---------|-------|-----|
| A100 for SD 1.5 | 75% | Use RTX 4090 |
| H100 for 7B LLM | 82% | Use RTX 4090 |
| 2 GPUs when 1 fits | 50% | Single GPU |
| No quantization | 50-75% | Use INT4/INT8 |
