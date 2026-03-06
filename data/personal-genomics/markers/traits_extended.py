"""
Extended Trait Markers
Additional physical, sensory, and behavioral traits from GWAS.
"""

TRAITS_EXTENDED = {
    # =========================================================================
    # PHYSICAL APPEARANCE EXTENDED
    # =========================================================================
    # Hair
    "rs4778211": {"gene": "OCA2", "trait": "Hair color", "effect": "A", "note": "Lighter hair"},
    "rs35264875": {"gene": "TPCN2", "trait": "Hair color", "effect": "T", "note": "Blonde association"},
    "rs1393350": {"gene": "TYR", "trait": "Hair/eye color", "effect": "A", "note": "Lighter coloring"},
    "rs4778241": {"gene": "OCA2", "trait": "Hair color", "effect": "A", "note": "Brown hair"},
    "rs1408799": {"gene": "TYRP1", "trait": "Hair color", "effect": "T", "note": "Brown hair"},
    "rs2733832": {"gene": "TYRP1", "trait": "Hair color", "effect": "C", "note": "Darker hair"},
    "rs683": {"gene": "TYRP1", "trait": "Hair color", "effect": "A", "note": "Hair color variation"},
    "rs12203592": {"gene": "IRF4", "trait": "Hair color", "effect": "T", "note": "Lighter hair/skin"},
    "rs1540771": {"gene": "ASIP", "trait": "Hair color", "effect": "G", "note": "Brown hair"},
    "rs2378249": {"gene": "ASIP", "trait": "Hair color", "effect": "A", "note": "Darker hair"},
    
    # Eye color extended
    "rs7495174": {"gene": "OCA2", "trait": "Eye color", "effect": "A", "note": "Blue eyes"},
    "rs4778138": {"gene": "OCA2", "trait": "Eye color", "effect": "A", "note": "Green/hazel eyes"},
    "rs916977": {"gene": "HERC2", "trait": "Eye color", "effect": "A", "note": "Blue eyes"},
    "rs1800407": {"gene": "OCA2", "trait": "Eye color", "effect": "T", "note": "Blue/green eyes"},
    "rs1800401": {"gene": "OCA2", "trait": "Eye color", "effect": "A", "note": "Eye color variation"},
    "rs7183877": {"gene": "HERC2", "trait": "Eye color", "effect": "C", "note": "Blue eyes"},
    "rs8028689": {"gene": "SLC45A2", "trait": "Eye color", "effect": "A", "note": "Light eyes"},
    
    # Skin
    "rs1805005": {"gene": "MC1R", "trait": "Skin type", "effect": "T", "note": "Fair skin, freckling"},
    "rs2228479": {"gene": "MC1R", "trait": "Skin type", "effect": "A", "note": "Fair skin"},
    "rs885479": {"gene": "MC1R", "trait": "Skin type", "effect": "T", "note": "Fair skin variant"},
    "rs1805006": {"gene": "MC1R", "trait": "Red hair/fair skin", "effect": "A", "note": "D84E mutation"},
    "rs2228478": {"gene": "MC1R", "trait": "Skin pigmentation", "effect": "A"},
    "rs1110400": {"gene": "MC1R", "trait": "Skin pigmentation", "effect": "C", "note": "Fair skin"},
    "rs26722": {"gene": "DCT", "trait": "Skin pigmentation", "effect": "T"},
    "rs10756819": {"gene": "BNC2", "trait": "Skin pigmentation", "effect": "G"},
    "rs6119471": {"gene": "ASIP", "trait": "Skin pigmentation", "effect": "C", "note": "Lighter skin"},
    "rs2424984": {"gene": "DDB1", "trait": "Tanning ability", "effect": "A"},
    
    # Baldness extended
    "rs929626": {"gene": "EBF1", "trait": "Male pattern baldness", "effect": "A"},
    "rs1160312": {"gene": "AR", "trait": "Male pattern baldness", "effect": "A"},
    "rs2497938": {"gene": "TARDBP", "trait": "Male pattern baldness", "effect": "T"},
    "rs10502861": {"gene": "AUTS2", "trait": "Male pattern baldness", "effect": "C"},
    "rs9668810": {"gene": "HDAC9", "trait": "Male pattern baldness", "effect": "A"},
    "rs4679955": {"gene": "SETBP1", "trait": "Male pattern baldness", "effect": "C"},
    
    # =========================================================================
    # HEIGHT EXTENDED
    # =========================================================================
    "rs1042725": {"gene": "HMGA2", "trait": "Height", "effect": "C", "cm": 0.4},
    "rs3791679": {"gene": "EFEMP1", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs6060369": {"gene": "GDF5", "trait": "Height", "effect": "C", "cm": 0.5},
    "rs143384": {"gene": "GDF5", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs724016": {"gene": "ZBTB38", "trait": "Height", "effect": "G", "cm": 0.4},
    "rs7759938": {"gene": "LIN28B", "trait": "Height", "effect": "T", "cm": 0.3},
    "rs6440003": {"gene": "HHIP", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs2274432": {"gene": "CDK6", "trait": "Height", "effect": "C", "cm": 0.3},
    "rs6684205": {"gene": "CABLES1", "trait": "Height", "effect": "G", "cm": 0.2},
    "rs1812175": {"gene": "HHIP", "trait": "Height", "effect": "G", "cm": 0.3},
    "rs4800148": {"gene": "ADAMTSL3", "trait": "Height", "effect": "G", "cm": 0.3},
    "rs17081935": {"gene": "SCMH1", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs798544": {"gene": "PAPPA", "trait": "Height", "effect": "A", "cm": 0.2},
    "rs314263": {"gene": "UQCC", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs7153027": {"gene": "TRIP11", "trait": "Height", "effect": "A", "cm": 0.3},
    "rs678962": {"gene": "ADAMTS17", "trait": "Height", "effect": "T", "cm": 0.3},
    "rs4896582": {"gene": "ADAMTS17", "trait": "Height", "effect": "G", "cm": 0.2},
    "rs12198986": {"gene": "HIST1H1D", "trait": "Height", "effect": "C", "cm": 0.2},
    "rs4549631": {"gene": "LCORL", "trait": "Height", "effect": "C", "cm": 0.3},
    "rs1046934": {"gene": "BMP6", "trait": "Height", "effect": "A", "cm": 0.2},
    
    # =========================================================================
    # TASTE/SMELL EXTENDED
    # =========================================================================
    "rs2590498": {"gene": "OR2J3", "trait": "Cinnamon smell", "effect": "A"},
    "rs6591536": {"gene": "OR5A1", "trait": "β-ionone smell (violets)", "effect": "A"},
    "rs1953558": {"gene": "OR10J5", "trait": "Bourgeonal smell", "effect": "A"},
    "rs4481887": {"gene": "OR6A2", "trait": "Cilantro aversion", "effect": "A"},
    "rs2074356": {"gene": "OR51V1", "trait": "Sweaty smell sensitivity", "effect": "C"},
    "rs28757581": {"gene": "OR7D4", "trait": "Androstenone smell", "effect": "T"},
    "rs5020278": {"gene": "TAS2R16", "trait": "Bitter taste sensitivity", "effect": "A"},
    "rs846664": {"gene": "TAS2R1", "trait": "Bitter taste", "effect": "G"},
    "rs1204014": {"gene": "TAS2R19", "trait": "Bitter taste (quinine)", "effect": "C"},
    "rs10772420": {"gene": "TAS2R19", "trait": "Grapefruit bitter", "effect": "A"},
    
    # =========================================================================
    # SLEEP/CIRCADIAN EXTENDED
    # =========================================================================
    "rs2304672": {"gene": "PER3", "trait": "Sleep duration", "effect": "C"},
    "rs228697": {"gene": "PER3", "trait": "Morning/evening", "effect": "C"},
    "rs2278749": {"gene": "BMAL1", "trait": "Chronotype", "effect": "T"},
    "rs7221412": {"gene": "PER1", "trait": "Morning preference", "effect": "G"},
    "rs35333999": {"gene": "DEC2/BHLHE41", "trait": "Short sleep", "effect": "T"},
    "rs8192440": {"gene": "ADA", "trait": "Sleep depth", "effect": "T"},
    "rs16830728": {"gene": "CLOCK", "trait": "Eveningness", "effect": "T"},
    "rs11545787": {"gene": "NPSR1", "trait": "Sleep/anxiety", "effect": "A"},
    
    # =========================================================================
    # METABOLISM
    # =========================================================================
    "rs10830963": {"gene": "MTNR1B", "trait": "Melatonin/glucose", "effect": "G"},
    "rs7903146": {"gene": "TCF7L2", "trait": "Glucose metabolism", "effect": "T"},
    "rs5219": {"gene": "KCNJ11", "trait": "Insulin secretion", "effect": "T"},
    "rs1801282": {"gene": "PPARG", "trait": "Fat metabolism", "effect": "G"},
    "rs328": {"gene": "LPL", "trait": "Triglyceride metabolism", "effect": "G"},
    "rs662799": {"gene": "APOA5", "trait": "Triglycerides", "effect": "C"},
    "rs174546": {"gene": "FADS1", "trait": "Fatty acid metabolism", "effect": "T"},
    
    # =========================================================================
    # MUSCLE/MOVEMENT
    # =========================================================================
    "rs1815739": {"gene": "ACTN3", "trait": "Muscle fiber type", "effect": "T", "note": "XX = endurance, RR = power"},
    "rs10497520": {"gene": "TTN", "trait": "Muscle stiffness", "effect": "T"},
    "rs4880": {"gene": "SOD2", "trait": "Muscle recovery", "effect": "G"},
    "rs12722": {"gene": "COL5A1", "trait": "Tendon flexibility", "effect": "T"},
    "rs3196378": {"gene": "ACE", "trait": "I/D endurance", "effect": "A"},
    
    # =========================================================================
    # BEHAVIORAL EXTENDED
    # =========================================================================
    "rs7794745": {"gene": "CNTNAP2", "trait": "Language", "effect": "T"},
    "rs1143674": {"gene": "ITGB3", "trait": "Harm avoidance", "effect": "A"},
    "rs322931": {"gene": "CUX2", "trait": "Wellbeing", "effect": "T"},
    "rs2576037": {"gene": "LINC00461", "trait": "Neuroticism", "effect": "T"},
    "rs12959006": {"gene": "DRD4", "trait": "Impulsivity", "effect": "A"},
    "rs2242446": {"gene": "SLC6A2", "trait": "ADHD-like traits", "effect": "T"},
    "rs6330": {"gene": "NGF", "trait": "Anxiety", "effect": "T"},
    "rs1360780": {"gene": "FKBP5", "trait": "Stress response", "effect": "T"},
    
    # =========================================================================
    # PHYSICAL PERFORMANCE
    # =========================================================================
    "rs8192678": {"gene": "PPARGC1A", "trait": "Aerobic capacity", "effect": "A"},
    "rs1799752": {"gene": "ACE", "trait": "Endurance vs power", "effect": "I"},
    "rs2016520": {"gene": "PPARD", "trait": "Endurance", "effect": "C"},
    "rs4253778": {"gene": "PPARA", "trait": "Fat oxidation", "effect": "G"},
    "rs699": {"gene": "AGT", "trait": "Blood pressure response", "effect": "C"},
    "rs5443": {"gene": "GNB3", "trait": "Exercise BP response", "effect": "T"},
    
    # =========================================================================
    # LONGEVITY-RELATED TRAITS
    # =========================================================================
    "rs2802292": {"gene": "FOXO3", "trait": "Longevity", "effect": "G"},
    "rs2764264": {"gene": "FOXO3", "trait": "Longevity", "effect": "C"},
    "rs5882": {"gene": "CETP", "trait": "HDL/longevity", "effect": "G"},
    "rs9536314": {"gene": "KLOTHO", "trait": "Cognitive longevity", "effect": "G"},
    
    # =========================================================================
    # DENTAL/ORAL
    # =========================================================================
    "rs17878486": {"gene": "EDAR", "trait": "Incisor shape", "effect": "A", "note": "Shovel-shaped"},
    "rs3827760": {"gene": "EDAR", "trait": "Tooth morphology", "effect": "A"},
    "rs7821494": {"gene": "PITX1", "trait": "Wisdom teeth", "effect": "T"},
    
    # =========================================================================
    # HAND/BODY
    # =========================================================================
    "rs11855415": {"gene": "PCSK6", "trait": "Handedness", "effect": "T"},
    "rs199512": {"gene": "LRRTM1", "trait": "Handedness", "effect": "T"},
    "rs7891818": {"gene": "TBX15", "trait": "Ear shape", "effect": "C"},
    "rs10946808": {"gene": "PRDM16", "trait": "Face shape", "effect": "A"},
    "rs1712499": {"gene": "GJB2", "trait": "Finger length ratio", "effect": "T"},
    
    # =========================================================================
    # MISC
    # =========================================================================
    "rs12896399": {"gene": "SLC24A4", "trait": "Blonde hair", "effect": "T"},
    "rs7574865": {"gene": "STAT4", "trait": "Sunburn recovery", "effect": "T"},
    "rs4911494": {"gene": "HERC2", "trait": "Gray hair onset", "effect": "T"},
    "rs2070959": {"gene": "UGT1A6", "trait": "Aspirin metabolism", "effect": "A"},
    "rs6730157": {"gene": "TRPV1", "trait": "Capsaicin sensitivity", "effect": "G"},
    "rs222747": {"gene": "TRPV1", "trait": "Spicy food tolerance", "effect": "C"},
    "rs1544410": {"gene": "VDR", "trait": "Vitamin D response", "effect": "A"},
    "rs1799883": {"gene": "FABP2", "trait": "Fat absorption", "effect": "G"},
    "rs12785878": {"gene": "DHCR7", "trait": "Vitamin D synthesis", "effect": "T"},
}
