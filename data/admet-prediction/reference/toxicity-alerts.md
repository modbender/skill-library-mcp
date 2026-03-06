# Toxicity Alerts Reference

Structural alerts and toxicity prediction for drug discovery.

## Overview

Toxicity alerts identify potentially problematic structural motifs in drug candidates.

## Alert Categories

| Category | Impact | Example |
|----------|--------|---------|
| Genotoxicity | DNA damage | Nitroaromatics |
| Cardiotoxicity | hERG block | Basic amines |
| Hepatotoxicity | Liver damage | Thiophenes |
| Respiratory | Lung toxicity | Lung surfactant inhibition |
| Skin sensitization | Allergic reaction | Michael acceptors |

## Genotoxicity Alerts

### Ames Positives

**Structural alerts**:
1. **Nitroaromatics**
   ```
   Ar-NO2  (where Ar = aromatic)
   ```
   Risk: Metabolic reduction to nitroso/hydroxylamine

2. **Azo compounds**
   ```
   Ar-N=N-Ar'
   ```
   Risk: Reduction to aromatic amines

3. **Aliphatic epoxides**
   ```
   C-C(-O-)C
   ```
   Risk: Alkylation of DNA

4. **Aromatic amines**
   ```
   Ar-NH2
   ```
   Risk: N-hydroxylation

5. **Alkyl sulfonates**
   ```
   R-OSO2-R'
   ```
   Risk: Alkylation

### Testing Strategy

1. **In silico**: Structural alert screening
2. **In vitro**: Ames test (5 strains)
3. **Follow-up**: Micronucleus assay if positive

## Cardiotoxicity Alerts

### hERG Inhibition

**Risk factors**:
1. **Basic nitrogen** (pKa > 8)
2. **Aromatic moiety**
3. **LogP > 3**
4. **MW > 400**

**High-risk patterns**:
```
# Basic tertiary amine with aromatic
Ar-CH2-CH2-N(R)-R

# Flexible linker between aromatic and amine
Ar-(CH2)3-N(R)2
```

**Mitigation**:
- Reduce basicity (pKa)
- Reduce lipophilicity
- Introduce polarity
- Constrain flexibility

### QT Prolongation

Beyond hERG: multiple ion channels affected.

**Testing**:
- hERG patch clamp assay
- QT interval in animals
- Thorough QT study (clinical)

## Hepatotoxicity Alerts

### DILI (Drug-Induced Liver Injury)

**Structural alerts**:

1. **Thiophenes**
   ```
   S-heterocycle
   ```
   Risk: Reactive epoxide formation

2. **Anilines**
   ```
   Ar-NH2
   ```
   Risk: Metabolic oxidation to quinone imines

3. **Hydrazines**
   ```
   R-NH-NH2
   ```
   Risk: Reactive intermediates

4. **Bromo/thioesters**
   ```
   R-C(=O)-Br / R-C(=O)-SR
   ```
   Risk: Alkylation

**High-risk combinations**:
- Lipophilic + basic nitrogen
- Multiple aromatic rings
- Low clearance

### Testing Strategy

1. **In silico**: DILI prediction models
2. **In vitro**: Hepatocyte cytotoxicity
3. **In vivo**: Liver enzymes in animals
4. **Biomarkers**: ALT, AST, bilirubin

## Respiratory Toxicity

### Lung Toxicity Alerts

1. **Lung surfactant inhibitors**
   - Cationic amphiphilic drugs
   - Pattern: Amine + bulky hydrophobic

2. **Pulmonary fibrosis**
   - Bleomycin-like
   - Pattern: Metal-chelating groups

## Skin Sensitization

### Structural Alerts

1. **Michael acceptors**
   ```
   C=C-C=O
   ```
   Mechanism: Thiol addition

2. **Aldehydes**
   ```
   R-CHO
   ```
   Mechanism: Protein binding

3. **Isocyanates**
   ```
   R-N=C=O
   ```
   Mechanism: Carbamylation

4. **Acid halides**
   ```
   R-C(=O)-X
   ```
   Mechanism: Acylation

### Testing

- Local Lymph Node Assay (LLNA)
- Guinea pig maximization test
- Direct peptide reactivity assay (DPRA)

