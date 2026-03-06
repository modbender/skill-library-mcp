"""
Sleep Optimization Profile v4.1.0
Combines chronotype markers, caffeine metabolism, and adenosine receptor variants
to provide personalized sleep/wake timing recommendations.

Sources:
- GWAS on sleep traits
- Caffeine metabolism studies (CYP1A2)
- Chronotype genetics (CLOCK, PER2, PER3)
- Adenosine receptor studies (ADORA2A)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Chronotype(Enum):
    """Sleep chronotype classifications."""
    DEFINITE_MORNING = "definite_morning"
    MODERATE_MORNING = "moderate_morning"
    INTERMEDIATE = "intermediate"
    MODERATE_EVENING = "moderate_evening"
    DEFINITE_EVENING = "definite_evening"


class CaffeineMetabolism(Enum):
    """Caffeine metabolism speed."""
    ULTRA_SLOW = "ultra_slow"
    SLOW = "slow"
    INTERMEDIATE = "intermediate"
    FAST = "fast"
    ULTRA_FAST = "ultra_fast"


# =============================================================================
# CHRONOTYPE MARKERS
# =============================================================================

CHRONOTYPE_MARKERS = {
    # CLOCK gene - Central circadian pacemaker
    "rs1801260": {
        "gene": "CLOCK",
        "trait": "Chronotype / Sleep Timing",
        "variant": "3111T/C",
        "risk_allele": "C",
        "effect": {
            "TT": "Morning preference tendency",
            "TC": "Intermediate chronotype",
            "CC": "Evening preference tendency, delayed sleep phase risk"
        },
        "weight": 1.5,
        "direction": "evening",  # C pushes toward evening
        "pmid": ["17404220", "12841365"],
        "evidence": "strong"
    },
    "rs2070062": {
        "gene": "CLOCK",
        "trait": "Sleep Duration",
        "risk_allele": "A",
        "effect": {
            "GG": "Average sleep duration",
            "GA": "Slightly shorter sleep",
            "AA": "Shorter sleep duration tendency"
        },
        "weight": 0.8,
        "pmid": ["23166328"]
    },
    
    # PER2 - Period circadian regulator 2
    "rs35333999": {
        "gene": "PER2",
        "trait": "Advanced Sleep Phase",
        "risk_allele": "G",
        "effect": {
            "AA": "Normal sleep timing",
            "AG": "Intermediate",
            "GG": "Strong morning preference, early wake tendency"
        },
        "weight": 2.0,
        "direction": "morning",
        "pmid": ["11232563"],
        "evidence": "strong",
        "note": "Associated with familial advanced sleep phase syndrome"
    },
    "rs2304672": {
        "gene": "PER2",
        "trait": "Sleep Timing",
        "risk_allele": "C",
        "effect": "Associated with sleep phase timing",
        "weight": 0.7,
        "pmid": ["17101883"]
    },
    
    # PER3 - Period circadian regulator 3
    "rs228697": {
        "gene": "PER3",
        "trait": "Chronotype / Sleep Homeostasis",
        "risk_allele": "C",
        "effect": {
            "GG": "Average chronotype",
            "GC": "Intermediate",
            "CC": "Morning preference, sensitive to sleep deprivation"
        },
        "weight": 1.2,
        "direction": "morning",
        "pmid": ["16585790"],
        "evidence": "moderate"
    },
    "rs2797685": {
        "gene": "PER3",
        "trait": "Sleep Duration",
        "risk_allele": "A",
        "effect": "A allele associated with longer sleep duration need",
        "weight": 0.6,
        "pmid": ["23166328"]
    },
    # PER3 VNTR proxy (5/5 vs 4/4 repeat - not directly testable via SNP)
    "rs228729": {
        "gene": "PER3",
        "trait": "Sleep Pressure Sensitivity",
        "risk_allele": "T",
        "effect": {
            "CC": "Less affected by sleep deprivation",
            "CT": "Intermediate",
            "TT": "More sensitive to sleep deprivation, higher sleep pressure"
        },
        "weight": 1.0,
        "pmid": ["17362476"]
    },
    
    # CRY1 - Cryptochrome circadian regulator 1
    "rs8192440": {
        "gene": "CRY1",
        "trait": "Delayed Sleep Phase",
        "risk_allele": "A",
        "effect": {
            "GG": "Normal sleep timing",
            "GA": "Mild delay tendency",
            "AA": "Delayed sleep phase tendency"
        },
        "weight": 1.3,
        "direction": "evening",
        "pmid": ["28252596"],
        "evidence": "moderate"
    },
    
    # CRY2 - Cryptochrome circadian regulator 2
    "rs10838524": {
        "gene": "CRY2",
        "trait": "Chronotype",
        "risk_allele": "A",
        "effect": "Associated with evening chronotype",
        "weight": 0.5,
        "direction": "evening",
        "pmid": ["30696823"]
    },
    
    # ARNTL (BMAL1) - Core clock gene
    "rs7107287": {
        "gene": "ARNTL",
        "trait": "Sleep Timing",
        "risk_allele": "T",
        "effect": "Associated with later sleep timing",
        "weight": 0.6,
        "direction": "evening",
        "pmid": ["23166328"]
    },
    
    # AHR - Aryl hydrocarbon receptor (regulates CLOCK/BMAL1)
    "rs2066853": {
        "gene": "AHR",
        "trait": "Chronotype Modulation",
        "risk_allele": "A",
        "effect": "May modify chronotype expression",
        "weight": 0.4,
        "pmid": ["23166328"]
    },
    
    # MTNR1B - Melatonin receptor 1B
    "rs10830963": {
        "gene": "MTNR1B",
        "trait": "Melatonin Signaling",
        "risk_allele": "G",
        "effect": {
            "CC": "Normal melatonin response",
            "CG": "Intermediate",
            "GG": "Altered melatonin signaling, may need more melatonin"
        },
        "weight": 0.8,
        "pmid": ["19079262"],
        "note": "Also associated with glucose metabolism"
    },
    
    # DRD2 - Dopamine reward (affects sleep motivation)
    "rs1800497": {
        "gene": "DRD2",
        "trait": "Sleep/Wake Drive",
        "variant": "TaqIA",
        "risk_allele": "A",
        "effect": "A1 allele may affect arousal regulation",
        "weight": 0.4,
        "pmid": ["23166328"]
    },
}


# =============================================================================
# CAFFEINE METABOLISM MARKERS
# =============================================================================

CAFFEINE_METABOLISM_MARKERS = {
    # CYP1A2 - Primary caffeine metabolizer
    "rs762551": {
        "gene": "CYP1A2",
        "trait": "Caffeine Metabolism Speed",
        "variant": "*1F",
        "effect_allele": "C",
        "effect": {
            "AA": "Fast caffeine metabolizer (half-life ~3-4 hours)",
            "AC": "Intermediate caffeine metabolizer (half-life ~5-6 hours)",
            "CC": "Slow caffeine metabolizer (half-life ~8-10+ hours)"
        },
        "weight": 3.0,  # Most important marker
        "pmid": ["16522833", "26554680"],
        "evidence": "very_strong",
        "clinical_implications": {
            "AA": {
                "max_daily_mg": 400,
                "cutoff_hours_before_bed": 6,
                "ergogenic_benefit": True,
                "cardiac_risk": "low"
            },
            "AC": {
                "max_daily_mg": 300,
                "cutoff_hours_before_bed": 8,
                "ergogenic_benefit": True,
                "cardiac_risk": "moderate"
            },
            "CC": {
                "max_daily_mg": 200,
                "cutoff_hours_before_bed": 12,
                "ergogenic_benefit": False,
                "cardiac_risk": "elevated"
            }
        }
    },
    "rs12720461": {
        "gene": "CYP1A2",
        "trait": "Caffeine Metabolism",
        "risk_allele": "T",
        "effect": "T allele further slows metabolism",
        "weight": 1.0,
        "pmid": ["26554680"]
    },
    
    # AHR - Regulates CYP1A2 expression
    "rs4410790": {
        "gene": "AHR",
        "trait": "CYP1A2 Inducibility",
        "risk_allele": "T",
        "effect": "Affects CYP1A2 induction - modifies caffeine metabolism",
        "weight": 0.5,
        "pmid": ["21107320"]
    },
}


# =============================================================================
# ADENOSINE RECEPTOR MARKERS
# =============================================================================

ADENOSINE_RECEPTOR_MARKERS = {
    # ADORA2A - Adenosine A2A receptor
    "rs5751876": {
        "gene": "ADORA2A",
        "trait": "Caffeine Sensitivity / Sleep Pressure",
        "variant": "1976C>T",
        "effect_allele": "T",
        "effect": {
            "CC": "Lower caffeine sensitivity, more resilient to sleep deprivation",
            "CT": "Intermediate caffeine sensitivity",
            "TT": "HIGH caffeine sensitivity, sensitive to sleep deprivation"
        },
        "weight": 2.0,
        "pmid": ["16213838", "22080499"],
        "evidence": "strong",
        "clinical_implications": {
            "CC": {
                "caffeine_anxiety_risk": "low",
                "sleep_disruption_risk": "low",
                "note": "May tolerate caffeine closer to bedtime"
            },
            "CT": {
                "caffeine_anxiety_risk": "moderate",
                "sleep_disruption_risk": "moderate"
            },
            "TT": {
                "caffeine_anxiety_risk": "high",
                "sleep_disruption_risk": "high",
                "note": "Caffeine more likely to cause anxiety and insomnia"
            }
        }
    },
    "rs2298383": {
        "gene": "ADORA2A",
        "trait": "Caffeine-Induced Anxiety",
        "risk_allele": "T",
        "effect": "T allele associated with caffeine-induced anxiety",
        "weight": 1.2,
        "pmid": ["22080499"]
    },
    "rs3761422": {
        "gene": "ADORA2A",
        "trait": "Sleep Depth",
        "risk_allele": "A",
        "effect": "Associated with sleep quality",
        "weight": 0.6,
        "pmid": ["22080499"]
    },
    
    # ADORA1 - Adenosine A1 receptor
    "rs5743248": {
        "gene": "ADORA1",
        "trait": "Sleep Drive",
        "risk_allele": "T",
        "effect": "May affect sleep pressure accumulation",
        "weight": 0.4,
        "pmid": ["17362476"]
    },
}


# =============================================================================
# SLEEP DURATION MARKERS
# =============================================================================

SLEEP_DURATION_MARKERS = {
    # DEC2 (BHLHE41) - Short sleep gene
    "rs121912617": {
        "gene": "DEC2",
        "trait": "Natural Short Sleeper",
        "variant": "P384R",
        "risk_allele": "G",
        "effect": {
            "AA": "Normal sleep need (7-9 hours)",
            "AG": "May need slightly less sleep",
            "GG": "Natural short sleeper - can thrive on 4-6 hours"
        },
        "weight": 3.0,
        "pmid": ["19609531"],
        "evidence": "strong",
        "note": "Rare variant. Most people need 7-9 hours."
    },
    
    # ADRB1 - Another short sleep gene
    "rs1801253": {
        "gene": "ADRB1",
        "trait": "Short Sleep",
        "variant": "Arg389Gly",
        "risk_allele": "G",
        "effect": "G allele associated with short sleep phenotype when combined with A187V",
        "weight": 0.8,
        "pmid": ["31473062"]
    },
    
    # PAX8 - Associated with sleep duration
    "rs1823125": {
        "gene": "PAX8",
        "trait": "Sleep Duration",
        "risk_allele": "A",
        "effect": "Associated with sleep duration variation",
        "weight": 0.5,
        "pmid": ["27798627"]
    },
}


# =============================================================================
# COMBINED SLEEP MARKERS
# =============================================================================

SLEEP_MARKERS = {
    **CHRONOTYPE_MARKERS,
    **CAFFEINE_METABOLISM_MARKERS,
    **ADENOSINE_RECEPTOR_MARKERS,
    **SLEEP_DURATION_MARKERS
}


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def determine_chronotype(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Determine chronotype (morning/evening preference) from genetic markers.
    """
    morning_score = 0
    evening_score = 0
    markers_found = []
    confidence_weight = 0
    
    for rsid, info in CHRONOTYPE_MARKERS.items():
        if rsid in genotypes:
            geno = genotypes[rsid]
            weight = info.get("weight", 1.0)
            direction = info.get("direction")
            risk_allele = info.get("risk_allele", "")
            
            markers_found.append({
                "rsid": rsid,
                "gene": info["gene"],
                "genotype": geno,
                "trait": info["trait"]
            })
            
            confidence_weight += weight
            
            # Count risk alleles
            if risk_allele:
                risk_count = geno.upper().count(risk_allele.upper())
                
                if direction == "morning":
                    morning_score += risk_count * weight
                elif direction == "evening":
                    evening_score += risk_count * weight
    
    # Determine chronotype
    net_score = morning_score - evening_score
    
    if net_score > 2:
        chronotype = Chronotype.DEFINITE_MORNING
        description = "Strong morning preference (early bird)"
        ideal_wake = "5:30 - 6:30 AM"
        ideal_sleep = "9:00 - 10:00 PM"
    elif net_score > 0.5:
        chronotype = Chronotype.MODERATE_MORNING
        description = "Moderate morning preference"
        ideal_wake = "6:00 - 7:00 AM"
        ideal_sleep = "10:00 - 11:00 PM"
    elif net_score > -0.5:
        chronotype = Chronotype.INTERMEDIATE
        description = "Intermediate chronotype (flexible)"
        ideal_wake = "6:30 - 7:30 AM"
        ideal_sleep = "10:30 - 11:30 PM"
    elif net_score > -2:
        chronotype = Chronotype.MODERATE_EVENING
        description = "Moderate evening preference"
        ideal_wake = "7:30 - 8:30 AM"
        ideal_sleep = "11:30 PM - 12:30 AM"
    else:
        chronotype = Chronotype.DEFINITE_EVENING
        description = "Strong evening preference (night owl)"
        ideal_wake = "8:30 - 10:00 AM"
        ideal_sleep = "12:30 - 2:00 AM"
    
    return {
        "chronotype": chronotype.value,
        "description": description,
        "morning_score": round(morning_score, 2),
        "evening_score": round(evening_score, 2),
        "net_score": round(net_score, 2),
        "ideal_wake_time": ideal_wake,
        "ideal_sleep_time": ideal_sleep,
        "markers_analyzed": len(markers_found),
        "markers_found": markers_found,
        "confidence": "high" if confidence_weight > 5 else "moderate" if confidence_weight > 2 else "low"
    }


