#!/usr/bin/env python3
"""
Ancestry and Ethnicity Analysis
Analyzes population-specific markers across ALL major ethnic groups.
Works with any ancestry background.

Privacy: All analysis runs locally. No network requests.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# POPULATION-SPECIFIC MARKERS - Global coverage
# =============================================================================

ANCESTRY_MARKERS = {
    # EUROPEAN MARKERS
    "european": {
        "rs16891982": {"name": "SLC45A2", "allele": "G", "desc": "Light skin pigmentation (European)"},
        "rs1426654": {"name": "SLC24A5", "allele": "A", "desc": "Light skin (European/Middle Eastern)"},
        "rs12913832": {"name": "HERC2", "allele": "G", "desc": "Blue eyes (Northern European)"},
        "rs4988235": {"name": "LCT", "allele": "A", "desc": "Lactase persistence (European)"},
    },
    
    # NORTHERN/WESTERN EUROPEAN
    "northern_european": {
        "rs1805007": {"name": "MC1R R151C", "allele": "T", "desc": "Red hair variant (Celtic/Nordic)"},
        "rs1805008": {"name": "MC1R R160W", "allele": "T", "desc": "Red hair variant"},
        "rs1805009": {"name": "MC1R D294H", "allele": "C", "desc": "Red hair variant"},
        "rs12203592": {"name": "IRF4", "allele": "T", "desc": "Freckling (high in Irish/British)"},
        "rs4778138": {"name": "OCA2", "allele": "A", "desc": "Light eyes (Northern European)"},
    },
    
    # SOUTHERN EUROPEAN / MEDITERRANEAN
    "mediterranean": {
        "rs1800407": {"name": "OCA2 R419Q", "allele": "T", "desc": "Blue/green eyes in darker populations"},
        "rs28777": {"name": "SLC45A2", "allele": "A", "desc": "Mediterranean pigmentation variant"},
    },
    
    # ASHKENAZI JEWISH
    "ashkenazi": {
        "rs1801133": {"name": "MTHFR C677T", "allele": "A", "desc": "Higher frequency in Ashkenazi (~30-40%)"},
        # Note: Disease carrier variants (Gaucher, Tay-Sachs) require clinical testing
    },
    
    # EAST ASIAN
    "east_asian": {
        "rs3827760": {"name": "EDAR V370A", "allele": "A", "desc": "Thick hair, shovel-shaped incisors (East Asian)"},
        "rs671": {"name": "ALDH2", "allele": "A", "desc": "Alcohol flush reaction (East Asian)"},
        "rs1229984": {"name": "ADH1B", "allele": "T", "desc": "Alcohol metabolism (East Asian)"},
        "rs17822931": {"name": "ABCC11", "allele": "T", "desc": "Dry earwax (East Asian)"},
    },
    
    # SOUTH ASIAN
    "south_asian": {
        "rs2470102": {"name": "SLC24A5", "allele": "G", "desc": "Skin pigmentation variant"},
        "rs1426654": {"name": "SLC24A5", "allele": "G", "desc": "South Asian pigmentation pattern"},
    },
    
    # AFRICAN
    "african": {
        "rs2814778": {"name": "DARC/Duffy", "allele": "C", "desc": "Duffy null (malaria resistance, African)"},
        "rs8176719": {"name": "ABO", "allele": "delG", "desc": "O blood type (higher in some African pops)"},
        "rs1426654": {"name": "SLC24A5", "allele": "G", "desc": "Ancestral skin pigmentation"},
        "rs16891982": {"name": "SLC45A2", "allele": "C", "desc": "Ancestral skin pigmentation"},
    },
    
    # NATIVE AMERICAN
    "native_american": {
        "rs3827760": {"name": "EDAR V370A", "allele": "A", "desc": "Shared with East Asian ancestry"},
        "rs17822931": {"name": "ABCC11", "allele": "T", "desc": "Dry earwax (Native American)"},
    },
    
    # MIDDLE EASTERN / NORTH AFRICAN
    "middle_eastern": {
        "rs1426654": {"name": "SLC24A5", "allele": "A", "desc": "Light skin variant"},
        "rs12913832": {"name": "HERC2", "allele": "A", "desc": "Brown eyes (ancestral)"},
    },
    
    # OCEANIAN / PACIFIC ISLANDER
    "oceanian": {
        "rs2814778": {"name": "DARC", "allele": "T", "desc": "Duffy positive (Oceanian pattern)"},
    },
}

# Y-DNA Haplogroup markers (simplified - full analysis requires more markers)
Y_HAPLOGROUP_MARKERS = {
    "rs9786184": {"haplogroup": "R1b", "allele": "A", "desc": "R1b indicator (Western European)"},
    "rs17250804": {"haplogroup": "R1a", "allele": "G", "desc": "R1a indicator (Eastern European/South Asian)"},
    "rs2032652": {"haplogroup": "I", "allele": "G", "desc": "Haplogroup I indicator (Nordic/Balkan)"},
    "rs9341296": {"haplogroup": "E", "allele": "C", "desc": "Haplogroup E indicator (African/Mediterranean)"},
    "rs2032631": {"haplogroup": "J", "allele": "A", "desc": "Haplogroup J indicator (Middle Eastern)"},
    "rs3908": {"haplogroup": "O", "allele": "T", "desc": "Haplogroup O indicator (East Asian)"},
    "rs17316625": {"haplogroup": "Q", "allele": "C", "desc": "Haplogroup Q indicator (Native American/Siberian)"},
    "rs9341301": {"haplogroup": "N", "allele": "A", "desc": "Haplogroup N indicator (Uralic/Siberian)"},
}

# mtDNA Haplogroup markers (simplified)
MT_HAPLOGROUP_MARKERS = {
    "rs2853499": {"haplogroup": "H", "allele": "G", "desc": "Haplogroup H indicator (European)"},
    "rs28358571": {"haplogroup": "U", "allele": "A", "desc": "Haplogroup U indicator (European/Middle Eastern)"},
    "rs3928306": {"haplogroup": "L", "allele": "A", "desc": "Haplogroup L indicator (African)"},
    "rs2853515": {"haplogroup": "A", "allele": "G", "desc": "Haplogroup A indicator (Asian/Native American)"},
    "rs2853508": {"haplogroup": "B", "allele": "A", "desc": "Haplogroup B indicator (Asian/Polynesian)"},
    "rs2853510": {"haplogroup": "C", "allele": "T", "desc": "Haplogroup C indicator (Asian/Native American)"},
    "rs2853511": {"haplogroup": "D", "allele": "C", "desc": "Haplogroup D indicator (Asian/Native American)"},
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
        df = df.rename(columns={df.columns[0]: 'rsid'})
        if 'genotype' not in df.columns:
            df['genotype'] = df.iloc[:, 3] if df.shape[1] > 3 else ''
        df = df.set_index('rsid')
    
    return df


def get_genotype(df, rsid):
    try:
        return df.loc[rsid, 'genotype']
    except:
        return None


def analyze_population_markers(df):
    """Analyze markers for each population group."""
    results = {}
    
    for population, markers in ANCESTRY_MARKERS.items():
        pop_results = {"score": 0, "total": 0, "markers": []}
        
        for rsid, info in markers.items():
            geno = get_genotype(df, rsid)
            if geno:
                allele_count = geno.count(info['allele'])
                pop_results['total'] += 2
                pop_results['score'] += allele_count
                pop_results['markers'].append({
                    'rsid': rsid,
                    'name': info['name'],
                    'genotype': geno,
                    'target_allele': info['allele'],
                    'count': allele_count,
                    'description': info['desc']
                })
        
        if pop_results['total'] > 0:
            pop_results['percentage'] = round(100 * pop_results['score'] / pop_results['total'], 1)
        else:
            pop_results['percentage'] = 0
        
        results[population] = pop_results
    
    return results


def analyze_haplogroups(df):
    """Analyze Y-DNA and mtDNA haplogroup indicators."""
    y_results = []
    mt_results = []
    
    for rsid, info in Y_HAPLOGROUP_MARKERS.items():
        geno = get_genotype(df, rsid)
        if geno and info['allele'] in geno:
            y_results.append({
                'haplogroup': info['haplogroup'],
                'rsid': rsid,
                'genotype': geno,
                'description': info['desc']
            })
    
    for rsid, info in MT_HAPLOGROUP_MARKERS.items():
        geno = get_genotype(df, rsid)
        if geno and info['allele'] in geno:
            mt_results.append({
                'haplogroup': info['haplogroup'],
                'rsid': rsid,
                'genotype': geno,
                'description': info['desc']
            })
    
    return {'y_dna': y_results, 'mt_dna': mt_results}


def generate_report(pop_results, haplogroups):
    """Generate human-readable ancestry report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ANCESTRY & ETHNICITY ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    lines.append("⚠️  Note: This analysis uses a limited set of ancestry-informative")
    lines.append("    markers. For comprehensive ancestry analysis, use services like")
    lines.append("    23andMe, AncestryDNA, or professional genetic genealogy tools.")
    lines.append("")
    
    # Population affinities
    lines.append("-" * 70)
    lines.append("POPULATION MARKER AFFINITIES")
    lines.append("-" * 70)
    lines.append("")
    
    # Sort by percentage
    sorted_pops = sorted(pop_results.items(), key=lambda x: x[1]['percentage'], reverse=True)
    
    for pop, data in sorted_pops:
        if data['total'] > 0:
            bar_len = int(data['percentage'] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {pop.replace('_', ' ').title():25} {bar} {data['percentage']:5.1f}%")
    
    lines.append("")
    lines.append("  (Higher % = more markers matching that population's typical pattern)")
    lines.append("")
    
    # Haplogroups
    lines.append("-" * 70)
    lines.append("HAPLOGROUP INDICATORS")
    lines.append("-" * 70)
    lines.append("")
    
    if haplogroups['y_dna']:
        lines.append("  Y-DNA (paternal line):")
        for h in haplogroups['y_dna']:
            lines.append(f"    → {h['haplogroup']}: {h['description']}")
    else:
        lines.append("  Y-DNA: No clear indicators found (may need more markers)")
    
    lines.append("")
    
    if haplogroups['mt_dna']:
        lines.append("  mtDNA (maternal line):")
        for h in haplogroups['mt_dna']:
            lines.append(f"    → {h['haplogroup']}: {h['description']}")
    else:
        lines.append("  mtDNA: No clear indicators found (may need more markers)")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("DETAILED MARKERS BY POPULATION")
    lines.append("-" * 70)
    
    for pop, data in sorted_pops:
        if data['markers']:
            lines.append(f"\n{pop.replace('_', ' ').upper()}:")
            for m in data['markers']:
                status = "✓" if m['count'] > 0 else "○"
                lines.append(f"  {status} {m['name']} ({m['rsid']}): {m['genotype']} - {m['description']}")
    
    lines.append("")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ethnicity_analysis.py <dna_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Analyzing population markers...")
    pop_results = analyze_population_markers(df)
    
    print("Analyzing haplogroups...")
    haplogroups = analyze_haplogroups(df)
    
    # Save JSON
    results = {
        'population_affinities': pop_results,
        'haplogroups': haplogroups
    }
    
    with open(OUTPUT_DIR / "ancestry_report.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate and print report
    report = generate_report(pop_results, haplogroups)
    
    with open(OUTPUT_DIR / "ancestry_report.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
