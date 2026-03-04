"""
UV Sensitivity Calculator v4.1.0
Combines pigmentation genes to estimate:
- SPF recommendations
- Burn risk
- Vitamin D synthesis capacity
- Melanoma risk factors

Genes analyzed:
- MC1R (melanocortin 1 receptor)
- SLC24A5 (European light skin)
- SLC45A2 (MATP)
- IRF4 (interferon regulatory factor 4)
- TYR (tyrosinase)
- OCA2 (oculocutaneous albinism 2)
- HERC2 (eye color)

Sources:
- GWAS on pigmentation
- Melanoma genetics studies
- Dermatology literature
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SkinType(Enum):
    """Fitzpatrick skin type classifications."""
    TYPE_I = "type_i"    # Always burns, never tans
    TYPE_II = "type_ii"   # Usually burns, tans minimally
    TYPE_III = "type_iii" # Sometimes burns, tans uniformly
    TYPE_IV = "type_iv"   # Burns minimally, tans easily
    TYPE_V = "type_v"    # Rarely burns, tans profusely
    TYPE_VI = "type_vi"   # Never burns


class MelanomaRisk(Enum):
    """Melanoma risk levels."""
    LOW = "low"
    AVERAGE = "average"
    ELEVATED = "elevated"
    HIGH = "high"


# =============================================================================
# PIGMENTATION MARKERS
# =============================================================================

MC1R_MARKERS = {
    # MC1R is the "red hair gene" - key for pigmentation and UV sensitivity
    "rs1805007": {
        "gene": "MC1R",
        "variant": "R151C",
        "trait": "Red Hair / Fair Skin",
        "risk_allele": "T",
        "weight": 3.0,  # Very strong effect
        "effects": {
            "CC": {
                "pigment_score": 0,
                "description": "Normal MC1R function",
                "phenotype": "Normal pigmentation"
            },
            "CT": {
                "pigment_score": -2,
                "description": "One R allele - fair skin/freckling likely",
                "phenotype": "Lighter skin, may have freckles, higher burn risk"
            },
            "TT": {
                "pigment_score": -4,
                "description": "Two R alleles - very fair/red hair likely",
                "phenotype": "Very fair skin, likely red hair, freckles, high burn risk"
            }
        },
        "melanoma_risk_multiplier": {"CC": 1.0, "CT": 2.0, "TT": 3.5},
        "pmid": ["11230166", "18488028"]
    },
    "rs1805008": {
        "gene": "MC1R",
        "variant": "R160W",
        "trait": "Red Hair / Fair Skin",
        "risk_allele": "T",
        "weight": 2.5,
        "effects": {
            "CC": {"pigment_score": 0, "description": "Normal"},
            "CT": {"pigment_score": -1.5, "description": "Fair skin tendency"},
            "TT": {"pigment_score": -3, "description": "Very fair, freckled"}
        },
        "melanoma_risk_multiplier": {"CC": 1.0, "CT": 1.8, "TT": 3.0},
        "pmid": ["11230166"]
    },
    "rs1805009": {
        "gene": "MC1R",
        "variant": "D294H",
        "trait": "Red Hair / Fair Skin",
        "risk_allele": "A",
        "weight": 2.0,
        "effects": {
            "GG": {"pigment_score": 0, "description": "Normal"},
            "GA": {"pigment_score": -1, "description": "Fair skin tendency"},
            "AA": {"pigment_score": -2, "description": "Fair skin"}
        },
        "pmid": ["11230166"]
    },
    "rs2228479": {
        "gene": "MC1R",
        "variant": "V92M",
        "trait": "Pigmentation",
        "risk_allele": "A",
        "weight": 0.8,
        "effects": {
            "GG": {"pigment_score": 0, "description": "Normal"},
            "GA": {"pigment_score": -0.5, "description": "Slight effect"},
            "AA": {"pigment_score": -1, "description": "Fair skin tendency"}
        },
        "pmid": ["11230166"]
    },
    "rs1110400": {
        "gene": "MC1R",
        "variant": "I155T",
        "trait": "Pigmentation",
        "risk_allele": "T",
        "weight": 0.8,
        "effects": {
            "CC": {"pigment_score": 0},
            "CT": {"pigment_score": -0.5},
            "TT": {"pigment_score": -1}
        },
        "pmid": ["11230166"]
    }
}

OTHER_PIGMENT_MARKERS = {
    "rs1426654": {
        "gene": "SLC24A5",
        "trait": "Skin Lightening (European)",
        "variant": "A111T",
        "risk_allele": "A",
        "weight": 3.0,
        "effects": {
            "GG": {
                "pigment_score": 2,
                "description": "Ancestral (darker pigmentation)",
                "uv_protection": "high"
            },
            "GA": {
                "pigment_score": 0,
                "description": "Intermediate pigmentation",
                "uv_protection": "moderate"
            },
            "AA": {
                "pigment_score": -2,
                "description": "European light skin variant",
                "uv_protection": "low"
            }
        },
        "note": "Nearly fixed in Europeans, major cause of light skin",
        "pmid": ["15695382"],
        "evidence": "very_strong"
    },
    "rs16891982": {
        "gene": "SLC45A2",
        "trait": "Skin/Hair Lightening",
        "variant": "L374F (MATP)",
        "risk_allele": "G",
        "weight": 2.5,
        "effects": {
            "CC": {
                "pigment_score": 2,
                "description": "Ancestral (darker pigmentation)",
                "uv_protection": "high"
            },
            "CG": {
                "pigment_score": 0,
                "description": "Intermediate"
            },
            "GG": {
                "pigment_score": -2,
                "description": "Light skin/hair variant",
                "uv_protection": "low"
            }
        },
        "pmid": ["17952075"],
        "evidence": "strong"
    },
    "rs12203592": {
        "gene": "IRF4",
        "trait": "Freckling / Sensitivity",
        "risk_allele": "T",
        "weight": 2.0,
        "effects": {
            "CC": {
                "pigment_score": 0,
                "description": "Normal IRF4 function"
            },
            "CT": {
                "pigment_score": -1,
                "description": "Increased freckling, light skin tendency"
            },
            "TT": {
                "pigment_score": -2,
                "description": "Strong freckling, sun sensitivity"
            }
        },
        "freckling_risk": {"CC": "low", "CT": "moderate", "TT": "high"},
        "pmid": ["18849994"]
    },
    "rs1042602": {
        "gene": "TYR",
        "trait": "Tyrosinase / Eye/Skin Color",
        "variant": "S192Y",
        "risk_allele": "A",
        "weight": 1.5,
        "effects": {
            "CC": {
                "pigment_score": 1,
                "description": "Normal tyrosinase"
            },
            "CA": {
                "pigment_score": 0,
                "description": "Intermediate"
            },
            "AA": {
                "pigment_score": -1,
                "description": "Reduced tyrosinase activity"
            }
        },
        "pmid": ["20585627"]
    },
    "rs1800407": {
        "gene": "OCA2",
        "trait": "Eye Color / Pigmentation",
        "variant": "R419Q",
        "risk_allele": "A",
        "weight": 1.0,
        "effects": {
            "GG": {"pigment_score": 0, "eye_effect": "darker"},
            "GA": {"pigment_score": -0.5, "eye_effect": "lighter tendency"},
            "AA": {"pigment_score": -1, "eye_effect": "blue/green eyes more likely"}
        },
        "pmid": ["18488028"]
    },
    "rs12913832": {
        "gene": "HERC2/OCA2",
        "trait": "Eye Color",
        "risk_allele": "G",
        "weight": 1.5,
        "effects": {
            "AA": {
                "pigment_score": 1,
                "eye_color": "brown (nearly certain)",
                "description": "Dominant for brown eyes"
            },
            "AG": {
                "pigment_score": 0,
                "eye_color": "brown likely, some green/hazel possible",
                "description": "Usually brown"
            },
            "GG": {
                "pigment_score": -1,
                "eye_color": "blue/gray/green likely",
                "description": "Strongly predictive of blue/gray eyes"
            }
        },
        "note": "Best single predictor of eye color",
        "pmid": ["18172690"],
        "evidence": "very_strong"
    }
}

VITAMIN_D_MARKERS = {
    "rs2282679": {
        "gene": "GC",
        "trait": "Vitamin D Binding Protein",
        "risk_allele": "G",
        "weight": 1.5,
        "effects": {
            "TT": {
                "vitd_score": 1,
                "description": "Normal vitamin D binding protein",
                "synthesis": "efficient"
            },
            "TG": {
                "vitd_score": 0,
                "description": "Slightly lower vitamin D levels",
                "synthesis": "normal"
            },
            "GG": {
                "vitd_score": -1,
                "description": "Lower vitamin D levels",
                "synthesis": "may need more sun/supplementation"
            }
        },
        "pmid": ["20541252"]
    },
    "rs12785878": {
        "gene": "DHCR7/NADSYN1",
        "trait": "Vitamin D Synthesis",
        "risk_allele": "T",
        "weight": 1.0,
        "effects": {
            "GG": {"vitd_score": 1, "synthesis": "efficient"},
            "GT": {"vitd_score": 0, "synthesis": "normal"},
            "TT": {"vitd_score": -1, "synthesis": "reduced from sun"}
        },
        "pmid": ["20541252"]
    },
    "rs10741657": {
        "gene": "CYP2R1",
        "trait": "Vitamin D 25-Hydroxylation",
        "risk_allele": "A",
        "weight": 1.0,
        "effects": {
            "GG": {"vitd_score": 1, "conversion": "efficient"},
            "GA": {"vitd_score": 0, "conversion": "normal"},
            "AA": {"vitd_score": -1, "conversion": "less efficient"}
        },
        "pmid": ["20541252"]
    }
}


# All pigmentation markers combined
PIGMENTATION_MARKERS = {
    **MC1R_MARKERS,
    **OTHER_PIGMENT_MARKERS,
    **VITAMIN_D_MARKERS
}


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_pigmentation_score(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate overall pigmentation score from genetic markers.
    Lower score = fairer skin = higher UV sensitivity.
    """
    total_score = 0
    weight_sum = 0
    markers_found = []
    melanoma_risk_factor = 1.0
    
    # Analyze MC1R markers
    for rsid, info in MC1R_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            weight = info.get("weight", 1.0)
            weight_sum += weight
            
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("pigment_score", 0) * weight
                total_score += score
                
                markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "variant": info.get("variant", ""),
                    "genotype": geno,
                    "effect": effect.get("description", ""),
                    "score_contribution": score
                })
                
                # Melanoma risk
                risk_mult = info.get("melanoma_risk_multiplier", {}).get(geno_upper, 1.0)
                melanoma_risk_factor *= risk_mult
    
    # Analyze other pigmentation markers
    for rsid, info in OTHER_PIGMENT_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            weight = info.get("weight", 1.0)
            weight_sum += weight
            
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("pigment_score", 0) * weight
                total_score += score
                
                markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "effect": effect.get("description", ""),
                    "score_contribution": score
                })
    
    # Normalize score
    if weight_sum > 0:
        normalized_score = total_score / (weight_sum / 3)  # Scale to roughly -10 to +10
    else:
        normalized_score = 0
    
    return {
        "raw_score": round(total_score, 2),
        "normalized_score": round(normalized_score, 2),
        "weight_sum": round(weight_sum, 2),
        "markers_found": markers_found,
        "markers_count": len(markers_found),
        "melanoma_risk_factor": round(melanoma_risk_factor, 2)
    }


