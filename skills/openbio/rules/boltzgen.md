# BoltzGen - End-to-End Protein Design System

## Overview

BoltzGen is a comprehensive protein design system combining diffusion-based generative models with structure prediction and analysis. It enables design of protein binders, peptides, nanobodies, and small molecule binders through a unified pipeline.

### When to Use BoltzGen
- Design protein binders to targets
- Design peptide binders (including cyclic)
- Design nanobodies/single-domain antibodies
- Design proteins for small molecule binding
- Need full pipeline: design → fold → analyze → filter

### When NOT to Use
- Simple sequence design → Use ProteinMPNN
- Just need structure prediction → Use Boltz/Chai
- Text-based de novo design → Use Pinal
- Quick exploration → Use simpler tools first

## Protocols

| Protocol | Use Case | Key Features |
|----------|----------|--------------|
| `protein-anything` | Protein binding to proteins/peptides | Includes design folding |
| `peptide-anything` | Peptide & cyclic peptide design | No Cys, no design folding |
| `nanobody-anything` | Single-domain antibodies | Nanobody constraints |
| `protein-small_molecule` | Protein-small molecule binding | Affinity prediction |

## Input Format: Design Specification YAML

### Basic Protein Binder
```yaml
entities:
  # Designed protein (80-140 residues)
  - protein: 
      id: B
      sequence: 80..140

  # Target from CIF file
  - file:
      path: 6m1u.cif
      include: 
        - chain:
            id: A
```

### With Binding Site Specification
```yaml
entities:
  - file:
      path: structure.cif
      include: 
        - chain:
            id: A
      binding_types:
        - chain:
            id: A
            binding: 5..7,13        # These should bind
            not_binding: 20..25     # These should NOT bind

  - protein: 
      id: G
      sequence: 80..120
```

### Cyclic Peptide with Disulfide
```yaml
entities:
  - protein:
      id: S
      sequence: 10..14C6C3    # Variable, then Cys, more residues
      cyclic: true

constraints:
  - bond:
      atom1: [S, 11, SG]
      atom2: [S, 18, SG]
```

### With Ligand
```yaml
entities:
  - protein:
      id: A
      sequence: 100

  - ligand:
      id: L
      ccd: ATP            # Chemical Component Dictionary
      # OR
      smiles: 'CCO'       # SMILES notation
```

## Parameters

### Core Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `design_spec_path` | string | - | required | YAML spec path |
| `protocol` | string | see above | protein-anything | Design protocol |
| `num_designs` | int | 1-200 | 50 | Designs to generate |
| `budget` | int | 1-50 | 10 | Final designs after filtering |
| `cif_file_path` | string | - | None | CIF file if referenced in YAML |

### Inverse Folding

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip_inverse_folding` | bool | false | Skip sequence optimization |
| `inverse_fold_num_sequences` | int | 1 | Sequences per backbone |
| `inverse_fold_avoid` | string | None | Disallowed AAs (e.g., "KEC") |
| `only_inverse_fold` | bool | false | Only inverse fold (skip design) |

### Filtering

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alpha` | float | auto | Diversity weight (0=quality, 1=diversity). Auto: 0.001 for protein, 0.01 for peptide |
| `metrics_override` | list | None | Custom metric weights |
| `additional_filters` | list | None | Extra filters (e.g., "design_ALA>0.3") |

## Output Structure

```
output_directory/
├── config/
│   └── steps.yaml
│
├── intermediate_designs/              # Initial backbones
│   ├── *.cif
│   └── *.npz
│
├── intermediate_designs_inverse_folded/
│   ├── *.cif                         # After inverse folding
│   ├── refold_cif/                   # ⭐ PRIMARY RESULTS
│   │   └── *.cif                     # Refolded complexes
│   ├── aggregate_metrics_analyze.csv
│   └── per_target_metrics_analyze.csv
│
└── final_ranked_designs/             # ⭐ FINAL OUTPUT
    ├── final_<budget>_designs/       # Selected designs
    │   └── *.cif
    ├── all_designs_metrics.csv
    ├── final_designs_metrics_<budget>.csv
    └── results_overview.pdf          # 📊 Visual analysis
```

### Key Files to Check First

1. **`results_overview.pdf`** - Visual quality assessment
2. **`final_<budget>_designs/`** - Your curated designs
3. **`final_designs_metrics_<budget>.csv`** - Quality scores
4. **`refold_cif/`** - Full complex structures

## API Usage

### Basic Protein Binder Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_boltzgen_prediction" \
  -F 'params={
    "design_spec_path": "designs/binder.yaml",
    "output_directory": "results/protein_design",
    "protocol": "protein-anything",
    "cif_file_path": "structures/target.cif",
    "num_designs": 50,
    "budget": 10
  }'
```

### Peptide Design
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_boltzgen_prediction" \
  -F 'params={
    "design_spec_path": "designs/peptide.yaml",
    "output_directory": "results/peptide_design",
    "protocol": "peptide-anything",
    "num_designs": 100,
    "budget": 20
  }'
```

### Small Molecule Binder
```bash
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=submit_boltzgen_prediction" \
  -F 'params={
    "design_spec_path": "designs/ligand_binder.yaml",
    "output_directory": "results/sm_design",
    "protocol": "protein-small_molecule",
    "num_designs": 50,
    "budget": 10
  }'
```

## Expected Runtime

