"""
Athletic Performance Profiling v4.1.0
Comprehensive genetic analysis for athletic potential, including:
- Endurance vs Power composite
- Recovery markers
- Injury susceptibility
- VO2max potential indicators

Sources:
- GWAS on athletic performance
- Sports genetics literature
- Exercise physiology research
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AthleticType(Enum):
    """Primary athletic profile types."""
    POWER = "power"
    POWER_ENDURANCE = "power_endurance"
    BALANCED = "balanced"
    ENDURANCE_POWER = "endurance_power"
    ENDURANCE = "endurance"


class RecoveryProfile(Enum):
    """Recovery speed classifications."""
    FAST = "fast"
    NORMAL = "normal"
    SLOW = "slow"


class InjuryRisk(Enum):
    """Injury susceptibility levels."""
    LOW = "low"
    AVERAGE = "average"
    ELEVATED = "elevated"
    HIGH = "high"


# =============================================================================
# ENDURANCE vs POWER MARKERS
# =============================================================================

POWER_ENDURANCE_MARKERS = {
    "rs1815739": {
        "gene": "ACTN3",
        "trait": "Muscle Fiber Type (Alpha-Actinin-3)",
        "variant": "R577X",
        "power_allele": "C",
        "endurance_allele": "T",
        "weight": 3.0,  # Strongest marker
        "effects": {
            "CC": {
                "type": "power",
                "score": 2,
                "description": "Full alpha-actinin-3 expression - fast-twitch muscle advantage",
                "athletic_type": "Sprinting, power lifting, explosive sports",
                "elite_athlete_association": "Overrepresented in sprint/power Olympians"
            },
            "CT": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate alpha-actinin-3 - versatile",
                "athletic_type": "Can excel at both power and endurance",
                "elite_athlete_association": "Most common in general athletes"
            },
            "TT": {
                "type": "endurance",
                "score": -2,
                "description": "No alpha-actinin-3 - slow-twitch muscle advantage",
                "athletic_type": "Distance running, cycling, triathlon",
                "elite_athlete_association": "Overrepresented in endurance athletes"
            }
        },
        "pmid": ["21448267", "12879365"],
        "evidence": "very_strong"
    },
    "rs1799752": {
        "gene": "ACE",
        "trait": "ACE I/D Polymorphism",
        "variant": "Insertion/Deletion",
        "power_allele": "D",
        "endurance_allele": "I",
        "weight": 2.5,
        "effects": {
            "II": {
                "type": "endurance",
                "score": -2,
                "description": "Lower ACE activity - endurance advantage",
                "athletic_type": "Long-distance events, high-altitude performance",
                "elite_athlete_association": "Overrepresented in elite endurance athletes"
            },
            "ID": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate ACE activity - versatile",
                "athletic_type": "Middle-distance, mixed sports"
            },
            "DD": {
                "type": "power",
                "score": 2,
                "description": "Higher ACE activity - power/strength advantage",
                "athletic_type": "Sprinting, throwing, strength sports"
            }
        },
        "note": "This marker may appear as rs4646994 or require special genotyping",
        "pmid": ["18043716", "10831086"],
        "evidence": "strong"
    },
    "rs8192678": {
        "gene": "PPARGC1A",
        "trait": "Mitochondrial Biogenesis (PGC-1α)",
        "variant": "Gly482Ser",
        "power_allele": "A",
        "endurance_allele": "G",
        "weight": 2.0,
        "effects": {
            "GG": {
                "type": "endurance",
                "score": -1,
                "description": "Higher PGC-1α activity - better mitochondrial function",
                "athletic_type": "Endurance sports, improved VO2max trainability"
            },
            "GA": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate mitochondrial biogenesis"
            },
            "AA": {
                "type": "power",
                "score": 1,
                "description": "Lower PGC-1α activity",
                "athletic_type": "May need to focus more on aerobic training"
            }
        },
        "pmid": ["14630221"],
        "evidence": "moderate"
    },
    "rs4253778": {
        "gene": "PPARA",
        "trait": "Fat Oxidation / Endurance",
        "power_allele": "C",
        "endurance_allele": "G",
        "weight": 1.5,
        "effects": {
            "GG": {
                "type": "endurance",
                "score": -1,
                "description": "Higher PPAR-alpha - better fat oxidation"
            },
            "GC": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate"
            },
            "CC": {
                "type": "power",
                "score": 1,
                "description": "Lower PPAR-alpha activity"
            }
        },
        "pmid": ["17021617"],
        "evidence": "moderate"
    },
    "rs2016520": {
        "gene": "PPARD",
        "trait": "PPAR-delta / Endurance Capacity",
        "power_allele": "T",
        "endurance_allele": "C",
        "weight": 1.5,
        "effects": {
            "CC": {
                "type": "endurance",
                "score": -1,
                "description": "Higher PPAR-delta - improved endurance capacity"
            },
            "CT": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate"
            },
            "TT": {
                "type": "power",
                "score": 1,
                "description": "Lower PPAR-delta activity"
            }
        },
        "pmid": ["22310492"],
        "evidence": "moderate"
    },
    "rs1042713": {
        "gene": "ADRB2",
        "trait": "Beta-2 Adrenergic Receptor",
        "power_allele": "A",
        "endurance_allele": "G",
        "weight": 1.0,
        "effects": {
            "GG": {
                "type": "endurance",
                "score": -0.5,
                "description": "Better bronchodilation during exercise"
            },
            "GA": {
                "type": "balanced",
                "score": 0,
                "description": "Intermediate"
            },
            "AA": {
                "type": "power",
                "score": 0.5,
                "description": "May have different response to exercise stress"
            }
        },
        "pmid": ["16046713"],
        "evidence": "weak"
    }
}


# =============================================================================
# VO2MAX MARKERS
# =============================================================================

VO2MAX_MARKERS = {
    "rs8192678": {  # Also in power/endurance
        "gene": "PPARGC1A",
        "trait": "VO2max Trainability",
        "effect_allele": "G",
        "effect": {
            "GG": {"vo2max_potential": "high", "trainability": "excellent"},
            "GA": {"vo2max_potential": "moderate", "trainability": "good"},
            "AA": {"vo2max_potential": "lower_ceiling", "trainability": "requires more work"}
        },
        "pmid": ["14630221"]
    },
    "rs699": {
        "gene": "AGT",
        "trait": "Angiotensinogen / VO2max",
        "variant": "M235T",
        "effect_allele": "C",
        "effect": {
            "TT": {"vo2max_potential": "lower", "note": "Lower trainability"},
            "CT": {"vo2max_potential": "moderate"},
            "CC": {"vo2max_potential": "higher", "note": "Better aerobic adaptations"}
        },
        "pmid": ["10499831"]
    },
    "rs7181866": {
        "gene": "VEGFA",
        "trait": "Angiogenesis / Capillary Density",
        "effect_allele": "A",
        "effect": {
            "beneficial": "A allele associated with better vascular adaptations"
        },
        "pmid": ["19225459"]
    },
    "rs660339": {
        "gene": "UCP2",
        "trait": "Metabolic Efficiency",
        "effect_allele": "T",
        "effect": {
            "beneficial": "May affect energy efficiency during exercise"
        },
        "pmid": ["17047610"]
    },
    "rs2070744": {
        "gene": "NOS3",
        "trait": "Nitric Oxide / Blood Flow",
        "variant": "-786T>C",
        "effect_allele": "T",
        "effect": {
            "TT": {"blood_flow": "higher", "note": "Better NO production for vasodilation"},
            "CT": {"blood_flow": "intermediate"},
            "CC": {"blood_flow": "reduced", "note": "May affect oxygen delivery"}
        },
        "pmid": ["16199905"]
    }
}


# =============================================================================
# RECOVERY MARKERS
# =============================================================================

RECOVERY_MARKERS = {
    "rs1800629": {
        "gene": "TNF",
        "trait": "TNF-alpha / Inflammation",
        "variant": "-308 G>A",
        "risk_allele": "A",
        "weight": 2.0,
        "effects": {
            "GG": {
                "recovery": "fast",
                "score": 1,
                "description": "Lower TNF-alpha production - faster recovery",
                "recommendation": "Normal recovery protocols should work well"
            },
            "GA": {
                "recovery": "normal",
                "score": 0,
                "description": "Intermediate TNF-alpha",
                "recommendation": "Standard recovery practices"
            },
            "AA": {
                "recovery": "slow",
                "score": -2,
                "description": "Higher TNF-alpha production - more inflammation",
                "recommendation": "Prioritize recovery: more rest between hard sessions, anti-inflammatory nutrition"
            }
        },
        "pmid": ["18511847"],
        "evidence": "moderate"
    },
    "rs1800795": {
        "gene": "IL6",
        "trait": "Interleukin-6 / Inflammation",
        "variant": "-174 G>C",
        "risk_allele": "C",
        "weight": 1.5,
        "effects": {
            "GG": {
                "recovery": "normal",
                "score": 0,
                "description": "Lower IL-6 production"
            },
            "GC": {
                "recovery": "normal",
                "score": 0,
                "description": "Intermediate IL-6"
            },
            "CC": {
                "recovery": "slow",
                "score": -1,
                "description": "Higher IL-6 production - more exercise-induced inflammation",
                "recommendation": "May need longer recovery between intense sessions"
            }
        },
        "pmid": ["16227966"],
        "evidence": "moderate"
    },
    "rs6265": {
        "gene": "BDNF",
        "trait": "Brain-Derived Neurotrophic Factor",
        "variant": "Val66Met",
        "effect_allele": "T",
        "weight": 1.0,
        "effects": {
            "CC": {
                "recovery": "normal",
                "score": 0,
                "description": "Val/Val - normal BDNF",
                "neuro_recovery": "Standard"
            },
            "CT": {
                "recovery": "normal",
                "score": 0.5,
                "description": "Val/Met - exercise may provide MORE cognitive benefit",
                "neuro_recovery": "Exercise is especially neuroprotective for you"
            },
            "TT": {
                "recovery": "normal",
                "score": 1,
                "description": "Met/Met - lower baseline BDNF",
                "neuro_recovery": "Exercise is VERY important - compensates for lower baseline BDNF",
                "recommendation": "Prioritize regular exercise for brain health"
            }
        },
        "pmid": ["14976042"],
        "evidence": "strong"
    },
    "rs2069762": {
        "gene": "IL2",
        "trait": "Immune Recovery",
        "risk_allele": "T",
        "weight": 0.8,
        "effects": {
            "beneficial": "Affects immune recovery after exercise"
        },
        "pmid": ["17628000"]
    },
    "rs1801131": {
        "gene": "MTHFR",
        "trait": "Methylation / Recovery",
        "variant": "A1298C",
        "risk_allele": "G",
        "weight": 0.5,
        "effects": {
            "note": "Homocysteine levels affect recovery and inflammation"
        }
    }
}


# =============================================================================
# INJURY SUSCEPTIBILITY MARKERS
# =============================================================================

INJURY_MARKERS = {
    "rs12722": {
        "gene": "COL5A1",
        "trait": "Tendon/Ligament Structure",
        "variant": "BstUI RFLP",
        "risk_allele": "T",
        "weight": 2.0,
        "injury_type": "Achilles tendinopathy, soft tissue",
        "effects": {
            "CC": {
                "risk": "low",
                "score": 0,
                "description": "Normal collagen structure"
            },
            "CT": {
                "risk": "average",
                "score": -0.5,
                "description": "Intermediate tendon injury risk"
            },
            "TT": {
                "risk": "elevated",
                "score": -1.5,
                "description": "Increased Achilles tendinopathy and soft tissue injury risk",
                "recommendation": "Gradual training progression, eccentric exercises, proper warm-up"
            }
        },
        "pmid": ["19700405", "20696082"],
        "evidence": "strong"
    },
    "rs1800012": {
        "gene": "COL1A1",
        "trait": "Bone/Soft Tissue",
        "variant": "Sp1 binding site",
        "risk_allele": "T",
        "weight": 1.5,
        "injury_type": "ACL, bone stress",
        "effects": {
            "GG": {
                "risk": "low",
                "score": 0,
                "description": "Normal collagen type 1"
            },
            "GT": {
                "risk": "average",
                "score": -0.5,
                "description": "Intermediate"
            },
            "TT": {
                "risk": "elevated",
                "score": -1,
                "description": "Increased ACL and ligament injury risk",
                "recommendation": "Neuromuscular training, proprioception work, landing mechanics"
            }
        },
        "pmid": ["19700405"],
        "evidence": "moderate"
    },
    "rs143383": {
        "gene": "GDF5",
        "trait": "Joint/Cartilage Health",
        "risk_allele": "T",
        "weight": 1.5,
        "injury_type": "Osteoarthritis, joint",
        "effects": {
            "CC": {
                "risk": "low",
                "score": 0,
                "description": "Lower osteoarthritis risk"
            },
            "CT": {
                "risk": "average",
                "score": -0.5,
                "description": "Intermediate joint health"
            },
            "TT": {
                "risk": "elevated",
                "score": -1,
                "description": "Increased osteoarthritis risk",
                "recommendation": "Joint-friendly training, maintain healthy weight, glucosamine/collagen may help"
            }
        },
        "pmid": ["18927265"],
        "evidence": "moderate"
    },
    "rs35068180": {
        "gene": "MMP3",
        "trait": "Achilles Tendinopathy",
        "risk_allele": "5A",  # Repeat polymorphism
        "weight": 1.0,
        "injury_type": "Tendon",
        "effects": {
            "note": "5A/5A genotype associated with higher tendinopathy risk"
        },
        "pmid": ["15976169"],
        "evidence": "moderate"
    },
    "rs679620": {
        "gene": "MMP3",
        "trait": "Disc Degeneration",
        "risk_allele": "A",
        "weight": 0.8,
        "injury_type": "Spinal",
        "effects": {
            "AA": {
                "risk": "elevated",
                "description": "Higher disc degeneration risk",
                "recommendation": "Core strengthening, avoid excessive spinal loading"
            }
        },
        "pmid": ["17194260"],
        "evidence": "moderate"
    },
    "rs1107946": {
        "gene": "COL1A1",
        "trait": "Cruciate Ligament Risk",
        "risk_allele": "T",
        "weight": 1.0,
        "injury_type": "ACL",
        "effects": {
            "note": "Associated with ACL injury susceptibility"
        },
        "pmid": ["19700405"],
        "evidence": "moderate"
    }
}


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_athletic_profile(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate comprehensive athletic profile from genetic markers.
    """
    # Power vs Endurance Score
    power_score = 0
    endurance_score = 0
    power_markers_found = []
    power_weight_sum = 0
    
    for rsid, info in POWER_ENDURANCE_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            weight = info.get("weight", 1.0)
            power_weight_sum += weight
            
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("score", 0) * weight
                
                if effect["type"] == "power":
                    power_score += abs(score)
                elif effect["type"] == "endurance":
                    endurance_score += abs(score)
                
                power_markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "type": effect["type"],
                    "score": score,
                    "description": effect.get("description", ""),
                    "athletic_type": effect.get("athletic_type", "")
                })
    
    # Determine athletic type
    net_score = power_score - endurance_score
    if net_score > 3:
        athletic_type = AthleticType.POWER
        type_description = "Strong power/sprint genetics"
    elif net_score > 1:
        athletic_type = AthleticType.POWER_ENDURANCE
        type_description = "Power-leaning with some endurance capacity"
    elif net_score > -1:
        athletic_type = AthleticType.BALANCED
        type_description = "Balanced - versatile across sports"
    elif net_score > -3:
        athletic_type = AthleticType.ENDURANCE_POWER
        type_description = "Endurance-leaning with some power capacity"
    else:
        athletic_type = AthleticType.ENDURANCE
        type_description = "Strong endurance genetics"
    
    # Recovery Profile
    recovery_score = 0
    recovery_markers_found = []
    recovery_weight_sum = 0
    
    for rsid, info in RECOVERY_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            weight = info.get("weight", 1.0)
            recovery_weight_sum += weight
            
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("score", 0) * weight
                recovery_score += score
                
                recovery_markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "recovery": effect.get("recovery", "normal"),
                    "description": effect.get("description", ""),
                    "recommendation": effect.get("recommendation", "")
                })
    
    if recovery_score > 1:
        recovery_profile = RecoveryProfile.FAST
        recovery_description = "Fast recovery - can handle higher training frequency"
    elif recovery_score > -1:
        recovery_profile = RecoveryProfile.NORMAL
        recovery_description = "Normal recovery - standard training protocols"
    else:
        recovery_profile = RecoveryProfile.SLOW
        recovery_description = "Slower recovery - prioritize rest and anti-inflammatory nutrition"
    
    # Injury Risk Profile
    injury_score = 0
    injury_markers_found = []
    injury_concerns = []
    
    for rsid, info in INJURY_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            
            if "effects" in info and geno_upper in info["effects"]:
                effect = info["effects"][geno_upper]
                score = effect.get("score", 0)
                injury_score += score
                
                injury_markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "injury_type": info.get("injury_type", "general"),
                    "risk": effect.get("risk", "unknown"),
                    "description": effect.get("description", ""),
                    "recommendation": effect.get("recommendation", "")
                })
                
                if effect.get("risk") in ["elevated", "high"]:
                    injury_concerns.append({
                        "area": info.get("injury_type", "general"),
                        "gene": info["gene"],
                        "recommendation": effect.get("recommendation", "")
                    })
    
    if injury_score > -1:
        injury_risk = InjuryRisk.LOW
        injury_description = "Lower than average genetic injury risk"
    elif injury_score > -2:
        injury_risk = InjuryRisk.AVERAGE
        injury_description = "Average genetic injury risk"
    elif injury_score > -4:
        injury_risk = InjuryRisk.ELEVATED
        injury_description = "Elevated injury risk - preventive strategies important"
    else:
        injury_risk = InjuryRisk.HIGH
        injury_description = "Higher injury susceptibility - careful progression essential"
    
    # VO2max Potential
    vo2max_findings = []
    for rsid, info in VO2MAX_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            if "effect" in info and geno_upper in info["effect"]:
                vo2max_findings.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    **info["effect"][geno_upper]
                })
    
    return {
        "athletic_type": {
            "type": athletic_type.value,
            "description": type_description,
            "power_score": round(power_score, 2),
            "endurance_score": round(endurance_score, 2),
            "net_score": round(net_score, 2),
            "markers_analyzed": len(power_markers_found),
            "markers": power_markers_found,
            "confidence": "high" if power_weight_sum > 6 else "moderate" if power_weight_sum > 3 else "low"
        },
        "recovery_profile": {
            "type": recovery_profile.value,
            "description": recovery_description,
            "score": round(recovery_score, 2),
            "markers_analyzed": len(recovery_markers_found),
            "markers": recovery_markers_found
        },
        "injury_risk": {
            "level": injury_risk.value,
            "description": injury_description,
            "score": round(injury_score, 2),
            "markers_analyzed": len(injury_markers_found),
            "markers": injury_markers_found,
            "concerns": injury_concerns
        },
        "vo2max_potential": {
            "markers_found": len(vo2max_findings),
            "findings": vo2max_findings
        }
    }


