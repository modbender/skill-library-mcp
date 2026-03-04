# Paradox Data — EcoCompute Complete Measurements

## Paradox 1: NF4 Small-Model Energy Penalty (RTX 5090 Blackwell)

NF4 quantization **increases** energy consumption for models ≤3B parameters.

### RTX 5090 — FP16 vs NF4

| Model | Params | Precision | Throughput (tok/s) | Power (W) | Energy (J/1k tok) | Δ vs FP16 |
|-------|--------|-----------|-------------------|-----------|-------------------|-----------|
| Qwen2-1.5B | 1.5B | FP16 | 71.45 ± 0.80 | 172.30 | 2,411 | — |
| Qwen2-1.5B | 1.5B | NF4 | 41.57 ± 0.29 | 129.83 | 3,123 | **+29.4%** ⚠️ |
| Phi-3-mini | 3.8B | FP16 | 43.47 ± 0.11 | 213.35 | 4,908 | — |
| Phi-3-mini | 3.8B | NF4 | 32.08 ± 0.13 | 175.85 | 5,483 | **+11.7%** ⚠️ |

**Root Cause — De-quantization Tax:**
- Small models fit in VRAM at FP16 → memory bandwidth is NOT the bottleneck
- NF4 adds de-quantization (NF4→FP16) at every linear layer
- Extra compute overhead DOMINATES the small memory savings
- Formula: E_ratio = (T_NF4/T_FP16) × (P_NF4/P_FP16) ≈ 1.72 × 0.75 ≈ 1.29 (matches +29.4%)

**Crossover Point:** ~5B parameters. Below this, FP16 is always more efficient.

### RTX 4090D — NF4 Saves Energy for Larger Models

| Model | Params | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 |
|-------|--------|-----------|-------------------|-------------------|-----------|
| Yi-1.5-6B | 6B | FP16 | 34.72 ± 0.18 | 4,716 ± 119 | — |
| Yi-1.5-6B | 6B | NF4 | 36.42 ± 0.27 | 3,333 ± 25 | **−29.3%** ✅ |
| Mistral-7B | 7B | FP16 | 29.06 ± 0.10 | 5,661 ± 143 | — |
| Mistral-7B | 7B | NF4 | 32.29 ± 0.02 | 3,707 ± 15 | **−34.5%** ✅ |
| Phi-3-mini | 3.8B | FP16 | 57.62 ± 0.48 | 2,775 ± 48 | — |
| Phi-3-mini | 3.8B | NF4 | 42.16 ± 0.25 | 3,076 ± 20 | **+10.8%** ⚠️ |
| Qwen2.5-7B | 7B | FP16 | 28.37 ± 0.39 | 5,649 ± 83 | — |
| Qwen2.5-7B | 7B | NF4 | 34.29 ± 0.24 | 5,191 ± 37 | **−8.1%** ✅ |

---

## Paradox 2: bitsandbytes INT8 Energy Overhead

Default `LLM.int8()` (threshold=6.0) **increases** energy consumption by 17–147%.

### RTX 4090D — Default INT8 vs FP16 vs Pure INT8

| Model | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 | Δ vs Default INT8 |
|-------|-----------|-------------------|-------------------|-----------|-------------------|
| **Yi-1.5-6B** | FP16 | 34.72 ± 0.18 | 4,716 ± 119 | — | — |
| Yi-1.5-6B | INT8 Default | 8.42 ± 0.03 | 6,258 ± 78 | **+32.7%** ⚠️ | — |
| Yi-1.5-6B | INT8 Pure (t=0.0) | 15.47 ± 0.08 | 4,568 | **−3.1%** ✅ | **−34.2%** ✅ |
| **Mistral-7B** | FP16 | 29.06 ± 0.10 | 5,661 ± 143 | — | — |
| Mistral-7B | INT8 Default | 7.88 ± 0.03 | 7,401 ± 115 | **+30.7%** ⚠️ | — |
| Mistral-7B | INT8 Pure (t=0.0) | 14.15 ± 0.23 | 5,212 | **−7.9%** ✅ | **−36.9%** ✅ |
| **Average** | — | — | — | **+31.7%** ⚠️ | — |
| **Average (Pure)** | — | — | — | **−5.5%** ✅ | **−35.6%** ✅ |

### A800 — INT8 Overhead Is Even Worse on Datacenter GPUs

| Model | BS | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 |
|-------|---|-----------|-------------------|-------------------|-----------|
| Mistral-7B | 1 | FP16 | 36.18 | 4,334 | — |
| Mistral-7B | 1 | INT8 Default | 9.87 | 9,608 | **+122%** ⚠️ |
| Mistral-7B | 1 | INT8 Pure | 18.09 | 5,781 | +33% |
| Mistral-7B | 4 | FP16 | 145.35 | 1,100 | — |
| Mistral-7B | 4 | INT8 Default | 35.91 | 2,718 | **+147%** ⚠️ |
| Mistral-7B | 4 | INT8 Pure | 72.96 | 1,580 | +44% |
| Mistral-7B | 8 | FP16 | 290.59 | 628 | — |
| Mistral-7B | 8 | INT8 Default | 69.88 | 1,417 | **+126%** ⚠️ |
| Mistral-7B | 8 | INT8 Pure | 144.32 | 827 | +32% |

**Root Cause — Mixed-Precision Decomposition:**
1. `LLM.int8()` with `threshold=6.0` detects "outlier" features (magnitude > 6.0)
2. Outlier features are extracted and computed in FP16
3. Remaining features computed in INT8
4. Results merged back → continuous INT8↔FP16 type conversion at every linear layer
5. This causes 72–76% throughput loss, which dominates the 25% power reduction

**Ablation Proof:**
Setting `llm_int8_threshold=0.0` disables the decomposition entirely:
- All features processed in INT8 (no outlier extraction)
- Throughput recovery: **+79–98%** vs default INT8
- Energy reduction: **−34–42%** vs default INT8
- Net vs FP16: **−3% to −8%** energy savings (RTX 4090D), **+32–44%** penalty still on A800

**Code to reproduce:**
```python
# Default INT8 (ENERGY WASTEFUL — avoid this)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,
    # llm_int8_threshold defaults to 6.0
)

# Pure INT8 (ENERGY EFFICIENT — use this instead)
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=0.0,  # ← This one line saves 34–42% energy
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
)
```

---

## Paradox 3: BS=1 Waste (A800)

Single-request inference wastes up to 95.7% of available energy efficiency.

See `batch_size_guide.md` for complete data.

---

## Summary Decision Matrix

| Model Size | GPU VRAM | Best Precision | Avoid | Notes |
|-----------|----------|---------------|-------|-------|
| ≤3B | Any | **FP16** | NF4 (+11–29%) | No memory pressure, dequant overhead dominates |
| 6–7B | ≤24GB | **NF4** | INT8 default (+17–33%) | Memory savings dominate |
| 6–7B | ≥80GB | **FP16 or Pure INT8** | INT8 default (+122–147%) | No memory pressure |
| Any | Any | — | INT8 default (always) | Always set threshold=0.0 if using INT8 |

## Quality Metrics

- All measurements: n=10 runs per configuration
- Coefficient of Variation: 0.3–1.7% (throughput), <5% (power)
- Cross-model consistency: ±3.5%
- Thermal stabilization: 30s between model loads
- Warmup: 3 runs discarded
