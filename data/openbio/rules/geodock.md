# GeoDock Protein-Protein Docking

## Overview

GeoDock is a deep learning-based tool for protein-protein docking. It uses graph neural networks (GNN) and ESM-2 protein language models to predict binding poses between two proteins.

### When to Use GeoDock
- Predict protein-protein complex structures
- Homodimer prediction (self-docking)
- Heterodimer prediction (two different proteins)
- Quick docking without MD refinement

### When NOT to Use
- Need protein-ligand docking → Use Boltz or Chai
- Need structure prediction → Use Boltz, Chai, or SimpleFold
- Need high-accuracy complex → Use Boltz (better for multi-chain)

## Decision Tree

```
What do you need to dock?
│
├─ Protein binding to itself (homodimer)?
│   └─ submit_geodock_prediction
│       → input_file_path only (self-docking)
│
├─ Two different proteins?
│   └─ submit_geodock_prediction
│       → input_file_path: protein1.pdb
│       → protein2_file_path: protein2.pdb
│
└─ Need binding affinity?
    └─ Use Boltz-2 instead (supports affinity)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input_file_path` | string | Yes | PDB file for protein 1 |
| `protein2_file_path` | string | No | PDB file for protein 2 (omit for self-docking) |
| `output_name` | string | No | Output filename prefix (default: "docked_complex") |
| `output_directory` | string | No | Output directory |

## Input Requirements

### PDB Format
- Standard PDB format with ATOM records
- Valid 3D coordinates
- Both experimental and predicted structures work

### Example PDB
```
ATOM      1  N   SER A  96      13.651 -16.577  32.202  1.00 46.57           N  
ATOM      2  CA  SER A  96      12.392 -17.077  32.829  1.00 45.90           C  
...
END
```

### Recommendations
- Remove ligands and waters unless needed
- Single chain per file preferred
- Check residue numbering is continuous

## Output

### Directory Structure
```
predictions/{job_id}/
└── {output_name}.pdb    # Docked complex
```

### Output PDB
- Contains both protein chains in docked orientation
- Standard PDB format
- Can be visualized in PyMOL, ChimeraX, etc.

## API Usage

### Homodimer (Self-Docking)
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_geodock_prediction" \
  -F 'params={
    "input_file_path": "proteins/protein.pdb",
    "output_name": "homodimer"
  }'
```

### Heterodimer (Two Proteins)
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_geodock_prediction" \
  -F 'params={
    "input_file_path": "proteins/receptor.pdb",
    "protein2_file_path": "proteins/ligand_protein.pdb",
    "output_name": "complex"
  }'
```

### Get Tool Info
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_geodock_tool_info" \
  -F 'params={}'
```

## Expected Runtime

| Protein Size | Time |
|--------------|------|
| Small (<200 aa) | 25-30 sec |
| Medium (200-400 aa) | 30-60 sec |
| Large (>400 aa) | 60-120 sec |

## Rate Limits

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **File size**: 10MB maximum
- **Timeout**: 30 minutes

## Quality Assessment

### Visual Inspection
Load output in molecular viewer and check:
- Reasonable contact interface
- No severe clashes
- Chemically sensible interactions

### Interface Analysis
- Buried surface area should be reasonable
- Complementary charges at interface
- Hydrophobic/hydrophilic compatibility

### Quality Indicators
| Indicator | Good | Poor |
|-----------|------|------|
| Interface contacts | Many | Few/none |
| Atomic clashes | Minimal | Severe |
| Buried surface | 800-2000 Å² | < 500 Å² |

## Common Mistakes

### Wrong: Multi-chain input file
```
❌ Single PDB with chains A and B
   → GeoDock may misinterpret
```
```
✅ Separate PDB files:
   → input_file_path: chainA.pdb
   → protein2_file_path: chainB.pdb
```

### Wrong: Including ligands
```
❌ PDB with bound ligands/waters
```
```
✅ Clean PDB with protein only
   Remove HETATM records if not needed
```

### Wrong: Incomplete structures
```
❌ PDB with missing regions
```
```
✅ Use complete structures
   Fill gaps with modeling if needed
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Timeout | Large proteins | Ensure <500 residues per protein |
| Invalid PDB | Bad format | Check ATOM records, coordinates |
| Memory error | Complex too large | Use smaller structures |
| No output | Modal issue | Retry submission |

## Next Steps After Docking

1. **Structure validation**
   - MolProbity geometry check
   - Ramachandran analysis

2. **Interface analysis**
   - Identify contact residues
   - Analyze interaction types

3. **Energy calculations**
   - Molecular mechanics scoring
   - Binding energy estimation

4. **Refinement**
   - Molecular dynamics equilibration
   - Energy minimization

5. **Experimental validation**
   - Design mutagenesis experiments
   - Test predicted contacts

## Sample Output

### Job Response
```json
{
  "success": true,
  "job_id": "geodock_abc123",
  "message": "Job submitted successfully",
  "estimated_runtime": "30-60 seconds"
}
```

### Output PDB
- Single PDB file with both chains in docked orientation
- Standard PDB format
- Can be visualized immediately in PyMOL/ChimeraX

### What Good Output Looks Like
- **Reasonable contact interface**: Many atom-atom contacts
- **No severe clashes**: Minimal steric clashes
- **Buried surface**: 800-2000 Å² at interface

## Typical Performance

| Protein Size | Time |
|--------------|------|
| Small (<200 aa each) | 25-30 sec |
| Medium (200-400 aa) | 30-60 sec |
| Large (>400 aa) | 60-120 sec |

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Verify both chains present in output
grep "^ATOM" docked.pdb | cut -c22 | sort -u
# Should show both chain IDs
```

## GeoDock vs Boltz for Complexes

| Feature | GeoDock | Boltz |
|---------|---------|-------|
| Input | Two PDB files | Sequences or YAML |
| Speed | **Fast (30-60 sec)** | Slower (10-30 min) |
| Binding affinity | No | **Yes (Boltz-2)** |
| Accuracy | Good | **Generally better** |
| Use case | Quick docking | Production complexes |

**Recommendation**: Use GeoDock for quick screening, Boltz for final structures.

---

**Next**: Analyze interface → Refine with molecular dynamics or validate with `Boltz` for higher accuracy.
