#!/usr/bin/env python3
"""
Ancient DNA Marker Analysis
Identifies markers shared with ancient populations.
Works with any ancestry/ethnic background.

Privacy: All analysis runs locally. No network requests.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# ANCIENT DNA MARKERS
# Markers commonly used in aDNA studies to identify ancestry layers
# =============================================================================

ANCIENT_MARKERS = {
    # Mesolithic Hunter-Gatherers (Western Europe)
    "mesolithic_hunter_gatherer": {
        "description": "Pre-farming Europeans (~10,000-5,000 BCE)",
        "markers": {
            "rs12913832": {"name": "HERC2", "ancient": "A", "derived": "G", "trait": "Blue eyes arose in this population"},
            "rs16891982": {"name": "SLC45A2", "ancient": "C", "derived": "G", "trait": "Light skin (partial)"},
        }
    },
    
    # Neolithic Farmers (Anatolia → Europe)
    "neolithic_farmer": {
        "description": "Early farmers from Anatolia (~7,000-4,000 BCE)",
        "markers": {
            "rs1426654": {"name": "SLC24A5", "ancient": "A", "derived": "A", "trait": "Light skin (fixed in this population)"},
            "rs4988235": {"name": "LCT", "ancient": "G", "derived": "A", "trait": "Lactose tolerance (rare in early farmers)"},
        }
    },
    
    # Steppe Pastoralists (Yamnaya and related)
    "steppe_pastoralist": {
        "description": "Bronze Age steppe herders (Yamnaya, ~3,000-2,000 BCE)",
        "markers": {
            "rs4988235": {"name": "LCT", "ancient": "A", "derived": "A", "trait": "Lactase persistence spread with this population"},
            "rs12913832": {"name": "HERC2", "ancient": "G", "derived": "G", "trait": "Mixed eye color"},
        }
    },
    
    # Archaic Introgression Markers
    "archaic_introgression": {
        "description": "Markers from Neanderthal/Denisovan introgression",
        "markers": {
            "rs2298850": {"name": "OAS1", "neanderthal": "G", "trait": "Immune function (Neanderthal origin)"},
            "rs1051730": {"name": "CHRNA3", "neanderthal": "A", "trait": "Nicotine addiction (possible Neanderthal origin)"},
            "rs4846049": {"name": "MCPH1", "archaic": "T", "trait": "Brain development (archaic variant)"},
        }
    },
    
    # Y-DNA Ancient Haplogroups
    "ancient_y_haplogroups": {
        "description": "Y-chromosome lineages traceable to ancient populations",
        "markers": {
            # R1b - Western European, spread with Bell Beaker
            "rs9786184": {"haplogroup": "R1b", "allele": "A", "origin": "Steppe → Western Europe via Bell Beaker"},
            # R1a - Eastern European/South Asian, Corded Ware
            "rs17250804": {"haplogroup": "R1a", "allele": "G", "origin": "Steppe → Eastern Europe via Corded Ware"},
            # I - Pre-Indo-European, Mesolithic Europe
            "rs2032652": {"haplogroup": "I", "allele": "G", "origin": "Mesolithic Europe (WHG)"},
            # J - Middle East/Mediterranean, Neolithic expansion
            "rs2032631": {"haplogroup": "J", "allele": "A", "origin": "Middle East, spread with Neolithic"},
            # E - Africa/Mediterranean
            "rs9341296": {"haplogroup": "E", "allele": "C", "origin": "Africa, present in Mediterranean"},
            # G - Anatolia/Caucasus, early farmers
            "rs2032636": {"haplogroup": "G", "allele": "T", "origin": "Anatolia, spread with early farmers"},
            # N - Siberia/Finland/Baltic
            "rs9341301": {"haplogroup": "N", "allele": "A", "origin": "Siberia, spread to Baltic/Finland"},
            # O - East Asia
            "rs3908": {"haplogroup": "O", "allele": "T", "origin": "East Asia"},
            # Q - Siberia/Americas
            "rs17316625": {"haplogroup": "Q", "allele": "C", "origin": "Siberia, spread to Americas"},
        }
    },
    
    # mtDNA Ancient Haplogroups
    "ancient_mt_haplogroups": {
        "description": "Mitochondrial lineages with ancient origins",
        "markers": {
            "rs2853499": {"haplogroup": "H", "allele": "G", "origin": "Most common European, expanded post-LGM"},
            "rs28358571": {"haplogroup": "U", "allele": "A", "origin": "Ancient European, strong in WHG"},
            "rs3928306": {"haplogroup": "L", "allele": "A", "origin": "African origin, basal human mtDNA"},
            "rs2853515": {"haplogroup": "A", "allele": "G", "origin": "East Asian/Native American"},
            "rs2853508": {"haplogroup": "B", "allele": "A", "origin": "East Asian/Polynesian"},
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
        # Assume first column is rsid
        df.columns = ['rsid', 'chromosome', 'position', 'genotype'] + list(df.columns[4:])
        df = df.set_index('rsid')
    
    return df


def get_genotype(df, rsid):
    try:
        return df.loc[rsid, 'genotype']
    except:
        return None


def analyze_ancient_markers(df):
    """Analyze ancient DNA markers."""
    results = {}
    
    for period, data in ANCIENT_MARKERS.items():
        period_results = {
            "description": data["description"],
            "markers_found": [],
            "markers_missing": []
        }
        
        for rsid, info in data["markers"].items():
            geno = get_genotype(df, rsid)
            marker_info = {"rsid": rsid, **info}
            
            if geno:
                marker_info["genotype"] = geno
                
                # Determine which allele(s) present
                if "ancient" in info:
                    marker_info["has_ancient"] = info["ancient"] in geno
                if "derived" in info:
                    marker_info["has_derived"] = info["derived"] in geno
                if "neanderthal" in info:
                    marker_info["has_archaic"] = info["neanderthal"] in geno
                if "allele" in info:
                    marker_info["has_haplogroup_marker"] = info["allele"] in geno
                
                period_results["markers_found"].append(marker_info)
            else:
                period_results["markers_missing"].append(marker_info)
        
        results[period] = period_results
    
    return results


def generate_report(results):
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ANCIENT DNA MARKER ANALYSIS")
    lines.append("=" * 70)
    lines.append("")
    lines.append("This analysis identifies markers shared with ancient populations.")
    lines.append("These markers have been studied in ancient DNA samples and can")
    lines.append("provide insights into your deep ancestry.")
    lines.append("")
    
    for period, data in results.items():
        lines.append("-" * 70)
        lines.append(f"{period.upper().replace('_', ' ')}")
        lines.append(f"  {data['description']}")
        lines.append("-" * 70)
        
        if data['markers_found']:
            for m in data['markers_found']:
                lines.append(f"\n  {m.get('name', m['rsid'])} ({m['rsid']}): {m.get('genotype', 'N/A')}")
                
                if m.get('trait'):
                    lines.append(f"    → {m['trait']}")
                if m.get('origin'):
                    lines.append(f"    → Origin: {m['origin']}")
                if m.get('has_ancient'):
                    lines.append(f"    → Carries ancient/ancestral allele")
                if m.get('has_derived'):
                    lines.append(f"    → Carries derived allele")
                if m.get('has_archaic'):
                    lines.append(f"    → Carries archaic (Neanderthal/Denisovan) allele")
                if m.get('has_haplogroup_marker'):
                    lines.append(f"    → Haplogroup {m.get('haplogroup', '?')} indicator positive")
        else:
            lines.append("  No markers available in your data for this category.")
        
        lines.append("")
    
    lines.append("=" * 70)
    lines.append("INTERPRETATION NOTES")
    lines.append("=" * 70)
    lines.append("""
