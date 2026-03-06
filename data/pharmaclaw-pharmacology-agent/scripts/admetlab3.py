#!/usr/bin/env python3
"""ADMETlab 3.0 Integration — ML-based ADME/Tox predictions.

Queries the ADMETlab 3.0 API for ML-predicted ADME, toxicity, and druglikeness
properties. Falls back to RDKit rule-based predictions if API is unavailable.

ADMETlab 3.0: https://admetlab3.scbdd.com (Zhejiang University, free, no key required)

Usage:
    python admetlab3.py --smiles "CC(=O)OC1=CC=CC=C1C(=O)O"
    python admetlab3.py --smiles "CN1C=NC2=C1C(=O)N(C(=O)N2C)C" --categories absorption,toxicity
    python admetlab3.py --smiles "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O" --all
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print(json.dumps({"status": "error", "error": "requests not installed"}))
    sys.exit(1)

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

ADMETLAB_URL = "https://admetlab3.scbdd.com/service/evaluation"
TIMEOUT = 30

# ADMETlab 3.0 endpoint categories
ENDPOINTS = {
    "absorption": {
        "caco2": "Caco-2 permeability (intestinal absorption model)",
        "hia": "Human intestinal absorption",
        "pgp_inhibitor": "P-glycoprotein inhibitor",
        "pgp_substrate": "P-glycoprotein substrate",
        "bioavailability": "Oral bioavailability (F20%)",
    },
    "distribution": {
        "bbb": "Blood-brain barrier penetration",
        "ppb": "Plasma protein binding",
        "vd": "Volume of distribution",
    },
    "metabolism": {
        "cyp1a2_inhibitor": "CYP1A2 inhibitor",
        "cyp2c19_inhibitor": "CYP2C19 inhibitor",
        "cyp2c9_inhibitor": "CYP2C9 inhibitor",
        "cyp2d6_inhibitor": "CYP2D6 inhibitor",
        "cyp3a4_inhibitor": "CYP3A4 inhibitor",
        "cyp2d6_substrate": "CYP2D6 substrate",
        "cyp3a4_substrate": "CYP3A4 substrate",
    },
    "excretion": {
        "clearance": "Total clearance",
        "half_life": "Half-life",
    },
    "toxicity": {
        "herg": "hERG channel inhibition (cardiotoxicity)",
        "ames": "Ames mutagenicity",
        "dili": "Drug-induced liver injury",
        "skin_sensitization": "Skin sensitization",
        "carcinogenicity": "Carcinogenicity",
        "respiratory_toxicity": "Respiratory toxicity",
        "eye_irritation": "Eye irritation/corrosion",
    },
    "physicochemical": {
        "logp": "Lipophilicity (LogP)",
        "logs": "Aqueous solubility (LogS)",
        "logd": "Distribution coefficient (LogD7.4)",
        "pka": "Acid dissociation constant",
    },
}


def query_admetlab(smiles: str, categories: list[str] = None) -> dict:
    """Query ADMETlab 3.0 API for ADME/Tox predictions."""
    results = {}
    errors = []

    # Validate SMILES first
    if HAS_RDKIT:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"status": "error", "error": f"Invalid SMILES: {smiles}"}
        smiles = Chem.MolToSmiles(mol)  # Canonicalize

    if categories is None:
        categories = list(ENDPOINTS.keys())

    # Try ADMETlab 3.0 API
    try:
        # ADMETlab 3.0 accepts SMILES via POST
        payload = {"smiles": smiles}
        resp = requests.post(
            f"{ADMETLAB_URL}/alogps",
            json=payload,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

        if resp.status_code == 200:
            data = resp.json()
            if data and not isinstance(data, str):
                results["admetlab3_raw"] = data
                results["source"] = "admetlab3"
        else:
            errors.append(f"ADMETlab API returned {resp.status_code}")
    except requests.exceptions.Timeout:
        errors.append("ADMETlab API timeout (30s)")
    except requests.exceptions.ConnectionError:
        errors.append("ADMETlab API unreachable")
    except Exception as e:
        errors.append(f"ADMETlab API error: {str(e)}")

    # Always compute RDKit-based predictions as baseline/fallback
    if HAS_RDKIT:
        rdkit_results = compute_rdkit_adme(smiles)
        if results.get("source") == "admetlab3":
            results["rdkit_baseline"] = rdkit_results
        else:
            results.update(rdkit_results)
            results["source"] = "rdkit_computed"
            if errors:
                results["api_notes"] = errors

    return results


def compute_rdkit_adme(smiles: str) -> dict:
    """Comprehensive RDKit-based ADME predictions (rule-based + descriptor-based)."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}

    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Descriptors.NumHDonors(mol)
    hba = Descriptors.NumHAcceptors(mol)
    rotb = Descriptors.NumRotatableBonds(mol)
    arom_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    fsp3 = rdMolDescriptors.CalcFractionCSP3(mol)
    num_rings = rdMolDescriptors.CalcNumRings(mol)
    mr = Descriptors.MolMR(mol)

    # --- Absorption predictions ---
    # Lipinski Ro5
    lipinski_violations = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    lipinski_pass = lipinski_violations <= 1

    # Veber rules (oral bioavailability)
    veber_pass = rotb <= 10 and tpsa <= 140

    # Egan absorption model (logP vs TPSA)
    egan_pass = -1 < logp < 5.88 and tpsa < 131.6

    # HIA prediction (simple model: TPSA < 140 and logP > -1)
    hia_prediction = "High" if tpsa < 140 and logp > -1 else "Low"

    # Caco-2 prediction (Yazdanian model: logP-based estimate)
    # log Papp ≈ -5.47 + 0.54 * logP (simplified)
    caco2_log_papp = -5.47 + 0.54 * logp
    caco2_permeable = caco2_log_papp > -5.15  # threshold for high permeability

    # --- Distribution predictions ---
    # BBB penetration (Clark model: logP - (MW/100) + PSA correction)
    bbb_score = logp - 0.148 * (tpsa ** 0.5) - 0.00845 * mw
    bbb_penetrant = bbb_score > 0

    # PPB estimate (high LogP = high binding)
    ppb_prediction = "High (>90%)" if logp > 3 else "Moderate (50-90%)" if logp > 1 else "Low (<50%)"

    # --- Metabolism predictions ---
    # CYP3A4 inhibition risk (MW > 400, LogP > 3, aromatic rings)
    cyp3a4_risk = "High" if (mw > 400 and logp > 3) or arom_rings >= 3 else "Moderate" if mw > 300 and logp > 2 else "Low"

    # P-gp substrate prediction (MW > 400, HBD > 2)
    pgp_substrate = "Likely" if mw > 400 and hbd > 2 else "Unlikely"

    # --- Toxicity predictions ---
    # hERG risk (LogP > 3.7 and basic amine)
    has_basic_n = any(a.GetSymbol() == "N" and a.GetFormalCharge() >= 0
                      and not a.GetIsAromatic() for a in mol.GetAtoms())
    herg_risk = "High" if logp > 3.7 and has_basic_n else "Moderate" if logp > 3 else "Low"

    # Ames mutagenicity risk (aromatic amines, nitro groups)
    has_nitro = mol.HasSubstructMatch(Chem.MolFromSmarts("[N+](=O)[O-]")) if Chem.MolFromSmarts("[N+](=O)[O-]") else False
    has_aromatic_amine = mol.HasSubstructMatch(Chem.MolFromSmarts("[NH2]c")) if Chem.MolFromSmarts("[NH2]c") else False
    ames_risk = "High" if (has_nitro or has_aromatic_amine) else "Low"

    # DILI risk (reactive metabolite potential)
    dili_risk = "Moderate" if logp > 3 and mw > 300 else "Low"

    # --- Solubility ---
    # ESOL model: LogS = 0.16 - 0.63*logP - 0.0062*MW + 0.066*rotB - 0.74*aromRings
    logs_esol = 0.16 - 0.63 * logp - 0.0062 * mw + 0.066 * rotb - 0.74 * arom_rings
    solubility_class = "High" if logs_esol > -2 else "Moderate" if logs_esol > -4 else "Low" if logs_esol > -6 else "Very Low"

    # --- Druglikeness scores ---
    try:
        from rdkit.Chem import QED as QEDModule
        qed = round(QEDModule.qed(mol), 4)
    except:
        qed = None

    # Synthetic accessibility
    try:
        from rdkit.Chem import RDConfig
        import os
        sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
        import sascorer
        sa_score = round(sascorer.calculateScore(mol), 2)
    except:
        sa_score = None

    return {
        "smiles": Chem.MolToSmiles(mol),
        "physicochemical": {
            "MW": round(mw, 2),
            "logP": round(logp, 2),
            "TPSA": round(tpsa, 2),
            "HBD": hbd,
            "HBA": hba,
            "rotatable_bonds": rotb,
            "aromatic_rings": arom_rings,
            "heavy_atoms": heavy_atoms,
            "fraction_csp3": round(fsp3, 3),
            "num_rings": num_rings,
            "molar_refractivity": round(mr, 2),
            "logS_ESOL": round(logs_esol, 2),
            "solubility_class": solubility_class,
        },
        "absorption": {
            "lipinski": {"pass": lipinski_pass, "violations": lipinski_violations},
            "veber": {"pass": veber_pass, "rotB_ok": rotb <= 10, "TPSA_ok": tpsa <= 140},
            "egan": {"pass": egan_pass},
            "HIA": hia_prediction,
            "caco2_log_papp": round(caco2_log_papp, 2),
            "caco2_permeable": caco2_permeable,
            "pgp_substrate": pgp_substrate,
            "oral_bioavailability": "Likely" if lipinski_pass and veber_pass else "Unlikely",
        },
        "distribution": {
            "BBB_score": round(bbb_score, 2),
            "BBB_penetrant": bbb_penetrant,
            "PPB": ppb_prediction,
        },
        "metabolism": {
            "CYP3A4_inhibition_risk": cyp3a4_risk,
        },
        "excretion": {
            "note": "Clearance/half-life require ML models (ADMETlab 3.0) for accurate prediction.",
        },
        "toxicity": {
            "hERG_risk": herg_risk,
            "ames_mutagenicity_risk": ames_risk,
            "DILI_risk": dili_risk,
            "alerts": {
                "nitro_group": has_nitro,
                "aromatic_amine": has_aromatic_amine,
            },
        },
        "druglikeness": {
            "QED": qed,
            "SA_score": sa_score,
            "lipinski_pass": lipinski_pass,
            "veber_pass": veber_pass,
            "lead_like": mw <= 350 and logp <= 3.5 and rotb <= 7,
            "drug_like": lipinski_pass and veber_pass and -2 < logp < 5,
        },
    }


def predict(smiles: str, categories: list[str] = None) -> dict:
    """Main prediction function."""
    results = query_admetlab(smiles, categories)

    return {
        "agent": "pharmacology",
        "version": "2.0.0",
        "action": "adme_predict",
        "smiles": smiles,
        "status": "success" if "error" not in results else "error",
        "predictions": results,
        "endpoints_available": ENDPOINTS,
        "recommend_next": ["toxicology", "ip-expansion", "literature"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="ADMETlab 3.0 + RDKit ADME Predictions")
    parser.add_argument("--smiles", required=True, help="SMILES string")
    parser.add_argument("--categories", help="Comma-separated: absorption,distribution,metabolism,excretion,toxicity,physicochemical")
    parser.add_argument("--all", action="store_true", help="Run all categories")
    args = parser.parse_args()

    categories = args.categories.split(",") if args.categories else None
    result = predict(args.smiles, categories)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
