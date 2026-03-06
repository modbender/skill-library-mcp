"""
Extended Carrier Status Markers
Additional recessive disease variants from ClinVar and ACMG.
"""

CARRIER_EXTENDED = {
    # =========================================================================
    # CYSTIC FIBROSIS EXTENDED
    # =========================================================================
    "rs77010898": {"gene": "CFTR", "variant": "G85E", "condition": "CF", "pathogenic": True, "risk": "T"},
    "rs121908745": {"gene": "CFTR", "variant": "R117H", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs74503330": {"gene": "CFTR", "variant": "621+1G>T", "condition": "CF", "pathogenic": True, "risk": "T"},
    "rs75039782": {"gene": "CFTR", "variant": "1717-1G>A", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs121908748": {"gene": "CFTR", "variant": "R334W", "condition": "CF", "pathogenic": True, "risk": "T"},
    "rs121909013": {"gene": "CFTR", "variant": "R347P", "condition": "CF", "pathogenic": True, "risk": "C"},
    "rs121908747": {"gene": "CFTR", "variant": "A455E", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs80282562": {"gene": "CFTR", "variant": "S549N", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs121908749": {"gene": "CFTR", "variant": "S549R", "condition": "CF", "pathogenic": True, "risk": "G"},
    "rs121909020": {"gene": "CFTR", "variant": "G1244E", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs121909041": {"gene": "CFTR", "variant": "S1251N", "condition": "CF", "pathogenic": True, "risk": "A"},
    "rs121909005": {"gene": "CFTR", "variant": "S1255P", "condition": "CF", "pathogenic": True, "risk": "C"},
    "rs267606723": {"gene": "CFTR", "variant": "G1349D", "condition": "CF", "pathogenic": True, "risk": "A"},
    
    # =========================================================================
    # BETA THALASSEMIA EXTENDED  
    # =========================================================================
    "rs33941849": {"gene": "HBB", "variant": "IVS-I-1", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "A"},
    "rs35699176": {"gene": "HBB", "variant": "IVS-I-5", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "C"},
    "rs34598529": {"gene": "HBB", "variant": "IVS-I-6", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "C"},
    "rs33944208": {"gene": "HBB", "variant": "IVS-II-1", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "A"},
    "rs63749819": {"gene": "HBB", "variant": "IVS-II-654", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "T"},
    "rs63750783": {"gene": "HBB", "variant": "IVS-II-745", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "G"},
    "rs33960103": {"gene": "HBB", "variant": "Cd8/9", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "del"},
    "rs34451549": {"gene": "HBB", "variant": "Cd41/42", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "del"},
    "rs33985472": {"gene": "HBB", "variant": "Cd17", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "A"},
    "rs35837759": {"gene": "HBB", "variant": "Cd26 (HbE)", "condition": "HbE/Thalassemia", "pathogenic": True, "risk": "A"},
    "rs35724775": {"gene": "HBB", "variant": "Cd27", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "T"},
    "rs33950507": {"gene": "HBB", "variant": "-28", "condition": "Beta-Thalassemia", "pathogenic": True, "risk": "C"},
    
    # =========================================================================
    # ASHKENAZI JEWISH PANEL EXTENDED
    # =========================================================================
    # Gaucher Extended
    "rs387906315": {"gene": "GBA", "variant": "84GG", "condition": "Gaucher", "pathogenic": True, "risk": "G"},
    "rs80356773": {"gene": "GBA", "variant": "IVS2+1", "condition": "Gaucher", "pathogenic": True, "risk": "A"},
    "rs121908312": {"gene": "GBA", "variant": "V394L", "condition": "Gaucher", "pathogenic": True, "risk": "G"},
    "rs76763715": {"gene": "GBA", "variant": "N370S", "condition": "Gaucher", "pathogenic": True, "risk": "A"},
    
    # Tay-Sachs Extended
    "rs121907972": {"gene": "HEXA", "variant": "+1IVS12", "condition": "Tay-Sachs", "pathogenic": True, "risk": "C"},
    "rs121907973": {"gene": "HEXA", "variant": "G269S", "condition": "Tay-Sachs adult", "pathogenic": True, "risk": "A"},
    
    # Familial Dysautonomia Extended
    "rs80338951": {"gene": "IKBKAP", "variant": "R696P", "condition": "Familial Dysautonomia", "pathogenic": True, "risk": "C"},
    
    # Niemann-Pick Extended
    "rs120074128": {"gene": "SMPD1", "variant": "fsP330", "condition": "Niemann-Pick A", "pathogenic": True, "risk": "del"},
    
    # Fanconi Anemia Extended
    "rs137852836": {"gene": "FANCC", "variant": "IVS4+4A>T", "condition": "Fanconi Anemia", "pathogenic": True, "risk": "T"},
    "rs104894095": {"gene": "FANCC", "variant": "R185X", "condition": "Fanconi Anemia", "pathogenic": True, "risk": "T"},
    
    # =========================================================================
    # HEARING LOSS EXTENDED
    # =========================================================================
    "rs80338942": {"gene": "GJB2", "variant": "M34T", "condition": "Hearing Loss", "pathogenic": True, "risk": "C"},
    "rs72474223": {"gene": "GJB2", "variant": "V37I", "condition": "Hearing Loss mild", "pathogenic": True, "risk": "A"},
    "rs104894396": {"gene": "GJB2", "variant": "W24X", "condition": "Hearing Loss", "pathogenic": True, "risk": "A"},
    "rs80338940": {"gene": "GJB2", "variant": "L90P", "condition": "Hearing Loss", "pathogenic": True, "risk": "C"},
    "rs111033196": {"gene": "GJB2", "variant": "R143W", "condition": "Hearing Loss", "pathogenic": True, "risk": "T"},
    "rs80338945": {"gene": "GJB2", "variant": "V95M", "condition": "Hearing Loss", "pathogenic": True, "risk": "A"},
    "rs104894404": {"gene": "GJB6", "variant": "del(GJB6-D13S1830)", "condition": "Hearing Loss", "pathogenic": True, "risk": "del"},
    "rs121918357": {"gene": "SLC26A4", "variant": "L236P", "condition": "Pendred/Hearing Loss", "pathogenic": True, "risk": "T"},
    "rs111033305": {"gene": "SLC26A4", "variant": "T416P", "condition": "Pendred/Hearing Loss", "pathogenic": True, "risk": "A"},
    
    # =========================================================================
    # METABOLIC DISORDERS
    # =========================================================================
    # PKU Extended
    "rs5030841": {"gene": "PAH", "variant": "R243Q", "condition": "PKU", "pathogenic": True, "risk": "A"},
    "rs62516101": {"gene": "PAH", "variant": "R261Q", "condition": "PKU", "pathogenic": True, "risk": "A"},
    "rs62642934": {"gene": "PAH", "variant": "E280K", "condition": "PKU", "pathogenic": True, "risk": "A"},
    "rs5030842": {"gene": "PAH", "variant": "L48S", "condition": "PKU", "pathogenic": True, "risk": "C"},
    "rs5030840": {"gene": "PAH", "variant": "P281L", "condition": "PKU", "pathogenic": True, "risk": "T"},
    
    # MCAD Deficiency
    "rs77931234": {"gene": "ACADM", "variant": "K329E", "condition": "MCAD Deficiency", "pathogenic": True, "risk": "A"},
    "rs121434274": {"gene": "ACADM", "variant": "Y67H", "condition": "MCAD Deficiency", "pathogenic": True, "risk": "C"},
    
    # Galactosemia
    "rs72551338": {"gene": "GALT", "variant": "Q188R", "condition": "Galactosemia", "pathogenic": True, "risk": "G"},
    "rs111033716": {"gene": "GALT", "variant": "K285N", "condition": "Galactosemia", "pathogenic": True, "risk": "T"},
    "rs72551339": {"gene": "GALT", "variant": "S135L", "condition": "Galactosemia", "pathogenic": True, "risk": "T"},
    
    # Biotinidase Deficiency
    "rs28934601": {"gene": "BTD", "variant": "D444H", "condition": "Biotinidase Deficiency", "pathogenic": True, "risk": "C"},
    "rs80338689": {"gene": "BTD", "variant": "R538C", "condition": "Biotinidase Deficiency", "pathogenic": True, "risk": "T"},
    
    # =========================================================================
    # LYSOSOMAL STORAGE DISORDERS
    # =========================================================================
    # Pompe Disease
    "rs386834236": {"gene": "GAA", "variant": "IVS1-13T>G", "condition": "Pompe Disease", "pathogenic": True, "risk": "G"},
    "rs28940868": {"gene": "GAA", "variant": "R854X", "condition": "Pompe Disease", "pathogenic": True, "risk": "T"},
    
    # Fabry Disease
    "rs28935490": {"gene": "GLA", "variant": "N215S", "condition": "Fabry Disease", "pathogenic": True, "risk": "A"},
    "rs104894834": {"gene": "GLA", "variant": "R227X", "condition": "Fabry Disease", "pathogenic": True, "risk": "T"},
    
    # Krabbe Disease
    "rs398123094": {"gene": "GALC", "variant": "30kb del", "condition": "Krabbe Disease", "pathogenic": True, "risk": "del"},
    
    # Metachromatic Leukodystrophy
    "rs74315370": {"gene": "ARSA", "variant": "P426L", "condition": "MLD", "pathogenic": True, "risk": "T"},
    "rs28940889": {"gene": "ARSA", "variant": "I179S", "condition": "MLD", "pathogenic": True, "risk": "G"},
    
    # =========================================================================
    # HEMOPHILIA & BLEEDING DISORDERS
    # =========================================================================
    "rs137852303": {"gene": "F9", "variant": "Hemophilia B Leiden", "condition": "Hemophilia B", "pathogenic": True, "risk": "A"},
    "rs118203938": {"gene": "F8", "variant": "Various", "condition": "Hemophilia A", "pathogenic": True, "risk": "var"},
    "rs121918474": {"gene": "VWF", "variant": "Various", "condition": "von Willebrand", "pathogenic": True, "risk": "var"},
    
    # =========================================================================
    # MUSCLE DISORDERS
    # =========================================================================
    # Duchenne/Becker (X-linked but still important)
    "rs128627255": {"gene": "DMD", "variant": "Various", "condition": "DMD/BMD", "pathogenic": True, "risk": "var"},
    
    # Limb-Girdle MD
    "rs104894363": {"gene": "SGCA", "variant": "R77C", "condition": "LGMD2D", "pathogenic": True, "risk": "T"},
    "rs80338892": {"gene": "FKRP", "variant": "L276I", "condition": "LGMD2I", "pathogenic": True, "risk": "A"},
    
    # Congenital Myasthenic Syndrome
    "rs80358245": {"gene": "CHRNE", "variant": "Various", "condition": "CMS", "pathogenic": True, "risk": "var"},
    
    # =========================================================================
    # PRIMARY IMMUNODEFICIENCIES
    # =========================================================================
    "rs104895042": {"gene": "ADA", "variant": "Various", "condition": "ADA-SCID", "pathogenic": True, "risk": "var"},
    "rs75851046": {"gene": "RAG1", "variant": "Various", "condition": "SCID", "pathogenic": True, "risk": "var"},
    "rs121912702": {"gene": "RAG2", "variant": "Various", "condition": "SCID", "pathogenic": True, "risk": "var"},
    
    # =========================================================================
    # ENDOCRINE
    # =========================================================================
    # Congenital Adrenal Hyperplasia
    "rs6467": {"gene": "CYP21A2", "variant": "V281L", "condition": "CAH non-classic", "pathogenic": True, "risk": "G"},
    "rs7755898": {"gene": "CYP21A2", "variant": "P30L", "condition": "CAH non-classic", "pathogenic": True, "risk": "T"},
    "rs72552764": {"gene": "CYP21A2", "variant": "Q318X", "condition": "CAH classic", "pathogenic": True, "risk": "T"},
    "rs6474": {"gene": "CYP21A2", "variant": "I172N", "condition": "CAH", "pathogenic": True, "risk": "A"},
    
    # =========================================================================
    # RETINAL DISORDERS
    # =========================================================================
    "rs61750900": {"gene": "USH2A", "variant": "Various", "condition": "Usher Syndrome 2A", "pathogenic": True, "risk": "var"},
    "rs104893915": {"gene": "ABCA4", "variant": "G1961E", "condition": "Stargardt Disease", "pathogenic": True, "risk": "A"},
    "rs1800553": {"gene": "ABCA4", "variant": "A1038V", "condition": "Stargardt Disease", "pathogenic": True, "risk": "T"},
    "rs76157638": {"gene": "CRB1", "variant": "C948Y", "condition": "Leber Congenital Amaurosis", "pathogenic": True, "risk": "A"},
    "rs62645885": {"gene": "RPE65", "variant": "Various", "condition": "Leber Congenital Amaurosis", "pathogenic": True, "risk": "var"},
    
    # =========================================================================
    # HEMOGLOBINOPATHIES EXTENDED
    # =========================================================================
    # Alpha Thalassemia (Note: often requires copy number analysis)
    "rs41294870": {"gene": "HBA1/HBA2", "variant": "Cd30", "condition": "Alpha-Thalassemia", "pathogenic": True, "risk": "del"},
    "rs63750067": {"gene": "HBA1", "variant": "Hb Constant Spring", "condition": "Alpha-Thalassemia", "pathogenic": True, "risk": "A"},
    
    # =========================================================================
    # FRAGILE X RELATED
    # =========================================================================
    "rs25714": {"gene": "FMR1", "variant": "CGG expansion", "condition": "Fragile X", "pathogenic": True, "risk": "expansion",
        "note": "Requires specialized testing for repeat expansion"},
}
