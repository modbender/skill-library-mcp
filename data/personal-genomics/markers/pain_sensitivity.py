"""
Pain Sensitivity & Analgesic Response Module
Genetic variants affecting pain perception and drug response

Sources:
- PharmGKB pain/opioid guidelines
- Published pain genetics studies
- CPIC opioid guidelines

This module covers:
- Pain perception sensitivity
- Opioid response and metabolism
- NSAID sensitivity
- Capsaicin sensitivity
- Migraine susceptibility
"""

from typing import Dict, List, Optional, Any

# =============================================================================
# COMT - CATECHOL-O-METHYLTRANSFERASE
# Key regulator of pain perception and opioid requirements
# =============================================================================

COMT_MARKERS = {
    "rs4680": {
        "gene": "COMT",
        "variant": "Val158Met (G>A)",
        "risk_allele": "A",
        "genotype_effects": {
            "GG": {
                "phenotype": "Val/Val - High COMT activity",
                "pain_sensitivity": "lower",
                "stress_resilience": "higher (warrior)",
                "opioid_requirements": "higher doses may be needed",
                "effect_size": "25-40% difference in experimental pain"
            },
            "GA": {
                "phenotype": "Val/Met - Intermediate COMT activity",
                "pain_sensitivity": "intermediate",
                "opioid_requirements": "standard dosing"
            },
            "AA": {
                "phenotype": "Met/Met - Low COMT activity",
                "pain_sensitivity": "higher",
                "stress_sensitivity": "higher (worrier)",
                "opioid_requirements": "may need lower doses",
                "effect_size": "Increased experimental pain sensitivity"
            }
        },
        "clinical_notes": [
            "Affects dopamine/norepinephrine metabolism in prefrontal cortex",
            "Met carriers have higher dopamine levels, better working memory under low stress",
            "Val carriers have lower dopamine, better stress tolerance",
            "Pain sensitivity differences modest but reproducible"
        ],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "action_type": "pain_sensitivity",
            "recommendations": [
                "COMT Val158Met affects pain perception and opioid needs",
                "Met/Met: May be more pain sensitive, may need less opioid",
                "Val/Val: May tolerate pain better, may need higher opioid doses"
            ]
        }
    },
    "rs4633": {
        "gene": "COMT",
        "variant": "Synonymous marker in LD with Val158Met",
        "note": "Tags Val158Met haplotype"
    },
    "rs6269": {
        "gene": "COMT",
        "variant": "Upstream/haplotype marker",
        "risk_allele": "A",
        "note": "Part of pain sensitivity haplotype"
    },
    "rs4818": {
        "gene": "COMT",
        "variant": "Haplotype marker",
        "risk_allele": "C",
        "note": "Combined with rs4680 defines pain haplotypes"
    },
}

# =============================================================================
# OPRM1 - MU OPIOID RECEPTOR
# Primary target for opioid analgesics
# =============================================================================

OPRM1_MARKERS = {
    "rs1799971": {
        "gene": "OPRM1",
        "variant": "A118G (Asn40Asp)",
        "risk_allele": "G",
        "genotype_effects": {
            "AA": {
                "phenotype": "Asn/Asn - Normal opioid receptor",
                "opioid_response": "standard response",
                "frequency": "~80% European, ~50% Asian"
            },
            "AG": {
                "phenotype": "Asn/Asp - Reduced receptor expression",
                "opioid_response": "reduced analgesia",
                "opioid_requirements": "may need 10-30% higher doses",
                "side_effects": "possibly less nausea/sedation"
            },
            "GG": {
                "phenotype": "Asp/Asp - Significantly reduced expression",
                "opioid_response": "reduced analgesia",
                "opioid_requirements": "may need significantly higher doses",
                "frequency": "~2% European, ~15% Asian"
            }
        },
        "clinical_notes": [
            "G allele reduces mu-opioid receptor expression by ~50%",
            "G carriers may need higher opioid doses for same analgesia",
            "G allele associated with less opioid side effects",
            "More common in East Asian populations"
        ],
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "action_type": "opioid_dosing",
            "recommendations": [
                "OPRM1 A118G affects opioid response",
                "G allele carriers may need higher opioid doses",
                "Monitor for inadequate analgesia in AG/GG genotypes"
            ]
        }
    },
}

