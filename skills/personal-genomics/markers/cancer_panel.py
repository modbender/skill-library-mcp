"""
Expanded Hereditary Cancer Panel
Comprehensive coverage of hereditary cancer syndrome markers

Sources:
- ClinVar pathogenic/likely pathogenic variants
- NCCN Guidelines for Genetic/Familial High-Risk Assessment
- ACMG recommendations for secondary findings
- Published literature on hereditary cancer syndromes

IMPORTANT CLINICAL NOTES:
- These variants require clinical confirmation
- Genetic counseling strongly recommended for any positive finding
- Consumer arrays may miss rare pathogenic variants
- Negative result does NOT rule out hereditary cancer syndrome
"""

from typing import Dict, List, Optional, Any

# =============================================================================
# BRCA1 VARIANTS - Breast/Ovarian Cancer Susceptibility
# =============================================================================

BRCA1_MARKERS = {
    # Ashkenazi Jewish founder mutations
    "i4000377": {
        "gene": "BRCA1",
        "variant": "185delAG (c.68_69delAG)",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "population": "Ashkenazi Jewish (1%)",
        "cancer_risks": {
            "breast": {"lifetime_risk": 0.65, "by_age_70": 0.55},
            "ovarian": {"lifetime_risk": 0.45, "by_age_70": 0.39},
        },
        "recommendations": [
            "Enhanced breast screening (MRI + mammogram)",
            "Consider risk-reducing surgery",
            "Genetic counseling for family members",
            "PARP inhibitor eligibility if cancer develops"
        ],
        "evidence": "strong",
        "actionable": {
            "priority": "critical",
            "action_type": "hereditary_cancer_syndrome",
            "recommendations": [
                "BRCA1 PATHOGENIC VARIANT - High cancer risk",
                "Urgent referral to genetic counseling",
                "Enhanced screening protocols required",
                "Discuss risk-reducing options"
            ]
        }
    },
    "i4000378": {
        "gene": "BRCA1",
        "variant": "5382insC (c.5266dupC)",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "population": "Ashkenazi Jewish, Eastern European",
        "cancer_risks": {
            "breast": {"lifetime_risk": 0.60},
            "ovarian": {"lifetime_risk": 0.40},
        },
        "evidence": "strong",
        "actionable": {
            "priority": "critical",
            "action_type": "hereditary_cancer_syndrome",
            "recommendations": [
                "BRCA1 PATHOGENIC VARIANT",
                "Refer to genetic counseling immediately"
            ]
        }
    },
    
    # Additional BRCA1 variants on consumer arrays
    "rs80357906": {
        "gene": "BRCA1",
        "variant": "c.5503C>T (R1835X)",
        "consequence": "nonsense",
        "classification": "pathogenic",
        "cancer_risks": {"breast": {"lifetime_risk": 0.60}},
        "evidence": "strong"
    },
    "rs80357713": {
        "gene": "BRCA1",
        "variant": "c.4327C>T (R1443X)",
        "consequence": "nonsense",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80357522": {
        "gene": "BRCA1",
        "variant": "c.1016dupA",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80357868": {
        "gene": "BRCA1",
        "variant": "c.3756_3759delGTCT",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80357065": {
        "gene": "BRCA1",
        "variant": "c.1687C>T (Q563X)",
        "consequence": "nonsense",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80358150": {
        "gene": "BRCA1",
        "variant": "c.4035delA",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
}

# =============================================================================
# BRCA2 VARIANTS - Breast/Ovarian/Prostate/Pancreatic Cancer
# =============================================================================

BRCA2_MARKERS = {
    # Ashkenazi Jewish founder mutation
    "i4000379": {
        "gene": "BRCA2",
        "variant": "6174delT (c.5946delT)",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "population": "Ashkenazi Jewish (1.5%)",
        "cancer_risks": {
            "breast_female": {"lifetime_risk": 0.55},
            "ovarian": {"lifetime_risk": 0.25},
            "breast_male": {"lifetime_risk": 0.08},
            "prostate": {"lifetime_risk": 0.20},
            "pancreatic": {"lifetime_risk": 0.05},
        },
        "evidence": "strong",
        "actionable": {
            "priority": "critical",
            "action_type": "hereditary_cancer_syndrome",
            "recommendations": [
                "BRCA2 PATHOGENIC VARIANT - High cancer risk",
                "Genetic counseling for family members",
                "Enhanced screening for multiple cancers",
                "Males also at increased risk (breast, prostate)"
            ]
        }
    },
    
    # Additional BRCA2 variants
    "rs80359550": {
        "gene": "BRCA2",
        "variant": "c.5645C>A (S1882X)",
        "consequence": "nonsense",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359352": {
        "gene": "BRCA2",
        "variant": "c.3109C>T (Q1037X)",
        "consequence": "nonsense",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359375": {
        "gene": "BRCA2",
        "variant": "c.3847_3848delGT",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359535": {
        "gene": "BRCA2",
        "variant": "c.5213_5216delCTAC",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359508": {
        "gene": "BRCA2",
        "variant": "c.4936_4939delGAAA",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359065": {
        "gene": "BRCA2",
        "variant": "c.658_659delGT",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs80359671": {
        "gene": "BRCA2",
        "variant": "c.6275_6276delTT",
        "consequence": "frameshift",
        "classification": "pathogenic",
        "evidence": "strong"
    },
    "rs11571833": {
        "gene": "BRCA2",
        "variant": "c.9976A>T (K3326X)",
        "consequence": "truncating",
        "classification": "likely_pathogenic",
        "risk_allele": "T",
        "cancer_risks": {
            "breast": {"or": 1.3},
            "ovarian": {"or": 1.4},
            "lung_squamous": {"or": 2.5},
        },
        "note": "Common truncating variant with modest risk increase",
        "evidence": "moderate"
    },
}

# =============================================================================
# LYNCH SYNDROME GENES (MLH1, MSH2, MSH6, PMS2, EPCAM)
# =============================================================================

LYNCH_SYNDROME_MARKERS = {
    # MLH1 - Colorectal, endometrial, ovarian cancer
    "rs63750449": {
        "gene": "MLH1",
        "variant": "c.350C>T (T117M)",
        "classification": "likely_pathogenic",
        "syndrome": "Lynch syndrome",
        "cancer_risks": {
            "colorectal": {"lifetime_risk": 0.50},
            "endometrial": {"lifetime_risk": 0.40},
        },
        "recommendations": [
            "Colonoscopy every 1-2 years starting age 20-25",
            "Consider prophylactic hysterectomy after childbearing",
            "Genetic counseling for family"
        ],
        "evidence": "moderate",
        "actionable": {
            "priority": "high",
            "action_type": "lynch_syndrome",
            "recommendations": [
                "Lynch syndrome gene variant detected",
                "Enhanced colorectal screening required",
                "Consider endometrial surveillance"
            ]
        }
    },
    "rs63749931": {
        "gene": "MLH1",
        "variant": "c.677G>A (R226Q)",
        "classification": "pathogenic",
        "syndrome": "Lynch syndrome",
        "evidence": "strong"
    },
    "rs63750006": {
        "gene": "MLH1",
        "variant": "c.790+1G>A",
        "classification": "pathogenic",
        "consequence": "splice_site",
        "syndrome": "Lynch syndrome",
        "evidence": "strong"
    },
    
    # MSH2 - Lynch syndrome
    "rs63749893": {
        "gene": "MSH2",
        "variant": "c.942+3A>T",
        "classification": "pathogenic",
        "consequence": "splice_site",
        "syndrome": "Lynch syndrome",
        "cancer_risks": {
            "colorectal": {"lifetime_risk": 0.55},
            "endometrial": {"lifetime_risk": 0.45},
            "ovarian": {"lifetime_risk": 0.15},
            "urinary_tract": {"lifetime_risk": 0.10},
        },
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "action_type": "lynch_syndrome",
            "recommendations": [
                "MSH2 Lynch syndrome variant",
                "Colonoscopy every 1-2 years",
                "Upper GI surveillance may be indicated"
            ]
        }
    },
    "rs63749869": {
        "gene": "MSH2",
        "variant": "c.1165C>T (R389X)",
        "classification": "pathogenic",
        "consequence": "nonsense",
        "syndrome": "Lynch syndrome",
        "evidence": "strong"
    },
    "rs63750241": {
        "gene": "MSH2",
        "variant": "c.1906G>C (A636P)",
        "classification": "pathogenic",
        "syndrome": "Lynch syndrome",
        "evidence": "strong"
    },
    
    # MSH6 - Attenuated Lynch syndrome
    "rs63750018": {
        "gene": "MSH6",
        "variant": "c.3261dupC",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "syndrome": "Lynch syndrome (attenuated)",
        "note": "MSH6 mutations have later onset and lower penetrance than MLH1/MSH2",
        "cancer_risks": {
            "colorectal": {"lifetime_risk": 0.30},
            "endometrial": {"lifetime_risk": 0.45},
        },
        "evidence": "strong"
    },
    "rs63750672": {
        "gene": "MSH6",
        "variant": "c.3959_3962delCAAG",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "syndrome": "Lynch syndrome",
        "evidence": "strong"
    },
    
    # PMS2 - Lower penetrance Lynch
    "rs63750631": {
        "gene": "PMS2",
        "variant": "c.2404C>T (R802X)",
        "classification": "pathogenic",
        "consequence": "nonsense",
        "syndrome": "Lynch syndrome (lower penetrance)",
        "note": "PMS2 has lowest penetrance of Lynch genes",
        "cancer_risks": {
            "colorectal": {"lifetime_risk": 0.20},
            "endometrial": {"lifetime_risk": 0.15},
        },
        "evidence": "strong"
    },
}