def estimate_skin_type(pigment_score: float) -> Dict[str, Any]:
    """
    Estimate Fitzpatrick skin type from pigmentation score.
    """
    if pigment_score < -5:
        skin_type = SkinType.TYPE_I
        description = "Very fair - always burns, never tans"
        burn_time_minutes = 10
        tan_potential = "none"
    elif pigment_score < -3:
        skin_type = SkinType.TYPE_II
        description = "Fair - usually burns, tans minimally"
        burn_time_minutes = 15
        tan_potential = "minimal"
    elif pigment_score < -1:
        skin_type = SkinType.TYPE_III
        description = "Medium - sometimes burns, tans gradually"
        burn_time_minutes = 20
        tan_potential = "moderate"
    elif pigment_score < 2:
        skin_type = SkinType.TYPE_IV
        description = "Olive - rarely burns, tans easily"
        burn_time_minutes = 30
        tan_potential = "good"
    elif pigment_score < 5:
        skin_type = SkinType.TYPE_V
        description = "Brown - very rarely burns"
        burn_time_minutes = 45
        tan_potential = "excellent"
    else:
        skin_type = SkinType.TYPE_VI
        description = "Dark - never burns"
        burn_time_minutes = 60
        tan_potential = "maximum"
    
    return {
        "skin_type": skin_type.value,
        "description": description,
        "burn_time_unprotected_min": burn_time_minutes,
        "tan_potential": tan_potential
    }


