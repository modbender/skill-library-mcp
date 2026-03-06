#!/usr/bin/env python3
"""
Convert consumer DNA data to PLINK format for advanced analysis.
Works with any ancestry/ethnic background.
"""

import sys
import pandas as pd
from pathlib import Path

def convert_to_plink(input_file, output_prefix):
    """Convert DNA file to PLINK .map and .ped format."""
    
    print(f"Loading {input_file}...")
    
    # Load data
    try:
        df = pd.read_csv(input_file, sep='\t', comment='#', dtype=str, low_memory=False)
        
        # Standardize column names
        col_map = {
            'rsID': 'rsid',
            'chromosome': 'chromosome', 
            'position': 'position',
            'allele1': 'allele1',
            'allele2': 'allele2'
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        
        if 'genotype' in df.columns and 'allele1' not in df.columns:
            # 23andMe format
            df['allele1'] = df['genotype'].str[0]
            df['allele2'] = df['genotype'].str[1] if df['genotype'].str.len().max() > 1 else df['genotype'].str[0]
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(df):,} SNPs")
    
    # Create MAP file (chromosome, rsid, genetic_distance, position)
    map_df = df[['chromosome', 'rsid', 'position']].copy()
    map_df.insert(2, 'genetic_distance', 0)
    map_df.to_csv(f'{output_prefix}.map', sep='\t', header=False, index=False)
    print(f"Created {output_prefix}.map")
    
    # Create PED file (family, individual, father, mother, sex, phenotype, genotypes...)
    genotypes = []
    for _, row in df.iterrows():
        a1 = row['allele1'] if pd.notna(row['allele1']) else '0'
        a2 = row['allele2'] if pd.notna(row['allele2']) else '0'
        genotypes.extend([a1, a2])
    
    # Use generic identifiers
    ped_line = ['FAM001', 'IND001', '0', '0', '0', '-9'] + genotypes
    
    with open(f'{output_prefix}.ped', 'w') as f:
        f.write('\t'.join(ped_line) + '\n')
    print(f"Created {output_prefix}.ped")
    
    print(f"\nDone! Created {output_prefix}.map and {output_prefix}.ped")
    print("\nTo convert to binary format (recommended for large analyses):")
    print(f"  plink --file {output_prefix} --make-bed --out {output_prefix}_binary")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_plink.py <input_dna_file> <output_prefix>")
        print("Example: python convert_to_plink.py ~/Downloads/AncestryDNA.txt my_genome")
        sys.exit(1)
    
    convert_to_plink(sys.argv[1], sys.argv[2])
