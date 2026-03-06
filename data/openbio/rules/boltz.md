# Boltz-2 Biomolecular Structure Prediction

## Overview

Boltz is an open-source family of biomolecular interaction prediction models. **Boltz-2** predicts 3D structures and binding affinities for proteins, DNA, RNA, and small molecules with physics-level accuracy.

### When to Use Boltz
- Protein structure prediction (single or multi-chain)
- Protein-ligand complex structures
- Binding affinity prediction
- DNA/RNA structure modeling
- Modified residues and covalent bonds

### When NOT to Use
- Just need inverse folding → Use ProteinMPNN/LigandMPNN
- Need protein-protein docking only → Use GeoDock  
- Simple single protein → Consider SimpleFold (faster)

## Decision Tree

```
What structure do you need?
│
├─ Single protein sequence?
│   └─ submit_boltz_prediction with FASTA
│
├─ Protein + small molecule?
│   └─ submit_boltz_prediction with YAML (recommended)
│       → Include "affinity" property for binding prediction
│
├─ Protein complex (multi-chain)?
│   └─ submit_boltz_prediction with multi-chain FASTA
│
└─ Need binding pocket constraints?
    └─ submit_boltz_prediction with YAML + constraints
```

## Input Formats

### FASTA Format (Simple Sequences)

Best for basic protein prediction:

```fasta
>A|protein
MKQHKAMIVALIVICITAVVAALVTRKDLCEVHIRTGQTEVAVF
>B|ligand|smiles
N[C@@H](Cc1ccc(O)cc1)C(=O)O
```

**Header Format**: `>CHAIN_ID|ENTITY_TYPE|ADDITIONAL_INFO`

**Entity Types**:
- `protein` - Amino acid sequences
- `dna` - DNA nucleotide sequences  
- `rna` - RNA nucleotide sequences
- `smiles` - Chemical notation for small molecules
- `ccd` - Chemical Components Dictionary codes

### YAML Format (Binding Affinity)

**Required for protein-ligand affinity prediction**:

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MVTPEGNVSLVDESLLVGVTDEDRAVRSAHQFYERLIGLWAPAVMEAAHELGVFAALAEAPAD
  - ligand:
      id: B
      smiles: 'N[C@@H](Cc1ccc(O)cc1)C(=O)O'
properties:
  - affinity:
      binder: B
```

### YAML Format (Binding Pocket)

For constrained pocket prediction:

```yaml
sequences:
  - protein:
      id: [A1]
      sequence: MYNMRRLSLSPTFSMGFHLLVTVSLLFSHVDHVIAETEMEGEGNETGECTGSYYCKKGV
  - ligand:
      ccd: EKY
      id: [B1]
constraints:
  - pocket:
      binder: B1
      contacts: [ [ A1, 829 ], [ A1, 138 ] ]
```

## Parameters

### Core Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `model` | string | boltz1, boltz2 | boltz2 | Model version (boltz2 recommended) |
| `recycling_steps` | integer | 1-10 | 3 | Refinement iterations |
| `sampling_steps` | integer | 50-500 | 200 | Diffusion steps |
| `diffusion_samples` | integer | 1-5 | 1 | Number of structure samples |

### Binding Affinity (Boltz-2 only)

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `diffusion_samples_affinity` | integer | 1-10 | Additional samples for binding affinity |

### Output Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_format` | string | mmcif | Structure format (mmcif/pdb) |
| `write_full_pae` | boolean | true | Save PAE matrices |
| `write_full_pde` | boolean | true | Save PDE matrices |
| `use_msa_server` | boolean | true | Use MSA server |

## Quality Thresholds

### Confidence Scores

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| confidence_score | > 0.9 | 0.7-0.9 | < 0.7 |
| ptm | > 0.8 | 0.5-0.8 | < 0.5 |
| iptm (interface) | > 0.78 | 0.5-0.78 | < 0.5 |
| complex_plddt | > 0.87 | 0.7-0.87 | < 0.7 |

### Interpreting Scores

- **PTM > 0.5**: Generally reliable fold
- **iPTM > 0.5**: Reliable interface for complexes
- **PDE < 2Å**: Excellent distance error, 2-4Å good
- **Affinity**: More negative = stronger binding, confidence > 0.8 is reliable

## Output Files

### Structure Files
- **Format**: mmCIF (default) or PDB
- **B-factor**: Contains per-residue confidence (pLDDT)

### Confidence JSON
```json
{
  "confidence_score": 0.85,
  "ptm": 0.82,
  "iptm": 0.78,
  "complex_plddt": 0.87,
  "complex_pde": 2.1
}
```

### Binding Affinity (Boltz-2)
```json
{
  "affinity": -8.5,
  "affinity_confidence": 0.92
}
```

## Performance Settings

