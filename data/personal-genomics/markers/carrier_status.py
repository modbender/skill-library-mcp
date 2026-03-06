"""
Carrier Status Markers
Source: ClinVar, ACMG 59 genes, ACOG screening guidelines

These variants cause recessive genetic disorders when inherited from both parents.
Carrier testing is important for family planning.
"""

CARRIER_MARKERS = {
    # =========================================================================
    # CYSTIC FIBROSIS (CFTR) - Most common severe recessive in Caucasians
    # =========================================================================
    "rs113993960": {
        "gene": "CFTR",
        "variant": "F508del (p.Phe508del)",
        "condition": "Cystic Fibrosis",
        "pathogenic": True,
        "risk_allele": "delCTT",
        "frequency_eur": 0.02,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "acmg_class": "Pathogenic",
        "carrier_implications": "1 in 25 Caucasians are carriers. If both parents carry, 25% risk of affected child.",
        "clinical_features": ["chronic lung infections", "pancreatic insufficiency", "male infertility"],
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Partner screening strongly recommended before pregnancy",
                "1 in 25 Northern Europeans are carriers",
                "Genetic counseling for family planning",
                "Newborn screening available in most countries"
            ]
        }
    },
    "rs75527207": {
        "gene": "CFTR",
        "variant": "G551D",
        "condition": "Cystic Fibrosis",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_eur": 0.002,
        "note": "Ivacaftor (Kalydeco) effective for this mutation"
    },
    "rs121908769": {
        "gene": "CFTR",
        "variant": "G542X",
        "condition": "Cystic Fibrosis",
        "pathogenic": True,
        "risk_allele": "A"
    },
    "rs78655421": {
        "gene": "CFTR",
        "variant": "W1282X",
        "condition": "Cystic Fibrosis",
        "pathogenic": True,
        "risk_allele": "A",
        "note": "Common in Ashkenazi Jewish population"
    },
    "rs121908752": {
        "gene": "CFTR",
        "variant": "N1303K",
        "condition": "Cystic Fibrosis",
        "pathogenic": True,
        "risk_allele": "G"
    },

    # =========================================================================
    # SICKLE CELL DISEASE (HBB)
    # =========================================================================
    "rs334": {
        "gene": "HBB",
        "variant": "E6V (HbS)",
        "condition": "Sickle Cell Disease / Sickle Cell Trait",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_afr": 0.08,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "carrier_implications": "Carriers (trait) are protected against malaria. Two copies = sickle cell disease.",
        "clinical_features": ["pain crises", "anemia", "organ damage", "stroke risk"],
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Partner screening essential if carrier",
                "1 in 12 African Americans carry HbS",
                "Carrier status offers partial malaria protection",
                "Newborn screening mandatory in most US states"
            ]
        }
    },
    "rs33930165": {
        "gene": "HBB",
        "variant": "E6K (HbC)",
        "condition": "Hemoglobin C Disease",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_afr": 0.02,
        "note": "HbSC disease if combined with HbS"
    },

    # =========================================================================
    # BETA-THALASSEMIA (HBB)
    # =========================================================================
    "rs11549407": {
        "gene": "HBB",
        "variant": "IVS-I-110 (G>A)",
        "condition": "Beta-Thalassemia",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_mena": 0.03,
        "inheritance": "autosomal_recessive",
        "carrier_implications": "Carriers have thalassemia minor (mild anemia). Important to distinguish from iron deficiency.",
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Common in Mediterranean, Middle Eastern, South Asian populations",
                "Partner screening before pregnancy",
                "Carriers may have microcytic anemia (not iron deficiency)",
                "Do NOT supplement iron unless deficient"
            ]
        }
    },
    "rs33971440": {
        "gene": "HBB",
        "variant": "Cd39 (C>T)",
        "condition": "Beta-Thalassemia",
        "pathogenic": True,
        "risk_allele": "A"
    },

    # =========================================================================
    # TAY-SACHS DISEASE (HEXA)
    # =========================================================================
    "rs76175932": {
        "gene": "HEXA",
        "variant": "c.1278insTATC",
        "condition": "Tay-Sachs Disease",
        "pathogenic": True,
        "risk_allele": "insTATC",
        "frequency_aj": 0.03,
        "inheritance": "autosomal_recessive",
        "severity": "fatal",
        "clinical_features": ["neurodegeneration", "cherry-red spot macula", "death by age 4"],
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "1 in 30 Ashkenazi Jews are carriers",
                "Also elevated in French Canadians, Cajuns",
                "ACOG recommends screening if at-risk ancestry",
                "Partner screening essential"
            ]
        }
    },
    "rs121907976": {
        "gene": "HEXA",
        "variant": "c.1421+1G>C (IVS12)",
        "condition": "Tay-Sachs Disease",
        "pathogenic": True,
        "risk_allele": "C"
    },

    # =========================================================================
    # GAUCHER DISEASE (GBA)
    # =========================================================================
    "rs76763715": {
        "gene": "GBA",
        "variant": "N370S (p.Asn409Ser)",
        "condition": "Gaucher Disease Type 1",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_aj": 0.04,
        "inheritance": "autosomal_recessive",
        "severity": "variable",
        "note": "Also Parkinson's disease risk factor when heterozygous",
        "clinical_features": ["hepatosplenomegaly", "bone disease", "anemia", "thrombocytopenia"],
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Most common lysosomal storage disorder",
                "1 in 15 Ashkenazi Jews carry a GBA mutation",
                "Type 1 is treatable with enzyme replacement",
                "Note: Heterozygous carriers have increased Parkinson's risk"
            ]
        }
    },
    "rs421016": {
        "gene": "GBA",
        "variant": "L444P (p.Leu483Pro)",
        "condition": "Gaucher Disease",
        "pathogenic": True,
        "risk_allele": "A",
        "note": "Associated with more severe disease"
    },

    # =========================================================================
    # FAMILIAL DYSAUTONOMIA (IKBKAP/ELP1)
    # =========================================================================
    "rs121908397": {
        "gene": "IKBKAP",
        "variant": "IVS20+6T>C",
        "condition": "Familial Dysautonomia",
        "pathogenic": True,
        "risk_allele": "C",
        "frequency_aj": 0.03,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "clinical_features": ["autonomic dysfunction", "insensitivity to pain", "dysautonomic crises"],
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Almost exclusively Ashkenazi Jewish",
                "1 in 30 Ashkenazi Jews are carriers",
                "Included in Jewish genetic disease panels"
            ]
        }
    },

    # =========================================================================
    # CANAVAN DISEASE (ASPA)
    # =========================================================================
    "rs104894091": {
        "gene": "ASPA",
        "variant": "E285A (p.Glu285Ala)",
        "condition": "Canavan Disease",
        "pathogenic": True,
        "risk_allele": "C",
        "frequency_aj": 0.02,
        "inheritance": "autosomal_recessive",
        "severity": "fatal",
        "clinical_features": ["leukodystrophy", "macrocephaly", "hypotonia", "death in childhood"]
    },

    # =========================================================================
    # PHENYLKETONURIA (PAH)
    # =========================================================================
    "rs5030858": {
        "gene": "PAH",
        "variant": "R408W",
        "condition": "Phenylketonuria (PKU)",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_eur": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "treatable",
        "clinical_features": ["intellectual disability if untreated", "seizures", "behavioral problems"],
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Newborn screening catches affected infants",
                "Phenylalanine-restricted diet prevents disability",
                "Carrier screening available"
            ]
        }
    },
    "rs62508196": {
        "gene": "PAH",
        "variant": "IVS12+1G>A",
        "condition": "Phenylketonuria (PKU)",
        "pathogenic": True,
        "risk_allele": "A"
    },

    # =========================================================================
    # SPINAL MUSCULAR ATROPHY (SMN1)
    # =========================================================================
    "rs1060501349": {
        "gene": "SMN1",
        "variant": "Exon 7 deletion",
        "condition": "Spinal Muscular Atrophy",
        "pathogenic": True,
        "inheritance": "autosomal_recessive",
        "severity": "severe_to_fatal",
        "frequency_pan": 0.02,
        "clinical_features": ["progressive muscle weakness", "respiratory failure", "variable onset"],
        "note": "Carrier testing requires copy number analysis (not standard SNP)",
        "actionable": {
            "priority": "high",
            "action_type": "genetic_counseling",
            "recommendations": [
                "1 in 50 people are carriers (all ethnicities)",
                "ACOG recommends carrier screening",
                "Treatments now available (Spinraza, Zolgensma)",
                "Early treatment dramatically improves outcomes"
            ]
        }
    },

    # =========================================================================
    # FANCONI ANEMIA (FANCC)
    # =========================================================================
    "rs104886517": {
        "gene": "FANCC",
        "variant": "IVS4+4A>T",
        "condition": "Fanconi Anemia Type C",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_aj": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "clinical_features": ["bone marrow failure", "birth defects", "cancer predisposition"]
    },

    # =========================================================================
    # FAMILIAL MEDITERRANEAN FEVER (MEFV)
    # =========================================================================
    "rs61752717": {
        "gene": "MEFV",
        "variant": "M694V",
        "condition": "Familial Mediterranean Fever",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_mena": 0.03,
        "frequency_aj": 0.02,
        "inheritance": "autosomal_recessive",
        "severity": "treatable",
        "clinical_features": ["recurrent fevers", "serositis", "amyloidosis if untreated"],
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Common in Mediterranean populations (Armenians, Turks, Arabs, Jews)",
                "Treatable with colchicine",
                "Without treatment, risk of renal amyloidosis"
            ]
        }
    },
    "rs28940578": {
        "gene": "MEFV",
        "variant": "M680I",
        "condition": "Familial Mediterranean Fever",
        "pathogenic": True,
        "risk_allele": "A"
    },
    "rs28940579": {
        "gene": "MEFV",
        "variant": "V726A",
        "condition": "Familial Mediterranean Fever",
        "pathogenic": True,
        "risk_allele": "T"
    },

    # =========================================================================
    # HEREDITARY DEAFNESS (GJB2 - Connexin 26)
    # =========================================================================
    "rs80338939": {
        "gene": "GJB2",
        "variant": "35delG",
        "condition": "Hereditary Hearing Loss (DFNB1)",
        "pathogenic": True,
        "risk_allele": "delG",
        "frequency_eur": 0.02,
        "inheritance": "autosomal_recessive",
        "severity": "non-lethal",
        "clinical_features": ["congenital deafness", "usually non-syndromic"],
        "actionable": {
            "priority": "medium",
            "action_type": "genetic_counseling",
            "recommendations": [
                "Most common genetic cause of deafness",
                "2% of Caucasians carry 35delG",
                "Cochlear implants highly effective",
                "Newborn hearing screening catches affected infants"
            ]
        }
    },
    "rs72474224": {
        "gene": "GJB2",
        "variant": "167delT",
        "condition": "Hereditary Hearing Loss",
        "pathogenic": True,
        "risk_allele": "delT",
        "frequency_aj": 0.04
    },
    "rs80338943": {
        "gene": "GJB2",
        "variant": "235delC",
        "condition": "Hereditary Hearing Loss",
        "pathogenic": True,
        "risk_allele": "delC",
        "frequency_eas": 0.01
    },

    # =========================================================================
    # BLOOM SYNDROME (BLM)
    # =========================================================================
    "rs113993991": {
        "gene": "BLM",
        "variant": "blmAsh",
        "condition": "Bloom Syndrome",
        "pathogenic": True,
        "risk_allele": "del",
        "frequency_aj": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "clinical_features": ["growth retardation", "sun sensitivity", "cancer predisposition", "immunodeficiency"]
    },

    # =========================================================================
    # NIEMANN-PICK DISEASE (SMPD1)
    # =========================================================================
    "rs120074129": {
        "gene": "SMPD1",
        "variant": "R496L",
        "condition": "Niemann-Pick Disease Type A",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_aj": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "fatal",
        "clinical_features": ["hepatosplenomegaly", "neurodegeneration", "cherry-red spot"]
    },
    "rs120074130": {
        "gene": "SMPD1",
        "variant": "L302P",
        "condition": "Niemann-Pick Disease Type A",
        "pathogenic": True,
        "risk_allele": "C"
    },

    # =========================================================================
    # ALPHA-1 ANTITRYPSIN DEFICIENCY (SERPINA1)
    # =========================================================================
    "rs28929474": {
        "gene": "SERPINA1",
        "variant": "Z allele (E342K)",
        "condition": "Alpha-1 Antitrypsin Deficiency",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_eur": 0.02,
        "inheritance": "autosomal_codominant",
        "severity": "variable",
        "clinical_features": ["emphysema", "liver disease", "panniculitis"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_screening",
            "recommendations": [
                "ZZ homozygotes: high COPD risk, especially if smoking",
                "Avoid smoking absolutely",
                "Augmentation therapy available",
                "Liver function monitoring recommended"
            ]
        }
    },
    "rs17580": {
        "gene": "SERPINA1",
        "variant": "S allele (E264V)",
        "condition": "Alpha-1 Antitrypsin Deficiency",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_eur": 0.03,
        "note": "Mild deficiency alone; SZ compound heterozygotes have intermediate risk"
    },

    # =========================================================================
    # WILSON DISEASE (ATP7B)
    # =========================================================================
    "rs76151636": {
        "gene": "ATP7B",
        "variant": "H1069Q",
        "condition": "Wilson Disease",
        "pathogenic": True,
        "risk_allele": "A",
        "frequency_eur": 0.005,
        "inheritance": "autosomal_recessive",
        "severity": "treatable",
        "clinical_features": ["liver disease", "neuropsychiatric symptoms", "Kayser-Fleischer rings"],
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Treatable with copper chelation",
                "Early diagnosis prevents irreversible damage",
                "Check ceruloplasmin if symptomatic"
            ]
        }
    },

    # =========================================================================
    # USHER SYNDROME (MYO7A)
    # =========================================================================
    "rs111033224": {
        "gene": "MYO7A",
        "variant": "c.3596_3597del",
        "condition": "Usher Syndrome Type 1B",
        "pathogenic": True,
        "risk_allele": "del",
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "clinical_features": ["congenital deafness", "progressive blindness", "vestibular dysfunction"]
    },

    # =========================================================================
    # MUCOLIPIDOSIS TYPE IV (MCOLN1)
    # =========================================================================
    "rs104886027": {
        "gene": "MCOLN1",
        "variant": "IVS3-2A>G",
        "condition": "Mucolipidosis Type IV",
        "pathogenic": True,
        "risk_allele": "G",
        "frequency_aj": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "severe",
        "clinical_features": ["psychomotor delay", "visual impairment", "achlorhydria"]
    },

    # =========================================================================
    # MAPLE SYRUP URINE DISEASE (BCKDHA)
    # =========================================================================
    "rs120074133": {
        "gene": "BCKDHA",
        "variant": "Y393N",
        "condition": "Maple Syrup Urine Disease",
        "pathogenic": True,
        "risk_allele": "A",
        "inheritance": "autosomal_recessive",
        "severity": "severe_treatable",
        "clinical_features": ["metabolic crisis", "maple syrup odor", "neurological damage if untreated"]
    },

    # =========================================================================
    # GLYCOGEN STORAGE DISEASE 1A (G6PC)
    # =========================================================================
    "rs80356471": {
        "gene": "G6PC",
        "variant": "R83C",
        "condition": "Glycogen Storage Disease Type 1a",
        "pathogenic": True,
        "risk_allele": "T",
        "frequency_aj": 0.01,
        "inheritance": "autosomal_recessive",
        "severity": "severe_treatable",
        "clinical_features": ["hepatomegaly", "hypoglycemia", "growth failure"]
    },
}

# Summary for agent
CARRIER_SCREENING_PANELS = {
    "ashkenazi_jewish": [
        "HEXA (Tay-Sachs)",
        "GBA (Gaucher)",
        "IKBKAP (Familial Dysautonomia)",
        "ASPA (Canavan)",
        "FANCC (Fanconi Anemia)",
        "BLM (Bloom Syndrome)",
        "CFTR (Cystic Fibrosis)",
        "SMPD1 (Niemann-Pick)",
        "MCOLN1 (Mucolipidosis IV)"
    ],
    "mediterranean": [
        "HBB (Beta-Thalassemia)",
        "MEFV (FMF)",
        "G6PD"
    ],
    "african_ancestry": [
        "HBB (Sickle Cell)",
        "G6PD"
    ],
    "south_asian": [
        "HBB (Beta-Thalassemia)",
        "G6PD"
    ],
    "pan_ethnic": [
        "CFTR (Cystic Fibrosis)",
        "SMN1 (SMA)",
        "GJB2 (Hearing Loss)",
        "PAH (PKU)"
    ]
}
