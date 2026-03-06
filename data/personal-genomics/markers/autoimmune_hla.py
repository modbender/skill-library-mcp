"""
Autoimmune HLA Associations Module
HLA-linked autoimmune disease susceptibility

Sources:
- NHGRI-EBI GWAS Catalog
- Published HLA disease association studies
- American College of Rheumatology guidelines

HLA (Human Leukocyte Antigen) genes are the most disease-associated region
in the human genome. Certain HLA types strongly predispose to specific
autoimmune conditions.

IMPORTANT NOTES:
- HLA associations are risk factors, not diagnostic
- Most people with risk alleles never develop disease
- Disease development requires genetic + environmental triggers
- These markers use tag SNPs that correlate with classical HLA types
"""

from typing import Dict, List, Optional, Any

# =============================================================================
# CELIAC DISEASE - HLA-DQ2/DQ8
# =============================================================================

CELIAC_HLA_MARKERS = {
    "rs2187668": {
        "gene": "HLA-DQA1*05",
        "hla_type": "DQ2.5 (DQA1*05:01/DQB1*02:01)",
        "risk_allele": "T",
        "condition": "Celiac disease",
        "odds_ratio": 7.0,
        "population_freq": {"EUR": 0.25, "Global": 0.20},
        "note": "~95% of celiacs are DQ2 and/or DQ8 positive. DQ2.5 is highest risk.",
        "clinical_utility": {
            "positive": "Cannot rule out celiac; if symptomatic, test tTG-IgA",
            "negative": "Celiac disease very unlikely (<1% of celiacs are DQ2/DQ8 negative)"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "celiac_risk",
            "recommendations": [
                "DQ2.5 positive - celiac susceptibility present",
                "If GI symptoms: do NOT start gluten-free diet before testing",
                "Check tTG-IgA if symptomatic",
                "DQ2/DQ8 negativity essentially rules OUT celiac"
            ]
        }
    },
    "rs7454108": {
        "gene": "HLA-DQB1*02",
        "hla_type": "DQ2.5 tag",
        "risk_allele": "C",
        "condition": "Celiac disease",
        "odds_ratio": 6.0,
        "note": "Second tag SNP for DQ2.5 haplotype"
    },
    "rs7775228": {
        "gene": "HLA-DQB1*03:02",
        "hla_type": "DQ8",
        "risk_allele": "C",
        "condition": "Celiac disease",
        "odds_ratio": 3.0,
        "note": "DQ8 confers lower risk than DQ2 but still significant",
        "clinical_utility": {
            "positive": "DQ8 positive - celiac possible if symptoms present"
        }
    },
    "rs2395182": {
        "gene": "HLA-DRB1",
        "hla_type": "DR3-DQ2 haplotype tag",
        "risk_allele": "T",
        "condition": "Celiac disease",
        "note": "Part of extended celiac risk haplotype"
    },
}

# =============================================================================
# TYPE 1 DIABETES - HLA-DR/DQ
# =============================================================================

TYPE1_DIABETES_HLA_MARKERS = {
    "rs7454108": {
        "gene": "HLA-DQB1",
        "hla_type": "DQ2/DQ8 tag",
        "risk_allele": "C",
        "condition": "Type 1 Diabetes",
        "odds_ratio": 3.5,
        "note": "Shared risk with celiac disease"
    },
    "rs9273363": {
        "gene": "HLA-DQB1",
        "hla_type": "DQB1*06:02 protective",
        "risk_allele": "C",
        "effect": "protective",
        "odds_ratio": 0.15,  # Protective
        "condition": "Type 1 Diabetes",
        "note": "DQB1*06:02 is strongly PROTECTIVE against T1D"
    },
    "rs2647044": {
        "gene": "HLA-DRB1",
        "hla_type": "DR4-DQ8",
        "risk_allele": "G",
        "condition": "Type 1 Diabetes",
        "odds_ratio": 4.0,
        "note": "DR4-DQ8 haplotype - highest T1D risk"
    },
    "rs3104413": {
        "gene": "HLA-DRB1",
        "hla_type": "DR3-DQ2",
        "risk_allele": "C",
        "condition": "Type 1 Diabetes",
        "odds_ratio": 3.0,
        "note": "DR3-DQ2 haplotype"
    },
    "rs2476601": {
        "gene": "PTPN22",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Type 1 Diabetes",
        "odds_ratio": 1.9,
        "note": "Non-HLA autoimmune susceptibility locus",
        "other_conditions": ["Rheumatoid arthritis", "Lupus", "Graves disease"]
    },
}

# =============================================================================
# ANKYLOSING SPONDYLITIS - HLA-B27
# =============================================================================

