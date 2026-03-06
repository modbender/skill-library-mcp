"""
Dermatology and Skin Genetics Markers.
Markers for skin conditions, pigmentation, aging, and dermatological traits.
"""

DERMATOLOGY_MARKERS = {
    # =========================================================================
    # SKIN PIGMENTATION
    # =========================================================================
    
    "rs1426654": {
        "gene": "SLC24A5",
        "name": "Light skin variant",
        "risk_allele": "A",
        "category": "pigmentation",
        "trait": "Skin color",
        "evidence": "strong",
        "references": ["PMID:16357253"],
        "interpretation": {
            "AA": "Light skin (European-associated)",
            "AG": "Intermediate pigmentation",
            "GG": "Darker skin pigmentation"
        },
        "clinical_notes": "Major determinant of skin color variation",
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "AA genotype: Higher UV sensitivity, sunscreen important",
                "Vitamin D synthesis may vary with pigmentation"
            ]
        }
    },
    
    "rs16891982": {
        "gene": "SLC45A2",
        "name": "MATP skin color",
        "risk_allele": "G",
        "category": "pigmentation",
        "trait": "Skin pigmentation",
        "evidence": "strong",
        "references": ["PMID:17952075"],
        "interpretation": {
            "GG": "Light skin pigmentation",
            "GC": "Intermediate",
            "CC": "Darker pigmentation"
        }
    },
    
    "rs1800407": {
        "gene": "OCA2",
        "name": "OCA2 R419Q",
        "risk_allele": "T",
        "category": "pigmentation",
        "trait": "Eye/skin color",
        "evidence": "strong",
        "references": ["PMID:18252222"],
        "interpretation": {
            "CC": "Typical melanin production",
            "CT": "Intermediate",
            "TT": "Reduced melanin, lighter features"
        }
    },
    
    "rs1800401": {
        "gene": "OCA2",
        "name": "OCA2 R305W",
        "risk_allele": "A",
        "category": "pigmentation",
        "trait": "Pigmentation",
        "evidence": "moderate",
        "references": ["PMID:18488027"]
    },
    
    "rs1805005": {
        "gene": "MC1R",
        "name": "MC1R V60L",
        "risk_allele": "T",
        "category": "pigmentation",
        "trait": "Red hair, fair skin, freckling",
        "evidence": "strong",
        "references": ["PMID:8733135"],
        "interpretation": {
            "CC": "Normal MC1R function",
            "CT": "Partial red hair trait carrier",
            "TT": "Likely red hair, fair skin, freckling"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Increased UV sensitivity",
                "Higher melanoma risk - vigilant sun protection",
                "Regular skin checks recommended"
            ]
        }
    },
    
    "rs1805007": {
        "gene": "MC1R",
        "name": "MC1R R151C",
        "risk_allele": "T",
        "category": "pigmentation",
        "trait": "Red hair, melanoma risk",
        "evidence": "strong",
        "references": ["PMID:8733135", "PMID:10737969"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Strong red hair/fair skin variant",
                "~2x melanoma risk per copy",
                "Annual dermatology screening recommended",
                "Strict sun protection"
            ]
        }
    },
    
    "rs1805008": {
        "gene": "MC1R",
        "name": "MC1R R160W",
        "risk_allele": "T",
        "category": "pigmentation",
        "trait": "Red hair variant",
        "evidence": "strong",
        "references": ["PMID:8733135"],
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": ["Melanoma risk variant", "Sun protection essential"]
        }
    },
    
    "rs1805009": {
        "gene": "MC1R",
        "name": "MC1R D294H",
        "risk_allele": "C",
        "category": "pigmentation",
        "trait": "Red hair, melanoma risk",
        "evidence": "strong",
        "references": ["PMID:8733135"]
    },
    
    # =========================================================================
    # SKIN CANCER RISK
    # =========================================================================
    
    "rs910873": {
        "gene": "TERT-CLPTM1L",
        "name": "Melanoma risk",
        "risk_allele": "C",
        "category": "skin_cancer",
        "conditions": ["Melanoma"],
        "evidence": "strong",
        "references": ["PMID:19783988"],
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": ["Regular skin screening", "Sun protection"]
        }
    },
    
    "rs401681": {
        "gene": "TERT-CLPTM1L",
        "name": "Skin cancer risk",
        "risk_allele": "T",
        "category": "skin_cancer",
        "conditions": ["Basal cell carcinoma", "Melanoma"],
        "evidence": "strong",
        "references": ["PMID:19578363"],
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": ["Annual skin checks", "Avoid excessive UV exposure"]
        }
    },
    
    "rs12203592": {
        "gene": "IRF4",
        "name": "IRF4 melanoma",
        "risk_allele": "T",
        "category": "skin_cancer",
        "conditions": ["Melanoma", "Sensitivity to UV"],
        "evidence": "strong",
        "references": ["PMID:19340009"],
        "note": "Also associated with skin, hair, eye pigmentation",
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": ["Sun protection", "Mole monitoring"]
        }
    },
    
    "rs13191343": {
        "gene": "MITF",
        "name": "MITF melanoma",
        "risk_allele": "T",
        "category": "skin_cancer",
        "conditions": ["Melanoma"],
        "evidence": "moderate",
        "references": ["PMID:21983787"],
        "note": "Transcription factor for melanocytes"
    },
    
    # =========================================================================
    # PSORIASIS
    # =========================================================================
    
    "rs10484554": {
        "gene": "HLA-C",
        "name": "Psoriasis HLA-C*06:02",
        "risk_allele": "T",
        "category": "psoriasis",
        "conditions": ["Psoriasis vulgaris"],
        "evidence": "strong",
        "references": ["PMID:17083362"],
        "interpretation": {
            "CC": "Lower psoriasis risk",
            "CT": "Moderate risk",
            "TT": "~10x increased psoriasis risk"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Strongest genetic psoriasis risk factor",
                "Watch for early signs (scalp, elbows, knees)",
                "Multiple effective treatments available"
            ]
        }
    },
    
    "rs6677595": {
        "gene": "LCE3D",
        "name": "Late cornified envelope",
        "risk_allele": "T",
        "category": "psoriasis",
        "conditions": ["Psoriasis"],
        "evidence": "strong",
        "references": ["PMID:19169255"],
        "note": "Skin barrier function"
    },
    
    "rs20541": {
        "gene": "IL13",
        "name": "IL-13 psoriasis",
        "risk_allele": "A",
        "category": "psoriasis",
        "conditions": ["Psoriasis", "Atopic dermatitis", "Asthma"],
        "evidence": "moderate",
        "references": ["PMID:16477178"]
    },
    
    # =========================================================================
    # ECZEMA / ATOPIC DERMATITIS
    # =========================================================================
    
    "rs2228145": {
        "gene": "IL6R",
        "name": "IL-6 receptor eczema",
        "risk_allele": "C",
        "category": "eczema",
        "conditions": ["Atopic dermatitis", "Eczema"],
        "evidence": "strong",
        "references": ["PMID:21909115"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Barrier care, moisturization important"]
        }
    },
    
    "rs2897442": {
        "gene": "FLG",
        "name": "Filaggrin region",
        "risk_allele": "A",
        "category": "eczema",
        "conditions": ["Atopic dermatitis", "Ichthyosis vulgaris"],
        "evidence": "strong",
        "references": ["PMID:16983376"],
        "note": "FLG loss-of-function mutations are strongest eczema risk",
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Skin barrier defect - intensive moisturization helps",
                "Associated with eczema-asthma-allergies triad",
                "May benefit from barrier repair creams"
            ]
        }
    },
    
    "rs61816761": {
        "gene": "FLG",
        "name": "Filaggrin R501X",
        "risk_allele": "A",
        "category": "eczema",
        "conditions": ["Atopic dermatitis", "Ichthyosis"],
        "evidence": "strong",
        "references": ["PMID:16983376"],
        "note": "Common European loss-of-function variant",
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Loss of skin barrier protein",
                "~3x eczema risk per copy",
                "Daily emollient use recommended"
            ]
        }
    },
    
    "rs10927670": {
        "gene": "OVOL1",
        "name": "OVOL1 eczema",
        "risk_allele": "G",
        "category": "eczema",
        "conditions": ["Atopic dermatitis"],
        "evidence": "strong",
        "references": ["PMID:23042114"],
        "note": "Skin differentiation factor"
    },
    
    # =========================================================================
    # ACNE
    # =========================================================================
    
    "rs4133274": {
        "gene": "DDB2",
        "name": "Acne susceptibility",
        "risk_allele": "A",
        "category": "acne",
        "conditions": ["Acne vulgaris"],
        "evidence": "moderate",
        "references": ["PMID:24927181"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["DNA repair gene - may affect post-acne scarring"]
        }
    },
    
    "rs7531806": {
        "gene": "8q24",
        "name": "Acne 8q24 locus",
        "risk_allele": "A",
        "category": "acne",
        "conditions": ["Severe acne"],
        "evidence": "moderate",
        "references": ["PMID:24927181"]
    },
    
    "rs1159268": {
        "gene": "FST",
        "name": "Follistatin acne",
        "risk_allele": "T",
        "category": "acne",
        "conditions": ["Acne"],
        "evidence": "moderate",
        "references": ["PMID:24927181"],
        "note": "TGF-beta signaling pathway"
    },
    
    # =========================================================================
    # SKIN AGING
    # =========================================================================
    
    "rs12785878": {
        "gene": "DHCR7",
        "name": "Vitamin D skin aging",
        "risk_allele": "G",
        "category": "skin_aging",
        "conditions": ["Skin aging", "Vitamin D synthesis"],
        "evidence": "moderate",
        "references": ["PMID:20086105"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": ["Affects vitamin D synthesis in skin"]
        }
    },
    
    "rs7997012": {
        "gene": "STXBP5L",
        "name": "Perceived age",
        "risk_allele": "A",
        "category": "skin_aging",
        "trait": "Perceived facial age",
        "evidence": "moderate",
        "references": ["PMID:28036287"],
        "note": "Associated with looking older/younger than actual age"
    },
    
    "rs322458": {
        "gene": "MC1R",
        "name": "MC1R perceived age",
        "risk_allele": "A",
        "category": "skin_aging",
        "trait": "Perceived facial age",
        "evidence": "moderate",
        "references": ["PMID:28036287"],
        "note": "MC1R variants associated with looking older"
    },
    
    # =========================================================================
    # VITILIGO
    # =========================================================================
    
    "rs4959053": {
        "gene": "MHC region",
        "name": "Vitiligo HLA",
        "risk_allele": "A",
        "category": "vitiligo",
        "conditions": ["Vitiligo"],
        "evidence": "strong",
        "references": ["PMID:20694014"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Autoimmune pigment condition", "Sun protection for affected areas"]
        }
    },
    
    "rs12206499": {
        "gene": "SMOC2",
        "name": "Vitiligo SMOC2",
        "risk_allele": "T",
        "category": "vitiligo",
        "conditions": ["Vitiligo"],
        "evidence": "moderate",
        "references": ["PMID:20694014"]
    },
    
    "rs1063635": {
        "gene": "UBASH3A",
        "name": "Vitiligo autoimmune",
        "risk_allele": "G",
        "category": "vitiligo",
        "conditions": ["Vitiligo", "Autoimmunity"],
        "evidence": "moderate",
        "references": ["PMID:20694014"],
        "note": "Shared with other autoimmune conditions"
    },
    
    # =========================================================================
    # HAIR TRAITS
    # =========================================================================
    
    "rs11803731": {
        "gene": "TCHH",
        "name": "Hair curl/straightness",
        "risk_allele": "A",
        "category": "hair",
        "trait": "Hair texture",
        "evidence": "strong",
        "references": ["PMID:19578383"],
        "interpretation": {
            "TT": "Straighter hair",
            "AT": "Intermediate",
            "AA": "Curlier hair"
        }
    },
    
    "rs17646946": {
        "gene": "TCHH",
        "name": "Hair thickness",
        "risk_allele": "A",
        "category": "hair",
        "trait": "Hair thickness",
        "evidence": "moderate",
        "references": ["PMID:19578383"]
    },
    
    "rs4778138": {
        "gene": "HERC2-OCA2",
        "name": "Hair color",
        "risk_allele": "G",
        "category": "hair",
        "trait": "Hair color",
        "evidence": "strong",
        "references": ["PMID:18488028"],
        "note": "Blonde vs dark hair"
    },
    
    "rs17822931": {
        "gene": "ABCC11",
        "name": "Earwax type / body odor",
        "risk_allele": "T",
        "category": "misc",
        "trait": "Earwax type, axillary odor",
        "evidence": "strong",
        "references": ["PMID:16444273"],
        "interpretation": {
            "CC": "Wet earwax, typical body odor",
            "CT": "Intermediate",
            "TT": "Dry earwax, reduced body odor (common in East Asian)"
        },
        "note": "Also affects colostrum secretion in breastfeeding"
    },
    
    # =========================================================================
    # MALE PATTERN BALDNESS
    # =========================================================================
    
    "rs2180439": {
        "gene": "20p11",
        "name": "Male pattern baldness",
        "risk_allele": "T",
        "category": "hair_loss",
        "conditions": ["Androgenetic alopecia"],
        "evidence": "strong",
        "references": ["PMID:18849991"],
        "sex": "male",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["One of multiple baldness risk factors"]
        }
    },
    
    "rs1385699": {
        "gene": "7p21.1",
        "name": "Male baldness 7p21",
        "risk_allele": "A",
        "category": "hair_loss",
        "conditions": ["Male pattern baldness"],
        "evidence": "moderate",
        "references": ["PMID:22693459"]
    },
    
    "rs6625163": {
        "gene": "AR region",
        "name": "Androgen receptor baldness",
        "risk_allele": "A",
        "category": "hair_loss",
        "conditions": ["Male pattern baldness"],
        "evidence": "strong",
        "references": ["PMID:18849991"],
        "note": "X chromosome - maternal inheritance pattern"
    },
    
    # =========================================================================
    # WOUND HEALING
    # =========================================================================
    
    "rs9321460": {
        "gene": "ANKRD55",
        "name": "Keloid scarring",
        "risk_allele": "A",
        "category": "wound_healing",
        "conditions": ["Keloid formation"],
        "evidence": "moderate",
        "references": ["PMID:20711178"],
        "note": "More common in African ancestry",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "Increased keloid risk with surgery/piercings",
                "Discuss with surgeon before elective procedures"
            ]
        }
    },
    
    "rs873549": {
        "gene": "FOXL2",
        "name": "Keloid FOXL2",
        "risk_allele": "T",
        "category": "wound_healing",
        "conditions": ["Keloid scarring"],
        "evidence": "moderate",
        "references": ["PMID:20711178"]
    },
}

# Summary information for dermatology section
DERMATOLOGY_SUMMARY = """
Skin Genetics Overview:

PIGMENTATION:
- MC1R variants strongest predictors of red hair/fair skin
- SLC24A5 and SLC45A2 major skin color determinants
- OCA2/HERC2 complex affects eyes and skin

CANCER RISK:
- MC1R variants increase melanoma risk 2-4x
- Fair skin + UV exposure = synergistic risk
- CDKN2A (not on consumer arrays) strongest familial melanoma gene

INFLAMMATORY CONDITIONS:
- HLA-C*06:02 is strongest psoriasis predictor
- FLG mutations increase eczema risk 3x
- Many conditions share genetic architecture

RECOMMENDATIONS BY GENOTYPE:
- MC1R carriers: SPF 30+ daily, annual derm checks, avoid tanning
- FLG carriers: Daily moisturizer, barrier creams, monitor for asthma
- HLA-C*06:02 carriers: Early treatment of psoriasis symptoms
"""