| Config | Time |
|--------|------|
| Testing: 50 designs, budget 10 | 15-30 min |
| Production: 100-200 designs, budget 20-32 | 1-2 hours |

## Rate Limits

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **Max designs**: 200 per job
- **Timeout**: 4 hours

## Quality Metrics

### Key Metrics in CSV

| Metric | Description | Good Value |
|--------|-------------|------------|
| `plip_hbonds_refolded` | H-bonds at interface | Higher = better |
| `delta_sasa_refolded` | Buried surface area | Higher = stronger |
| `design_plddt` | Confidence score | > 0.7 |
| RMSD | Refolding accuracy | Lower = better |

## Common Mistakes

### Wrong: Missing CIF file
```
❌ YAML references "6m1u.cif" but cif_file_path not provided
```
```
✅ cif_file_path: "structures/6m1u.cif"
```

### Wrong: Too many designs for testing
```
❌ num_designs: 200 for initial test
   → Wastes time and quota
```
```
✅ num_designs: 50, budget: 10 for testing
   Scale up after validation
```

### Wrong: Invalid YAML syntax
```
❌ Indentation errors, missing quotes on SMILES
```
```
✅ Validate YAML with online tool before submitting
   Always quote SMILES strings
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| YAML error | Syntax | Validate YAML online |
| CIF not found | Missing path | Provide cif_file_path |
| Timeout | Too many designs | Reduce num_designs |
| Low quality | Poor sampling | Increase num_designs |
| Memory error | Large complex | Simplify target |

## Sample Output

### Successful Job Response
```json
{
  "success": true,
  "job_id": "boltzgen_def456ghi789",
  "message": "Job submitted successfully",
  "estimated_runtime": "30-60 minutes"
}
```

### Directory After Completion
```
out/boltzgen/2501301234/
├── intermediate_designs/           # Raw diffusion outputs
│   ├── design_0.cif
│   └── design_0.npz
├── intermediate_designs_inverse_folded/
│   ├── refold_cif/                # ⭐ Refolded complexes
│   └── aggregate_metrics_analyze.csv
└── final_ranked_designs/
    ├── final_10_designs/          # ⭐ Top designs
    └── results_overview.pdf       # 📊 Summary plots
```

### What Good Output Looks Like
- **Refolding RMSD < 2.0Å**: Design folds as predicted
- **ipTM > 0.5**: Confident interface
- **All designs complete pipeline**: No errors in logs

## Typical Performance

| Campaign Size | Time | Notes |
|---------------|------|-------|
| 50 designs | 30-45 min | Quick exploration |
| 100 designs | 1-1.5 hours | Standard campaign |
| 200 designs | 2-3 hours | Large campaign |
| 500+ designs | Not recommended | Split into multiple jobs |

**Per-design**: ~30-60 seconds for typical binder.

## Verify Success

```bash
# Check job completed
curl -s "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY" | jq '.status'

# After downloading results:
# Count final designs (should match budget)
ls final_ranked_designs/final_*_designs/*.cif | wc -l

# Check results overview exists
ls final_ranked_designs/results_overview.pdf
```

## Best Practices

1. **Start small**: num_designs: 50, budget: 10 for testing
2. **Choose right protocol**: protein-anything for most cases
3. **Specify binding sites**: Improves design quality
4. **Provide CIF path**: If YAML references structure file
5. **Check results_overview.pdf**: Quick quality assessment
6. **Use defaults for filtering**: Auto-tuned for most cases

### Failure Recovery

```
Too few designs pass filtering?
├── Increase num_designs
│   └── Try 100-200 instead of 50
├── Relax alpha (more diversity)
│   └── alpha: 0.01-0.1
├── Check binding site specification
│   └── Are hotspots surface-exposed?
└── Simplify constraints
    └── Remove overly restrictive binding_types

Low ipTM across designs?
├── Review hotspot selection
│   ├── Are hotspots surface-exposed?
│   └── Try 3-6 different hotspot combinations
├── Increase binder length
│   └── sequence: 80..120 instead of 60..80
├── Check interface geometry
│   └── Flat targets need different approach than concave
└── Try different protocol
    └── peptide-anything for smaller interfaces

High refolding RMSD (> 2.5Å)?
├── Sequences don't specify intended structure
│   └── Increase inverse_fold_num_sequences: 2-3
├── Try lower alpha (quality focus)
│   └── alpha: 0.001 or 0.0
└── Reduce complexity
    └── Simpler topology, fewer constraints
```

## Campaign Health Assessment

| Pass Rate | Status | Action |
|-----------|--------|--------|
| > 15% | Excellent | Proceed to experimental testing |
| 10-15% | Good | Normal, proceed |
| 5-10% | Marginal | Review parameters, increase designs |
| < 5% | Poor | Diagnose issues before scaling |

## BoltzGen vs Other Tools

| Feature | BoltzGen | Pinal | ProteinMPNN |
|---------|----------|-------|-------------|
| De novo backbone | Yes | Yes | No |
| Inverse folding | Integrated | No | Standalone |
| Structure validation | Integrated | No | No |
| Filtering/ranking | Integrated | No | No |
| Binding sites | Precise | Text | Backbone |
| Complexity | High | Low | Low |
| Use case | Full pipeline | Exploration | Sequence only |

---

**Next**: Validate top designs with `Boltz` or `Chai` for independent confirmation → Experimental testing.
