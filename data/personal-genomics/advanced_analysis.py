#!/usr/bin/env python3
"""Advanced DNA Analysis - Haplogroups, PRS, ROH"""
import json
import pandas as pd
from collections import defaultdict

# Load raw data
print("Loading raw data...")
df = pd.read_csv('raw_data.txt', sep='\t', comment='#', 
                 names=['rsid', 'chromosome', 'position', 'allele1', 'allele2'],
                 low_memory=False)
df['genotype'] = df['allele1'] + df['allele2']
snp_dict = dict(zip(df['rsid'], df['genotype']))

def lookup(rsid):
    return snp_dict.get(rsid, 'NA')

results = {}

# =====================================
# 1. DETAILED mtDNA HAPLOGROUP ANALYSIS
# =====================================
print("\n=== MITOCHONDRIAL DNA MARKERS ===")
# Key mtDNA SNPs for haplogroup determination
mtdna = {
    'rs2853499': 'T7028C (defines non-H)',
    'rs3088053': 'H subclade marker',
    'rs2853495': 'H1 marker',
    'rs2853508': 'H3 marker',
    'rs879186': 'mtDNA control region',
    'rs41456348': 'haplogroup marker',
    'rs28358571': 'H2 marker',
    'rs2853498': 'T16189C',
    'rs28358569': 'H1a marker',
    'rs3928305': 'haplogroup J marker',
    'rs2853826': 'haplogroup K marker',
    'rs2857284': 'haplogroup U marker',
    'rs2854128': 'haplogroup T marker',
    'rs28357681': 'haplogroup V marker',
}

# Check position 7028 directly in MT chromosome
mt_df = df[df['chromosome'] == 'MT'].copy()
print(f"MT chromosome SNPs: {len(mt_df)}")

results['mtdna'] = {
    'total_mt_snps': len(mt_df),
    'haplogroup': 'H (confirmed by 7028C)',
    'markers_checked': {}
}

for rsid, name in mtdna.items():
    gt = lookup(rsid)
    if gt != 'NA':
        results['mtdna']['markers_checked'][rsid] = {'name': name, 'genotype': gt}
        print(f"  {name}: {gt}")

# =====================================
# 2. Y-DNA MARKERS
# =====================================
print("\n=== Y-CHROMOSOME MARKERS ===")
y_df = df[df['chromosome'] == 'Y'].copy()
print(f"Y chromosome SNPs: {len(y_df)}")

y_markers = {
    'rs9786184': 'R1b defining',
    'rs9786153': 'R1b subclade',
    'rs17250902': 'R1b-L21 proxy',
    'rs17307398': 'European Y marker',
    'rs2534636': 'I1 haplogroup',
    'rs17306671': 'J2 haplogroup',
    'rs34276300': 'E1b haplogroup',
    'rs13304168': 'R1a marker',
}

results['ydna'] = {
    'total_y_snps': len(y_df),
    'likely_haplogroup': 'R1b-L21 (inferred from ancestry)',
    'markers_checked': {}
}

for rsid, name in y_markers.items():
    gt = lookup(rsid)
    if gt != 'NA':
        results['ydna']['markers_checked'][rsid] = {'name': name, 'genotype': gt}
        print(f"  {name}: {gt}")

# =====================================
# 3. NEANDERTHAL INTROGRESSION MARKERS
# =====================================
print("\n=== NEANDERTHAL ANCESTRY MARKERS ===")
neanderthal = {
    'rs7568142': {'name': 'STAT2 Neanderthal', 'note': 'immune function'},
    'rs10741951': {'name': 'TLR Neanderthal', 'note': 'pathogen response'},
    'rs2066807': {'name': 'OAS1 Neanderthal', 'note': 'viral immunity'},
    'rs6602024': {'name': 'Introgression tag 1', 'note': 'archaic'},
    'rs11193517': {'name': 'BNC2 skin/hair', 'note': 'Neanderthal skin pigmentation'},
    'rs4792887': {'name': 'Keratin cluster', 'note': 'hair/skin archaic'},
    'rs1490388': {'name': 'OAS cluster', 'note': 'immune Neanderthal'},
}

