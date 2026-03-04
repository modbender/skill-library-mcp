# GPU Infrastructure

## Kubernetes GPU Scheduling

**Basic setup:**
- nvidia-device-plugin or gpu-operator
- Node selectors + tolerations for GPU nodes
- ResourceQuotas per namespace

**Request = entire GPU:**
```yaml
resources:
  limits:
    nvidia.com/gpu: 1  # This reserves the WHOLE GPU
```

❌ You cannot request 0.5 GPU natively
❌ Memory-based requests don't exist in standard K8s

## GPU Sharing Options

| Method | Pros | Cons |
|--------|------|------|
| MPS (Multi-Process Service) | Time-slicing | Complex setup, not all workloads |
| MIG (Multi-Instance GPU) | Hardware isolation | A100 only, fixed partitions |
| vGPU | Enterprise support | $$$ licensing |
| Sequential jobs | Simple | No real concurrency |

**Reality check:** GPU sharing is harder than agents suggest.

## Common Traps

**Memory management:**
- GPU OOM kills pod silently (no useful logs)
- Memory fragmentation in long-running training
- CUDA_VISIBLE_DEVICES needed for isolation

**Cost traps:**
- Egress for TB datasets > compute cost
- Checkpoint storage adds up (hundreds of GB per run)
- GPU-to-GPU networking (InfiniBand vs Ethernet) matters for multi-node

**Scaling:**
- Spot/preemptible viable for training (checkpoint often)
- "Turn off when not using" ignores warm-up time
- HPA doesn't scale fractionally on GPU

## Multi-Node Training

**Networking matters:**
- InfiniBand >> Ethernet for gradient sync
- NVLink for intra-node, but cross-node is bottleneck
- Consider data parallelism before model parallelism

## Pragmatic Advice

- Don't use Kubernetes until you need it
- A single node with `docker compose` + GPUs is often enough
- Data scientists will bypass complex infra (design for that)