# =============================================================================
# SCN9A - SODIUM CHANNEL (PAIN SIGNALING)
# =============================================================================

SCN9A_MARKERS = {
    "rs6746030": {
        "gene": "SCN9A",
        "variant": "Nav1.7 pain channel polymorphism",
        "risk_allele": "A",
        "genotype_effects": {
            "GG": {
                "pain_sensitivity": "average",
            },
            "GA": {
                "pain_sensitivity": "slightly increased"
            },
            "AA": {
                "pain_sensitivity": "increased experimental pain",
                "note": "Higher thermal and ischemic pain ratings"
            }
        },
        "clinical_notes": [
            "SCN9A encodes Nav1.7 voltage-gated sodium channel",
            "Key in pain signal transmission from peripheral neurons",
            "Rare loss-of-function mutations cause congenital insensitivity to pain",
            "Common variant has modest effect on pain threshold"
        ],
        "evidence": "moderate"
    },
    "rs3750904": {
        "gene": "SCN9A",
        "variant": "Nav1.7 polymorphism",
        "risk_allele": "T",
        "condition": "Pain sensitivity",
        "evidence": "moderate"
    },
}

# =============================================================================
# TRPV1 - CAPSAICIN RECEPTOR
# =============================================================================

TRPV1_MARKERS = {
    "rs8065080": {
        "gene": "TRPV1",
        "variant": "I585V",
        "risk_allele": "T",
        "genotype_effects": {
            "CC": {
                "capsaicin_sensitivity": "higher",
                "thermal_pain": "higher sensitivity"
            },
            "CT": {
                "capsaicin_sensitivity": "intermediate"
            },
            "TT": {
                "capsaicin_sensitivity": "lower",
                "thermal_pain": "lower sensitivity"
            }
        },
        "clinical_notes": [
            "TRPV1 is the capsaicin (hot pepper) receptor",
            "Also responds to heat and inflammation",
            "Affects spicy food tolerance and thermal pain"
        ],
        "fun_fact": "Explains why some people tolerate extremely spicy food",
        "evidence": "moderate",
        "actionable": {
            "priority": "low",
            "action_type": "capsaicin_sensitivity",
            "recommendations": [
                "TRPV1 variant affects spicy food tolerance",
                "Also affects thermal pain sensitivity"
            ]
        }
    },
    "rs222747": {
        "gene": "TRPV1",
        "variant": "M315I",
        "risk_allele": "G",
        "condition": "Capsaicin sensitivity, thermal pain",
        "evidence": "moderate"
    },
}

# =============================================================================
# OPIOID METABOLISM (CYP2D6 context)
# =============================================================================

OPIOID_METABOLISM_MARKERS = {
    # CYP2D6 markers (critical for codeine, tramadol)
    "rs3892097": {
        "gene": "CYP2D6",
        "variant": "*4 allele tag",
        "risk_allele": "A",
        "genotype_effects": {
            "GG": {
                "metabolizer_status": "normal/extensive",
                "codeine_response": "normal activation to morphine"
            },
            "GA": {
                "metabolizer_status": "intermediate",
                "codeine_response": "reduced but present"
            },
            "AA": {
                "metabolizer_status": "poor",
                "codeine_response": "NO activation - codeine ineffective",
                "tramadol_response": "Reduced/absent"
            }
        },
        "clinical_notes": [
            "CYP2D6 converts codeine to morphine (active)",
            "Poor metabolizers get NO pain relief from codeine",
            "Ultra-rapid metabolizers at risk of toxicity",
            "Affects ~10% of Europeans"
        ],
        "evidence": "strong",
        "actionable": {
            "priority": "high",
            "action_type": "opioid_metabolism",
            "recommendations": [
                "CYP2D6 poor metabolizer - codeine INEFFECTIVE",
                "Use morphine, oxycodone, or hydromorphone instead",
                "Tramadol also affected"
            ]
        }
    },
    "rs5030655": {
        "gene": "CYP2D6",
        "variant": "*6 deletion",
        "risk_allele": "del",
        "condition": "CYP2D6 poor metabolizer",
        "evidence": "strong"
    },
    "rs1065852": {
        "gene": "CYP2D6",
        "variant": "*10 tag",
        "risk_allele": "A",
        "condition": "CYP2D6 reduced function (common in Asians)",
        "population": "30-50% East Asian",
        "evidence": "strong"
    },
    
    # CYP2D6 copy number (ultra-rapid metabolizers)
    # Note: CNV not directly detectable on most consumer arrays
    "rs28371725": {
        "gene": "CYP2D6",
        "variant": "*41 reduced function",
        "risk_allele": "T",
        "condition": "CYP2D6 intermediate metabolizer",
        "evidence": "strong"
    },
}

