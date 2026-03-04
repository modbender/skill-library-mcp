#!/usr/bin/env python3
"""
Parental Ancestry Inference
Infer which genetic variants likely came from each parent.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.

Note: Without parental DNA, this is inferential based on:
- X chromosome (for males - all from mother)
- mtDNA (maternal only)
- Y-DNA (paternal only, for males)
- Phasing heuristics for autosomal chromosomes
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Markers useful for parental inference
INFORMATIVE_MARKERS = {
    # Ancestry-informative markers that can help trace parental contributions
    # These are population-specific variants that may differ between parents
    
    "european": {
        "rs16891982": {"name": "SLC45A2", "derived": "G", "ancestral": "C"},
        "rs1426654": {"name": "SLC24A5", "derived": "A", "ancestral": "G"},
        "rs12913832": {"name": "HERC2", "derived": "G", "ancestral": "A"},
    },
    
    "east_asian": {
        "rs3827760": {"name": "EDAR", "derived": "A", "ancestral": "G"},
        "rs671": {"name": "ALDH2", "derived": "A", "ancestral": "G"},
    },
    
    "african": {
        "rs2814778": {"name": "DARC", "derived": "C", "ancestral": "T"},
    },
    
    # Methylation markers (often population-stratified)
    "methylation": {
        "rs1801133": {"name": "MTHFR C677T", "risk": "A", "common": "G"},
        "rs1801131": {"name": "MTHFR A1298C", "risk": "G", "common": "T"},
    },
    
    # Pigmentation (informative for mixed ancestry)
    "pigmentation": {
        "rs1805007": {"name": "MC1R R151C", "red_hair": "T", "common": "C"},
        "rs1805008": {"name": "MC1R R160W", "red_hair": "T", "common": "C"},
        "rs12203592": {"name": "IRF4", "light": "T", "common": "C"},
    },
}

# Y-DNA and mtDNA haplogroup markers
HAPLOGROUP_MARKERS = {
    "y_dna": {
        "rs9786184": {"haplo": "R1b", "allele": "A"},
        "rs17250804": {"haplo": "R1a", "allele": "G"},
        "rs2032652": {"haplo": "I", "allele": "G"},
        "rs2032631": {"haplo": "J", "allele": "A"},
        "rs9341296": {"haplo": "E", "allele": "C"},
    },
    "mt_dna": {
        "rs2853499": {"haplo": "H", "allele": "G"},
        "rs28358571": {"haplo": "U", "allele": "A"},
    }
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


def analyze_haplogroups(df):
    """Identify Y-DNA and mtDNA haplogroups."""
    results = {"y_dna": None, "mt_dna": None}
    
    # Y-DNA (only meaningful for males)
    y_matches = []
    for rsid, info in HAPLOGROUP_MARKERS["y_dna"].items():
        geno = get_genotype(df, rsid)
        if geno and info["allele"] in geno:
            y_matches.append(info["haplo"])
    
    if y_matches:
        results["y_dna"] = y_matches[0]  # Take first match
    
    # mtDNA
    mt_matches = []
    for rsid, info in HAPLOGROUP_MARKERS["mt_dna"].items():
        geno = get_genotype(df, rsid)
        if geno and info["allele"] in geno:
            mt_matches.append(info["haplo"])
    
    if mt_matches:
        results["mt_dna"] = mt_matches[0]
    
    return results


def analyze_heterozygous_markers(df):
    """Find heterozygous markers useful for parental inference."""
    results = defaultdict(list)
    
    for category, markers in INFORMATIVE_MARKERS.items():
        for rsid, info in markers.items():
            geno = get_genotype(df, rsid)
            if geno and len(set(geno)) == 2:  # Heterozygous
                results[category].append({
                    "rsid": rsid,
                    "name": info["name"],
                    "genotype": geno,
                    "info": info
                })
    
    return dict(results)


def generate_report(haplogroups, het_markers):
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PARENTAL ANCESTRY INFERENCE")
    lines.append("=" * 70)
    lines.append("")
    lines.append("This analysis infers parental contributions based on:")
    lines.append("• Y-DNA haplogroup (paternal line, males only)")
    lines.append("• mtDNA haplogroup (maternal line)")
    lines.append("• Heterozygous ancestry-informative markers")
    lines.append("")
    lines.append("⚠️  Note: Without parental DNA samples, these are inferences only.")
    lines.append("")
    
    lines.append("-" * 70)
    lines.append("UNIPARENTAL MARKERS")
    lines.append("-" * 70)
    lines.append("")
    
    lines.append("  Y-DNA HAPLOGROUP (Father's paternal line):")
    if haplogroups["y_dna"]:
        lines.append(f"    → {haplogroups['y_dna']}")
        lines.append(f"    This Y-chromosome lineage traces your father's father's father's...")
        lines.append(f"    line back thousands of years.")
    else:
        lines.append("    → Not determined (either female or markers not found)")
    
    lines.append("")
    lines.append("  mtDNA HAPLOGROUP (Mother's maternal line):")
    if haplogroups["mt_dna"]:
        lines.append(f"    → {haplogroups['mt_dna']}")
        lines.append(f"    This mitochondrial lineage traces your mother's mother's mother's...")
        lines.append(f"    line back thousands of years.")
    else:
        lines.append("    → Not determined (markers not found)")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("HETEROZYGOUS ANCESTRY MARKERS")
    lines.append("-" * 70)
    lines.append("")
    lines.append("  Heterozygous (mixed) markers suggest different parental ancestries:")
    lines.append("")
    
    for category, markers in het_markers.items():
        if markers:
            lines.append(f"  {category.upper().replace('_', ' ')}:")
            for m in markers:
                lines.append(f"    • {m['name']} ({m['rsid']}): {m['genotype']}")
                lines.append(f"      One allele from each parent")
            lines.append("")
    
    if not any(het_markers.values()):
        lines.append("  No informative heterozygous markers found.")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("INTERPRETATION")
    lines.append("-" * 70)
    lines.append("""
HOW TO USE THIS INFORMATION:

1. Y-DNA and mtDNA trace single lineages (father's father's... and 
   mother's mother's...) but represent only 2 of your many ancestors.

2. Heterozygous ancestry markers show where your parents differed.
   If you have mixed ancestry, these markers can help identify which
   ancestral components came from which parent.

3. For definitive parental phasing, you would need:
   - DNA from one or both parents, OR
   - DNA from siblings or other relatives, OR
   - Whole genome sequencing with statistical phasing

LIMITATIONS:
• This analysis uses a small subset of ancestry-informative markers
• Homozygous markers cannot distinguish parental origin
• Recombination means your autosomes are a mosaic of both parents
""")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python parental_inference.py <dna_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Analyzing haplogroups...")
    haplogroups = analyze_haplogroups(df)
    
    print("Finding heterozygous ancestry markers...")
    het_markers = analyze_heterozygous_markers(df)
    
    # Save results
    results = {
        "haplogroups": haplogroups,
        "heterozygous_markers": het_markers
    }
    
    with open(OUTPUT_DIR / "parental_inference.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = generate_report(haplogroups, het_markers)
    
    with open(OUTPUT_DIR / "parental_inference.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
