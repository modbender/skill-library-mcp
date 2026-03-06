"""
Extended Pharmacogenomics Markers
Additional drug metabolism, transport, and response markers.
"""

PHARMACOGENOMICS_EXTENDED = {
    # =========================================================================
    # CYP2D6 Extended
    # =========================================================================
    "rs1135840": {"gene": "CYP2D6", "variant": "*2/*10 tag", "function": "Variable", "risk_allele": "C"},
    "rs1080985": {"gene": "CYP2D6", "variant": "*2A tag", "risk_allele": "G"},
    "rs28371703": {"gene": "CYP2D6", "variant": "*9", "function": "Decreased", "risk_allele": "del"},
    "rs5030656": {"gene": "CYP2D6", "variant": "*9 tag", "function": "Decreased", "risk_allele": "A"},
    "rs59421388": {"gene": "CYP2D6", "variant": "*29", "function": "Decreased", "risk_allele": "G"},
    "rs28371699": {"gene": "CYP2D6", "variant": "*4 tag", "risk_allele": "G"},

    # =========================================================================
    # CYP2C19 Extended
    # =========================================================================
    "rs17884712": {"gene": "CYP2C19", "variant": "*9", "function": "Decreased", "risk_allele": "A"},
    "rs6413438": {"gene": "CYP2C19", "variant": "*10", "function": "Decreased", "risk_allele": "T"},
    "rs55752064": {"gene": "CYP2C19", "variant": "*13", "function": "No function", "risk_allele": "T"},
    "rs17879685": {"gene": "CYP2C19", "variant": "*14", "function": "Decreased", "risk_allele": "A"},
    "rs17882687": {"gene": "CYP2C19", "variant": "*15", "function": "Decreased", "risk_allele": "A"},
    "rs192154563": {"gene": "CYP2C19", "variant": "*16", "function": "No function", "risk_allele": "T"},

    # =========================================================================
    # CYP2C9 Extended
    # =========================================================================
    "rs9332131": {"gene": "CYP2C9", "variant": "*6", "function": "No function", "risk_allele": "del"},
    "rs67807361": {"gene": "CYP2C9", "variant": "*13", "function": "Decreased", "risk_allele": "C"},
    "rs2256871": {"gene": "CYP2C9", "variant": "*9", "function": "Decreased", "risk_allele": "A"},
    "rs28371685": {"gene": "CYP2C9", "variant": "*5", "function": "Decreased", "risk_allele": "G"},

    # =========================================================================
    # CYP2A6 - Nicotine, Tegafur
    # =========================================================================
    "rs28399433": {"gene": "CYP2A6", "variant": "*9", "function": "Decreased", "risk_allele": "T",
        "drugs": ["nicotine", "tegafur", "letrozole"]},
    "rs28399444": {"gene": "CYP2A6", "variant": "*12", "function": "Decreased", "risk_allele": "A"},
    "rs28399454": {"gene": "CYP2A6", "variant": "*17", "function": "Decreased", "risk_allele": "A"},
    "rs1801272": {"gene": "CYP2A6", "variant": "*2", "function": "No function", "risk_allele": "A"},
    "rs5031016": {"gene": "CYP2A6", "variant": "*7", "function": "No function", "risk_allele": "C"},

    # =========================================================================
    # CYP2B6 Extended
    # =========================================================================
    "rs8192709": {"gene": "CYP2B6", "variant": "*2", "function": "Increased", "risk_allele": "T"},
    "rs2279343": {"gene": "CYP2B6", "variant": "*4", "function": "Increased", "risk_allele": "A"},
    "rs3211371": {"gene": "CYP2B6", "variant": "*5", "function": "Decreased", "risk_allele": "A"},
    "rs3745274": {"gene": "CYP2B6", "variant": "*6", "function": "Decreased", "risk_allele": "T"},
    "rs35979566": {"gene": "CYP2B6", "variant": "*15", "function": "Decreased", "risk_allele": "A"},
    "rs35303484": {"gene": "CYP2B6", "variant": "*16", "function": "Decreased", "risk_allele": "C"},

    # =========================================================================
    # CYP3A4 Extended
    # =========================================================================
    "rs2740574": {"gene": "CYP3A4", "variant": "*1B", "function": "Variable", "risk_allele": "G"},
    "rs4986910": {"gene": "CYP3A4", "variant": "*3", "function": "Decreased", "risk_allele": "G"},
    "rs4986909": {"gene": "CYP3A4", "variant": "*2", "function": "Decreased", "risk_allele": "C"},
    "rs55785340": {"gene": "CYP3A4", "variant": "*20", "function": "No function", "risk_allele": "A"},
    "rs28371759": {"gene": "CYP3A4", "variant": "*17", "function": "Decreased", "risk_allele": "T"},

    # =========================================================================
    # CYP1A2 Extended
    # =========================================================================
    "rs2069514": {"gene": "CYP1A2", "variant": "*1C", "function": "Decreased", "risk_allele": "A"},
    "rs12720461": {"gene": "CYP1A2", "variant": "*1K", "function": "Decreased", "risk_allele": "T"},
    "rs2470890": {"gene": "CYP1A2", "variant": "*1F tag", "function": "Variable", "risk_allele": "C"},
    "rs35694136": {"gene": "CYP1A2", "variant": "*1L", "function": "Decreased", "risk_allele": "del"},

    # =========================================================================
    # CYP4F2 - Warfarin
    # =========================================================================
    "rs2108622": {"gene": "CYP4F2", "variant": "*3", "function": "Decreased", "risk_allele": "T",
        "drugs": ["warfarin"], "note": "Higher warfarin dose needed"},

    # =========================================================================
    # DPYD Extended
    # =========================================================================
    "rs1801265": {"gene": "DPYD", "variant": "*9A", "function": "Normal", "risk_allele": "A"},
    "rs1801266": {"gene": "DPYD", "variant": "*9B", "function": "Decreased", "risk_allele": "A"},
    "rs2297595": {"gene": "DPYD", "variant": "M166V", "function": "Decreased", "risk_allele": "C"},
    "rs1801159": {"gene": "DPYD", "variant": "I543V", "function": "Normal", "risk_allele": "T"},
    "rs1801158": {"gene": "DPYD", "variant": "S534N", "function": "Normal", "risk_allele": "G"},

    # =========================================================================
    # UGT1A1 Extended
    # =========================================================================
    "rs887829": {"gene": "UGT1A1", "variant": "*80", "function": "Decreased", "risk_allele": "T"},
    "rs10929302": {"gene": "UGT1A1", "variant": "*60", "function": "Decreased", "risk_allele": "A"},
    "rs4124874": {"gene": "UGT1A1", "variant": "Promoter", "function": "Variable", "risk_allele": "T"},
    "rs6742078": {"gene": "UGT1A1", "variant": "*28 tag", "function": "Decreased", "risk_allele": "T"},

    # =========================================================================
    # NAT2 - Isoniazid acetylation
    # =========================================================================
    "rs1799929": {"gene": "NAT2", "variant": "*11", "function": "Slow", "risk_allele": "A"},
    "rs1208": {"gene": "NAT2", "variant": "*4 tag", "function": "Rapid", "risk_allele": "A"},
    "rs1041983": {"gene": "NAT2", "variant": "*5/*6 tag", "function": "Slow", "risk_allele": "C"},
    "rs1495741": {"gene": "NAT2", "variant": "Phenotype tag", "function": "Variable", "risk_allele": "A"},

    # =========================================================================
    # ABCB1 (P-glycoprotein) - Drug transport
    # =========================================================================
    "rs1045642": {"gene": "ABCB1", "variant": "C3435T", "function": "Decreased", "risk_allele": "T",
        "drugs": ["digoxin", "fexofenadine", "cyclosporine", "tacrolimus"]},
    "rs2032582": {"gene": "ABCB1", "variant": "G2677T/A", "function": "Variable", "risk_allele": "T"},
    "rs1128503": {"gene": "ABCB1", "variant": "C1236T", "function": "Variable", "risk_allele": "T"},

    # =========================================================================
    # ABCG2 (BCRP) - Drug transport
    # =========================================================================
    "rs2231142": {"gene": "ABCG2", "variant": "Q141K", "function": "Decreased", "risk_allele": "A",
        "drugs": ["rosuvastatin", "atorvastatin", "sulfasalazine", "methotrexate", "topotecan"]},

    # =========================================================================
    # SLC Transporters
    # =========================================================================
    "rs2306283": {"gene": "SLCO1B1", "variant": "*1b", "function": "Increased", "risk_allele": "G"},
    "rs4149015": {"gene": "SLCO1B1", "variant": "*1a", "function": "Normal", "risk_allele": "G"},
    "rs11045819": {"gene": "SLCO1B1", "variant": "*14", "function": "Decreased", "risk_allele": "A"},
    "rs2306168": {"gene": "SLCO1B3", "variant": "M233I", "function": "Variable", "risk_allele": "C"},
    "rs7311358": {"gene": "SLCO1B3", "variant": "S112A", "function": "Variable", "risk_allele": "A"},
    "rs316019": {"gene": "SLC22A1", "variant": "*2", "function": "Decreased", "risk_allele": "C",
        "drugs": ["metformin"]},
    "rs628031": {"gene": "SLC22A1", "variant": "M408V", "function": "Variable", "risk_allele": "A"},
    "rs72552763": {"gene": "SLC22A1", "variant": "*3", "function": "Decreased", "risk_allele": "del"},
    "rs12208357": {"gene": "SLC22A1", "variant": "*4", "function": "Decreased", "risk_allele": "C"},
    "rs34130495": {"gene": "SLC22A1", "variant": "*5", "function": "Decreased", "risk_allele": "T"},
    "rs34059508": {"gene": "SLC22A1", "variant": "*6", "function": "Decreased", "risk_allele": "G"},

    # =========================================================================
    # Beta Blockers Response
    # =========================================================================
    "rs1801252": {"gene": "ADRB1", "variant": "Ser49Gly", "function": "Variable", "risk_allele": "G",
        "drugs": ["metoprolol", "carvedilol", "atenolol"]},
    "rs1801253": {"gene": "ADRB1", "variant": "Arg389Gly", "function": "Variable", "risk_allele": "C"},
    "rs1042713": {"gene": "ADRB2", "variant": "Arg16Gly", "function": "Variable", "risk_allele": "A",
        "drugs": ["albuterol", "salmeterol"]},
    "rs1042714": {"gene": "ADRB2", "variant": "Gln27Glu", "function": "Variable", "risk_allele": "C"},

    # =========================================================================
    # ACE Inhibitors
    # =========================================================================
    "rs4646994": {"gene": "ACE", "variant": "I/D", "function": "Variable", "risk_allele": "D",
        "drugs": ["enalapril", "lisinopril", "ramipril"],
        "note": "DD may have better BP response but more cough"},

    # =========================================================================
    # Opioids Extended
    # =========================================================================
    "rs1799971": {"gene": "OPRM1", "variant": "A118G", "function": "Variable", "risk_allele": "G",
        "drugs": ["morphine", "fentanyl", "methadone"],
        "note": "G allele may need higher doses"},
    "rs2952768": {"gene": "KCNJ6", "variant": "Opioid response", "function": "Variable", "risk_allele": "T"},
    "rs563649": {"gene": "OPRM1", "variant": "Promoter", "function": "Variable", "risk_allele": "G"},

    # =========================================================================
    # Antidepressants
    # =========================================================================
    "rs6295": {"gene": "HTR1A", "variant": "-1019C>G", "function": "Variable", "risk_allele": "G",
        "drugs": ["SSRIs", "buspirone"]},
    "rs7997012": {"gene": "HTR2A", "variant": "Intron 2", "function": "Variable", "risk_allele": "A",
        "drugs": ["SSRIs"]},
    "rs17288723": {"gene": "HTR2A", "variant": "SSRI response", "function": "Variable", "risk_allele": "T"},
    "rs4795541": {"gene": "SLC6A4", "variant": "5-HTTLPR L/S", "function": "Variable", "risk_allele": "S",
        "drugs": ["SSRIs"]},

    # =========================================================================
    # Antipsychotics
    # =========================================================================
    "rs6277": {"gene": "DRD2", "variant": "C957T", "function": "Variable", "risk_allele": "T",
        "drugs": ["haloperidol", "risperidone"]},
    "rs1800955": {"gene": "DRD4", "variant": "-521C>T", "function": "Variable", "risk_allele": "T"},
    "rs165599": {"gene": "COMT", "variant": "Antipsychotic response", "function": "Variable", "risk_allele": "A"},

    # =========================================================================
    # Anticoagulants Extended
    # =========================================================================
    "rs2359612": {"gene": "VKORC1", "variant": "1173C>T", "function": "Variable", "risk_allele": "T"},
    "rs8050894": {"gene": "VKORC1", "variant": "Haplotype tag", "function": "Variable", "risk_allele": "G"},
    "rs7294": {"gene": "VKORC1", "variant": "3730G>A", "function": "Variable", "risk_allele": "A"},
    "rs17708472": {"gene": "CYP4F2", "variant": "W12G", "function": "Decreased", "risk_allele": "A"},

    # =========================================================================
    # Antiplatelet Extended
    # =========================================================================
    "rs6809699": {"gene": "ITGB3", "variant": "PlA1/A2", "function": "Variable", "risk_allele": "T",
        "drugs": ["aspirin"]},
    "rs5918": {"gene": "ITGB3", "variant": "L33P", "function": "Variable", "risk_allele": "C",
        "drugs": ["aspirin", "clopidogrel"]},
    "rs12041331": {"gene": "PEAR1", "variant": "Aspirin response", "function": "Variable", "risk_allele": "A"},
    "rs1472122": {"gene": "P2RY12", "variant": "Clopidogrel response", "function": "Variable", "risk_allele": "T"},

    # =========================================================================
    # Proton Pump Inhibitors
    # =========================================================================
    "rs17110453": {"gene": "CYP2C19", "variant": "PPI metabolism", "function": "Variable", "risk_allele": "A"},
    "rs12571421": {"gene": "CYP2C19", "variant": "PPI response", "function": "Variable", "risk_allele": "A"},

    # =========================================================================
    # Statins Extended
    # =========================================================================
    "rs17238540": {"gene": "HMGCR", "variant": "Statin efficacy", "function": "Variable", "risk_allele": "T",
        "drugs": ["atorvastatin", "simvastatin", "pravastatin"]},
    "rs12916": {"gene": "HMGCR", "variant": "LDL response", "function": "Variable", "risk_allele": "T"},
    "rs17244841": {"gene": "HMGCR", "variant": "H7 haplotype", "function": "Decreased response", "risk_allele": "A"},
    "rs2199936": {"gene": "GATM", "variant": "Myopathy risk", "function": "Variable", "risk_allele": "A"},
    "rs1346268": {"gene": "CLMN", "variant": "Myopathy risk", "function": "Variable", "risk_allele": "C"},

    # =========================================================================
    # Immunosuppressants
    # =========================================================================
    "rs1057868": {"gene": "POR", "variant": "A503V", "function": "Decreased", "risk_allele": "T",
        "drugs": ["tacrolimus", "cyclosporine"]},
    "rs11568658": {"gene": "CYP3A4", "variant": "Tacrolimus", "function": "Variable", "risk_allele": "C"},
    "rs2740574": {"gene": "CYP3A4", "variant": "*1B", "function": "Variable", "risk_allele": "G"},

    # =========================================================================
    # Chemotherapy Extended
    # =========================================================================
    "rs9344": {"gene": "CCND1", "variant": "A870G", "function": "Variable", "risk_allele": "A",
        "drugs": ["5-FU"]},
    "rs25487": {"gene": "XRCC1", "variant": "R399Q", "function": "Variable", "risk_allele": "A",
        "drugs": ["platinum compounds"]},
    "rs1695": {"gene": "GSTP1", "variant": "I105V", "function": "Decreased", "risk_allele": "G",
        "drugs": ["platinum compounds", "anthracyclines"]},
    "rs1138272": {"gene": "GSTP1", "variant": "A114V", "function": "Decreased", "risk_allele": "C"},
    "rs3212986": {"gene": "ERCC1", "variant": "C8092A", "function": "Variable", "risk_allele": "T",
        "drugs": ["platinum compounds"]},
    "rs11615": {"gene": "ERCC1", "variant": "N118N", "function": "Variable", "risk_allele": "T"},
    "rs1801131": {"gene": "MTHFR", "variant": "A1298C", "function": "Decreased", "risk_allele": "G",
        "drugs": ["methotrexate"]},
    "rs1801133": {"gene": "MTHFR", "variant": "C677T", "function": "Decreased", "risk_allele": "A",
        "drugs": ["methotrexate"]},
    "rs1051266": {"gene": "SLC19A1", "variant": "G80A", "function": "Variable", "risk_allele": "A",
        "drugs": ["methotrexate"]},

    # =========================================================================
    # Biologics
    # =========================================================================
    "rs396991": {"gene": "FCGR3A", "variant": "V158F", "function": "Variable", "risk_allele": "T",
        "drugs": ["rituximab", "trastuzumab", "cetuximab"]},
    "rs1801274": {"gene": "FCGR2A", "variant": "H131R", "function": "Variable", "risk_allele": "G",
        "drugs": ["rituximab", "infliximab"]},

    # =========================================================================
    # Allopurinol / Febuxostat
    # =========================================================================
    "rs2231142": {"gene": "ABCG2", "variant": "Q141K", "function": "Decreased transport", "risk_allele": "A",
        "drugs": ["allopurinol"], "note": "Higher urate, may need higher dose"},

    # =========================================================================
    # Anesthetics
    # =========================================================================
    "rs2279343": {"gene": "CYP2B6", "variant": "Propofol metabolism", "function": "Increased", "risk_allele": "A"},
    "rs12721655": {"gene": "ACHE", "variant": "Succinylcholine", "function": "Decreased", "risk_allele": "G"},

    # =========================================================================
    # Hormonal
    # =========================================================================
    "rs700518": {"gene": "CYP19A1", "variant": "Aromatase inhibitor response", "function": "Variable", "risk_allele": "A",
        "drugs": ["letrozole", "anastrozole"]},
    "rs2234693": {"gene": "ESR1", "variant": "PvuII", "function": "Variable", "risk_allele": "T",
        "drugs": ["tamoxifen", "HRT"]},
    "rs9340799": {"gene": "ESR1", "variant": "XbaI", "function": "Variable", "risk_allele": "A"},

    # =========================================================================
    # Diabetes Medications
    # =========================================================================
    "rs622342": {"gene": "SLC22A1", "variant": "Metformin transporter", "function": "Variable", "risk_allele": "C"},
    "rs2289669": {"gene": "SLC47A1", "variant": "MATE1", "function": "Decreased", "risk_allele": "A",
        "drugs": ["metformin"]},
    "rs8065082": {"gene": "SLC47A2", "variant": "MATE2-K", "function": "Variable", "risk_allele": "T"},
    "rs5219": {"gene": "KCNJ11", "variant": "E23K", "function": "Variable", "risk_allele": "T",
        "drugs": ["sulfonylureas"]},
    "rs757110": {"gene": "ABCC8", "variant": "A1369S", "function": "Variable", "risk_allele": "G",
        "drugs": ["sulfonylureas"]},
}
