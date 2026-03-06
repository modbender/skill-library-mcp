"""
Comprehensive health marker database.
Markers verified to be present on AncestryDNA v2 chip.
Each marker includes citations and evidence levels.
"""

HEALTH_MARKERS = {
    # =========================================================================
    # CARDIOVASCULAR
    # =========================================================================
    
    "rs7412": {
        "gene": "APOE",
        "name": "APOE epsilon status",
        "risk_allele": "C",
        "category": "cardiovascular",
        "conditions": ["Alzheimer's disease", "Cardiovascular disease", "Lipid metabolism"],
        "evidence": "strong",
        "references": ["PMID:8346443", "PMID:19734902"],
        "notes": "Combined with rs429358 determines APOE epsilon status",
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Lipid panel monitoring",
                "Consider cognitive screening if family history",
                "Mediterranean diet may be protective"
            ]
        }
    },
    
    "rs1333049": {
        "gene": "9p21.3",
        "name": "CAD risk locus",
        "risk_allele": "C",
        "category": "cardiovascular",
        "conditions": ["Coronary artery disease", "Myocardial infarction"],
        "evidence": "strong",
        "references": ["PMID:17478679", "PMID:17554300"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Cardiovascular risk factor management",
                "Regular exercise",
                "Consider early lipid screening"
            ]
        }
    },
    
    "rs10757274": {
        "gene": "9p21.3",
        "name": "CAD risk locus 2",
        "risk_allele": "G",
        "category": "cardiovascular",
        "conditions": ["Coronary artery disease"],
        "evidence": "strong",
        "references": ["PMID:17478679"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": ["Cardiovascular screening", "Lifestyle modification"]
        }
    },
    
    "rs6025": {
        "gene": "F5",
        "name": "Factor V Leiden",
        "risk_allele": "A",
        "category": "clotting",
        "conditions": ["Deep vein thrombosis", "Pulmonary embolism", "Venous thromboembolism"],
        "evidence": "strong",
        "references": ["PMID:7989260", "ClinVar:VCV000017567"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Inform all healthcare providers",
                "Discuss thromboprophylaxis before surgery",
                "Avoid prolonged immobility",
                "Consider compression stockings for long flights"
            ]
        }
    },
    
    "rs1799963": {
        "gene": "F2",
        "name": "Prothrombin G20210A",
        "risk_allele": "A",
        "category": "clotting",
        "conditions": ["Venous thromboembolism", "Pregnancy complications"],
        "evidence": "strong",
        "references": ["PMID:8872854", "ClinVar:VCV000017564"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Inform healthcare providers",
                "Thrombosis risk assessment before estrogen therapy",
                "VTE prevention counseling"
            ]
        }
    },
    
    # =========================================================================
    # METHYLATION / DETOXIFICATION
    # =========================================================================
    
    "rs1801133": {
        "gene": "MTHFR",
        "name": "C677T",
        "risk_allele": "A",
        "category": "methylation",
        "conditions": ["Elevated homocysteine", "Neural tube defects", "Cardiovascular risk"],
        "evidence": "strong",
        "references": ["PMID:8630491", "PMID:26647857"],
        "actionable": {
            "priority": "medium",
            "action_type": "supplementation",
            "recommendations": [
                "Consider methylfolate over folic acid",
                "Methylcobalamin (B12) may be beneficial",
                "Consider homocysteine testing"
            ]
        }
    },
    
    "rs1801131": {
        "gene": "MTHFR",
        "name": "A1298C",
        "risk_allele": "G",
        "category": "methylation",
        "conditions": ["BH4 metabolism", "Neurotransmitter synthesis"],
        "evidence": "moderate",
        "references": ["PMID:10444342"],
        "actionable": {
            "priority": "low",
            "action_type": "supplementation",
            "recommendations": ["Consider methylfolate if compound heterozygous with C677T"]
        }
    },
    
    "rs1805087": {
        "gene": "MTR",
        "name": "A2756G",
        "risk_allele": "G",
        "category": "methylation",
        "conditions": ["B12 metabolism", "Homocysteine"],
        "evidence": "moderate",
        "references": ["PMID:21114891"],
        "actionable": {
            "priority": "low",
            "action_type": "supplementation",
            "recommendations": ["Ensure adequate B12 intake", "Consider methylcobalamin"]
        }
    },
    
    "rs1801394": {
        "gene": "MTRR",
        "name": "A66G",
        "risk_allele": "G",
        "category": "methylation",
        "conditions": ["B12 regeneration", "Homocysteine"],
        "evidence": "moderate",
        "references": ["PMID:12518998"],
        "actionable": {
            "priority": "low",
            "action_type": "supplementation",
            "recommendations": ["B12 optimization"]
        }
    },
    
    "rs4680": {
        "gene": "COMT",
        "name": "Val158Met",
        "risk_allele": "A",
        "category": "neurotransmitter",
        "conditions": ["Dopamine metabolism", "Stress response", "Pain sensitivity"],
        "evidence": "strong",
        "references": ["PMID:12716966", "PMID:17008817"],
        "notes": "GG = Warrior (stress resilient), AA = Worrier (higher dopamine, detail-oriented)",
        "actionable": {
            "priority": "informational",
            "action_type": "lifestyle",
            "recommendations": [
                "AA genotype: may benefit from stress management techniques",
                "GG genotype: may need more stimulation to feel engaged"
            ]
        }
    },
    
    "rs4633": {
        "gene": "COMT",
        "name": "C/T polymorphism",
        "risk_allele": "T",
        "category": "neurotransmitter",
        "conditions": ["Linked to Val158Met", "Catecholamine metabolism"],
        "evidence": "moderate",
        "references": ["PMID:12716966"],
        "actionable": {
            "priority": "informational",
            "action_type": "none",
            "recommendations": []
        }
    },
    
    # =========================================================================
    # PHARMACOGENOMICS
    # =========================================================================
    
    "rs4244285": {
        "gene": "CYP2C19",
        "name": "*2 allele",
        "risk_allele": "A",
        "category": "pharmacogenomics",
        "conditions": ["Clopidogrel metabolism", "PPI metabolism"],
        "evidence": "strong",
        "references": ["PMID:21716271", "CPIC guideline"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Inform prescriber before starting clopidogrel (Plavix)",
                "Alternative antiplatelet therapy may be indicated",
                "Affects PPI and some antidepressant metabolism"
            ]
        }
    },
    
    "rs1799853": {
        "gene": "CYP2C9",
        "name": "*2 allele",
        "risk_allele": "T",
        "category": "pharmacogenomics",
        "conditions": ["Warfarin metabolism", "NSAID metabolism"],
        "evidence": "strong",
        "references": ["PMID:21900891", "CPIC guideline"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Lower warfarin dose typically needed",
                "Increased bleeding risk with NSAIDs",
                "Share with prescribers"
            ]
        }
    },
    
    "rs1057910": {
        "gene": "CYP2C9",
        "name": "*3 allele",
        "risk_allele": "C",
        "category": "pharmacogenomics",
        "conditions": ["Warfarin sensitivity", "Reduced drug metabolism"],
        "evidence": "strong",
        "references": ["PMID:21900891", "CPIC guideline"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Significant warfarin dose reduction needed",
                "More potent effect than *2 allele",
                "Critical to share with anticoagulation clinic"
            ]
        }
    },
    
    "rs9923231": {
        "gene": "VKORC1",
        "name": "-1639G>A",
        "risk_allele": "T",
        "category": "pharmacogenomics",
        "conditions": ["Warfarin sensitivity"],
        "evidence": "strong",
        "references": ["PMID:15930419", "CPIC guideline"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "TT genotype: approximately 50% lower warfarin dose needed",
                "Critical for warfarin dosing algorithms",
                "Share with anticoagulation providers"
            ]
        }
    },
    
    "rs4149056": {
        "gene": "SLCO1B1",
        "name": "*5 allele",
        "risk_allele": "C",
        "category": "pharmacogenomics",
        "conditions": ["Statin-induced myopathy"],
        "evidence": "strong",
        "references": ["PMID:18650507", "CPIC guideline"],
        "actionable": {
            "priority": "medium",
            "action_type": "medical_alert",
            "recommendations": [
                "Increased risk of muscle problems with simvastatin",
                "Consider lower statin doses or alternatives",
                "Monitor for muscle pain on statins"
            ]
        }
    },
    
    "rs762551": {
        "gene": "CYP1A2",
        "name": "*1F allele",
        "risk_allele": "C",
        "category": "pharmacogenomics",
        "conditions": ["Caffeine metabolism", "Drug metabolism"],
        "evidence": "moderate",
        "references": ["PMID:17132150", "PMID:16522833"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "CC genotype: slow caffeine metabolizer",
                "May want to limit afternoon caffeine",
                "Higher cardiovascular risk with high caffeine intake (CC genotype)"
            ]
        }
    },
    
    # =========================================================================
    # DIABETES / OBESITY
    # =========================================================================
    
    "rs7903146": {
        "gene": "TCF7L2",
        "name": "Strongest T2D variant",
        "risk_allele": "T",
        "category": "metabolic",
        "conditions": ["Type 2 diabetes"],
        "evidence": "strong",
        "references": ["PMID:16415884", "PMID:17463248"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Maintain healthy weight",
                "Regular blood glucose monitoring",
                "Low glycemic diet may be beneficial",
                "Regular physical activity"
            ]
        }
    },
    
    "rs12255372": {
        "gene": "TCF7L2",
        "name": "T2D risk variant",
        "risk_allele": "T",
        "category": "metabolic",
        "conditions": ["Type 2 diabetes"],
        "evidence": "strong",
        "references": ["PMID:16415884"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": ["Diabetes prevention lifestyle measures"]
        }
    },
    
    "rs9939609": {
        "gene": "FTO",
        "name": "Obesity risk variant",
        "risk_allele": "A",
        "category": "metabolic",
        "conditions": ["Obesity", "BMI"],
        "evidence": "strong",
        "references": ["PMID:17434869", "PMID:17554300"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Physical activity especially important",
                "Protein-rich diet may help with satiety",
                "Weight management focus"
            ]
        }
    },
    
    "rs17782313": {
        "gene": "MC4R",
        "name": "Appetite regulation",
        "risk_allele": "C",
        "category": "metabolic",
        "conditions": ["Obesity", "Appetite"],
        "evidence": "strong",
        "references": ["PMID:18454148"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": ["Mindful eating", "Structured meal timing"]
        }
    },
    
    "rs1801282": {
        "gene": "PPARG",
        "name": "Pro12Ala",
        "risk_allele": "C",
        "category": "metabolic",
        "conditions": ["Insulin sensitivity", "Type 2 diabetes"],
        "evidence": "strong",
        "references": ["PMID:9614613", "PMID:11574435"],
        "notes": "G allele (Ala) is protective against T2D",
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": ["Weight management", "Exercise improves insulin sensitivity"]
        }
    },
    
    # =========================================================================
    # IRON METABOLISM
    # =========================================================================
    
    "rs1800562": {
        "gene": "HFE",
        "name": "C282Y",
        "risk_allele": "A",
        "category": "iron",
        "conditions": ["Hereditary hemochromatosis", "Iron overload"],
        "evidence": "strong",
        "references": ["PMID:8696333", "ClinVar:VCV000003828"],
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Monitor ferritin and transferrin saturation",
                "AVOID iron supplements",
                "Limit vitamin C with meals (increases iron absorption)",
                "Consider therapeutic phlebotomy if iron elevated",
                "Homozygotes at high risk for iron overload"
            ]
        }
    },
    
    "rs1799945": {
        "gene": "HFE",
        "name": "H63D",
        "risk_allele": "G",
        "category": "iron",
        "conditions": ["Mild iron overload risk"],
        "evidence": "moderate",
        "references": ["PMID:8696333"],
        "actionable": {
            "priority": "low",
            "action_type": "monitoring",
            "recommendations": ["Periodic iron studies if compound heterozygous with C282Y"]
        }
    },
    
    # =========================================================================
    # EYE HEALTH
    # =========================================================================
    
    "rs1061170": {
        "gene": "CFH",
        "name": "Y402H",
        "risk_allele": "C",
        "category": "eye",
        "conditions": ["Age-related macular degeneration"],
        "evidence": "strong",
        "references": ["PMID:15761121", "PMID:15870199"],
        "actionable": {
            "priority": "medium",
            "action_type": "supplementation",
            "recommendations": [
                "Regular dilated eye exams after age 50",
                "AREDS2 formula supplements if indicated",
                "Lutein and zeaxanthin supplementation",
                "Don't smoke (major modifiable risk factor)",
                "UV protection outdoors"
            ]
        }
    },
    
    "rs10490924": {
        "gene": "ARMS2/HTRA1",
        "name": "AMD risk locus",
        "risk_allele": "T",
        "category": "eye",
        "conditions": ["Age-related macular degeneration"],
        "evidence": "strong",
        "references": ["PMID:16174643", "PMID:16936732"],
        "actionable": {
            "priority": "medium",
            "action_type": "supplementation",
            "recommendations": [
                "Regular eye exams",
                "AREDS2 formula if at risk",
                "Green leafy vegetables (lutein source)"
            ]
        }
    },
    
    # =========================================================================
    # AUTOIMMUNE / CELIAC
    # =========================================================================
    
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "name": "Celiac risk",
        "risk_allele": "T",
        "category": "autoimmune",
        "conditions": ["Celiac disease"],
        "evidence": "strong",
        "references": ["PMID:18509540", "PMID:20190752"],
        "notes": "HLA-DQ2.5 present in ~95% of celiac patients",
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": [
                "tTG-IgA test if GI symptoms present",
                "Do not start gluten-free diet before testing",
                "Genetic counseling for family members"
            ]
        }
    },
    
    "rs2476601": {
        "gene": "PTPN22",
        "name": "R620W",
        "risk_allele": "A",
        "category": "autoimmune",
        "conditions": ["Type 1 diabetes", "Rheumatoid arthritis", "Lupus", "Thyroid autoimmunity"],
        "evidence": "strong",
        "references": ["PMID:15208781", "PMID:16175503"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Awareness of autoimmune susceptibility"]
        }
    },
    
    "rs3087243": {
        "gene": "CTLA4",
        "name": "+49A/G",
        "risk_allele": "G",
        "category": "autoimmune",
        "conditions": ["Type 1 diabetes", "Graves disease", "Autoimmune thyroiditis"],
        "evidence": "strong",
        "references": ["PMID:12724780", "PMID:11140838"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Thyroid function monitoring if symptoms"]
        }
    },
    
    # =========================================================================
    # OXIDATIVE STRESS / LONGEVITY
    # =========================================================================
    
    "rs4880": {
        "gene": "SOD2",
        "name": "Ala16Val",
        "risk_allele": "A",
        "category": "oxidative_stress",
        "conditions": ["Oxidative stress", "Aging"],
        "evidence": "moderate",
        "references": ["PMID:12618587", "PMID:15534163"],
        "actionable": {
            "priority": "low",
            "action_type": "supplementation",
            "recommendations": [
                "AA genotype: may benefit from antioxidant support",
                "Consider NAC, CoQ10, or alpha-lipoic acid",
                "Avoid excessive iron (increases oxidative stress)"
            ]
        }
    },
    
    # =========================================================================
    # VITAMIN D
    # =========================================================================
    
    "rs2282679": {
        "gene": "GC",
        "name": "Vitamin D binding protein",
        "risk_allele": "G",
        "category": "vitamin_d",
        "conditions": ["Vitamin D levels", "D binding protein"],
        "evidence": "strong",
        "references": ["PMID:20541252", "PMID:20418485"],
        "actionable": {
            "priority": "medium",
            "action_type": "supplementation",
            "recommendations": [
                "Test 25(OH)D levels",
                "May need higher vitamin D supplementation",
                "Take D3 with vitamin K2",
                "Take with fat for absorption"
            ]
        }
    },
    
    "rs12785878": {
        "gene": "DHCR7/NADSYN1",
        "name": "Vitamin D synthesis",
        "risk_allele": "T",
        "category": "vitamin_d",
        "conditions": ["Vitamin D synthesis"],
        "evidence": "strong",
        "references": ["PMID:20541252"],
        "actionable": {
            "priority": "low",
            "action_type": "supplementation",
            "recommendations": ["May have reduced vitamin D synthesis from sunlight"]
        }
    },
    
    # =========================================================================
    # NEUROLOGICAL / PSYCHIATRIC
    # =========================================================================
    
    "rs6265": {
        "gene": "BDNF",
        "name": "Val66Met",
        "risk_allele": "T",
        "category": "neurological",
        "conditions": ["Memory", "Depression", "Anxiety", "Neuroplasticity"],
        "evidence": "moderate",
        "references": ["PMID:12802784", "PMID:15341763"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "Exercise increases BDNF (especially important for Met carriers)",
                "Cognitive training may be beneficial"
            ]
        }
    },
    
    "rs1800497": {
        "gene": "ANKK1/DRD2",
        "name": "Taq1A",
        "risk_allele": "A",
        "category": "neurological",
        "conditions": ["Dopamine receptor density", "Addiction susceptibility"],
        "evidence": "moderate",
        "references": ["PMID:8807664", "PMID:2906084"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Awareness of addiction susceptibility", "Avoid addictive substances"]
        }
    },
    
    "rs53576": {
        "gene": "OXTR",
        "name": "Oxytocin receptor",
        "risk_allele": "A",
        "category": "neurological",
        "conditions": ["Empathy", "Social behavior", "Stress response"],
        "evidence": "moderate",
        "references": ["PMID:19015103", "PMID:21595907"],
        "notes": "GG associated with greater empathy and social sensitivity",
        "actionable": {
            "priority": "informational",
            "action_type": "none",
            "recommendations": []
        }
    },
    
    # =========================================================================
    # CANCER (Common low-penetrance variants)
    # =========================================================================
    
    "rs2981582": {
        "gene": "FGFR2",
        "name": "Breast cancer risk",
        "risk_allele": "A",
        "category": "cancer",
        "conditions": ["Breast cancer susceptibility"],
        "evidence": "strong",
        "references": ["PMID:17529967"],
        "notes": "Common variant, modest effect size",
        "actionable": {
            "priority": "low",
            "action_type": "screening",
            "recommendations": ["Follow standard screening guidelines"]
        }
    },
    
    "rs6983267": {
        "gene": "8q24",
        "name": "Colorectal cancer risk",
        "risk_allele": "G",
        "category": "cancer",
        "conditions": ["Colorectal cancer", "Prostate cancer"],
        "evidence": "strong",
        "references": ["PMID:17618284", "PMID:17603485"],
        "actionable": {
            "priority": "low",
            "action_type": "screening",
            "recommendations": ["Follow standard colorectal cancer screening guidelines"]
        }
    },
    
    "rs1447295": {
        "gene": "8q24",
        "name": "Prostate cancer risk",
        "risk_allele": "A",
        "category": "cancer",
        "conditions": ["Prostate cancer"],
        "evidence": "strong",
        "references": ["PMID:17401366"],
        "actionable": {
            "priority": "low",
            "action_type": "screening",
            "recommendations": ["Discuss PSA screening with physician"]
        }
    },
}

# Count markers by category
def get_marker_stats():
    categories = {}
    for rsid, info in HEALTH_MARKERS.items():
        cat = info.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    return categories