# =============================================================================
# MIGRAINE SUSCEPTIBILITY
# =============================================================================

MIGRAINE_MARKERS = {
    "rs1835740": {
        "gene": "8q22.1",
        "variant": "Migraine susceptibility locus",
        "risk_allele": "A",
        "condition": "Migraine",
        "odds_ratio": 1.2,
        "evidence": "strong",
        "note": "Affects glutamate clearance"
    },
    "rs2651899": {
        "gene": "PRDM16",
        "variant": "Migraine risk variant",
        "risk_allele": "C",
        "condition": "Migraine",
        "odds_ratio": 1.1,
        "evidence": "strong"
    },
    "rs10166942": {
        "gene": "TRPM8",
        "variant": "Cold sensor / migraine",
        "risk_allele": "T",
        "condition": "Migraine",
        "odds_ratio": 1.2,
        "evidence": "strong",
        "note": "Menthol receptor - involved in cold headache response"
    },
    "rs11172113": {
        "gene": "LRP1",
        "variant": "Migraine susceptibility",
        "risk_allele": "T",
        "condition": "Migraine",
        "odds_ratio": 1.15,
        "evidence": "strong"
    },
    "rs3790455": {
        "gene": "CACNA1A",
        "variant": "Calcium channel",
        "risk_allele": "T",
        "condition": "Migraine with aura",
        "note": "Rare mutations cause familial hemiplegic migraine",
        "evidence": "moderate"
    },
}

# =============================================================================
# NSAID RESPONSE
# =============================================================================

NSAID_RESPONSE_MARKERS = {
    "rs20417": {
        "gene": "PTGS2",
        "variant": "COX-2 promoter variant",
        "risk_allele": "C",
        "genotype_effects": {
            "GG": {"nsaid_response": "standard"},
            "GC": {"nsaid_response": "possibly reduced COX-2 expression"},
            "CC": {"nsaid_response": "reduced COX-2 expression"}
        },
        "clinical_notes": [
            "COX-2 is target of NSAIDs and coxibs",
            "May affect cardiovascular risk profile of NSAIDs"
        ],
        "evidence": "moderate"
    },
    "rs5275": {
        "gene": "PTGS2",
        "variant": "COX-2 3'-UTR",
        "risk_allele": "C",
        "condition": "NSAID response variation",
        "evidence": "moderate"
    },
}

# =============================================================================
# COMBINED PAIN SENSITIVITY PANEL
# =============================================================================

PAIN_SENSITIVITY_MARKERS = {
    **COMT_MARKERS,
    **OPRM1_MARKERS,
    **SCN9A_MARKERS,
    **TRPV1_MARKERS,
    **OPIOID_METABOLISM_MARKERS,
    **MIGRAINE_MARKERS,
    **NSAID_RESPONSE_MARKERS,
}


