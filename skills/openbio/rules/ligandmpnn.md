# LigandMPNN Ligand-Aware Sequence Design

## Overview

LigandMPNN extends ProteinMPNN to enable ligand-aware protein sequence design. It designs protein sequences optimized for interacting with ligands, small molecules, nucleotides, metals, and other non-protein components.

### When to Use LigandMPNN
- Protein with bound ligand/small molecule
- Enzyme design with substrate/cofactor
- Protein-DNA/RNA binding design
- Metalloprotein design
- Fixed binding site residues needed

### When NOT to Use
- No ligand present → Use ProteinMPNN (faster)
- Need de novo backbone → Use BoltzGen or Pinal
- Only need stability → Use ThermoMPNN

## Decision Tree

```
What do you need to design?
│
├─ Protein binding small molecule?
│   └─ submit_ligandmpnn_prediction
│       → ligand_mpnn_use_atom_context: true
│
├─ Enzyme with cofactor?
│   └─ submit_ligandmpnn_prediction
│       → fixed_residues: "A23 A45" (catalytic)
│       → ligand_mpnn_use_atom_context: true
│
├─ Need side chain packing?
│   └─ submit_ligandmpnn_prediction
│       → pack_side_chains: true
│       → pack_with_ligand_context: true
│
├─ Score existing sequence?
│   └─ submit_ligandmpnn_scoring
│
└─ Design specific residues only?
    └─ submit_ligandmpnn_prediction
        → redesigned_residues: "A10 A11 A12"
```

## Parameters

### Essential Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `temperature` | float | 0.01-1.0 | 0.1 | Sampling temperature |
| `batch_size` | int | 1-5 | 1 | Sequences per batch |
| `number_of_batches` | int | 1-10 | 1 | Number of batches |
| `seed` | int | 1-999999 | 111 | Random seed |
| `ligand_mpnn_use_atom_context` | bool | - | true | Use ligand atoms |

### Temperature Guide

| Temperature | Effect | Use Case |
|-------------|--------|----------|
| 0.01-0.05 | Very conservative | Critical binding sites |
| 0.1 | Conservative | Default, balanced |
| 0.2-0.3 | More diverse | Exploration |
| 0.5-1.0 | Very diverse | Maximum variation |

### Design Control Parameters

| Parameter | Format | Description |
|-----------|--------|-------------|
| `ligand_mpnn_cutoff_for_score` | 4.0-12.0 Å | Distance cutoff (default 8.0) |
| `fixed_residues` | "A10 A11 B5" | Keep these unchanged |
| `redesigned_residues` | "A10 A11 B5" | Only redesign these |
| `bias_AA` | "W:3.0,C:-5.0" | Amino acid biases |
| `omit_AA` | "CP" | Exclude these AAs |
| `chains_to_design` | "A,B" | Design only these chains |
| `parse_these_chains_only` | "A,B,C" | Parse only these chains |

### Side Chain Packing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pack_side_chains` | false | Enable full-atom packing |
| `number_of_packs_per_design` | 4 | Packing samples |
| `ligand_mpnn_use_side_chain_context` | false | Use fixed side chains |
| `repack_everything` | false | Repack all residues |
| `pack_with_ligand_context` | true | Consider ligands in packing |

## Quality Metrics

### Output Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| `overall_confidence` | Model confidence | 0.7-1.0 |
| `ligand_confidence` | Ligand region confidence | 0.7-1.0 |
| `seq_rec` | Sequence recovery | Context-dependent |
| `num_ligand_res` | Residues near ligand | Varies |

## Common Mistakes

### Wrong: Not using atom context
```
❌ ligand_mpnn_use_atom_context: false
   → Ignores ligand, acts like ProteinMPNN
```
```
✅ ligand_mpnn_use_atom_context: true
   → Considers ligand atoms during design
```

### Wrong: Cutoff too small
```
❌ ligand_mpnn_cutoff_for_score: 4.0
   → Misses important interactions
```
```
✅ ligand_mpnn_cutoff_for_score: 8.0
   → Default captures most binding site residues
```

### Wrong: Not fixing catalytic residues
```
❌ Redesigning entire enzyme including active site
```
```
✅ fixed_residues: "A23 A45 A67"
   → Preserve critical catalytic residues
```

### Wrong: Using both fixed and redesigned
```
❌ fixed_residues: "A10" AND redesigned_residues: "A20"
   → Mutually exclusive, behavior undefined
```
```
✅ Use ONE of:
   - fixed_residues (fix these, design rest)
   - redesigned_residues (only design these)
```

## API Usage

### Basic Ligand-Aware Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_ligandmpnn_prediction" \
  -F 'params={
    "input_file_path": "protein_with_ligand.pdb",
    "temperature": 0.1,
    "batch_size": 1,
    "number_of_batches": 2,
    "ligand_mpnn_use_atom_context": true
  }'