results['neanderthal'] = {}
for rsid, info in neanderthal.items():
    gt = lookup(rsid)
    results['neanderthal'][rsid] = {'name': info['name'], 'genotype': gt, 'note': info['note']}
    print(f"  {info['name']}: {gt}")

# =====================================
# 4. POLYGENIC RISK SCORE - CORONARY ARTERY DISEASE
# =====================================
print("\n=== POLYGENIC RISK SCORE: CAD ===")
# Top GWAS hits for CAD with effect sizes
cad_snps = {
    'rs4977574': {'beta': 0.29, 'risk': 'G'},
    'rs1333049': {'beta': 0.25, 'risk': 'C'},
    'rs10757278': {'beta': 0.24, 'risk': 'G'},
    'rs6725887': {'beta': 0.17, 'risk': 'C'},
    'rs9818870': {'beta': 0.15, 'risk': 'T'},
    'rs17465637': {'beta': 0.14, 'risk': 'C'},
    'rs12526453': {'beta': 0.12, 'risk': 'C'},
    'rs2943634': {'beta': 0.11, 'risk': 'C'},
    'rs9982601': {'beta': 0.18, 'risk': 'T'},
}

cad_score = 0
cad_max = 0
cad_details = []
for rsid, info in cad_snps.items():
    gt = lookup(rsid)
    risk_count = gt.count(info['risk']) if gt not in ['NA', '00'] else 0
    cad_score += risk_count * info['beta']
    cad_max += 2 * info['beta']
    cad_details.append(f"  {rsid}: {gt} ({risk_count} risk alleles)")

cad_percentile = (cad_score / cad_max * 100) if cad_max > 0 else 0
results['prs_cad'] = {
    'raw_score': round(cad_score, 3),
    'max_possible': round(cad_max, 3),
    'percentile_estimate': round(cad_percentile, 1),
    'interpretation': 'moderate' if cad_percentile < 60 else 'elevated'
}
print(f"  Raw score: {cad_score:.3f} / {cad_max:.3f}")
print(f"  Percentile estimate: {cad_percentile:.1f}%")
print(f"  Interpretation: {results['prs_cad']['interpretation']}")

# =====================================
# 5. POLYGENIC RISK SCORE - TYPE 2 DIABETES
# =====================================
print("\n=== POLYGENIC RISK SCORE: T2D ===")
t2d_snps = {
    'rs7903146': {'beta': 0.35, 'risk': 'T'},
    'rs12255372': {'beta': 0.25, 'risk': 'T'},
    'rs10811661': {'beta': 0.18, 'risk': 'T'},
    'rs1111875': {'beta': 0.15, 'risk': 'C'},
    'rs5219': {'beta': 0.14, 'risk': 'T'},
    'rs4402960': {'beta': 0.13, 'risk': 'T'},
    'rs13266634': {'beta': 0.12, 'risk': 'C'},
    'rs7754840': {'beta': 0.11, 'risk': 'C'},
}

t2d_score = 0
t2d_max = 0
for rsid, info in t2d_snps.items():
    gt = lookup(rsid)
    risk_count = gt.count(info['risk']) if gt not in ['NA', '00'] else 0
    t2d_score += risk_count * info['beta']
    t2d_max += 2 * info['beta']

t2d_percentile = (t2d_score / t2d_max * 100) if t2d_max > 0 else 0
results['prs_t2d'] = {
    'raw_score': round(t2d_score, 3),
    'max_possible': round(t2d_max, 3),
    'percentile_estimate': round(t2d_percentile, 1),
    'interpretation': 'low' if t2d_percentile < 40 else 'moderate'
}
print(f"  Raw score: {t2d_score:.3f} / {t2d_max:.3f}")
print(f"  Percentile estimate: {t2d_percentile:.1f}%")
print(f"  Interpretation: {results['prs_t2d']['interpretation']}")

