"""
Synthetic DNA test fixtures.
All data is synthetic/anonymized - no real human data.

These fixtures provide realistic test data covering:
- Various ancestry backgrounds
- Common and rare variants
- High-risk findings
- Carrier status scenarios
- Edge cases
"""

# Complete synthetic genome with ~500 clinically relevant SNPs
# Represents a fictional individual for testing

SYNTHETIC_GENOME_EUROPEAN = """# Synthetic Test Genome - European Ancestry
# Generated for software testing - NOT REAL HUMAN DATA
# Format: 23andMe-like
rsid	chromosome	position	allele1	allele2
# APOE - E3/E4 (elevated Alzheimer's risk)
rs429358	19	44908684	T	C
rs7412	19	44908822	C	C
# Factor V Leiden - Normal
rs6025	1	169519049	C	C
# Prothrombin - Normal
rs1799963	11	46761055	G	G
# MTHFR C677T - Heterozygous
rs1801133	1	11856378	A	G
# MTHFR A1298C - Normal
rs1801131	1	11854476	T	T
# COMT - Warrior (GG)
rs4680	22	19951271	G	G
# CYP2C19 - Poor metabolizer (*2/*2)
rs4244285	10	96541616	A	A
# CYP2D6 - Normal
rs3892097	22	42526694	C	C
# Warfarin sensitivity - VKORC1 AA (sensitive)
rs9923231	16	31107689	T	T
# CYP2C9 - *1/*2
rs1799853	10	96702047	C	T
# DPYD - Normal (critical for 5-FU)
rs3918290	1	97915614	C	C
rs67376798	1	97981395	T	T
# SLCO1B1 - Reduced function (statin myopathy risk)
rs4149056	12	21331549	T	C
# Lactase persistence
rs4988235	2	136608646	A	A
# Alcohol flush (normal)
rs671	12	112241766	G	G
# Caffeine metabolism - Slow
rs762551	15	75041917	A	C
# Bitter taste
rs713598	7	141673345	C	G
# Eye color - Blue
rs12913832	15	28365618	G	G
# Skin pigmentation
rs1426654	15	48426484	A	A
rs16891982	5	33951693	G	G
# Celiac risk
rs2187668	6	32713862	T	T
# Type 2 Diabetes PRS markers
rs7903146	10	114758349	T	C
rs1801282	3	12393125	C	C
rs13266634	8	118184783	C	T
# CAD PRS markers
rs1333049	9	22125503	C	G
rs10757274	9	22124477	A	G
rs2383206	9	22125347	G	A
# Obesity
rs9939609	16	53820527	T	A
# Vitamin D
rs2282679	4	72608383	T	G
# BDNF
rs6265	11	27679916	C	T
# Clock genes
rs1801260	4	56299829	A	G
# HLA-B*5701 proxy (abacavir)
rs2395029	6	31548161	T	T
# CF carrier (heterozygous)
rs75527207	7	117559590	G	A
# Hemochromatosis
rs1800562	6	26093141	G	G
rs1799945	6	26091179	C	G
# Age-related macular degeneration
rs1061170	1	196642233	T	C
rs10490924	10	124214448	G	T
# Muscle composition
rs1815739	11	66560624	C	T
# Tendon injury risk
rs12722	9	117243839	C	T
# Longevity markers
rs2802292	6	108979939	G	T
# Ancestry informative markers
rs3827760	2	109513601	A	A
rs1042602	11	89011046	C	A
"""

SYNTHETIC_GENOME_AFRICAN = """# Synthetic Test Genome - African Ancestry
# Generated for software testing - NOT REAL HUMAN DATA
rsid	chromosome	position	allele1	allele2
# APOE - E3/E3 (average risk)
rs429358	19	44908684	T	T
rs7412	19	44908822	C	C
# Factor V Leiden - Normal (rare in African ancestry)
rs6025	1	169519049	C	C
# Sickle cell carrier (heterozygous HbAS)
rs334	11	5227002	A	T
# G6PD deficiency variant
rs1050828	X	154535277	C	T
# Duffy antigen negative (malaria protection)
rs2814778	1	159174683	C	C
# MTHFR - Normal
rs1801133	1	11856378	G	G
# Alpha thalassemia marker
rs41464951	16	223323	G	A
# CYP2D6 - Ultrarapid
rs3892097	22	42526694	C	C
# Lactase - Non-persistent
rs4988235	2	136608646	G	G
# Alcohol flush - Normal
rs671	12	112241766	G	G
# Skin pigmentation
rs1426654	15	48426484	G	G
rs16891982	5	33951693	C	C
# Eye color
rs12913832	15	28365618	A	A
# Vitamin D binding
rs2282679	4	72608383	A	A
# COMT
rs4680	22	19951271	A	G
# Warfarin - Normal sensitivity
rs9923231	16	31107689	C	C
# Type 2 Diabetes markers
rs7903146	10	114758349	T	T
# CAD markers
rs1333049	9	22125503	C	C
# Ancestry informative
rs3827760	2	109513601	G	G
rs1042602	11	89011046	C	C
# Beta globin - carrier status shown
# Hemochromatosis - normal
rs1800562	6	26093141	G	G
"""

