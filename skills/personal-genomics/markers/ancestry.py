"""
Ancestry Informative Markers (AIMs)
SNPs with high population differentiation for ancestry inference.
"""

# Ancestry Informative Markers from various studies
ANCESTRY_MARKERS = {
    # =========================================================================
    # PIGMENTATION (Highly ancestry-informative)
    # =========================================================================
    "rs1426654": {"gene": "SLC24A5", "trait": "Skin pigmentation", "eur_freq": 0.99, "afr_freq": 0.02, "ancestry_info": True},
    "rs16891982": {"gene": "SLC45A2", "trait": "Skin/hair pigmentation", "eur_freq": 0.96, "afr_freq": 0.02, "ancestry_info": True},
    "rs1042602": {"gene": "TYR", "trait": "Skin pigmentation", "eur_freq": 0.60, "afr_freq": 0.05, "ancestry_info": True},
    "rs12913832": {"gene": "HERC2", "trait": "Blue eyes", "eur_freq": 0.40, "afr_freq": 0.02, "ancestry_info": True},
    "rs1800407": {"gene": "OCA2", "trait": "Eye color", "eur_freq": 0.15, "afr_freq": 0.01, "ancestry_info": True},
    "rs1805007": {"gene": "MC1R", "trait": "Red hair", "eur_freq": 0.12, "afr_freq": 0.001, "ancestry_info": True},
    "rs1805008": {"gene": "MC1R", "trait": "Red hair", "eur_freq": 0.10, "afr_freq": 0.001, "ancestry_info": True},
    "rs2228479": {"gene": "MC1R", "trait": "Fair skin", "eur_freq": 0.08, "afr_freq": 0.01, "ancestry_info": True},
    
    # =========================================================================
    # EUROPEAN-SPECIFIC
    # =========================================================================
    "rs4988235": {"gene": "LCT", "trait": "Lactase persistence", "eur_freq": 0.75, "afr_freq": 0.05, "eas_freq": 0.01,
        "note": "Evolved with dairy farming ~7500 years ago in Europe"},
    "rs182549": {"gene": "MCM6", "trait": "Lactase persistence (EUR)", "eur_freq": 0.75, "afr_freq": 0.05, "ancestry_info": True},
    "rs1393350": {"gene": "TYR", "trait": "Light coloring", "eur_freq": 0.35, "afr_freq": 0.03, "ancestry_info": True},
    "rs12896399": {"gene": "SLC24A4", "trait": "Hair color", "eur_freq": 0.45, "afr_freq": 0.05, "ancestry_info": True},
    "rs12821256": {"gene": "KITLG", "trait": "Blonde hair", "eur_freq": 0.15, "afr_freq": 0.01, "ancestry_info": True},
    "rs28777": {"gene": "SLC45A2", "trait": "Skin pigmentation", "eur_freq": 0.98, "afr_freq": 0.05, "ancestry_info": True},
    "rs35391": {"gene": "TYRP1", "trait": "Pigmentation", "eur_freq": 0.70, "afr_freq": 0.20, "ancestry_info": True},
    "rs683": {"gene": "TYRP1", "trait": "Hair color", "eur_freq": 0.65, "afr_freq": 0.30, "ancestry_info": True},
    
    # =========================================================================
    # EAST ASIAN-SPECIFIC
    # =========================================================================
    "rs3827760": {"gene": "EDAR", "trait": "Hair thickness, tooth shape", "eas_freq": 0.90, "eur_freq": 0.01, "afr_freq": 0.01,
        "note": "Near-universal in East Asian ancestry"},
    "rs17822931": {"gene": "ABCC11", "trait": "Dry earwax", "eas_freq": 0.90, "eur_freq": 0.10, "afr_freq": 0.05,
        "note": "Dry earwax common in East/Northeast Asia"},
    "rs671": {"gene": "ALDH2", "trait": "Alcohol flush", "eas_freq": 0.30, "eur_freq": 0.001, "afr_freq": 0.001,
        "note": "Alcohol flush reaction, common in East Asians"},
    "rs1229984": {"gene": "ADH1B", "trait": "Fast alcohol metabolism", "eas_freq": 0.70, "eur_freq": 0.05, "afr_freq": 0.02,
        "note": "Protective against alcoholism"},
    "rs1065852": {"gene": "CYP2D6", "trait": "Drug metabolism", "eas_freq": 0.40, "eur_freq": 0.02, "note": "CYP2D6*10"},
    "rs4646903": {"gene": "CYP1A1", "trait": "Metabolism", "eas_freq": 0.35, "eur_freq": 0.10, "ancestry_info": True},
    "rs4149056": {"gene": "SLCO1B1", "trait": "Drug transport", "eas_freq": 0.15, "eur_freq": 0.15, "afr_freq": 0.02},
    "rs116855232": {"gene": "NUDT15", "trait": "Thiopurine sensitivity", "eas_freq": 0.10, "eur_freq": 0.001,
        "note": "Important for azathioprine dosing in Asian populations"},
    
    # =========================================================================
    # AFRICAN-SPECIFIC
    # =========================================================================
    "rs334": {"gene": "HBB", "trait": "Sickle cell", "afr_freq": 0.08, "eur_freq": 0.001, "eas_freq": 0.001,
        "note": "Malaria resistance in heterozygotes"},
    "rs73885319": {"gene": "APOL1", "trait": "G1 kidney risk", "afr_freq": 0.22, "eur_freq": 0.001,
        "note": "Kidney disease risk, trypanosome resistance"},
    "rs60910145": {"gene": "APOL1", "trait": "G2 kidney risk", "afr_freq": 0.13, "eur_freq": 0.001},
    "rs1050828": {"gene": "G6PD", "trait": "G6PD A-", "afr_freq": 0.20, "eur_freq": 0.001, "note": "Malaria resistance"},
    "rs28371706": {"gene": "CYP2D6", "trait": "Drug metabolism", "afr_freq": 0.20, "eur_freq": 0.001, "note": "CYP2D6*17"},
    "rs7900194": {"gene": "CYP2C9", "trait": "Warfarin metabolism", "afr_freq": 0.06, "eur_freq": 0.001, "note": "CYP2C9*8"},
    "rs28399499": {"gene": "CYP2B6", "trait": "Efavirenz metabolism", "afr_freq": 0.08, "eur_freq": 0.001, "note": "CYP2B6*18"},
    "rs4986893": {"gene": "CYP2C19", "trait": "Drug metabolism", "afr_freq": 0.15, "eur_freq": 0.001, "note": "CYP2C19*3"},
    
    # =========================================================================
    # NATIVE AMERICAN MARKERS
    # =========================================================================
    "rs3135027": {"gene": "HLA", "trait": "HLA type", "amr_freq": 0.30, "eur_freq": 0.05, "ancestry_info": True},
    "rs3765524": {"gene": "CACNA1A", "trait": "Various", "amr_freq": 0.40, "eur_freq": 0.15, "ancestry_info": True},
    
    # =========================================================================
    # SOUTH ASIAN MARKERS
    # =========================================================================
    "rs2227956": {"gene": "HSPA1L", "trait": "Various", "sas_freq": 0.35, "eur_freq": 0.10, "ancestry_info": True},
    
    # =========================================================================
    # MIDDLE EASTERN/NORTH AFRICAN
    # =========================================================================
    "rs61752717": {"gene": "MEFV", "trait": "FMF", "mena_freq": 0.05, "eur_freq": 0.001,
        "note": "Familial Mediterranean Fever, common in Mediterranean populations"},
    
    # =========================================================================
    # ASHKENAZI JEWISH MARKERS
    # =========================================================================
    "rs76763715": {"gene": "GBA", "trait": "Gaucher/Parkinson", "aj_freq": 0.04, "eur_freq": 0.005,
        "note": "N370S, common in Ashkenazi Jews"},
    "rs78655421": {"gene": "CFTR", "trait": "CF W1282X", "aj_freq": 0.01, "eur_freq": 0.001,
        "note": "Ashkenazi Jewish CF mutation"},
    "rs72474224": {"gene": "GJB2", "trait": "Hearing loss 167delT", "aj_freq": 0.04, "eur_freq": 0.001,
        "note": "Common in Ashkenazi Jews"},
    
    # =========================================================================
    # HIGHLY INFORMATIVE AIMs (Used in forensics/ancestry tests)
    # =========================================================================
    "rs2814778": {"gene": "DARC", "trait": "Duffy null", "afr_freq": 0.95, "eur_freq": 0.001, "eas_freq": 0.001,
        "note": "Near-fixed in sub-Saharan Africans, provides malaria resistance"},
    "rs3737576": {"gene": "ASIP", "trait": "Pigmentation", "eur_freq": 0.85, "afr_freq": 0.15, "ancestry_info": True},
    "rs1834640": {"gene": "SYT1", "trait": "AIM", "ancestry_info": True},
    "rs881929": {"gene": "PPARGC1A", "trait": "AIM", "ancestry_info": True},
    "rs1079597": {"gene": "DRD2", "trait": "AIM/Dopamine", "ancestry_info": True},
    "rs2065160": {"gene": "GC", "trait": "Vitamin D binding", "ancestry_info": True},
    "rs1800292": {"gene": "CFH", "trait": "AIM", "ancestry_info": True},
    "rs3768641": {"gene": "MYO5A", "trait": "AIM", "ancestry_info": True},
    "rs260690": {"gene": "APOL1", "trait": "AIM", "ancestry_info": True},
    "rs1540771": {"gene": "ASIP", "trait": "Pigmentation AIM", "ancestry_info": True},
    "rs6003": {"gene": "F13B", "trait": "AIM", "ancestry_info": True},
    "rs722869": {"gene": "HERC2", "trait": "AIM", "ancestry_info": True},
    "rs2070776": {"gene": "NADSYN1", "trait": "AIM", "ancestry_info": True},
    "rs3768056": {"gene": "ACTN3", "trait": "AIM", "ancestry_info": True},
    "rs7689609": {"gene": "FOXP2", "trait": "AIM", "ancestry_info": True},
    "rs4471745": {"gene": "TRPM1", "trait": "AIM", "ancestry_info": True},
    "rs1426654": {"gene": "SLC24A5", "trait": "Skin pigmentation AIM", "ancestry_info": True},
    "rs1800414": {"gene": "OCA2", "trait": "AIM", "ancestry_info": True},
    "rs10843148": {"gene": "KITLG", "trait": "AIM", "ancestry_info": True},
    
    # =========================================================================
    # Y-CHROMOSOME HAPLOGROUP MARKERS (Male only)
    # =========================================================================
    "rs2032597": {"gene": "Y", "haplogroup": "A", "note": "African, oldest Y lineage"},
    "rs9786714": {"gene": "Y", "haplogroup": "A", "note": "Khoisan"},
    "rs9786076": {"gene": "Y", "haplogroup": "B", "note": "African Pygmies/Hadza"},
    "rs35284970": {"gene": "Y", "haplogroup": "C", "note": "Asia, Australia, Americas"},
    "rs2032602": {"gene": "Y", "haplogroup": "D", "note": "Tibet, Japan (Ainu)"},
    "rs9341296": {"gene": "Y", "haplogroup": "E", "note": "Africa, Mediterranean"},
    "rs2032636": {"gene": "Y", "haplogroup": "G", "note": "Caucasus, Neolithic farmers"},
    "rs2032639": {"gene": "Y", "haplogroup": "H", "note": "South Asia, Roma"},
    "rs2032652": {"gene": "Y", "haplogroup": "I", "note": "Europe (pre-Neolithic)"},
    "rs2032631": {"gene": "Y", "haplogroup": "J", "note": "Middle East, Jewish"},
    "rs9341301": {"gene": "Y", "haplogroup": "N", "note": "Finland, Siberia, Uralic"},
    "rs3908": {"gene": "Y", "haplogroup": "O", "note": "East/Southeast Asia"},
    "rs17316625": {"gene": "Y", "haplogroup": "Q", "note": "Native American, Siberia"},
    "rs9786184": {"gene": "Y", "haplogroup": "R1a", "note": "Eastern Europe, South Asia"},
    "rs17250804": {"gene": "Y", "haplogroup": "R1b", "note": "Western Europe"},
    
    # =========================================================================
    # mtDNA HAPLOGROUP PROXY MARKERS
    # =========================================================================
    "rs2853499": {"gene": "MT-HV", "haplogroup": "mtDNA H/V", "note": "European maternal"},
    "rs28358569": {"gene": "MT-CO2", "haplogroup": "mtDNA L", "note": "African maternal"},
    "rs193302994": {"gene": "MT-ND3", "haplogroup": "mtDNA A", "note": "Native American/Asian"},
    
    # =========================================================================
    # NATURAL SELECTION SIGNATURES
    # =========================================================================
    "rs4340": {"gene": "ACE", "trait": "Altitude adaptation", "note": "I/D, varies by population"},
    "rs11549465": {"gene": "HIF1A", "trait": "Hypoxia response", "note": "Adaptation to altitude"},
    "rs13419896": {"gene": "EPAS1", "trait": "Tibetan altitude adaptation", "tibet_freq": 0.87, "han_freq": 0.09,
        "note": "Strongest known example of recent human adaptation"},
}

# Population frequency reference
POPULATION_CODES = {
    "eur": "European",
    "afr": "African",
    "eas": "East Asian",
    "sas": "South Asian",
    "amr": "Native American",
    "mena": "Middle Eastern/North African",
    "aj": "Ashkenazi Jewish"
}
