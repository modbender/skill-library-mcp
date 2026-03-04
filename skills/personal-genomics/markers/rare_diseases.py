"""
Rare Disease Markers Database.
Markers for rare genetic conditions, validated against consumer arrays.
Citations from ClinVar, OMIM, and peer-reviewed literature.
"""

RARE_DISEASE_MARKERS = {
    # =========================================================================
    # LYSOSOMAL STORAGE DISORDERS
    # =========================================================================
    
    "rs76763715": {
        "gene": "GBA",
        "name": "Gaucher Disease N370S",
        "variant": "N370S",
        "risk_allele": "A",
        "condition": "Gaucher disease type 1",
        "inheritance": "autosomal_recessive",
        "population_frequency": "1:855 Ashkenazi Jewish",
        "evidence": "strong",
        "references": ["PMID:11389483", "ClinVar:VCV000004288"],
        "carrier_implications": "Increased Parkinson's risk in carriers",
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Consider genetic counseling if carrier",
                "Screen for Parkinson's symptoms in carriers",
                "Family testing recommended"
            ]
        }
    },
    
    "rs421016": {
        "gene": "GBA",
        "name": "Gaucher L444P",
        "variant": "L444P",
        "risk_allele": "A",
        "condition": "Gaucher disease",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["PMID:8490621"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["Genetic counseling recommended"]
        }
    },
    
    "rs28940871": {
        "gene": "HEXA",
        "name": "Tay-Sachs carrier",
        "risk_allele": "T",
        "condition": "Tay-Sachs disease",
        "inheritance": "autosomal_recessive",
        "population_frequency": "1:30 Ashkenazi Jewish, 1:250 general",
        "evidence": "strong",
        "references": ["PMID:2116665", "ClinVar:VCV000003764"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Partner testing if carrier",
                "Genetic counseling before pregnancy"
            ]
        }
    },
    
    "rs80338939": {
        "gene": "SMPD1",
        "name": "Niemann-Pick A/B",
        "risk_allele": "T",
        "condition": "Niemann-Pick disease",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000007069"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["Genetic counseling if carrier"]
        }
    },
    
    "rs80338945": {
        "gene": "IDUA",
        "name": "Hurler syndrome marker",
        "risk_allele": "A",
        "condition": "Mucopolysaccharidosis type I (Hurler)",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000003811"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["Carrier testing for partners"]
        }
    },
    
    "rs281865161": {
        "gene": "GAA",
        "name": "Pompe disease marker",
        "risk_allele": "A",
        "condition": "Pompe disease (Glycogen storage disease II)",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000005335"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Enzyme activity testing if homozygous",
                "ERT available for treatment"
            ]
        }
    },
    
    # =========================================================================
    # CONNECTIVE TISSUE DISORDERS
    # =========================================================================
    
    "rs137853242": {
        "gene": "FBN1",
        "name": "Marfan syndrome marker",
        "risk_allele": "T",
        "condition": "Marfan syndrome",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000015089"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Cardiac evaluation (aortic root dilation)",
                "Regular ophthalmologic exams",
                "Activity restrictions for contact sports"
            ]
        }
    },
    
    "rs121909211": {
        "gene": "COL3A1",
        "name": "Ehlers-Danlos vascular type",
        "risk_allele": "A",
        "condition": "Ehlers-Danlos syndrome vascular type",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000014236"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "CRITICAL: Vascular rupture risk",
                "Avoid invasive procedures when possible",
                "Blood pressure management essential",
                "Pregnancy high-risk - specialist care needed"
            ]
        }
    },
    
    # =========================================================================
    # NEUROLOGICAL RARE DISEASES
    # =========================================================================
    
    "rs63750847": {
        "gene": "APP",
        "name": "Early-onset Alzheimer's",
        "risk_allele": "A",
        "condition": "Early-onset familial Alzheimer's disease",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["PMID:1944558", "ClinVar:VCV000018267"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Genetic counseling essential",
                "Discuss predictive testing implications",
                "Clinical trial eligibility"
            ]
        }
    },
    
    "rs63750066": {
        "gene": "PSEN1",
        "name": "Presenilin-1 AD",
        "risk_allele": "T",
        "condition": "Early-onset familial Alzheimer's disease",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000012557"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Genetic counseling before results disclosure",
                "Psychological support recommended"
            ]
        }
    },
    
    "rs80356773": {
        "gene": "HTT",
        "name": "Huntington's disease CAG repeat marker",
        "risk_allele": "expansion",
        "condition": "Huntington's disease",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "note": "Full diagnosis requires CAG repeat length testing",
        "references": ["PMID:8021009"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Predictive testing protocol required",
                "Pre-test counseling mandatory",
                "Family implications significant"
            ]
        }
    },
    
    "rs11568821": {
        "gene": "SNCA",
        "name": "Alpha-synuclein Parkinson's",
        "risk_allele": "A",
        "condition": "Familial Parkinson's disease",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["PMID:9197268"],
        "actionable": {
            "priority": "high",
            "action_type": "monitoring",
            "recommendations": ["Neurological monitoring", "Research study eligibility"]
        }
    },
    
    "rs33939927": {
        "gene": "LRRK2",
        "name": "LRRK2 G2019S",
        "variant": "G2019S",
        "risk_allele": "A",
        "condition": "Parkinson's disease",
        "inheritance": "autosomal_dominant",
        "population_frequency": "Higher in Ashkenazi Jewish and North African Berber",
        "evidence": "strong",
        "references": ["PMID:15541309", "ClinVar:VCV000031156"],
        "actionable": {
            "priority": "high",
            "action_type": "monitoring",
            "recommendations": [
                "~30% lifetime Parkinson's risk if heterozygous",
                "Neurological baseline evaluation",
                "Clinical trial eligibility (neuroprotection)"
            ]
        }
    },
    
    "rs104893877": {
        "gene": "SOD1",
        "name": "ALS SOD1",
        "risk_allele": "T",
        "condition": "Familial ALS (Amyotrophic Lateral Sclerosis)",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["PMID:8446170"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Genetic counseling essential",
                "Family testing considerations",
                "Emerging antisense therapies available"
            ]
        }
    },
    
    # =========================================================================
    # METABOLIC DISORDERS
    # =========================================================================
    
    "rs62516101": {
        "gene": "PAH",
        "name": "Phenylketonuria carrier",
        "risk_allele": "A",
        "condition": "Phenylketonuria (PKU)",
        "inheritance": "autosomal_recessive",
        "population_frequency": "1:50 carrier frequency",
        "evidence": "strong",
        "references": ["ClinVar:VCV000000823"],
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": [
                "Partner testing if carrier",
                "Treatable with dietary management"
            ]
        }
    },
    
    "rs121908002": {
        "gene": "GALT",
        "name": "Galactosemia Q188R",
        "variant": "Q188R",
        "risk_allele": "A",
        "condition": "Classic galactosemia",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000000785"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["Newborn screening standard", "Lactose-free diet if affected"]
        }
    },
    
    "rs104894395": {
        "gene": "CBS",
        "name": "Homocystinuria marker",
        "risk_allele": "A",
        "condition": "Homocystinuria",
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000000821"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["B6 responsive in some cases", "Methionine restriction"]
        }
    },
    
    "rs113993959": {
        "gene": "BLM",
        "name": "Bloom syndrome carrier",
        "risk_allele": "C",
        "condition": "Bloom syndrome",
        "inheritance": "autosomal_recessive",
        "population_frequency": "1:100 Ashkenazi Jewish",
        "evidence": "strong",
        "references": ["ClinVar:VCV000000786"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": ["Cancer surveillance if affected", "Partner testing if carrier"]
        }
    },
    
    # =========================================================================
    # HEMATOLOGIC DISORDERS
    # =========================================================================
    
    "rs1800056": {
        "gene": "F9",
        "name": "Hemophilia B marker",
        "risk_allele": "T",
        "condition": "Hemophilia B",
        "inheritance": "X-linked_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000010695"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Factor IX testing if suspected",
                "Female carriers may have bleeding tendency"
            ]
        }
    },
    
    "rs137852591": {
        "gene": "F8",
        "name": "Hemophilia A marker",
        "risk_allele": "deletion",
        "condition": "Hemophilia A",
        "inheritance": "X-linked_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000010571"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Factor VIII testing",
                "Carrier testing for females"
            ]
        }
    },
    
    "rs1801020": {
        "gene": "F12",
        "name": "Factor XII deficiency",
        "risk_allele": "T",
        "condition": "Factor XII deficiency",
        "inheritance": "autosomal_recessive",
        "evidence": "moderate",
        "references": ["PMID:16507180"],
        "note": "Usually asymptomatic but may affect aPTT",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May cause prolonged aPTT without bleeding risk"]
        }
    },
    
    # =========================================================================
    # CARDIAC RARE DISEASES
    # =========================================================================
    
    "rs104894504": {
        "gene": "MYH7",
        "name": "Hypertrophic cardiomyopathy",
        "risk_allele": "A",
        "condition": "Hypertrophic cardiomyopathy (HCM)",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000014066"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "Cardiac evaluation (echo, ECG)",
                "Family screening recommended",
                "Activity restrictions may apply",
                "Sudden cardiac death risk assessment"
            ]
        }
    },
    
    "rs104893768": {
        "gene": "MYBPC3",
        "name": "HCM MYBPC3",
        "risk_allele": "T",
        "condition": "Hypertrophic cardiomyopathy",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000014074"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": ["Cardiac evaluation", "Family cascade screening"]
        }
    },
    
    "rs12143842": {
        "gene": "NOS1AP",
        "name": "Long QT syndrome modifier",
        "risk_allele": "T",
        "condition": "Long QT syndrome susceptibility",
        "inheritance": "modifier",
        "evidence": "moderate",
        "references": ["PMID:16648850"],
        "actionable": {
            "priority": "medium",
            "action_type": "monitoring",
            "recommendations": [
                "ECG monitoring if on QT-prolonging drugs",
                "Avoid drug combinations that prolong QT"
            ]
        }
    },
    
    "rs72552713": {
        "gene": "SCN5A",
        "name": "Brugada syndrome marker",
        "risk_allele": "A",
        "condition": "Brugada syndrome",
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000000777"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "ECG evaluation for Brugada pattern",
                "Avoid triggering medications (Class I antiarrhythmics, cocaine)",
                "ICD consideration if symptomatic"
            ]
        }
    },
    
    # =========================================================================
    # RESPIRATORY RARE DISEASES  
    # =========================================================================
    
    "rs28929474": {
        "gene": "SERPINA1",
        "name": "Alpha-1 antitrypsin Z allele",
        "variant": "Z allele (Glu342Lys)",
        "risk_allele": "T",
        "condition": "Alpha-1 antitrypsin deficiency",
        "inheritance": "autosomal_codominant",
        "population_frequency": "1:25 carrier in Northern Europeans",
        "evidence": "strong",
        "references": ["PMID:1730332", "ClinVar:VCV000007777"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Pulmonary function testing",
                "Liver function monitoring",
                "CRITICAL: Avoid smoking (accelerates lung damage)",
                "AAT level testing recommended",
                "Augmentation therapy available for severe deficiency"
            ]
        }
    },
    
    "rs17580": {
        "gene": "SERPINA1",
        "name": "Alpha-1 antitrypsin S allele",
        "variant": "S allele",
        "risk_allele": "T",
        "condition": "Alpha-1 antitrypsin deficiency (mild)",
        "inheritance": "autosomal_codominant",
        "evidence": "strong",
        "references": ["ClinVar:VCV000007780"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "SZ compound heterozygotes at higher risk",
                "Smoking cessation critical"
            ]
        }
    },
    
    # =========================================================================
    # IMMUNODEFICIENCY
    # =========================================================================
    
    "rs104895097": {
        "gene": "BTK",
        "name": "X-linked agammaglobulinemia",
        "risk_allele": "T",
        "condition": "X-linked agammaglobulinemia (Bruton's)",
        "inheritance": "X-linked_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000018436"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Immunoglobulin levels if affected",
                "IVIG replacement therapy",
                "Female carriers identified for family planning"
            ]
        }
    },
    
    "rs5030868": {
        "gene": "CYBB",
        "name": "Chronic granulomatous disease",
        "risk_allele": "T",
        "condition": "Chronic granulomatous disease",
        "inheritance": "X-linked_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000013247"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Infection prophylaxis",
                "Avoid live vaccines",
                "HSCT consideration for severe cases"
            ]
        }
    },
}

# Panel definitions for expanded carrier screening
RARE_DISEASE_PANELS = {
    "ashkenazi_jewish": [
        "rs76763715",  # Gaucher
        "rs28940871",  # Tay-Sachs
        "rs80338939",  # Niemann-Pick
        "rs113993959", # Bloom
        "rs33939927",  # LRRK2 Parkinson's
    ],
    "mediterranean": [
        "rs1800562",   # Hemochromatosis
        "rs61752717",  # Familial Mediterranean Fever
    ],
    "pan_ethnic": [
        "rs75527207",  # CF
        "rs62516101",  # PKU
        "rs28929474",  # Alpha-1 antitrypsin
        "rs121908002", # Galactosemia
    ]
}
