# ThermoMPNN Protein Stability Prediction

## Overview

ThermoMPNN is a graph neural network (GNN) trained using transfer learning to predict changes in thermodynamic stability (ΔΔG) for protein point mutations. It analyzes all possible single amino acid substitutions at each position.

### When to Use ThermoMPNN
- Predict mutation effects on stability
- Identify stabilizing mutations
- Screen mutation libraries
- Design thermostable variants
- Avoid destabilizing mutations

### When NOT to Use
- Need sequence design → Use ProteinMPNN/LigandMPNN
- Need structure prediction → Use Boltz/Chai
- Need binding affinity → Use Boltz-2

## What ThermoMPNN Does

**Site-Saturation Mutagenesis**: For each position in your protein, ThermoMPNN predicts how all 19 possible amino acid substitutions would affect stability.

- **Input**: Protein structure (PDB)
- **Output**: ΔΔG predictions for ~N × 19 mutations (N = protein length)

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_file_path` | string | Yes | Path to PDB file |
| `chain` | string | No | Specific chain to analyze (default: all) |
| `output_directory` | string | No | Custom output path |

## Interpreting ΔΔG Results

### ΔΔG Values (kcal/mol)

| ΔΔG | Effect | Action |
|-----|--------|--------|
| < -1.0 | **Stabilizing** | Good candidates for engineering |
| -1.0 to +1.0 | **Neutral** | Minimal impact |
| > +1.0 | **Destabilizing** | Avoid in design |

### Sign Convention
- **Negative ΔΔG**: Mutation stabilizes protein
- **Positive ΔΔG**: Mutation destabilizes protein

## Output Format

### CSV Results

| Column | Description |
|--------|-------------|
| `Mutation` | Mutation (e.g., A123V) |
| `ddG_pred` | Predicted ΔΔG in kcal/mol |
| `Position` | Residue position |
| `wildtype` | Original amino acid |
| `mutation` | Mutated amino acid |
| `Chain` | Chain identifier |

### Example Output
```csv
Mutation,ddG_pred,Position,wildtype,mutation,Chain
A123V,-1.2,123,A,V,A
A123G,0.3,123,A,G,A
S45F,-0.8,45,S,F,A
```

## Quality Guidelines

### Reliable Predictions
- Structured regions (high pLDDT in original structure)
- Buried core residues
- Well-resolved positions

### Less Reliable
- Flexible loops
- Disordered regions
- Surface-exposed termini

## API Usage

### Basic Analysis
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_thermompnn_prediction" \
  -F 'params={
    "input_file_path": "inputs/protein.pdb"
  }'
```

### Specific Chain
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_thermompnn_prediction" \
  -F 'params={
    "input_file_path": "inputs/protein.pdb",
    "chain": "A"
  }'
```

### Get Tool Info
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_thermompnn_tool_info" \
  -F 'params={}'
```

## Expected Runtime

| Protein Size | Time |
|--------------|------|
| Small (<200 aa) | 1-5 min |
| Medium (200-500 aa) | 5-15 min |
| Large (>500 aa) | 15-30 min |

**Scaling**: N residues × 19 mutations = N × 19 predictions

## Workflow: Find Stabilizing Mutations

```
1. Submit structure
   → submit_thermompnn_prediction

2. Poll until complete
   → GET /api/v1/jobs/{job_id}/status

3. Download results
   → GET /api/v1/jobs/{job_id}
   → Download CSV from signed URL

4. Filter stabilizing mutations
   → Sort by ddG_pred ascending
   → Select mutations with ddG < -1.0

5. Validate with structure prediction
   → Run Boltz on mutated sequence
   → Verify fold is maintained
```

## Common Mistakes

### Wrong: Using unclean PDB
```
❌ PDB with waters, ligands, alternate conformations
```
```
✅ Clean PDB with only protein ATOM records
```

### Wrong: Ignoring chain specification
```
❌ Analyzing multi-chain protein without specifying chain
   → Results may be mixed/confusing
```
```
✅ chain: "A" for focused analysis
```

### Wrong: Trusting all predictions equally
```
❌ Using ΔΔG for disordered loop region
```
```
✅ Focus on structured regions
   Cross-reference with pLDDT if structure is predicted
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| PDB format error | Non-standard format | Clean PDB, proper ATOM records |
| Chain not found | Wrong chain ID | Check chain IDs in PDB |
| Timeout | Very large protein | Analyze chains separately |
| Memory error | Complex too large | Split into domains |

## Best Practices

1. **Clean input structures**: Remove heteroatoms, waters if not needed
2. **Specify chain**: For multi-chain proteins
3. **Focus on significant changes**: |ΔΔG| > 1.0 kcal/mol
4. **Consider context**: Buried vs surface residues
5. **Validate experimentally**: Computational predictions need validation
6. **Combine with design**: Use results to guide ProteinMPNN design

## Sample Output

### Job Response
```json
{
  "success": true,
  "job_id": "thermompnn_abc123",
  "message": "Job submitted successfully",
  "estimated_runtime": "5-15 minutes"
}
```

### CSV Output Example
```csv
Mutation,ddG_pred,Position,wildtype,mutation,Chain
A5V,-1.8,5,A,V,A
A5G,0.2,5,A,G,A
S10F,-0.9,10,S,F,A
K15E,1.5,15,K,E,A
```

### What Good Output Looks Like
- **Many stabilizing mutations** (ΔΔG < -1.0) in structured regions
- **Consistent predictions** across similar positions
- **File size**: Proportional to N × 19 (residues × mutations)

## Typical Performance

| Protein Size | Time | Output Size |
|--------------|------|-------------|
| 100 aa | 2-3 min | ~1900 predictions |
| 300 aa | 5-10 min | ~5700 predictions |
| 500 aa | 10-20 min | ~9500 predictions |

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Count predictions (should be ~19 × num_residues)
wc -l output.csv
```

## Use Cases

1. **Protein Stabilization**
   - Identify mutations with ΔΔG < -1.0
   - Combine multiple stabilizing mutations
   - Validate with thermal denaturation assays

2. **Avoid Destabilizing**
   - Check designed sequences for destabilizing changes
   - Filter out mutations with ΔΔG > 1.5

3. **Rational Engineering**
   - Focus on specific positions
   - Compare all possible substitutions
   - Rank by predicted effect

---

**Next**: Apply stabilizing mutations → Validate with `Boltz/Chai` structure prediction.
