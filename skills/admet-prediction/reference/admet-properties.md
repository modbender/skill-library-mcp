# ADMET Properties Reference

Comprehensive reference for ADMET property prediction.

## Property Categories

| Category | Properties | Impact |
|----------|------------|--------|
| Absorption | HIA, Caco-2, Pgp, F% | Oral bioavailability |
| Distribution | VDss, PPB, BBB | Tissue exposure |
| Metabolism | CYP, Clearance | PK profile |
| Excretion | Half-life, CL | Dosing frequency |
| Toxicity | hERG, DILI, Ames | Safety |

## Absorption Properties

### Human Intestinal Absorption (HIA)

**Definition**: Percentage of orally administered drug reaching systemic circulation.

**Prediction methods**:
- Rule-based (PSA, LogP)
- Machine learning (random forest, neural networks)

**Good range**: >80%
**Poor range**: <40%

**Rule of thumb**:
```
HIA_good = PSA < 75 Ų or (PSA < 140 Ų and LogP > 0)
```

### Caco-2 Permeability

**Definition**: Permeability across Caco-2 cell monolayer.

**Units**: × 10⁻⁶ cm/s

**Ranges**:
| Value | Interpretation |
|-------|----------------|
| >10 | High permeability |
| 1-10 | Moderate |
| <1 | Low |

**Influencing factors**:
- Molecular weight
- Hydrogen bonding
- Polar surface area

### P-glycoprotein Substrate

**Definition**: Whether compound is transported by Pgp.

**Impact**: Efflux reduces oral absorption and brain penetration.

**Prediction rules**:
- Basic nitrogen + PSA > 75 Ų → Likely substrate
- MW > 400 + aromatic → Likely substrate

### Bioavailability (F%)

**Definition**: Percentage of oral dose reaching systemic circulation unchanged.

**Good range**: >50%
**Excellent range**: >70%

**Influencing factors**:
- First-pass metabolism
- Solubility
- Permeability
- Stability

## Distribution Properties

### Volume of Distribution (VDss)

**Definition**: Apparent volume in which drug distributes.

**Units**: L/kg

**Ranges**:
| Value | Interpretation |
|-------|----------------|
| <0.3 L/kg | Plasma distribution |
| 0.3-5 L/kg | Moderate distribution |
| >5 L/kg | Extensive tissue distribution |

**Influencing factors**:
- Lipophilicity (LogP)
- Plasma protein binding
- Tissue binding

**Rule of thumb**:
```
VDss ≈ 0.5 + LogP (approximate)
```

### Plasma Protein Binding (PPB)

**Definition**: Percentage bound to plasma proteins.

**Ranges**:
| Value | Interpretation |
|-------|----------------|
| <90% | Low binding |
| 90-95% | Moderate |
| >95% | High binding |

**Major proteins**: Albumin, α1-acid glycoprotein

**Impact**: High PPB → Low free concentration

### Blood-Brain Barrier (BBB)

**Definition**: Ability to cross BBB.

**Prediction rules**:
- LogBB > -0.3 → Permeable
- LogBB < -0.3 → Non-permeable

**LogBB calculation**:
```
LogBB = 0.152 - 0.0148 × PSA + 0.138 × LogP
```

**CNS MPO score** (6-point scale):
- LogP: 2-4 ideal
- PSA: <90 Ų ideal
- MW: <450 Da ideal
- HBD: ≤1 ideal
- pKa: 8-10 ideal

## Metabolism Properties

### CYP450 Interactions

**CYP3A4** (most common):
- Substrates: ~50% of drugs
- Inhibition: Common with basic nitrogen compounds
- Induction: Rifampin-like

**CYP2D6**:
- Polymorphic enzyme
- Substrates: Basic amines
- Inhibition: Competitive

**CYP2C9**:
- Substrates: Acidic compounds
- Inhibition: NSAID-like

**Prediction rules**:
- Basic nitrogen + LogP > 3 → CYP3A4 inhibitor likely
- Aromatic amine → CYP2D6 substrate likely

### Clearance

**Definition**: Volume of plasma cleared per time.

**Units**: mL/min/kg

**Ranges**:
| Value | Interpretation |
|-------|----------------|
| <5 | Low clearance |
| 5-15 | Moderate |
| >15 | High clearance |

**Hepatic clearance prediction**:
```
CLh = Qh × (f × CLint) / (Qh + f × CLint)
```

Where:
- Qh = hepatic blood flow (~90 L/h for human)
- f = fraction unbound
- CLint = intrinsic clearance

## Excretion Properties

### Half-Life

**Definition**: Time for plasma concentration to decrease by 50%.

**Units**: hours

**Ranges**:
| Value | Dosing Frequency |
|-------|------------------|
| <4 h | QID |
| 4-8 h | TID/BID |
| 8-16 h | BID/QD |
| >16 h | QD |

**Relationship**:
```
t1/2 = 0.693 × VD / CL
```

### Renal Excretion

**Definition**: Percentage excreted unchanged in urine.

**Ranges**:
| Value | Interpretation |
|-------|----------------|
| <10% | Minimal renal |
| 10-30% | Moderate renal |
| >30% | Significant renal |

**Impact**: Renal impairment requires dose adjustment

## Toxicity Properties

### hERG Inhibition

**Definition**: Blockade of hERG potassium channel.

**Risk**: Cardiac arrhythmia (QT prolongation)

**Prediction rules**:
- Basic nitrogen + Aromatic = High risk
- LogP > 3 + MW > 400 = High risk

### DILI (Drug-Induced Liver Injury)

**Definition**: Liver damage caused by drug.

**Categories**:
- Most DILI concern
- Less DILI concern
- No DILI concern

**Risk factors**:
- LogP > 3
- Aromatic rings > 3
- Reactive functional groups

### Ames Mutagenicity

**Definition**: Bacterial reverse mutation assay result.

**Positive indicators**:
- Aromatic nitro groups
- Azo groups
- Epoxides
- Alkylating agents

### Carcinogenicity

**Definition**: Potential to cause cancer.

**Prediction**: Based on structural alerts and Ames result

## Property Calculation Tools

| Tool | Method | Coverage |
|------|--------|----------|
| ADMETlab 2.0 | Deep learning | Comprehensive |
| pkCSM | ML-based | 20+ properties |
| SwissADME | Rule-based | Key properties |
| ProTox-II | Toxicity | Toxicity only |
| DeepPurpose | Graph neural network | Binding + ADMET |

## Best Practices

1. **Use multiple models**: Consensus more reliable
2. **Check applicability domain**: Novel scaffolds uncertain
3. **Consider chemistry**: Functional groups matter
4. **Validate early**: In vitro confirmation needed
5. **Iterate design**: Use predictions to guide synthesis

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Over-reliance | Experimental validation required |
| Single model | Use consensus |
| Ignoring confidence | Check AD |
| Novel chemistry | High uncertainty |
| Late testing | Early ADMET saves money

## Reference Values

### Oral Drug Standards

| Property | Typical Range |
|----------|---------------|
| MW | 200-500 Da |
| LogP | 1-4 |
| PSA | 40-120 Ų |
| HBD | 0-3 |
| HBA | 2-8 |
| RotB | 2-8 |
| F% | 30-70% |
| t1/2 | 6-24 h |

### CNS Drug Standards

| Property | Typical Range |
|----------|---------------|
| MW | 200-450 Da |
| LogP | 2-4 |
| PSA | <90 Ų |
| HBD | 0-2 |
| CNS MPO | >4 |
| LogBB | >-0.3 |
