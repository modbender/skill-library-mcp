"""
Dietary Interaction Matrix v4.1.0
Maps genetic variants to specific food/nutrient interactions and recommendations.

Categories:
- Caffeine metabolism (CYP1A2)
- Alcohol processing (ADH1B/ALDH2)
- Saturated fat response (APOE)
- Lactose tolerance (LCT)
- Gluten sensitivity (HLA-DQ)
- Bitter taste perception (TAS2R38)
- Additional nutrient interactions

Sources:
- GWAS on nutrigenomics
- PharmGKB dietary factors
- Clinical literature
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class ToleranceLevel(Enum):
    """Tolerance/sensitivity levels for foods."""
    EXCELLENT = "excellent"      # No issues, may have benefits
    GOOD = "good"               # Normal tolerance
    MODERATE = "moderate"       # Some caution advised
    POOR = "poor"              # Significant issues likely
    VERY_POOR = "very_poor"    # Avoid or severely limit


class RecommendationStrength(Enum):
    """Strength of dietary recommendation."""
    STRONG = "strong"           # Clear genetic evidence
    MODERATE = "moderate"       # Good evidence
    WEAK = "weak"              # Suggestive evidence


# =============================================================================
# DIETARY INTERACTION MARKERS
# =============================================================================

CAFFEINE_DIET_MARKERS = {
    "rs762551": {
        "gene": "CYP1A2",
        "trait": "Caffeine Metabolism",
        "effect_allele": "C",
        "interactions": {
            "AA": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Fast caffeine metabolizer",
                "daily_limit_mg": 400,
                "recommendations": [
                    "Can enjoy coffee without significant health concerns",
                    "Caffeine provides ergogenic benefits for exercise",
                    "May still affect sleep if consumed late"
                ],
                "foods_to_enjoy": ["coffee", "tea", "dark chocolate"],
                "cardiac_risk": "low"
            },
            "AC": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Intermediate caffeine metabolizer",
                "daily_limit_mg": 300,
                "recommendations": [
                    "Moderate coffee consumption (2-3 cups max)",
                    "Stop caffeine 8+ hours before bed",
                    "May have modest cardiac risk at high intake"
                ],
                "foods_to_enjoy": ["tea (lower caffeine)", "decaf options"],
                "cardiac_risk": "moderate"
            },
            "CC": {
                "tolerance": ToleranceLevel.POOR,
                "description": "Slow caffeine metabolizer",
                "daily_limit_mg": 200,
                "recommendations": [
                    "Limit coffee to 1-2 cups per day maximum",
                    "Strong association with hypertension at >3 cups/day",
                    "Consider decaf or tea",
                    "Stop caffeine before noon for good sleep"
                ],
                "foods_to_limit": ["coffee", "energy drinks", "pre-workout supplements"],
                "cardiac_risk": "elevated"
            }
        },
        "pmid": ["16522833", "26554680"]
    }
}

ALCOHOL_DIET_MARKERS = {
    "rs1229984": {
        "gene": "ADH1B",
        "trait": "Alcohol Metabolism - First Step",
        "effect_allele": "T",
        "interactions": {
            "CC": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Normal alcohol metabolism",
                "recommendations": [
                    "Standard alcohol guidelines apply",
                    "Women: ≤1 drink/day, Men: ≤2 drinks/day"
                ]
            },
            "CT": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Fast alcohol to acetaldehyde conversion",
                "recommendations": [
                    "May feel effects faster",
                    "Paradoxically protective against alcoholism",
                    "Flushing possible"
                ]
            },
            "TT": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Very fast alcohol metabolism",
                "recommendations": [
                    "Alcohol converted to acetaldehyde very quickly",
                    "Unpleasant flushing reaction possible",
                    "Lower alcoholism risk but if you drink, more acetaldehyde exposure"
                ]
            }
        },
        "pmid": ["19624168"]
    },
    "rs671": {
        "gene": "ALDH2",
        "trait": "Alcohol Metabolism - Second Step (Acetaldehyde clearance)",
        "effect_allele": "A",
        "interactions": {
            "GG": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Normal acetaldehyde clearance",
                "recommendations": [
                    "Can metabolize acetaldehyde normally",
                    "Standard alcohol guidelines apply"
                ]
            },
            "GA": {
                "tolerance": ToleranceLevel.POOR,
                "description": "Impaired acetaldehyde clearance - ASIAN FLUSH",
                "recommendations": [
                    "⚠️ SIGNIFICANT flush reaction to alcohol",
                    "Acetaldehyde (carcinogen) accumulates",
                    "STRONGLY limit alcohol - esophageal cancer risk 6-10x higher if drinking",
                    "Do not 'push through' the flush"
                ],
                "health_risks": ["esophageal cancer", "head/neck cancer"],
                "foods_to_avoid": ["alcohol", "fermented foods (may worsen)"]
            },
            "AA": {
                "tolerance": ToleranceLevel.VERY_POOR,
                "description": "Cannot clear acetaldehyde - AVOID ALCOHOL",
                "recommendations": [
                    "🚫 AVOID ALCOHOL completely",
                    "Severe flushing, nausea, rapid heartbeat",
                    "Cannot safely consume alcohol",
                    "Even small amounts cause significant reaction"
                ],
                "foods_to_avoid": ["all alcoholic beverages"],
                "health_risks": ["severe acetaldehyde toxicity"]
            }
        },
        "pmid": ["19624168", "16971766"],
        "note": "Very common in East Asian populations (~30-50% carry A allele)"
    }
}

SATURATED_FAT_MARKERS = {
    "rs429358": {
        "gene": "APOE",
        "trait": "APOE ε4 - Saturated Fat Response",
        "effect_allele": "C",
        "note": "Must combine with rs7412 to determine APOE genotype",
        "dietary_context": "APOE genotype affects response to dietary saturated fat"
    },
    "rs7412": {
        "gene": "APOE",
        "trait": "APOE Genotype Component",
        "effect_allele": "T",
        "note": "Must combine with rs429358"
    },
    "rs5082": {
        "gene": "APOA2",
        "trait": "Saturated Fat and BMI",
        "effect_allele": "C",
        "interactions": {
            "TT": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Normal saturated fat response",
                "recommendations": [
                    "Saturated fat intake less strongly associated with BMI",
                    "Still follow general healthy fat guidelines"
                ]
            },
            "TC": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Intermediate saturated fat sensitivity",
                "recommendations": [
                    "Moderate saturated fat (~20-25g/day) reasonable"
                ]
            },
            "CC": {
                "tolerance": ToleranceLevel.POOR,
                "description": "High saturated fat = higher BMI/obesity risk",
                "recommendations": [
                    "⚠️ Strong gene-diet interaction for weight",
                    "Keep saturated fat <15g/day",
                    "Replace with unsaturated fats (olive oil, avocado, nuts)",
                    "Higher weight gain with high saturated fat diet"
                ],
                "foods_to_limit": ["butter", "red meat", "cheese", "coconut oil", "palm oil"],
                "foods_to_enjoy": ["olive oil", "avocado", "nuts", "fish"]
            }
        },
        "pmid": ["19939984", "24760145"]
    }
}

LACTOSE_MARKERS = {
    "rs4988235": {
        "gene": "LCT",
        "trait": "Lactase Persistence",
        "effect_allele": "A",
        "interactions": {
            "AA": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Lactase persistent - full dairy tolerance",
                "recommendations": [
                    "Can digest lactose throughout life",
                    "Dairy is a good calcium source for you",
                    "No need to avoid dairy products"
                ],
                "foods_to_enjoy": ["milk", "cheese", "yogurt", "ice cream"]
            },
            "GA": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Likely lactase persistent",
                "recommendations": [
                    "Most likely can digest lactose well",
                    "Dairy should be well tolerated",
                    "Watch for any GI symptoms"
                ],
                "foods_to_enjoy": ["dairy products"]
            },
            "GG": {
                "tolerance": ToleranceLevel.POOR,
                "description": "Lactase non-persistent - lactose intolerant",
                "recommendations": [
                    "⚠️ Cannot efficiently digest lactose",
                    "Dairy may cause bloating, gas, diarrhea",
                    "Use lactase enzyme supplements with dairy",
                    "Choose lactose-free or fermented dairy",
                    "Ensure adequate calcium from other sources"
                ],
                "foods_to_limit": ["milk", "soft cheeses", "ice cream"],
                "foods_to_enjoy": ["hard aged cheeses (low lactose)", "lactose-free milk", "yogurt (partial digestion)", "plant milks"],
                "alternative_calcium": ["fortified plant milks", "leafy greens", "tofu", "sardines"]
            }
        },
        "pmid": ["12185609"],
        "note": "European allele (A) confers lactase persistence. Different variants exist in other populations."
    },
    "rs182549": {
        "gene": "MCM6",
        "trait": "Lactase Persistence (enhancer)",
        "effect_allele": "T",
        "note": "Another marker for lactase persistence, common in Europeans"
    }
}

GLUTEN_SENSITIVITY_MARKERS = {
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "trait": "Celiac Disease - HLA-DQ2",
        "effect_allele": "T",
        "interactions": {
            "CC": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Low celiac disease genetic risk",
                "recommendations": [
                    "HLA-DQ2 negative",
                    "Celiac disease extremely unlikely (<0.1% if both DQ2 and DQ8 negative)",
                    "Gluten-free diet not necessary unless other sensitivity"
                ],
                "foods_to_enjoy": ["wheat", "barley", "rye", "whole grains"]
            },
            "CT": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "One copy HLA-DQ2 - intermediate celiac risk",
                "recommendations": [
                    "~3% lifetime celiac risk with one copy",
                    "Watch for symptoms: GI issues, fatigue, anemia, skin rash",
                    "If symptomatic, get tested for celiac (antibodies + biopsy)",
                    "Gluten is fine unless diagnosed with celiac"
                ],
                "note": "Presence of HLA-DQ2/DQ8 is necessary but not sufficient for celiac"
            },
            "TT": {
                "tolerance": ToleranceLevel.POOR,
                "description": "Homozygous HLA-DQ2 - highest celiac risk",
                "recommendations": [
                    "⚠️ Highest genetic risk for celiac disease",
                    "~10-15% lifetime risk if both DQ2 copies",
                    "Get screened if any symptoms",
                    "Consider periodic celiac screening even without symptoms",
                    "Do NOT go gluten-free before testing (masks diagnosis)"
                ],
                "symptoms_to_watch": ["chronic diarrhea", "bloating", "weight loss", "fatigue", "anemia", "dermatitis herpetiformis"],
                "foods_to_potentially_avoid_if_celiac": ["wheat", "barley", "rye", "cross-contaminated oats"]
            }
        },
        "pmid": ["24011413"],
        "note": "HLA-DQ2.5 is necessary for celiac disease but ~25% of population carries it"
    },
    "rs7454108": {
        "gene": "HLA-DQ8",
        "trait": "Celiac Disease - HLA-DQ8",
        "effect_allele": "C",
        "interactions": {
            "TT": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "No HLA-DQ8"
            },
            "TC": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "One copy HLA-DQ8",
                "recommendations": [
                    "Intermediate celiac risk",
                    "If DQ2 also negative, still <5% risk"
                ]
            },
            "CC": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Homozygous HLA-DQ8",
                "recommendations": [
                    "Elevated celiac risk",
                    "DQ8 alone sufficient for celiac in some cases"
                ]
            }
        },
        "pmid": ["24011413"]
    }
}

BITTER_TASTE_MARKERS = {
    "rs713598": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste Perception (PTC/PROP)",
        "effect_allele": "C",
        "note": "Must combine with rs1726866 and rs10246939 for full phenotype"
    },
    "rs1726866": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste Perception",
        "effect_allele": "A",
        "combined_phenotype": True
    },
    "rs10246939": {
        "gene": "TAS2R38",
        "trait": "Bitter Taste Perception",
        "effect_allele": "C",
        "interactions": {
            "CC": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Strong bitter taster - supertaster likely",
                "recommendations": [
                    "May find cruciferous vegetables very bitter",
                    "May dislike black coffee, grapefruit, dark chocolate",
                    "Consider cooking methods that reduce bitterness",
                    "Important to still eat vegetables despite taste"
                ],
                "foods_you_may_dislike": ["broccoli", "brussels sprouts", "kale", "grapefruit", "black coffee", "tonic water"],
                "cooking_tips": ["Roast vegetables to reduce bitterness", "Add fat/salt to mask bitter", "Start with milder varieties"]
            },
            "CT": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Medium bitter taster",
                "recommendations": [
                    "Moderate bitter taste perception",
                    "Most vegetables tolerable"
                ]
            },
            "TT": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Non-taster - low bitter perception",
                "recommendations": [
                    "Cannot taste PROP/PTC compounds",
                    "May enjoy bitter foods others dislike",
                    "Cruciferous vegetables probably taste fine",
                    "May have higher sweet/salt preference"
                ],
                "foods_you_may_enjoy": ["dark chocolate", "hoppy beer", "bitter greens", "black coffee"]
            }
        },
        "pmid": ["12595690", "21907054"]
    }
}

# Additional nutrient interaction markers
ADDITIONAL_DIET_MARKERS = {
    "rs174547": {
        "gene": "FADS1",
        "trait": "Omega-3/Omega-6 Conversion",
        "effect_allele": "C",
        "interactions": {
            "TT": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Efficient ALA to EPA/DHA conversion",
                "recommendations": [
                    "Can convert plant omega-3s (flax, chia, walnuts) to EPA/DHA",
                    "Fish oil less critical",
                    "Plant-based omega-3 sources work well"
                ],
                "foods_to_enjoy": ["flaxseed", "chia seeds", "walnuts", "hemp seeds"]
            },
            "CT": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Intermediate omega-3 conversion",
                "recommendations": [
                    "Include both plant and marine omega-3 sources"
                ]
            },
            "CC": {
                "tolerance": ToleranceLevel.POOR,
                "description": "Poor ALA to EPA/DHA conversion",
                "recommendations": [
                    "⚠️ Cannot efficiently convert plant omega-3s to active forms",
                    "Need preformed EPA/DHA from fish or algae oil",
                    "Flax/chia alone may not meet omega-3 needs",
                    "Fish 2-3x/week or supplement"
                ],
                "foods_to_prioritize": ["fatty fish (salmon, mackerel, sardines)", "fish oil", "algae oil"]
            }
        },
        "pmid": ["22610424"]
    },
    "rs1800562": {
        "gene": "HFE",
        "trait": "Hemochromatosis - Iron Overload",
        "effect_allele": "A",
        "interactions": {
            "GG": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Normal iron metabolism",
                "recommendations": [
                    "Standard iron intake appropriate"
                ]
            },
            "GA": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Carrier - slightly higher iron levels",
                "recommendations": [
                    "Usually no dietary changes needed",
                    "Avoid iron supplements unless deficient",
                    "Donate blood if levels elevated"
                ]
            },
            "AA": {
                "tolerance": ToleranceLevel.VERY_POOR,
                "description": "Homozygous C282Y - hemochromatosis risk",
                "recommendations": [
                    "🚫 HIGH risk of iron overload",
                    "AVOID iron supplements",
                    "Limit vitamin C with meals (increases absorption)",
                    "Avoid raw shellfish (Vibrio vulnificus risk)",
                    "Tea/coffee with meals reduces absorption (helpful)",
                    "Regular blood donation is therapeutic"
                ],
                "foods_to_limit": ["liver", "iron-fortified cereals", "red meat", "cooking in cast iron"],
                "foods_helpful": ["tea", "coffee", "dairy (inhibits iron absorption)"]
            }
        },
        "pmid": ["9863595"]
    },
    "rs4680": {
        "gene": "COMT",
        "trait": "Catechol Metabolism (Coffee, Tea, Catechins)",
        "effect_allele": "A",
        "interactions": {
            "GG": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Fast COMT - rapid catechol metabolism",
                "recommendations": [
                    "Process catechins and catecholamines quickly",
                    "May need more frequent dosing of caffeine for effect"
                ]
            },
            "GA": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Intermediate COMT",
                "recommendations": []
            },
            "AA": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Slow COMT - catechins may accumulate",
                "recommendations": [
                    "Green tea catechins may be more potent for you",
                    "More sensitive to stress hormones",
                    "B vitamins (especially folate, B12) important for methylation"
                ]
            }
        },
        "pmid": ["18181169"]
    },
    "rs1801133": {
        "gene": "MTHFR",
        "trait": "Folate Metabolism",
        "effect_allele": "A",
        "interactions": {
            "GG": {
                "tolerance": ToleranceLevel.EXCELLENT,
                "description": "Normal MTHFR function",
                "recommendations": [
                    "Can use regular folic acid effectively"
                ],
                "foods_to_enjoy": ["leafy greens", "fortified grains"]
            },
            "GA": {
                "tolerance": ToleranceLevel.GOOD,
                "description": "Mildly reduced MTHFR (~65% activity)",
                "recommendations": [
                    "Standard folate intake usually fine",
                    "Leafy greens provide natural methylfolate"
                ]
            },
            "AA": {
                "tolerance": ToleranceLevel.MODERATE,
                "description": "Reduced MTHFR (~30% activity) - C677T homozygous",
                "recommendations": [
                    "⚠️ May not process folic acid efficiently",
                    "Consider methylfolate (L-5-MTHF) instead of folic acid",
                    "Prioritize food sources of folate (leafy greens)",
                    "B12 (methylcobalamin) also important",
                    "Check homocysteine levels"
                ],
                "foods_to_prioritize": ["leafy greens", "asparagus", "lentils", "avocado"],
                "supplements_to_consider": ["methylfolate", "methylcobalamin B12"]
            }
        },
        "pmid": ["25853894"]
    }
}


# =============================================================================
# COMBINED DIETARY MARKERS
# =============================================================================

DIETARY_MARKERS = {
    **CAFFEINE_DIET_MARKERS,
    **ALCOHOL_DIET_MARKERS,
    **SATURATED_FAT_MARKERS,
    **LACTOSE_MARKERS,
    **GLUTEN_SENSITIVITY_MARKERS,
    **BITTER_TASTE_MARKERS,
    **ADDITIONAL_DIET_MARKERS
}


# =============================================================================
# APOE-SPECIFIC DIETARY ANALYSIS
# =============================================================================

def determine_apoe_diet_recommendations(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Determine APOE genotype and provide saturated fat dietary recommendations.
    """
    rs429358 = genotypes.get("rs429358", "")
    rs7412 = genotypes.get("rs7412", "")
    
    if not rs429358 or not rs7412:
        return {
            "apoe_genotype": "unknown",
            "saturated_fat_sensitivity": "unknown",
            "recommendations": ["Unable to determine APOE - ensure rs429358 and rs7412 are in dataset"]
        }
    
    # Determine alleles (e2, e3, e4)
    alleles = []
    for i in range(min(len(rs429358), len(rs7412))):
        c1 = rs429358[i].upper()
        c2 = rs7412[i].upper()
        
        if c1 == 'T' and c2 == 'T':
            alleles.append('e2')
        elif c1 == 'T' and c2 == 'C':
            alleles.append('e3')
        elif c1 == 'C' and c2 == 'C':
            alleles.append('e4')
    
    if len(alleles) == 2:
        genotype = '/'.join(sorted(alleles))
    elif len(alleles) == 1:
        genotype = f"{alleles[0]}/{alleles[0]}"
    else:
        genotype = "unknown"
    
    # Dietary recommendations based on APOE
    recommendations = {
        "e2/e2": {
            "saturated_fat_sensitivity": "low",
            "tolerance": ToleranceLevel.GOOD,
            "recommendations": [
                "Lower cardiovascular disease risk from saturated fat",
                "But watch triglycerides - e2/e2 can elevate them",
                "Limit alcohol and refined carbs for triglycerides"
            ],
            "foods_to_limit": ["alcohol", "refined sugars"],
            "special_note": "Focus on triglyceride management"
        },
        "e2/e3": {
            "saturated_fat_sensitivity": "low",
            "tolerance": ToleranceLevel.GOOD,
            "recommendations": [
                "Generally favorable lipid response",
                "Standard healthy diet guidelines apply"
            ]
        },
        "e3/e3": {
            "saturated_fat_sensitivity": "average",
            "tolerance": ToleranceLevel.GOOD,
            "recommendations": [
                "Most common genotype",
                "Standard healthy eating guidelines apply",
                "Balance saturated fat with unsaturated"
            ]
        },
        "e2/e4": {
            "saturated_fat_sensitivity": "moderate",
            "tolerance": ToleranceLevel.MODERATE,
            "recommendations": [
                "Mixed effects - some protection from e2",
                "Still moderate caution with saturated fat",
                "Mediterranean diet beneficial"
            ]
        },
        "e3/e4": {
            "saturated_fat_sensitivity": "high",
            "tolerance": ToleranceLevel.POOR,
            "recommendations": [
                "⚠️ ELEVATED sensitivity to dietary saturated fat",
                "Saturated fat significantly raises LDL in e4 carriers",
                "Limit saturated fat to <10% of calories",
                "Replace with unsaturated fats (olive oil, nuts, avocado)",
                "Mediterranean diet strongly recommended",
                "Fish 2-3x weekly beneficial"
            ],
            "foods_to_limit": ["butter", "red meat", "cheese", "coconut oil", "processed meats"],
            "foods_to_prioritize": ["olive oil", "fatty fish", "nuts", "avocados", "legumes"]
        },
        "e4/e4": {
            "saturated_fat_sensitivity": "very_high",
            "tolerance": ToleranceLevel.VERY_POOR,
            "recommendations": [
                "🚨 HIGHEST sensitivity to dietary saturated fat",
                "Very strong LDL increase with saturated fat",
                "STRICT limitation of saturated fat recommended",
                "Mediterranean diet provides the most protection",
                "Consider consulting lipidologist/dietitian",
                "Exercise particularly beneficial for this genotype"
            ],
            "foods_to_avoid": ["butter", "fatty red meat", "full-fat cheese", "tropical oils"],
            "foods_essential": ["olive oil", "fatty fish", "vegetables", "whole grains", "legumes", "nuts"]
        }
    }
    
    result = recommendations.get(genotype, {
        "saturated_fat_sensitivity": "unknown",
        "tolerance": ToleranceLevel.MODERATE,
        "recommendations": ["Unknown APOE combination - moderate caution advised"]
    })
    
    return {
        "apoe_genotype": genotype,
        **result
    }


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_dietary_interactions(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze dietary interactions across all food categories.
    """
    results = {
        "categories": {},
        "summary": {
            "total_markers_checked": 0,
            "markers_found": 0,
            "foods_to_enjoy": [],
            "foods_to_limit": [],
            "foods_to_avoid": [],
            "key_recommendations": []
        }
    }
    
    # Caffeine
    caffeine_result = _analyze_category(genotypes, CAFFEINE_DIET_MARKERS, "caffeine")
    results["categories"]["caffeine"] = caffeine_result
    
    # Alcohol
    alcohol_result = _analyze_category(genotypes, ALCOHOL_DIET_MARKERS, "alcohol")
    results["categories"]["alcohol"] = alcohol_result
    
    # APOE/Saturated fat (special handling)
    apoe_result = determine_apoe_diet_recommendations(genotypes)
    results["categories"]["saturated_fat"] = {
        "gene": "APOE",
        "status": "analyzed",
        "findings": apoe_result
    }
    
    # Lactose
    lactose_result = _analyze_category(genotypes, LACTOSE_MARKERS, "lactose")
    results["categories"]["lactose"] = lactose_result
    
    # Gluten
    gluten_result = _analyze_category(genotypes, GLUTEN_SENSITIVITY_MARKERS, "gluten_sensitivity")
    results["categories"]["gluten"] = gluten_result
    
    # Bitter taste
    bitter_result = _analyze_category(genotypes, BITTER_TASTE_MARKERS, "bitter_taste")
    results["categories"]["bitter_taste"] = bitter_result
    
    # Additional markers (omega-3, iron, folate)
    other_result = _analyze_category(genotypes, ADDITIONAL_DIET_MARKERS, "other_nutrients")
    results["categories"]["other_nutrients"] = other_result
    
    # Compile summary
    for category, data in results["categories"].items():
        if "findings" in data:
            for finding in data.get("findings", []) if isinstance(data.get("findings"), list) else [data.get("findings", {})]:
                if isinstance(finding, dict):
                    if "foods_to_enjoy" in finding:
                        results["summary"]["foods_to_enjoy"].extend(finding["foods_to_enjoy"])
                    if "foods_to_limit" in finding:
                        results["summary"]["foods_to_limit"].extend(finding["foods_to_limit"])
                    if "foods_to_avoid" in finding:
                        results["summary"]["foods_to_avoid"].extend(finding["foods_to_avoid"])
                    if "recommendations" in finding:
                        for rec in finding.get("recommendations", []):
                            if rec.startswith("⚠️") or rec.startswith("🚫") or rec.startswith("🚨"):
                                results["summary"]["key_recommendations"].append(rec)
    
    # Deduplicate
    results["summary"]["foods_to_enjoy"] = list(set(results["summary"]["foods_to_enjoy"]))
    results["summary"]["foods_to_limit"] = list(set(results["summary"]["foods_to_limit"]))
    results["summary"]["foods_to_avoid"] = list(set(results["summary"]["foods_to_avoid"]))
    results["summary"]["key_recommendations"] = list(set(results["summary"]["key_recommendations"]))
    
    return results


def _analyze_category(genotypes: Dict[str, str], markers: Dict, category: str) -> Dict[str, Any]:
    """Analyze a specific dietary category."""
    result = {
        "category": category,
        "markers_checked": len(markers),
        "markers_found": 0,
        "findings": []
    }
    
    for rsid, info in markers.items():
        geno = genotypes.get(rsid)
        if geno:
            result["markers_found"] += 1
            
            if "interactions" in info:
                interaction = info["interactions"].get(geno.upper())
                if interaction:
                    finding = {
                        "rsid": rsid,
                        "gene": info["gene"],
                        "genotype": geno,
                        "trait": info.get("trait", ""),
                        **interaction
                    }
                    result["findings"].append(finding)
    
    return result


def generate_dietary_matrix_report(genotypes: Dict[str, str]) -> str:
    """
    Generate a plain-English dietary interaction report.
    """
    analysis = analyze_dietary_interactions(genotypes)
    
    lines = []
    lines.append("🍽️ PERSONALIZED DIETARY INTERACTION MATRIX")
    lines.append("=" * 50)
    lines.append("")
    
    # Caffeine
    if "caffeine" in analysis["categories"]:
        cat = analysis["categories"]["caffeine"]
        lines.append("☕ CAFFEINE")
        if cat["findings"]:
            for f in cat["findings"]:
                lines.append(f"   {f.get('description', 'No data')}")
                if "daily_limit_mg" in f:
                    lines.append(f"   Daily limit: {f['daily_limit_mg']}mg")
        else:
            lines.append("   No CYP1A2 data available")
        lines.append("")
    
    # Alcohol
    if "alcohol" in analysis["categories"]:
        cat = analysis["categories"]["alcohol"]
        lines.append("🍷 ALCOHOL")
        if cat["findings"]:
            for f in cat["findings"]:
                lines.append(f"   {f['gene']}: {f.get('description', 'No data')}")
                if f.get("tolerance") == ToleranceLevel.VERY_POOR:
                    lines.append("   ⚠️ AVOID ALCOHOL")
        else:
            lines.append("   No alcohol metabolism data available")
        lines.append("")
    
    # Saturated Fat
    if "saturated_fat" in analysis["categories"]:
        cat = analysis["categories"]["saturated_fat"]["findings"]
        lines.append("🥩 SATURATED FAT (APOE)")
        lines.append(f"   APOE: {cat.get('apoe_genotype', 'unknown')}")
        lines.append(f"   Sensitivity: {cat.get('saturated_fat_sensitivity', 'unknown')}")
        if cat.get("recommendations"):
            for rec in cat["recommendations"][:2]:
                lines.append(f"   • {rec}")
        lines.append("")
    
    # Lactose
    if "lactose" in analysis["categories"]:
        cat = analysis["categories"]["lactose"]
        lines.append("🥛 LACTOSE")
        if cat["findings"]:
            for f in cat["findings"]:
                if f["gene"] == "LCT":
                    lines.append(f"   {f.get('description', 'No data')}")
        else:
            lines.append("   No lactase persistence data available")
        lines.append("")
    
    # Gluten
    if "gluten" in analysis["categories"]:
        cat = analysis["categories"]["gluten"]
        lines.append("🌾 GLUTEN (CELIAC RISK)")
        if cat["findings"]:
            for f in cat["findings"]:
                if "HLA" in f["gene"]:
                    lines.append(f"   {f['gene']}: {f.get('description', 'No data')}")
        else:
            lines.append("   No HLA-DQ2/DQ8 data available")
        lines.append("")
    
    # Bitter taste
    if "bitter_taste" in analysis["categories"]:
        cat = analysis["categories"]["bitter_taste"]
        lines.append("🥬 BITTER TASTE")
        if cat["findings"]:
            for f in cat["findings"]:
                lines.append(f"   {f.get('description', 'No data')}")
        else:
            lines.append("   No TAS2R38 data available")
        lines.append("")
    
    # Key recommendations
    if analysis["summary"]["key_recommendations"]:
        lines.append("-" * 50)
        lines.append("⚠️ KEY DIETARY ALERTS:")
        for rec in analysis["summary"]["key_recommendations"]:
            lines.append(f"   {rec}")
    
    return "\n".join(lines)


def get_food_specific_guidance(genotypes: Dict[str, str], food: str) -> Dict[str, Any]:
    """
    Get guidance for a specific food based on genetics.
    """
    food_lower = food.lower()
    analysis = analyze_dietary_interactions(genotypes)
    
    guidance = {
        "food": food,
        "relevant_genes": [],
        "tolerance": "unknown",
        "recommendations": []
    }
    
    # Map foods to categories
    food_mapping = {
        "coffee": "caffeine",
        "caffeine": "caffeine",
        "tea": "caffeine",
        "alcohol": "alcohol",
        "wine": "alcohol",
        "beer": "alcohol",
        "milk": "lactose",
        "dairy": "lactose",
        "cheese": "lactose",
        "bread": "gluten",
        "wheat": "gluten",
        "gluten": "gluten",
        "broccoli": "bitter_taste",
        "vegetables": "bitter_taste",
        "butter": "saturated_fat",
        "red meat": "saturated_fat",
        "steak": "saturated_fat"
    }
    
    category = food_mapping.get(food_lower)
    
    if category and category in analysis["categories"]:
        cat_data = analysis["categories"][category]
        if "findings" in cat_data:
            findings = cat_data["findings"] if isinstance(cat_data["findings"], list) else [cat_data["findings"]]
            for f in findings:
                if isinstance(f, dict):
                    guidance["relevant_genes"].append(f.get("gene", "Unknown"))
                    if "tolerance" in f:
                        guidance["tolerance"] = f["tolerance"].value if hasattr(f["tolerance"], "value") else str(f["tolerance"])
                    if "recommendations" in f:
                        guidance["recommendations"].extend(f["recommendations"])
    
    return guidance
