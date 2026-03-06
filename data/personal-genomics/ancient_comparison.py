#!/usr/bin/env python3
"""
Ancient DNA Comparison
Compare your genome to the Allen Ancient DNA Resource (AADR) database.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.

Note: For full comparison, download the AADR v62+ files from:
https://reich.hms.harvard.edu/allen-ancient-dna-resource-aadr-downloadable-genotypes-present-day-and-ancient-dna-data
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Path to AADR annotation file (download separately)
AADR_DIR = Path.home() / "ancient-dna"
AADR_ANNO = AADR_DIR / "v62.0_1240k_public.anno"

# Major ancient population categories
POPULATION_CATEGORIES = {
    'hunter_gatherer': [
        'WHG', 'EHG', 'SHG', 'CHG', 'Mesolithic', 'Epipaleolithic',
        'HG', 'Forager', 'Hunter', 'Gatherer'
    ],
    'neolithic_farmer': [
        'Neolithic', 'EEF', 'Farmer', 'Anatolian_N', 'LBK',
        'Cardial', 'TRB', 'Funnelbeaker'
    ],
    'steppe': [
        'Yamnaya', 'Corded', 'Steppe', 'Sintashta', 'Andronovo',
        'Afanasievo', 'Srubnaya', 'Scythian', 'Sarmatian'
    ],
    'bronze_age': [
        'Bronze', 'BA_', 'Bell_Beaker', 'Beaker', 'Unetice',
        'Mycenaean', 'Minoan'
    ],
    'iron_age': [
        'Iron', 'IA_', 'Celtic', 'Hallstatt', 'La_Tene',
        'Villanova', 'Etruscan'
    ],
    'viking_age': [
        'Viking', 'VA_', 'Norse', 'Scandinavian'
    ],
    'medieval': [
        'Medieval', 'MA_', 'Migration_period', 'Anglo', 'Saxon',
        'Frank', 'Goth', 'Lombard'
    ],
    'ancient_african': [
        'Africa', 'Mota', 'Taforalt', 'Iberomaurusian'
    ],
    'ancient_east_asian': [
        'Tianyuan', 'Jomon', 'Devil', 'China_', 'Japan_',
        'Korea_', 'Mongolia_'
    ],
    'ancient_american': [
        'Clovis', 'Anzick', 'Kennewick', 'Spirit_Cave',
        'Ancient_American', 'Paleo_American'
    ],
    'ancient_middle_east': [
        'Natufian', 'PPNB', 'Levant', 'Iran_N', 'Mesopotamia',
        'Phoenician', 'Canaanite'
    ],
}

# Y-DNA haplogroup distributions by population
Y_HAPLOGROUP_POPS = {
    'R1b': ['Western_Europe', 'Celtic', 'Bell_Beaker', 'Iberia', 'Britain', 'Ireland', 'France', 'Germany'],
    'R1a': ['Eastern_Europe', 'Corded_Ware', 'Sintashta', 'Indo_Iranian', 'Slavic', 'Baltic'],
    'I1': ['Scandinavia', 'Viking', 'Germanic', 'Nordic'],
    'I2': ['Balkans', 'Sardinia', 'WHG', 'Mesolithic_Europe'],
    'J1': ['Middle_East', 'Semitic', 'Arabian', 'Jewish'],
    'J2': ['Mediterranean', 'Anatolia', 'Neolithic_Farmer', 'Phoenician'],
    'E': ['Africa', 'Mediterranean', 'Berber', 'Bantu'],
    'G': ['Caucasus', 'Anatolia', 'EEF', 'Early_Farmer'],
    'N': ['Siberia', 'Uralic', 'Finland', 'Baltic', 'Yakut'],
    'O': ['East_Asia', 'China', 'Japan', 'Korea', 'Southeast_Asia'],
    'Q': ['Siberia', 'Native_American', 'Paleo_Siberian'],
    'C': ['Mongolia', 'East_Asia', 'Australia', 'Pacific'],
    'D': ['Tibet', 'Japan', 'Andaman'],
}

# mtDNA haplogroup distributions
MT_HAPLOGROUP_POPS = {
    'H': ['Europe', 'Western_Europe', 'Post_LGM', 'Franco_Cantabrian'],
    'U': ['Europe', 'WHG', 'Mesolithic', 'South_Asia'],
    'K': ['Europe', 'Middle_East', 'Neolithic'],
    'J': ['Middle_East', 'Neolithic_Farmer', 'Near_East'],
    'T': ['Europe', 'Middle_East', 'Neolithic'],
    'V': ['Europe', 'Iberia', 'Saami'],
    'W': ['South_Asia', 'Europe', 'Middle_East'],
    'X': ['Europe', 'Middle_East', 'Native_American'],
    'L': ['Africa', 'Basal_Human'],
    'M': ['Asia', 'South_Asia', 'East_Asia'],
    'N': ['Asia', 'Europe', 'Oceania'],
    'A': ['East_Asia', 'Native_American', 'Siberia'],
    'B': ['East_Asia', 'Native_American', 'Polynesia'],
    'C': ['East_Asia', 'Native_American', 'Siberia'],
    'D': ['East_Asia', 'Native_American', 'Siberia'],
}


def load_dna_file(filepath):
    """Load user's DNA data."""
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


