"""
Pharmacogenomics Markers
Source: PharmGKB, CPIC Guidelines, FDA Table of Pharmacogenomic Biomarkers

These markers affect drug metabolism, efficacy, and adverse reactions.
Critical for precision medicine and medication safety.
"""

PHARMACOGENOMICS_MARKERS = {
    # =========================================================================
    # CYP2D6 - Metabolizes ~25% of all drugs
    # =========================================================================
    "rs3892097": {
        "gene": "CYP2D6",
        "variant": "*4",
        "function": "No function (null allele)",
        "risk_allele": "A",
        "frequency_eur": 0.20,
        "drugs_affected": [
            "codeine", "tramadol", "oxycodone",
            "tamoxifen", "ondansetron",
            "fluoxetine", "paroxetine", "venlafaxine",
            "metoprolol", "carvedilol",
            "risperidone", "aripiprazole"
        ],
        "clinical_impact": "Poor metabolizer - reduced activation of prodrugs, increased toxicity of others",
        "cpic_level": "1A",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Codeine may be ineffective (cannot convert to morphine)",
                "Tramadol may be ineffective", 
                "Tamoxifen may have reduced efficacy",
                "Request pharmacogenomic consultation before starting these drugs"
            ]
        }
    },
    "rs5030655": {
        "gene": "CYP2D6",
        "variant": "*6",
        "function": "No function (null allele)",
        "risk_allele": "del",
        "drugs_affected": ["Same as *4"],
        "clinical_impact": "Poor metabolizer",
        "cpic_level": "1A"
    },
    "rs16947": {
        "gene": "CYP2D6",
        "variant": "*2",
        "function": "Normal to increased function",
        "risk_allele": "A",
        "note": "May indicate ultrarapid metabolizer status if duplicated",
        "clinical_impact": "Ultrarapid if gene duplicated - prodrugs may cause toxicity"
    },
    "rs1065852": {
        "gene": "CYP2D6",
        "variant": "*10",
        "function": "Decreased function",
        "risk_allele": "A",
        "frequency_eas": 0.40,
        "note": "Common in East Asian populations",
        "clinical_impact": "Intermediate metabolizer"
    },
    "rs28371706": {
        "gene": "CYP2D6",
        "variant": "*17",
        "function": "Decreased function",
        "risk_allele": "A",
        "frequency_afr": 0.20,
        "note": "Common in African populations",
        "clinical_impact": "Intermediate metabolizer"
    },
    "rs28371725": {
        "gene": "CYP2D6",
        "variant": "*41",
        "function": "Decreased function",
        "risk_allele": "A",
        "clinical_impact": "Intermediate metabolizer"
    },

    # =========================================================================
    # CYP2C19 - Clopidogrel, PPIs, SSRIs
    # =========================================================================
    "rs4244285": {
        "gene": "CYP2C19",
        "variant": "*2",
        "function": "No function",
        "risk_allele": "A",
        "frequency_eur": 0.15,
        "frequency_eas": 0.30,
        "drugs_affected": [
            "clopidogrel (Plavix)",
            "omeprazole", "esomeprazole", "pantoprazole",
            "citalopram", "escitalopram", "sertraline",
            "voriconazole"
        ],
        "clinical_impact": "Poor metabolizer - clopidogrel ineffective",
        "cpic_level": "1A",
        "fda_label": "boxed_warning",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "CLOPIDOGREL (Plavix) may be INEFFECTIVE",
                "Alternative antiplatelet therapy recommended (prasugrel, ticagrelor)",
                "Higher PPI doses may be needed for acid reflux",
                "Inform cardiologist BEFORE any cardiac procedure"
            ]
        }
    },
    "rs4986893": {
        "gene": "CYP2C19",
        "variant": "*3",
        "function": "No function",
        "risk_allele": "A",
        "frequency_eas": 0.05,
        "clinical_impact": "Poor metabolizer",
        "cpic_level": "1A"
    },
    "rs12248560": {
        "gene": "CYP2C19",
        "variant": "*17",
        "function": "Increased function",
        "risk_allele": "T",
        "frequency_eur": 0.20,
        "drugs_affected": ["clopidogrel", "SSRIs", "PPIs"],
        "clinical_impact": "Ultrarapid metabolizer - increased clopidogrel effect, reduced SSRI/PPI effect",
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "May need higher SSRI doses",
                "PPIs may be less effective",
                "Increased bleeding risk with clopidogrel"
            ]
        }
    },

    # =========================================================================
    # CYP2C9 - Warfarin, NSAIDs, Sulfonylureas
    # =========================================================================
    "rs1799853": {
        "gene": "CYP2C9",
        "variant": "*2",
        "function": "Decreased function (~70% activity)",
        "risk_allele": "T",
        "frequency_eur": 0.13,
        "drugs_affected": [
            "warfarin",
            "phenytoin",
            "losartan",
            "celecoxib", "ibuprofen", "flurbiprofen",
            "glipizide", "glimepiride", "tolbutamide"
        ],
        "clinical_impact": "Reduced warfarin clearance - lower dose needed",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "WARFARIN: ~20% dose reduction typically needed",
                "Increased bleeding risk if standard dose given",
                "Sulfonylureas: increased hypoglycemia risk",
                "Inform prescribers before anticoagulation"
            ]
        }
    },
    "rs1057910": {
        "gene": "CYP2C9",
        "variant": "*3",
        "function": "Significantly decreased function (~5% activity)",
        "risk_allele": "C",
        "frequency_eur": 0.07,
        "drugs_affected": ["Same as *2"],
        "clinical_impact": "Poor metabolizer - major warfarin dose reduction needed",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "WARFARIN: ~40% dose reduction typically needed",
                "HIGH bleeding risk at standard doses",
                "Consider alternative anticoagulants (DOACs)",
                "MANDATORY pharmacogenomic consultation for warfarin"
            ]
        }
    },
    "rs7900194": {
        "gene": "CYP2C9",
        "variant": "*8",
        "function": "Decreased function",
        "risk_allele": "A",
        "frequency_afr": 0.06,
        "note": "Important in African populations"
    },
    "rs28371686": {
        "gene": "CYP2C9",
        "variant": "*11",
        "function": "Decreased function",
        "risk_allele": "T",
        "frequency_afr": 0.02
    },

    # =========================================================================
    # VKORC1 - Warfarin Target
    # =========================================================================
    "rs9923231": {
        "gene": "VKORC1",
        "variant": "-1639G>A",
        "function": "Reduced expression",
        "risk_allele": "T",
        "frequency_eur": 0.40,
        "frequency_eas": 0.90,
        "drugs_affected": ["warfarin", "phenprocoumon", "acenocoumarol"],
        "clinical_impact": "Lower warfarin dose requirement (TT needs ~50% less)",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "TT genotype: ~50% lower warfarin dose needed",
                "CT genotype: ~25% lower dose",
                "Combines with CYP2C9 for total dose calculation",
                "Use FDA-approved warfarin dosing algorithms"
            ]
        }
    },

    # =========================================================================
    # CYP3A4/CYP3A5 - Largest drug-metabolizing CYP
    # =========================================================================
    "rs776746": {
        "gene": "CYP3A5",
        "variant": "*3",
        "function": "Non-expressor (splicing defect)",
        "risk_allele": "C",
        "frequency_eur": 0.90,
        "frequency_afr": 0.30,
        "drugs_affected": [
            "tacrolimus", "cyclosporine",
            "midazolam", "alprazolam",
            "atorvastatin", "simvastatin",
            "amlodipine", "nifedipine"
        ],
        "clinical_impact": "Non-expressors need lower tacrolimus doses",
        "cpic_level": "1A",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Tacrolimus: *3/*3 needs lower starting dose",
                "Critical for organ transplant patients",
                "Inform transplant team of CYP3A5 status"
            ]
        }
    },
    "rs35599367": {
        "gene": "CYP3A4",
        "variant": "*22",
        "function": "Decreased expression",
        "risk_allele": "T",
        "frequency_eur": 0.05,
        "drugs_affected": ["tacrolimus", "statins", "benzodiazepines"],
        "clinical_impact": "Reduced CYP3A4 activity"
    },

    # =========================================================================
    # CYP1A2 - Caffeine, Theophylline, Clozapine
    # =========================================================================
    "rs762551": {
        "gene": "CYP1A2",
        "variant": "*1F",
        "function": "Inducible (high activity when induced)",
        "risk_allele": "C",
        "frequency_eur": 0.30,
        "drugs_affected": [
            "caffeine",
            "theophylline",
            "clozapine",
            "olanzapine",
            "melatonin"
        ],
        "clinical_impact": "CC = slow metabolizer (caffeine sensitive)",
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle_modification",
            "recommendations": [
                "CC genotype: slow caffeine metabolism",
                "Limit afternoon/evening caffeine",
                "May have stronger response to caffeine",
                "Theophylline dosing may need adjustment"
            ]
        }
    },
    "rs2069514": {
        "gene": "CYP1A2",
        "variant": "*1C",
        "function": "Decreased expression",
        "risk_allele": "A",
        "frequency_eas": 0.25
    },

    # =========================================================================
    # DPYD - 5-Fluorouracil (Cancer Chemotherapy)
    # =========================================================================
    "rs3918290": {
        "gene": "DPYD",
        "variant": "*2A (IVS14+1G>A)",
        "function": "No function",
        "risk_allele": "A",
        "frequency_eur": 0.01,
        "drugs_affected": ["5-fluorouracil", "capecitabine", "tegafur"],
        "clinical_impact": "SEVERE/FATAL TOXICITY with standard fluoropyrimidine doses",
        "cpic_level": "1A",
        "fda_label": "boxed_warning",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "CONTRAINDICATED: Standard 5-FU/capecitabine doses",
                "Risk of FATAL toxicity (neutropenia, mucositis, neurotoxicity)",
                "50% dose reduction required if heterozygous",
                "MANDATORY testing before fluoropyrimidine chemotherapy"
            ]
        }
    },
    "rs55886062": {
        "gene": "DPYD",
        "variant": "*13 (I560S)",
        "function": "No function",
        "risk_allele": "A",
        "drugs_affected": ["5-fluorouracil", "capecitabine"],
        "clinical_impact": "Severe toxicity risk",
        "cpic_level": "1A"
    },
    "rs67376798": {
        "gene": "DPYD",
        "variant": "D949V",
        "function": "Decreased function",
        "risk_allele": "A",
        "drugs_affected": ["5-fluorouracil", "capecitabine"],
        "clinical_impact": "25-50% dose reduction recommended",
        "cpic_level": "1A"
    },
    "rs75017182": {
        "gene": "DPYD",
        "variant": "HapB3",
        "function": "Decreased function",
        "risk_allele": "G",
        "clinical_impact": "25% dose reduction recommended"
    },

    # =========================================================================
    # TPMT/NUDT15 - Thiopurines (Azathioprine, 6-MP)
    # =========================================================================
    "rs1142345": {
        "gene": "TPMT",
        "variant": "*3C",
        "function": "No function",
        "risk_allele": "G",
        "frequency_eur": 0.05,
        "drugs_affected": ["azathioprine", "mercaptopurine", "thioguanine"],
        "clinical_impact": "Severe myelosuppression at standard doses",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Heterozygous: Start at 30-70% of standard dose",
                "Homozygous: Start at 10% of dose or use alternative",
                "Risk of life-threatening bone marrow suppression",
                "MANDATORY testing before thiopurine therapy"
            ]
        }
    },
    "rs1800460": {
        "gene": "TPMT",
        "variant": "*3B",
        "function": "No function",
        "risk_allele": "A",
        "clinical_impact": "Severe myelosuppression risk"
    },
    "rs1800462": {
        "gene": "TPMT",
        "variant": "*2",
        "function": "No function",
        "risk_allele": "G",
        "clinical_impact": "Severe myelosuppression risk"
    },
    "rs116855232": {
        "gene": "NUDT15",
        "variant": "*3",
        "function": "No function",
        "risk_allele": "T",
        "frequency_eas": 0.10,
        "frequency_sas": 0.08,
        "drugs_affected": ["azathioprine", "mercaptopurine"],
        "clinical_impact": "Severe toxicity - especially important in Asian populations",
        "cpic_level": "1A",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "More important than TPMT in Asian populations",
                "Homozygous: Contraindicated at standard doses",
                "Heterozygous: 25-50% dose reduction"
            ]
        }
    },

    # =========================================================================
    # UGT1A1 - Irinotecan, Atazanavir
    # =========================================================================
    "rs8175347": {
        "gene": "UGT1A1",
        "variant": "*28 (TA repeat)",
        "function": "Decreased expression",
        "risk_allele": "7_repeats",
        "frequency_eur": 0.35,
        "drugs_affected": ["irinotecan", "atazanavir", "belinostat"],
        "clinical_impact": "Increased toxicity with irinotecan (neutropenia, diarrhea)",
        "cpic_level": "1A",
        "fda_label": "required",
        "note": "Also causes Gilbert syndrome (benign jaundice)",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Irinotecan: Consider dose reduction if *28/*28",
                "Atazanavir: Increased hyperbilirubinemia (usually benign)",
                "Gilbert syndrome (yellow eyes) is benign"
            ]
        }
    },
    "rs4148323": {
        "gene": "UGT1A1",
        "variant": "*6",
        "function": "Decreased function",
        "risk_allele": "A",
        "frequency_eas": 0.15,
        "note": "Important in East Asian populations"
    },

    # =========================================================================
    # SLCO1B1 - Statin Myopathy
    # =========================================================================
    "rs4149056": {
        "gene": "SLCO1B1",
        "variant": "*5",
        "function": "Decreased transport",
        "risk_allele": "C",
        "frequency_eur": 0.15,
        "drugs_affected": [
            "simvastatin",
            "atorvastatin", 
            "pravastatin",
            "rosuvastatin",
            "pitavastatin"
        ],
        "clinical_impact": "4.5x increased risk of simvastatin myopathy per C allele",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "CC genotype: Avoid simvastatin >20mg",
                "Consider pravastatin or rosuvastatin (lower risk)",
                "Monitor for muscle pain/weakness on any statin",
                "Check CK if muscle symptoms develop"
            ]
        }
    },
    "rs2306283": {
        "gene": "SLCO1B1",
        "variant": "*1b",
        "function": "Increased transport",
        "risk_allele": "G",
        "clinical_impact": "May partially offset *5 effect"
    },

    # =========================================================================
    # HLA Alleles - Severe Drug Reactions
    # =========================================================================
    "rs2395029": {
        "gene": "HLA-B*5701",
        "variant": "Tag SNP",
        "function": "HLA marker",
        "risk_allele": "G",
        "frequency_eur": 0.06,
        "drugs_affected": ["abacavir"],
        "clinical_impact": "Hypersensitivity reaction to abacavir (can be fatal)",
        "cpic_level": "1A",
        "fda_label": "boxed_warning",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "ABACAVIR IS CONTRAINDICATED if HLA-B*5701 positive",
                "Risk of severe, potentially fatal hypersensitivity",
                "Standard of care: Test before prescribing abacavir"
            ]
        }
    },
    "rs3909184": {
        "gene": "HLA-B*1502",
        "variant": "Tag SNP",
        "function": "HLA marker",
        "risk_allele": "A",
        "frequency_eas": 0.08,
        "frequency_sas": 0.05,
        "drugs_affected": ["carbamazepine", "oxcarbazepine", "phenytoin"],
        "clinical_impact": "Stevens-Johnson Syndrome / Toxic Epidermal Necrolysis",
        "cpic_level": "1A",
        "fda_label": "boxed_warning",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "CARBAMAZEPINE CONTRAINDICATED if HLA-B*1502 positive",
                "Risk of fatal Stevens-Johnson Syndrome (SJS/TEN)",
                "FDA recommends testing in Asian ancestry patients",
                "Consider alternative anticonvulsants"
            ]
        }
    },
    "rs1061235": {
        "gene": "HLA-A*3101",
        "variant": "Tag SNP",
        "function": "HLA marker",
        "risk_allele": "A",
        "frequency_eur": 0.03,
        "drugs_affected": ["carbamazepine"],
        "clinical_impact": "Drug reaction with eosinophilia (DRESS)",
        "cpic_level": "1A"
    },

    # =========================================================================
    # CYP2B6 - Efavirenz, Methadone
    # =========================================================================
    "rs3745274": {
        "gene": "CYP2B6",
        "variant": "*6",
        "function": "Decreased function",
        "risk_allele": "T",
        "frequency_eur": 0.25,
        "frequency_afr": 0.40,
        "drugs_affected": ["efavirenz", "methadone", "bupropion", "ketamine"],
        "clinical_impact": "Increased efavirenz plasma levels - CNS side effects",
        "cpic_level": "1A",
        "actionable": {
            "priority": "medium",
            "action_type": "medical_alert",
            "recommendations": [
                "Efavirenz: Consider lower dose (400mg vs 600mg)",
                "Increased risk of CNS side effects (vivid dreams, dizziness)",
                "Methadone: May need dose adjustment"
            ]
        }
    },
    "rs28399499": {
        "gene": "CYP2B6",
        "variant": "*18",
        "function": "Decreased function",
        "risk_allele": "C",
        "frequency_afr": 0.08
    },

    # =========================================================================
    # G6PD - Antimalarials, Sulfonamides
    # =========================================================================
    "rs1050828": {
        "gene": "G6PD",
        "variant": "V68M (A-)",
        "function": "Decreased activity",
        "risk_allele": "T",
        "frequency_afr": 0.20,
        "drugs_affected": [
            "primaquine", "dapsone", "rasburicase",
            "methylene blue", "sulfonamides", "nitrofurantoin"
        ],
        "clinical_impact": "Hemolytic anemia with oxidative drugs",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "AVOID primaquine, dapsone, rasburicase",
                "Risk of severe hemolytic anemia",
                "Check G6PD activity before antimalarials",
                "X-linked: Males more severely affected"
            ]
        }
    },
    "rs5030868": {
        "gene": "G6PD",
        "variant": "S188F (Mediterranean)",
        "function": "Severely decreased activity",
        "risk_allele": "A",
        "frequency_mena": 0.05,
        "clinical_impact": "Severe G6PD deficiency"
    },

    # =========================================================================
    # NAT2 - Isoniazid, Hydralazine
    # =========================================================================
    "rs1801280": {
        "gene": "NAT2",
        "variant": "*5",
        "function": "Slow acetylator",
        "risk_allele": "A",
        "frequency_eur": 0.45,
        "drugs_affected": ["isoniazid", "hydralazine", "procainamide", "sulfasalazine"],
        "clinical_impact": "Slow acetylators: increased drug-induced lupus, hepatotoxicity",
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Isoniazid: increased hepatotoxicity risk in slow acetylators",
                "Hydralazine: increased lupus-like syndrome risk",
                "Monitor liver function on isoniazid"
            ]
        }
    },
    "rs1799930": {
        "gene": "NAT2",
        "variant": "*6",
        "function": "Slow acetylator",
        "risk_allele": "A"
    },
    "rs1799931": {
        "gene": "NAT2",
        "variant": "*7",
        "function": "Slow acetylator",
        "risk_allele": "A"
    },

    # =========================================================================
    # IFNL3/IL28B - Hepatitis C Treatment
    # =========================================================================
    "rs12979860": {
        "gene": "IFNL3",
        "variant": "IL28B",
        "function": "Treatment response",
        "risk_allele": "T",
        "drugs_affected": ["peginterferon alfa", "ribavirin"],
        "clinical_impact": "CC genotype: better response to HCV treatment",
        "note": "Less relevant with modern DAA therapies",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "CC: Better response to interferon-based HCV treatment",
                "Less relevant with modern direct-acting antivirals"
            ]
        }
    },

    # =========================================================================
    # F5 and F2 - Hormonal Contraceptives
    # =========================================================================
    "rs6025": {
        "gene": "F5",
        "variant": "Factor V Leiden",
        "function": "Resistance to activated protein C",
        "risk_allele": "A",
        "frequency_eur": 0.05,
        "drugs_affected": ["estrogen-containing contraceptives", "HRT"],
        "clinical_impact": "7x increased VTE risk; 35x with estrogen contraceptives",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "AVOID estrogen-containing contraceptives",
                "Use progestin-only or non-hormonal methods",
                "Inform providers before surgery/immobilization",
                "Risk of deep vein thrombosis/pulmonary embolism"
            ]
        }
    },
    "rs1799963": {
        "gene": "F2",
        "variant": "Prothrombin G20210A",
        "function": "Increased prothrombin levels",
        "risk_allele": "A",
        "frequency_eur": 0.02,
        "drugs_affected": ["estrogen-containing contraceptives", "HRT"],
        "clinical_impact": "3x increased VTE risk; multiplicative with estrogen",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "AVOID estrogen-containing contraceptives",
                "Use progestin-only or non-hormonal methods",
                "Genetic counseling recommended"
            ]
        }
    },

    # =========================================================================
    # CFTR - Ivacaftor Response
    # =========================================================================
    "rs75527207": {
        "gene": "CFTR",
        "variant": "G551D",
        "function": "Gating mutation",
        "risk_allele": "A",
        "drugs_affected": ["ivacaftor (Kalydeco)"],
        "clinical_impact": "Ivacaftor highly effective for this mutation",
        "cpic_level": "1A",
        "fda_label": "required",
        "actionable": {
            "priority": "high",
            "action_type": "treatment_option",
            "recommendations": [
                "Ivacaftor approved and effective for G551D",
                "Discuss with CF specialist"
            ]
        }
    },

    # =========================================================================
    # RYR1 - Malignant Hyperthermia
    # =========================================================================
    "rs121918592": {
        "gene": "RYR1",
        "variant": "R614C",
        "function": "Malignant hyperthermia susceptibility",
        "risk_allele": "T",
        "drugs_affected": ["succinylcholine", "volatile anesthetics (sevoflurane, desflurane)"],
        "clinical_impact": "Life-threatening reaction to anesthesia",
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "AVOID succinylcholine and volatile anesthetics",
                "Dantrolene must be available if anesthesia required",
                "Medical alert bracelet recommended",
                "Inform ALL healthcare providers"
            ]
        }
    },
}

# Drug interaction summary for agents
DRUG_INTERACTIONS = {
    "warfarin": {
        "genes": ["CYP2C9", "VKORC1", "CYP4F2"],
        "snps": ["rs1799853", "rs1057910", "rs9923231", "rs2108622"],
        "clinical_note": "Use FDA dosing algorithm combining all variants",
        "url": "https://warfarindosing.org"
    },
    "clopidogrel": {
        "genes": ["CYP2C19"],
        "snps": ["rs4244285", "rs4986893", "rs12248560"],
        "clinical_note": "Poor metabolizers should use prasugrel or ticagrelor"
    },
    "simvastatin": {
        "genes": ["SLCO1B1"],
        "snps": ["rs4149056"],
        "clinical_note": "CC genotype: max 20mg/day, consider alternative statin"
    },
    "codeine": {
        "genes": ["CYP2D6"],
        "snps": ["rs3892097", "rs5030655", "rs28371725"],
        "clinical_note": "Poor metabolizers: codeine ineffective. Ultrarapid: toxicity risk"
    },
    "tamoxifen": {
        "genes": ["CYP2D6"],
        "snps": ["rs3892097", "rs5030655", "rs28371725"],
        "clinical_note": "Poor metabolizers may have reduced efficacy"
    },
    "tacrolimus": {
        "genes": ["CYP3A5"],
        "snps": ["rs776746"],
        "clinical_note": "Expressers (*1/*1) need higher doses"
    },
    "azathioprine": {
        "genes": ["TPMT", "NUDT15"],
        "snps": ["rs1142345", "rs1800460", "rs116855232"],
        "clinical_note": "Test BOTH genes. NUDT15 especially important in Asians"
    },
    "5-fluorouracil": {
        "genes": ["DPYD"],
        "snps": ["rs3918290", "rs55886062", "rs67376798"],
        "clinical_note": "MANDATORY testing. Potentially fatal toxicity in poor metabolizers"
    },
    "abacavir": {
        "genes": ["HLA-B*5701"],
        "snps": ["rs2395029"],
        "clinical_note": "CONTRAINDICATED if positive. Hypersensitivity can be fatal"
    },
    "carbamazepine": {
        "genes": ["HLA-B*1502", "HLA-A*3101"],
        "snps": ["rs3909184", "rs1061235"],
        "clinical_note": "Test HLA-B*1502 in Asian ancestry. Risk of SJS/TEN"
    }
}