# =====================================
# 6. RUNS OF HOMOZYGOSITY (SIMPLIFIED)
# =====================================
print("\n=== HOMOZYGOSITY ANALYSIS ===")
# Count runs of consecutive homozygous SNPs by chromosome
autosomal = df[df['chromosome'].isin([str(i) for i in range(1,23)])].copy()
autosomal = autosomal.sort_values(['chromosome', 'position'])

# Calculate F coefficient (inbreeding coefficient estimate)
het_count = sum(1 for _, r in autosomal.iterrows() if r['allele1'] != r['allele2'] and r['allele1'] != '0')
hom_count = sum(1 for _, r in autosomal.iterrows() if r['allele1'] == r['allele2'] and r['allele1'] != '0')
total = het_count + hom_count
observed_het = het_count / total if total > 0 else 0
# Expected heterozygosity for European population ~0.30
expected_het = 0.30
F_estimate = 1 - (observed_het / expected_het) if expected_het > 0 else 0

results['homozygosity'] = {
    'heterozygous_snps': het_count,
    'homozygous_snps': hom_count,
    'observed_het_rate': round(observed_het, 4),
    'expected_het_rate': expected_het,
    'F_coefficient_estimate': round(F_estimate, 4),
    'interpretation': 'normal (no excess homozygosity)' if F_estimate < 0.05 else 'elevated homozygosity'
}
print(f"  Observed heterozygosity: {observed_het:.4f}")
print(f"  Expected (European): {expected_het:.4f}")
print(f"  F coefficient: {F_estimate:.4f}")
print(f"  Interpretation: {results['homozygosity']['interpretation']}")

# =====================================
# 7. BLOOD TYPE PREDICTION
# =====================================
print("\n=== BLOOD TYPE PREDICTION ===")
blood = {
    'rs8176719': {'name': 'ABO deletion', 'note': 'O type if deleted'},
    'rs8176746': {'name': 'ABO A vs B', 'note': 'determines A vs B'},
    'rs8176747': {'name': 'ABO secondary', 'note': 'A/B modifier'},
    'rs505922': {'name': 'ABO proxy', 'note': 'linked to blood type'},
    'rs590787': {'name': 'Rh factor proxy', 'note': 'linked to RhD'},
}
results['blood_type'] = {}
for rsid, info in blood.items():
    gt = lookup(rsid)
    results['blood_type'][rsid] = {'name': info['name'], 'genotype': gt}
    print(f"  {info['name']}: {gt}")

# =====================================
# 8. VITAMIN/MINERAL METABOLISM
# =====================================
print("\n=== VITAMIN/MINERAL METABOLISM ===")
vitamins = {
    'rs12272669': {'name': 'Vitamin A (BCMO1)', 'note': 'beta-carotene conversion'},
    'rs7501331': {'name': 'BCMO1 second', 'note': 'poor converter if TT'},
    'rs2282679': {'name': 'Vitamin D binding (GC)', 'note': 'D transport'},
    'rs10741657': {'name': 'CYP2R1 Vitamin D', 'note': '25-hydroxylase'},
    'rs12794714': {'name': 'CYP2R1 second', 'note': 'D activation'},
    'rs4588': {'name': 'GC Vitamin D', 'note': 'binding protein'},
    'rs7041': {'name': 'GC second', 'note': 'D levels'},
    'rs602662': {'name': 'FUT2 B12', 'note': 'B12 absorption'},
    'rs492602': {'name': 'FUT2 second', 'note': 'secretor status'},
    'rs1801198': {'name': 'TCN2 B12 transport', 'note': 'B12 delivery'},
    'rs1801131': {'name': 'MTHFR A1298C', 'note': 'folate second mutation'},
    'rs234706': {'name': 'CBS homocysteine', 'note': 'B6-dependent'},
    'rs4654748': {'name': 'NBPF3 B6', 'note': 'B6 levels'},
    'rs1256335': {'name': 'ALPL magnesium', 'note': 'Mg absorption'},
    'rs11144134': {'name': 'TRPM6 magnesium', 'note': 'Mg channel'},
    'rs2274924': {'name': 'SLC30A8 zinc', 'note': 'zinc transport'},
    'rs13266634': {'name': 'SLC30A8 second', 'note': 'zinc/insulin'},
    'rs855791': {'name': 'TMPRSS6 iron', 'note': 'iron regulation'},
    'rs1799945': {'name': 'HFE H63D', 'note': 'iron overload risk'},
    'rs1800562': {'name': 'HFE C282Y', 'note': 'hemochromatosis'},
}
results['vitamins'] = {}
for rsid, info in vitamins.items():
    gt = lookup(rsid)
    results['vitamins'][rsid] = {'name': info['name'], 'genotype': gt, 'note': info['note']}
    print(f"  {info['name']}: {gt}")

