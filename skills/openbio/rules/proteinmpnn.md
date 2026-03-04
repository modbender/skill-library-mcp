# ProteinMPNN Sequence Design

## Overview

ProteinMPNN (Protein Message Passing Neural Network) is a deep learning framework for protein sequence design. It takes protein backbone structures as input and generates amino acid sequences predicted to be compatible with those structures.

### When to Use ProteinMPNN
- Design new sequences for existing backbone structures
- Redesign protein surface residues
- Stabilize proteins via conservative design
- Design multi-chain complex interfaces
- Generate diverse sequence variants

### When NOT to Use
- Ligand in binding site → Use LigandMPNN
- Need thermostability focus → Use ThermoMPNN
- Need de novo backbone → Use BoltzGen or Pinal
- Have only sequence → Need structure first (Boltz/Chai)

## Decision Tree

```
What do you need to design?
│
├─ Protein with ligand bound?
│   └─ NO: submit_proteinmpnn_prediction ✓
│   └─ YES: Use LigandMPNN instead
│
├─ Priority is soluble expression?
│   └─ submit_proteinmpnn_prediction with use_soluble_model: true
│
├─ Need fast processing?
│   └─ submit_proteinmpnn_prediction with ca_only: true
│
├─ Multi-chain complex?
│   └─ submit_proteinmpnn_prediction with pdb_path_chains: "A B"
│
└─ Need reproducible results?
    └─ submit_proteinmpnn_prediction with seed: 42
```

## Parameters

### Core Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `num_seq_per_target` | int | 1-50 | 1 | Sequences to generate |
| `sampling_temp` | string | "0.1"-"1.0" | "0.1" | Temperature (string!) |
| `use_soluble_model` | bool | - | false | Enhanced solubility |
| `ca_only` | bool | - | false | CA-only for speed |
| `seed` | int | 0-2147483647 | None | Random seed |
| `pdb_path_chains` | string | - | None | Chains to design (e.g., "A B") |
| `backbone_noise` | float | 0.0-0.5 | None | Noise for diversity |

### Temperature Guide

| Temperature | Diversity | Quality | Use For |
|-------------|-----------|---------|---------|
| 0.1 | Low | High | Production, conservative |
| 0.2 | Moderate | Good | Default exploration |
| 0.3 | Higher | Moderate | Initial screening |
| 0.5+ | Very high | Lower | Maximum diversity |

**IMPORTANT**: Temperature must be passed as a **string**, not float!

## Quality Metrics

### Output Header Format
```
>protein_0001, score=1.234, global_score=1.189, seq_recovery=0.82
MKTAYIAKQRQISFVKSHFSRQLEERGLTKE...
```

### Interpreting Scores

| Metric | Good | Acceptable | Investigate |
|--------|------|------------|-------------|
| score | < 1.5 | 1.5-2.5 | > 2.5 |
| seq_recovery (de novo) | 0.3-0.5 | 0.5-0.6 | > 0.7 (too conservative) |
| seq_recovery (redesign) | 0.6-0.8 | 0.5-0.6 | < 0.4 |

- **Lower scores** = better sequence-structure compatibility
- **Higher seq_recovery** = more conservative design

## Model Selection

| Model | Use Case | Speed |
|-------|----------|-------|
| Standard (default) | General protein design | Normal |
| Soluble (`use_soluble_model: true`) | E. coli expression | Normal |
| CA-only (`ca_only: true`) | Large structures, fast | Fast |

## Common Mistakes

### Wrong: Float temperature
```
❌ sampling_temp: 0.1  # May cause errors
```
```
✅ sampling_temp: "0.1"  # String with quotes
```

### Wrong: Space in chain specification
```
❌ pdb_path_chains: "A, B"  # Space after comma
```
```
✅ pdb_path_chains: "A B"  # Space-separated, no commas
```

### Wrong: Not fixing critical residues
```
❌ Redesigning catalytic residues in enzyme
```
```
✅ Use fixed_positions in LigandMPNN or redesign specific chains only
```

## API Usage

### Basic Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_proteinmpnn_prediction" \
  -F 'params={
    "input_file_path": "structures/my_protein.pdb",
    "num_seq_per_target": 8,
    "sampling_temp": "0.1",
    "seed": 42
  }'
```

### Soluble Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_proteinmpnn_prediction" \
  -F 'params={
    "input_file_path": "structures/my_protein.pdb",
    "use_soluble_model": true,
    "num_seq_per_target": 5,
    "sampling_temp": "0.2"
  }'
```