SYNTHETIC_GENOME_ASIAN = """# Synthetic Test Genome - East Asian Ancestry
# Generated for software testing - NOT REAL HUMAN DATA
rsid	chromosome	position	allele1	allele2
# APOE - E3/E3
rs429358	19	44908684	T	T
rs7412	19	44908822	C	C
# Alcohol flush - ALDH2*2 (Asian flush)
rs671	12	112241766	G	A
# HLA-B*1502 proxy (carbamazepine SJS risk - higher in Han Chinese)
rs2844682	6	31377677	A	G
# ADH1B - Fast metabolizer (common in East Asian)
rs1229984	4	100239319	T	C
# MTHFR - Heterozygous
rs1801133	1	11856378	A	G
# CYP2C19 - Poor metabolizer (higher frequency in Asian)
rs4244285	10	96541616	A	A
rs4986893	10	96540410	G	A
# Dry earwax / reduced body odor
rs17822931	16	48258198	T	T
# Lactase - Non-persistent
rs4988235	2	136608646	G	G
# Skin pigmentation
rs1426654	15	48426484	G	A
rs16891982	5	33951693	G	C
# Eye color - Brown
rs12913832	15	28365618	A	A
# COMT
rs4680	22	19951271	G	A
# Hair thickness (EDAR)
rs3827760	2	109513601	A	A
# Warfarin - Sensitive
rs9923231	16	31107689	T	C
rs1799853	10	96702047	C	C
# Type 2 Diabetes
rs7903146	10	114758349	C	C
rs1801282	3	12393125	C	G
# CAD
rs1333049	9	22125503	G	G
# Factor V Leiden - Normal
rs6025	1	169519049	C	C
# Ancestry informative
rs1042602	11	89011046	C	C
"""

# High-risk scenario for testing critical alerts
SYNTHETIC_GENOME_HIGH_RISK = """# Synthetic Test Genome - High Risk Scenario
# Generated for software testing - NOT REAL HUMAN DATA
# This represents WORST-CASE scenarios for testing alert systems
rsid	chromosome	position	allele1	allele2
# APOE - E4/E4 (highest Alzheimer's risk)
rs429358	19	44908684	C	C
rs7412	19	44908822	C	C
# Factor V Leiden - HETEROZYGOUS (VTE risk)
rs6025	1	169519049	C	A
# Prothrombin - HETEROZYGOUS (VTE risk)
rs1799963	11	46761055	G	A
# DPYD - HETEROZYGOUS (5-FU toxicity risk - CRITICAL)
rs3918290	1	97915614	C	T
# TPMT - HETEROZYGOUS (thiopurine toxicity)
rs1800460	6	18130918	C	T
# HLA-B*5701 positive (abacavir hypersensitivity)
rs2395029	6	31548161	G	T
# CYP2C19 - Poor metabolizer
rs4244285	10	96541616	A	A
# SLCO1B1 - Reduced function
rs4149056	12	21331549	C	C
# BRCA1 proxy region (breast cancer risk - elevated)
rs799917	17	43091983	C	T
# BRCA2 proxy region
rs144848	13	32929387	T	T
# MTHFR - Compound heterozygous
rs1801133	1	11856378	A	A
rs1801131	1	11854476	G	G
# Hemochromatosis - Compound heterozygous
rs1800562	6	26093141	G	A
rs1799945	6	26091179	C	G
# Celiac - High risk
rs2187668	6	32713862	T	T
# Alpha-1 antitrypsin deficiency - heterozygous
rs28929474	14	94378610	C	T
# Long QT syndrome marker
rs12143842	1	237778923	T	T
# Type 2 Diabetes - Multiple risk alleles
rs7903146	10	114758349	T	T
rs1801282	3	12393125	G	G
# CAD - High genetic risk
rs1333049	9	22125503	C	C
rs10757274	9	22124477	G	G
# AMD - High risk
rs1061170	1	196642233	C	C
rs10490924	10	124214448	T	T
# COMT
rs4680	22	19951271	A	A
# Warfarin super-sensitive
rs9923231	16	31107689	T	T
rs1799853	10	96702047	T	T
rs1057910	10	96741053	A	C
"""

