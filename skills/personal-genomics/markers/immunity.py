"""
Immunity & HLA Markers
Source: GWAS, Literature

Genetic variants affecting immune function, autoimmunity, and infection susceptibility.
"""

IMMUNITY_MARKERS = {
    # =========================================================================
    # HLA - Drug Hypersensitivity (Critical)
    # =========================================================================
    "rs2395029": {
        "gene": "HLA-B*5701",
        "variant": "Tag SNP for HLA-B*5701",
        "risk_allele": "G",
        "condition": "Abacavir hypersensitivity",
        "evidence": "strong",
        "clinical_importance": "critical",
        "actionable": {
            "priority": "critical",
            "recommendations": [
                "ABACAVIR CONTRAINDICATED if positive",
                "Hypersensitivity can be fatal",
                "Standard of care to test before prescribing"
            ]
        }
    },
    "rs3909184": {
        "gene": "HLA-B*1502",
        "variant": "Tag SNP",
        "risk_allele": "A",
        "condition": "Carbamazepine-induced SJS/TEN",
        "populations": ["East Asian", "South Asian"],
        "evidence": "strong",
        "clinical_importance": "critical",
        "actionable": {
            "priority": "critical",
            "recommendations": [
                "Test before carbamazepine in Asian ancestry",
                "Stevens-Johnson Syndrome can be fatal",
                "Use alternative anticonvulsants if positive"
            ]
        }
    },
    "rs1061235": {
        "gene": "HLA-A*3101",
        "variant": "Tag SNP",
        "risk_allele": "A",
        "condition": "Carbamazepine DRESS syndrome",
        "populations": ["European", "Japanese"],
        "evidence": "strong"
    },
    "rs2844682": {
        "gene": "HLA-B*5801",
        "variant": "Tag SNP",
        "risk_allele": "T",
        "condition": "Allopurinol hypersensitivity",
        "populations": ["Asian", "African"],
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "Consider testing before allopurinol in high-risk populations",
                "Start with low dose if prescribed",
                "Watch for skin reactions"
            ]
        }
    },

    # =========================================================================
    # HLA - Autoimmune Disease Risk
    # =========================================================================
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "variant": "DQA1*05/DQB1*02",
        "risk_allele": "T",
        "condition": "Celiac disease",
        "or_per_allele": 7.0,
        "evidence": "strong",
        "note": "~95% of celiacs have DQ2 or DQ8",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "DQ2/DQ8 negative essentially rules out celiac",
                "If positive + symptoms, get tTG-IgA test",
                "Do NOT start gluten-free before testing"
            ]
        }
    },
    "rs7454108": {
        "gene": "HLA-DQ8",
        "variant": "DQB1*0302",
        "risk_allele": "C",
        "condition": "Celiac disease, Type 1 diabetes",
        "evidence": "strong"
    },
    "rs9273363": {
        "gene": "HLA-DQB1",
        "risk_allele": "C",
        "condition": "Type 1 diabetes",
        "evidence": "strong"
    },
    "rs2395185": {
        "gene": "HLA-DRA",
        "risk_allele": "G",
        "condition": "Multiple sclerosis",
        "evidence": "strong"
    },
    "rs3129882": {
        "gene": "HLA-DRB1",
        "risk_allele": "A",
        "condition": "Rheumatoid arthritis",
        "evidence": "strong"
    },
    "rs6457617": {
        "gene": "HLA-DQB1",
        "risk_allele": "T",
        "condition": "Rheumatoid arthritis",
        "evidence": "strong"
    },
    "rs9275596": {
        "gene": "HLA-DQB1",
        "risk_allele": "C",
        "condition": "Systemic lupus erythematosus",
        "evidence": "strong"
    },

    # =========================================================================
    # Autoimmune - Non-HLA
    # =========================================================================
    "rs2476601": {
        "gene": "PTPN22",
        "variant": "R620W",
        "risk_allele": "A",
        "condition": "Multiple autoimmune diseases",
        "or_per_allele": 1.7,
        "evidence": "strong",
        "note": "Increases risk of T1D, RA, lupus, Graves, vitiligo",
        "mechanisms": ["T cell activation threshold"]
    },
    "rs3087243": {
        "gene": "CTLA4",
        "variant": "+49A>G",
        "risk_allele": "G",
        "condition": "Autoimmune thyroid, T1D",
        "evidence": "strong",
        "mechanisms": ["T cell inhibition checkpoint"]
    },
    "rs231775": {
        "gene": "CTLA4",
        "risk_allele": "G",
        "condition": "Graves disease, Hashimoto's"
    },
    "rs11209026": {
        "gene": "IL23R",
        "variant": "R381Q",
        "risk_allele": "A",
        "condition": "IBD, psoriasis (PROTECTIVE)",
        "or_per_allele": 0.45,
        "evidence": "strong",
        "note": "Rare protective variant - A allele reduces IBD risk"
    },
    "rs10889677": {
        "gene": "IL23R",
        "risk_allele": "A",
        "condition": "Crohn's disease, ankylosing spondylitis"
    },

    # =========================================================================
    # Infection Susceptibility
    # =========================================================================
    "rs334": {
        "gene": "HBB",
        "variant": "Sickle cell trait (HbS)",
        "effect_allele": "T",
        "condition": "Malaria resistance",
        "note": "Heterozygotes protected against severe malaria",
        "evidence": "strong"
    },
    "rs8176719": {
        "gene": "ABO",
        "variant": "Blood type O",
        "effect_allele": "del",
        "conditions": {
            "malaria": "O type: some protection",
            "norovirus": "O type: increased susceptibility",
            "cholera": "O type: increased severity"
        },
        "note": "Blood type affects many infection risks"
    },
    "rs601338": {
        "gene": "FUT2",
        "variant": "Secretor status",
        "effect_allele": "A",
        "condition": "Norovirus susceptibility",
        "note": "Non-secretors (AA) resistant to many norovirus strains",
        "evidence": "strong",
        "actionable": {
            "priority": "informational",
            "note": "Non-secretors less likely to get norovirus (stomach flu)"
        }
    },
    "rs12979860": {
        "gene": "IFNL3/IL28B",
        "variant": "Interferon lambda",
        "effect_allele": "C",
        "condition": "Hepatitis C clearance",
        "note": "CC: better spontaneous clearance and treatment response",
        "evidence": "strong"
    },
    "rs8099917": {
        "gene": "IFNL3",
        "risk_allele": "T",
        "condition": "Hepatitis C treatment response"
    },

    # =========================================================================
    # Innate Immunity
    # =========================================================================
    "rs2066844": {
        "gene": "NOD2",
        "variant": "R702W",
        "risk_allele": "T",
        "condition": "Crohn's disease",
        "or_per_allele": 2.4,
        "evidence": "strong",
        "mechanisms": ["bacterial sensing in gut"]
    },
    "rs2066845": {
        "gene": "NOD2",
        "variant": "G908R",
        "risk_allele": "C",
        "condition": "Crohn's disease",
        "or_per_allele": 2.4
    },
    "rs2066847": {
        "gene": "NOD2",
        "variant": "L1007fs",
        "risk_allele": "C",
        "condition": "Crohn's disease",
        "or_per_allele": 4.0,
        "note": "Strongest Crohn's risk variant"
    },
    "rs4986790": {
        "gene": "TLR4",
        "variant": "D299G",
        "risk_allele": "G",
        "condition": "Gram-negative bacterial infections",
        "mechanisms": ["LPS sensing"]
    },
    "rs5743708": {
        "gene": "TLR2",
        "variant": "R753Q",
        "risk_allele": "A",
        "condition": "Tuberculosis susceptibility"
    },

    # =========================================================================
    # Complement System
    # =========================================================================
    "rs1061170": {
        "gene": "CFH",
        "variant": "Y402H",
        "risk_allele": "C",
        "condition": "AMD, atypical HUS",
        "evidence": "strong",
        "mechanisms": ["complement regulation"]
    },
    "rs547154": {
        "gene": "C2/CFB",
        "risk_allele": "A",
        "condition": "AMD (protective)"
    },

    # =========================================================================
    # Inflammatory Response
    # =========================================================================
    "rs1800629": {
        "gene": "TNF",
        "variant": "-308 G>A",
        "risk_allele": "A",
        "condition": "Various inflammatory conditions",
        "note": "A allele: higher TNF-alpha production",
        "evidence": "moderate"
    },
    "rs1800795": {
        "gene": "IL6",
        "variant": "-174 G>C",
        "risk_allele": "G",
        "condition": "Inflammatory response",
        "note": "GG: higher IL-6 production"
    },
    "rs1800896": {
        "gene": "IL10",
        "variant": "-1082 A>G",
        "risk_allele": "A",
        "condition": "Inflammatory/autoimmune",
        "note": "Low IL-10 producers may have more inflammation"
    },
    "rs20417": {
        "gene": "PTGS2 (COX-2)",
        "variant": "-765 G>C",
        "risk_allele": "C",
        "condition": "Inflammatory response",
        "note": "Affects NSAID efficacy"
    },

    # =========================================================================
    # COVID-19 Risk (Recent discoveries)
    # =========================================================================
    "rs11385942": {
        "gene": "3p21.31 (SLC6A20)",
        "risk_allele": "A",
        "condition": "Severe COVID-19",
        "or_per_allele": 1.77,
        "evidence": "strong",
        "note": "Strongest genetic risk factor for severe COVID"
    },
    "rs657152": {
        "gene": "ABO",
        "risk_allele": "A",
        "condition": "COVID-19 susceptibility",
        "note": "Blood type A: slightly higher risk. Type O: slightly protective"
    },
    "rs2236757": {
        "gene": "IFNAR2",
        "risk_allele": "A",
        "condition": "Severe COVID-19",
        "mechanisms": ["interferon signaling"]
    },

    # =========================================================================
    # Immunodeficiency
    # =========================================================================
    "rs1800872": {
        "gene": "IL10",
        "risk_allele": "T",
        "condition": "Recurrent infections",
        "note": "Low IL-10: altered immune regulation"
    },
    "rs1800871": {
        "gene": "IL10",
        "variant": "-819 C>T",
        "risk_allele": "A",
        "condition": "Immune regulation"
    },

    # =========================================================================
    # Allergy / Atopy
    # =========================================================================
    "rs7216389": {
        "gene": "ORMDL3/GSDMB",
        "risk_allele": "T",
        "condition": "Asthma",
        "evidence": "strong"
    },
    "rs2305480": {
        "gene": "GSDMB",
        "risk_allele": "G",
        "condition": "Asthma"
    },
    "rs1295686": {
        "gene": "IL13",
        "risk_allele": "A",
        "condition": "Asthma, atopic dermatitis"
    },
    "rs20541": {
        "gene": "IL13",
        "variant": "R130Q",
        "risk_allele": "A",
        "condition": "Allergic diseases, asthma"
    },
    "rs1801275": {
        "gene": "IL4R",
        "variant": "Q576R",
        "risk_allele": "G",
        "condition": "Atopy, asthma"
    },
    "rs2243250": {
        "gene": "IL4",
        "variant": "-589 C>T",
        "risk_allele": "T",
        "condition": "Allergic rhinitis, asthma"
    },
}

# HLA quick reference for agents
HLA_DRUG_ALERTS = {
    "HLA-B*5701": {
        "drugs": ["abacavir"],
        "reaction": "Hypersensitivity syndrome",
        "action": "CONTRAINDICATED",
        "populations": "All"
    },
    "HLA-B*1502": {
        "drugs": ["carbamazepine", "oxcarbazepine", "phenytoin"],
        "reaction": "Stevens-Johnson Syndrome / TEN",
        "action": "CONTRAINDICATED",
        "populations": "Asian ancestry"
    },
    "HLA-B*5801": {
        "drugs": ["allopurinol"],
        "reaction": "DRESS, SJS/TEN",
        "action": "Consider testing in Asians, Africans",
        "populations": "Asian, African"
    },
    "HLA-A*3101": {
        "drugs": ["carbamazepine"],
        "reaction": "DRESS, maculopapular eruption",
        "action": "Consider testing",
        "populations": "European, Japanese"
    }
}