### Multi-Chain Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_proteinmpnn_prediction" \
  -F 'params={
    "input_file_path": "structures/complex.pdb",
    "pdb_path_chains": "A B",
    "num_seq_per_target": 4,
    "sampling_temp": "0.15"
  }'
```

### High Diversity
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_proteinmpnn_prediction" \
  -F 'params={
    "input_file_path": "structures/scaffold.pdb",
    "sampling_temp": "0.5",
    "backbone_noise": 0.1,
    "num_seq_per_target": 10
  }'
```

## Sample Output

### Successful Job Response
```json
{
  "success": true,
  "job_id": "proteinmpnn_xyz789",
  "message": "Job submitted successfully",
  "estimated_runtime": "2-5 minutes"
}
```

### Output FASTA Header
```
>protein_0001, score=1.234, global_score=1.189, seq_recovery=0.82
MKTAYIAKQRQISFVKSHFSRQLEERGLTKE...
>protein_0002, score=1.198, global_score=1.156, seq_recovery=0.79
MKTAYIAKQRQISFVKSQFSRQLDERGLTKE...
```

### What Good Output Looks Like
- **Score**: 1.0-2.0 (lower = more confident)
- **Seq recovery**: 0.3-0.6 for de novo, 0.7-0.9 for redesign
- **Diverse sequences** (not all identical) when temp > 0.1

## Expected Runtime

| Protein Size | Sequences | Time |
|--------------|-----------|------|
| Small (<100 aa) | 1-3 | 1-2 min |
| Medium (100-500 aa) | 3-10 | 2-5 min |
| Large (>500 aa) | 5-10 | 5-15 min |

## Typical Performance

| Campaign Size | Time | Notes |
|---------------|------|-------|
| 10 backbones × 8 seq | 5-10 min | Quick test |
| 100 backbones × 8 seq | 30-60 min | Standard |
| 500 backbones × 16 seq | 2-4 hours | Large campaign |

**Throughput**: ~50-100 sequences/minute for typical proteins.

## Verify Success

```bash
# Check job status
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Count generated sequences (should match num_seq_per_target)
# Download FASTA and count headers
grep -c "^>" output.fa
```

## Tool Comparison

| Variant | Use Case | Key Difference |
|---------|----------|----------------|
| ProteinMPNN | General protein design | Standard model |
| SolubleMPNN (`use_soluble_model: true`) | Bacterial expression | Trained on soluble proteins |
| LigandMPNN | Small molecules/metals | Ligand-aware context |
| CA-only (`ca_only: true`) | Large structures | Faster, backbone only |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid PDB format` | Bad format | Check ATOM records, proper formatting |
| `Chain not found` | Wrong chain ID | Verify chain exists in PDB (`grep "^ATOM" file.pdb \| cut -c22 \| sort -u`) |
| `Temperature error` | Float instead of string | Use `"0.1"` not `0.1` |
| `File too large` | >50MB | Reduce or use CA-only |
| `All identical sequences` | Temperature too low | Increase to 0.2-0.3 |
| `Low quality sequences` | Temperature too high | Decrease to 0.1-0.15 |
| `IndexError: list index` | Empty chain or residue list | Check PDB has atoms, not just HEADER |

### Failure Recovery

```
Low sequence diversity?
├── Increase temperature
│   └── sampling_temp: "0.2" or "0.3"
├── Add backbone noise
│   └── backbone_noise: 0.1
└── Generate more sequences
    └── num_seq_per_target: 16-32

High scores (> 2.5)?
├── Backbone may be strained
│   └── Check input structure geometry
├── Try lower temperature
│   └── sampling_temp: "0.1"
└── Use different model
    └── use_soluble_model: true

Sequences don't fold correctly (high scRMSD)?
├── Lower temperature for more conservative design
│   └── sampling_temp: "0.1"
├── Increase sequences per target
│   └── num_seq_per_target: 32
└── Check backbone quality
    └── Regenerate backbone with different parameters
```

## Best Practices

1. **Start conservative**: Use temp 0.1-0.2 initially
2. **Use seeds**: Set seed for reproducible results
3. **Keep file size small**: <50MB for optimal performance
4. **Choose right model**:
   - Standard for general use
   - Soluble for bacterial expression
   - CA-only for large structures
5. **Validate with structure prediction**: Run Boltz/Chai on designed sequences

---

**Next**: Validate designed sequences with `Boltz` or `Chai` → Use `ThermoMPNN` to check stability.
