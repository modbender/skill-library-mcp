# ADME Prediction Rules Reference

## Drug-Likeness Rules

### Lipinski Rule of Five (Ro5)
- MW < 500 Da
- logP < 5
- HBD (hydrogen bond donors) < 5
- HBA (hydrogen bond acceptors) < 10
- **Pass:** ≤1 violation. Ref: Lipinski et al., Adv Drug Deliv Rev, 2001.

### Veber Rules (Oral Bioavailability)
- TPSA ≤ 140 Å²
- Rotatable bonds ≤ 10
- Ref: Veber et al., J Med Chem, 2002.

## ADME Prediction Methods

### BBB Permeability (Clark's Rules)
- TPSA < 60 + logP 1–3 → high penetration
- TPSA < 90 → moderate
- TPSA ≥ 90 → low
- Ref: Clark, J Pharm Sci, 1999.

### Aqueous Solubility (ESOL Approximation)
- logS ≈ 0.16 − 0.63·logP − 0.0062·MW + 0.066·rotB − 0.74·aromRings
- logS > −2: high; −4 to −2: moderate; < −4: low
- Ref: Delaney, J Chem Inf Model, 2004.

### GI Absorption (Egan Egg Model)
- High if logP < 5.6 AND TPSA < 131.6
- Ref: Egan et al., J Med Chem, 2000.

### CYP3A4 Inhibition Risk
- Rule-based: logP > 3 AND MW > 300 → high risk
- Rationale: lipophilic, larger molecules more likely CYP substrates/inhibitors.

### P-glycoprotein Substrate
- MW > 400 AND HBD > 2 → likely substrate
- Ref: Polli et al., J Pharmacol Exp Ther, 2001.

### Plasma Protein Binding
- logP > 3 → high binding (>90%)
- Ref: Yamazaki & Kanaoka, J Pharm Sci, 2004.

## Scores

### QED (Quantitative Estimate of Drug-likeness)
- Range 0–1 (higher = more drug-like)
- Ref: Bickerton et al., Nat Chem, 2012.

### SA Score (Synthetic Accessibility)
- Range 1–10 (1 = easy, 10 = hard)
- Ref: Ertl & Schuffenhauer, J Cheminform, 2009.

### PAINS (Pan-Assay Interference Compounds)
- RDKit FilterCatalog with PAINS catalog
- Ref: Baell & Holloway, J Med Chem, 2010.
