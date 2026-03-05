"""
Trait Markers
Source: GWAS Catalog, 23andMe research

Physical, sensory, and behavioral traits.
These are fun/interesting but generally not medically actionable.
"""

TRAIT_MARKERS = {
    # =========================================================================
    # PHYSICAL APPEARANCE
    # =========================================================================
    "rs12913832": {
        "gene": "HERC2/OCA2",
        "trait": "Eye Color (Blue vs Brown)",
        "effect_allele": "A",
        "effect": "AA = ~85% chance blue eyes. GG = brown eyes likely.",
        "heritability": 0.90,
        "note": "Single strongest eye color determinant"
    },
    "rs1129038": {
        "gene": "HERC2",
        "trait": "Eye Color",
        "effect_allele": "A",
        "effect": "Blue eye association"
    },
    "rs1667394": {
        "gene": "OCA2",
        "trait": "Eye Color (Green/Hazel)",
        "effect_allele": "A",
        "effect": "Associated with lighter eyes"
    },
    "rs12896399": {
        "gene": "SLC24A4",
        "trait": "Eye Color",
        "effect_allele": "T",
        "effect": "Green/hazel association"
    },
    
    "rs12821256": {
        "gene": "KITLG",
        "trait": "Hair Color (Blonde)",
        "effect_allele": "C",
        "effect": "Associated with blonde hair"
    },
    "rs1805007": {
        "gene": "MC1R",
        "trait": "Red Hair / Fair Skin",
        "effect_allele": "T",
        "effect": "Strong red hair association",
        "note": "Also increased sun sensitivity and skin cancer risk"
    },
    "rs1805008": {
        "gene": "MC1R",
        "trait": "Red Hair",
        "effect_allele": "T",
        "effect": "Red hair association"
    },
    "rs1805009": {
        "gene": "MC1R",
        "trait": "Red Hair",
        "effect_allele": "C",
        "effect": "Red hair association"
    },
    "rs11547464": {
        "gene": "MC1R",
        "trait": "Red Hair / Freckling",
        "effect_allele": "A",
        "effect": "Red hair and freckling"
    },
    "rs4778138": {
        "gene": "OCA2",
        "trait": "Freckling",
        "effect_allele": "A",
        "effect": "Increased freckling"
    },
    
    "rs17822931": {
        "gene": "ABCC11",
        "trait": "Earwax Type / Body Odor",
        "effect_allele": "T",
        "effect": "TT = dry earwax, less body odor. CC = wet earwax, more body odor.",
        "note": "TT common in East Asia (80-95%), CC common elsewhere",
        "actionable": {
            "priority": "informational",
            "note": "TT genotype: May not need deodorant as strongly"
        }
    },
    
    "rs3827760": {
        "gene": "EDAR",
        "trait": "Hair Thickness / Tooth Shape",
        "effect_allele": "A",
        "effect": "Thicker hair, shovel-shaped incisors",
        "note": "Near-universal in East Asian/Native American ancestry"
    },
    
    "rs1042602": {
        "gene": "TYR",
        "trait": "Skin Pigmentation",
        "effect_allele": "A",
        "effect": "Lighter skin"
    },
    "rs1426654": {
        "gene": "SLC24A5",
        "trait": "Skin Pigmentation",
        "effect_allele": "A",
        "effect": "Lighter skin (nearly fixed in Europeans)"
    },
    "rs16891982": {
        "gene": "SLC45A2",
        "trait": "Skin/Hair Pigmentation",
        "effect_allele": "C",
        "effect": "Lighter skin and hair"
    },
    
    "rs2228479": {
        "gene": "MC1R",
        "trait": "Sun Sensitivity",
        "effect_allele": "A",
        "effect": "Increased sun sensitivity"
    },
    
    "rs7349332": {
        "gene": "FGFR2",
        "trait": "Male Pattern Baldness",
        "effect_allele": "T",
        "effect": "Increased baldness risk"
    },
    "rs2180439": {
        "gene": "20p11",
        "trait": "Male Pattern Baldness",
        "effect_allele": "T",
        "effect": "Increased baldness risk"
    },
    "rs6152": {
        "gene": "AR",
        "trait": "Male Pattern Baldness",
        "effect_allele": "A",
        "effect": "Androgen receptor - baldness association",
        "note": "X-linked - often inherited from maternal grandfather"
    },
    
    "rs4778241": {
        "gene": "OCA2",
        "trait": "Tan Response",
        "effect_allele": "A",
        "effect": "Tendency to burn rather than tan"
    },

    # =========================================================================
    # HEIGHT & BODY COMPOSITION
    # =========================================================================
    "rs1042725": {
        "gene": "HMGA2",
        "trait": "Height",
        "effect_allele": "C",
        "effect": "+0.4 cm per allele"
    },
    "rs6060373": {
        "gene": "GDF5-UQCC",
        "trait": "Height",
        "effect_allele": "T",
        "effect": "Height reduction"
    },
    "rs724016": {
        "gene": "ZBTB38",
        "trait": "Height",
        "effect_allele": "A",
        "effect": "Height increase"
    },

    # =========================================================================
    # SENSORY / TASTE
    # =========================================================================
    "rs713598": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste (PTC/PROP)",
        "effect_allele": "C",
        "effect": "Taster phenotype",
        "note": "PAV haplotype = supertaster, AVI = non-taster"
    },
    "rs1726866": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste",
        "effect_allele": "T",
        "effect": "Taster phenotype"
    },
    "rs10246939": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste",
        "effect_allele": "C",
        "effect": "Taster phenotype",
        "actionable": {
            "priority": "informational",
            "note": "PAV/PAV: Bitter foods (brussels sprouts, grapefruit) taste very bitter"
        }
    },
    
    "rs4481887": {
        "gene": "OR6A2",
        "trait": "Cilantro Taste (Soap)",
        "effect_allele": "A",
        "effect": "Cilantro tastes like soap",
        "note": "~15% of people have this aversion"
    },
    
    "rs2274333": {
        "gene": "CA6",
        "trait": "Sweet Taste Sensitivity",
        "effect_allele": "A",
        "effect": "Altered sweet taste perception"
    },
    
    "rs35744813": {
        "gene": "TRPA1",
        "trait": "Wasabi/Mustard Sensitivity",
        "effect_allele": "T",
        "effect": "Altered sensitivity to pungent foods"
    },
    
    "rs236514": {
        "gene": "OR10A2",
        "trait": "Asparagus Urine Smell",
        "effect_allele": "A",
        "effect": "Can smell asparagus metabolite in urine",
        "note": "About 40% cannot smell it"
    },

    # =========================================================================
    # SLEEP & CIRCADIAN
    # =========================================================================
    "rs1801260": {
        "gene": "CLOCK",
        "trait": "Chronotype (Morning/Evening)",
        "effect_allele": "C",
        "effect": "CC = more evening preference",
        "actionable": {
            "priority": "low",
            "note": "If evening type, try light therapy in morning"
        }
    },
    "rs57875989": {
        "gene": "PER2",
        "trait": "Advanced Sleep Phase",
        "effect_allele": "G",
        "effect": "Extreme morning person (rare)",
        "note": "FASPS - wake 4-5am naturally"
    },
    "rs12927162": {
        "gene": "ADA",
        "trait": "Sleep Depth",
        "effect_allele": "T",
        "effect": "Deeper sleep, more slow-wave activity"
    },
    "rs73598374": {
        "gene": "ADA",
        "trait": "Caffeine-Induced Insomnia",
        "effect_allele": "A",
        "effect": "More sensitive to caffeine disrupting sleep"
    },

    # =========================================================================
    # BEHAVIORAL
    # =========================================================================
    "rs6265": {
        "gene": "BDNF",
        "trait": "Memory & Learning",
        "effect_allele": "T",
        "effect": "Val66Met - reduced activity-dependent BDNF secretion",
        "note": "Met carriers may benefit more from exercise for cognition"
    },
    "rs4680": {
        "gene": "COMT",
        "trait": "Stress Response / Cognition",
        "effect_allele": "A",
        "effect": "Met/Met = 'Worrier' (better working memory, more stress sensitive). Val/Val = 'Warrior' (stress resilient, faster processing)",
        "note": "Context-dependent advantage"
    },
    "rs1800497": {
        "gene": "DRD2/ANKK1",
        "trait": "Dopamine Signaling",
        "effect_allele": "A",
        "effect": "Reduced D2 receptor density",
        "note": "Associated with novelty-seeking, addiction susceptibility"
    },
    "rs53576": {
        "gene": "OXTR",
        "trait": "Empathy / Social Behavior",
        "effect_allele": "G",
        "effect": "GG = higher empathy scores, more social sensitivity"
    },
    "rs25531": {
        "gene": "SLC6A4",
        "trait": "Serotonin Transporter",
        "effect_allele": "G",
        "effect": "Long allele variant - affects 5-HTT expression",
        "note": "Gene x Environment for depression (controversial)"
    },
    
    # =========================================================================
    # ALCOHOL
    # =========================================================================
    "rs671": {
        "gene": "ALDH2",
        "trait": "Alcohol Flush Reaction",
        "effect_allele": "A",
        "effect": "AA = severe flush, nausea. AG = moderate flush.",
        "note": "Common in East Asians. ASSOCIATED WITH ESOPHAGEAL CANCER if drinking despite flush.",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "If you flush with alcohol (AG or AA), AVOID or limit alcohol",
                "Flushing indicates acetaldehyde buildup",
                "Increased esophageal cancer risk if drinking despite flush"
            ]
        }
    },
    "rs1229984": {
        "gene": "ADH1B",
        "trait": "Alcohol Metabolism Speed",
        "effect_allele": "T",
        "effect": "Fast alcohol metabolism (protective against alcoholism)",
        "note": "Common in East Asians - may contribute to lower alcoholism rates"
    },
    
    # =========================================================================
    # MISCELLANEOUS
    # =========================================================================
    "rs4988235": {
        "gene": "MCM6/LCT",
        "trait": "Lactose Tolerance",
        "effect_allele": "A",
        "effect": "AA/AG = lactase persistent (can digest dairy). GG = lactase non-persistent.",
        "note": "GG is ancestral; lactase persistence evolved with dairy farming"
    },
    "rs182549": {
        "gene": "MCM6/LCT",
        "trait": "Lactose Tolerance (European)",
        "effect_allele": "T",
        "effect": "European lactase persistence variant"
    },
    
    "rs7412": {
        "gene": "APOE",
        "trait": "Lipid Metabolism / Longevity",
        "effect_allele": "T",
        "effect": "TT = ε2 allele (protective against AD, but higher triglycerides)"
    },
    
    "rs4778232": {
        "gene": "BNC2",
        "trait": "Skin Aging / Wrinkles",
        "effect_allele": "A",
        "effect": "Tendency toward facial wrinkles"
    },
    
    "rs11803731": {
        "gene": "TRICHOHYALIN",
        "trait": "Hair Curl",
        "effect_allele": "A",
        "effect": "Straighter hair"
    },
    
    "rs2294008": {
        "gene": "PSCA",
        "trait": "Stomach Cancer Risk / Blood Type",
        "effect_allele": "T",
        "effect": "Increased stomach cancer risk (especially with H. pylori)"
    },
    
    "rs2032582": {
        "gene": "ABCB1",
        "trait": "Drug Transport / P-glycoprotein",
        "effect_allele": "T",
        "effect": "Altered drug transport across blood-brain barrier"
    },
    
    "rs2066702": {
        "gene": "OPRM1",
        "trait": "Opioid Sensitivity",
        "effect_allele": "G",
        "effect": "May require higher opioid doses for pain control"
    },
    
    "rs1800955": {
        "gene": "DRD4",
        "trait": "Novelty Seeking",
        "effect_allele": "T",
        "effect": "Associated with novelty seeking behavior"
    },
    
    "rs6311": {
        "gene": "HTR2A",
        "trait": "Serotonin Receptor",
        "effect_allele": "T",
        "effect": "Altered serotonin signaling"
    },
    
    "rs4570625": {
        "gene": "TPH2",
        "trait": "Anxiety/Amygdala Reactivity",
        "effect_allele": "G",
        "effect": "Increased amygdala reactivity to emotional stimuli"
    },
    
    "rs1800629": {
        "gene": "TNF",
        "trait": "Inflammation Response",
        "effect_allele": "A",
        "effect": "Higher TNF-alpha production"
    },
}
