---
name: openbio
version: 1.0.4
updated_at: 2026-02-15
description: >
  OpenBio API for biological data access and computational biology tools.
  Use when: (1) Querying biological databases (PDB, UniProt, ChEMBL, etc.),
  (2) Searching scientific literature (PubMed, bioRxiv, arXiv),
  (3) Running structure prediction (Boltz, Chai, ProteinMPNN),
  (4) Performing pathway/enrichment analysis,
  (5) Designing molecular biology experiments (primers, cloning),
  (6) Analyzing variants and clinical data,
  (7) Analyzing and editing plasmid files (GenBank, SnapGene).
metadata:
  tags: [biology, protein, genomics, chemistry, bioinformatics, drug-discovery]
---

## Installation

```bash
bunx skills add https://github.com/openbio-ai/skills --skill openbio
```

## Authentication

**Required**: `OPENBIO_API_KEY` environment variable.

Tell the user to create their API key at: http://openbio.tech/profile#apikeys and securely store it in their environment variables.

If the user has not signed in to OpenBio, tell them to sign in to OpenBio (https://openbio.tech/auth) and create their account first and then create their API key.

```bash
export OPENBIO_API_KEY=your_key_here
```

**Base URL**: `https://api.openbio.tech/api/v1`

## Version Check (Do This First)

Before using the API, verify your skill is up to date:

```bash
curl -s "https://api.openbio.tech/api/v1/tools/skill-version"
```

This returns `{"skill": "openbio", "version": "X.Y.Z", ...}`. Compare against the `version` field at the top of this file (currently **1.0.4**). If the API returns a newer version:

```bash
bunx skills update
```

If that fails, remove and re-install:

```bash
bunx skills remove openbio --global -y
bunx skills add openbio-ai/skills --skill openbio --global --agent '*' -y
```

## Quick Start

```bash
# Health check (no auth required)
curl -X GET "https://api.openbio.tech/api/v1/tools/health"

# List available tools
curl -X GET "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY"

# Get tool schema (always do this first!)
curl -X GET "https://api.openbio.tech/api/v1/tools/{tool_name}" \
  -H "X-API-Key: $OPENBIO_API_KEY"

# Validate parameters before invoking (optional)
curl -X POST "https://api.openbio.tech/api/v1/tools/validate" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_pubmed", "params": {"query": "CRISPR", "max_results": 5}}'

# Invoke tool
curl -X POST "https://api.openbio.tech/api/v1/tools" \
  -H "X-API-Key: $OPENBIO_API_KEY" \
  -F "tool_name=search_pubmed" \
  -F 'params={"query": "CRISPR", "max_results": 5}'
```

## Decision Tree: Which Tools to Use

```
What do you need?
│
├─ Protein/structure data?
│   └─ Read rules/protein-structure.md
│       → PDB, AlphaFold, UniProt tools
│
├─ Literature search?
│   └─ Read rules/literature.md
│       → PubMed, arXiv, bioRxiv, OpenAlex
│
├─ Genomics/variants?
│   └─ Read rules/genomics.md
│       → Ensembl, GWAS, VEP, GEO
│
├─ Sequence similarity search (BLAST)?
│   └─ Read rules/blast.md
│       → submit_blast, check_blast_status, get_blast_results
│
├─ Small molecule analysis?
│   └─ Read rules/cheminformatics.md
│       → RDKit, PubChem, ChEMBL
│
├─ Cloning/PCR/assembly?
│   └─ Read rules/molecular-biology.md
│       → Primers, restriction, Gibson, Golden Gate
│
├─ Plasmid analysis/editing?
│   └─ Read rules/plasmid.md
│       → parse_plasmid_file, edit_plasmid
│
├─ Structure prediction/design?
│   └─ Read rules/structure-prediction.md
│       → Boltz, Chai, ProteinMPNN, LigandMPNN
│
├─ Pathway analysis?
│   └─ Read rules/pathway-analysis.md
│       → KEGG, Reactome, STRING, g:Profiler (GO enrichment)
│
└─ Clinical/drug data?
    └─ Read rules/clinical-data.md
        → ClinicalTrials, ClinVar, FDA, Open Targets
```

## Critical Rules

### 1. Always Check Tool Schema First
```bash
# Before invoking ANY tool:
curl -X GET "https://api.openbio.tech/api/v1/tools/{tool_name}" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```
Parameter names vary (e.g., `pdb_ids` not `pdb_id`). Check schema to avoid errors.

### 2. Long-Running Jobs (submit_* tools)
Prediction tools return a `job_id`. Poll for completion:
```bash
# Check status
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}/status" \
  -H "X-API-Key: $OPENBIO_API_KEY"

# Get results with download URLs
curl -X GET "https://api.openbio.tech/api/v1/jobs/{job_id}" \
  -H "X-API-Key: $OPENBIO_API_KEY"
```

### 3. Quality Thresholds
Don't just retrieve data—interpret it:

**AlphaFold pLDDT**: > 70 = confident, < 50 = disordered
**Experimental resolution**: < 2.5 Å for binding sites
**GWAS p-value**: < 5×10⁻⁸ = genome-wide significant
**Tanimoto similarity**: > 0.7 = similar compounds

See individual rule files for detailed thresholds.

## Rule Files

Read these for domain-specific knowledge:

### Core API
| File | Description |
|------|-------------|
| [rules/api.md](rules/api.md) | Core endpoints, authentication, job management |

### Data Access Tools
| File | Tools Covered |
|------|---------------|
| [rules/protein-structure.md](rules/protein-structure.md) | PDB, PDBe, AlphaFold, UniProt |
| [rules/literature.md](rules/literature.md) | PubMed, arXiv, bioRxiv, OpenAlex |
| [rules/genomics.md](rules/genomics.md) | Ensembl, ENA, Gene, GWAS, GEO |
| [rules/blast.md](rules/blast.md) | NCBI BLAST sequence similarity search |
| [rules/cheminformatics.md](rules/cheminformatics.md) | RDKit, PubChem, ChEMBL |
| [rules/molecular-biology.md](rules/molecular-biology.md) | Primers, PCR, restriction, assembly |
| [rules/plasmid.md](rules/plasmid.md) | parse_plasmid_file, edit_plasmid |
| [rules/pathway-analysis.md](rules/pathway-analysis.md) | KEGG, Reactome, STRING, g:Profiler |
| [rules/clinical-data.md](rules/clinical-data.md) | ClinicalTrials, ClinVar, FDA |

### ML Prediction Tools (Detailed)
| File | Tool | Use Case |
|------|------|----------|
| [rules/structure-prediction.md](rules/structure-prediction.md) | **Index** | Decision tree for all prediction tools |
| [rules/boltz.md](rules/boltz.md) | Boltz-2 | Structure + binding affinity |
| [rules/chai.md](rules/chai.md) | Chai-1 | Multi-modal (protein+ligand+RNA+glycan) |
| [rules/simplefold.md](rules/simplefold.md) | SimpleFold | Quick single-protein folding |
| [rules/proteinmpnn.md](rules/proteinmpnn.md) | ProteinMPNN | Fixed-backbone sequence design |
| [rules/ligandmpnn.md](rules/ligandmpnn.md) | LigandMPNN | Ligand-aware sequence design |
| [rules/thermompnn.md](rules/thermompnn.md) | ThermoMPNN | Stability (ΔΔG) prediction |
| [rules/geodock.md](rules/geodock.md) | GeoDock | Protein-protein docking |
| [rules/pinal.md](rules/pinal.md) | Pinal | De novo design from text |
| [rules/boltzgen.md](rules/boltzgen.md) | BoltzGen | End-to-end binder design |

## Tool Categories Summary

| Category | Count | Examples |
|----------|-------|----------|
| Protein structure | 23 | fetch_pdb_metadata, get_alphafold_prediction |
| Literature | 14 | search_pubmed, arxiv_search, biorxiv_search_keywords |
| Genomics | 27 | lookup_gene, vep_predict, gwas_search_associations_by_trait |
| Sequence similarity | 3 | submit_blast, check_blast_status, get_blast_results |
| Cheminformatics | 20+ | calculate_molecular_properties, chembl_similarity_search |
| Molecular biology | 15 | design_primers, restriction_digest, assemble_gibson |
| Plasmid | 2 | parse_plasmid_file, edit_plasmid |
| Structure prediction | 15+ | submit_boltz_prediction, submit_proteinmpnn_prediction |
| Pathway analysis | 26 | analyze_gene_list, get_string_network, go_enrichment, convert_gene_ids |
| Clinical data | 22 | search_clinical_trials, clinvar_search |

## Troubleshooting: Updating the Skill

If the API returns a newer version than the one in this file (see **Version Check** above), update your skill. See the Version Check section at the top for commands.

## Common Mistakes

1. **Not checking schemas** → Parameter errors. Use `POST /api/v1/tools/validate` to pre-check params.
2. **Ignoring quality metrics** → Using unreliable data
3. **Wrong tool for task** → Check decision trees in rule files
4. **Not polling jobs** → Missing prediction results
5. **Wrong tool name** → 404 responses include "Did you mean?" suggestions with similar tool names

---

**Tip**: When in doubt, search for tools: `GET /api/v1/tools/search?q=your_query`
