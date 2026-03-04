---
name: Genomics
slug: genomics
version: 1.0.0
homepage: https://clawic.com/skills/genomics
description: Interpret genomic variants with ACMG classification, pharmacogenomics, and clinical annotation from ClinVar and gnomAD.
metadata: {"clawdbot":{"emoji":"🧬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Ask user consent before creating `~/genomics/` workspace.

## When to Use

User has processed genomic data (VCF files) and needs clinical interpretation. Agent handles variant classification, pharmacogenomics recommendations, and annotation lookup. NOT for raw data processing — use `bioinformatics` skill for alignment and variant calling.

## Architecture

Memory lives in `~/genomics/`. See `memory-template.md` for structure.

```
~/genomics/
├── memory.md           # Context + preferences + interpretation history
└── cases/              # Active interpretation cases
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Classify Variants Using ACMG Guidelines
Every variant needs systematic classification:

| Category | Criteria |
|----------|----------|
| Pathogenic | PVS1, PS1-4, PM1-6, PP1-5 weighted |
| Likely Pathogenic | Strong + moderate evidence |
| VUS | Insufficient or conflicting evidence |
| Likely Benign | BS1-4, BP1-7 weighted |
| Benign | Strong benign evidence |

**Never classify without evidence.** State "insufficient data" when appropriate.

### 2. Check Population Frequency First
Before clinical interpretation, verify frequency:

| Source | Use For |
|--------|---------|
| gnomAD v4 | Global population frequency |
| gnomAD non-cancer | Somatic analysis |
| Population-specific | Ancestry-appropriate filtering |

**MAF >1% in any population = likely benign for rare disease.**

### 3. Cross-Reference Multiple Databases

| Database | Information |
|----------|-------------|
| ClinVar | Clinical classifications + submitter evidence |
| OMIM | Gene-disease relationships |
| HGMD | Literature-reported mutations |
| UniProt | Protein function + domains |

**Single-source interpretation is insufficient.** Triangulate evidence.

### 4. Report Pharmacogenomics Actionably
For drug-gene interactions, provide:
- Diplotype (e.g., CYP2D6 *1/*4)
- Predicted phenotype (poor/intermediate/normal/ultra-rapid metabolizer)
- Drug list affected
- Dosing guidance (CPIC/DPWG when available)

### 5. Separate Germline from Somatic Context

| Context | Key Differences |
|---------|-----------------|
| Germline | Family implications, carrier testing, predictive |
| Somatic | Tumor-specific, therapy selection, no inheritance |

**Always state which context you're interpreting.**

### 6. Acknowledge Uncertainty
- Novel variants often lack evidence
- VUS ≠ benign — requires ongoing monitoring
- Reclassification happens (ClinVar updates monthly)
- Computational predictions are supportive, not definitive

## Pharmacogenomics Reference

### High-Priority Drug-Gene Pairs (CPIC Level A)

| Gene | Drugs | Clinical Action |
|------|-------|-----------------|
| CYP2D6 | Codeine, tramadol, tamoxifen, SSRIs | Dosing/alternative |
| CYP2C19 | Clopidogrel, PPIs, voriconazole | Dosing/alternative |
| CYP2C9 + VKORC1 | Warfarin | Dosing algorithm |
| DPYD | Fluorouracil, capecitabine | Dose reduction/avoid |
| TPMT + NUDT15 | Azathioprine, mercaptopurine | Dose reduction |
| HLA-B*57:01 | Abacavir | Contraindication |
| HLA-B*15:02 | Carbamazepine | Contraindication (Asian ancestry) |
| SLCO1B1 | Simvastatin | Dose cap/alternative statin |
| G6PD | Rasburicase, primaquine | Contraindication |
| CYP3A5 | Tacrolimus | Dosing adjustment |

### Phenotype Interpretation

| Metabolizer Status | Meaning | Typical Action |
|--------------------|---------|----------------|
| Poor (PM) | Little/no enzyme activity | Alternative drug or dose ↓↓ |
| Intermediate (IM) | Reduced activity | Consider dose ↓ |
| Normal (NM) | Expected activity | Standard dosing |
| Rapid/Ultra-rapid (UM) | Increased activity | Dose ↑ or alternative |

## Annotation Resources

| Resource | URL | Content |
|----------|-----|---------|
| ClinVar | ncbi.nlm.nih.gov/clinvar | Clinical variant classifications |
| gnomAD | gnomad.broadinstitute.org | Population frequencies |
| OMIM | omim.org | Gene-disease relationships |
| PharmGKB | pharmgkb.org | Drug-gene annotations |
| CPIC | cpicpgx.org | Pharmacogenomics guidelines |
| ClinGen | clinicalgenome.org | Gene-disease validity |
| Franklin | franklin.genoox.com | Variant interpretation aid |
| VarSome | varsome.com | ACMG auto-classification |

## Common Interpretation Traps

- **Ignoring population specificity** — Variants common in African populations may look rare in European-biased databases
- **Trusting single ClinVar submitter** — Check submitter count and review status (≥2 submitters, no conflict preferred)
- **Conflating computational prediction with evidence** — CADD/REVEL are supportive, not diagnostic
- **Missing compound heterozygosity** — Two VUS in trans can be pathogenic together
- **Outdated database versions** — gnomAD v4 has 800K+ exomes vs v2's 125K
- **Ignoring gene-level constraint** — pLI/LOEUF scores indicate tolerance to loss-of-function

## External Endpoints

This skill does NOT automatically call external APIs. All database references are for manual lookup:

| Resource | When Used | Data Sent |
|----------|-----------|-----------|
| ClinVar, gnomAD, OMIM | User manually visits | None by this skill |
| PharmGKB, CPIC | User manually visits | None by this skill |
| VarSome, Franklin | User manually visits | None by this skill |

**No automatic network requests.** The skill provides URLs and guidance for manual lookup only.

## Security & Privacy

**Data that stays local:**
- All interpretation work runs locally
- No variant data sent externally by this skill
- No automatic API calls to any database

**This skill does NOT:**
- Make network requests automatically
- Upload patient variants anywhere
- Connect to databases without explicit user action
- Store identifiable genomic information outside ~/genomics/

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `medicine` — clinical decision support
- `biology` — molecular mechanisms
- `chemistry` — drug metabolism pathways
- `health` — patient care context

## Feedback

- If useful: `clawhub star genomics`
- Stay updated: `clawhub sync`