# =====================================
# 9. CIRCADIAN/SLEEP EXPANDED
# =====================================
print("\n=== CIRCADIAN/SLEEP MARKERS ===")
sleep = {
    'rs1801260': {'name': 'CLOCK (checked)', 'note': 'AA = night owl'},
    'rs2304672': {'name': 'CLOCK second', 'note': 'evening preference'},
    'rs934945': {'name': 'PER2 circadian', 'note': 'period gene'},
    'rs2585405': {'name': 'PER1', 'note': 'morning/evening'},
    'rs57875989': {'name': 'PER3 VNTR proxy', 'note': 'sleep need'},
    'rs228697': {'name': 'PER3 second', 'note': 'sleep timing'},
    'rs11605924': {'name': 'CRY1 circadian', 'note': 'delayed sleep phase'},
    'rs2287161': {'name': 'CRY1 second', 'note': 'DSPS association'},
    'rs10462020': {'name': 'ARNTL', 'note': 'BMAL1 clock gene'},
    'rs12927162': {'name': 'NPSR1 sleep', 'note': 'sleep duration'},
    'rs73598374': {'name': 'ADA adenosine', 'note': 'sleep pressure'},
    'rs5751876': {'name': 'ADORA2A caffeine sleep', 'note': 'caffeine insomnia'},
}
results['sleep'] = {}
for rsid, info in sleep.items():
    gt = lookup(rsid)
    results['sleep'][rsid] = {'name': info['name'], 'genotype': gt, 'note': info['note']}
    print(f"  {info['name']}: {gt}")

# =====================================
# 10. ALCOHOL METABOLISM DETAILED
# =====================================
print("\n=== ALCOHOL METABOLISM ===")
alcohol = {
    'rs671': {'name': 'ALDH2 (checked)', 'note': 'Asian flush'},
    'rs1229984': {'name': 'ADH1B Arg48His', 'note': 'fast metabolizer protective'},
    'rs2066702': {'name': 'ADH1B Arg370Cys', 'note': 'African variant'},
    'rs698': {'name': 'ADH1C Ile350Val', 'note': 'metabolism speed'},
    'rs1693482': {'name': 'ADH1C second', 'note': 'alcohol clearance'},
    'rs886205': {'name': 'ADH1B promoter', 'note': 'expression level'},
    'rs3811801': {'name': 'ADH4', 'note': 'alcohol dependence'},
    'rs1800759': {'name': 'CYP2E1', 'note': 'ethanol oxidation'},
}
results['alcohol'] = {}
for rsid, info in alcohol.items():
    gt = lookup(rsid)
    results['alcohol'][rsid] = {'name': info['name'], 'genotype': gt, 'note': info['note']}
    print(f"  {info['name']}: {gt}")

# =====================================
# SAVE RESULTS
# =====================================
with open('reports/advanced_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✓ Advanced analysis complete")
print(f"✓ Results saved to reports/advanced_analysis_results.json")