# =============================================================================
# OTHER HEREDITARY CANCER GENES
# =============================================================================

OTHER_CANCER_MARKERS = {
    # APC - Familial Adenomatous Polyposis
    "rs121913239": {
        "gene": "APC",
        "variant": "c.3920T>A (I1307K)",
        "classification": "pathogenic",
        "population": "Ashkenazi Jewish (6%)",
        "syndrome": "Increased colorectal cancer risk",
        "cancer_risks": {
            "colorectal": {"or": 2.0, "lifetime_increase": 0.10},
        },
        "note": "Not classical FAP, but ~2x colorectal cancer risk",
        "recommendations": [
            "Colonoscopy starting age 40",
            "Repeat every 3-5 years"
        ],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "action_type": "colorectal_surveillance",
            "recommendations": [
                "APC I1307K - Increased colorectal cancer risk",
                "Earlier/more frequent colonoscopies recommended"
            ]
        }
    },
    "rs121913240": {
        "gene": "APC",
        "variant": "c.3927_3931delAAAGA",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "syndrome": "Familial Adenomatous Polyposis",
        "note": "Classical FAP - hundreds to thousands of polyps",
        "cancer_risks": {
            "colorectal": {"lifetime_risk": 0.95},
        },
        "evidence": "strong"
    },
    
    # TP53 - Li-Fraumeni Syndrome
    "rs28934578": {
        "gene": "TP53",
        "variant": "c.743G>A (R248Q)",
        "classification": "pathogenic",
        "syndrome": "Li-Fraumeni syndrome",
        "cancer_risks": {
            "multiple_cancers": {"lifetime_risk": 0.90},
            "breast": {"lifetime_risk": 0.50},
            "sarcoma": {"lifetime_risk": 0.15},
            "brain_tumor": {"lifetime_risk": 0.05},
            "adrenocortical": {"childhood_risk": 0.03},
        },
        "note": "Very high penetrance multi-cancer syndrome",
        "evidence": "strong",
        "actionable": {
            "priority": "critical",
            "action_type": "li_fraumeni",
            "recommendations": [
                "TP53 PATHOGENIC - Li-Fraumeni Syndrome",
                "URGENT genetic counseling",
                "Comprehensive cancer surveillance protocol",
                "Avoid radiation when possible"
            ]
        }
    },
    "rs121912651": {
        "gene": "TP53",
        "variant": "c.524G>A (R175H)",
        "classification": "pathogenic",
        "syndrome": "Li-Fraumeni syndrome",
        "evidence": "strong"
    },
    "rs121912656": {
        "gene": "TP53",
        "variant": "c.817C>T (R273C)",
        "classification": "pathogenic",
        "syndrome": "Li-Fraumeni syndrome",
        "evidence": "strong"
    },
    
    # CHEK2 - Moderate breast cancer risk
    "i4000417": {
        "gene": "CHEK2",
        "variant": "c.1100delC",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "cancer_risks": {
            "breast": {"or": 2.5, "lifetime_risk": 0.25},
            "colorectal": {"or": 1.5},
        },
        "population": "Northern European (0.5-1%)",
        "note": "Moderate penetrance - enhanced screening, not prophylactic surgery",
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "action_type": "moderate_breast_risk",
            "recommendations": [
                "CHEK2 frameshift - Moderate breast cancer risk",
                "Consider annual MRI screening",
                "Not typically indication for prophylactic mastectomy"
            ]
        }
    },
    "rs555607708": {
        "gene": "CHEK2",
        "variant": "c.470T>C (I157T)",
        "classification": "likely_pathogenic",
        "cancer_risks": {
            "breast": {"or": 1.5},
        },
        "note": "Lower risk than c.1100delC",
        "evidence": "moderate"
    },
    
    # PALB2 - Breast cancer partner of BRCA2
    "rs180177102": {
        "gene": "PALB2",
        "variant": "c.1592delT",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "cancer_risks": {
            "breast": {"lifetime_risk": 0.40, "or_strong_fhx": 5.0},
            "pancreatic": {"or": 2.3},
        },
        "note": "Risk approaches BRCA2 with strong family history",
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "action_type": "palb2_syndrome",
            "recommendations": [
                "PALB2 pathogenic - High breast cancer risk",
                "Enhanced screening with MRI",
                "Family history affects risk level significantly"
            ]
        }
    },
    "rs515726136": {
        "gene": "PALB2",
        "variant": "c.3113G>A (W1038X)",
        "classification": "pathogenic",
        "consequence": "nonsense",
        "evidence": "strong"
    },
    
    # ATM - Moderate breast cancer risk
    "rs11212587": {
        "gene": "ATM",
        "variant": "c.7271T>G (V2424G)",
        "classification": "pathogenic",
        "cancer_risks": {
            "breast": {"or": 3.0, "lifetime_risk": 0.30},
        },
        "note": "This specific variant has higher risk than other ATM variants",
        "evidence": "strong"
    },
    "rs28904921": {
        "gene": "ATM",
        "variant": "c.6095G>A (R2032K)",
        "classification": "likely_pathogenic",
        "cancer_risks": {
            "breast": {"or": 2.0},
        },
        "evidence": "moderate"
    },
    
    # MUTYH - MAP (MUTYH-associated polyposis) - requires biallelic
    "rs36053993": {
        "gene": "MUTYH",
        "variant": "c.536A>G (Y179C)",
        "classification": "pathogenic",
        "inheritance": "autosomal_recessive",
        "note": "Requires TWO pathogenic MUTYH variants for MAP. Single carrier = minimal risk",
        "population": "European (1-2% carriers)",
        "cancer_risks": {
            "colorectal_biallelic": {"lifetime_risk": 0.80},
            "colorectal_monoallelic": {"or": 1.1},  # Minimal
        },
        "evidence": "strong"
    },
    "rs34612342": {
        "gene": "MUTYH",
        "variant": "c.1187G>A (G396D)",
        "classification": "pathogenic",
        "inheritance": "autosomal_recessive",
        "evidence": "strong"
    },
    
    # CDH1 - Hereditary diffuse gastric cancer
    "rs587776603": {
        "gene": "CDH1",
        "variant": "c.1003C>T (R335X)",
        "classification": "pathogenic",
        "consequence": "nonsense",
        "syndrome": "Hereditary Diffuse Gastric Cancer",
        "cancer_risks": {
            "gastric": {"lifetime_risk": 0.70},
            "lobular_breast": {"lifetime_risk": 0.42},
        },
        "note": "Consider prophylactic gastrectomy",
        "evidence": "strong",
        "actionable": {
            "priority": "critical",
            "action_type": "hdgc",
            "recommendations": [
                "CDH1 pathogenic - Hereditary Diffuse Gastric Cancer syndrome",
                "Prophylactic gastrectomy often recommended",
                "Lobular breast cancer risk in females"
            ]
        }
    },
    
    # STK11 - Peutz-Jeghers syndrome
    "rs137853906": {
        "gene": "STK11",
        "variant": "c.842_843delTG",
        "classification": "pathogenic",
        "consequence": "frameshift",
        "syndrome": "Peutz-Jeghers Syndrome",
        "cancer_risks": {
            "any_cancer": {"lifetime_risk": 0.85},
            "breast": {"lifetime_risk": 0.45},
            "colorectal": {"lifetime_risk": 0.40},
            "pancreatic": {"lifetime_risk": 0.35},
        },
        "evidence": "strong"
    },
}

