"""
Trait markers database.
Non-health phenotypic traits.
"""

TRAIT_MARKERS = {
    # =========================================================================
    # PIGMENTATION
    # =========================================================================
    
    "rs12913832": {
        "gene": "HERC2/OCA2",
        "trait": "eye_color",
        "category": "pigmentation",
        "interpretation": {
            "GG": "Blue eyes likely",
            "AG": "Green/hazel likely, or blue possible",
            "AA": "Brown eyes likely"
        },
        "references": ["PMID:18172690", "PMID:17952075"]
    },
    
    "rs16891982": {
        "gene": "SLC45A2",
        "trait": "skin_pigmentation",
        "category": "pigmentation",
        "interpretation": {
            "GG": "Light skin (European)",
            "CG": "Intermediate",
            "CC": "Darker pigmentation"
        },
        "references": ["PMID:16357253"]
    },
    
    "rs1426654": {
        "gene": "SLC24A5",
        "trait": "skin_pigmentation",
        "category": "pigmentation",
        "interpretation": {
            "AA": "Light skin (nearly fixed in Europeans)",
            "AG": "Intermediate",
            "GG": "Darker pigmentation (ancestral)"
        },
        "references": ["PMID:16357253", "PMID:15883587"]
    },
    
    "rs1805007": {
        "gene": "MC1R",
        "trait": "red_hair",
        "category": "pigmentation",
        "interpretation": {
            "TT": "R151C variant (red hair, fair skin, freckling)",
            "CT": "Carrier (may have red highlights, freckles)",
            "CC": "No R151C variant"
        },
        "references": ["PMID:11260714"]
    },
    
    "rs1805008": {
        "gene": "MC1R",
        "trait": "red_hair",
        "category": "pigmentation",
        "interpretation": {
            "TT": "R160W variant (red hair, fair skin)",
            "CT": "Carrier",
            "CC": "No R160W variant"
        },
        "references": ["PMID:11260714"]
    },
    
    # =========================================================================
    # TASTE AND SMELL
    # =========================================================================
    
    "rs671": {
        "gene": "ALDH2",
        "trait": "alcohol_flush",
        "category": "metabolism",
        "interpretation": {
            "AA": "ALDH2*2 homozygote (severe flush, very low alcohol tolerance)",
            "AG": "Heterozygote (moderate flush reaction)",
            "GG": "Normal ALDH2 (no flush reaction)"
        },
        "notes": "Common in East Asian populations. AA genotype protective against alcoholism but increases esophageal cancer risk with alcohol.",
        "references": ["PMID:10379521"]
    },
    
    "rs1229984": {
        "gene": "ADH1B",
        "trait": "alcohol_metabolism",
        "category": "metabolism",
        "interpretation": {
            "TT": "Fast alcohol metabolizer (protective against alcoholism)",
            "CT": "Intermediate",
            "CC": "Normal metabolism"
        },
        "references": ["PMID:19384953"]
    },
    
    # =========================================================================
    # OTHER TRAITS
    # =========================================================================
    
    "rs4988235": {
        "gene": "LCT/MCM6",
        "trait": "lactase_persistence",
        "category": "digestion",
        "interpretation": {
            "AA": "Lactase persistent (can digest lactose as adult)",
            "AG": "Lactase persistent (can digest lactose)",
            "GG": "Lactase non-persistent (likely lactose intolerant)"
        },
        "notes": "The A allele arose in European pastoral populations. GG is ancestral and common in East Asian, African, and Native American populations.",
        "references": ["PMID:14681826", "PMID:15106124"]
    },
    
    "rs17822931": {
        "gene": "ABCC11",
        "trait": "earwax_type",
        "category": "other",
        "interpretation": {
            "TT": "Dry earwax (common in East Asian populations)",
            "CT": "Intermediate/wet",
            "CC": "Wet earwax (common in European/African populations)"
        },
        "notes": "Also affects body odor. TT genotype associated with reduced body odor.",
        "references": ["PMID:16444273"]
    },
}