def analyze_pain_sensitivity(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze pain sensitivity and analgesic response profile.
    
    Returns:
        Dict with pain sensitivity analysis
    """
    results = {
        "markers_found": 0,
        "pain_sensitivity_profile": {
            "overall": "average",
            "thermal": None,
            "capsaicin": None,
        },
        "opioid_response": {
            "comt_effect": None,
            "oprm1_effect": None,
            "cyp2d6_metabolism": None,
            "recommendations": []
        },
        "migraine_risk": {
            "risk_alleles": 0,
            "total_markers": 0,
            "risk_level": "average"
        },
        "key_findings": [],
        "actionable_items": []
    }
    
    # Analyze COMT
    comt_geno = genotypes.get("rs4680")
    if comt_geno:
        results["markers_found"] += 1
        comt_info = COMT_MARKERS["rs4680"]["genotype_effects"].get(comt_geno)
        if comt_info:
            results["opioid_response"]["comt_effect"] = comt_info
            results["pain_sensitivity_profile"]["overall"] = comt_info.get("pain_sensitivity", "average")
            
            if comt_geno == "AA":
                results["key_findings"].append({
                    "gene": "COMT",
                    "genotype": "Met/Met (AA)",
                    "effect": "Higher pain sensitivity, may need lower opioid doses"
                })
            elif comt_geno == "GG":
                results["key_findings"].append({
                    "gene": "COMT",
                    "genotype": "Val/Val (GG)",
                    "effect": "Lower pain sensitivity, may need higher opioid doses"
                })
    
    # Analyze OPRM1
    oprm1_geno = genotypes.get("rs1799971")
    if oprm1_geno:
        results["markers_found"] += 1
        oprm1_info = OPRM1_MARKERS["rs1799971"]["genotype_effects"].get(oprm1_geno)
        if oprm1_info:
            results["opioid_response"]["oprm1_effect"] = oprm1_info
            
            if "G" in oprm1_geno:
                results["key_findings"].append({
                    "gene": "OPRM1",
                    "genotype": oprm1_geno,
                    "effect": "Reduced opioid receptor function - may need higher doses"
                })
    
    # Analyze CYP2D6
    cyp2d6_geno = genotypes.get("rs3892097")
    if cyp2d6_geno:
        results["markers_found"] += 1
        if cyp2d6_geno == "AA":
            results["opioid_response"]["cyp2d6_metabolism"] = "poor"
            results["opioid_response"]["recommendations"].append(
                "AVOID codeine and tramadol - no activation to active metabolite"
            )
            results["key_findings"].append({
                "gene": "CYP2D6",
                "genotype": cyp2d6_geno,
                "effect": "Poor metabolizer - codeine/tramadol INEFFECTIVE",
                "priority": "high"
            })
            results["actionable_items"].append({
                "gene": "CYP2D6",
                "action": "Avoid codeine and tramadol",
                "alternative": "Use morphine, oxycodone, or hydromorphone"
            })
        elif cyp2d6_geno == "GA":
            results["opioid_response"]["cyp2d6_metabolism"] = "intermediate"
    
    # Analyze TRPV1 (capsaicin)
    trpv1_geno = genotypes.get("rs8065080")
    if trpv1_geno:
        results["markers_found"] += 1
        trpv1_info = TRPV1_MARKERS["rs8065080"]["genotype_effects"].get(trpv1_geno)
        if trpv1_info:
            results["pain_sensitivity_profile"]["capsaicin"] = trpv1_info.get("capsaicin_sensitivity")
            results["pain_sensitivity_profile"]["thermal"] = trpv1_info.get("thermal_pain")
    
    # Analyze migraine markers
    for rsid, info in MIGRAINE_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            results["migraine_risk"]["total_markers"] += 1
            risk_allele = info.get("risk_allele", "")
            risk_count = sum(1 for a in geno if a.upper() == risk_allele.upper())
            if risk_count > 0:
                results["migraine_risk"]["risk_alleles"] += risk_count
    
    if results["migraine_risk"]["total_markers"] > 0:
        ratio = results["migraine_risk"]["risk_alleles"] / (results["migraine_risk"]["total_markers"] * 2)
        if ratio > 0.6:
            results["migraine_risk"]["risk_level"] = "elevated"
        elif ratio > 0.4:
            results["migraine_risk"]["risk_level"] = "slightly_elevated"
    
    # Generate summary
    summaries = []
    if results["pain_sensitivity_profile"]["overall"] == "higher":
        summaries.append("Genetically higher pain sensitivity")
    elif results["pain_sensitivity_profile"]["overall"] == "lower":
        summaries.append("Genetically lower pain sensitivity")
    
    if results["opioid_response"]["cyp2d6_metabolism"] == "poor":
        summaries.append("CYP2D6 poor metabolizer - avoid codeine/tramadol")
    
    results["summary"] = "; ".join(summaries) if summaries else "No major pain-related findings"
    
    return results