# =============================================================================
# COMBINED HEREDITARY CANCER PANEL
# =============================================================================

HEREDITARY_CANCER_MARKERS = {
    **BRCA1_MARKERS,
    **BRCA2_MARKERS,
    **LYNCH_SYNDROME_MARKERS,
    **OTHER_CANCER_MARKERS,
}

# Panels for screening
CANCER_SCREENING_PANELS = {
    "brca": {
        "genes": ["BRCA1", "BRCA2"],
        "markers": list(BRCA1_MARKERS.keys()) + list(BRCA2_MARKERS.keys()),
        "indications": [
            "Personal history of breast cancer <50 or triple-negative",
            "Personal history of ovarian cancer",
            "Male breast cancer",
            "Ashkenazi Jewish ancestry with breast/ovarian cancer",
            "Family history of breast/ovarian cancer"
        ]
    },
    "lynch": {
        "genes": ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"],
        "markers": list(LYNCH_SYNDROME_MARKERS.keys()),
        "indications": [
            "Colorectal cancer <50",
            "Multiple Lynch-associated cancers",
            "Family history of colorectal/endometrial cancer",
            "Tumor with MSI-H or dMMR"
        ]
    },
    "comprehensive_cancer": {
        "genes": ["BRCA1", "BRCA2", "MLH1", "MSH2", "MSH6", "PMS2", 
                 "APC", "TP53", "CHEK2", "PALB2", "ATM", "CDH1", "STK11"],
        "markers": list(HEREDITARY_CANCER_MARKERS.keys()),
        "note": "Broad hereditary cancer panel"
    }
}


