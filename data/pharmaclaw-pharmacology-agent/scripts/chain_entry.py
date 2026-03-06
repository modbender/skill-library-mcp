#!/usr/bin/env python3
"""Pharmacology Agent - ADME/PK profiling via RDKit descriptors and rule-based predictions."""
import argparse
import json
import sys
import os
from datetime import datetime, timezone

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors, FilterCatalog
    from rdkit.Chem import QED as QEDModule
except ImportError as e:
    print(json.dumps({"error": f"RDKit import failed: {e}"}))
    sys.exit(1)

# Try SA Score import (may not be available in all RDKit installs)
try:
    from rdkit.Chem import RDConfig
    sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
    import sascorer
    HAS_SASCORER = True
except Exception:
    HAS_SASCORER = False

# PAINS filter catalog
try:
    params = FilterCatalog.FilterCatalogParams()
    params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
    PAINS_CATALOG = FilterCatalog.FilterCatalog(params)
    HAS_PAINS = True
except Exception:
    HAS_PAINS = False


def compute_descriptors(mol):
    """Compute core molecular descriptors."""
    mw = Descriptors.ExactMolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rotb = Descriptors.NumRotatableBonds(mol)
    arom_rings = Descriptors.NumAromaticRings(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    mr = Descriptors.MolMR(mol)
    return {
        "mw": round(mw, 2),
        "logp": round(logp, 4),
        "tpsa": round(tpsa, 2),
        "hbd": hbd,
        "hba": hba,
        "rotb": rotb,
        "arom_rings": arom_rings,
        "heavy_atoms": heavy_atoms,
        "mr": round(mr, 2),
    }


def lipinski(desc):
    """Lipinski Rule of Five."""
    violations = 0
    details = {}
    checks = [
        ("MW < 500", desc["mw"] < 500, desc["mw"]),
        ("logP < 5", desc["logp"] < 5, desc["logp"]),
        ("HBD < 5", desc["hbd"] < 5, desc["hbd"]),
        ("HBA < 10", desc["hba"] < 10, desc["hba"]),
    ]
    for label, passed, val in checks:
        details[label] = {"value": val, "pass": passed}
        if not passed:
            violations += 1
    return {
        "pass": violations <= 1,
        "violations": violations,
        "details": details,
    }


def veber(desc):
    """Veber rules for oral bioavailability."""
    tpsa_ok = desc["tpsa"] <= 140
    rotb_ok = desc["rotb"] <= 10
    return {
        "pass": tpsa_ok and rotb_ok,
        "tpsa": {"value": desc["tpsa"], "threshold": 140, "pass": tpsa_ok},
        "rotatable_bonds": {"value": desc["rotb"], "threshold": 10, "pass": rotb_ok},
    }


def compute_qed(mol):
    """Quantitative Estimate of Drug-likeness."""
    try:
        return round(QEDModule.qed(mol), 4)
    except Exception:
        return None


def compute_sa_score(mol):
    """Synthetic Accessibility Score (1=easy, 10=hard)."""
    if not HAS_SASCORER:
        return None
    try:
        return round(sascorer.calculateScore(mol), 2)
    except Exception:
        return None


def predict_adme(desc):
    """Rule-based ADME predictions."""
    adme = {}

    # BBB permeability (Clark's rules: TPSA<90 and logP 1-3 favorable)
    if desc["tpsa"] < 60 and 1 <= desc["logp"] <= 3:
        adme["bbb"] = {"prediction": "high", "confidence": "medium",
                       "rationale": f"TPSA={desc['tpsa']}<60, logP={desc['logp']} in 1-3 range"}
    elif desc["tpsa"] < 90:
        adme["bbb"] = {"prediction": "moderate", "confidence": "medium",
                       "rationale": f"TPSA={desc['tpsa']}<90"}
    else:
        adme["bbb"] = {"prediction": "low", "confidence": "medium",
                       "rationale": f"TPSA={desc['tpsa']}>=90, poor CNS penetration expected"}

    # Aqueous solubility (ESOL-like estimate: logS ≈ 0.16 - 0.63*logP - 0.0062*MW + 0.066*rotB - 0.74*aromRings)
    log_s = 0.16 - 0.63 * desc["logp"] - 0.0062 * desc["mw"] + 0.066 * desc["rotb"] - 0.74 * desc["arom_rings"]
    log_s = round(log_s, 2)
    if log_s > -2:
        sol_class = "high"
    elif log_s > -4:
        sol_class = "moderate"
    else:
        sol_class = "low"
    adme["solubility"] = {"logS_estimate": log_s, "class": sol_class,
                          "rationale": "ESOL-approximation from descriptors"}

    # GI absorption (Egan egg: logP<5.6 and TPSA<131.6)
    gi_pass = desc["logp"] < 5.6 and desc["tpsa"] < 131.6
    adme["gi_absorption"] = {"prediction": "high" if gi_pass else "low",
                             "rationale": "Egan egg model (logP/TPSA)"}

    # CYP3A4 inhibition risk (rule-based)
    cyp_risk = desc["logp"] > 3 and desc["mw"] > 300
    adme["cyp3a4_inhibition"] = {
        "risk": "high" if cyp_risk else "low",
        "rationale": f"logP={desc['logp']}>3 and MW={desc['mw']}>300" if cyp_risk else "Below risk thresholds"
    }

    # P-glycoprotein substrate prediction
    pgp_sub = desc["mw"] > 400 and desc["hbd"] > 2
    adme["pgp_substrate"] = {
        "prediction": "likely" if pgp_sub else "unlikely",
        "rationale": f"MW={desc['mw']}>400 and HBD={desc['hbd']}>2" if pgp_sub else "Below Pgp substrate thresholds"
    }

    # Plasma protein binding
    ppb_high = desc["logp"] > 3
    adme["plasma_protein_binding"] = {
        "prediction": "high (>90%)" if ppb_high else "moderate-low",
        "rationale": f"logP={desc['logp']}>3 suggests high PPB" if ppb_high else f"logP={desc['logp']}<=3"
    }

    return adme


def check_pains(mol):
    """Check for PAINS (Pan-Assay Interference Compounds) alerts."""
    if not HAS_PAINS:
        return {"checked": False, "reason": "PAINS catalog not available"}
    entry = PAINS_CATALOG.GetFirstMatch(mol)
    if entry:
        return {"alert": True, "pattern": entry.GetDescription()}
    return {"alert": False}


def assess_risks(desc, lipinski_result, adme, pains_result):
    """Compile risk factors."""
    risks = []
    if not lipinski_result["pass"]:
        risks.append(f"Lipinski violations: {lipinski_result['violations']}")
    if desc["mw"] > 600:
        risks.append(f"High MW ({desc['mw']}) - oral absorption concerns")
    if desc["logp"] > 5:
        risks.append(f"High logP ({desc['logp']}) - solubility/metabolism concerns")
    if desc["tpsa"] > 140:
        risks.append(f"High TPSA ({desc['tpsa']}) - permeability concerns")
    if adme.get("solubility", {}).get("class") == "low":
        risks.append("Low predicted aqueous solubility")
    if adme.get("cyp3a4_inhibition", {}).get("risk") == "high":
        risks.append("CYP3A4 inhibition risk - potential drug-drug interactions")
    if adme.get("pgp_substrate", {}).get("prediction") == "likely":
        risks.append("Likely P-gp substrate - may affect oral absorption")
    if isinstance(pains_result, dict) and pains_result.get("alert"):
        risks.append(f"PAINS alert: {pains_result.get('pattern', 'unknown')}")
    return risks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--input-json')
    args = parser.parse_args()

    if args.input_json:
        input_data = json.loads(args.input_json)
    else:
        input_data = json.load(sys.stdin)

    smiles = input_data.get('smiles', '')
    canonical_smiles = ''

    try:
        if not smiles:
            name = input_data.get('name', '')
            if not name:
                raise ValueError('Require "smiles" or "name" in input')
            # Try to resolve via PubChem (optional - caller should provide SMILES)
            raise ValueError(f'No SMILES provided. Chain from chemistry-query first, or provide "smiles" directly.')

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f'Invalid SMILES: {smiles}')
        canonical_smiles = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)

        # Core descriptors
        desc = compute_descriptors(mol)

        # Drug-likeness rules
        lip = lipinski(desc)
        veb = veber(desc)
        qed_val = compute_qed(mol)
        sa_score = compute_sa_score(mol)

        # ADME predictions
        adme = predict_adme(desc)

        # PAINS check
        pains = check_pains(mol)

        # Risk assessment
        risks = assess_risks(desc, lip, adme, pains)

        report = {
            "descriptors": desc,
            "lipinski": lip,
            "veber": veb,
            "qed": qed_val,
            "sa_score": sa_score,
            "adme": adme,
            "pains": pains,
        }

        output = {
            "agent": "pharma-pharmacology",
            "version": "1.1.0",
            "smiles": canonical_smiles,
            "status": "success",
            "report": report,
            "risks": risks,
            "recommend_next": ["toxicology", "ip-expansion"],
            "confidence": 0.85,
            "warnings": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        output = {
            "agent": "pharma-pharmacology",
            "version": "1.1.0",
            "smiles": canonical_smiles,
            "status": "error",
            "report": {},
            "risks": [],
            "recommend_next": ["toxicology", "ip-expansion"],
            "confidence": 0.0,
            "warnings": [str(e)],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    print(json.dumps(output, indent=2, default=str))


if __name__ == '__main__':
    main()
