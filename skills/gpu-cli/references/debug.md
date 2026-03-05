# Debug GPU CLI Issues

Turn errors into solutions.

## Diagnostic Commands

```bash
gpu daemon status              # Daemon running?
gpu daemon logs --tail 50      # Recent logs
gpu status                     # Pod/job state
gpu logs                       # logs for job/agent
```

## Common Errors

### CUDA Out of Memory

**Error**: `CUDA out of memory`, `torch.cuda.OutOfMemoryError`

**Fixes (easiest first):**
```python
# 1. Reduce batch size
BATCH_SIZE = 1

# 2. Enable gradient checkpointing
model.gradient_checkpointing_enable()

# 3. Use FP16
model = model.half()

# 4. Use INT4 quantization
from transformers import BitsAndBytesConfig
bnb_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config)

# 5. CPU offloading
pipe.enable_model_cpu_offload()
```

**Config fix** - use bigger GPU:
```jsonc
{ "gpu_types": [{ "type": "A100 PCIe 80GB" }], "min_vram": 80 }
```

### Connection Refused

**Error**: `Connection refused`, `SSH connection failed`

**Fixes:**
```bash
gpu daemon status     # Check if running
gpu daemon restart    # Restart daemon
```

### Pod Won't Start

**Error**: `No GPUs available`, `Provisioning timeout`

**Fixes:**
```jsonc
// Use min_vram instead of specific GPU
{ "min_vram": 24 }

// Or try different GPU
{ "gpu_types": [{ "type": "RTX A6000" }] }

// Or relax price
{ "max_price": 2.0 }
```

### Sync Errors

**Error**: `rsync error`, `Sync failed`

**Fixes:**
1. Check `.gitignore` - large files should be ignored
2. Check `outputs` in config matches your output paths
3. Increase storage: `"workspace_size_gb": 100`

### Model Loading Failed

**Error**: `Model not found`, `HuggingFace rate limit`

**Fixes:**
```jsonc
{
  "download": [
    { "strategy": "hf", "source": "meta-llama/Llama-3.1-8B-Instruct", "timeout": 7200 }
  ]
}
```

For gated models, set HF token: `gpu auth add huggingface`

### Exit Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 1 | Script error | Check Python traceback |
| 126 | Permission denied | `chmod +x script.sh` |
| 127 | Command not found | Install missing package |
| 137 | OOM killed | Reduce memory or bigger GPU |

### CUDA Version Mismatch

**Error**: `CUDA error: no kernel image`, `Torch not compiled with CUDA`

**Fix** - use compatible base image:
```jsonc
{
  "environment": {
    "base_image": "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
  }
}
```

## Quick Reference

| Error Contains | Quick Fix |
|----------------|-----------|
| `CUDA out of memory` | Reduce batch, quantize, bigger GPU |
| `Connection refused` | `gpu daemon restart` |
| `No GPUs available` | Try different GPU type |
| `Model not found` | Add to download spec |
| `Killed` (exit 137) | OOM - bigger GPU |
| `rate limit` | Set HF_TOKEN |
