"""
Sample genetic data for testing.
Uses synthetic data with known genotypes.
"""

SAMPLE_DNA_DATA = """# Test genetic data
# This is synthetic data for testing purposes only
rsid	chromosome	position	allele1	allele2
rs1801133	1	11856378	A	G
rs1801131	1	11854476	T	G
rs4680	22	19951271	G	G
rs762551	15	75041917	A	C
rs7903146	10	114758349	C	C
rs9939609	16	53820527	T	T
rs6025	1	169519049	C	C
rs1799963	11	46761055	G	G
rs1800562	6	26093141	G	G
rs1061170	1	196642233	T	C
rs12913832	15	28365618	A	G
rs4988235	2	136608646	A	A
rs17822931	16	48258198	T	C
rs1426654	15	48426484	A	A
rs16891982	5	33951693	G	G
rs7412	19	45412079	C	C
rs9923231	16	31107689	T	T
rs4149056	12	21331549	T	T
rs2282679	4	72608383	T	G
rs4880	6	160113872	A	A
"""

# Expected results for sample data
EXPECTED_MTHFR_C677T = "AG"  # Heterozygous
EXPECTED_COMT = "GG"  # Warrior genotype
EXPECTED_LACTASE = "AA"  # Lactase persistent
EXPECTED_EYE_COLOR = "AG"  # Green/hazel possible
EXPECTED_WARFARIN_VKORC1 = "TT"  # Sensitive
