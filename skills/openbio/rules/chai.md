# Chai-1 Multi-Modal Molecular Structure Prediction

## Overview

Chai-1 is a multi-modal foundation model for molecular structure prediction. It performs at state-of-the-art levels across various benchmarks and enables unified prediction of proteins, small molecules, DNA, RNA, glycosylations using diffusion-based modeling.

### When to Use Chai
- Multi-modal structure prediction (proteins + ligands + nucleic acids + glycans)
- Protein-ligand complex structures
- Protein-RNA/DNA complexes
- Glycoprotein structures
- Modified residue handling

### When NOT to Use
- Binding affinity needed → Use Boltz-2 (supports affinity)
- Simple protein only → Consider SimpleFold (faster)
- Just need sequence design → Use ProteinMPNN

## Decision Tree

```
What do you need to predict?
│
├─ Protein + small molecule?
│   └─ submit_chai_prediction
│       → Format: >ligand|name=X followed by SMILES
│
├─ Protein + RNA/DNA?
│   └─ submit_chai_prediction
│       → Format: >rna|name=X or >dna|name=X
│
├─ Protein + glycan?
│   └─ submit_chai_prediction
│       → Format: >glycan|name=X
│
└─ Protein with modified residues?
    └─ submit_chai_prediction
        → Format: Sequence with (MOD) notation
```

## Input Format

### FASTA with Entity Type Headers

```
>entity_type|name=entity_name
SEQUENCE
```

### Supported Entity Types

**1. Protein Sequences**
```
>protein|name=example-protein
AGSHSMRYFSTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASPRGEPRAPWVEQEGPEYWDRETQK
```

**2. Ligands (SMILES)**
```
>ligand|name=aspirin
CC(=O)OC1=CC=CC=C1C(=O)O
```

**3. RNA Sequences**
```
>rna|name=example-rna
AUGGCCAUUGUAAUGGGCCGC
```

**4. DNA Sequences**
```
>dna|name=example-dna
ATGGCCATTGTAATGGGCCGC
```

**5. Glycans**
```
>glycan|name=example-glycan
NAG(4-1 NAG)
```

**6. Modified Residues**
```
>protein|name=modified-protein
RKDES(SEP)EES
```

### Multi-Entity Complex Example
```
>protein|name=receptor
MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG
>ligand|name=small-molecule
CCCCCCCCCCCCCC(=O)O
>glycan|name=sugar
NAG(4-1 NAG)
```

## Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `num_trunk_recycles` | int | 3 | 1-10 | Trunk model recycles |
| `num_diffn_timesteps` | int | 200 | 50-500 | Diffusion steps |
| `num_diffn_samples` | int | 5 | 1-10 | Structures to generate |
| `use_esm_embeddings` | bool | True | - | ESM embeddings for accuracy |
| `seed` | int | None | 0-999999 | Random seed |

## Quality Thresholds

### Confidence Metrics

| Metric | Range | Good | Interpret |
|--------|-------|------|-----------|
| pLDDT | 0-100 | > 70 | Per-residue confidence |
| PAE | Variable | Lower better | Aligned error |
| PDE | Variable | Lower better | Distance error |

### Interpreting Results

- **pLDDT > 70**: Generally good structure
- **pLDDT 50-70**: Low confidence, use with caution
- **pLDDT < 50**: Likely disordered or unreliable

## Output Files

### Directory Structure
```
output_folder/
├── pred_0.cif          # Best predicted structure
├── pred_1.cif          # Second best structure
├── ...
├── scores.model_idx_0.npz   # Confidence metrics
├── scores.model_idx_1.npz
├── ranking_data.json        # Model rankings
└── msa_coverage.pdf         # If MSAs used
```

### Using ranking_data.json

Rank structures by quality:
1. Load `ranking_data.json`
2. Sort by aggregate score
3. Use top-ranked structure for analysis

## Performance Settings

| Goal | Parameters | Notes |
|------|------------|-------|
| Fast | recycles: 3, timesteps: 200, samples: 1-3, ESM: false | Quick screening |
| Balanced | defaults | Recommended |
| High accuracy | recycles: 5-7, timesteps: 300-400, samples: 5-10, ESM: true | Critical predictions |

## Rate Limits

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **File size**: 50MB
- **Runtime**: 5-30 minutes depending on complexity

## API Usage

### Submit Prediction
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_chai_prediction" \
  -F 'params={
    "input_file_path": "inputs/complex.fasta",
    "num_trunk_recycles": 5,
    "num_diffn_timesteps": 300,
    "num_diffn_samples": 5,
    "use_esm_embeddings": true,
    "seed": 42
  }'
```

### Poll Job Status
```bash
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```

### Get Results
```bash
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Invalid header | Wrong entity type format | Use `>entity_type\|name=X` |
| Too many tokens | Sequence too long | Reduce sequence length |
| Invalid entity type | Typo in header | Check: protein, ligand, rna, dna, glycan |
| Processing timeout | Large complex | Reduce parameters |
| Low confidence | Poor input | Increase recycles/timesteps |

## Best Practices

1. **Input Preparation**
   - Use clear entity type headers
   - Validate SMILES strings for ligands
   - Keep sequences to reasonable lengths

2. **Parameter Selection**
   - Start with defaults for initial testing
   - Increase parameters for production runs
   - Use reproducible seeds for consistent results

3. **Result Analysis**
   - Check confidence scores (pLDDT > 70)
   - Compare multiple samples
   - Use `ranking_data.json` to identify best structures

## Sample Output

### Successful Job Response
```json
{
  "success": true,
  "job_id": "chai_xyz123abc456",
  "message": "Job submitted successfully",
  "estimated_runtime": "10-20 minutes"
}
```

### Output Directory
```
predictions/
├── pred_0.cif          # Best predicted structure
├── pred_1.cif          # Second best structure
├── scores.model_idx_0.npz
├── ranking_data.json   # Model rankings
└── msa_coverage.pdf    # If MSAs used
```

### What Good Output Looks Like
- **pTM > 0.7**: Confident global structure
- **ipTM > 0.5**: Confident interface (> 0.7 for high confidence)
- **pLDDT > 70**: Per-residue confidence
- **CIF files**: With reasonable atom positions

## Typical Performance

| Campaign Size | Time | Notes |
|---------------|------|-------|
| 1 complex | 10-20 min | Single validation |
| 10 complexes | 1-2 hours | Small batch |
| 100 complexes | 8-16 hours | Standard campaign |

**Per-complex**: ~10-20 min for typical binder-target complex.

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# After downloading, verify CIF files exist
ls *.cif | wc -l  # Should match num_diffn_samples
```

### Failure Recovery

```
Low pLDDT across predictions?
├── Increase recycles
│   └── num_trunk_recycles: 5-7
├── Check sequence quality
│   └── Validate amino acids, SMILES strings
└── Try with more samples
    └── num_diffn_samples: 8-10

Low ipTM (interface quality)?
├── Check chain order in FASTA
│   └── Ensure multiple chains present
├── Interface region may be disordered
│   └── Check if binding region is well-defined
└── Try Boltz-2 for comparison
    └── Different models may capture different features
```

## Chai vs Boltz Comparison

| Feature | Chai-1 | Boltz-2 |
|---------|--------|---------|
| Binding affinity | No | **Yes** |
| Glycans | **Yes** | Limited |
| Multi-modal | **Strong** | Strong |
| Speed | Moderate | Moderate |
| MSA-free option | No | **Yes** |
| Best for | Multi-modal complexes | Affinity prediction |

---

**Next**: After validation → Use `ProteinMPNN/LigandMPNN` for sequence optimization or `ThermoMPNN` for stability.
