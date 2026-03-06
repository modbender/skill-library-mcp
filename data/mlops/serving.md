# Model Serving at Scale

## Cold Start Problem

**Large models (1B+ params):**
- Loading weights = 30-60 seconds
- Solutions: preloading, model caching, keep-warm pods
- Serverless is problematic for large models

**Warm-up before traffic:**
- Run dummy predictions before marking pod ready
- Use `readinessProbe` that actually tests inference
- ❌ Common mistake: health check only checks HTTP, not model loaded

## Batch vs Real-Time

| Aspect | Batch | Real-Time |
|--------|-------|-----------|
| Latency target | Minutes | <100ms |
| Throughput | High (vectorized) | Per-request |
| Scaling | Job-based | HPA/replicas |
| Failure mode | Retry job | Graceful degradation |

**Don't use batch architecture for real-time or vice versa.**

## Scaling Traps

**HPA with GPUs doesn't work well:**
- Can't scale fractionally (0.5 GPU)
- GPU utilization metric often wrong
- Solution: scale on request queue depth instead

**Triton/TorchServe production configs differ from defaults:**
- Dynamic batching needs tuning
- Model warmup is critical
- Concurrent model execution limits

## Graceful Degradation

When model fails, what's the fallback?
- Return cached result
- Use simpler rule-based system
- Return "unable to predict" with retry

❌ Never return 500 without a degradation path
❌ Never assume the model is always available