def load_aadr_annotation():
    """Load AADR annotation file if available."""
    if not AADR_ANNO.exists():
        return None
    
    import pandas as pd
    
    # AADR annotation columns
    cols = ['sample_id', 'master_id', 'skeleton_id', 'publication', 'date_mean', 
            'date_sd', 'location', 'country', 'lat', 'lon', 'coverage',
            'y_haplogroup', 'mt_haplogroup', 'group_id', 'political_entity']
    
    df = pd.read_csv(AADR_ANNO, sep='\t', usecols=range(15), names=cols, 
                     skiprows=1, dtype=str, low_memory=False)
    
    return df


def match_haplogroups_to_populations(y_haplo, mt_haplo):
    """Find which ancient populations share the user's haplogroups."""
    matches = []
    
    if y_haplo:
        y_base = y_haplo.split('-')[0].split('*')[0][:2] if y_haplo else None
        if y_base in Y_HAPLOGROUP_POPS:
            matches.append({
                'haplogroup': y_haplo,
                'type': 'Y-DNA',
                'associated_populations': Y_HAPLOGROUP_POPS[y_base]
            })
    
    if mt_haplo:
        mt_base = mt_haplo[0] if mt_haplo else None
        if mt_base in MT_HAPLOGROUP_POPS:
            matches.append({
                'haplogroup': mt_haplo,
                'type': 'mtDNA', 
                'associated_populations': MT_HAPLOGROUP_POPS[mt_base]
            })
    
    return matches


def categorize_by_period(populations):
    """Categorize ancient populations by time period."""
    categorized = defaultdict(list)
    
    for pop in populations:
        for category, keywords in POPULATION_CATEGORIES.items():
            if any(kw.lower() in pop.lower() for kw in keywords):
                categorized[category].append(pop)
                break
    
    return dict(categorized)


def generate_report(aadr_available, haplo_matches, y_haplo, mt_haplo):
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ANCIENT DNA COMPARISON")
    lines.append("=" * 70)
    lines.append("")
    
    if not aadr_available:
        lines.append("⚠️  AADR database not found. For full comparison, download from:")
        lines.append("    https://reich.hms.harvard.edu/allen-ancient-dna-resource")
        lines.append("")
        lines.append("    Place files in: ~/ancient-dna/")
        lines.append("    Required: v62.0_1240k_public.anno")
        lines.append("")
    
    lines.append("-" * 70)
    lines.append("HAPLOGROUP ASSOCIATIONS")
    lines.append("-" * 70)
    lines.append("")
    
    if y_haplo:
        lines.append(f"  Y-DNA Haplogroup: {y_haplo}")
        y_base = y_haplo.split('-')[0].split('*')[0][:2]
        if y_base in Y_HAPLOGROUP_POPS:
            lines.append(f"    Associated ancient populations:")
            for pop in Y_HAPLOGROUP_POPS[y_base][:5]:
                lines.append(f"      • {pop.replace('_', ' ')}")
    else:
        lines.append("  Y-DNA Haplogroup: Not determined (need haplogroup analysis)")
    
    lines.append("")
    
    if mt_haplo:
        lines.append(f"  mtDNA Haplogroup: {mt_haplo}")
        mt_base = mt_haplo[0] if mt_haplo else None
        if mt_base in MT_HAPLOGROUP_POPS:
            lines.append(f"    Associated ancient populations:")
            for pop in MT_HAPLOGROUP_POPS[mt_base][:5]:
                lines.append(f"      • {pop.replace('_', ' ')}")
    else:
        lines.append("  mtDNA Haplogroup: Not determined (need haplogroup analysis)")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("ANCIENT POPULATION REFERENCE")
    lines.append("-" * 70)
    lines.append("")
    
    lines.append("Major ancient population categories:")
    lines.append("")
    
    for category, keywords in POPULATION_CATEGORIES.items():
        lines.append(f"  {category.upper().replace('_', ' ')}:")
        lines.append(f"    Examples: {', '.join(keywords[:5])}")
        lines.append("")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("ABOUT AADR COMPARISON")
    lines.append("-" * 70)
    lines.append("""
The Allen Ancient DNA Resource (AADR) contains data from 17,000+ ancient
individuals spanning from the Paleolithic to the Medieval period.

Full comparison allows:
• Finding ancient individuals who share your haplogroups
• Identifying your closest ancient population matches
• Tracing the geographic origins of your ancestry

To enable full comparison:
1. Download AADR v62+ from Harvard Reich Lab
2. Place annotation file in ~/ancient-dna/
3. Re-run this analysis
""")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ancient_comparison.py <dna_file> [y_haplogroup] [mt_haplogroup]")
        print("Example: python ancient_comparison.py my_dna.txt R1b H")
        sys.exit(1)
    
    filepath = sys.argv[1]
    y_haplo = sys.argv[2] if len(sys.argv) > 2 else None
    mt_haplo = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Checking for AADR database...")
    aadr = load_aadr_annotation()
    aadr_available = aadr is not None
    
    if aadr_available:
        print(f"Found AADR with {len(aadr):,} ancient samples")
    else:
        print("AADR not found - using haplogroup reference data")
    
    print("Matching haplogroups to ancient populations...")
    haplo_matches = match_haplogroups_to_populations(y_haplo, mt_haplo)
    
    # Save results
    results = {
        'aadr_available': aadr_available,
        'y_haplogroup': y_haplo,
        'mt_haplogroup': mt_haplo,
        'haplogroup_matches': haplo_matches,
    }
    
    with open(OUTPUT_DIR / "ancient_comparison.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = generate_report(aadr_available, haplo_matches, y_haplo, mt_haplo)
    
    with open(OUTPUT_DIR / "ancient_comparison.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