def determine_caffeine_metabolism(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Determine caffeine metabolism speed from CYP1A2 and related markers.
    """
    result = {
        "metabolism_speed": CaffeineMetabolism.INTERMEDIATE.value,
        "cyp1a2_genotype": None,
        "adora2a_sensitivity": None,
        "half_life_estimate": "5-6 hours",
        "max_daily_caffeine_mg": 300,
        "cutoff_before_bed_hours": 8,
        "ergogenic_benefit": True,
        "cardiac_risk": "average",
        "anxiety_risk": "average",
        "markers_found": [],
        "recommendations": []
    }
    
    # Check CYP1A2 rs762551 (main marker)
    cyp1a2_geno = genotypes.get("rs762551")
    if cyp1a2_geno:
        result["cyp1a2_genotype"] = cyp1a2_geno
        result["markers_found"].append({
            "rsid": "rs762551",
            "gene": "CYP1A2",
            "genotype": cyp1a2_geno
        })
        
        marker_info = CAFFEINE_METABOLISM_MARKERS["rs762551"]
        clinical = marker_info["clinical_implications"].get(cyp1a2_geno.upper())
        
        if clinical:
            result["max_daily_caffeine_mg"] = clinical["max_daily_mg"]
            result["cutoff_before_bed_hours"] = clinical["cutoff_hours_before_bed"]
            result["ergogenic_benefit"] = clinical["ergogenic_benefit"]
            result["cardiac_risk"] = clinical["cardiac_risk"]
            
            if cyp1a2_geno.upper() == "AA":
                result["metabolism_speed"] = CaffeineMetabolism.FAST.value
                result["half_life_estimate"] = "3-4 hours"
            elif cyp1a2_geno.upper() == "AC":
                result["metabolism_speed"] = CaffeineMetabolism.INTERMEDIATE.value
                result["half_life_estimate"] = "5-6 hours"
            else:  # CC
                result["metabolism_speed"] = CaffeineMetabolism.SLOW.value
                result["half_life_estimate"] = "8-10+ hours"
    
    # Check ADORA2A rs5751876 (caffeine sensitivity)
    adora2a_geno = genotypes.get("rs5751876")
    if adora2a_geno:
        result["markers_found"].append({
            "rsid": "rs5751876",
            "gene": "ADORA2A",
            "genotype": adora2a_geno
        })
        
        marker_info = ADENOSINE_RECEPTOR_MARKERS["rs5751876"]
        clinical = marker_info["clinical_implications"].get(adora2a_geno.upper())
        
        if clinical:
            result["adora2a_sensitivity"] = adora2a_geno
            result["anxiety_risk"] = clinical["caffeine_anxiety_risk"]
            
            # Adjust cutoff if high sensitivity
            if adora2a_geno.upper() == "TT":
                result["cutoff_before_bed_hours"] = max(
                    result["cutoff_before_bed_hours"],
                    10
                )
                result["max_daily_caffeine_mg"] = min(
                    result["max_daily_caffeine_mg"],
                    200
                )
    
    # Generate recommendations
    if result["metabolism_speed"] == CaffeineMetabolism.SLOW.value:
        result["recommendations"].extend([
            "☕ Limit caffeine to morning only (before 10 AM ideally)",
            "☕ Max 1-2 cups of coffee per day",
            "☕ Consider switching to tea (lower caffeine)",
            "⚠️ Evening caffeine significantly disrupts sleep architecture"
        ])
    elif result["metabolism_speed"] == CaffeineMetabolism.FAST.value:
        result["recommendations"].extend([
            "☕ You can safely consume caffeine later in the day",
            "☕ Caffeine provides good ergogenic benefits for you",
            f"☕ Still aim to stop {result['cutoff_before_bed_hours']} hours before bed"
        ])
    
    if result["anxiety_risk"] == "high":
        result["recommendations"].append(
            "⚠️ You're genetically prone to caffeine-induced anxiety - reduce intake if anxious"
        )
    
    return result


def generate_sleep_profile(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate comprehensive sleep optimization profile.
    """
    chronotype = determine_chronotype(genotypes)
    caffeine = determine_caffeine_metabolism(genotypes)
    
    # Determine sleep duration needs
    sleep_duration = {
        "estimated_need": "7-8 hours",
        "short_sleeper_variant": False
    }
    
    dec2_geno = genotypes.get("rs121912617")
    if dec2_geno and "G" in dec2_geno.upper():
        sleep_duration["short_sleeper_variant"] = True
        sleep_duration["estimated_need"] = "5-6 hours (rare short sleeper gene)"
    
    # Calculate optimal coffee cutoff time
    sleep_time = chronotype["ideal_sleep_time"].split(" - ")[0]
    cutoff_hours = caffeine["cutoff_before_bed_hours"]
    
    # Parse sleep time and calculate cutoff
    if "PM" in sleep_time or "AM" in sleep_time:
        # Simple calculation - approximate
        base_hour = int(sleep_time.split(":")[0])
        if "PM" in sleep_time:
            base_hour += 12 if base_hour != 12 else 0
        elif "AM" in sleep_time and base_hour == 12:
            base_hour = 0
        
        cutoff_hour = (base_hour - cutoff_hours) % 24
        if cutoff_hour < 12:
            coffee_cutoff = f"{cutoff_hour}:00 AM" if cutoff_hour > 0 else "12:00 AM"
        else:
            cutoff_hour = cutoff_hour - 12 if cutoff_hour > 12 else 12
            coffee_cutoff = f"{cutoff_hour}:00 PM"
    else:
        coffee_cutoff = "Early afternoon"
    
    # Generate actionable recommendations
    recommendations = []
    
    # Chronotype-based
    if chronotype["chronotype"] in ["definite_morning", "moderate_morning"]:
        recommendations.append({
            "category": "sleep_timing",
            "priority": "high",
            "recommendation": "Embrace your early bird genetics - schedule demanding tasks in morning",
            "explanation": "Your circadian genes favor morning alertness"
        })
        recommendations.append({
            "category": "light_exposure",
            "priority": "medium",
            "recommendation": "Get bright light exposure within 30 min of waking",
            "explanation": "Reinforces your natural morning rhythm"
        })
    elif chronotype["chronotype"] in ["definite_evening", "moderate_evening"]:
        recommendations.append({
            "category": "sleep_timing",
            "priority": "high",
            "recommendation": "If possible, shift work schedule later - you're a genetic night owl",
            "explanation": "Fighting your chronotype causes chronic sleep debt"
        })
        recommendations.append({
            "category": "light_exposure",
            "priority": "high",
            "recommendation": "Avoid bright/blue light after 8 PM to help sleep onset",
            "explanation": "Evening types are more sensitive to evening light"
        })
    
    # Caffeine-based
    recommendations.append({
        "category": "caffeine",
        "priority": "high",
        "recommendation": f"Stop ALL caffeine by {coffee_cutoff}",
        "explanation": f"Based on your {caffeine['metabolism_speed']} metabolism, caffeine stays active {caffeine['half_life_estimate']}"
    })
    
    if caffeine["anxiety_risk"] == "high":
        recommendations.append({
            "category": "caffeine",
            "priority": "medium",
            "recommendation": "Limit caffeine to 100-200mg if you experience anxiety",
            "explanation": "Your ADORA2A variant makes you sensitive to caffeine's anxiogenic effects"
        })
    
    # General sleep hygiene with genetic context
    recommendations.append({
        "category": "consistency",
        "priority": "high",
        "recommendation": f"Maintain consistent sleep/wake times ({chronotype['ideal_wake_time']} wake, {chronotype['ideal_sleep_time']} sleep)",
        "explanation": "Consistency reinforces circadian rhythms"
    })
    
    return {
        "profile_summary": {
            "chronotype": chronotype["chronotype"],
            "chronotype_description": chronotype["description"],
            "caffeine_metabolism": caffeine["metabolism_speed"],
            "caffeine_half_life": caffeine["half_life_estimate"],
            "sleep_duration_need": sleep_duration["estimated_need"],
            "short_sleeper_gene": sleep_duration["short_sleeper_variant"]
        },
        "optimal_timing": {
            "ideal_wake_time": chronotype["ideal_wake_time"],
            "ideal_sleep_time": chronotype["ideal_sleep_time"],
            "coffee_cutoff_time": coffee_cutoff,
            "max_caffeine_mg": caffeine["max_daily_caffeine_mg"]
        },
        "detailed_analysis": {
            "chronotype": chronotype,
            "caffeine": caffeine,
            "sleep_duration": sleep_duration
        },
        "recommendations": recommendations,
        "markers_analyzed": len(chronotype["markers_found"]) + len(caffeine["markers_found"]),
        "confidence": chronotype["confidence"]
    }


def get_sleep_optimization_summary(genotypes: Dict[str, str]) -> str:
    """
    Generate a plain-English summary of sleep optimization profile.
    """
    profile = generate_sleep_profile(genotypes)
    
    lines = []
    lines.append("🌙 SLEEP OPTIMIZATION PROFILE")
    lines.append("=" * 40)
    lines.append("")
    
    # Chronotype
    lines.append(f"⏰ Chronotype: {profile['profile_summary']['chronotype_description']}")
    lines.append(f"   Best wake time: {profile['optimal_timing']['ideal_wake_time']}")
    lines.append(f"   Best sleep time: {profile['optimal_timing']['ideal_sleep_time']}")
    lines.append("")
    
    # Caffeine
    lines.append(f"☕ Caffeine Metabolism: {profile['profile_summary']['caffeine_metabolism']}")
    lines.append(f"   Half-life: {profile['profile_summary']['caffeine_half_life']}")
    lines.append(f"   Stop caffeine by: {profile['optimal_timing']['coffee_cutoff_time']}")
    lines.append(f"   Max daily: {profile['optimal_timing']['max_caffeine_mg']}mg")
    lines.append("")
    
    # Sleep need
    lines.append(f"😴 Sleep Need: {profile['profile_summary']['sleep_duration_need']}")
    if profile['profile_summary']['short_sleeper_gene']:
        lines.append("   (You carry a rare short sleeper variant!)")
    lines.append("")
    
    # Top recommendations
    lines.append("📋 KEY RECOMMENDATIONS:")
    for rec in profile['recommendations'][:5]:
        lines.append(f"   • {rec['recommendation']}")
    
    return "\n".join(lines)
