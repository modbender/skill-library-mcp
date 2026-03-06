"""
Longevity & Aging Markers
Source: GWAS, Centenarian studies, Literature

Genetic variants associated with lifespan and healthy aging.
"""

LONGEVITY_MARKERS = {
    # =========================================================================
    # APOE - Strongest longevity association
    # =========================================================================
    "rs429358": {
        "gene": "APOE",
        "variant": "ε4 determinant",
        "effect_allele": "C",
        "longevity_effect": "negative",
        "or_longevity": 0.53,
        "evidence": "strong",
        "note": "ε4 reduces longevity; ε2 (rs7412 T) increases it",
        "mechanisms": ["Alzheimer's risk", "cardiovascular disease", "lipid metabolism"]
    },
    "rs7412": {
        "gene": "APOE",
        "variant": "ε2 determinant", 
        "effect_allele": "T",
        "longevity_effect": "positive",
        "note": "TT = ε2/ε2: associated with exceptional longevity"
    },

    # =========================================================================
    # FOXO3 - Replicated in multiple populations
    # =========================================================================
    "rs2802292": {
        "gene": "FOXO3",
        "variant": "Longevity variant",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "or_longevity": 1.26,
        "evidence": "strong",
        "note": "Replicated in Japanese, German, Italian, Chinese centenarians",
        "mechanisms": ["insulin/IGF-1 signaling", "stress resistance", "autophagy"],
        "actionable": {
            "priority": "informational",
            "note": "G allele associated with reaching 100. Lifestyle still dominant factor."
        }
    },
    "rs2764264": {
        "gene": "FOXO3",
        "effect_allele": "C",
        "longevity_effect": "positive"
    },
    "rs13217795": {
        "gene": "FOXO3",
        "effect_allele": "T",
        "longevity_effect": "positive"
    },

    # =========================================================================
    # TERT/TERC - Telomere maintenance
    # =========================================================================
    "rs2736100": {
        "gene": "TERT",
        "variant": "Telomerase",
        "effect_allele": "C",
        "longevity_effect": "positive",
        "evidence": "moderate",
        "mechanisms": ["telomere length maintenance"],
        "note": "Also associated with some cancer risks (complex trade-off)"
    },
    "rs10936599": {
        "gene": "TERC",
        "variant": "Telomerase RNA",
        "effect_allele": "C",
        "longevity_effect": "positive",
        "evidence": "moderate"
    },
    "rs7726159": {
        "gene": "TERT",
        "effect_allele": "A",
        "longevity_effect": "positive"
    },

    # =========================================================================
    # CETP - Lipid metabolism / HDL
    # =========================================================================
    "rs5882": {
        "gene": "CETP",
        "variant": "I405V",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "evidence": "moderate",
        "mechanisms": ["higher HDL cholesterol", "larger HDL particles"],
        "note": "Associated with longevity in Ashkenazi Jewish centenarians"
    },
    "rs708272": {
        "gene": "CETP",
        "variant": "TaqIB",
        "effect_allele": "A",
        "longevity_effect": "positive",
        "note": "B2 allele: lower CETP, higher HDL"
    },

    # =========================================================================
    # IGF1/GH pathway
    # =========================================================================
    "rs2229765": {
        "gene": "IGF1R",
        "variant": "Insulin-like growth factor receptor",
        "effect_allele": "A",
        "longevity_effect": "positive",
        "evidence": "moderate",
        "note": "Reduced IGF-1 signaling associated with longevity in model organisms"
    },
    "rs35767": {
        "gene": "IGF1",
        "effect_allele": "G",
        "longevity_effect": "variable",
        "note": "Complex - affects both growth and aging"
    },

    # =========================================================================
    # Inflammation / IL6
    # =========================================================================
    "rs1800795": {
        "gene": "IL6",
        "variant": "-174 G>C",
        "effect_allele": "G",
        "longevity_effect": "context_dependent",
        "evidence": "moderate",
        "note": "GG: higher IL-6, but some longevity association in certain populations"
    },

    # =========================================================================
    # Antioxidant defense
    # =========================================================================
    "rs4880": {
        "gene": "SOD2",
        "variant": "Ala16Val",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "mechanisms": ["mitochondrial antioxidant defense"],
        "note": "Val allele (G): better mitochondrial import, better ROS defense"
    },
    "rs1001179": {
        "gene": "CAT",
        "variant": "Catalase",
        "effect_allele": "T",
        "mechanisms": ["hydrogen peroxide detoxification"]
    },

    # =========================================================================
    # DNA repair
    # =========================================================================
    "rs1052133": {
        "gene": "OGG1",
        "variant": "Ser326Cys",
        "effect_allele": "G",
        "mechanisms": ["oxidative DNA damage repair"],
        "note": "Ser/Ser may have better repair capacity"
    },
    "rs25487": {
        "gene": "XRCC1",
        "variant": "Arg399Gln",
        "effect_allele": "A",
        "mechanisms": ["base excision repair"]
    },
    "rs1799793": {
        "gene": "ERCC2/XPD",
        "variant": "Asp312Asn",
        "effect_allele": "A",
        "mechanisms": ["nucleotide excision repair"]
    },

    # =========================================================================
    # Cardiovascular protection
    # =========================================================================
    "rs1333049": {
        "gene": "9p21.3",
        "variant": "CAD risk locus",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "note": "G allele protective against heart disease"
    },
    "rs10757278": {
        "gene": "9p21.3",
        "effect_allele": "A",
        "longevity_effect": "positive"
    },

    # =========================================================================
    # Klotho - Anti-aging hormone
    # =========================================================================
    "rs9536314": {
        "gene": "KL (Klotho)",
        "variant": "F352V (KL-VS)",
        "effect_allele": "G",
        "longevity_effect": "complex",
        "evidence": "moderate",
        "note": "Heterozygotes may have longevity advantage (overdominance)",
        "mechanisms": ["mineral metabolism", "insulin signaling", "cognition"]
    },

    # =========================================================================
    # mTOR pathway
    # =========================================================================
    "rs1130214": {
        "gene": "AKT1",
        "effect_allele": "G",
        "mechanisms": ["insulin/mTOR signaling"],
        "note": "mTOR inhibition extends lifespan in model organisms"
    },

    # =========================================================================
    # Adiponectin
    # =========================================================================
    "rs2241766": {
        "gene": "ADIPOQ",
        "variant": "+45T>G",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "mechanisms": ["insulin sensitivity", "anti-inflammatory"],
        "note": "Higher adiponectin associated with longevity"
    },
    "rs1501299": {
        "gene": "ADIPOQ",
        "variant": "+276G>T",
        "effect_allele": "T",
        "longevity_effect": "positive"
    },

    # =========================================================================
    # Sirtuins
    # =========================================================================
    "rs7069102": {
        "gene": "SIRT3",
        "effect_allele": "C",
        "mechanisms": ["mitochondrial function", "metabolic regulation"],
        "note": "Sirtuins are key longevity regulators"
    },
    "rs2273773": {
        "gene": "SIRT1",
        "effect_allele": "C",
        "mechanisms": ["caloric restriction response", "DNA repair"]
    },

    # =========================================================================
    # Cholesterol / Lipids
    # =========================================================================
    "rs688": {
        "gene": "LDLR",
        "variant": "LDL receptor",
        "effect_allele": "T",
        "note": "Affects LDL clearance"
    },
    "rs693": {
        "gene": "APOB",
        "variant": "Apolipoprotein B",
        "effect_allele": "G",
        "note": "Affects LDL particle number"
    },

    # =========================================================================
    # Immune aging
    # =========================================================================
    "rs2069762": {
        "gene": "IL2",
        "effect_allele": "T",
        "mechanisms": ["immune function maintenance"]
    },
    "rs1800896": {
        "gene": "IL10",
        "variant": "-1082 A>G",
        "effect_allele": "G",
        "longevity_effect": "positive",
        "mechanisms": ["anti-inflammatory cytokine"],
        "note": "High IL-10 producers may have longevity advantage"
    },
}

# Summary for agents
LONGEVITY_GENE_SUMMARY = {
    "strong_evidence": ["APOE", "FOXO3"],
    "moderate_evidence": ["TERT", "TERC", "CETP", "IL6", "KL"],
    "emerging": ["SIRT1", "SIRT3", "ADIPOQ", "IGF1R"],
    "key_pathways": [
        "Insulin/IGF-1 signaling (FOXO3, IGF1R)",
        "Lipid metabolism (APOE, CETP)",
        "Telomere maintenance (TERT, TERC)",
        "Inflammation (IL6, IL10)",
        "Oxidative stress (SOD2, CAT)",
        "DNA repair (OGG1, XRCC1)"
    ],
    "note": "Genetics explains ~25% of lifespan variance. Lifestyle, environment, and luck matter more."
}
