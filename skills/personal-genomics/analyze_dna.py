#!/usr/bin/env python3
"""
Personal Genomics Analysis - Core Health, Pharmacogenomics & Traits
Analyzes raw DNA data from consumer genetic testing services.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Output directory
OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# SNP DATABASES - Comprehensive markers for all populations
# =============================================================================

HEALTH_MARKERS = {
    # Cardiovascular
    "rs429358": {"gene": "APOE", "name": "APOE ε4 marker 1", "risk": "C", "category": "alzheimers_cardiovascular", "impact": "high"},
    "rs7412": {"gene": "APOE", "name": "APOE ε4 marker 2", "risk": "C", "category": "alzheimers_cardiovascular", "impact": "high"},
    "rs1333049": {"gene": "9p21", "name": "CAD risk variant", "risk": "C", "category": "cardiovascular", "impact": "moderate"},
    "rs10757274": {"gene": "9p21", "name": "CAD risk variant 2", "risk": "G", "category": "cardiovascular", "impact": "moderate"},
    "rs4420638": {"gene": "APOC1", "name": "Lipid metabolism", "risk": "G", "category": "cardiovascular", "impact": "moderate"},
    "rs6025": {"gene": "F5", "name": "Factor V Leiden", "risk": "A", "category": "clotting", "impact": "high"},
    "rs1799963": {"gene": "F2", "name": "Prothrombin G20210A", "risk": "A", "category": "clotting", "impact": "high"},
    
    # Metabolic
    "rs1801133": {"gene": "MTHFR", "name": "C677T", "risk": "A", "category": "methylation", "impact": "moderate"},
    "rs1801131": {"gene": "MTHFR", "name": "A1298C", "risk": "G", "category": "methylation", "impact": "moderate"},
    "rs1805087": {"gene": "MTR", "name": "A2756G", "risk": "G", "category": "methylation", "impact": "low"},
    "rs1801394": {"gene": "MTRR", "name": "A66G", "risk": "G", "category": "methylation", "impact": "low"},
    "rs1800562": {"gene": "HFE", "name": "C282Y", "risk": "A", "category": "iron_metabolism", "impact": "high"},
    "rs1799945": {"gene": "HFE", "name": "H63D", "risk": "G", "category": "iron_metabolism", "impact": "moderate"},
    "rs7903146": {"gene": "TCF7L2", "name": "Diabetes risk", "risk": "T", "category": "diabetes", "impact": "moderate"},
    
    # Cancer predisposition indicators (NOT diagnostic - common variants only)
    "rs1042522": {"gene": "TP53", "name": "Arg72Pro", "risk": "C", "category": "cancer_related", "impact": "low"},
    "rs2981582": {"gene": "FGFR2", "name": "Breast cancer risk", "risk": "A", "category": "cancer_related", "impact": "low"},
    "rs6983267": {"gene": "8q24", "name": "Colorectal risk", "risk": "G", "category": "cancer_related", "impact": "low"},
    
    # Eye Health
    "rs1061170": {"gene": "CFH", "name": "Macular degeneration", "risk": "C", "category": "eye_health", "impact": "moderate"},
    "rs10490924": {"gene": "ARMS2", "name": "AMD risk", "risk": "T", "category": "eye_health", "impact": "moderate"},
    
    # Autoimmune
    "rs2187668": {"gene": "HLA-DQ2.5", "name": "Celiac risk", "risk": "T", "category": "autoimmune", "impact": "moderate"},
    "rs7454108": {"gene": "HLA-DQ8", "name": "Celiac risk 2", "risk": "C", "category": "autoimmune", "impact": "moderate"},
    
    # Neurological
    "rs9939609": {"gene": "FTO", "name": "Obesity risk", "risk": "A", "category": "metabolic", "impact": "low"},
    "rs4680": {"gene": "COMT", "name": "Val158Met", "risk": "G", "category": "neurological", "impact": "moderate"},
    "rs6265": {"gene": "BDNF", "name": "Val66Met", "risk": "T", "category": "neurological", "impact": "moderate"},
    "rs53576": {"gene": "OXTR", "name": "Oxytocin receptor", "risk": "A", "category": "neurological", "impact": "low"},
    "rs1800497": {"gene": "DRD2", "name": "Taq1A", "risk": "A", "category": "neurological", "impact": "moderate"},
}

PHARMACOGENOMICS = {
    # Warfarin
    "rs9923231": {"gene": "VKORC1", "name": "Warfarin sensitivity", "effect_allele": "T", "effect": "Increased sensitivity - lower dose needed", "drugs": ["warfarin"]},
    "rs1799853": {"gene": "CYP2C9", "name": "*2 variant", "effect_allele": "T", "effect": "Reduced metabolism", "drugs": ["warfarin", "NSAIDs"]},
    "rs1057910": {"gene": "CYP2C9", "name": "*3 variant", "effect_allele": "C", "effect": "Significantly reduced metabolism", "drugs": ["warfarin", "NSAIDs"]},
    
    # Clopidogrel
    "rs4244285": {"gene": "CYP2C19", "name": "*2 variant", "effect_allele": "A", "effect": "Poor metabolizer", "drugs": ["clopidogrel", "PPIs"]},
    "rs4986893": {"gene": "CYP2C19", "name": "*3 variant", "effect_allele": "A", "effect": "Poor metabolizer", "drugs": ["clopidogrel"]},
    "rs12248560": {"gene": "CYP2C19", "name": "*17 variant", "effect_allele": "T", "effect": "Ultra-rapid metabolizer", "drugs": ["clopidogrel"]},
    
    # Statins
    "rs4149056": {"gene": "SLCO1B1", "name": "Statin myopathy risk", "effect_allele": "C", "effect": "Increased myopathy risk", "drugs": ["simvastatin", "atorvastatin"]},
    
    # Opioids
    "rs1799971": {"gene": "OPRM1", "name": "Opioid receptor", "effect_allele": "G", "effect": "Reduced response to opioids", "drugs": ["morphine", "codeine"]},
    
    # Caffeine
    "rs762551": {"gene": "CYP1A2", "name": "Caffeine metabolism", "effect_allele": "C", "effect": "Slow metabolizer", "drugs": ["caffeine"]},
    
    # Codeine
    "rs3892097": {"gene": "CYP2D6", "name": "*4 variant", "effect_allele": "A", "effect": "Poor metabolizer", "drugs": ["codeine", "tramadol", "antidepressants"]},
    
    # Antidepressants
    "rs25531": {"gene": "SLC6A4", "name": "Serotonin transporter", "effect_allele": "G", "effect": "May affect SSRI response", "drugs": ["SSRIs"]},
}

TRAITS = {
    # Eye color
    "rs12913832": {"name": "Eye color (primary)", "trait": "eye_color", "alleles": {"A": "brown tendency", "G": "blue/green tendency"}},
    "rs1800407": {"name": "Eye color (OCA2)", "trait": "eye_color", "alleles": {"T": "blue/green tendency", "C": "brown tendency"}},
    
    # Hair
    "rs1805007": {"name": "MC1R R151C", "trait": "red_hair", "alleles": {"T": "red hair variant"}},
    "rs1805008": {"name": "MC1R R160W", "trait": "red_hair", "alleles": {"T": "red hair variant"}},
    "rs1805009": {"name": "MC1R D294H", "trait": "red_hair", "alleles": {"C": "red hair variant"}},
    "rs12203592": {"name": "IRF4", "trait": "freckling", "alleles": {"T": "increased freckling"}},
    
    # Muscle
    "rs1815739": {"name": "ACTN3 R577X", "trait": "muscle_type", "alleles": {"T": "endurance tendency", "C": "power/sprint tendency"}},
    
    # Taste
    "rs713598": {"name": "TAS2R38", "trait": "bitter_taste", "alleles": {"C": "taster", "G": "non-taster"}},
    "rs1726866": {"name": "TAS2R38 (2)", "trait": "bitter_taste", "alleles": {"T": "taster", "C": "non-taster"}},
    
    # Metabolism
    "rs4988235": {"name": "MCM6/LCT", "trait": "lactose", "alleles": {"A": "lactase persistent", "G": "lactose intolerant tendency"}},
    "rs671": {"name": "ALDH2", "trait": "alcohol_flush", "alleles": {"A": "alcohol flush reaction"}},
    
    # Sleep
    "rs1801260": {"name": "CLOCK", "trait": "chronotype", "alleles": {"C": "evening preference", "T": "morning preference"}},
}

def load_dna_file(filepath):
    """Load DNA data from common formats (23andMe, AncestryDNA, etc.)"""
    import pandas as pd
    
    print(f"Loading DNA data from {filepath}...")
    
    # Try different formats
    try:
        # AncestryDNA format
        df = pd.read_csv(filepath, sep='\t', comment='#', 
                        dtype=str, low_memory=False)
        if 'rsid' in df.columns:
            df['genotype'] = df['allele1'] + df['allele2']
            df = df.set_index('rsid')
        elif 'rsID' in df.columns:
            df = df.rename(columns={'rsID': 'rsid'})
            df['genotype'] = df['allele1'] + df['allele2']
            df = df.set_index('rsid')
    except:
        try:
            # 23andMe format
            df = pd.read_csv(filepath, sep='\t', comment='#',
                            names=['rsid', 'chromosome', 'position', 'genotype'],
                            dtype=str, low_memory=False)
            df = df.set_index('rsid')
        except:
            raise ValueError(f"Unable to parse DNA file format: {filepath}")
    
    print(f"Loaded {len(df):,} SNPs")
    return df

def get_genotype(df, rsid):
    """Get genotype for a SNP, handling missing data."""
    try:
        return df.loc[rsid, 'genotype']
    except:
        return None

def analyze_health(df):
    """Analyze health markers."""
    results = defaultdict(dict)
    
    for rsid, info in HEALTH_MARKERS.items():
        geno = get_genotype(df, rsid)
        if geno:
            risk_count = geno.count(info['risk'])
            results[info['category']][rsid] = {
                'gene': info['gene'],
                'name': info['name'],
                'genotype': geno,
                'risk_allele': info['risk'],
                'risk_alleles_present': risk_count,
                'impact': info['impact'],
                'status': 'homozygous_risk' if risk_count == 2 else 'heterozygous' if risk_count == 1 else 'normal'
            }
    
    return dict(results)

def analyze_pharmacogenomics(df):
    """Analyze pharmacogenomic markers."""
    results = {}
    
    for rsid, info in PHARMACOGENOMICS.items():
        geno = get_genotype(df, rsid)
        if geno:
            effect_count = geno.count(info['effect_allele'])
            results[rsid] = {
                'gene': info['gene'],
                'name': info['name'],
                'genotype': geno,
                'effect_allele': info['effect_allele'],
                'effect_alleles_present': effect_count,
                'effect': info['effect'] if effect_count > 0 else 'Normal metabolism',
                'affected_drugs': info['drugs'],
                'actionable': effect_count > 0
            }
    
    return results

def analyze_traits(df):
    """Analyze trait markers."""
    results = {}
    
    for rsid, info in TRAITS.items():
        geno = get_genotype(df, rsid)
        if geno:
            interpretations = []
            for allele, meaning in info['alleles'].items():
                if allele in geno:
                    interpretations.append(meaning)
            
            results[rsid] = {
                'name': info['name'],
                'trait': info['trait'],
                'genotype': geno,
                'interpretation': interpretations
            }
    
    return results

def determine_apoe_status(health_results):
    """Determine APOE genotype (ε2/ε3/ε4)."""
    apoe_cat = health_results.get('alzheimers_cardiovascular', {})
    rs429358 = apoe_cat.get('rs429358', {}).get('genotype', '')
    rs7412 = apoe_cat.get('rs7412', {}).get('genotype', '')
    
    if not rs429358 or not rs7412:
        return "Unable to determine"
    
    # Determine haplotypes
    # ε2 = T-T (rs429358-rs7412)
    # ε3 = T-C
    # ε4 = C-C
    
    c_429 = rs429358.count('C')
    t_7412 = rs7412.count('T')
    
    if c_429 == 0 and t_7412 == 2:
        return "ε2/ε2"
    elif c_429 == 0 and t_7412 == 1:
        return "ε2/ε3"
    elif c_429 == 0 and t_7412 == 0:
        return "ε3/ε3"
    elif c_429 == 1 and t_7412 == 1:
        return "ε2/ε4"
    elif c_429 == 1 and t_7412 == 0:
        return "ε3/ε4"
    elif c_429 == 2 and t_7412 == 0:
        return "ε4/ε4"
    else:
        return f"Complex ({rs429358}/{rs7412})"

def generate_report(health, pharma, traits, apoe_status):
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PERSONAL GENOMICS ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("⚠️  DISCLAIMER: This is NOT medical advice. Consult healthcare")
    lines.append("    professionals before making any health decisions.")
    lines.append("")
    
    # APOE
    lines.append("-" * 70)
    lines.append("APOE STATUS")
    lines.append("-" * 70)
    lines.append(f"APOE Genotype: {apoe_status}")
    if "ε4" in apoe_status:
        lines.append("  → ε4 allele present - discuss with physician")
    lines.append("")
    
    # Health by category
    lines.append("-" * 70)
    lines.append("HEALTH MARKERS BY CATEGORY")
    lines.append("-" * 70)
    
    for category, markers in health.items():
        lines.append(f"\n{category.upper().replace('_', ' ')}:")
        for rsid, data in markers.items():
            status_icon = "⚠️" if data['status'] != 'normal' else "✓"
            lines.append(f"  {status_icon} {data['gene']} {data['name']}: {data['genotype']} ({data['status']})")
    
    # Pharmacogenomics
    lines.append("")
    lines.append("-" * 70)
    lines.append("PHARMACOGENOMICS")
    lines.append("-" * 70)
    
    actionable = [r for r in pharma.values() if r['actionable']]
    if actionable:
        for r in actionable:
            lines.append(f"  ⚠️ {r['gene']} {r['name']}: {r['genotype']}")
            lines.append(f"     Effect: {r['effect']}")
            lines.append(f"     Drugs: {', '.join(r['affected_drugs'])}")
    else:
        lines.append("  No actionable pharmacogenomic variants detected.")
    
    # Traits
    lines.append("")
    lines.append("-" * 70)
    lines.append("TRAITS")
    lines.append("-" * 70)
    
    trait_groups = defaultdict(list)
    for data in traits.values():
        if data['interpretation']:
            trait_groups[data['trait']].extend(data['interpretation'])
    
    for trait, interps in trait_groups.items():
        lines.append(f"  {trait.replace('_', ' ').title()}: {', '.join(set(interps))}")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_dna.py <path_to_dna_file>")
        print("Supports: AncestryDNA, 23andMe, MyHeritage, FamilyTreeDNA, LivingDNA")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Load data
    df = load_dna_file(filepath)
    
    # Analyze
    print("Analyzing health markers...")
    health = analyze_health(df)
    
    print("Analyzing pharmacogenomics...")
    pharma = analyze_pharmacogenomics(df)
    
    print("Analyzing traits...")
    traits = analyze_traits(df)
    
    # APOE status
    apoe_status = determine_apoe_status(health)
    
    # Generate reports
    print(f"\nSaving reports to {OUTPUT_DIR}/")
    
    with open(OUTPUT_DIR / "health_report.json", 'w') as f:
        json.dump({'apoe_status': apoe_status, 'markers': health}, f, indent=2)
    
    with open(OUTPUT_DIR / "pharma_report.json", 'w') as f:
        json.dump(pharma, f, indent=2)
    
    with open(OUTPUT_DIR / "traits_report.json", 'w') as f:
        json.dump(traits, f, indent=2)
    
    report = generate_report(health, pharma, traits, apoe_status)
    with open(OUTPUT_DIR / "full_report.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
