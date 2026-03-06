"""
Fitness & Athletic Performance Markers
Source: Literature, GWAS

Genetic variants affecting athletic performance, recovery, and injury risk.
"""

FITNESS_MARKERS = {
    # =========================================================================
    # MUSCLE FIBER TYPE / POWER vs ENDURANCE
    # =========================================================================
    "rs1815739": {
        "gene": "ACTN3",
        "trait": "Muscle Fiber Type (Sprint/Power)",
        "variant": "R577X",
        "effect_allele": "T",
        "effect": {
            "CC": "Full alpha-actinin-3 - sprinter/power athlete advantage",
            "CT": "Intermediate - versatile",
            "TT": "No alpha-actinin-3 - endurance advantage, sprint disadvantage"
        },
        "evidence": "strong",
        "note": "~18% of world population is TT. More common in endurance athletes.",
        "actionable": {
            "priority": "informational",
            "recommendations": [
                "TT: May excel at endurance sports",
                "CC: May have edge in power/sprint events",
                "CT: Versatile, can train either direction"
            ]
        }
    },
    
    "rs1799752": {
        "gene": "ACE",
        "trait": "Endurance vs Power (I/D)",
        "variant": "Insertion/Deletion",
        "effect_allele": "D",
        "effect": {
            "II": "Lower ACE activity - endurance advantage",
            "ID": "Intermediate",
            "DD": "Higher ACE activity - power/strength advantage"
        },
        "evidence": "moderate",
        "note": "I allele overrepresented in elite endurance athletes"
    },
    
    "rs4253778": {
        "gene": "PPARA",
        "trait": "Endurance Capacity",
        "effect_allele": "G",
        "effect": "G allele associated with endurance performance",
        "note": "Affects fat oxidation during exercise"
    },
    
    "rs8192678": {
        "gene": "PPARGC1A",
        "trait": "Endurance/Mitochondrial Biogenesis",
        "variant": "Gly482Ser",
        "effect_allele": "A",
        "effect": "Gly/Gly (GG) associated with higher VO2max potential",
        "note": "PGC-1α is master regulator of mitochondrial biogenesis"
    },

    # =========================================================================
    # VO2 MAX / AEROBIC CAPACITY
    # =========================================================================
    "rs699": {
        "gene": "AGT",
        "trait": "Blood Pressure / VO2max",
        "variant": "M235T",
        "effect_allele": "C",
        "effect": "TT genotype may have lower VO2max trainability"
    },
    
    "rs7181866": {
        "gene": "VEGFA",
        "trait": "Angiogenesis / VO2max",
        "effect_allele": "A",
        "effect": "Affects vascular adaptation to training"
    },
    
    "rs2016520": {
        "gene": "PPARD",
        "trait": "Fat Oxidation / Endurance",
        "effect_allele": "C",
        "effect": "C allele associated with improved endurance capacity"
    },
    
    "rs660339": {
        "gene": "UCP2",
        "trait": "Metabolic Efficiency",
        "effect_allele": "T",
        "effect": "Affects energy efficiency during exercise"
    },

    # =========================================================================
    # STRENGTH / POWER
    # =========================================================================
    "rs1800169": {
        "gene": "CILP",
        "trait": "Cartilage / Strength Training",
        "effect_allele": "T",
        "effect": "May affect response to strength training"
    },
    
    "rs2275998": {
        "gene": "TRHR",
        "trait": "Lean Body Mass",
        "effect_allele": "T",
        "effect": "Associated with lean body mass"
    },
    
    "rs10497520": {
        "gene": "TTN",
        "trait": "Muscle Stiffness",
        "effect_allele": "T",
        "effect": "Titin variant affecting muscle properties"
    },

    # =========================================================================
    # INJURY RISK
    # =========================================================================
    "rs12722": {
        "gene": "COL5A1",
        "trait": "Tendon/Ligament Injury",
        "variant": "BstUI RFLP",
        "effect_allele": "T",
        "effect": "TT genotype: increased Achilles tendinopathy risk",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "Gradual training progression",
                "Adequate warm-up",
                "Eccentric strengthening for tendons"
            ]
        }
    },
    
    "rs143383": {
        "gene": "GDF5",
        "trait": "Joint/Cartilage Health",
        "effect_allele": "T",
        "effect": "Increased osteoarthritis risk",
        "note": "Also affects height slightly"
    },
    
    "rs1800012": {
        "gene": "COL1A1",
        "trait": "Bone/Soft Tissue",
        "variant": "Sp1 binding site",
        "effect_allele": "T",
        "effect": "TT genotype: slightly increased ACL injury risk"
    },
    
    "rs35068180": {
        "gene": "MMP3",
        "trait": "Achilles Tendinopathy",
        "effect_allele": "A",
        "effect": "5A/5A genotype: increased tendinopathy risk"
    },
    
    "rs679620": {
        "gene": "MMP3",
        "trait": "Disc Degeneration",
        "effect_allele": "A",
        "effect": "Increased disc degeneration risk"
    },

    # =========================================================================
    # RECOVERY
    # =========================================================================
    "rs1800629": {
        "gene": "TNF",
        "trait": "Inflammation/Recovery",
        "variant": "-308 G>A",
        "effect_allele": "A",
        "effect": "AA genotype: higher TNF-alpha, more inflammation",
        "actionable": {
            "priority": "low",
            "recommendations": [
                "Anti-inflammatory diet (omega-3, turmeric)",
                "Adequate sleep crucial",
                "May need more recovery time"
            ]
        }
    },
    
    "rs1800795": {
        "gene": "IL6",
        "trait": "Recovery/Inflammation",
        "variant": "-174 G>C",
        "effect_allele": "C",
        "effect": "CC genotype: higher IL-6 production"
    },
    
    "rs2069762": {
        "gene": "IL2",
        "trait": "Immune Recovery",
        "effect_allele": "T",
        "effect": "Altered immune response post-exercise"
    },
    
    "rs4961": {
        "gene": "ADD1",
        "trait": "Salt Sensitivity / BP Recovery",
        "effect_allele": "T",
        "effect": "Salt-sensitive blood pressure",
        "note": "May affect BP response to exercise in heat"
    },

    # =========================================================================
    # EXERCISE RESPONSE
    # =========================================================================
    "rs6265": {
        "gene": "BDNF",
        "trait": "Exercise-Cognition Response",
        "variant": "Val66Met",
        "effect_allele": "T",
        "effect": "Met carriers may get MORE cognitive benefit from exercise",
        "note": "Exercise increases BDNF, compensating for lower baseline"
    },
    
    "rs8192678": {
        "gene": "PPARGC1A",
        "trait": "Training Adaptability",
        "effect_allele": "A",
        "effect": "May affect how well you adapt to endurance training"
    },
    
    "rs2070744": {
        "gene": "NOS3",
        "trait": "Blood Flow/Endurance",
        "variant": "-786T>C",
        "effect_allele": "C",
        "effect": "CC genotype: lower NO production, may affect blood flow"
    },
    
    "rs2104772": {
        "gene": "TNC",
        "trait": "Training Response",
        "effect_allele": "T",
        "effect": "Affects extracellular matrix adaptation"
    },

    # =========================================================================
    # PAIN / FATIGUE
    # =========================================================================
    "rs6746030": {
        "gene": "SCN9A",
        "trait": "Pain Sensitivity",
        "effect_allele": "A",
        "effect": "AA genotype: increased pain sensitivity"
    },
    
    "rs4680": {
        "gene": "COMT",
        "trait": "Pain/Stress Response",
        "variant": "Val158Met",
        "effect_allele": "A",
        "effect": "Met/Met (AA): higher pain sensitivity, but better pain medication response"
    },
    
    "rs2066702": {
        "gene": "OPRM1",
        "trait": "Opioid/Pain Response",
        "effect_allele": "G",
        "effect": "AG/GG may need higher pain medication doses"
    },

    # =========================================================================
    # BODY COMPOSITION RESPONSE
    # =========================================================================
    "rs9939609": {
        "gene": "FTO",
        "trait": "Exercise vs Obesity",
        "effect_allele": "A",
        "effect": "AA genotype: higher obesity risk BUT exercise reduces this more",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Exercise is especially important for FTO risk carriers",
                "Physical activity attenuates genetic obesity risk by ~30%"
            ]
        }
    },
    
    "rs7498665": {
        "gene": "SH2B1",
        "trait": "BMI Response to Exercise",
        "effect_allele": "A",
        "effect": "Affects body composition response to exercise"
    },

    # =========================================================================
    # CAFFEINE / ERGOGENIC AIDS
    # =========================================================================
    "rs762551": {
        "gene": "CYP1A2",
        "trait": "Caffeine Metabolism",
        "effect_allele": "C",
        "effect": "CC = slow metabolizer. AC/AA = fast metabolizer.",
        "actionable": {
            "priority": "informational",
            "recommendations": [
                "Fast metabolizers (AA): caffeine more ergogenic for performance",
                "Slow metabolizers (CC): caffeine may not help, could increase cardiac risk",
                "Time caffeine 60min before exercise for fast metabolizers"
            ]
        }
    },
    
    "rs1800497": {
        "gene": "DRD2",
        "trait": "Motivation/Reward",
        "effect_allele": "A",
        "effect": "A1 allele: may need more external motivation for exercise adherence"
    },
}
