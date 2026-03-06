# Structure Prediction & Protein Design Tools

This is a guide for choosing between OpenBio's ML-based prediction and design tools. See individual tool files for detailed documentation.

## Quick Reference

| Tool | Input | Output | Best For |
|------|-------|--------|----------|
| [Boltz](boltz.md) | Sequences/YAML | Structure + affinity | General prediction, binding affinity |
| [Chai](chai.md) | FASTA w/ entity types | Structure | Multi-modal (protein+ligand+RNA+glycan) |
| [SimpleFold](simplefold.md) | Sequence | Structure | Quick single-protein prediction |
| [ProteinMPNN](proteinmpnn.md) | Backbone PDB | Sequences | Fixed-backbone design |
| [LigandMPNN](ligandmpnn.md) | Complex PDB | Sequences | Ligand-aware design |
| [ThermoMPNN](thermompnn.md) | Structure PDB | ΔΔG values | Stability prediction |
| [GeoDock](geodock.md) | Two PDBs | Docked complex | Protein-protein docking |
| [Pinal](pinal.md) | Text description | Sequences | De novo from language |
| [BoltzGen](boltzgen.md) | YAML spec | Full pipeline | Comprehensive binder design |

## Master Decision Tree

```
What do you need?
│
├─ PREDICT STRUCTURE FROM SEQUENCE?
│   │
│   ├─ Single protein only?
│   │   ├─ Need speed → SimpleFold
│   │   └─ Need best quality → Boltz
│   │
│   ├─ Protein complex (multi-chain)?
│   │   └─ Boltz or Chai
│   │
│   ├─ Protein + small molecule?
│   │   ├─ Need binding affinity → Boltz-2 (YAML format)
│   │   └─ Just structure → Chai or Boltz
│   │
│   ├─ Protein + RNA/DNA/glycan?
│   │   └─ Chai (best multi-modal)
│   │
│   └─ Protein-protein docking?
│       ├─ Quick result → GeoDock
│       └─ Better accuracy → Boltz with multi-chain
│
├─ DESIGN SEQUENCES FOR BACKBONE?
│   │
│   ├─ No ligand present?
│   │   └─ ProteinMPNN
│   │
│   ├─ Ligand/cofactor in binding site?
│   │   └─ LigandMPNN
│   │
│   └─ Need thermostability focus?
│       └─ ThermoMPNN (for analysis) + ProteinMPNN (for design)
│
├─ PREDICT MUTATION EFFECTS?
│   └─ ThermoMPNN
│
├─ DE NOVO PROTEIN DESIGN?
│   │
│   ├─ From text description?
│   │   └─ Pinal
│   │
│   └─ Need full design pipeline with filtering?
│       └─ BoltzGen
│
└─ DESIGN PROTEIN BINDERS?
    │
    ├─ Protein binder to protein target?
    │   └─ BoltzGen (protein-anything protocol)
    │
    ├─ Peptide binder (including cyclic)?
    │   └─ BoltzGen (peptide-anything protocol)
    │
    ├─ Nanobody design?
    │   └─ BoltzGen (nanobody-anything protocol)
    │
    └─ Protein binding small molecule?
        └─ BoltzGen (protein-small_molecule protocol)
```

## Comparison Tables

### Structure Prediction

| Feature | Boltz-2 | Chai-1 | SimpleFold |
|---------|---------|--------|------------|
| Single protein | ✓ | ✓ | ✓ |
| Multi-chain complex | ✓ | ✓ | ✗ |
| Small molecules | ✓ | ✓ | ✗ |
| RNA/DNA | ✓ | ✓ | ✗ |
| Glycans | Limited | ✓ | ✗ |
| Binding affinity | ✓ | ✗ | ✗ |
| MSA-free option | ✓ | ✗ | ✓ |
| Speed | Moderate | Moderate | Fast |

### Sequence Design

| Feature | ProteinMPNN | LigandMPNN | ThermoMPNN |
|---------|-------------|------------|------------|
| Fixed backbone | ✓ | ✓ | ✗ (analysis) |
| Ligand awareness | ✗ | ✓ | ✗ |
| Side chain packing | ✗ | ✓ | ✗ |
| Scoring mode | ✗ | ✓ | ✗ |
| Stability prediction | ✗ | ✗ | ✓ |
| Soluble model | ✓ | ✗ | ✗ |

