"""
Health Risk Markers (Non-Mendelian)
Source: GWAS Catalog, ClinVar, Literature

These are common variants that modify disease risk.
Most are NOT diagnostic but contribute to overall genetic liability.
"""

HEALTH_RISK_MARKERS = {
    # =========================================================================
    # CARDIOVASCULAR
    # =========================================================================
    "rs1333049": {
        "gene": "9p21.3",
        "name": "Coronary Artery Disease Risk",
        "risk_allele": "C",
        "or_per_allele": 1.29,
        "conditions": ["coronary artery disease", "myocardial infarction"],
        "evidence": "strong",
        "gwas_pvalue": "1e-100",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Cardiovascular risk factor optimization",
                "Consider coronary calcium scoring if multiple risk factors",
                "Lipid panel monitoring"
            ]
        }
    },
    "rs10757278": {
        "gene": "9p21.3",
        "name": "CAD/Aneurysm Risk",
        "risk_allele": "G",
        "or_per_allele": 1.25,
        "conditions": ["coronary artery disease", "abdominal aortic aneurysm"]
    },
    "rs3798220": {
        "gene": "LPA",
        "name": "Lipoprotein(a) High",
        "risk_allele": "C",
        "or_per_allele": 1.51,
        "conditions": ["coronary artery disease", "aortic stenosis"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Check Lp(a) level (only need to measure once)",
                "If elevated, aggressive LDL lowering",
                "PCSK9 inhibitors may help",
                "Niacin may reduce Lp(a)"
            ]
        }
    },
    "rs10455872": {
        "gene": "LPA",
        "name": "Lipoprotein(a) High",
        "risk_allele": "G",
        "or_per_allele": 1.70,
        "conditions": ["coronary artery disease", "aortic stenosis"]
    },
    "rs6025": {
        "gene": "F5",
        "name": "Factor V Leiden",
        "risk_allele": "A",
        "or_per_allele": 7.0,
        "conditions": ["deep vein thrombosis", "pulmonary embolism"],
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "Avoid estrogen-containing contraceptives",
                "VTE prophylaxis for surgery/immobility",
                "Medical alert for healthcare providers"
            ]
        }
    },
    "rs1799963": {
        "gene": "F2",
        "name": "Prothrombin G20210A",
        "risk_allele": "A",
        "or_per_allele": 2.8,
        "conditions": ["venous thromboembolism"]
    },
    "rs1801020": {
        "gene": "F12",
        "name": "Factor XII 46C>T",
        "risk_allele": "T",
        "conditions": ["prolonged aPTT (benign)", "NOT thrombosis"],
        "note": "Lab abnormality only, no clinical significance"
    },

    # =========================================================================
    # DIABETES
    # =========================================================================
    "rs7903146": {
        "gene": "TCF7L2",
        "name": "Type 2 Diabetes (Strongest)",
        "risk_allele": "T",
        "or_per_allele": 1.40,
        "conditions": ["type 2 diabetes"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Regular glucose/HbA1c monitoring",
                "Weight management",
                "Exercise (especially resistance training)",
                "Consider metformin if prediabetic"
            ]
        }
    },
    "rs5219": {
        "gene": "KCNJ11",
        "name": "K+ Channel - Diabetes",
        "risk_allele": "T",
        "or_per_allele": 1.15,
        "conditions": ["type 2 diabetes"],
        "note": "Also affects sulfonylurea response"
    },
    "rs1801282": {
        "gene": "PPARG",
        "name": "Pro12Ala",
        "risk_allele": "C",
        "or_per_allele": 1.14,
        "conditions": ["type 2 diabetes", "insulin resistance"]
    },
    "rs10830963": {
        "gene": "MTNR1B",
        "name": "Melatonin Receptor - Glucose",
        "risk_allele": "G",
        "or_per_allele": 1.09,
        "conditions": ["type 2 diabetes", "fasting glucose"],
        "note": "Night shift work may increase diabetes risk more with risk allele"
    },

    # =========================================================================
    # OBESITY
    # =========================================================================
    "rs9939609": {
        "gene": "FTO",
        "name": "Fat Mass & Obesity Associated",
        "risk_allele": "A",
        "effect": "+0.39 kg/m² BMI per allele",
        "conditions": ["obesity", "increased BMI"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Exercise attenuates FTO effect significantly",
                "Protein-rich diet may help",
                "Portion control more important",
                "Not deterministic - lifestyle matters more"
            ]
        }
    },
    "rs17782313": {
        "gene": "MC4R",
        "name": "Melanocortin 4 Receptor",
        "risk_allele": "C",
        "conditions": ["obesity", "appetite regulation"],
        "note": "Affects satiety signaling"
    },
    "rs1558902": {
        "gene": "FTO",
        "name": "FTO Lead SNP",
        "risk_allele": "A",
        "conditions": ["obesity"]
    },

    # =========================================================================
    # ALZHEIMER'S DISEASE
    # =========================================================================
    "rs429358": {
        "gene": "APOE",
        "name": "APOE ε4 determinant 1",
        "risk_allele": "C",
        "or_per_allele": 3.0,
        "conditions": ["Alzheimer's disease", "cardiovascular disease", "longevity"],
        "evidence": "strong",
        "note": "Combined with rs7412 to determine APOE genotype",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "Exercise (especially aerobic) is protective",
                "Mediterranean diet",
                "Sleep optimization",
                "Cognitive engagement",
                "Consider not learning APOE status (personal choice)"
            ]
        }
    },
    "rs7412": {
        "gene": "APOE",
        "name": "APOE ε2/ε4 determinant",
        "risk_allele": "C",
        "conditions": ["Alzheimer's disease", "lipid metabolism"],
        "note": "TT = ε2 (protective), CC = ε3 or ε4"
    },
    "rs6656401": {
        "gene": "CR1",
        "name": "Complement Receptor 1",
        "risk_allele": "A",
        "or_per_allele": 1.18,
        "conditions": ["Alzheimer's disease"]
    },
    "rs744373": {
        "gene": "BIN1",
        "name": "Bridging Integrator 1",
        "risk_allele": "G",
        "or_per_allele": 1.15,
        "conditions": ["Alzheimer's disease"]
    },

    # =========================================================================
    # CANCER - COMMON VARIANTS (Not BRCA)
    # =========================================================================
    "rs2981582": {
        "gene": "FGFR2",
        "name": "Breast Cancer Risk",
        "risk_allele": "A",
        "or_per_allele": 1.26,
        "conditions": ["breast cancer (ER+)"],
        "evidence": "strong",
        "note": "Common variant, modest effect"
    },
    "rs13281615": {
        "gene": "8q24",
        "name": "Breast Cancer Risk",
        "risk_allele": "G",
        "or_per_allele": 1.08,
        "conditions": ["breast cancer"]
    },
    "rs6983267": {
        "gene": "8q24",
        "name": "Colorectal & Prostate Cancer",
        "risk_allele": "G",
        "or_per_allele": 1.21,
        "conditions": ["colorectal cancer", "prostate cancer"],
        "evidence": "strong"
    },
    "rs1447295": {
        "gene": "8q24",
        "name": "Prostate Cancer Risk",
        "risk_allele": "A",
        "or_per_allele": 1.44,
        "conditions": ["prostate cancer"],
        "evidence": "strong"
    },
    "rs10993994": {
        "gene": "MSMB",
        "name": "Prostate Cancer / PSA",
        "risk_allele": "T",
        "or_per_allele": 1.25,
        "conditions": ["prostate cancer"],
        "note": "Also affects baseline PSA levels"
    },
    "rs401681": {
        "gene": "TERT-CLPTM1L",
        "name": "Multiple Cancer Risk",
        "risk_allele": "T",
        "conditions": ["lung cancer", "bladder cancer", "prostate cancer"]
    },

    # =========================================================================
    # MACULAR DEGENERATION
    # =========================================================================
    "rs1061170": {
        "gene": "CFH",
        "name": "Complement Factor H Y402H",
        "risk_allele": "C",
        "or_per_allele": 2.5,
        "conditions": ["age-related macular degeneration"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "AREDS2 formula supplements",
                "Annual dilated eye exams",
                "Don't smoke",
                "Lutein/zeaxanthin supplementation"
            ]
        }
    },
    "rs10490924": {
        "gene": "ARMS2",
        "name": "AMD Major Risk",
        "risk_allele": "T",
        "or_per_allele": 2.7,
        "conditions": ["age-related macular degeneration"],
        "evidence": "strong"
    },

    # =========================================================================
    # AUTOIMMUNE
    # =========================================================================
    "rs2476601": {
        "gene": "PTPN22",
        "name": "Autoimmunity Master Switch",
        "risk_allele": "A",
        "or_per_allele": 1.7,
        "conditions": ["type 1 diabetes", "rheumatoid arthritis", "lupus", "Graves disease", "vitiligo"],
        "evidence": "strong",
        "note": "One variant, multiple autoimmune conditions"
    },
    "rs3087243": {
        "gene": "CTLA4",
        "name": "T Cell Regulation",
        "risk_allele": "G",
        "conditions": ["type 1 diabetes", "Graves disease", "autoimmune thyroid"],
        "evidence": "strong"
    },
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "name": "Celiac Disease Risk",
        "risk_allele": "T",
        "or_per_allele": 7.0,
        "conditions": ["celiac disease"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "DQ2/DQ8 negative essentially rules out celiac",
                "If GI symptoms, check tTG-IgA",
                "Do NOT start gluten-free diet before testing"
            ]
        }
    },
    "rs7574865": {
        "gene": "STAT4",
        "name": "Autoimmune Risk",
        "risk_allele": "T",
        "conditions": ["rheumatoid arthritis", "lupus"]
    },
    "rs11209026": {
        "gene": "IL23R",
        "name": "IBD Protective",
        "risk_allele": "A",
        "protective": True,
        "conditions": ["Crohn's disease", "psoriasis", "ankylosing spondylitis"],
        "note": "Rare protective variant - A allele reduces IBD risk ~2x"
    },

    # =========================================================================
    # IRON METABOLISM
    # =========================================================================
    "rs1800562": {
        "gene": "HFE",
        "name": "C282Y (Hemochromatosis)",
        "risk_allele": "A",
        "conditions": ["hereditary hemochromatosis", "iron overload"],
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "Monitor ferritin/transferrin saturation",
                "AVOID iron supplements",
                "Blood donation can be therapeutic",
                "Limit vitamin C with meals (increases absorption)"
            ]
        }
    },
    "rs1799945": {
        "gene": "HFE",
        "name": "H63D",
        "risk_allele": "G",
        "conditions": ["mild iron overload"],
        "note": "Much milder than C282Y; compound heterozygotes (C282Y/H63D) have intermediate risk"
    },

    # =========================================================================
    # GOUT / URIC ACID
    # =========================================================================
    "rs2231142": {
        "gene": "ABCG2",
        "name": "Urate Transport - Gout",
        "risk_allele": "T",
        "or_per_allele": 1.75,
        "conditions": ["gout", "hyperuricemia"],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Limit purine-rich foods (organ meats, shellfish)",
                "Limit alcohol (especially beer)",
                "Stay hydrated",
                "Monitor uric acid"
            ]
        }
    },
    "rs16890979": {
        "gene": "SLC2A9",
        "name": "Urate Transport",
        "risk_allele": "T",
        "conditions": ["gout", "uric acid levels"]
    },

    # =========================================================================
    # KIDNEY DISEASE
    # =========================================================================
    "rs73885319": {
        "gene": "APOL1",
        "name": "G1 (African Kidney Risk)",
        "risk_allele": "G",
        "conditions": ["FSGS", "HIVAN", "hypertensive nephropathy"],
        "evidence": "strong",
        "note": "Risk requires TWO risk variants (G1/G1, G1/G2, or G2/G2)",
        "population": "African ancestry",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "Annual kidney function testing if two risk alleles",
                "Blood pressure control critical",
                "Avoid nephrotoxic medications",
                "HIV/COVID may trigger kidney disease"
            ]
        }
    },
    "rs60910145": {
        "gene": "APOL1",
        "name": "G2 (African Kidney Risk)",
        "risk_allele": "del",
        "conditions": ["FSGS", "HIVAN", "hypertensive nephropathy"]
    },

    # =========================================================================
    # GLAUCOMA
    # =========================================================================
    "rs10483727": {
        "gene": "SIX1-SIX6",
        "name": "Primary Open Angle Glaucoma",
        "risk_allele": "A",
        "or_per_allele": 1.32,
        "conditions": ["glaucoma"]
    },
    "rs1063192": {
        "gene": "CDKN2B-AS1",
        "name": "Glaucoma Risk",
        "risk_allele": "A",
        "conditions": ["glaucoma"]
    },

    # =========================================================================
    # OSTEOPOROSIS
    # =========================================================================
    "rs3736228": {
        "gene": "LRP5",
        "name": "Bone Density",
        "risk_allele": "T",
        "conditions": ["osteoporosis", "fracture risk"]
    },
    "rs4988235": {
        "gene": "LCT",
        "name": "Lactase Persistence",
        "risk_allele": "A",
        "protective": True,
        "conditions": ["lactose tolerance"],
        "note": "AA = lactase persistent (can digest dairy). GG = lactose intolerant.",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "GG: Likely lactose intolerant in adulthood",
                "Lactase supplements help",
                "Ensure adequate calcium from other sources"
            ]
        }
    },

    # =========================================================================
    # THYROID
    # =========================================================================
    "rs965513": {
        "gene": "FOXE1",
        "name": "Thyroid Cancer Risk",
        "risk_allele": "A",
        "or_per_allele": 1.75,
        "conditions": ["thyroid cancer"]
    },
    "rs2910164": {
        "gene": "MIR146A",
        "name": "Thyroid Cancer",
        "risk_allele": "G",
        "conditions": ["thyroid cancer"]
    },
}
