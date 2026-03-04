# Metrics and Token Budgeting

## Measuring Compression

### Primary Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Compression ratio | `len(compressed) / len(original)` | Depends on level |
| Token reduction | `original_tokens - compressed_tokens` | Higher = better |
| Validation score | `matched_facts / total_facts` | Must be 1.0 |
| Iterations needed | Count of refine loops | ≤3 |

### Expected Ratios by Level

| Level | Token Ratio | Character Ratio |
|-------|-------------|-----------------|
| L1 | 0.75-0.85 | 0.70-0.80 |
| L2 | 0.45-0.55 | 0.40-0.50 |
| L3 | 0.25-0.35 | 0.20-0.30 |
| L4 | 0.10-0.20 | 0.08-0.15 |

---

## Fit to Budget

When you need to fit content into a token limit:

```
function fit_to_budget(content, max_tokens):
    current_tokens = count_tokens(content)
    
    if current_tokens <= max_tokens:
        return content  # Already fits
    
    # Calculate required ratio
    required_ratio = max_tokens / current_tokens
    
    # Select appropriate level
    if required_ratio > 0.75: level = L1
    elif required_ratio > 0.45: level = L2
    elif required_ratio > 0.25: level = L3
    else: level = L4
    
    compressed = compress_lossless(content, level)
    
    if count_tokens(compressed) > max_tokens:
        # Need to chunk or escalate
        return chunk_and_compress(content, max_tokens)
    
    return compressed
```

---

## Cost Estimation

For API cost planning:

```
Monthly savings = (original_tokens - compressed_tokens) × requests_per_month × cost_per_token

Example:
- System prompt: 2000 tokens → 800 tokens (L2)
- Savings per request: 1200 tokens
- 10,000 requests/month at $0.01/1K tokens
- Monthly savings: 1200 × 10,000 × $0.00001 = $120
```

---

## Compression Report Template

```
═══════════════════════════════════════
COMPRESSION REPORT
═══════════════════════════════════════

Input
  Type: [code/markdown/prompt/json/conversation]
  Tokens: [X]
  Characters: [Y]

Output
  Level: [L1/L2/L3/L4]
  Tokens: [X']
  Characters: [Y']

Performance
  Token ratio: [X'/X] ([%] reduction)
  Iterations: [N]
  Validation: [PASS/FAIL]

Preservation Check
  ✓ Entities: [N/N]
  ✓ Numbers: [N/N]
  ✓ Relationships: [N/N]
  ✓ Logic flow: [intact/modified]

[If applicable]
Mapping table stored: [location]
Decompression prompt: [included/separate]
═══════════════════════════════════════
```

---

## Incremental Compression

For versioned content:

```
v1: Full compression → store as base
v2: Compress only delta from v1
v3: Compress only delta from v2
...

Reconstruction: base + delta1 + delta2 + ...
```

Storage savings: ~70% vs independent compression

---

## Quality Thresholds

| Metric | Minimum | Warning | Fail |
|--------|---------|---------|------|
| Validation score | 1.0 | <1.0 | <0.95 |
| Iterations | ≤3 | 4 | ≥5 |
| Entity match | 100% | <100% | <95% |
| Number match | 100% | <100% | <100% |
