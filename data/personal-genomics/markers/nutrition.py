"""
Nutrigenomics Markers
Source: GWAS, Literature

Genetic variants affecting nutrient metabolism and dietary requirements.
"""

NUTRITION_MARKERS = {
    # =========================================================================
    # VITAMINS
    # =========================================================================
    "rs1801133": {
        "gene": "MTHFR",
        "nutrient": "Folate",
        "variant": "C677T",
        "risk_allele": "A",
        "effect": "TT genotype: 30% reduced enzyme activity, elevated homocysteine",
        "prevalence": {"EUR": 0.35, "EAS": 0.30, "AFR": 0.10},
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Consider methylfolate (5-MTHF) instead of folic acid",
                "B12 also important (methylcobalamin preferred)",
                "Check homocysteine levels",
                "Leafy greens provide natural folate"
            ]
        }
    },
    "rs1801131": {
        "gene": "MTHFR",
        "nutrient": "Folate",
        "variant": "A1298C",
        "risk_allele": "G",
        "effect": "Reduced enzyme activity (milder than C677T)",
        "note": "Compound heterozygous (C677T + A1298C) has additive effect"
    },
    
    "rs2282679": {
        "gene": "GC",
        "nutrient": "Vitamin D",
        "variant": "Vitamin D binding protein",
        "risk_allele": "G",
        "effect": "Lower 25(OH)D levels",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Higher vitamin D supplementation may be needed",
                "Test 25(OH)D levels",
                "Combine D3 with K2",
                "Sun exposure helps but may not be sufficient"
            ]
        }
    },
    "rs12785878": {
        "gene": "DHCR7/NADSYN1",
        "nutrient": "Vitamin D",
        "variant": "Synthesis pathway",
        "risk_allele": "T",
        "effect": "Reduced synthesis from sun exposure"
    },
    "rs10741657": {
        "gene": "CYP2R1",
        "nutrient": "Vitamin D",
        "variant": "25-hydroxylation",
        "risk_allele": "A",
        "effect": "Lower 25(OH)D levels"
    },
    
    "rs492602": {
        "gene": "FUT2",
        "nutrient": "Vitamin B12",
        "variant": "Secretor status",
        "risk_allele": "G",
        "effect": "Non-secretor: altered B12 absorption",
        "note": "Also affects gut microbiome"
    },
    "rs602662": {
        "gene": "FUT2",
        "nutrient": "Vitamin B12",
        "risk_allele": "A",
        "effect": "Lower B12 levels"
    },
    
    "rs234706": {
        "gene": "CBS",
        "nutrient": "B6/Homocysteine",
        "variant": "C699T",
        "risk_allele": "A",
        "effect": "Upregulated enzyme - rapid homocysteine clearance",
        "note": "May need more B6, but high sulfur foods may cause issues"
    },
    
    "rs1799998": {
        "gene": "CYP11B2",
        "nutrient": "Sodium sensitivity",
        "risk_allele": "T",
        "effect": "Salt-sensitive blood pressure",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Limit sodium if hypertensive",
                "DASH diet beneficial",
                "Potassium-rich foods help counteract"
            ]
        }
    },

    # =========================================================================
    # MINERALS
    # =========================================================================
    "rs1800562": {
        "gene": "HFE",
        "nutrient": "Iron",
        "variant": "C282Y",
        "risk_allele": "A",
        "effect": "Hemochromatosis - iron overload",
        "actionable": {
            "priority": "high",
            "recommendations": [
                "AVOID iron supplements",
                "Limit vitamin C with meals (increases absorption)",
                "Monitor ferritin",
                "Blood donation therapeutic"
            ]
        }
    },
    "rs855791": {
        "gene": "TMPRSS6",
        "nutrient": "Iron",
        "risk_allele": "G",
        "effect": "Lower iron/hemoglobin levels",
        "note": "May need more iron-rich foods"
    },
    
    "rs11568820": {
        "gene": "VDR",
        "nutrient": "Calcium/Vitamin D",
        "variant": "Cdx2",
        "risk_allele": "A",
        "effect": "Altered VDR transcription"
    },
    "rs1544410": {
        "gene": "VDR",
        "nutrient": "Vitamin D Receptor",
        "variant": "BsmI",
        "risk_allele": "A",
        "effect": "Altered vitamin D signaling"
    },
    
    "rs9402373": {
        "gene": "SLC39A8",
        "nutrient": "Zinc",
        "risk_allele": "T",
        "effect": "Lower plasma zinc",
        "note": "Zinc supplementation may be beneficial"
    },
    
    "rs7579169": {
        "gene": "SHMT1",
        "nutrient": "Folate/B12",
        "risk_allele": "A",
        "effect": "Altered one-carbon metabolism"
    },

    # =========================================================================
    # MACRONUTRIENTS
    # =========================================================================
    "rs5082": {
        "gene": "APOA2",
        "nutrient": "Saturated Fat Response",
        "risk_allele": "C",
        "effect": "CC genotype: higher BMI with high saturated fat intake",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "If CC, limiting saturated fat may help weight management",
                "Replace with unsaturated fats (olive oil, nuts)"
            ]
        }
    },
    "rs662799": {
        "gene": "APOA5",
        "nutrient": "Fat Response",
        "risk_allele": "C",
        "effect": "Higher triglycerides, especially with high fat diet"
    },
    
    "rs1799883": {
        "gene": "FABP2",
        "nutrient": "Fat Absorption",
        "variant": "Ala54Thr",
        "risk_allele": "G",
        "effect": "Increased fat absorption",
        "note": "May benefit from lower fat diet"
    },
    
    "rs1800206": {
        "gene": "PPARA",
        "nutrient": "Fat Metabolism",
        "variant": "Leu162Val",
        "risk_allele": "C",
        "effect": "Altered PPAR signaling",
        "note": "May affect response to omega-3 fatty acids"
    },
    
    "rs174547": {
        "gene": "FADS1",
        "nutrient": "Omega-3/Omega-6 Conversion",
        "risk_allele": "C",
        "effect": "Reduced conversion of plant omega-3 (ALA) to EPA/DHA",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "May need preformed EPA/DHA (fish oil or algae)",
                "Plant sources (flax) less efficient"
            ]
        }
    },
    "rs174575": {
        "gene": "FADS2",
        "nutrient": "Fatty Acid Desaturation",
        "risk_allele": "G",
        "effect": "Altered omega-3/6 metabolism"
    },
    
    "rs9930506": {
        "gene": "FTO",
        "nutrient": "Carbohydrate Response",
        "risk_allele": "G",
        "effect": "Higher BMI, especially with high carb diet",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Exercise significantly reduces FTO effect",
                "Protein may increase satiety",
                "Portion control important"
            ]
        }
    },
    
    "rs1801278": {
        "gene": "IRS1",
        "nutrient": "Carbohydrate/Insulin",
        "variant": "Gly972Arg",
        "risk_allele": "T",
        "effect": "Insulin resistance - may benefit from low glycemic diet"
    },

    # =========================================================================
    # METABOLISM / DETOX
    # =========================================================================
    "rs4880": {
        "gene": "SOD2",
        "nutrient": "Antioxidants",
        "variant": "Ala16Val",
        "risk_allele": "A",
        "effect": "AA = mitochondria more susceptible to oxidative stress",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "Antioxidant-rich diet beneficial",
                "Consider CoQ10, NAC supplementation",
                "Avoid excess iron/copper (pro-oxidant)"
            ]
        }
    },
    "rs1695": {
        "gene": "GSTP1",
        "nutrient": "Detoxification",
        "variant": "Ile105Val",
        "risk_allele": "G",
        "effect": "Altered glutathione conjugation",
        "note": "Cruciferous vegetables may be especially beneficial"
    },
    "rs1050450": {
        "gene": "GPX1",
        "nutrient": "Selenium",
        "variant": "Pro198Leu",
        "risk_allele": "T",
        "effect": "Lower GPX activity - selenium more important"
    },
    
    "rs762551": {
        "gene": "CYP1A2",
        "nutrient": "Caffeine",
        "risk_allele": "C",
        "effect": "CC = slow caffeine metabolizer",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "CC genotype: Limit caffeine to <200mg/day",
                "Avoid afternoon caffeine",
                "May have stronger cardiovascular effects"
            ]
        }
    },
    
    "rs72921001": {
        "gene": "ALPL",
        "nutrient": "Vitamin B6",
        "risk_allele": "T",
        "effect": "Altered B6 metabolism",
        "note": "May need pyridoxal-5-phosphate (active B6)"
    },

    # =========================================================================
    # APPETITE / SATIETY
    # =========================================================================
    "rs17782313": {
        "gene": "MC4R",
        "nutrient": "Appetite Regulation",
        "risk_allele": "C",
        "effect": "Increased appetite, reduced satiety",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "Protein at each meal may help satiety",
                "Structured meal timing",
                "Mindful eating practices"
            ]
        }
    },
    "rs1137101": {
        "gene": "LEPR",
        "nutrient": "Leptin Signaling",
        "risk_allele": "A",
        "effect": "Altered leptin receptor - may affect satiety"
    },
    "rs7799039": {
        "gene": "LEP",
        "nutrient": "Leptin",
        "risk_allele": "A",
        "effect": "Altered leptin production"
    },

    # =========================================================================
    # ALCOHOL / HISTAMINE
    # =========================================================================
    "rs671": {
        "gene": "ALDH2",
        "nutrient": "Alcohol",
        "risk_allele": "A",
        "effect": "Alcohol flush - AVOID alcohol if AG or AA",
        "note": "Esophageal cancer risk if drinking despite flush"
    },
    
    "rs1049793": {
        "gene": "AOC1/ABP1",
        "nutrient": "Histamine",
        "risk_allele": "G",
        "effect": "Reduced DAO enzyme - histamine intolerance",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "If symptoms: limit aged foods (cheese, wine, fermented)",
                "Fresh foods preferred",
                "DAO supplements may help"
            ]
        }
    },
    
    "rs10156191": {
        "gene": "AOC1",
        "nutrient": "Histamine",
        "risk_allele": "T",
        "effect": "Reduced DAO activity"
    },
}
