"""
Extended Polygenic Risk Score Weights
Additional SNPs from major GWAS meta-analyses.
"""

PRS_EXTENDED = {
    # =========================================================================
    # CORONARY ARTERY DISEASE EXTENDED (from CARDIoGRAMplusC4D)
    # =========================================================================
    "rs1333048": {"effect": "C", "beta": 0.13, "gene": "9p21", "condition": "cad"},
    "rs2891168": {"effect": "G", "beta": 0.11, "gene": "9p21", "condition": "cad"},
    "rs10953541": {"effect": "C", "beta": 0.07, "gene": "5q31", "condition": "cad"},
    "rs4129267": {"effect": "C", "beta": 0.06, "gene": "IL6R", "condition": "cad"},
    "rs4845625": {"effect": "T", "beta": 0.06, "gene": "IL6R", "condition": "cad"},
    "rs3918226": {"effect": "T", "beta": 0.10, "gene": "NOS3", "condition": "cad"},
    "rs17087335": {"effect": "T", "beta": 0.06, "gene": "REST-NOA1", "condition": "cad"},
    "rs1122608": {"effect": "G", "beta": 0.09, "gene": "LDLR", "condition": "cad"},
    "rs56289821": {"effect": "G", "beta": 0.07, "gene": "LDLR", "condition": "cad"},
    "rs11556924": {"effect": "C", "beta": 0.07, "gene": "ZC3HC1", "condition": "cad"},
    "rs7173743": {"effect": "T", "beta": 0.05, "gene": "ADAMTS7", "condition": "cad"},
    "rs4252120": {"effect": "T", "beta": 0.06, "gene": "PLG", "condition": "cad"},
    "rs6544713": {"effect": "T", "beta": 0.07, "gene": "ABCG5", "condition": "cad"},
    "rs2107595": {"effect": "A", "beta": 0.07, "gene": "HDAC9", "condition": "cad"},
    "rs7500448": {"effect": "T", "beta": 0.05, "gene": "EDNRA", "condition": "cad"},
    "rs3825807": {"effect": "A", "beta": 0.07, "gene": "ADAMTS7", "condition": "cad"},
    "rs11057830": {"effect": "A", "beta": 0.06, "gene": "KIAA1462", "condition": "cad"},
    "rs974819": {"effect": "T", "beta": 0.05, "gene": "PDGFD", "condition": "cad"},
    "rs9515203": {"effect": "T", "beta": 0.07, "gene": "COL4A1", "condition": "cad"},
    "rs964184": {"effect": "G", "beta": 0.08, "gene": "ZNF259-APOA5", "condition": "cad"},
    "rs6544714": {"effect": "C", "beta": 0.06, "gene": "ABCG8", "condition": "cad"},
    "rs267": {"effect": "A", "beta": 0.05, "gene": "LPL", "condition": "cad"},
    "rs2954029": {"effect": "A", "beta": 0.06, "gene": "TRIB1", "condition": "cad"},
    "rs11984041": {"effect": "T", "beta": 0.12, "gene": "6p21", "condition": "cad"},
    
    # =========================================================================
    # TYPE 2 DIABETES EXTENDED (from DIAGRAM)
    # =========================================================================
    "rs10906115": {"effect": "A", "beta": 0.06, "gene": "CDC123", "condition": "t2d"},
    "rs11708067": {"effect": "A", "beta": 0.10, "gene": "ADCY5", "condition": "t2d"},
    "rs1552224": {"effect": "A", "beta": 0.10, "gene": "CENTD2", "condition": "t2d"},
    "rs4607517": {"effect": "A", "beta": 0.07, "gene": "GCK", "condition": "t2d"},
    "rs459193": {"effect": "G", "beta": 0.05, "gene": "ANKRD55", "condition": "t2d"},
    "rs6813195": {"effect": "C", "beta": 0.06, "gene": "TMEM154", "condition": "t2d"},
    "rs1531343": {"effect": "C", "beta": 0.06, "gene": "HMGA2", "condition": "t2d"},
    "rs7578326": {"effect": "A", "beta": 0.05, "gene": "IRS1", "condition": "t2d"},
    "rs10842994": {"effect": "C", "beta": 0.07, "gene": "KLHDC5", "condition": "t2d"},
    "rs7756992": {"effect": "G", "beta": 0.12, "gene": "CDKAL1", "condition": "t2d"},
    "rs4275659": {"effect": "C", "beta": 0.05, "gene": "MPHOSPH9", "condition": "t2d"},
    "rs1801282": {"effect": "C", "beta": 0.09, "gene": "PPARG", "condition": "t2d"},
    "rs2943634": {"effect": "C", "beta": 0.06, "gene": "IRS1", "condition": "t2d"},
    "rs17168486": {"effect": "T", "beta": 0.07, "gene": "DGKB", "condition": "t2d"},
    "rs7034200": {"effect": "A", "beta": 0.05, "gene": "GCKR", "condition": "t2d"},
    "rs11634397": {"effect": "G", "beta": 0.06, "gene": "ZFAND6", "condition": "t2d"},
    "rs163182": {"effect": "C", "beta": 0.05, "gene": "KCNQ1", "condition": "t2d"},
    "rs5015480": {"effect": "C", "beta": 0.09, "gene": "HHEX", "condition": "t2d"},
    "rs10965250": {"effect": "G", "beta": 0.08, "gene": "CDKN2A/B", "condition": "t2d"},
    "rs7901695": {"effect": "C", "beta": 0.31, "gene": "TCF7L2", "condition": "t2d"},
    
    # =========================================================================
    # BREAST CANCER EXTENDED (from BCAC)
    # =========================================================================
    "rs17529111": {"effect": "A", "beta": 0.06, "gene": "6q14", "condition": "breast_ca"},
    "rs9693444": {"effect": "A", "beta": 0.06, "gene": "6p25.3", "condition": "breast_ca"},
    "rs13329835": {"effect": "A", "beta": 0.08, "gene": "16q12.2", "condition": "breast_ca"},
    "rs17817449": {"effect": "T", "beta": 0.05, "gene": "FTO", "condition": "breast_ca"},
    "rs2823093": {"effect": "G", "beta": 0.06, "gene": "21q21", "condition": "breast_ca"},
    "rs10474352": {"effect": "C", "beta": 0.05, "gene": "5q14.2", "condition": "breast_ca"},
    "rs2588809": {"effect": "T", "beta": 0.06, "gene": "14q24.1", "condition": "breast_ca"},
    "rs6001930": {"effect": "T", "beta": 0.09, "gene": "22q13", "condition": "breast_ca"},
    "rs4808801": {"effect": "A", "beta": 0.07, "gene": "19p13.11", "condition": "breast_ca"},
    "rs11820646": {"effect": "C", "beta": 0.05, "gene": "11q24.3", "condition": "breast_ca"},
    "rs12493607": {"effect": "C", "beta": 0.06, "gene": "3p24", "condition": "breast_ca"},
    "rs9790517": {"effect": "T", "beta": 0.05, "gene": "10q22.3", "condition": "breast_ca"},
    "rs2236007": {"effect": "G", "beta": 0.08, "gene": "PAX9", "condition": "breast_ca"},
    "rs7726159": {"effect": "A", "beta": 0.05, "gene": "TERT", "condition": "breast_ca"},
    "rs941764": {"effect": "G", "beta": 0.06, "gene": "14q32.11", "condition": "breast_ca"},
    
    # =========================================================================
    # PROSTATE CANCER EXTENDED (from PRACTICAL)
    # =========================================================================
    "rs6465657": {"effect": "C", "beta": 0.12, "gene": "7q21", "condition": "prostate_ca"},
    "rs12543663": {"effect": "C", "beta": 0.08, "gene": "8p21", "condition": "prostate_ca"},
    "rs7841060": {"effect": "G", "beta": 0.09, "gene": "8q24", "condition": "prostate_ca"},
    "rs2928679": {"effect": "A", "beta": 0.08, "gene": "8q24", "condition": "prostate_ca"},
    "rs1571801": {"effect": "A", "beta": 0.09, "gene": "9q33", "condition": "prostate_ca"},
    "rs10896449": {"effect": "G", "beta": 0.11, "gene": "11q13", "condition": "prostate_ca"},
    "rs7931342": {"effect": "G", "beta": 0.16, "gene": "11q13", "condition": "prostate_ca"},
    "rs10875943": {"effect": "T", "beta": 0.07, "gene": "12q13", "condition": "prostate_ca"},
    "rs8023959": {"effect": "G", "beta": 0.08, "gene": "15q21", "condition": "prostate_ca"},
    "rs11650494": {"effect": "A", "beta": 0.13, "gene": "17p13", "condition": "prostate_ca"},
    "rs11672691": {"effect": "G", "beta": 0.08, "gene": "19q13", "condition": "prostate_ca"},
    "rs2735839": {"effect": "G", "beta": 0.18, "gene": "KLK3", "condition": "prostate_ca"},
    "rs11568818": {"effect": "G", "beta": 0.07, "gene": "MMP7", "condition": "prostate_ca"},
    "rs2660753": {"effect": "T", "beta": 0.12, "gene": "3p12", "condition": "prostate_ca"},
    "rs10934853": {"effect": "A", "beta": 0.11, "gene": "3q21", "condition": "prostate_ca"},
    
    # =========================================================================
    # ALZHEIMER'S EXTENDED (from IGAP)
    # =========================================================================
    "rs11771145": {"effect": "A", "beta": 0.08, "gene": "EPHA1", "condition": "alzheimer"},
    "rs10792832": {"effect": "A", "beta": 0.12, "gene": "PICALM", "condition": "alzheimer"},
    "rs1476679": {"effect": "C", "beta": 0.08, "gene": "ZCWPW1", "condition": "alzheimer"},
    "rs2718058": {"effect": "G", "beta": 0.07, "gene": "NME8", "condition": "alzheimer"},
    "rs7274581": {"effect": "T", "beta": 0.10, "gene": "CASS4", "condition": "alzheimer"},
    "rs35349669": {"effect": "T", "beta": 0.08, "gene": "INPP5D", "condition": "alzheimer"},
    "rs190982": {"effect": "G", "beta": 0.07, "gene": "MEF2C", "condition": "alzheimer"},
    "rs1532278": {"effect": "T", "beta": 0.13, "gene": "CLU", "condition": "alzheimer"},
    "rs9331896": {"effect": "C", "beta": 0.14, "gene": "CLU", "condition": "alzheimer"},
    "rs10838725": {"effect": "C", "beta": 0.08, "gene": "CELF1", "condition": "alzheimer"},
    "rs983392": {"effect": "G", "beta": 0.10, "gene": "MS4A6A", "condition": "alzheimer"},
    "rs4147929": {"effect": "A", "beta": 0.09, "gene": "ABCA7", "condition": "alzheimer"},
    "rs2070045": {"effect": "G", "beta": 0.09, "gene": "SORL1", "condition": "alzheimer"},
    "rs28834970": {"effect": "C", "beta": 0.08, "gene": "PTK2B", "condition": "alzheimer"},
    "rs1476679": {"effect": "C", "beta": 0.09, "gene": "ZCWPW1", "condition": "alzheimer"},
    
    # =========================================================================
    # OBESITY/BMI EXTENDED (from GIANT)
    # =========================================================================
    "rs2207139": {"effect": "G", "beta": 0.15, "gene": "TFAP2B", "condition": "obesity"},
    "rs4836133": {"effect": "A", "beta": 0.06, "gene": "ZNF608", "condition": "obesity"},
    "rs3101336": {"effect": "C", "beta": 0.07, "gene": "NEGR1", "condition": "obesity"},
    "rs6548238": {"effect": "T", "beta": 0.10, "gene": "TMEM18", "condition": "obesity"},
    "rs2112347": {"effect": "T", "beta": 0.07, "gene": "POC5", "condition": "obesity"},
    "rs10968576": {"effect": "G", "beta": 0.08, "gene": "LRRN6C", "condition": "obesity"},
    "rs7498665": {"effect": "G", "beta": 0.10, "gene": "SH2B1", "condition": "obesity"},
    "rs3817334": {"effect": "T", "beta": 0.07, "gene": "MTCH2", "condition": "obesity"},
    "rs4771122": {"effect": "G", "beta": 0.06, "gene": "MTIF3", "condition": "obesity"},
    "rs10150332": {"effect": "C", "beta": 0.07, "gene": "NRXN3", "condition": "obesity"},
    "rs13078960": {"effect": "G", "beta": 0.10, "gene": "CADM2", "condition": "obesity"},
    "rs1514175": {"effect": "A", "beta": 0.07, "gene": "TNNI3K", "condition": "obesity"},
    "rs1558902": {"effect": "A", "beta": 0.39, "gene": "FTO", "condition": "obesity"},
    "rs6567160": {"effect": "C", "beta": 0.22, "gene": "MC4R", "condition": "obesity"},
    "rs2287019": {"effect": "C", "beta": 0.11, "gene": "QPCTL", "condition": "obesity"},
    
    # =========================================================================
    # COLORECTAL CANCER EXTENDED (from GECCO)
    # =========================================================================
    "rs6687758": {"effect": "G", "beta": 0.08, "gene": "1q41", "condition": "colorectal_ca"},
    "rs11903757": {"effect": "T", "beta": 0.15, "gene": "2q32", "condition": "colorectal_ca"},
    "rs10936599": {"effect": "C", "beta": 0.08, "gene": "TERC", "condition": "colorectal_ca"},
    "rs35360328": {"effect": "A", "beta": 0.07, "gene": "3q26", "condition": "colorectal_ca"},
    "rs1321311": {"effect": "A", "beta": 0.08, "gene": "6p21", "condition": "colorectal_ca"},
    "rs7136702": {"effect": "T", "beta": 0.06, "gene": "12q13", "condition": "colorectal_ca"},
    "rs1957636": {"effect": "T", "beta": 0.07, "gene": "14q22", "condition": "colorectal_ca"},
    "rs4779584": {"effect": "T", "beta": 0.15, "gene": "GREM1", "condition": "colorectal_ca"},
    "rs12603526": {"effect": "C", "beta": 0.06, "gene": "17p13", "condition": "colorectal_ca"},
    "rs4813802": {"effect": "G", "beta": 0.09, "gene": "20p12", "condition": "colorectal_ca"},
    "rs5934683": {"effect": "C", "beta": 0.05, "gene": "Xp22", "condition": "colorectal_ca"},
    "rs4444235": {"effect": "C", "beta": 0.08, "gene": "BMP4", "condition": "colorectal_ca"},
    "rs9929218": {"effect": "G", "beta": 0.09, "gene": "CDH1", "condition": "colorectal_ca"},
    "rs16892766": {"effect": "C", "beta": 0.27, "gene": "8q23", "condition": "colorectal_ca"},
    "rs7014346": {"effect": "A", "beta": 0.19, "gene": "8q24", "condition": "colorectal_ca"},
    
    # =========================================================================
    # ATRIAL FIBRILLATION EXTENDED
    # =========================================================================
    "rs17042171": {"effect": "A", "beta": 0.21, "gene": "4q25", "condition": "afib"},
    "rs6843082": {"effect": "G", "beta": 0.17, "gene": "4q25", "condition": "afib"},
    "rs2106261": {"effect": "T", "beta": 0.13, "gene": "ZFHX3", "condition": "afib"},
    "rs7164883": {"effect": "G", "beta": 0.10, "gene": "PRRX1", "condition": "afib"},
    "rs6490029": {"effect": "C", "beta": 0.12, "gene": "WNT8A", "condition": "afib"},
    "rs3807989": {"effect": "A", "beta": 0.08, "gene": "CAV1", "condition": "afib"},
    "rs10821415": {"effect": "A", "beta": 0.07, "gene": "C9orf3", "condition": "afib"},
    "rs10824026": {"effect": "G", "beta": 0.08, "gene": "SYNPO2L", "condition": "afib"},
    "rs1152591": {"effect": "A", "beta": 0.07, "gene": "SYNE2", "condition": "afib"},
    "rs2359171": {"effect": "T", "beta": 0.07, "gene": "SCN10A", "condition": "afib"},
    "rs6584555": {"effect": "T", "beta": 0.06, "gene": "NUCKS1", "condition": "afib"},
    "rs17042171": {"effect": "A", "beta": 0.18, "gene": "4q25", "condition": "afib"},
    "rs11047543": {"effect": "A", "beta": 0.14, "gene": "SOX5", "condition": "afib"},
    "rs12415501": {"effect": "T", "beta": 0.16, "gene": "KCNQ1", "condition": "afib"},
    "rs4400058": {"effect": "A", "beta": 0.07, "gene": "SYNPO2L", "condition": "afib"},
    
    # =========================================================================
    # IBD EXTENDED
    # =========================================================================
    "rs2066843": {"effect": "T", "beta": 0.35, "gene": "NOD2", "condition": "ibd"},
    "rs7517847": {"effect": "T", "beta": 0.10, "gene": "IL23R", "condition": "ibd"},
    "rs17234657": {"effect": "G", "beta": 0.25, "gene": "5p13", "condition": "ibd"},
    "rs1000113": {"effect": "C", "beta": 0.18, "gene": "5p13", "condition": "ibd"},
    "rs13361189": {"effect": "T", "beta": 0.16, "gene": "IRGM", "condition": "ibd"},
    "rs11465804": {"effect": "G", "beta": 0.35, "gene": "IL23R", "condition": "ibd"},
    "rs762421": {"effect": "G", "beta": 0.14, "gene": "IL12B", "condition": "ibd"},
    "rs7807268": {"effect": "C", "beta": 0.12, "gene": "C7orf66", "condition": "ibd"},
    "rs1793004": {"effect": "G", "beta": 0.10, "gene": "NELL1", "condition": "ibd"},
    "rs9858542": {"effect": "A", "beta": 0.11, "gene": "BSN", "condition": "ibd"},
    "rs10045431": {"effect": "C", "beta": 0.12, "gene": "IL12B", "condition": "ibd"},
    "rs12994997": {"effect": "A", "beta": 0.11, "gene": "TNFSF11", "condition": "ibd"},
    "rs2188962": {"effect": "T", "beta": 0.12, "gene": "5q33", "condition": "ibd"},
    "rs4902642": {"effect": "G", "beta": 0.10, "gene": "ZNF365", "condition": "ibd"},
    "rs2274910": {"effect": "T", "beta": 0.09, "gene": "ITLN1", "condition": "ibd"},
}
