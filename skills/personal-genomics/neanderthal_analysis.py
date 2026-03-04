#!/usr/bin/env python3
"""
Neanderthal & Archaic Human DNA Analysis
Identifies variants inherited from Neanderthals and Denisovans.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.

Note: All non-African modern humans carry 1-2% Neanderthal DNA.
East Asians and Oceanians may also carry Denisovan ancestry.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# NEANDERTHAL INTROGRESSION MARKERS
# SNPs where the archaic allele is known to have introgressed from Neanderthals
# =============================================================================

NEANDERTHAL_MARKERS = {
    # Immune System (BN-associated)
    "rs2066807": {
        "gene": "TLR1", 
        "neanderthal_allele": "G",
        "function": "Innate immunity - bacterial recognition",
        "note": "Neanderthal version may increase inflammation"
    },
    "rs5743618": {
        "gene": "TLR1",
        "neanderthal_allele": "G", 
        "function": "Innate immunity",
        "note": "Associated with susceptibility to leprosy"
    },
    "rs2298850": {
        "gene": "OAS1",
        "neanderthal_allele": "G",
        "function": "Antiviral defense",
        "note": "Neanderthal version may improve viral resistance"
    },
    "rs1800629": {
        "gene": "TNF",
        "neanderthal_allele": "A",
        "function": "Inflammatory response",
        "note": "May influence autoimmune conditions"
    },
    
    # Skin and Hair
    "rs1042602": {
        "gene": "TYR",
        "neanderthal_allele": "A",
        "function": "Pigmentation",
        "note": "May influence skin color variation"
    },
    "rs2228479": {
        "gene": "MC1R",
        "neanderthal_allele": "A",
        "function": "Pigmentation (red hair/fair skin)",
        "note": "Possible Neanderthal contribution to European coloring"
    },
    "rs11803731": {
        "gene": "TCHH",
        "neanderthal_allele": "A",
        "function": "Hair texture",
        "note": "Neanderthal version associated with straight hair"
    },
    
    # Brain and Behavior
    "rs4846049": {
        "gene": "MCPH1",
        "neanderthal_allele": "T",
        "function": "Brain development",
        "note": "Haplogroup D variant, possible Neanderthal origin"
    },
    "rs1051730": {
        "gene": "CHRNA3",
        "neanderthal_allele": "A",
        "function": "Nicotinic receptor",
        "note": "May influence nicotine addiction susceptibility"
    },
    "rs3781413": {
        "gene": "DISC1",
        "neanderthal_allele": "T",
        "function": "Brain development/mental health",
        "note": "Disrupted in schizophrenia gene 1"
    },
    
    # Metabolism
    "rs2237892": {
        "gene": "KCNQ1",
        "neanderthal_allele": "C",
        "function": "Glucose metabolism",
        "note": "Type 2 diabetes risk (higher in East Asians)"
    },
    "rs10811661": {
        "gene": "CDKN2A/B",
        "neanderthal_allele": "T",
        "function": "Cell cycle regulation",
        "note": "Diabetes risk variant"
    },
    
    # Blood/Coagulation
    "rs3917643": {
        "gene": "SELP",
        "neanderthal_allele": "A",
        "function": "Blood clotting",
        "note": "Neanderthal version may increase clotting"
    },
    
    # Circadian Rhythm
    "rs934945": {
        "gene": "PER2",
        "neanderthal_allele": "G",
        "function": "Circadian rhythm",
        "note": "May have helped adaptation to northern latitudes"
    },
    
    # Keratin (Skin/Hair)
    "rs3768298": {
        "gene": "BNC2",
        "neanderthal_allele": "A",
        "function": "Skin pigmentation",
        "note": "Associated with freckling and skin tone"
    },
}

# Denisovan-specific markers (less well characterized)
DENISOVAN_MARKERS = {
    "rs73185325": {
        "gene": "EPAS1",
        "denisovan_allele": "G",
        "function": "High-altitude adaptation",
        "note": "Found in Tibetans, Denisovan origin confirmed"
    },
    # Note: Most Denisovan introgression is in Oceanian/East Asian populations
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


def analyze_archaic_markers(df):
    """Analyze Neanderthal and Denisovan markers."""
    neanderthal_results = {
        "markers_found": 0,
        "archaic_alleles": 0,
        "total_possible": 0,
        "details": []
    }
    
    denisovan_results = {
        "markers_found": 0,
        "archaic_alleles": 0,
        "details": []
    }
    
    # Neanderthal markers
    for rsid, info in NEANDERTHAL_MARKERS.items():
        geno = get_genotype(df, rsid)
        if geno:
            neanderthal_results["markers_found"] += 1
            neanderthal_results["total_possible"] += 2
            
            archaic_count = geno.count(info["neanderthal_allele"])
            neanderthal_results["archaic_alleles"] += archaic_count
            
            neanderthal_results["details"].append({
                "rsid": rsid,
                "gene": info["gene"],
                "genotype": geno,
                "neanderthal_allele": info["neanderthal_allele"],
                "archaic_count": archaic_count,
                "function": info["function"],
                "note": info["note"],
                "has_archaic": archaic_count > 0
            })
    
    # Denisovan markers
    for rsid, info in DENISOVAN_MARKERS.items():
        geno = get_genotype(df, rsid)
        if geno:
            denisovan_results["markers_found"] += 1
            archaic_count = geno.count(info["denisovan_allele"])
            denisovan_results["archaic_alleles"] += archaic_count
            
            denisovan_results["details"].append({
                "rsid": rsid,
                "gene": info["gene"],
                "genotype": geno,
                "denisovan_allele": info["denisovan_allele"],
                "archaic_count": archaic_count,
                "function": info["function"],
                "note": info["note"],
                "has_archaic": archaic_count > 0
            })
    
    # Calculate percentage
    if neanderthal_results["total_possible"] > 0:
        neanderthal_results["archaic_percentage"] = round(
            100 * neanderthal_results["archaic_alleles"] / neanderthal_results["total_possible"], 1
        )
    else:
        neanderthal_results["archaic_percentage"] = 0
    
    return {"neanderthal": neanderthal_results, "denisovan": denisovan_results}


def generate_report(results):
    """Generate human-readable report."""
    n = results["neanderthal"]
    d = results["denisovan"]
    
    lines = []
    lines.append("=" * 70)
    lines.append("NEANDERTHAL & ARCHAIC DNA ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    lines.append("All non-African humans carry 1-2% Neanderthal DNA from interbreeding")
    lines.append("~50,000-60,000 years ago. Some populations also carry Denisovan DNA.")
    lines.append("")
    
    lines.append("-" * 70)
    lines.append("NEANDERTHAL INTROGRESSION")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"  Markers analyzed: {n['markers_found']}/{len(NEANDERTHAL_MARKERS)}")
    lines.append(f"  Archaic alleles: {n['archaic_alleles']}/{n['total_possible']}")
    lines.append(f"  Archaic percentage: {n['archaic_percentage']}%")
    lines.append("")
    
    # Group by function
    by_function = defaultdict(list)
    for m in n["details"]:
        if m["has_archaic"]:
            by_function[m["function"]].append(m)
    
    if by_function:
        lines.append("  Neanderthal variants detected by function:")
        lines.append("")
        for func, markers in by_function.items():
            lines.append(f"  {func.upper()}:")
            for m in markers:
                lines.append(f"    • {m['gene']} ({m['rsid']}): {m['genotype']}")
                lines.append(f"      {m['note']}")
            lines.append("")
    
    lines.append("-" * 70)
    lines.append("DENISOVAN MARKERS")
    lines.append("-" * 70)
    lines.append("")
    
    if d["details"]:
        for m in d["details"]:
            status = "✓ Present" if m["has_archaic"] else "○ Not present"
            lines.append(f"  {m['gene']} ({m['rsid']}): {status}")
            lines.append(f"    {m['note']}")
    else:
        lines.append("  No Denisovan markers found in data.")
        lines.append("  (Denisovan ancestry is primarily found in Oceanian populations)")
    
    lines.append("")
    lines.append("-" * 70)
    lines.append("INTERPRETATION")
    lines.append("-" * 70)
    lines.append("""
NEANDERTHAL ANCESTRY BY POPULATION (typical ranges):
  • Europeans: 1.8-2.4%
  • East Asians: 1.9-2.5%  
  • South Asians: 1.7-2.2%
  • Native Americans: 1.6-2.0%
  • Africans: <0.5% (from back-migration)

This analysis uses ~15 well-characterized Neanderthal introgression markers.
Your actual total Neanderthal ancestry may differ from this estimate.
For precise measurement, whole genome sequencing is recommended.

FUNCTIONAL IMPLICATIONS:
• Immune variants may affect disease susceptibility
• Skin/hair variants contributed to human adaptation to northern climates
• Metabolic variants may influence modern disease risks
• Circadian variants may have helped adaptation to seasonal light changes
""")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python neanderthal_analysis.py <dna_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Analyzing archaic introgression markers...")
    results = analyze_archaic_markers(df)
    
    # Save JSON
    with open(OUTPUT_DIR / "neanderthal_report.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = generate_report(results)
    
    with open(OUTPUT_DIR / "neanderthal_report.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
