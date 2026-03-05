#!/usr/bin/env python3
"""
Genetically-Informed Supplement Protocol Generator
Suggests supplements based on genetic markers.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.

⚠️  IMPORTANT DISCLAIMERS:
- This is NOT medical advice
- Consult a healthcare provider before starting any supplements
- Supplements can interact with medications
- Individual needs vary regardless of genetics
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# SUPPLEMENT RECOMMENDATIONS BY GENETIC MARKER
# Evidence-based suggestions with citations
# =============================================================================

SUPPLEMENT_PROTOCOLS = {
    # Methylation Support
    "rs1801133": {
        "gene": "MTHFR",
        "name": "C677T",
        "risk_allele": "A",
        "risk_genotypes": ["AA", "AG", "GA"],
        "supplement": {
            "name": "Methylfolate (5-MTHF)",
            "dose_heterozygous": "400-800 mcg/day",
            "dose_homozygous": "800-1500 mcg/day",
            "rationale": "MTHFR variants reduce folate conversion to active form",
            "evidence": "Strong - well-established biochemistry",
            "references": ["PMID:26647857", "PMID:23609091"],
            "cautions": [
                "Start low, increase gradually",
                "May cause anxiety in some people",
                "Monitor homocysteine levels"
            ],
            "synergistic": ["B12 (methylcobalamin)", "B6 (P5P)"]
        }
    },
    
    "rs1801131": {
        "gene": "MTHFR", 
        "name": "A1298C",
        "risk_allele": "G",
        "risk_genotypes": ["GG", "AG", "GA"],
        "supplement": {
            "name": "Methylfolate + BH4 support",
            "dose": "400-800 mcg methylfolate",
            "rationale": "A1298C affects BH4 recycling, impacting neurotransmitters",
            "evidence": "Moderate",
            "references": ["PMID:26647857"],
            "cautions": ["Effects less severe than C677T"],
            "synergistic": ["Methylfolate", "SAMe (with caution)"]
        }
    },
    
    "rs1805087": {
        "gene": "MTR",
        "name": "A2756G",
        "risk_allele": "G",
        "risk_genotypes": ["GG", "AG", "GA"],
        "supplement": {
            "name": "Methylcobalamin (B12)",
            "dose": "1000-2000 mcg/day",
            "rationale": "MTR variants affect B12-dependent methylation",
            "evidence": "Moderate",
            "references": ["PMID:21114891"],
            "cautions": ["Check B12 levels first"],
            "synergistic": ["Methylfolate"]
        }
    },
    
    # Vitamin D Metabolism
    "rs2282679": {
        "gene": "GC/DBP",
        "name": "Vitamin D binding protein",
        "risk_allele": "G",
        "risk_genotypes": ["GG", "AG", "GA"],
        "supplement": {
            "name": "Vitamin D3",
            "dose": "2000-5000 IU/day (test levels first)",
            "rationale": "GC variants affect vitamin D transport and bioavailability",
            "evidence": "Strong",
            "references": ["PMID:20541252", "PMID:27537608"],
            "cautions": [
                "Test 25(OH)D levels before supplementing",
                "Take with K2 for calcium metabolism",
                "Take with fat for absorption"
            ],
            "synergistic": ["Vitamin K2 (MK-7)"]
        }
    },
    
    # Oxidative Stress
    "rs4880": {
        "gene": "SOD2",
        "name": "Ala16Val",
        "risk_allele": "A",
        "risk_genotypes": ["AA"],
        "supplement": {
            "name": "Antioxidant support",
            "components": ["NAC 600-1200mg", "CoQ10 100-200mg", "Alpha-lipoic acid 300-600mg"],
            "rationale": "SOD2 AA genotype associated with reduced antioxidant capacity",
            "evidence": "Moderate",
            "references": ["PMID:20102930"],
            "cautions": ["NAC may interact with nitroglycerin"],
            "synergistic": ["Vitamin C", "Vitamin E (mixed tocopherols)"]
        }
    },
    
    # Cardiovascular
    "rs1333049": {
        "gene": "9p21",
        "name": "CAD risk variant",
        "risk_allele": "C",
        "risk_genotypes": ["CC", "CG", "GC"],
        "supplement": {
            "name": "Omega-3 fatty acids",
            "dose": "2-3g EPA/DHA combined daily",
            "rationale": "Cardiovascular risk variants may benefit from omega-3s",
            "evidence": "Strong for cardiovascular support",
            "references": ["PMID:12114036", "PMID:28062407"],
            "cautions": [
                "May increase bleeding risk",
                "Consult doctor if on blood thinners"
            ],
            "synergistic": ["CoQ10"]
        }
    },
    
    # Eye Health
    "rs1061170": {
        "gene": "CFH",
        "name": "Y402H",
        "risk_allele": "C",
        "risk_genotypes": ["CC", "CT", "TC"],
        "supplement": {
            "name": "AREDS2 formula / Lutein & Zeaxanthin",
            "dose": "10-20mg lutein, 2mg zeaxanthin",
            "rationale": "CFH variants increase macular degeneration risk",
            "evidence": "Strong (AREDS2 trial)",
            "references": ["PMID:23644932"],
            "cautions": ["Don't use beta-carotene if smoker"],
            "synergistic": ["Omega-3s", "Vitamin C & E", "Zinc"]
        }
    },
    
    # Neurotransmitter Support
    "rs4680": {
        "gene": "COMT",
        "name": "Val158Met",
        "risk_allele": "A",
        "risk_genotypes": ["AA"],  # Met/Met - slow COMT
        "supplement": {
            "name": "Magnesium (for stress support)",
            "dose": "300-400mg magnesium glycinate",
            "rationale": "Slow COMT may benefit from magnesium for stress response",
            "evidence": "Moderate",
            "references": ["PMID:28445426"],
            "cautions": ["Start low to assess tolerance"],
            "note": "GG (Val/Val) = 'Warrior' - handles stress well but needs more dopamine support"
        }
    },
    
    # Iron Metabolism
    "rs1800562": {
        "gene": "HFE",
        "name": "C282Y",
        "risk_allele": "A",
        "risk_genotypes": ["AA", "AG", "GA"],
        "supplement": {
            "name": "AVOID iron supplements",
            "dose": "Do not supplement iron",
            "rationale": "HFE variants increase iron absorption - risk of overload",
            "evidence": "Strong",
            "references": ["PMID:11073787"],
            "cautions": [
                "Monitor ferritin levels regularly",
                "Avoid vitamin C with iron-rich meals",
                "May need periodic blood donation"
            ],
            "action": "avoid"
        }
    },
}


def load_dna_file(filepath):
    """Load DNA data."""
    import pandas as pd
    
    df = pd.read_csv(filepath, sep='\t', comment='#', dtype=str, low_memory=False)
    
    if 'rsid' in df.columns:
        df['genotype'] = df['allele1'].fillna('') + df['allele2'].fillna('')
        df = df.set_index('rsid')
    elif 'rsID' in df.columns:
        df['genotype'] = df['allele1'].fillna('') + df['allele2'].fillna('')
        df = df.rename(columns={'rsID': 'rsid'}).set_index('rsid')
    else:
        df.columns = ['rsid', 'chromosome', 'position', 'genotype'] + list(df.columns[4:])
        df = df.set_index('rsid')
    
    return df


def get_genotype(df, rsid):
    try:
        return df.loc[rsid, 'genotype']
    except:
        return None


def analyze_supplements(df):
    """Analyze genetic markers and generate supplement recommendations."""
    recommendations = []
    avoid_list = []
    
    for rsid, info in SUPPLEMENT_PROTOCOLS.items():
        geno = get_genotype(df, rsid)
        if geno:
            # Check if genotype matches risk
            is_risk = geno in info["risk_genotypes"] or any(
                info["risk_allele"] in geno for _ in [1]
            )
            
            if is_risk:
                rec = {
                    "rsid": rsid,
                    "gene": info["gene"],
                    "variant": info["name"],
                    "genotype": geno,
                    "supplement": info["supplement"]
                }
                
                if info["supplement"].get("action") == "avoid":
                    avoid_list.append(rec)
                else:
                    recommendations.append(rec)
    
    return {"take": recommendations, "avoid": avoid_list}


def generate_report(results):
    """Generate human-readable supplement protocol."""
    lines = []
    lines.append("=" * 70)
    lines.append("GENETICALLY-INFORMED SUPPLEMENT PROTOCOL")
    lines.append("=" * 70)
    lines.append("")
    lines.append("╔══════════════════════════════════════════════════════════════════╗")
    lines.append("║  ⚠️  IMPORTANT: This is NOT medical advice.                      ║")
    lines.append("║  • Consult a healthcare provider before starting supplements     ║")
    lines.append("║  • Supplements can interact with medications                     ║")
    lines.append("║  • Get baseline lab tests (B12, folate, D, ferritin, etc.)      ║")
    lines.append("║  • Individual needs vary regardless of genetics                  ║")
    lines.append("╚══════════════════════════════════════════════════════════════════╝")
    lines.append("")
    
    # Things to AVOID first
    if results["avoid"]:
        lines.append("-" * 70)
        lines.append("🚫 SUPPLEMENTS TO AVOID")
        lines.append("-" * 70)
        for rec in results["avoid"]:
            supp = rec["supplement"]
            lines.append(f"\n  {supp['name']}")
            lines.append(f"  Gene: {rec['gene']} {rec['variant']} | Genotype: {rec['genotype']}")
            lines.append(f"  Reason: {supp['rationale']}")
            if supp.get('cautions'):
                for c in supp['cautions']:
                    lines.append(f"    ⚠️  {c}")
        lines.append("")
    
    # Recommendations
    if results["take"]:
        lines.append("-" * 70)
        lines.append("✓ RECOMMENDED SUPPLEMENTS")
        lines.append("-" * 70)
        
        for rec in results["take"]:
            supp = rec["supplement"]
            lines.append("")
            lines.append(f"  📋 {supp['name']}")
            lines.append(f"  ─────────────────────────────────────")
            lines.append(f"  Gene: {rec['gene']} {rec['variant']}")
            lines.append(f"  Your genotype: {rec['genotype']}")
            
            if supp.get('dose'):
                lines.append(f"  Suggested dose: {supp['dose']}")
            if supp.get('dose_heterozygous') and rec['genotype'].count(rec.get('risk_allele', 'X')) == 1:
                lines.append(f"  Suggested dose (heterozygous): {supp['dose_heterozygous']}")
            if supp.get('dose_homozygous') and rec['genotype'].count(rec.get('risk_allele', 'X')) == 2:
                lines.append(f"  Suggested dose (homozygous): {supp['dose_homozygous']}")
            if supp.get('components'):
                lines.append(f"  Components: {', '.join(supp['components'])}")
            
            lines.append(f"  Rationale: {supp['rationale']}")
            lines.append(f"  Evidence level: {supp['evidence']}")
            
            if supp.get('cautions'):
                lines.append("  Cautions:")
                for c in supp['cautions']:
                    lines.append(f"    ⚠️  {c}")
            
            if supp.get('synergistic'):
                lines.append(f"  Works well with: {', '.join(supp['synergistic'])}")
            
            if supp.get('references'):
                lines.append(f"  References: {', '.join(supp['references'])}")
    else:
        lines.append("")
        lines.append("  No specific supplement recommendations based on analyzed markers.")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("GENERAL NOTES")
    lines.append("-" * 70)
    lines.append("""
• Always start with low doses and increase gradually
• Take supplements with food unless otherwise indicated
• Space out supplements that compete for absorption
• Keep a log of what you take and how you feel
• Re-test relevant biomarkers after 3-6 months
• Quality matters - choose reputable manufacturers
• More is not always better - follow dosing guidelines
""")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python supplement_protocol.py <dna_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Analyzing supplement-relevant markers...")
    results = analyze_supplements(df)
    
    # Save JSON
    with open(OUTPUT_DIR / "supplement_protocol.json", 'w') as f:
        # Convert to serializable format
        json_results = {
            "take": [{k: v for k, v in r.items()} for r in results["take"]],
            "avoid": [{k: v for k, v in r.items()} for r in results["avoid"]]
        }
        json.dump(json_results, f, indent=2, default=str)
    
    # Generate report
    report = generate_report(results)
    
    with open(OUTPUT_DIR / "supplement_protocol.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
