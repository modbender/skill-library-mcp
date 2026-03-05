#!/usr/bin/env python3
"""
ADMET property prediction for drug discovery.

Usage:
    python admet_predict.py --smiles "CC1=CC=C..." --full
    python admet_predict.py --library compounds.sdf --properties hERG,DILI
    python admet_predict.py --filter lipinski,veber --input molecules.smi
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, rdMolDescriptors
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
except ImportError:
    print("Error: RDKit required. Install with: pip install rdkit")
    sys.exit(1)


class ADMETPredictor:
    """Predict ADMET properties from molecular structure."""

    # Toxicity substructure alerts (simplified)
    TOXICITY_ALERTS = {
        "hERG": [
            "N>1@C>1CCN(CC)CC",  # Basic tertiary amine with aromatic
            "c1ccccc1N>1",       # Aromatic amine
        ],
        "DILI": [
                # Thiophene
            "C1=CS=CC=C1",       # Thiophene
        ],
        "Ames": [
            "N=[N+]=[N-]",       # Azo group
            "c1ccc([N+](=O)[O-])cc1",  # Nitroaromatic
        ],
        "PAINS": [
                # Various PAINS patterns
        ]
    }

    def __init__(self):
        self.results = {
            "compounds": [],
            "timestamp": datetime.now().isoformat()
        }

        # Initialize filter catalog
        self._init_filters()

    def _init_filters(self):
        """Initialize RDKit filter catalogs."""
        try:
            # PAINS filter
            pains_params = FilterCatalogParams()
            pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
            self.pains_catalog = FilterCatalog(pains_params)

            # Brenk filter
            brenk_params = FilterCatalogParams()
            brenk_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
            self.brenk_catalog = FilterCatalog(brenk_params)
        except:
            self.pains_catalog = None
            self.brenk_catalog = None

    def predict_full(self, smiles: str, name: str = None) -> Dict[str, Any]:
        """Predict full ADMET profile."""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol:
                return {"error": "Invalid SMILES"}

            mol = Chem.AddHs(mol)

            profile = {
                "name": name or "Unknown",
                "smiles": smiles,
                "drug_likeness": self._assess_drug_likeness(mol),
                "absorption": self._predict_absorption(mol),
                "distribution": self._predict_distribution(mol),
                "metabolism": self._predict_metabolism(mol),
                "excretion": self._predict_excretion(mol),
                "toxicity": self._predict_toxicity(mol)
            }

            return profile

        except Exception as e:
            return {"error": str(e)}

    def predict_batch(self, input_file: str, properties: List[str] = None) -> List[Dict]:
        """Predict ADMET for compound library."""
        try:
            print(f"Processing {input_file}")

            compounds = self._read_compounds(input_file)
            results = []

            for i, (smiles, name) in enumerate(compounds):
                print(f"  Processing {i+1}/{len(compounds)}: {name}")

                if properties:
                    profile = self._predict_specific(smiles, properties)
                else:
                    profile = self.predict_full(smiles, name)

                results.append(profile)

            self.results["compounds"] = results
            return results

        except Exception as e:
            print(f"✗ Batch prediction error: {e}")
            return []

    def filter_compounds(self, input_file: str, rules: List[str]) -> List[Dict]:
        """Filter compounds by drug-likeness rules."""
        try:
            compounds = self._read_compounds(input_file)
            passed = []

            for smiles, name in compounds:
                mol = Chem.MolFromSmiles(smiles)
                if not mol:
                    continue

                violations = self._check_rules(mol, rules)

                passed.append({
                    "name": name,
                    "smiles": smiles,
                    "passed": violations["passed"],
                    "violations": violations["details"],
                    "score": violations["score"]
                })

            return passed

        except Exception as e:
            print(f"✗ Filter error: {e}")
            return []

    def _read_compounds(self, input_file: str) -> List[tuple]:
        """Read compounds from file."""
        compounds = []

        if input_file.endswith('.sdf'):
            suppl = Chem.SDMolSupplier(input_file)
            for mol in suppl:
                if mol:
                    name = mol.GetProp('_Name') if mol.HasProp('_Name') else f"Mol{len(compounds)}"
                    smiles = Chem.MolToSmiles(mol)
                    compounds.append((smiles, name))

        elif input_file.endswith('.smi'):
            with open(input_file) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 1:
                        smiles = parts[0]
                        name = parts[1] if len(parts) > 1 else f"Mol{len(compounds)}"
                        compounds.append((smiles, name))

        return compounds

    def _assess_drug_likeness(self, mol) -> Dict:
        """Assess drug-likeness."""
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Lipinski.NumHDonors(mol)
        hba = Lipinski.NumHAcceptors(mol)
        psa = Descriptors.TPSA(mol)
        rotb = Lipinski.NumRotatableBonds(mol)

        # Lipinski violations
        ro5_violations = sum([
            mw > 500,
            logp > 5,
            hbd > 5,
            hba > 10
        ])

        # Veber criteria
        veber_pass = rotb <= 10 and psa <= 140

        # Egan criteria
        egan_pass = logp <= 5 and psa <= 131.6

        # Filter alerts
        pains_matches = self._check_catalog(mol, self.pains_catalog)
        brenk_matches = self._check_catalog(mol, self.brenk_catalog)

        return {
            "mw": round(mw, 1),
            "logp": round(logp, 2),
            "hbd": hbd,
            "hba": hba,
            "psa": round(psa, 1),
            "rotb": rotb,
            "ro5_violations": ro5_violations,
            "ro5_pass": ro5_violations <= 1,
            "veber_pass": veber_pass,
            "egan_pass": egan_pass,
            "pains_alerts": len(pains_matches),
            "brenk_alerts": len(brenk_matches),
            "drug_likeness": "Pass" if ro5_violations <= 1 and veber_pass else "Fail"
        }

    def _predict_absorption(self, mol) -> Dict:
        """Predict absorption properties."""
        # Simplified predictions based on physicochemical properties
        psa = Descriptors.TPSA(mol)
        logp = Descriptors.MolLogP(mol)
        mw = Descriptors.MolWt(mol)

        # Human Intestinal Absorption (HIA)
        # Rule of thumb: good if PSA < 140 and LogP > 0
        hia_prob = 0.98 if psa < 75 else (0.85 if psa < 100 else 0.5)

        # Caco-2 permeability
        caco2 = 25 * (1 - psa/200) if psa < 140 else 0

        # P-gp substrate prediction (basic, high PSA)
        is_basic = any(atom.GetFormalCharge() > 0 for atom in mol.GetAtoms())
        pgp_sub = is_basic and psa > 75

        # Bioavailability (F%)
        # Lipinski + Veber = good oral bioavailability
        ro5_violations = sum([
            Descriptors.MolWt(mol) > 500,
            Descriptors.MolLogP(mol) > 5,
            Lipinski.NumHDonors(mol) > 5,
            Lipinski.NumHAcceptors(mol) > 10
        ])
        f_percent = max(10, 80 - ro5_violations * 20 - (1 if psa > 140 else 0) * 30)

        return {
            "hia": f"{int(hia_prob * 100)}%",
            "hia_probability": round(hia_prob, 2),
            "caco2": f"{caco2:.1f} × 10⁻⁶ cm/s",
            "caco2_value": round(caco2, 1),
            "pgp_substrate": "Yes" if pgp_sub else "No",
            "bioavailability": f"{int(f_percent)}%",
            "bioavailability_value": round(f_percent, 0)
        }

    def _predict_distribution(self, mol) -> Dict:
        """Predict distribution properties."""
        logp = Descriptors.MolLogP(mol)
        psa = Descriptors.TPSA(mol)

        # Volume of distribution (VDss)
        # High LogP = high VDss
        vdss = 0.5 * logp + 2

        # Plasma protein binding
        # High LogP = high PPB
        ppb = min(99, 50 + logp * 10)

        # Blood-brain barrier penetration
        # Rule: LogP > 0 and PSA < 90
        logbb = 0.5 - 0.01 * psa + 0.1 * logp
        bbb_penetrant = logbb > -0.3

        # CNS MPO score
        cns_mpo = self._calculate_cns_mpo(mol)

        return {
            "vdss": f"{vdss:.1f} L/kg",
            "vdss_value": round(vdss, 1),
            "ppb": f"{int(ppb)}%",
            "ppb_value": round(ppb, 0),
            "bbb": "Yes" if bbb_penetrant else "No",
            "logbb": round(logbb, 2),
            "cns_mpo": round(cns_mpo, 1)
        }

    def _predict_metabolism(self, mol) -> Dict:
        """Predict metabolism properties."""
        # Simplified CYP predictions
        logp = Descriptors.MolLogP(mol)

        # CYP3A4 substrate (most drugs are)
        cyp3a4_sub = "Yes"  # Conservative assumption

        # CYP3A4 inhibitor
        # High logP, nitrogen-containing compounds likely
        n_count = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'N')
        cyp3a4_inh = "Yes" if logp > 3 and n_count > 2 else "No"

        # CYP2D6 inhibition (basic nitrogen)
        is_basic = any(atom.GetFormalCharge() > 0 for atom in mol.GetAtoms()
                      if atom.GetSymbol() == 'N')
        cyp2d6_inh = "Possible" if is_basic else "No"

        # Clearance
        # Low clearance for lipophilic compounds
        cl_hepatic = max(2, 15 - logp * 2)

        return {
            "cyp3a4_substrate": cyp3a4_sub,
            "cyp3a4_inhibitor": cyp3a4_inh,
            "cyp2d6_inhibitor": cyp2d6_inh,
            "cyp2c9_inhibitor": "No",  # Simplified
            "clearance": f"{cl_hepatic:.1f} mL/min/kg",
            "clearance_value": round(cl_hepatic, 1)
        }

    def _predict_excretion(self, mol) -> Dict:
        """Predict excretion properties."""
        logp = Descriptors.MolLogP(mol)
        mw = Descriptors.MolWt(mol)

        # Half-life (correlated with logp and MW)
        half_life = 12 + logp * 4 + mw / 100

        # Renal excretion (inversely correlated with logp)
        renal_excretion = max(5, 50 - logp * 10)

        return {
            "half_life": f"{int(half_life)} hours",
            "half_life_value": round(half_life, 0),
            "renal_clearance": f"{int(renal_excretion)}%",
            "renal_clearance_value": round(renal_excretion, 0)
        }

    def _predict_toxicity(self, mol) -> Dict:
        """Predict toxicity properties."""
        smiles = Chem.MolToSmiles(mol)

        # hERG inhibition (basic nitrogen + aromatic)
        has_basic_n = any(atom.GetFormalCharge() > 0 for atom in mol.GetAtoms()
                          if atom.GetSymbol() == 'N')
        has_aromatic = any(atom.GetIsAromatic() for atom in mol.GetAtoms())
        herg_risk = "Yes" if has_basic_n and has_aromatic else "No"

        # DILI risk (simplified)
        logp = Descriptors.MolLogP(mol)
        dili_risk = "Concern" if logp > 3 else "Low"

        # Ames mutagenicity (structural alerts)
        ames_positive = "N"  # Simplified

        # Carcinogenicity
        carcinogenicity = "Unlikely"

        return {
            "herg_inhibition": herg_risk,
            "dili": dili_risk,
            "ames": ames_positive,
            "carcinogenicity": carcinogenicity,
            "respiratory_toxicity": "No",
            "overall_toxicity_risk": "Low" if herg_risk == "No" else "Moderate"
        }

    def _calculate_cns_mpo(self, mol) -> float:
        """Calculate CNS MPO score."""
        score = 0
        logp = Descriptors.MolLogP(mol)
        psa = Descriptors.TPSA(mol)
        mw = Descriptors.MolWt(mol)
        hbd = Lipinski.NumHDonors(mol)
        pka = 7  # Simplified

        # LogP: 2-4 ideal
        if 2 <= logp <= 4:
            score += 1
        elif 1 <= logp <= 5:
            score += 0.5

        # PSA: < 90 ideal
        if psa < 90:
            score += 1
        elif psa < 120:
            score += 0.5

        # MW: < 450 ideal
        if mw < 450:
            score += 1
        elif mw < 500:
            score += 0.5

        # HBD: <= 1 ideal
        if hbd <= 1:
            score += 1
        elif hbd <= 2:
            score += 0.5

        # pKa: 8-10 ideal
        if 8 <= pka <= 10:
            score += 1
        elif 7 <= pka <= 11:
            score += 0.5

        return score

    def _predict_specific(self, smiles: str, properties: List[str]) -> Dict:
        """Predict specific properties only."""
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return {"error": "Invalid SMILES"}

        results = {"smiles": smiles}

        for prop in properties:
            prop_lower = prop.lower()

            if "herg" in prop_lower:
                results["herg"] = self._predict_toxicity(mol)["herg_inhibition"]
            elif "dili" in prop_lower:
                results["dili"] = self._predict_toxicity(mol)["dili"]
            elif "ames" in prop_lower:
                results["ames"] = self._predict_toxicity(mol)["ames"]
            elif "cyp" in prop_lower:
                results["cyp"] = self._predict_metabolism(mol)
            elif "bbb" in prop_lower:
                results["bbb"] = self._predict_distribution(mol)["bbb"]

        return results

    def _check_rules(self, mol, rules: List[str]) -> Dict:
        """Check if compound passes specified rules."""
        details = {}
        passed = True

        for rule in rules:
            rule_lower = rule.lower()

            if "lipinski" in rule_lower or "ro5" in rule_lower:
                violations = sum([
                    Descriptors.MolWt(mol) > 500,
                    Descriptors.MolLogP(mol) > 5,
                    Lipinski.NumHDonors(mol) > 5,
                    Lipinski.NumHAcceptors(mol) > 10
                ])
                details["lipinski"] = f"{violations} violations"
                if violations > 1:
                    passed = False

            elif "veber" in rule_lower:
                rotb = Lipinski.NumRotatableBonds(mol)
                psa = Descriptors.TPSA(mol)
                veber_pass = rotb <= 10 and psa <= 140
                details["veber"] = "Pass" if veber_pass else "Fail"
                if not veber_pass:
                    passed = False

            elif "pains" in rule_lower:
                pains = self._check_catalog(mol, self.pains_catalog)
                details["pains"] = f"{len(pains)} alerts"
                if pains:
                    passed = False

        # Calculate score
        score = sum(1 for v in details.values() if "Pass" in v or "0 violations" in v or "0 alerts" in v)

        return {
            "passed": passed,
            "details": details,
            "score": score
        }

    def _check_catalog(self, mol, catalog) -> List:
        """Check filter catalog."""
        if catalog is None:
            return []
        try:
            return list(catalog.GetMatches(mol))
        except:
            return []

    def save(self, output: str):
        """Save results to file."""
        with open(output, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Results saved to {output}")


def main():
    parser = argparse.ArgumentParser(description="ADMET prediction")
    parser.add_argument("--smiles", help="SMILES string")
    parser.add_argument("--name", help="Compound name")
    parser.add_argument("--library", help="Compound library file (SDF/SMI)")
    parser.add_argument("--properties", help="Specific properties (comma-separated)")
    parser.add_argument("--filter", help="Filter by rules (comma-separated)")
    parser.add_argument("--input", help="Input file for filtering")
    parser.add_argument("--full", action="store_true", help="Full ADMET profile")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "summary", "csv"],
                        default="summary", help="Output format")

    args = parser.parse_args()

    predictor = ADMETPredictor()

    if args.smiles:
        # Single compound
        profile = predictor.predict_full(args.smiles, args.name)

        if args.format == "summary":
            print_admet_summary(profile)
        else:
            predictor.results["profile"] = profile
            output = args.output or "admet_profile.json"
            predictor.save(output)

    elif args.library:
        # Batch prediction
        properties = args.properties.split(",") if args.properties else None
        results = predictor.predict_batch(args.library, properties)

        if args.format == "summary":
            for result in results[:5]:
                print_admet_summary(result)
        else:
            output = args.output or "admet_batch.json"
            predictor.save(output)

    elif args.filter and args.input:
        # Filter mode
        rules = args.filter.split(",")
        results = predictor.filter_compounds(args.input, rules)

        passed = [r for r in results if r["passed"]]
        print(f"\nPassed: {len(passed)}/{len(results)}")

        if args.format == "summary":
            for result in passed[:10]:
                print(f"  {result['name']}: {result['score']} rules passed")
        else:
            predictor.results["filtered"] = results
            output = args.output or "filtered.json"
            predictor.save(output)
    else:
        parser.print_help()


def print_admet_summary(profile: Dict):
    """Print ADMET profile summary."""
    if "error" in profile:
        print(f"Error: {profile['error']}")
        return

    print("\n" + "="*60)
    print(f"ADMET PROFILE: {profile.get('name', 'Unknown')}")
    print("="*60 + "\n")

    # Drug-likeness
    dl = profile.get("drug_likeness", {})
    print("**Drug-Likeness**")
    print(f"  MW: {dl.get('mw', 'N/A')} Da")
    print(f"  LogP: {dl.get('logp', 'N/A')}")
    print(f"  HBD: {dl.get('hbd', 'N/A')}, HBA: {dl.get('hba', 'N/A')}")
    print(f"  PSA: {dl.get('psa', 'N/A')} Ų")
    print(f"  RotB: {dl.get('rotb', 'N/A')}")
    print(f"  Ro5 violations: {dl.get('ro5_violations', 'N/A')}")
    print(f"  Status: {dl.get('drug_likeness', 'N/A')}")

    # Absorption
    abs_prop = profile.get("absorption", {})
    print(f"\n**Absorption**")
    print(f"  HIA: {abs_prop.get('hia', 'N/A')}")
    print(f"  Caco-2: {abs_prop.get('caco2', 'N/A')}")
    print(f"  Pgp substrate: {abs_prop.get('pgp_substrate', 'N/A')}")
    print(f"  Bioavailability: {abs_prop.get('bioavailability', 'N/A')}")

    # Toxicity
    tox = profile.get("toxicity", {})
    print(f"\n**Toxicity**")
    print(f"  hERG: {tox.get('herg_inhibition', 'N/A')}")
    print(f"  DILI: {tox.get('dili', 'N/A')}")
    print(f"  Ames: {tox.get('ames', 'N/A')}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
