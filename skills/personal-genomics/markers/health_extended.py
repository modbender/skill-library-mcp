"""
Extended Health Risk Markers
Additional disease susceptibility variants from GWAS Catalog.
"""

HEALTH_EXTENDED = {
    # =========================================================================
    # CARDIOVASCULAR EXTENDED
    # =========================================================================
    "rs383830": {"gene": "WDR12", "condition": "CAD", "risk": "T", "or": 1.15},
    "rs10953541": {"gene": "5q31", "condition": "CAD", "risk": "C", "or": 1.08},
    "rs3869109": {"gene": "6p24", "condition": "CAD", "risk": "A", "or": 1.09},
    "rs9369640": {"gene": "6p24", "condition": "CAD", "risk": "A", "or": 1.12},
    "rs4252185": {"gene": "ANKS1A", "condition": "CAD", "risk": "T", "or": 1.08},
    "rs1870634": {"gene": "ZNF259", "condition": "CAD", "risk": "T", "or": 1.10},
    "rs2891168": {"gene": "9p21", "condition": "CAD", "risk": "G", "or": 1.18},
    "rs7025486": {"gene": "DAB2IP", "condition": "CAD", "risk": "A", "or": 1.12},
    "rs17609940": {"gene": "CNNM2", "condition": "CAD", "risk": "G", "or": 1.10},
    "rs11191416": {"gene": "NT5C2", "condition": "CAD", "risk": "T", "or": 1.06},
    "rs2505083": {"gene": "KIAA1462", "condition": "CAD", "risk": "C", "or": 1.07},
    "rs3184504": {"gene": "SH2B3", "condition": "CAD", "risk": "T", "or": 1.08},
    "rs56062135": {"gene": "SMCR3", "condition": "CAD", "risk": "C", "or": 1.07},
    "rs216172": {"gene": "SMG6", "condition": "CAD", "risk": "C", "or": 1.07},
    "rs663129": {"gene": "ABO", "condition": "CAD", "risk": "A", "or": 1.10},
    "rs2048327": {"gene": "SLC22A3", "condition": "CAD", "risk": "T", "or": 1.06},
    
    # Atrial Fibrillation Extended
    "rs1448818": {"gene": "CAV1", "condition": "AFib", "risk": "G", "or": 1.11},
    "rs10821415": {"gene": "9q22", "condition": "AFib", "risk": "A", "or": 1.10},
    "rs6584555": {"gene": "NUCKS1", "condition": "AFib", "risk": "T", "or": 1.08},
    "rs2040862": {"gene": "NEURL", "condition": "AFib", "risk": "T", "or": 1.13},
    "rs12415501": {"gene": "KCNQ1", "condition": "AFib", "risk": "T", "or": 1.20},
    "rs2834618": {"gene": "ZFHX3", "condition": "AFib", "risk": "C", "or": 1.12},
    "rs2129977": {"gene": "KCNN3", "condition": "AFib", "risk": "A", "or": 1.14},
    
    # Hypertension
    "rs16998073": {"gene": "FGF5", "condition": "Hypertension", "risk": "T", "or": 1.09},
    "rs653178": {"gene": "ATXN2", "condition": "Hypertension", "risk": "T", "or": 1.07},
    "rs1004467": {"gene": "CYP17A1", "condition": "Hypertension", "risk": "A", "or": 1.08},
    "rs11191548": {"gene": "CYP17A1", "condition": "Hypertension", "risk": "T", "or": 1.11},
    "rs17367504": {"gene": "MTHFR", "condition": "Hypertension", "risk": "A", "or": 1.09},
    "rs2681472": {"gene": "ATP2B1", "condition": "Hypertension", "risk": "A", "or": 1.10},
    "rs2681492": {"gene": "ATP2B1", "condition": "Hypertension", "risk": "T", "or": 1.08},
    "rs1799945": {"gene": "HFE", "condition": "Hypertension", "risk": "G", "or": 1.07},
    "rs13107325": {"gene": "SLC39A8", "condition": "Hypertension", "risk": "T", "or": 1.17},
    "rs12946454": {"gene": "PLCD3", "condition": "Hypertension", "risk": "T", "or": 1.07},
    "rs3184504": {"gene": "SH2B3", "condition": "Hypertension", "risk": "T", "or": 1.07},
    
    # =========================================================================
    # CANCER EXTENDED
    # =========================================================================
    # Breast Cancer Extended
    "rs4784227": {"gene": "TOX3", "condition": "Breast cancer", "risk": "T", "or": 1.23},
    "rs6504950": {"gene": "COX11", "condition": "Breast cancer", "risk": "A", "or": 1.05},
    "rs999737": {"gene": "RAD51L1", "condition": "Breast cancer", "risk": "T", "or": 1.06},
    "rs8170": {"gene": "19p13.11", "condition": "Breast cancer", "risk": "G", "or": 1.26},
    "rs2380205": {"gene": "10p15", "condition": "Breast cancer", "risk": "T", "or": 1.05},
    "rs2981579": {"gene": "FGFR2", "condition": "Breast cancer", "risk": "G", "or": 1.26},
    "rs3757318": {"gene": "ESR1", "condition": "Breast cancer", "risk": "G", "or": 1.09},
    "rs10069690": {"gene": "TERT", "condition": "Breast cancer ER-", "risk": "T", "or": 1.18},
    "rs2363956": {"gene": "ANKLE1", "condition": "Breast cancer", "risk": "T", "or": 1.06},
    "rs865686": {"gene": "9q31.2", "condition": "Breast cancer", "risk": "T", "or": 1.11},
    "rs10759243": {"gene": "9q31.2", "condition": "Breast cancer", "risk": "A", "or": 1.06},
    "rs1011970": {"gene": "CDKN2A", "condition": "Breast cancer", "risk": "T", "or": 1.09},
    "rs704010": {"gene": "ZMIZ1", "condition": "Breast cancer", "risk": "T", "or": 1.07},
    
    # Prostate Cancer Extended
    "rs10086908": {"gene": "8q24", "condition": "Prostate cancer", "risk": "T", "or": 1.25},
    "rs16902094": {"gene": "8q24", "condition": "Prostate cancer", "risk": "G", "or": 1.21},
    "rs445114": {"gene": "8q24", "condition": "Prostate cancer", "risk": "T", "or": 1.14},
    "rs11568818": {"gene": "MMP7", "condition": "Prostate cancer", "risk": "G", "or": 1.09},
    "rs7679673": {"gene": "4q24", "condition": "Prostate cancer", "risk": "C", "or": 1.15},
    "rs2735839": {"gene": "KLK3/PSA", "condition": "Prostate cancer", "risk": "G", "or": 1.20},
    "rs9364554": {"gene": "SLC22A3", "condition": "Prostate cancer", "risk": "T", "or": 1.12},
    "rs10934853": {"gene": "3q21", "condition": "Prostate cancer", "risk": "A", "or": 1.12},
    "rs17021918": {"gene": "PDLIM5", "condition": "Prostate cancer", "risk": "C", "or": 1.11},
    "rs12418451": {"gene": "11q13", "condition": "Prostate cancer", "risk": "A", "or": 1.16},
    "rs5759167": {"gene": "22q13", "condition": "Prostate cancer", "risk": "G", "or": 1.11},
    "rs2121875": {"gene": "5p15", "condition": "Prostate cancer", "risk": "T", "or": 1.09},
    "rs11214775": {"gene": "11q13", "condition": "Prostate cancer", "risk": "T", "or": 1.07},
    
    # Colorectal Cancer Extended
    "rs6691170": {"gene": "1q41", "condition": "CRC", "risk": "T", "or": 1.06},
    "rs10936599": {"gene": "TERC", "condition": "CRC", "risk": "C", "or": 1.10},
    "rs647161": {"gene": "5q31", "condition": "CRC", "risk": "A", "or": 1.11},
    "rs992157": {"gene": "EFEMP1", "condition": "CRC", "risk": "C", "or": 1.08},
    "rs12603526": {"gene": "17p13", "condition": "CRC", "risk": "C", "or": 1.08},
    "rs11169552": {"gene": "12q13", "condition": "CRC", "risk": "C", "or": 1.09},
    "rs3802842": {"gene": "11q23", "condition": "CRC", "risk": "C", "or": 1.11},
    "rs7229639": {"gene": "SMAD7", "condition": "CRC", "risk": "A", "or": 1.11},
    "rs10411210": {"gene": "RHPN2", "condition": "CRC", "risk": "T", "or": 1.10},
    "rs5934683": {"gene": "Xp22", "condition": "CRC", "risk": "C", "or": 1.07},
    
    # Lung Cancer Extended
    "rs2736100": {"gene": "TERT", "condition": "Lung cancer", "risk": "C", "or": 1.15},
    "rs402710": {"gene": "5p15.33", "condition": "Lung cancer", "risk": "T", "or": 1.14},
    "rs4488809": {"gene": "TP63", "condition": "Lung cancer", "risk": "T", "or": 1.12},
    "rs1051730": {"gene": "CHRNA3", "condition": "Lung cancer", "risk": "A", "or": 1.30},
    "rs8034191": {"gene": "15q25", "condition": "Lung cancer", "risk": "C", "or": 1.27},
    "rs4324798": {"gene": "6p21", "condition": "Lung cancer", "risk": "T", "or": 1.11},
    "rs6920364": {"gene": "BAT3", "condition": "Lung cancer", "risk": "C", "or": 1.10},
    
    # Melanoma
    "rs910873": {"gene": "20q11", "condition": "Melanoma", "risk": "C", "or": 1.75},
    "rs1801516": {"gene": "ATM", "condition": "Melanoma", "risk": "A", "or": 1.12},
    "rs1126809": {"gene": "TYR", "condition": "Melanoma", "risk": "A", "or": 1.21},
    "rs4911414": {"gene": "MTAP", "condition": "Melanoma", "risk": "T", "or": 1.14},
    "rs7023329": {"gene": "MTAP", "condition": "Melanoma", "risk": "A", "or": 1.16},
    "rs2218220": {"gene": "PLA2G6", "condition": "Melanoma", "risk": "T", "or": 1.09},
    "rs45430": {"gene": "TYR", "condition": "Melanoma", "risk": "T", "or": 1.14},
    "rs1015362": {"gene": "AFG3L1P", "condition": "Melanoma", "risk": "A", "or": 1.18},

    # =========================================================================
    # DIABETES EXTENDED
    # =========================================================================
    "rs1801214": {"gene": "WFS1", "condition": "T2D", "risk": "T", "or": 1.12},
    "rs4506565": {"gene": "TCF7L2", "condition": "T2D", "risk": "T", "or": 1.35},
    "rs10401969": {"gene": "CILP2", "condition": "T2D", "risk": "C", "or": 1.07},
    "rs17046216": {"gene": "KCNQ1", "condition": "T2D", "risk": "C", "or": 1.29},
    "rs2237895": {"gene": "KCNQ1", "condition": "T2D", "risk": "C", "or": 1.23},
    "rs231362": {"gene": "KCNQ1", "condition": "T2D", "risk": "G", "or": 1.08},
    "rs5015480": {"gene": "HHEX", "condition": "T2D", "risk": "C", "or": 1.13},
    "rs7756992": {"gene": "CDKAL1", "condition": "T2D", "risk": "G", "or": 1.16},
    "rs7754840": {"gene": "CDKAL1", "condition": "T2D", "risk": "C", "or": 1.14},
    "rs564398": {"gene": "CDKN2A/B", "condition": "T2D", "risk": "T", "or": 1.13},
    "rs4457053": {"gene": "ZBED3", "condition": "T2D", "risk": "G", "or": 1.08},
    "rs7961581": {"gene": "TSPAN8", "condition": "T2D", "risk": "C", "or": 1.09},
    "rs1531343": {"gene": "HMGA2", "condition": "T2D", "risk": "C", "or": 1.10},
    "rs12779790": {"gene": "CDC123", "condition": "T2D", "risk": "G", "or": 1.11},
    "rs849135": {"gene": "JAZF1", "condition": "T2D", "risk": "G", "or": 1.10},
    "rs1552224": {"gene": "ARAP1", "condition": "T2D", "risk": "A", "or": 1.14},
    "rs7593730": {"gene": "RBMS1", "condition": "T2D", "risk": "C", "or": 1.11},
    "rs243021": {"gene": "BCL11A", "condition": "T2D", "risk": "A", "or": 1.08},
    "rs6723108": {"gene": "TMEM163", "condition": "T2D", "risk": "T", "or": 1.06},
    "rs896854": {"gene": "TP53INP1", "condition": "T2D", "risk": "T", "or": 1.06},
    
    # =========================================================================
    # AUTOIMMUNE EXTENDED
    # =========================================================================
    # Rheumatoid Arthritis
    "rs6920220": {"gene": "TNFAIP3", "condition": "RA", "risk": "A", "or": 1.22},
    "rs10499194": {"gene": "6q23", "condition": "RA", "risk": "T", "or": 1.15},
    "rs2104286": {"gene": "IL2RA", "condition": "RA", "risk": "T", "or": 1.13},
    "rs10488631": {"gene": "IRF5", "condition": "RA", "risk": "C", "or": 1.17},
    "rs2230926": {"gene": "TNFAIP3", "condition": "RA", "risk": "G", "or": 1.22},
    "rs3761847": {"gene": "TRAF1-C5", "condition": "RA", "risk": "G", "or": 1.13},
    "rs10760130": {"gene": "STAT4", "condition": "RA", "risk": "A", "or": 1.14},
    "rs6822844": {"gene": "IL2-IL21", "condition": "RA", "risk": "T", "or": 1.15},
    
    # Multiple Sclerosis
    "rs3135388": {"gene": "HLA-DRA", "condition": "MS", "risk": "A", "or": 2.94},
    "rs6897932": {"gene": "IL7R", "condition": "MS", "risk": "C", "or": 1.18},
    "rs12722489": {"gene": "IL2RA", "condition": "MS", "risk": "C", "or": 1.25},
    "rs2300747": {"gene": "CD58", "condition": "MS", "risk": "A", "or": 1.23},
    "rs10492972": {"gene": "KIF1B", "condition": "MS", "risk": "C", "or": 1.35},
    "rs4963128": {"gene": "CLEC16A", "condition": "MS", "risk": "C", "or": 1.14},
    "rs2760524": {"gene": "CD226", "condition": "MS", "risk": "C", "or": 1.12},
    "rs4680534": {"gene": "TNFRSF1A", "condition": "MS", "risk": "C", "or": 1.11},
    
    # Type 1 Diabetes
    "rs2476601": {"gene": "PTPN22", "condition": "T1D", "risk": "A", "or": 1.97},
    "rs17696736": {"gene": "NAA25", "condition": "T1D", "risk": "G", "or": 1.28},
    "rs12251307": {"gene": "CLEC16A", "condition": "T1D", "risk": "T", "or": 1.22},
    "rs2292239": {"gene": "ERBB3", "condition": "T1D", "risk": "T", "or": 1.34},
    "rs1990760": {"gene": "IFIH1", "condition": "T1D", "risk": "C", "or": 1.21},
    "rs3087243": {"gene": "CTLA4", "condition": "T1D", "risk": "G", "or": 1.25},
    "rs2069763": {"gene": "IL2", "condition": "T1D", "risk": "G", "or": 1.31},
    "rs6476839": {"gene": "GLIS3", "condition": "T1D", "risk": "T", "or": 1.14},
    
    # Lupus (SLE)
    "rs7574865": {"gene": "STAT4", "condition": "SLE", "risk": "T", "or": 1.55},
    "rs13277113": {"gene": "BANK1", "condition": "SLE", "risk": "A", "or": 1.38},
    "rs1234315": {"gene": "TNFSF4", "condition": "SLE", "risk": "T", "or": 1.45},
    "rs2205960": {"gene": "TNFSF4", "condition": "SLE", "risk": "T", "or": 1.32},
    "rs10516487": {"gene": "BANK1", "condition": "SLE", "risk": "G", "or": 1.30},
    "rs3131379": {"gene": "MSH5", "condition": "SLE", "risk": "A", "or": 1.85},
    "rs2187668": {"gene": "HLA-DQA1", "condition": "SLE", "risk": "T", "or": 1.84},
    
    # IBD Extended
    "rs11465804": {"gene": "IL23R", "condition": "IBD", "risk": "T", "or": 1.42},
    "rs10883365": {"gene": "NKX2-3", "condition": "IBD", "risk": "A", "or": 1.19},
    "rs2066847": {"gene": "NOD2", "condition": "Crohn's", "risk": "C", "or": 3.99},
    "rs17234657": {"gene": "5p13", "condition": "Crohn's", "risk": "G", "or": 1.38},
    "rs1000113": {"gene": "5p13", "condition": "Crohn's", "risk": "C", "or": 1.25},
    "rs744166": {"gene": "STAT3", "condition": "Crohn's", "risk": "A", "or": 1.18},
    "rs3828309": {"gene": "ATG16L1", "condition": "Crohn's", "risk": "A", "or": 1.27},
    "rs2201841": {"gene": "IL23R", "condition": "Crohn's", "risk": "T", "or": 1.28},
    "rs6596075": {"gene": "C5orf56", "condition": "UC", "risk": "C", "or": 1.22},
    "rs3024505": {"gene": "IL10", "condition": "UC", "risk": "C", "or": 1.28},
    
    # =========================================================================
    # NEUROLOGICAL
    # =========================================================================
    # Parkinson's
    "rs11931074": {"gene": "SNCA", "condition": "Parkinson's", "risk": "G", "or": 1.34},
    "rs356220": {"gene": "SNCA", "condition": "Parkinson's", "risk": "T", "or": 1.28},
    "rs393152": {"gene": "MAPT", "condition": "Parkinson's", "risk": "G", "or": 1.45},
    "rs1491942": {"gene": "LRRK2", "condition": "Parkinson's", "risk": "C", "or": 1.14},
    "rs6599389": {"gene": "BST1", "condition": "Parkinson's", "risk": "T", "or": 1.14},
    "rs11060180": {"gene": "CCDC62", "condition": "Parkinson's", "risk": "A", "or": 1.11},
    "rs11868035": {"gene": "SREBF1", "condition": "Parkinson's", "risk": "A", "or": 1.11},
    "rs4698412": {"gene": "GAK", "condition": "Parkinson's", "risk": "A", "or": 1.14},
    "rs76763715": {"gene": "GBA", "condition": "Parkinson's", "risk": "A", "or": 5.43},
    
    # Migraine
    "rs2651899": {"gene": "PRDM16", "condition": "Migraine", "risk": "C", "or": 1.11},
    "rs10166942": {"gene": "TRPM8", "condition": "Migraine", "risk": "T", "or": 1.15},
    "rs11172113": {"gene": "LRP1", "condition": "Migraine", "risk": "T", "or": 1.14},
    "rs1835740": {"gene": "8q22", "condition": "Migraine", "risk": "A", "or": 1.23},
    "rs6790925": {"gene": "TGFBR2", "condition": "Migraine", "risk": "T", "or": 1.09},
    
    # Restless Legs Syndrome
    "rs3923809": {"gene": "BTBD9", "condition": "RLS", "risk": "A", "or": 1.80},
    "rs1026732": {"gene": "MEIS1", "condition": "RLS", "risk": "G", "or": 2.03},
    "rs6710341": {"gene": "PTPRD", "condition": "RLS", "risk": "A", "or": 1.44},
    
    # =========================================================================
    # EYE DISEASE EXTENDED
    # =========================================================================
    "rs10490924": {"gene": "ARMS2", "condition": "AMD", "risk": "T", "or": 2.69},
    "rs3750846": {"gene": "ARMS2", "condition": "AMD", "risk": "T", "or": 2.45},
    "rs2230199": {"gene": "C3", "condition": "AMD", "risk": "G", "or": 1.70},
    "rs641153": {"gene": "CFB", "condition": "AMD", "risk": "A", "or": 1.47},
    "rs9332739": {"gene": "C2", "condition": "AMD", "risk": "G", "or": 1.56},
    "rs800292": {"gene": "CFH", "condition": "AMD", "risk": "A", "or": 1.51},
    "rs429608": {"gene": "C2", "condition": "AMD", "risk": "A", "or": 1.52},
    
    # Glaucoma Extended
    "rs2165241": {"gene": "LOXL1", "condition": "Exfoliation glaucoma", "risk": "T", "or": 2.14},
    "rs3825942": {"gene": "LOXL1", "condition": "Exfoliation glaucoma", "risk": "A", "or": 3.00},
    "rs1048661": {"gene": "LOXL1", "condition": "Exfoliation glaucoma", "risk": "T", "or": 2.72},
    "rs2304718": {"gene": "SIX1", "condition": "POAG", "risk": "C", "or": 1.28},
    "rs10483727": {"gene": "SIX6", "condition": "POAG", "risk": "A", "or": 1.32},
    "rs4236601": {"gene": "CAV1-CAV2", "condition": "POAG", "risk": "A", "or": 1.25},
    "rs7555523": {"gene": "TMCO1", "condition": "POAG", "risk": "T", "or": 1.63},
    "rs1900004": {"gene": "ATXN2", "condition": "POAG", "risk": "T", "or": 1.17},
}