```

### Design with Fixed Binding Site
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_ligandmpnn_prediction" \
  -F 'params={
    "input_file_path": "enzyme_substrate.pdb",
    "temperature": 0.1,
    "batch_size": 1,
    "number_of_batches": 2,
    "fixed_residues": "A23 A45 A67 A89",
    "ligand_mpnn_use_atom_context": true
  }'
```

### Design with Side Chain Packing
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_ligandmpnn_prediction" \
  -F 'params={
    "input_file_path": "protein_ligand.pdb",
    "temperature": 0.1,
    "pack_side_chains": true,
    "number_of_packs_per_design": 4,
    "pack_with_ligand_context": true,
    "ligand_mpnn_use_atom_context": true
  }'
```

### Design with AA Restrictions
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_ligandmpnn_prediction" \
  -F 'params={
    "input_file_path": "protein.pdb",
    "temperature": 0.1,
    "omit_AA": "CP",
    "bias_AA": "S:2.0,T:2.0",
    "ligand_mpnn_use_atom_context": true
  }'
```

### Sequence Scoring
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_ligandmpnn_scoring" \
  -F 'params={
    "input_file_path": "designed_protein.pdb",
    "ligand_mpnn_use_atom_context": true,
    "ligand_mpnn_cutoff_for_score": 8.0
  }'
```

## Expected Runtime

| Protein Size | With Packing | Without Packing |
|--------------|--------------|-----------------|
| Small (<100 aa) | 3-5 min | 2-3 min |
| Medium (100-300 aa) | 5-10 min | 3-5 min |
| Large (>300 aa) | 10-20 min | 5-10 min |

## Output Files

### Generated Files
- **FASTA files** (`seqs/*.fa`): Designed sequences with metrics
- **PDB files** (`backbones/*.pdb`): Backbone structures with new sequences
- **Summary JSON**: Processing statistics

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| No ligand residues detected | Missing HETATM | Check PDB has HETATM records |
| Low ligand_confidence | Bad ligand coordinates | Verify ligand has valid coords |
| Processing timeout | Large protein | Reduce batches, disable packing |
| Empty output | Bad PDB format | Check backbone completeness |

## Sample Output

### Successful Job Response
```json
{
  "success": true,
  "job_id": "ligandmpnn_abc123",
  "message": "Job submitted successfully",
  "estimated_runtime": "3-5 minutes"
}
```

### Output FASTA Header
```
>enzyme_substrate_0001, score=1.45, global_score=1.38
MKTAYIAKQRQISFVKSHFSRQLE...
>enzyme_substrate_0002, score=1.52, global_score=1.41
MKTAYIAKQRQISFVKSQFSRQLD...
```

### What Good Output Looks Like
- **Score**: 1.0-2.0 (lower = more confident)
- **Ligand detected**: "Found ligand: LIG (12 atoms)"
- **Active site residues**: Preserved or optimized

## Typical Performance

| Campaign Size | Time | Notes |
|---------------|------|-------|
| 10 backbones × 8 seq | 10-15 min | Quick test |
| 100 backbones × 8 seq | 45-90 min | Standard |
| 500 backbones × 16 seq | 3-6 hours | Large campaign |

**Throughput**: ~40-80 sequences/minute for typical proteins.

## Verify Success

```bash
# Check job status
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# Verify ligand was detected in logs
# Download results and check sequence count
grep -c "^>" output.fa
```

## Best Practices

1. **Enable atom context**: Always use `ligand_mpnn_use_atom_context: true`
2. **Fix critical residues**: Preserve catalytic sites with `fixed_residues`
3. **Use appropriate cutoff**: Default 8.0 Å works for most binding sites
4. **Start conservative**: Use temperature 0.1 initially
5. **Validate with structure prediction**: Run Boltz on designed sequences
6. **Increase batches for diversity**: Better than increasing batch_size

### Failure Recovery

```
Ligand not recognized?
├── Check HETATM records in PDB
│   └── grep "^HETATM" protein.pdb | head
├── Verify ligand has proper residue name
│   └── Standard 3-letter code (e.g., ATP, NAD, LIG)
└── Ensure ligand has coordinates
    └── Check for 0,0,0 placeholder coordinates

Low ligand_confidence?
├── Verify ligand coordinates are correct
│   └── Visual inspection in PyMOL/ChimeraX
├── Increase cutoff_for_score
│   └── ligand_mpnn_cutoff_for_score: 10.0-12.0
└── Try with side chain context
    └── ligand_mpnn_use_side_chain_context: true
```

## LigandMPNN vs ProteinMPNN

| Feature | LigandMPNN | ProteinMPNN |
|---------|------------|-------------|
| Ligand awareness | Yes | No |
| Fixed residues | Yes | Limited |
| Side chain packing | Yes | No |
| Sequence scoring | Yes | No |
| Speed | Slightly slower | Faster |

---

**Next**: Validate designed sequences with `Boltz` → Check stability with `ThermoMPNN`.