def calculate_spf_recommendation(skin_type_info: Dict[str, Any], uv_index: int = 6) -> Dict[str, Any]:
    """
    Calculate SPF recommendation based on skin type and UV index.
    """
    skin_type = skin_type_info["skin_type"]
    burn_time = skin_type_info["burn_time_unprotected_min"]
    
    # Base SPF recommendations by skin type
    base_spf = {
        "type_i": 50,
        "type_ii": 50,
        "type_iii": 30,
        "type_iv": 30,
        "type_v": 15,
        "type_vi": 15
    }
    
    # Adjust for UV index
    uv_multiplier = 1 + (uv_index - 6) * 0.1  # Increase for higher UV
    
    recommended_spf = int(base_spf.get(skin_type, 30) * max(1, uv_multiplier))
    
    # Cap at reasonable values
    recommended_spf = min(recommended_spf, 100)
    
    # Calculate safe exposure time with SPF
    # SPF 30 means you can stay 30x longer than without protection
    safe_time_with_spf = burn_time * recommended_spf
    
    return {
        "recommended_spf": recommended_spf,
        "minimum_spf": base_spf.get(skin_type, 30),
        "safe_exposure_minutes": min(safe_time_with_spf, 480),  # Cap at 8 hours
        "reapply_every_hours": 2,
        "uv_index_assumed": uv_index,
        "tips": _get_spf_tips(skin_type)
    }