ANKYLOSING_SPONDYLITIS_MARKERS = {
    "rs4349859": {
        "gene": "HLA-B",
        "hla_type": "HLA-B*27",
        "risk_allele": "A",
        "condition": "Ankylosing spondylitis",
        "odds_ratio": 69.0,
        "population_freq": {"EUR": 0.08, "Global": 0.05},
        "note": "Strongest genetic association in any complex disease. ~90% of AS patients are B27+",
        "clinical_utility": {
            "positive": "HLA-B27 positive - strongly supports AS if symptoms present",
            "negative": "Does not rule out, but makes AS less likely"
        },
        "associated_conditions": [
            "Ankylosing spondylitis",
            "Reactive arthritis",
            "Psoriatic spondyloarthritis", 
            "IBD-associated spondyloarthritis",
            "Acute anterior uveitis"
        ],
        "actionable": {
            "priority": "medium",
            "action_type": "hla_b27_positive",
            "recommendations": [
                "HLA-B27 positive",
                "If back pain: consider spondyloarthritis workup",
                "Note: Most B27+ people never develop AS (~5%)",
                "Associated with acute anterior uveitis risk"
            ]
        }
    },
    "rs13202464": {
        "gene": "HLA-B",
        "hla_type": "B27 tag SNP 2",
        "risk_allele": "G",
        "condition": "Ankylosing spondylitis",
        "note": "Secondary B27 tag marker"
    },
    # ERAP1 - non-HLA modifier
    "rs30187": {
        "gene": "ERAP1",
        "hla_type": "Non-HLA",
        "risk_allele": "T",
        "condition": "Ankylosing spondylitis",
        "odds_ratio": 1.4,
        "note": "Modifies risk in B27+ individuals only"
    },
}

# =============================================================================
# RHEUMATOID ARTHRITIS - HLA-DR4/DR1 (Shared Epitope)
# =============================================================================

RHEUMATOID_ARTHRITIS_MARKERS = {
    "rs6910071": {
        "gene": "HLA-DRB1",
        "hla_type": "Shared Epitope tag",
        "risk_allele": "G",
        "condition": "Rheumatoid arthritis",
        "odds_ratio": 2.8,
        "note": "Tags HLA-DRB1 shared epitope alleles (DR4, DR1, DR10)",
        "clinical_utility": {
            "positive": "Increased RA susceptibility",
            "note": "Shared epitope present in ~70% of RA patients vs 30% controls"
        },
        "actionable": {
            "priority": "low",
            "action_type": "ra_susceptibility",
            "recommendations": [
                "Shared epitope present - RA susceptibility",
                "If joint symptoms: RF and anti-CCP testing indicated"
            ]
        }
    },
    "rs660895": {
        "gene": "HLA-DRB1",
        "hla_type": "DR4 tag",
        "risk_allele": "G",
        "condition": "Rheumatoid arthritis",
        "odds_ratio": 2.5
    },
    "rs2476601": {
        "gene": "PTPN22",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Rheumatoid arthritis",
        "odds_ratio": 1.8,
        "note": "Shared autoimmune risk locus"
    },
    "rs3087243": {
        "gene": "CTLA4",
        "hla_type": "Non-HLA",
        "risk_allele": "G",
        "condition": "Rheumatoid arthritis",
        "odds_ratio": 1.2,
        "note": "T cell regulation"
    },
}

# =============================================================================
# SYSTEMIC LUPUS ERYTHEMATOSUS (SLE/LUPUS)
# =============================================================================

LUPUS_MARKERS = {
    "rs1270942": {
        "gene": "HLA-DRB1",
        "hla_type": "DR3 tag",
        "risk_allele": "A",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 2.5,
        "note": "HLA-DR3 associated with SLE, especially in European ancestry"
    },
    "rs2476601": {
        "gene": "PTPN22",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 1.5
    },
    "rs7574865": {
        "gene": "STAT4",
        "hla_type": "Non-HLA",
        "risk_allele": "T",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 1.6,
        "note": "Also associated with RA"
    },
    "rs2205960": {
        "gene": "TNFSF4",
        "hla_type": "Non-HLA",
        "risk_allele": "T",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 1.4
    },
    "rs10488631": {
        "gene": "IRF5",
        "hla_type": "Non-HLA",
        "risk_allele": "C",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 1.8,
        "note": "Interferon pathway - key in lupus pathogenesis"
    },
    "rs1143679": {
        "gene": "ITGAM",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Systemic lupus erythematosus",
        "odds_ratio": 1.6,
        "note": "Associated with lupus nephritis"
    },
}

# =============================================================================
# OTHER AUTOIMMUNE CONDITIONS
# =============================================================================