def generate_training_recommendations(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate personalized training recommendations based on athletic profile.
    """
    recommendations = []
    
    athletic_type = profile["athletic_type"]["type"]
    recovery = profile["recovery_profile"]["type"]
    injury_risk = profile["injury_risk"]["level"]
    
    # Athletic type recommendations
    if athletic_type == "power":
        recommendations.append({
            "category": "training_style",
            "priority": "high",
            "recommendation": "Your genetics favor explosive, power-based training",
            "details": [
                "Strength training (heavy, low-rep) plays to your strengths",
                "Plyometrics and speed work will be effective",
                "Sprint intervals over long steady-state cardio",
                "Sports: sprinting, weightlifting, football, jumping events"
            ]
        })
    elif athletic_type == "endurance":
        recommendations.append({
            "category": "training_style",
            "priority": "high",
            "recommendation": "Your genetics favor endurance activities",
            "details": [
                "Aerobic base building is your strength",
                "Can handle higher volume training",
                "Marathon, cycling, triathlon, rowing suit your profile",
                "Include some strength work for injury prevention"
            ]
        })
    else:
        recommendations.append({
            "category": "training_style",
            "priority": "high",
            "recommendation": "Balanced genetics - versatile across sport types",
            "details": [
                "Can train both power and endurance effectively",
                "Good for mixed sports (soccer, basketball, CrossFit)",
                "Periodize between strength and endurance phases",
                "Find what you enjoy - you can succeed at many activities"
            ]
        })
    
    # Recovery recommendations
    if recovery == "slow":
        recommendations.append({
            "category": "recovery",
            "priority": "high",
            "recommendation": "Your genetics indicate slower recovery - prioritize rest",
            "details": [
                "Allow 48-72 hours between intense sessions",
                "Sleep 8+ hours for optimal recovery",
                "Anti-inflammatory foods: fatty fish, berries, turmeric",
                "Consider recovery modalities: massage, cold exposure",
                "Don't stack hard days back-to-back"
            ]
        })
    elif recovery == "fast":
        recommendations.append({
            "category": "recovery",
            "priority": "medium",
            "recommendation": "Your genetics support faster recovery",
            "details": [
                "Can handle higher training frequency",
                "Still don't neglect recovery completely",
                "Can potentially train same muscle groups more frequently"
            ]
        })
    
    # Injury prevention
    concerns = profile["injury_risk"]["concerns"]
    if concerns:
        injury_recs = []
        for concern in concerns:
            if concern["recommendation"]:
                injury_recs.append(concern["recommendation"])
        
        if injury_recs:
            recommendations.append({
                "category": "injury_prevention",
                "priority": "high",
                "recommendation": "Address specific injury vulnerabilities",
                "details": injury_recs
            })
    
    if injury_risk in ["elevated", "high"]:
        recommendations.append({
            "category": "injury_prevention",
            "priority": "high",
            "recommendation": "General injury prevention is critical for your profile",
            "details": [
                "Gradual progression (10% rule for volume increases)",
                "Thorough warm-up before every session",
                "Address mobility limitations",
                "Don't train through pain",
                "Consider working with a physical therapist"
            ]
        })
    
    return recommendations


def generate_athletic_report(genotypes: Dict[str, str]) -> str:
    """
    Generate plain-English athletic profile report.
    """
    profile = calculate_athletic_profile(genotypes)
    recommendations = generate_training_recommendations(profile)
    
    lines = []
    lines.append("🏃 ATHLETIC GENETIC PROFILE")
    lines.append("=" * 50)
    lines.append("")
    
    # Athletic Type
    at = profile["athletic_type"]
    lines.append("💪 POWER vs ENDURANCE")
    lines.append(f"   Type: {at['description']}")
    lines.append(f"   Power Score: {at['power_score']} | Endurance Score: {at['endurance_score']}")
    lines.append(f"   Confidence: {at['confidence']}")
    lines.append("")
    
    # Key genetic markers
    if at["markers"]:
        lines.append("   Key Markers:")
        for m in at["markers"][:3]:
            lines.append(f"   • {m['gene']} ({m['genotype']}): {m['description'][:50]}...")
    lines.append("")
    
    # Recovery
    rec = profile["recovery_profile"]
    lines.append("⚡ RECOVERY PROFILE")
    lines.append(f"   {rec['description']}")
    lines.append("")
    
    # Injury Risk
    inj = profile["injury_risk"]
    lines.append("🩹 INJURY SUSCEPTIBILITY")
    lines.append(f"   Risk Level: {inj['level'].upper()}")
    lines.append(f"   {inj['description']}")
    if inj["concerns"]:
        lines.append("   Areas of Concern:")
        for c in inj["concerns"]:
            lines.append(f"   • {c['area']}: {c['gene']}")
    lines.append("")
    
    # Training Recommendations
    lines.append("-" * 50)
    lines.append("📋 TRAINING RECOMMENDATIONS")
    lines.append("-" * 50)
    for rec in recommendations:
        lines.append(f"\n{rec['recommendation']}")
        for detail in rec["details"][:3]:
            lines.append(f"   • {detail}")
    
    return "\n".join(lines)


def get_sport_suitability(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Get sport suitability scores based on genetic profile.
    """
    profile = calculate_athletic_profile(genotypes)
    
    # Sport categories
    sports = {
        "power_sports": {
            "name": "Power/Sprint Sports",
            "examples": ["100m sprint", "Weightlifting", "Shot put", "Long jump"],
            "requirements": ["power"],
            "score": 0
        },
        "endurance_sports": {
            "name": "Endurance Sports",
            "examples": ["Marathon", "Triathlon", "Cycling", "Rowing"],
            "requirements": ["endurance"],
            "score": 0
        },
        "mixed_sports": {
            "name": "Mixed/Team Sports",
            "examples": ["Soccer", "Basketball", "Rugby", "Tennis"],
            "requirements": ["balanced"],
            "score": 0
        },
        "combat_sports": {
            "name": "Combat Sports",
            "examples": ["Boxing", "MMA", "Wrestling", "Judo"],
            "requirements": ["power", "recovery"],
            "score": 0
        },
        "skill_sports": {
            "name": "Skill-Based Sports",
            "examples": ["Golf", "Archery", "Shooting", "Curling"],
            "requirements": [],  # Less dependent on these markers
            "score": 50  # Baseline
        }
    }
    
    athletic_type = profile["athletic_type"]["type"]
    recovery = profile["recovery_profile"]["type"]
    injury_risk = profile["injury_risk"]["level"]
    
    # Score power sports
    if athletic_type in ["power", "power_endurance"]:
        sports["power_sports"]["score"] = 80 if athletic_type == "power" else 65
        sports["combat_sports"]["score"] += 40
    
    # Score endurance sports
    if athletic_type in ["endurance", "endurance_power"]:
        sports["endurance_sports"]["score"] = 80 if athletic_type == "endurance" else 65
    
    # Score mixed sports
    if athletic_type == "balanced":
        sports["mixed_sports"]["score"] = 70
    elif athletic_type in ["power_endurance", "endurance_power"]:
        sports["mixed_sports"]["score"] = 75
    
    # Modify by recovery
    if recovery == "fast":
        for cat in ["power_sports", "combat_sports", "mixed_sports"]:
            sports[cat]["score"] += 10
    elif recovery == "slow":
        sports["endurance_sports"]["score"] += 5  # Can train more moderately
    
    # Modify by injury risk
    if injury_risk in ["elevated", "high"]:
        sports["combat_sports"]["score"] -= 15
        sports["power_sports"]["score"] -= 5
    
    # Normalize scores
    for sport in sports.values():
        sport["score"] = max(0, min(100, sport["score"]))
    
    # Sort by score
    sorted_sports = sorted(sports.items(), key=lambda x: x[1]["score"], reverse=True)
    
    return {
        "top_categories": [
            {
                "category": s[1]["name"],
                "score": s[1]["score"],
                "examples": s[1]["examples"]
            }
            for s in sorted_sports[:3]
        ],
        "all_categories": sports
    }
