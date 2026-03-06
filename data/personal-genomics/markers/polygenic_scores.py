"""
Polygenic Risk Score (PRS) Markers
Source: GWAS Catalog, PGS Catalog, Published literature

PRS combines many small-effect variants to estimate genetic liability.
These are the top-weighted SNPs from validated PRS models.

NOTE: Full PRS requires thousands of variants. These are the highest-impact
SNPs that provide meaningful signal from consumer genotyping arrays.
"""

# Conditions with validated PRS models
PRS_CONDITIONS = {
    "coronary_artery_disease": {
        "heritability": 0.48,
        "snp_count_full": 6630000,
        "snp_count_consumer": 50,
        "population_prevalence": 0.06,
        "clinical_utility": "high",
        "interventions": ["statins", "lifestyle", "BP control", "screening"]
    },
    "type_2_diabetes": {
        "heritability": 0.35,
        "snp_count_full": 403,
        "snp_count_consumer": 40,
        "population_prevalence": 0.10,
        "clinical_utility": "high",
        "interventions": ["metformin", "lifestyle", "weight loss", "screening"]
    },
    "breast_cancer": {
        "heritability": 0.31,
        "snp_count_full": 313,
        "snp_count_consumer": 35,
        "population_prevalence": 0.12,
        "clinical_utility": "moderate",
        "interventions": ["screening frequency", "risk-reducing surgery discussion"]
    },
    "prostate_cancer": {
        "heritability": 0.58,
        "snp_count_full": 269,
        "snp_count_consumer": 35,
        "population_prevalence": 0.13,
        "clinical_utility": "moderate",
        "interventions": ["PSA screening decisions", "active surveillance"]
    },
    "alzheimer_disease": {
        "heritability": 0.58,
        "snp_count_full": 38,
        "snp_count_consumer": 20,
        "population_prevalence": 0.10,
        "clinical_utility": "moderate",
        "interventions": ["lifestyle (exercise, cognitive engagement)", "risk awareness"]
    },
    "atrial_fibrillation": {
        "heritability": 0.62,
        "snp_count_full": 134,
        "snp_count_consumer": 25,
        "population_prevalence": 0.03,
        "clinical_utility": "moderate",
        "interventions": ["screening", "anticoagulation decisions"]
    },
    "inflammatory_bowel_disease": {
        "heritability": 0.75,
        "snp_count_full": 240,
        "snp_count_consumer": 30,
        "population_prevalence": 0.005,
        "clinical_utility": "moderate",
        "interventions": ["early diagnosis", "treatment selection"]
    },
    "schizophrenia": {
        "heritability": 0.80,
        "snp_count_full": 287,
        "snp_count_consumer": 25,
        "population_prevalence": 0.01,
        "clinical_utility": "research",
        "note": "Not recommended for individual prediction"
    },
    "major_depression": {
        "heritability": 0.37,
        "snp_count_full": 102,
        "snp_count_consumer": 20,
        "population_prevalence": 0.15,
        "clinical_utility": "low",
        "note": "Environment plays major role"
    },
    "obesity": {
        "heritability": 0.40,
        "snp_count_full": 941,
        "snp_count_consumer": 30,
        "population_prevalence": 0.40,
        "clinical_utility": "moderate",
        "interventions": ["lifestyle", "GLP-1 agonist consideration"]
    }
}