All modern humans outside Africa carry 1-2% Neanderthal DNA.
Ancient ancestry markers show the "layers" of your genome:

1. DEEP AFRICAN ORIGIN (>70,000 years ago)
   → All humans share common African ancestry

2. OUT OF AFRICA (70,000-50,000 years ago)
   → Non-African populations diverged; Neanderthal admixture occurred

3. POPULATION DIFFERENTIATION (50,000-10,000 years ago)
   → Regional populations developed; haplogroups diversified

4. AGRICULTURAL REVOLUTION (10,000-5,000 years ago)
   → Farmers from Anatolia spread across Europe
   → Lactase persistence began to spread

5. BRONZE AGE MIGRATIONS (5,000-3,000 years ago)
   → Steppe ancestry spread via Yamnaya and related cultures
   → R1a/R1b haplogroups expanded dramatically

Your genome is a palimpsest of all these layers.
""")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ancient_dna.py <dna_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Loading {filepath}...")
    df = load_dna_file(filepath)
    print(f"Loaded {len(df):,} SNPs")
    
    print("Analyzing ancient DNA markers...")
    results = analyze_ancient_markers(df)
    
    # Save JSON
    with open(OUTPUT_DIR / "ancient_dna_report.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = generate_report(results)
    
    with open(OUTPUT_DIR / "ancient_dna_report.md", 'w') as f:
        f.write(report)
    
    print(report)
    print(f"\n✓ Reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