### De Novo Design

| Feature | Pinal | BoltzGen |
|---------|-------|----------|
| Text input | ✓ | ✗ |
| Backbone design | ✗ | ✓ |
| Inverse folding | ✗ | ✓ |
| Structure validation | ✗ | ✓ |
| Filtering/ranking | ✗ | ✓ |
| Complexity | Low | High |

## Common Workflows

### Workflow 1: Validate Designed Binder

```
1. Design with BoltzGen
   → Get sequences from final_designs/

2. Predict complex structure
   → submit_boltz_prediction with binder + target

3. Check confidence
   → Keep ipTM > 0.6, pLDDT > 0.7

4. Analyze interface
   → Use structure tools for contacts
```

### Workflow 2: Engineer Enzyme

```
1. Analyze stability
   → submit_thermompnn_prediction
   → Identify stabilizing mutations

2. Design with ligand awareness
   → submit_ligandmpnn_prediction
   → Fix catalytic residues
   → Keep substrate in context

3. Validate design
   → submit_boltz_prediction
   → Check fold maintained (pTM > 0.8)
```

### Workflow 3: Quick Screening

```
1. Predict structures rapidly
   → submit_simplefold_prediction for each sequence

2. Filter by confidence
   → Keep pLDDT > 0.7

3. Detailed analysis for top candidates
   → submit_boltz_prediction for best ones
```

## Quality Thresholds Summary

### Structure Prediction

| Metric | Excellent | Good | Poor |
|--------|-----------|------|------|
| pLDDT | > 90 | 70-90 | < 70 |
| pTM | > 0.8 | 0.5-0.8 | < 0.5 |
| ipTM (interface) | > 0.7 | 0.5-0.7 | < 0.5 |

### Sequence Design

| Metric | Good | Investigate |
|--------|------|-------------|
| Score (ProteinMPNN) | < 1.5 | > 2.5 |
| Temperature | 0.1-0.2 (conservative) | > 0.3 (diverse) |

### Stability

| ΔΔG | Effect |
|-----|--------|
| < -1.0 | Stabilizing |
| -1.0 to +1.0 | Neutral |
| > +1.0 | Destabilizing |

## Quality Control Guidelines

### Critical Limitation

**Individual metrics have weak predictive power for binding**. Research shows:
- Individual metric ROC AUC: 0.64-0.66 (slightly better than random)
- Metrics are **pre-screening filters**, not affinity predictors
- **Composite scoring is essential** for meaningful ranking

### Sequential Filtering Pipeline

```python
# Stage 1: Structural confidence
designs = designs[designs['pLDDT'] > 0.85]

# Stage 2: Self-consistency (scRMSD)
designs = designs[designs['scRMSD'] < 2.0]

# Stage 3: Binding quality
designs = designs[(designs['ipTM'] > 0.5) & (designs['PAE_interaction'] < 10)]

# Stage 4: Expression checks
designs = designs[designs['cysteine_count'] % 2 == 0]  # Even cysteines
```

### Campaign Health Assessment

| Pass Rate | Status | Action |
|-----------|--------|--------|
| > 15% | Excellent | Proceed to experimental testing |
| 10-15% | Good | Normal, proceed |
| 5-10% | Marginal | Review parameters, increase designs |
| < 5% | Poor | Diagnose issues before scaling |

### Failure Recovery Trees

**Low pLDDT across predictions?**
```
├── Check scRMSD distribution
│   ├── High scRMSD (>2.5Å) → Backbone issue, regenerate
│   └── Low scRMSD but low pLDDT → Disordered regions
├── Increase sequence diversity
│   └── num_seq_per_target: 16-32, temp: 0.2
└── Try different design approach
    └── Use SolubleMPNN or different tool
```

**Low ipTM (interface quality)?**
```
├── Review hotspot selection
│   └── Are hotspots surface-exposed?
├── Increase binder length
│   └── More contact area helps
└── Check interface geometry
    └── Flat vs concave targets need different approaches
```

## Rate Limits (All Tools)

- **Per minute**: 2 jobs
- **Per day**: 10 jobs
- **Timeout**: 30 min (most), 4 hours (BoltzGen)

## Job Management

All prediction tools return `job_id`. Poll and download:

```bash
# Check status
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY"

# Get results with download URLs
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```

---

**See individual tool files for detailed parameters, examples, and troubleshooting.**
