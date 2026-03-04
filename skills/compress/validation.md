# Validation Algorithm

## The Core Loop

```
function compress_lossless(original, target_level):
    compressed = compress(original, target_level)
    
    for iteration in 1..MAX_ITERATIONS:
        reconstructed = decompress(compressed)  # No access to original
        diff = semantic_diff(original, reconstructed)
        
        if diff.is_empty():
            return compressed  # Success: lossless
        
        # Refine: add missing information
        compressed = refine(compressed, diff.missing)
    
    # Failed to converge
    if target_level > L1:
        return compress_lossless(original, target_level - 1)
    else:
        return original  # Cannot compress losslessly
```

---

## Semantic Diff

Not just string comparison. Check:

### Must Match 100%
- Named entities (people, places, products)
- Numbers and measurements
- Dates and times
- Relationships between entities
- Causal chains (A causes B)
- Conditions and constraints

### Allowed to Differ
- Word choice (synonyms OK)
- Sentence structure
- Formatting
- Filler words

---

## Diff Commands

```bash
# Quick check: character diff
diff <(echo "$original") <(echo "$reconstructed")

# Semantic check: extract key facts
extract_entities "$original" > /tmp/orig_ents
extract_entities "$reconstructed" > /tmp/recon_ents
diff /tmp/orig_ents /tmp/recon_ents
```

---

## Refinement Strategy

When diff shows missing info:

1. **Identify gap type**
   - Missing entity → Add to entity table
   - Missing relationship → Add to relation graph
   - Missing detail → Expand abbreviated section

2. **Targeted addition**
   - Don't recompress everything
   - Inject only the missing piece
   - Re-validate just that section

3. **Format preservation**
   - Keep same compression notation
   - Maintain consistency with existing compressed text

---

## Convergence Metrics

| Iterations | Assessment |
|------------|------------|
| 1 | Excellent compression prompt |
| 2 | Normal |
| 3 | Borderline, consider lower level |
| >3 | Level too aggressive, auto-downgrade |

---

## Validation Report

After successful compression, output:

```
Compression Report
==================
Original: 4,521 tokens
Compressed: 1,806 tokens
Ratio: 0.40 (L2)
Iterations: 2
Validation: PASS

Entities preserved: 47/47 ✓
Numbers preserved: 12/12 ✓
Relationships preserved: 23/23 ✓
```