| Goal | Parameters | Runtime |
|------|------------|---------|
| Fast | `sampling_steps: 100`, `recycling_steps: 1` | 5-10 min |
| Balanced | defaults | 10-20 min |
| High accuracy | `sampling_steps: 400`, `recycling_steps: 5` | 20-45 min |
| Protein-ligand | `diffusion_samples_affinity: 5`, `sampling_steps: 300` | 15-30 min |

## Rate Limits

- **Per minute**: 2 jobs maximum
- **Per day**: 10 jobs maximum
- **Burst**: 3 jobs in 5 minutes
- **File size**: 10MB maximum
- **Timeout**: 30 minutes

## API Usage

### Get Tool Info
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=get_boltz_tool_info" \
  -F 'params={}'
```

### Submit Prediction
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_boltz_prediction" \
  -F 'params={
    "input_file_path": "inputs/protein.yaml",
    "model": "boltz2",
    "recycling_steps": 3,
    "sampling_steps": 200
  }'
```

### Poll and Download
```bash
# Check status
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY"

# Get results with download URLs
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Timeout | Complex too large | Reduce sampling_steps, recycling_steps |
| Low confidence (<0.5) | Unreliable prediction | Check sequence quality, enable MSA |
| Memory error | Sequence too long | Keep under ~2000 residues |
| Invalid format | YAML syntax error | Validate YAML online |
| No affinity | Missing property | Add `properties: - affinity:` to YAML |

## Sample Output

### Successful Job Submission
```json
{
  "success": true,
  "job_id": "boltz_abc123def456",
  "message": "Job submitted successfully",
  "estimated_runtime": "15-20 minutes"
}
```

### Completed Job Response
```json
{
  "success": true,
  "job": {
    "job_id": "boltz_abc123def456",
    "status": "completed",
    "created_at": "2025-01-30T10:00:00Z",
    "completed_at": "2025-01-30T10:18:32Z"
  },
  "output_files_signed_urls": {
    "structure.cif": "https://s3.../structure.cif?...",
    "confidence.json": "https://s3.../confidence.json?..."
  }
}
```

### What Good Output Looks Like
- **pTM > 0.7**: Confident global structure
- **ipTM > 0.5**: Confident interface (> 0.7 for high confidence)
- **pLDDT > 0.7**: Confident per-residue predictions
- **CIF file**: ~100-500 KB for typical complex

## Typical Performance

| Campaign Size | Time | Notes |
|---------------|------|-------|
| 1 complex | 10-20 min | Single validation |
| 10 complexes | 1-2 hours | Small batch |
| 50 complexes | 4-8 hours | Standard campaign |
| 100 complexes | 8-16 hours | Large campaign |

**Per-complex**: ~10-20 min for typical binder-target complex.

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'
# Should return: "completed"

# Verify output files exist
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.output_files_signed_urls | keys'
# Should list: structure files, confidence.json
```

## Tool Comparison

| Feature | Boltz-2 | Chai-1 | SimpleFold |
|---------|---------|--------|------------|
| Single protein | ✓ | ✓ | ✓ |
| Multi-chain complex | ✓ | ✓ | ✗ |
| Small molecules | ✓ | ✓ | ✗ |
| RNA/DNA | ✓ | ✓ | ✗ |
| Glycans | Limited | ✓ | ✗ |
| **Binding affinity** | **✓** | ✗ | ✗ |
| MSA-free option | ✓ | ✗ | ✓ |
| Speed | Moderate | Moderate | **Fast** |
| Best for | Affinity, complexes | Multi-modal | Quick single protein |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Timeout` | Complex too large | Reduce sampling_steps, recycling_steps |
| `Low confidence (<0.5)` | Unreliable prediction | Check sequence quality, enable MSA |
| `CUDA out of memory` | Sequence too long | Keep under ~2000 residues, reduce diffusion_samples |
| `Invalid YAML` | Syntax error | Validate YAML online, check quotes on SMILES |
| `No affinity output` | Missing property | Add `properties: - affinity:` to YAML |
| `KeyError: 'iptm'` | Single chain only | Ensure input has 2+ chains for interface metrics |
| `File too large` | Input > 10MB | Compress or split input file |

### Failure Recovery

```
Low confidence across predictions?
├── Check sequence quality
│   └── Validate amino acid sequence (standard 20 AAs only)
├── Enable MSA server
│   └── use_msa_server: true (provides evolutionary context)
├── Increase sampling
│   └── sampling_steps: 300-400, recycling_steps: 5
└── Check if target is difficult
    └── Some proteins are intrinsically disordered
```

## Best Practices

1. **Start with defaults** for initial predictions
2. **Use YAML format** for protein-ligand complexes
3. **Increase sampling_steps** (200→400) for critical predictions
4. **Check confidence scores** - aim for > 0.7
5. **Use MSA server** unless you have specific reasons not to
6. **For binding affinity**: Set `diffusion_samples_affinity: 5`

---

**Next**: After structure prediction → Use `ThermoMPNN` for stability analysis or `ProteinMPNN/LigandMPNN` for sequence optimization.