def _get_spf_tips(skin_type: str) -> List[str]:
    """Get skin-type specific sun protection tips."""
    tips = {
        "type_i": [
            "Always use SPF 50+ broad-spectrum sunscreen",
            "Seek shade during peak UV hours (10am-4pm)",
            "Wear protective clothing, wide-brimmed hat",
            "Consider UPF-rated clothing for extended outdoor time",
            "Reapply sunscreen every 90 minutes",
            "You are at HIGH melanoma risk - annual skin checks essential"
        ],
        "type_ii": [
            "Use SPF 50 broad-spectrum sunscreen",
            "Avoid peak sun hours when possible",
            "Wear a hat and sunglasses",
            "Reapply sunscreen every 2 hours",
            "Check skin monthly for new or changing moles"
        ],
        "type_iii": [
            "Use SPF 30+ broad-spectrum sunscreen",
            "Wear sunglasses to protect eyes",
            "Reapply after swimming or sweating",
            "Gradual sun exposure reduces burn risk"
        ],
        "type_iv": [
            "Use SPF 15-30 for extended exposure",
            "You can tan but still need protection",
            "Don't skip sunscreen - skin damage still occurs",
            "Protect against photoaging"
        ],
        "type_v": [
            "Use SPF 15 for extended outdoor time",
            "Lower burn risk but not zero",
            "Sunscreen helps prevent hyperpigmentation"
        ],
        "type_vi": [
            "SPF 15 recommended for extended exposure",
            "Very low burn risk",
            "Still protect against UV-induced skin changes"
        ]
    }
    return tips.get(skin_type, ["Use appropriate sunscreen for your skin type"])


def calculate_vitamin_d_synthesis(genotypes: Dict[str, str], pigment_score: float) -> Dict[str, Any]:
    """
    Estimate vitamin D synthesis capacity from sun exposure.
    """
    vitd_score = 0
    markers_found = []
    
    for rsid, info in VITAMIN_D_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("vitd_score", 0)
                vitd_score += score
                
                markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "effect": effect.get("synthesis", "normal")
                })
    
    # Darker skin needs more sun for vitamin D
    skin_adjustment = -pigment_score * 0.3  # Darker skin = more sun needed
    
    total_vitd_score = vitd_score + skin_adjustment
    
    if total_vitd_score > 1:
        synthesis = "efficient"
        sun_needed = "Standard 10-15 min midday sun"
        supplement_likely = False
    elif total_vitd_score > -1:
        synthesis = "normal"
        sun_needed = "15-20 min midday sun"
        supplement_likely = False
    elif total_vitd_score > -3:
        synthesis = "reduced"
        sun_needed = "20-30 min midday sun, or supplement"
        supplement_likely = True
    else:
        synthesis = "low"
        sun_needed = "30+ min sun OR supplementation recommended"
        supplement_likely = True
    
    return {
        "synthesis_capacity": synthesis,
        "genetic_score": round(vitd_score, 2),
        "skin_factor": round(skin_adjustment, 2),
        "total_score": round(total_vitd_score, 2),
        "sun_exposure_needed": sun_needed,
        "supplement_recommended": supplement_likely,
        "markers_found": markers_found,
        "note": "Darker skin requires more sun exposure for vitamin D synthesis"
    }