OTHER_AUTOIMMUNE_MARKERS = {
    # Multiple Sclerosis - HLA-DRB1*15:01
    "rs3135388": {
        "gene": "HLA-DRB1",
        "hla_type": "DRB1*15:01 tag",
        "risk_allele": "A",
        "condition": "Multiple sclerosis",
        "odds_ratio": 3.0,
        "note": "Strongest MS risk locus"
    },
    "rs2104286": {
        "gene": "IL2RA",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Multiple sclerosis",
        "odds_ratio": 1.3
    },
    
    # Graves' Disease (hyperthyroidism)
    "rs3087243": {
        "gene": "CTLA4",
        "hla_type": "Non-HLA",
        "risk_allele": "G",
        "condition": "Graves disease",
        "odds_ratio": 1.5
    },
    "rs179247": {
        "gene": "TSHR",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Graves disease",
        "odds_ratio": 1.4,
        "note": "TSH receptor variants"
    },
    
    # Hashimoto's Thyroiditis
    "rs3184504": {
        "gene": "SH2B3",
        "hla_type": "Non-HLA",
        "risk_allele": "T",
        "condition": "Hashimoto thyroiditis",
        "odds_ratio": 1.3,
        "note": "Also associated with other autoimmune conditions"
    },
    
    # Psoriasis
    "rs10484554": {
        "gene": "HLA-C",
        "hla_type": "HLA-C*06:02",
        "risk_allele": "A",
        "condition": "Psoriasis",
        "odds_ratio": 4.0,
        "note": "Strongest psoriasis risk allele"
    },
    "rs12191877": {
        "gene": "HLA-C",
        "hla_type": "HLA-C*06:02 tag 2",
        "risk_allele": "T",
        "condition": "Psoriasis",
        "odds_ratio": 3.5
    },
    
    # IBD (Crohn's/Ulcerative Colitis)
    "rs11209026": {
        "gene": "IL23R",
        "hla_type": "Non-HLA",
        "risk_allele": "A",  # Minor allele is PROTECTIVE
        "condition": "Crohn disease",
        "odds_ratio": 0.4,  # Protective
        "note": "R381Q - protective variant",
        "effect": "protective"
    },
    "rs2066844": {
        "gene": "NOD2",
        "hla_type": "Non-HLA",
        "risk_allele": "T",
        "condition": "Crohn disease",
        "odds_ratio": 2.4,
        "note": "R702W - Crohn's susceptibility"
    },
    "rs2066845": {
        "gene": "NOD2",
        "hla_type": "Non-HLA",
        "risk_allele": "C",
        "condition": "Crohn disease",
        "odds_ratio": 2.8,
        "note": "G908R"
    },
    "rs2066847": {
        "gene": "NOD2",
        "hla_type": "Non-HLA",
        "risk_allele": "C",
        "condition": "Crohn disease",
        "odds_ratio": 4.0,
        "note": "1007fs frameshift - highest Crohn's risk variant in NOD2"
    },
    
    # Vitiligo
    "rs1393350": {
        "gene": "TYR",
        "hla_type": "Non-HLA",
        "risk_allele": "A",
        "condition": "Vitiligo",
        "odds_ratio": 1.5
    },
    
    # Alopecia Areata
    "rs9275572": {
        "gene": "HLA-DQB1",
        "hla_type": "HLA-DQB1 tag",
        "risk_allele": "A",
        "condition": "Alopecia areata",
        "odds_ratio": 2.0
    },
}

# =============================================================================
# COMBINED AUTOIMMUNE HLA PANEL
# =============================================================================

AUTOIMMUNE_HLA_MARKERS = {
    **CELIAC_HLA_MARKERS,
    **TYPE1_DIABETES_HLA_MARKERS,
    **ANKYLOSING_SPONDYLITIS_MARKERS,
    **RHEUMATOID_ARTHRITIS_MARKERS,
    **LUPUS_MARKERS,
    **OTHER_AUTOIMMUNE_MARKERS,
}

# Condition summaries
AUTOIMMUNE_CONDITIONS = {
    "celiac": {
        "name": "Celiac Disease",
        "markers": list(CELIAC_HLA_MARKERS.keys()),
        "prevalence": "1 in 100",
        "key_hla": "HLA-DQ2.5, HLA-DQ8",
        "note": "DQ2/DQ8 testing can rule OUT celiac if negative"
    },
    "type1_diabetes": {
        "name": "Type 1 Diabetes",
        "markers": list(TYPE1_DIABETES_HLA_MARKERS.keys()),
        "prevalence": "1 in 300",
        "key_hla": "DR3-DQ2, DR4-DQ8"
    },
    "ankylosing_spondylitis": {
        "name": "Ankylosing Spondylitis",
        "markers": list(ANKYLOSING_SPONDYLITIS_MARKERS.keys()),
        "prevalence": "1 in 200 (HLA-B27+)",
        "key_hla": "HLA-B27",
        "note": "Strongest HLA-disease association known (OR ~70)"
    },
    "rheumatoid_arthritis": {
        "name": "Rheumatoid Arthritis",
        "markers": list(RHEUMATOID_ARTHRITIS_MARKERS.keys()),
        "prevalence": "1 in 100",
        "key_hla": "Shared Epitope (DR4, DR1)"
    },
    "lupus": {
        "name": "Systemic Lupus Erythematosus",
        "markers": list(LUPUS_MARKERS.keys()),
        "prevalence": "1 in 1000",
        "key_hla": "HLA-DR3",
        "note": "Multiple non-HLA loci also important"
    },
}