# PRS weights for major conditions
# Format: rsid -> {effect_allele, beta, condition}
# Beta values are log(OR) or effect sizes from largest GWAS meta-analyses
PRS_WEIGHTS = {
    # =========================================================================
    # CORONARY ARTERY DISEASE (CAD)
    # Source: CARDIoGRAMplusC4D, UK Biobank
    # =========================================================================
    "rs1333049": {"effect": "C", "beta": 0.29, "gene": "9p21.3", "condition": "cad"},
    "rs4977574": {"effect": "G", "beta": 0.25, "gene": "9p21.3", "condition": "cad"},
    "rs46522": {"effect": "T", "beta": 0.08, "gene": "UBE2Z", "condition": "cad"},
    "rs9818870": {"effect": "T", "beta": 0.07, "gene": "MRAS", "condition": "cad"},
    "rs2259816": {"effect": "A", "beta": 0.08, "gene": "HNF1A", "condition": "cad"},
    "rs11206510": {"effect": "T", "beta": 0.15, "gene": "PCSK9", "condition": "cad"},
    "rs17465637": {"effect": "A", "beta": 0.10, "gene": "MIA3", "condition": "cad"},
    "rs6725887": {"effect": "C", "beta": 0.14, "gene": "WDR12", "condition": "cad"},
    "rs9982601": {"effect": "T", "beta": 0.18, "gene": "6p24", "condition": "cad"},
    "rs1746048": {"effect": "C", "beta": 0.08, "gene": "CXCL12", "condition": "cad"},
    "rs12190287": {"effect": "C", "beta": 0.08, "gene": "TCF21", "condition": "cad"},
    "rs3798220": {"effect": "C", "beta": 0.47, "gene": "LPA", "condition": "cad"},
    "rs10455872": {"effect": "G", "beta": 0.40, "gene": "LPA", "condition": "cad"},
    "rs2048327": {"effect": "T", "beta": 0.06, "gene": "SLC22A3", "condition": "cad"},
    "rs12413409": {"effect": "G", "beta": 0.10, "gene": "CYP17A1", "condition": "cad"},
    "rs2246833": {"effect": "T", "beta": 0.07, "gene": "LIPA", "condition": "cad"},
    "rs2895811": {"effect": "C", "beta": 0.07, "gene": "HHIPL1", "condition": "cad"},
    "rs4773144": {"effect": "G", "beta": 0.07, "gene": "COL4A1/COL4A2", "condition": "cad"},
    "rs2023938": {"effect": "G", "beta": 0.10, "gene": "HDAC9", "condition": "cad"},
    "rs12526453": {"effect": "C", "beta": 0.08, "gene": "PHACTR1", "condition": "cad"},
    "rs17514846": {"effect": "A", "beta": 0.07, "gene": "FURIN", "condition": "cad"},
    "rs264": {"effect": "G", "beta": 0.08, "gene": "LPL", "condition": "cad"},
    "rs2954029": {"effect": "A", "beta": 0.06, "gene": "TRIB1", "condition": "cad"},
    "rs579459": {"effect": "C", "beta": 0.11, "gene": "ABO", "condition": "cad"},
    "rs515135": {"effect": "C", "beta": 0.12, "gene": "APOB", "condition": "cad"},
    "rs646776": {"effect": "T", "beta": 0.12, "gene": "SORT1", "condition": "cad"},

    # =========================================================================
    # TYPE 2 DIABETES (T2D)
    # Source: DIAGRAM Consortium
    # =========================================================================
    "rs7903146": {"effect": "T", "beta": 0.35, "gene": "TCF7L2", "condition": "t2d"},
    "rs12255372": {"effect": "T", "beta": 0.26, "gene": "TCF7L2", "condition": "t2d"},
    "rs13266634": {"effect": "C", "beta": 0.11, "gene": "SLC30A8", "condition": "t2d"},
    "rs10811661": {"effect": "T", "beta": 0.18, "gene": "CDKN2A/B", "condition": "t2d"},
    "rs8050136": {"effect": "A", "beta": 0.15, "gene": "FTO", "condition": "t2d"},
    "rs5219": {"effect": "T", "beta": 0.11, "gene": "KCNJ11", "condition": "t2d"},
    "rs1111875": {"effect": "C", "beta": 0.12, "gene": "HHEX", "condition": "t2d"},
    "rs7756992": {"effect": "G", "beta": 0.14, "gene": "CDKAL1", "condition": "t2d"},
    "rs10946398": {"effect": "C", "beta": 0.13, "gene": "CDKAL1", "condition": "t2d"},
    "rs4402960": {"effect": "T", "beta": 0.11, "gene": "IGF2BP2", "condition": "t2d"},
    "rs1801282": {"effect": "C", "beta": 0.14, "gene": "PPARG", "condition": "t2d"},
    "rs7578597": {"effect": "T", "beta": 0.11, "gene": "THADA", "condition": "t2d"},
    "rs10830963": {"effect": "G", "beta": 0.09, "gene": "MTNR1B", "condition": "t2d"},
    "rs2943641": {"effect": "C", "beta": 0.10, "gene": "IRS1", "condition": "t2d"},
    "rs1387153": {"effect": "T", "beta": 0.08, "gene": "MTNR1B", "condition": "t2d"},
    "rs17036101": {"effect": "G", "beta": 0.09, "gene": "SYN2", "condition": "t2d"},
    "rs4607103": {"effect": "C", "beta": 0.08, "gene": "ADAMTS9", "condition": "t2d"},
    "rs5015480": {"effect": "C", "beta": 0.09, "gene": "HHEX", "condition": "t2d"},
    "rs780094": {"effect": "C", "beta": 0.06, "gene": "GCKR", "condition": "t2d"},
    "rs2191349": {"effect": "T", "beta": 0.07, "gene": "DGKB", "condition": "t2d"},

    # =========================================================================
    # BREAST CANCER
    # Source: BCAC
    # =========================================================================
    "rs2981582": {"effect": "A", "beta": 0.26, "gene": "FGFR2", "condition": "breast_ca"},
    "rs3817198": {"effect": "C", "beta": 0.07, "gene": "LSP1", "condition": "breast_ca"},
    "rs889312": {"effect": "C", "beta": 0.13, "gene": "MAP3K1", "condition": "breast_ca"},
    "rs13281615": {"effect": "G", "beta": 0.08, "gene": "8q24", "condition": "breast_ca"},
    "rs3803662": {"effect": "A", "beta": 0.20, "gene": "TOX3", "condition": "breast_ca"},
    "rs13387042": {"effect": "A", "beta": 0.12, "gene": "2q35", "condition": "breast_ca"},
    "rs4784227": {"effect": "T", "beta": 0.25, "gene": "TOX3", "condition": "breast_ca"},
    "rs11249433": {"effect": "G", "beta": 0.10, "gene": "FCGR1B", "condition": "breast_ca"},
    "rs10941679": {"effect": "G", "beta": 0.12, "gene": "5p12", "condition": "breast_ca"},
    "rs2046210": {"effect": "A", "beta": 0.11, "gene": "ESR1", "condition": "breast_ca"},
    "rs999737": {"effect": "C", "beta": 0.08, "gene": "RAD51L1", "condition": "breast_ca"},
    "rs6504950": {"effect": "G", "beta": 0.06, "gene": "STXBP4", "condition": "breast_ca"},
    "rs2380205": {"effect": "C", "beta": 0.05, "gene": "10p15", "condition": "breast_ca"},
    "rs614367": {"effect": "T", "beta": 0.15, "gene": "11q13", "condition": "breast_ca"},
    "rs11780156": {"effect": "C", "beta": 0.11, "gene": "8q21", "condition": "breast_ca"},
    "rs720475": {"effect": "G", "beta": 0.08, "gene": "INHBB", "condition": "breast_ca"},

    # =========================================================================
    # PROSTATE CANCER
    # Source: PRACTICAL Consortium
    # =========================================================================
    "rs16901979": {"effect": "A", "beta": 0.59, "gene": "8q24", "condition": "prostate_ca"},
    "rs6983267": {"effect": "G", "beta": 0.21, "gene": "8q24", "condition": "prostate_ca"},
    "rs1447295": {"effect": "A", "beta": 0.32, "gene": "8q24", "condition": "prostate_ca"},
    "rs10993994": {"effect": "T", "beta": 0.25, "gene": "MSMB", "condition": "prostate_ca"},
    "rs17021918": {"effect": "C", "beta": 0.11, "gene": "4q22", "condition": "prostate_ca"},
    "rs10896449": {"effect": "G", "beta": 0.14, "gene": "11q13", "condition": "prostate_ca"},
    "rs7679673": {"effect": "C", "beta": 0.14, "gene": "TET2", "condition": "prostate_ca"},
    "rs2735839": {"effect": "G", "beta": 0.20, "gene": "KLK3", "condition": "prostate_ca"},
    "rs1859962": {"effect": "G", "beta": 0.17, "gene": "17q24", "condition": "prostate_ca"},
    "rs4430796": {"effect": "A", "beta": 0.16, "gene": "HNF1B", "condition": "prostate_ca"},
    "rs620861": {"effect": "G", "beta": 0.11, "gene": "22q13", "condition": "prostate_ca"},
    "rs11649743": {"effect": "A", "beta": 0.12, "gene": "HNF1B", "condition": "prostate_ca"},
    "rs7127900": {"effect": "A", "beta": 0.19, "gene": "11p15", "condition": "prostate_ca"},
    "rs12621278": {"effect": "A", "beta": 0.31, "gene": "2q31", "condition": "prostate_ca"},
    "rs2660753": {"effect": "T", "beta": 0.15, "gene": "3p12", "condition": "prostate_ca"},

    # =========================================================================
    # ALZHEIMER'S DISEASE
    # Source: IGAP
    # =========================================================================
    "rs429358": {"effect": "C", "beta": 1.20, "gene": "APOE", "condition": "alzheimer"},
    "rs7412": {"effect": "C", "beta": 0.50, "gene": "APOE", "condition": "alzheimer"},
    "rs6656401": {"effect": "A", "beta": 0.18, "gene": "CR1", "condition": "alzheimer"},
    "rs3764650": {"effect": "G", "beta": 0.13, "gene": "ABCA7", "condition": "alzheimer"},
    "rs744373": {"effect": "G", "beta": 0.15, "gene": "BIN1", "condition": "alzheimer"},
    "rs3851179": {"effect": "T", "beta": 0.14, "gene": "PICALM", "condition": "alzheimer"},
    "rs11136000": {"effect": "T", "beta": 0.12, "gene": "CLU", "condition": "alzheimer"},
    "rs610932": {"effect": "G", "beta": 0.08, "gene": "MS4A6A", "condition": "alzheimer"},
    "rs670139": {"effect": "T", "beta": 0.08, "gene": "MS4A4E", "condition": "alzheimer"},
    "rs3865444": {"effect": "A", "beta": 0.10, "gene": "CD33", "condition": "alzheimer"},
    "rs9349407": {"effect": "C", "beta": 0.11, "gene": "CD2AP", "condition": "alzheimer"},
    "rs11771145": {"effect": "A", "beta": 0.09, "gene": "EPHA1", "condition": "alzheimer"},
    "rs17125944": {"effect": "C", "beta": 0.15, "gene": "FERMT2", "condition": "alzheimer"},
    "rs10498633": {"effect": "T", "beta": 0.12, "gene": "SLC24A4", "condition": "alzheimer"},
    "rs28834970": {"effect": "C", "beta": 0.10, "gene": "PTK2B", "condition": "alzheimer"},

    # =========================================================================
    # ATRIAL FIBRILLATION
    # Source: AFGen Consortium
    # =========================================================================
    "rs2200733": {"effect": "T", "beta": 0.45, "gene": "PITX2", "condition": "afib"},
    "rs10033464": {"effect": "T", "beta": 0.22, "gene": "4q25", "condition": "afib"},
    "rs2106261": {"effect": "T", "beta": 0.13, "gene": "ZFHX3", "condition": "afib"},
    "rs6666258": {"effect": "G", "beta": 0.10, "gene": "KCNN3", "condition": "afib"},
    "rs10821415": {"effect": "C", "beta": 0.09, "gene": "KCNQ1", "condition": "afib"},
    "rs7164883": {"effect": "G", "beta": 0.12, "gene": "PRRX1", "condition": "afib"},
    "rs13376333": {"effect": "T", "beta": 0.14, "gene": "KCNN3", "condition": "afib"},
    "rs3807989": {"effect": "A", "beta": 0.11, "gene": "CAV1", "condition": "afib"},
    "rs2040862": {"effect": "T", "beta": 0.08, "gene": "NEURL", "condition": "afib"},
    "rs10824026": {"effect": "G", "beta": 0.10, "gene": "SYNPO2L", "condition": "afib"},
    "rs6817105": {"effect": "T", "beta": 0.42, "gene": "PITX2", "condition": "afib"},

    # =========================================================================
    # INFLAMMATORY BOWEL DISEASE (IBD)
    # Source: IIBDGC
    # =========================================================================
    "rs2066844": {"effect": "T", "beta": 0.50, "gene": "NOD2", "condition": "ibd"},
    "rs2066845": {"effect": "C", "beta": 0.40, "gene": "NOD2", "condition": "ibd"},
    "rs2066847": {"effect": "C", "beta": 0.75, "gene": "NOD2", "condition": "ibd"},
    "rs11209026": {"effect": "A", "beta": -0.45, "gene": "IL23R", "condition": "ibd"},  # Protective
    "rs2201841": {"effect": "T", "beta": 0.18, "gene": "IL23R", "condition": "ibd"},
    "rs17234657": {"effect": "G", "beta": 0.30, "gene": "5p13.1", "condition": "ibd"},
    "rs10883365": {"effect": "G", "beta": 0.12, "gene": "NKX2-3", "condition": "ibd"},
    "rs744166": {"effect": "A", "beta": 0.14, "gene": "STAT3", "condition": "ibd"},
    "rs3810936": {"effect": "C", "beta": 0.11, "gene": "TNFSF15", "condition": "ibd"},
    "rs2476601": {"effect": "A", "beta": 0.22, "gene": "PTPN22", "condition": "ibd"},
    "rs17293632": {"effect": "T", "beta": 0.16, "gene": "SMAD3", "condition": "ibd"},
    "rs11465804": {"effect": "G", "beta": 0.13, "gene": "IL23R", "condition": "ibd"},
    "rs7517847": {"effect": "T", "beta": 0.11, "gene": "IL23R", "condition": "ibd"},

    # =========================================================================
    # OBESITY (BMI)
    # Source: GIANT Consortium
    # =========================================================================
    "rs9939609": {"effect": "A", "beta": 0.39, "gene": "FTO", "condition": "obesity"},
    "rs17782313": {"effect": "C", "beta": 0.23, "gene": "MC4R", "condition": "obesity"},
    "rs1421085": {"effect": "C", "beta": 0.39, "gene": "FTO", "condition": "obesity"},
    "rs6548238": {"effect": "C", "beta": 0.17, "gene": "TMEM18", "condition": "obesity"},
    "rs10938397": {"effect": "G", "beta": 0.18, "gene": "GNPDA2", "condition": "obesity"},
    "rs2867125": {"effect": "C", "beta": 0.14, "gene": "TMEM18", "condition": "obesity"},
    "rs543874": {"effect": "G", "beta": 0.18, "gene": "SEC16B", "condition": "obesity"},
    "rs987237": {"effect": "A", "beta": 0.15, "gene": "TFAP2B", "condition": "obesity"},
    "rs7359397": {"effect": "T", "beta": 0.16, "gene": "SH2B1", "condition": "obesity"},
    "rs10767664": {"effect": "A", "beta": 0.19, "gene": "BDNF", "condition": "obesity"},
    "rs2241423": {"effect": "G", "beta": 0.13, "gene": "MAP2K5", "condition": "obesity"},
    "rs13107325": {"effect": "T", "beta": 0.19, "gene": "SLC39A8", "condition": "obesity"},
    "rs571312": {"effect": "A", "beta": 0.24, "gene": "MC4R", "condition": "obesity"},
    "rs2815752": {"effect": "A", "beta": 0.12, "gene": "NEGR1", "condition": "obesity"},
    "rs7138803": {"effect": "A", "beta": 0.12, "gene": "BCDIN3D", "condition": "obesity"},

    # =========================================================================
    # SCHIZOPHRENIA (Research only)
    # Source: PGC
    # =========================================================================
    "rs1625579": {"effect": "T", "beta": 0.16, "gene": "MIR137", "condition": "scz"},
    "rs2007044": {"effect": "G", "beta": 0.10, "gene": "CACNA1C", "condition": "scz"},
    "rs6704641": {"effect": "G", "beta": 0.08, "gene": "PCGEM1", "condition": "scz"},
    "rs7914558": {"effect": "G", "beta": 0.09, "gene": "CNNM2", "condition": "scz"},
    "rs17512836": {"effect": "C", "beta": 0.12, "gene": "TCF4", "condition": "scz"},
    "rs12966547": {"effect": "G", "beta": 0.08, "gene": "MHC", "condition": "scz"},

    # =========================================================================
    # MAJOR DEPRESSION
    # Source: PGC-MDD
    # =========================================================================
    "rs1545843": {"effect": "A", "beta": 0.04, "gene": "LHPP", "condition": "mdd"},
    "rs7044150": {"effect": "G", "beta": 0.04, "gene": "OLFM4", "condition": "mdd"},
    "rs2422321": {"effect": "T", "beta": 0.04, "gene": "RFWD2", "condition": "mdd"},
    "rs4543289": {"effect": "T", "beta": 0.04, "gene": "NEGR1", "condition": "mdd"},
    "rs301806": {"effect": "A", "beta": 0.05, "gene": "RERE", "condition": "mdd"},

    # =========================================================================
    # COLORECTAL CANCER
    # Source: GECCO
    # =========================================================================
    "rs6983267": {"effect": "G", "beta": 0.21, "gene": "8q24", "condition": "colorectal_ca"},
    "rs4779584": {"effect": "T", "beta": 0.18, "gene": "GREM1", "condition": "colorectal_ca"},
    "rs4939827": {"effect": "T", "beta": 0.18, "gene": "SMAD7", "condition": "colorectal_ca"},
    "rs10795668": {"effect": "G", "beta": 0.11, "gene": "10p14", "condition": "colorectal_ca"},
    "rs4444235": {"effect": "C", "beta": 0.11, "gene": "BMP4", "condition": "colorectal_ca"},
    "rs9929218": {"effect": "G", "beta": 0.11, "gene": "CDH1", "condition": "colorectal_ca"},
    "rs3802842": {"effect": "C", "beta": 0.11, "gene": "11q23.1", "condition": "colorectal_ca"},
    "rs10411210": {"effect": "T", "beta": 0.09, "gene": "RHPN2", "condition": "colorectal_ca"},
    "rs961253": {"effect": "A", "beta": 0.12, "gene": "20p12.3", "condition": "colorectal_ca"},
    "rs2423279": {"effect": "T", "beta": 0.10, "gene": "20p12.3", "condition": "colorectal_ca"},
}