def calculate_melanoma_risk(genotypes: Dict[str, str], pigment_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimate melanoma risk from genetic markers.
    """
    risk_factor = pigment_info.get("melanoma_risk_factor", 1.0)
    
    # Additional risk factors from MC1R
    mc1r_variants = 0
    for rsid in MC1R_MARKERS:
        geno = genotypes.get(rsid)
        if geno:
            risk_allele = MC1R_MARKERS[rsid].get("risk_allele", "")
            mc1r_variants += geno.upper().count(risk_allele.upper())
    
    # Freckling (IRF4) increases risk
    irf4 = genotypes.get("rs12203592")
    if irf4 and "T" in irf4.upper():
        risk_factor *= 1.3
    
    # Classify risk
    if risk_factor > 3:
        risk_level = MelanomaRisk.HIGH
        description = "HIGH melanoma risk - strict sun protection required"
        screening = "Annual dermatologist visit, monthly self-exams"
    elif risk_factor > 2:
        risk_level = MelanomaRisk.ELEVATED
        description = "Elevated melanoma risk - careful sun protection"
        screening = "Annual dermatologist visit recommended"
    elif risk_factor > 1.3:
        risk_level = MelanomaRisk.AVERAGE
        description = "Average melanoma risk"
        screening = "Regular self-exams, dermatologist as needed"
    else:
        risk_level = MelanomaRisk.LOW
        description = "Lower melanoma risk (still use sun protection)"
        screening = "Periodic self-exams"
    
    return {
        "risk_level": risk_level.value,
        "risk_factor": round(risk_factor, 2),
        "mc1r_risk_variants": mc1r_variants,
        "description": description,
        "screening_recommendation": screening,
        "protective_factors": [
            "Avoid sunburns - even one blistering burn increases risk",
            "No tanning beds - very high melanoma association",
            "Wear sunscreen daily, even in winter",
            "Cover up with clothing during peak hours",
            "Know your moles - use ABCDE criteria"
        ]
    }


def generate_uv_sensitivity_report(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate comprehensive UV sensitivity report.
    """
    # Calculate pigmentation
    pigment = calculate_pigmentation_score(genotypes)
    
    # Estimate skin type
    skin_type = estimate_skin_type(pigment["normalized_score"])
    
    # SPF recommendation
    spf = calculate_spf_recommendation(skin_type)
    
    # Vitamin D synthesis
    vitd = calculate_vitamin_d_synthesis(genotypes, pigment["normalized_score"])
    
    # Melanoma risk
    melanoma = calculate_melanoma_risk(genotypes, pigment)
    
    return {
        "summary": {
            "estimated_skin_type": skin_type["skin_type"],
            "skin_description": skin_type["description"],
            "burn_risk": skin_type["burn_time_unprotected_min"],
            "recommended_spf": spf["recommended_spf"],
            "vitamin_d_synthesis": vitd["synthesis_capacity"],
            "melanoma_risk": melanoma["risk_level"]
        },
        "pigmentation_analysis": pigment,
        "skin_type_detail": skin_type,
        "spf_recommendation": spf,
        "vitamin_d": vitd,
        "melanoma_risk": melanoma
    }


def generate_uv_report_text(genotypes: Dict[str, str]) -> str:
    """
    Generate plain-English UV sensitivity report.
    """
    report = generate_uv_sensitivity_report(genotypes)
    
    lines = []
    lines.append("☀️ UV SENSITIVITY PROFILE")
    lines.append("=" * 50)
    lines.append("")
    
    summary = report["summary"]
    
    # Skin type
    lines.append(f"🧬 Estimated Skin Type: {summary['estimated_skin_type'].upper()}")
    lines.append(f"   {summary['skin_description']}")
    lines.append(f"   Unprotected burn time: ~{summary['burn_risk']} minutes")
    lines.append("")
    
    # SPF
    spf = report["spf_recommendation"]
    lines.append(f"🧴 SPF RECOMMENDATION: {summary['recommended_spf']}")
    for tip in spf["tips"][:3]:
        lines.append(f"   • {tip}")
    lines.append("")
    
    # Vitamin D
    vitd = report["vitamin_d"]
    lines.append(f"☀️ VITAMIN D SYNTHESIS: {summary['vitamin_d_synthesis'].upper()}")
    lines.append(f"   {vitd['sun_exposure_needed']}")
    if vitd["supplement_recommended"]:
        lines.append("   💊 Supplementation may be beneficial")
    lines.append("")
    
    # Melanoma
    melanoma = report["melanoma_risk"]
    lines.append(f"⚠️ MELANOMA RISK: {summary['melanoma_risk'].upper()}")
    lines.append(f"   {melanoma['description']}")
    lines.append(f"   Screening: {melanoma['screening_recommendation']}")
    
    if melanoma["mc1r_risk_variants"] > 0:
        lines.append(f"   MC1R risk variants: {melanoma['mc1r_risk_variants']}")
    
    return "\n".join(lines)
