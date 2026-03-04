# SimpleFold Protein Structure Prediction

## Overview

SimpleFold is a protein structure prediction model developed by Apple that uses flow-matching generative modeling. It employs general-purpose transformer layers and achieves competitive performance on standard folding benchmarks.

### When to Use SimpleFold
- Quick single-protein structure prediction
- Sequence-only input (no MSA needed)
- Initial screening before detailed analysis
- Proteins where Boltz/Chai might be overkill

### When NOT to Use
- Protein complexes → Use Boltz or Chai
- Protein-ligand complexes → Use Boltz or Chai
- Need binding affinity → Use Boltz-2
- Need highest accuracy → Use Boltz/Chai

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `sequence` | string | Amino acid sequence |

### Optional

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `output_name` | string | - | "predicted_protein" | Output filename |
| `output_dir` | string | - | auto | Output directory |
| `num_steps` | int | 50-1000 | 500 | Inference steps |
| `tau` | float | 0.01-1.0 | 0.05 | Stochasticity scale |

## Performance Settings

| Goal | num_steps | tau | Runtime |
|------|-----------|-----|---------|
| Fast | 200 | 0.1 | 3-5 min |
| Balanced | 500 | 0.05 | 5-15 min |
| High accuracy | 750 | 0.03 | 15-30 min |

## Quality Thresholds

### pLDDT Scores

| pLDDT | Confidence | Interpretation |
|-------|------------|----------------|
| > 90 | Very high | Excellent prediction |
| 70-90 | High | Reliable structure |
| 50-70 | Low | Use with caution |
| < 50 | Very low | Likely disordered |

### Interpreting Results

- **Well-folded regions**: High pLDDT (>70)
- **Flexible loops**: Lower pLDDT (50-70)
- **Disordered regions**: Very low pLDDT (<50)
- **Domain boundaries**: Often show confidence transitions

## Output

### Files Generated
- **mmCIF structure**: Atomic coordinates
- **B-factor column**: Contains pLDDT scores per residue

### Using Results
1. Load in PyMOL/ChimeraX
2. Color by B-factor to visualize confidence
3. High B-factor = high confidence regions

## API Usage

### Basic Prediction
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_simplefold_prediction" \
  -F 'params={
    "sequence": "MKLLHVPLRRGTRYKLLKKKLSLPNPSLRTLGCISVIIVMSLGDPTNAGMHT"
  }'
```

### High Accuracy
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_simplefold_prediction" \
  -F 'params={
    "sequence": "MKLLHVPLRRGTRYKLLKKKLSLPNPSLRTLGCISVIIVMSLGDPTNAGMHT",
    "output_name": "my_protein",
    "num_steps": 750,
    "tau": 0.03
  }'
```

### Fast Prediction
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_simplefold_prediction" \
  -F 'params={
    "sequence": "MKLLHVPLRRGTRYKLLKKKLSLPNPSLRTLGCISVIIVMSLGDPTNAGMHT",
    "num_steps": 200,
    "tau": 0.1
  }'
```

### Get Tool Info
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_simplefold_tool_info" \
  -F 'params={}'
```

## Expected Runtime

| Sequence Length | Default | Fast | High Accuracy |
|-----------------|---------|------|---------------|
| Short (<100 aa) | 5 min | 3 min | 10 min |
| Medium (100-300 aa) | 10 min | 5 min | 20 min |
| Long (>300 aa) | 15 min | 8 min | 30 min |

## Rate Limits

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **Max sequence**: ~2000 residues
- **Timeout**: 30 minutes

## Common Mistakes

### Wrong: Non-standard amino acids
```
❌ sequence: "MKLLHXPLRR"  # X is non-standard
```
```
✅ sequence: "MKLLHAPLRR"  # Standard 20 AAs only
```

### Wrong: FASTA format
```
❌ sequence: ">protein\nMKLLH..."  # FASTA header
```
```
✅ sequence: "MKLLH..."  # Plain sequence only
```

### Wrong: Too long for resources
```
❌ sequence: (3000+ amino acids)
```
```
✅ Keep under ~2000 residues
   Split into domains if needed
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Timeout | Long sequence | Reduce num_steps |
| Low confidence | Difficult target | Increase num_steps |
| Memory error | Sequence too long | Keep under 1500 aa |
| Invalid sequence | Non-standard AA | Use only standard 20 |

## Best Practices

1. **Validate sequence**: Standard 20 AAs only
2. **Start with defaults**: 500 steps, 0.05 tau
3. **Check confidence**: Focus on pLDDT > 70 regions
4. **Consider alternatives**: For complexes, use Boltz/Chai
5. **Compare methods**: Run SimpleFold + Boltz for important proteins

## Sample Output

### Job Response
```json
{
  "success": true,
  "job_id": "simplefold_xyz789",
  "message": "Job submitted successfully",
  "estimated_runtime": "5-10 minutes"
}
```

### What Good Output Looks Like
- **pLDDT > 70**: Reliable per-residue confidence
- **B-factor column**: Contains pLDDT scores
- **mmCIF file**: ~50-200 KB for typical protein

## Typical Performance

| Sequence Length | Time |
|-----------------|------|
| Short (<100 aa) | 3-5 min |
| Medium (100-300 aa) | 5-10 min |
| Long (>300 aa) | 10-15 min |

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Verify structure file exists
ls *.cif
```

## SimpleFold vs Boltz/Chai

| Feature | SimpleFold | Boltz | Chai |
|---------|------------|-------|------|
| Speed | **Fast** | Moderate | Moderate |
| Single protein | Good | Excellent | Excellent |
| Complexes | No | **Yes** | **Yes** |
| Ligands | No | **Yes** | **Yes** |
| Binding affinity | No | **Yes (v2)** | No |
| MSA-free | **Yes** | Optional | No |

**Use SimpleFold for**: Quick single-protein predictions, initial screening
**Use Boltz/Chai for**: Complexes, ligands, production-quality structures

---

**Next**: For complexes → Use `Boltz` or `Chai`. For sequence optimization → Use `ProteinMPNN`.
