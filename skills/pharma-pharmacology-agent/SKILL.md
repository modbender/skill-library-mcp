---
name: pharma-pharmacology-agent
description: Pharmacology agent for ADME/PK profiling of drug candidates from SMILES. Computes drug-likeness (Lipinski Ro5, Veber rules), QED, SA Score, ADME predictions (BBB permeability, aqueous solubility, GI absorption, CYP3A4 inhibition, P-gp substrate, plasma protein binding), and PAINS alerts. Chains from chemistry-query for SMILES input. Triggers on pharmacology, ADME, PK/PD, drug likeness, Lipinski, absorption, distribution, metabolism, excretion, BBB, solubility, bioavailability, lead optimization, drug profiling.
---

# Pharma Pharmacology Agent v1.1.0

## Overview

Predictive pharmacology profiling for drug candidates using RDKit descriptors and validated rule-based heuristics. Provides comprehensive ADME assessment, drug-likeness scoring, and risk flagging — all from a SMILES string.

**Key capabilities:**
- **Drug-likeness:** Lipinski Rule of Five, Veber oral bioavailability rules
- **Scores:** QED (Quantitative Estimate of Drug-likeness), SA Score (Synthetic Accessibility)
- **ADME predictions:** BBB permeability, aqueous solubility (ESOL), GI absorption (Egan), CYP3A4 inhibition risk, P-glycoprotein substrate, plasma protein binding
- **Safety:** PAINS (Pan-Assay Interference) filter alerts
- **Risk assessment:** Automated flagging of pharmacological concerns
- **Standard chain output:** JSON schema compatible with all downstream agents

## Quick Start

```bash
# Profile a molecule from SMILES
exec python scripts/chain_entry.py --input-json '{"smiles": "CC(=O)Oc1ccccc1C(=O)O", "context": "user"}'

# Chain from chemistry-query output
exec python scripts/chain_entry.py --input-json '{"smiles": "<canonical_smiles>", "context": "from_chemistry"}'
```

## Scripts

### `scripts/chain_entry.py`
Main entry point. Accepts JSON with `smiles` field, returns full pharmacology profile.

**Input:**
```json
{"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "context": "user"}
```

**Output schema:**
```json
{
  "agent": "pharma-pharmacology",
  "version": "1.1.0",
  "smiles": "<canonical>",
  "status": "success|error",
  "report": {
    "descriptors": {"mw": 194.08, "logp": -1.03, "tpsa": 61.82, "hbd": 0, "hba": 6, "rotb": 0, "arom_rings": 2, "heavy_atoms": 14, "mr": 51.2},
    "lipinski": {"pass": true, "violations": 0, "details": {...}},
    "veber": {"pass": true, "tpsa": {...}, "rotatable_bonds": {...}},
    "qed": 0.5385,
    "sa_score": 2.3,
    "adme": {
      "bbb": {"prediction": "moderate", "confidence": "medium", "rationale": "..."},
      "solubility": {"logS_estimate": -1.87, "class": "high", "rationale": "..."},
      "gi_absorption": {"prediction": "high", "rationale": "..."},
      "cyp3a4_inhibition": {"risk": "low", "rationale": "..."},
      "pgp_substrate": {"prediction": "unlikely", "rationale": "..."},
      "plasma_protein_binding": {"prediction": "moderate-low", "rationale": "..."}
    },
    "pains": {"alert": false}
  },
  "risks": [],
  "recommend_next": ["toxicology", "ip-expansion"],
  "confidence": 0.85,
  "warnings": [],
  "timestamp": "ISO8601"
}
```

## ADME Prediction Rules

| Property | Method | Thresholds |
|----------|--------|-----------|
| BBB permeability | Clark's rules (TPSA/logP) | TPSA<60+logP 1-3 = high; TPSA<90 = moderate |
| Solubility | ESOL approximation | logS > -2 high; > -4 moderate; else low |
| GI absorption | Egan egg model | logP<5.6 and TPSA<131.6 = high |
| CYP3A4 inhibition | Rule-based | logP>3 and MW>300 = high risk |
| P-gp substrate | Rule-based | MW>400 and HBD>2 = likely |
| Plasma protein binding | logP correlation | logP>3 = high (>90%) |

## Chaining

This agent is designed to receive output from `chemistry-query`:

```
chemistry-query (name→SMILES+props) → pharma-pharmacology (ADME profile) → toxicology / ip-expansion
```

The `recommend_next` field always includes `["toxicology", "ip-expansion"]` for pipeline continuation.

## Tested With

All features verified end-to-end with RDKit 2024.03+:

| Molecule | MW | logP | Lipinski | Key Findings |
|----------|-----|------|----------|-------------|
| Caffeine | 194.08 | -1.03 | ✅ Pass (0 violations) | High solubility, moderate BBB, QED 0.54 |
| Aspirin | 180.04 | 1.31 | ✅ Pass (0 violations) | Moderate solubility, SA 1.58 (easy), QED 0.55 |
| Sotorasib | 560.23 | 4.48 | ✅ Pass (1 violation: MW) | Low solubility, CYP3A4 risk, high PPB |
| Metformin | 129.10 | -1.03 | ✅ Pass (0 violations) | High solubility, low BBB, QED 0.25 |
| Invalid SMILES | — | — | — | Graceful JSON error |
| Empty input | — | — | — | Graceful JSON error |

## Error Handling

- Invalid SMILES: Returns `status: "error"` with descriptive warning
- Missing input: Clear error message requesting `smiles` or `name`
- All errors produce valid JSON (never crashes)

## Resources

- `references/api_reference.md` — API and methodology references

## Changelog

**v1.1.0** (2026-02-14)
- Initial production release with full ADME profiling
- Lipinski, Veber, QED, SA Score, PAINS
- BBB, solubility, GI absorption, CYP3A4, P-gp, PPB predictions
- Automated risk assessment
- Standard chain output schema
- Comprehensive error handling
- End-to-end tested with diverse molecules