def calculate_prs(genotypes: dict, condition: str) -> dict:
    """
    Calculate polygenic risk score for a condition.
    
    Args:
        genotypes: dict mapping rsid -> genotype string (e.g., "AG")
        condition: condition code (e.g., "cad", "t2d")
    
    Returns:
        dict with score, percentile estimate, and interpretation
    """
    condition_snps = {k: v for k, v in PRS_WEIGHTS.items() if v["condition"] == condition}
    
    score = 0
    snps_found = 0
    snps_missing = 0
    
    for rsid, info in condition_snps.items():
        geno = genotypes.get(rsid)
        if geno:
            snps_found += 1
            effect_allele = info["effect"]
            beta = info["beta"]
            
            # Count effect alleles (0, 1, or 2)
            effect_count = geno.count(effect_allele)
            score += effect_count * beta
        else:
            snps_missing += 1
    
    # Normalize to percentile (rough approximation)
    # This is simplified - real PRS would use population-specific distributions
    snp_coverage = snps_found / max(len(condition_snps), 1)
    
    # Convert raw score to approximate percentile
    # Assuming roughly normal distribution centered at 0
    import math
    try:
        z_score = score / math.sqrt(snps_found * 0.5) if snps_found > 5 else 0
        # Crude percentile approximation
        percentile = min(99, max(1, int(50 + z_score * 15)))
    except:
        percentile = 50
    
    # Risk interpretation
    if percentile >= 90:
        risk_category = "high"
        interpretation = "Top 10% genetic risk - consider enhanced screening/prevention"
    elif percentile >= 75:
        risk_category = "above_average"
        interpretation = "Above average genetic risk - standard prevention recommended"
    elif percentile >= 25:
        risk_category = "average"
        interpretation = "Average genetic risk"
    else:
        risk_category = "below_average"
        interpretation = "Below average genetic risk (still need standard screening)"
    
    return {
        "condition": condition,
        "raw_score": round(score, 3),
        "snps_analyzed": snps_found,
        "snps_missing": snps_missing,
        "coverage": round(snp_coverage, 2),
        "percentile_estimate": percentile,
        "risk_category": risk_category,
        "interpretation": interpretation,
        "confidence": "moderate" if snp_coverage > 0.7 else "low",
        "note": "Consumer arrays capture subset of full PRS. Clinical-grade testing recommended for medical decisions."
    }