# Carrier status testing - multiple recessive carriers
SYNTHETIC_GENOME_CARRIER = """# Synthetic Test Genome - Multiple Carrier Status
# Generated for software testing - NOT REAL HUMAN DATA
rsid	chromosome	position	allele1	allele2
# CF carrier - deltaF508 heterozygous
rs75527207	7	117559590	G	A
rs113993960	7	117587811	TCTT	T
# Sickle cell carrier
rs334	11	5227002	A	T
# Tay-Sachs carrier proxy
rs28940871	15	72638892	C	T
# Gaucher carrier proxy
rs76763715	1	155205634	T	C
# PKU carrier proxy
rs62516101	12	103240210	G	A
# SMA carrier proxy
rs1454515571	5	70049523	C	T
# Hemochromatosis carrier
rs1800562	6	26093141	G	A
# Beta thalassemia carrier proxy
rs33950507	11	5225670	G	A
# Bloom syndrome carrier
rs113993959	15	91355081	T	C
# Canavan carrier
rs28940279	17	3485410	C	A
# Familial Mediterranean Fever carrier
rs61752717	16	3299468	C	T
# Usher syndrome carrier
rs111033304	11	17548434	T	C
# Normal markers
rs429358	19	44908684	T	T
rs7412	19	44908822	C	C
rs6025	1	169519049	C	C
rs1801133	1	11856378	G	G
rs4680	22	19951271	A	G
"""

# VCF format test data
SYNTHETIC_VCF = """##fileformat=VCFv4.2
##source=SyntheticTestData
##reference=GRCh38
##INFO=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
19	44908684	rs429358	T	C	99	PASS	DP=50	GT:GQ:DP	0/1:99:50
19	44908822	rs7412	C	T	99	PASS	DP=48	GT:GQ:DP	0/0:99:48
1	169519049	rs6025	G	A	99	PASS	DP=45	GT:GQ:DP	0/0:99:45
1	11856378	rs1801133	C	T	99	PASS	DP=52	GT:GQ:DP	0/1:99:52
22	19951271	rs4680	G	A	99	PASS	DP=60	GT:GQ:DP	1/1:99:60
10	96541616	rs4244285	G	A	99	PASS	DP=55	GT:GQ:DP	0/1:99:55
"""

# Multi-sample VCF for edge case testing
SYNTHETIC_VCF_MULTISAMPLE = """##fileformat=VCFv4.2
##source=SyntheticTestData
##reference=GRCh38
##INFO=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE1	SAMPLE2	SAMPLE3
19	44908684	rs429358	T	C	99	PASS	DP=150	GT:GQ	0/0:99	0/1:99	1/1:99
19	44908822	rs7412	C	T	99	PASS	DP=148	GT:GQ	0/0:99	0/0:99	0/1:99
1	169519049	rs6025	G	A	99	PASS	DP=145	GT:GQ	0/0:99	0/1:99	0/0:99
1	11856378	rs1801133	C	T	99	PASS	DP=152	GT:GQ	0/1:99	1/1:99	0/0:99
22	19951271	rs4680	G	A	99	PASS	DP=160	GT:GQ	0/0:99	0/1:99	1/1:99
"""

# Edge cases - missing data, unusual genotypes
SYNTHETIC_GENOME_EDGE_CASES = """# Synthetic Test Genome - Edge Cases
# Testing unusual inputs and missing data handling
rsid	chromosome	position	allele1	allele2
rs429358	19	44908684	T	-
rs7412	19	44908822	C	C
rs6025	1	169519049	--	--
rs1801133	1	11856378	A	G
invalid_rsid	1	100	A	G
rs4680	22	19951271	G	G
rs762551	15	75041917	00	00
rs9939609	16	53820527	T	T
rs12913832	15	28365618	AG	
rs4988235	2	136608646	A	A
"""

# Expected results for validation
EXPECTED_RESULTS = {
    "european": {
        "apoe": "ε3/ε4",
        "apoe_risk": "elevated",
        "factor_v": "normal",
        "mthfr_c677t": "heterozygous",
        "cyp2c19": "poor_metabolizer",
        "cf_carrier": True,
        "lactase_persistent": True
    },
    "african": {
        "apoe": "ε3/ε3",
        "apoe_risk": "average",
        "sickle_carrier": True,
        "lactase_persistent": False
    },
    "asian": {
        "apoe": "ε3/ε3",
        "alcohol_flush": True,
        "cyp2c19": "poor_metabolizer",
        "dry_earwax": True
    },
    "high_risk": {
        "apoe": "ε4/ε4",
        "apoe_risk": "high",
        "factor_v": "heterozygous",
        "dpyd_risk": True,
        "critical_alerts_expected": 3
    }
}