## PAINS (Pan-Assay Interference Compounds)

### Common PAINS Patterns

1. **Rhodanines**
   ```
   S-C(=S)-N
   ```
   Issue: Metal chelation

2. **Curcuminoids**
   ```
   Enone with multiple phenols
   ```
   Issue: Redox activity

3. **Quinones**
   ```
   Quinone core
   ```
   Issue: Redox cycling

4. **Catechols**
   ```
   Di-hydroxyphenyl
   ```
   Issue: Metal binding

5. **Enones**
   ```
   α,β-unsaturated carbonyl
   ```
   Issue: Michael addition

### Filtering

Use RDKit filter catalog:
```python
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

params = FilterCatalogParams()
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
catalog = FilterCatalog(params)

matches = catalog.GetMatches(mol)
```

## Brenk Alerts

Additional problematic structural motifs.

### Alert Types

1. **Alkyl halides**
   - Potential alkylating agents

2. **Azides**
   - Explosive potential

3. **Diazos**
   - Reactivity

4. **Peroxides**
   - Explosive/oxidizing

5. **Polyhalogenated**
   - Environmental persistence

## Reactive Functional Groups

### High Reactivity

| Group | Risk | Mitigation |
|-------|-------|------------|
| Acyl halide | High | Avoid or mask |
| Epoxide | High | Ring-open or replace |
| Aziridine | High | Replace |
| Isocyanate | High | Replace |
| Michael acceptor | Medium | Steric hindrance |
| Aldehyde | Medium | Protect or reduce |
| α-Haloketone | High | Avoid |

## Toxicity Prediction Tools

| Tool | Method | Coverage |
|------|--------|----------|
| ProTox-II | ML + rules | General toxicity |
| DILIpred | ML | Liver toxicity |
| hERGpredict | ML | Cardiac toxicity |
| pkCSM | ML | Multiple endpoints |
| TEST | QSAR | EPA endpoints |
| Derek Nexus | Rules | Comprehensive |

## Mitigation Strategies

### Structure Modification

1. **Reduce reactivity**
   - Mask functional groups
   - Introduce steric hindrance
   - Replace with bioisosteres

2. **Reduce lipophilicity**
   - Add polar groups
   - Remove hydrophobics
   - Shorten chains

3. **Reduce basicity**
   - Modify amine pKa
   - Replace with amide
   - Introduce electron-withdrawing groups

### Bioisosteric Replacements

| Problematic Group | Bioisostere |
|-------------------|-------------|
| Carboxylic acid | Tetrazole, sulfonamide |
| Aniline | Pyridine, pyrimidine |
| Thiophene | Furane, pyrrole |
| Michael acceptor | Saturated carbonyl |

## Testing Workflow

```
1. In silico screening
   ├── Structural alerts
   ├── QSAR models
   └── Machine learning

2. In vitro testing (high risk)
   ├── Ames test
   ├── hERG patch clamp
   ├── Hepatocyte cytotoxicity
   └── Micronucleus assay

3. In vivo testing (lead candidates)
   ├── Repeat-dose toxicity
   ├── Safety pharmacology
   └── Genotoxicity in vivo

4. Clinical monitoring
   ├── Liver enzymes
   ├── ECG (QT)
   └── Renal function
```

## Best Practices

1. **Screen early**: Remove toxic compounds before synthesis
2. **Use multiple models**: Consensus approach
3. **Check metabolites**: Metabolites may be toxic
4. **Consider dose**: Toxicity is dose-dependent
5. **Risk-benefit**: Severity of disease vs toxicity risk

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Over-removal | Balance safety with efficacy |
| False positives | Experimental validation needed |
| Ignoring metabolites | Test metabolic pathways |
| Late-stage testing | Early screening saves money |
| Species differences | Human relevance uncertain

## Regulatory Guidelines

| Agency | Guidance | Focus |
|--------|----------|-------|
| FDA | M3(R2) | Nonclinical safety |
| EMA | Guideline on repeated dose | Toxicity testing |
| ICH | S2(R1) | Genotoxicity |
| ICH | S7A/B | Safety pharmacology |
| ICH | S9 | Carcinogenicity