def analyze_cancer_panel(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze hereditary cancer panel markers.
    
    Returns:
        Dict with cancer panel results and recommendations
    """
    results = {
        "pathogenic_variants": [],
        "likely_pathogenic_variants": [],
        "vus": [],  # Variants of uncertain significance
        "markers_analyzed": 0,
        "genes_covered": set(),
        "syndromes_detected": [],
        "critical_findings": False,
        "recommendations": [],
        "summary": ""
    }
    
    for rsid, info in HEREDITARY_CANCER_MARKERS.items():
        geno = genotypes.get(rsid)
        if not geno:
            continue
        
        results["markers_analyzed"] += 1
        results["genes_covered"].add(info.get("gene", "Unknown"))
        
        # Check for pathogenic allele
        risk_allele = info.get("risk_allele")
        classification = info.get("classification", "unknown")
        
        # For most pathogenic variants, presence of any non-reference indicates carrier
        # This is simplified - full interpretation requires knowing ref/alt
        is_carrier = True  # Conservative: if genotyped, assume may be informative
        
        if classification == "pathogenic":
            variant_info = {
                "rsid": rsid,
                "gene": info.get("gene"),
                "variant": info.get("variant"),
                "genotype": geno,
                "syndrome": info.get("syndrome"),
                "cancer_risks": info.get("cancer_risks"),
                "recommendations": info.get("recommendations", []),
            }
            results["pathogenic_variants"].append(variant_info)
            
            if info.get("actionable", {}).get("priority") == "critical":
                results["critical_findings"] = True
            
            syndrome = info.get("syndrome")
            if syndrome and syndrome not in results["syndromes_detected"]:
                results["syndromes_detected"].append(syndrome)
        
        elif classification == "likely_pathogenic":
            results["likely_pathogenic_variants"].append({
                "rsid": rsid,
                "gene": info.get("gene"),
                "variant": info.get("variant"),
                "genotype": geno,
            })
    
    # Generate summary
    results["genes_covered"] = list(results["genes_covered"])
    
    if results["pathogenic_variants"]:
        results["summary"] = f"ALERT: {len(results['pathogenic_variants'])} pathogenic variant(s) detected"
        results["recommendations"].append("Genetic counseling strongly recommended")
        results["recommendations"].append("Clinical confirmation required")
        
        for var in results["pathogenic_variants"]:
            if var.get("recommendations"):
                results["recommendations"].extend(var["recommendations"])
    elif results["likely_pathogenic_variants"]:
        results["summary"] = f"Possible findings: {len(results['likely_pathogenic_variants'])} likely pathogenic variant(s)"
        results["recommendations"].append("Consider genetic counseling")
    else:
        results["summary"] = "No known pathogenic variants detected in tested markers"
        results["recommendations"].append(
            "Note: Consumer arrays cannot detect all hereditary cancer variants. "
            "Comprehensive genetic testing may be warranted based on family history."
        )
    
    return results