def analyze_autoimmune_risk(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze autoimmune disease risk based on HLA and related markers.
    
    Returns:
        Dict with autoimmune risk profile
    """
    results = {
        "conditions_analyzed": list(AUTOIMMUNE_CONDITIONS.keys()),
        "markers_found": 0,
        "risk_profile": {},
        "hla_types_detected": [],
        "key_findings": [],
        "actionable_items": [],
        "protective_factors": []
    }
    
    condition_scores = {cond: {"risk_markers": 0, "total_or": 1.0, "markers": []} 
                       for cond in AUTOIMMUNE_CONDITIONS}
    
    for rsid, info in AUTOIMMUNE_HLA_MARKERS.items():
        geno = genotypes.get(rsid)
        if not geno:
            continue
        
        results["markers_found"] += 1
        risk_allele = info.get("risk_allele", "")
        condition = info.get("condition", "")
        
        # Count risk alleles
        risk_count = sum(1 for a in geno if a.upper() == risk_allele.upper())
        
        if risk_count > 0:
            or_val = info.get("odds_ratio", 1.0)
            
            # Check if protective
            if info.get("effect") == "protective" or or_val < 1.0:
                results["protective_factors"].append({
                    "gene": info.get("gene"),
                    "condition": condition,
                    "genotype": geno,
                    "protective_effect": f"OR={or_val}"
                })
            else:
                # Map to condition category
                cond_key = None
                for key, cond_info in AUTOIMMUNE_CONDITIONS.items():
                    if condition.lower() in cond_info["name"].lower() or \
                       key.replace("_", " ") in condition.lower():
                        cond_key = key
                        break
                
                if cond_key:
                    condition_scores[cond_key]["risk_markers"] += 1
                    condition_scores[cond_key]["total_or"] *= or_val ** risk_count
                    condition_scores[cond_key]["markers"].append({
                        "rsid": rsid,
                        "gene": info.get("gene"),
                        "hla_type": info.get("hla_type"),
                        "genotype": geno,
                        "risk_copies": risk_count,
                        "odds_ratio": or_val
                    })
                
                # Track HLA types
                hla_type = info.get("hla_type")
                if hla_type and "HLA" in hla_type:
                    results["hla_types_detected"].append(hla_type)
                
                # Actionable items
                if info.get("actionable"):
                    results["actionable_items"].append({
                        "condition": condition,
                        "gene": info.get("gene"),
                        **info["actionable"]
                    })
    
    # Build risk profile
    for cond_key, scores in condition_scores.items():
        cond_info = AUTOIMMUNE_CONDITIONS[cond_key]
        
        if scores["risk_markers"] > 0:
            # Determine risk level
            total_or = scores["total_or"]
            if total_or >= 10:
                risk_level = "high"
            elif total_or >= 3:
                risk_level = "moderate"
            elif total_or >= 1.5:
                risk_level = "slightly_elevated"
            else:
                risk_level = "population_average"
            
            results["risk_profile"][cond_key] = {
                "condition": cond_info["name"],
                "risk_level": risk_level,
                "combined_or": round(total_or, 1),
                "risk_markers_found": scores["risk_markers"],
                "key_hla": cond_info.get("key_hla"),
                "markers": scores["markers"]
            }
            
            # Key findings for high-risk
            if risk_level in ["high", "moderate"]:
                results["key_findings"].append({
                    "condition": cond_info["name"],
                    "risk_level": risk_level,
                    "explanation": f"Combined OR: {round(total_or, 1)}",
                    "note": cond_info.get("note")
                })
    
    # Generate summary
    high_risk = [r for r in results["risk_profile"].values() if r["risk_level"] == "high"]
    mod_risk = [r for r in results["risk_profile"].values() if r["risk_level"] == "moderate"]
    
    if high_risk:
        results["summary"] = f"Elevated genetic risk for: {', '.join(r['condition'] for r in high_risk)}"
    elif mod_risk:
        results["summary"] = f"Moderately elevated risk for: {', '.join(r['condition'] for r in mod_risk)}"
    else:
        results["summary"] = "No highly elevated autoimmune disease risks detected"
    
    return results
