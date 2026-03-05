"""
Advanced Genetic Analysis v4.1.0
Includes:
- Runs of Homozygosity (ROH) detection
- Telomere length estimation
- Additional advanced genetic metrics

These analyses require careful interpretation and sensitive handling.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


# =============================================================================
# RUNS OF HOMOZYGOSITY (ROH)
# =============================================================================

class ROHLevel(Enum):
    """Classification of ROH findings."""
    MINIMAL = "minimal"      # Very low homozygosity
    NORMAL = "normal"        # Expected for outbred population
    ELEVATED = "elevated"    # Some extended runs detected
    HIGH = "high"           # Significant homozygosity


@dataclass
class ROHRegion:
    """Represents a detected run of homozygosity."""
    chromosome: str
    start_position: int
    end_position: int
    length_mb: float
    snp_count: int
    density: float


def calculate_heterozygosity_rate(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate overall heterozygosity rate from genotype data.
    
    Expected heterozygosity in outbred populations: ~0.30-0.35 for autosomal SNPs
    Lower values suggest increased homozygosity (possibly consanguinity or population isolate)
    """
    total = 0
    heterozygous = 0
    homozygous = 0
    missing = 0
    
    for rsid, geno in genotypes.items():
        if not geno or geno in ['--', '00', 'NC', 'N/A']:
            missing += 1
            continue
        
        total += 1
        
        # Check if heterozygous (different alleles)
        if len(geno) >= 2:
            allele1 = geno[0].upper()
            allele2 = geno[1].upper() if len(geno) > 1 else geno[0].upper()
            
            if allele1 != allele2:
                heterozygous += 1
            else:
                homozygous += 1
    
    het_rate = heterozygous / total if total > 0 else 0
    hom_rate = homozygous / total if total > 0 else 0
    
    # Interpret heterozygosity
    if het_rate > 0.32:
        interpretation = "Normal heterozygosity for outbred population"
        level = ROHLevel.MINIMAL
    elif het_rate > 0.28:
        interpretation = "Slightly reduced heterozygosity - likely normal variation"
        level = ROHLevel.NORMAL
    elif het_rate > 0.22:
        interpretation = "Reduced heterozygosity - may indicate distant common ancestry"
        level = ROHLevel.ELEVATED
    else:
        interpretation = "Low heterozygosity - may warrant further investigation"
        level = ROHLevel.HIGH
    
    return {
        "total_snps_analyzed": total,
        "heterozygous_count": heterozygous,
        "homozygous_count": homozygous,
        "missing_count": missing,
        "heterozygosity_rate": round(het_rate, 4),
        "homozygosity_rate": round(hom_rate, 4),
        "expected_het_rate": 0.32,
        "interpretation": interpretation,
        "level": level.value
    }


def detect_roh_regions(
    genotypes: Dict[str, str],
    snp_positions: Optional[Dict[str, Tuple[str, int]]] = None,
    min_snps: int = 100,
    max_het_allowed: int = 2
) -> Dict[str, Any]:
    """
    Detect runs of homozygosity from genotype data.
    
    Note: This is a simplified detection. Clinical ROH analysis requires
    dense SNP data with known chromosomal positions (not available in all
    consumer tests).
    
    Args:
        genotypes: Dict of rsid -> genotype
        snp_positions: Optional dict of rsid -> (chromosome, position)
        min_snps: Minimum SNPs in a row to consider an ROH
        max_het_allowed: Maximum heterozygous calls allowed in an ROH
    """
    results = {
        "analysis_possible": False,
        "note": "",
        "roh_regions": [],
        "total_roh_length_mb": 0,
        "roh_percentage": 0,
        "froh": 0,  # Coefficient of inbreeding estimated from ROH
        "interpretation": ""
    }
    
    # Check if we have position data
    if not snp_positions:
        results["note"] = (
            "ROH analysis requires SNP position data which is not included in standard "
            "consumer genetic tests. Heterozygosity rate is calculated instead."
        )
        # Calculate overall heterozygosity as fallback
        het_stats = calculate_heterozygosity_rate(genotypes)
        results["heterozygosity_analysis"] = het_stats
        
        # Estimate ROH from heterozygosity
        # Lower het rate suggests more homozygosity
        estimated_froh = max(0, (0.32 - het_stats["heterozygosity_rate"]) / 0.32)
        results["estimated_froh"] = round(estimated_froh, 4)
        
        if estimated_froh < 0.01:
            results["interpretation"] = "Homozygosity levels consistent with outbred population."
        elif estimated_froh < 0.03:
            results["interpretation"] = (
                "Slightly elevated homozygosity. May indicate ancestry from "
                "a population isolate or very distant shared ancestry."
            )
        elif estimated_froh < 0.0625:  # First cousin level
            results["interpretation"] = (
                "Elevated homozygosity detected. This may indicate shared ancestry "
                "in recent generations. Consider discussing with a genetic counselor."
            )
        else:
            results["interpretation"] = (
                "High homozygosity detected. This warrants clinical evaluation "
                "to assess implications. Please consult a genetic counselor."
            )
        
        return results
    
    # If we have positions, do actual ROH detection
    results["analysis_possible"] = True
    # [Full ROH detection would go here with positional data]
    
    return results


def generate_roh_report(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate a sensitive, informative ROH report.
    """
    # Calculate basic stats
    het_stats = calculate_heterozygosity_rate(genotypes)
    roh_analysis = detect_roh_regions(genotypes)
    
    report = {
        "summary": {},
        "heterozygosity": het_stats,
        "roh_analysis": roh_analysis,
        "clinical_note": "",
        "resources": []
    }
    
    # Determine summary
    level = het_stats.get("level", "normal")
    
    if level in ["minimal", "normal"]:
        report["summary"] = {
            "status": "normal",
            "description": (
                "Your genetic data shows heterozygosity levels typical of an outbred "
                "population. No concerns regarding runs of homozygosity."
            ),
            "action_needed": False
        }
    elif level == "elevated":
        report["summary"] = {
            "status": "elevated",
            "description": (
                "Your genetic data shows somewhat reduced heterozygosity. This is often "
                "seen in individuals from founder populations, population isolates, or "
                "those with some degree of shared ancestry. This is informational and "
                "typically does not indicate health concerns."
            ),
            "action_needed": False
        }
        report["clinical_note"] = (
            "Elevated homozygosity can sometimes increase the chance of inheriting two "
            "copies of recessive variants. If you have specific health concerns, consider "
            "discussing carrier screening with a genetic counselor."
        )
    else:  # high
        report["summary"] = {
            "status": "significant",
            "description": (
                "Your genetic data suggests higher than typical homozygosity. This finding "
                "is handled sensitively. It may have various explanations and implications."
            ),
            "action_needed": True
        }
        report["clinical_note"] = (
            "We recommend consulting with a certified genetic counselor to discuss "
            "these findings. They can provide context, answer questions, and discuss "
            "any health considerations in a supportive environment."
        )
        report["resources"] = [
            {
                "name": "National Society of Genetic Counselors",
                "url": "https://www.nsgc.org/",
                "description": "Find a genetic counselor near you"
            },
            {
                "name": "ACMG - Consanguinity Resources",
                "url": "https://www.acmg.net/",
                "description": "Professional genetics resources"
            }
        ]
    
    return report


# =============================================================================
# TELOMERE LENGTH ESTIMATION
# =============================================================================

TELOMERE_MARKERS = {
    "rs12696304": {
        "gene": "TERC",
        "trait": "Telomerase RNA Component",
        "effect_allele": "G",
        "effect": {
            "CC": {"telomere_effect": "shorter", "score": -1},
            "CG": {"telomere_effect": "intermediate", "score": 0},
            "GG": {"telomere_effect": "longer", "score": 1}
        },
        "pmid": ["20018825"],
        "note": "Associated with leukocyte telomere length"
    },
    "rs10936599": {
        "gene": "TERC",
        "trait": "Telomerase RNA Component",
        "effect_allele": "T",
        "effect": {
            "CC": {"telomere_effect": "longer", "score": 1},
            "CT": {"telomere_effect": "intermediate", "score": 0},
            "TT": {"telomere_effect": "shorter", "score": -1}
        },
        "pmid": ["20018825"]
    },
    "rs2736100": {
        "gene": "TERT",
        "trait": "Telomerase Reverse Transcriptase",
        "effect_allele": "C",
        "effect": {
            "AA": {"telomere_effect": "shorter", "score": -1},
            "AC": {"telomere_effect": "intermediate", "score": 0},
            "CC": {"telomere_effect": "longer", "score": 1}
        },
        "pmid": ["20018825"],
        "note": "TERT is the catalytic subunit of telomerase"
    },
    "rs7726159": {
        "gene": "TERT",
        "trait": "Telomerase Activity",
        "effect_allele": "C",
        "effect": {
            "AA": {"telomere_effect": "shorter", "score": -0.5},
            "AC": {"telomere_effect": "intermediate", "score": 0},
            "CC": {"telomere_effect": "longer", "score": 0.5}
        },
        "pmid": ["20018825"]
    },
    "rs9420907": {
        "gene": "OBFC1",
        "trait": "Telomere Binding",
        "effect_allele": "A",
        "effect": {
            "CC": {"telomere_effect": "shorter", "score": -0.5},
            "AC": {"telomere_effect": "intermediate", "score": 0},
            "AA": {"telomere_effect": "longer", "score": 0.5}
        },
        "pmid": ["20018825"],
        "note": "Part of the CST telomere capping complex"
    },
    "rs8105767": {
        "gene": "ZNF208",
        "trait": "Telomere Length Associated",
        "effect_allele": "G",
        "effect": {
            "AA": {"telomere_effect": "shorter", "score": -0.3},
            "AG": {"telomere_effect": "intermediate", "score": 0},
            "GG": {"telomere_effect": "longer", "score": 0.3}
        },
        "pmid": ["23064413"]
    },
    "rs11125529": {
        "gene": "ACYP2",
        "trait": "Telomere Maintenance",
        "effect_allele": "A",
        "effect": {
            "CC": {"telomere_effect": "shorter", "score": -0.3},
            "AC": {"telomere_effect": "intermediate", "score": 0},
            "AA": {"telomere_effect": "longer", "score": 0.3}
        },
        "pmid": ["23064413"]
    }
}

# Longevity-associated variants
LONGEVITY_RELATED_MARKERS = {
    "rs429358": {
        "gene": "APOE",
        "trait": "APOE ε4 (Longevity association)",
        "note": "ε4 allele associated with reduced longevity; ε2 may be protective",
        "longevity_effect": "context_dependent"
    },
    "rs7412": {
        "gene": "APOE",
        "trait": "APOE ε2/ε3 determination",
        "note": "Combined with rs429358 to determine APOE genotype"
    },
    "rs2802292": {
        "gene": "FOXO3",
        "trait": "Longevity Gene",
        "effect_allele": "G",
        "effect": {
            "TT": {"longevity": "baseline", "score": 0},
            "TG": {"longevity": "slightly_favorable", "score": 0.5},
            "GG": {"longevity": "favorable", "score": 1}
        },
        "pmid": ["18316725", "19078267"],
        "note": "One of the most replicated longevity associations"
    }
}


def estimate_telomere_length(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Estimate relative telomere length from genetic markers.
    
    IMPORTANT CAVEATS:
    - This estimates genetic predisposition, not actual telomere length
    - Actual telomere length is strongly influenced by lifestyle, stress, etc.
    - These variants explain only ~5-10% of telomere length variation
    """
    telomere_score = 0
    weight_sum = 0
    markers_found = []
    
    for rsid, info in TELOMERE_MARKERS.items():
        geno = genotypes.get(rsid)
        if geno:
            geno_upper = geno.upper()
            
            if "effect" in info and geno_upper in info["effect"]:
                effect = info["effect"][geno_upper]
                score = effect.get("score", 0)
                telomere_score += score
                weight_sum += 1
                
                markers_found.append({
                    "rsid": rsid,
                    "gene": info["gene"],
                    "genotype": geno,
                    "effect": effect.get("telomere_effect", "unknown"),
                    "score": score
                })
    
    # Normalize and interpret
    if weight_sum > 0:
        normalized_score = telomere_score / weight_sum * 3  # Scale to -3 to +3
    else:
        normalized_score = 0
    
    # Determine relative estimate
    if normalized_score > 1:
        estimate = "longer_than_average"
        percentile_estimate = "60-75th percentile (rough estimate)"
        description = "Your genetic variants are associated with somewhat longer telomeres."
    elif normalized_score > 0:
        estimate = "slightly_longer"
        percentile_estimate = "50-60th percentile (rough estimate)"
        description = "Your genetic variants suggest slightly longer than average telomeres."
    elif normalized_score > -0.5:
        estimate = "average"
        percentile_estimate = "40-60th percentile (rough estimate)"
        description = "Your genetic variants suggest typical telomere length."
    elif normalized_score > -1:
        estimate = "slightly_shorter"
        percentile_estimate = "40-50th percentile (rough estimate)"
        description = "Your genetic variants suggest slightly shorter than average telomeres."
    else:
        estimate = "shorter_than_average"
        percentile_estimate = "25-40th percentile (rough estimate)"
        description = "Your genetic variants are associated with somewhat shorter telomeres."
    
    return {
        "estimate": estimate,
        "percentile_estimate": percentile_estimate,
        "description": description,
        "raw_score": round(telomere_score, 2),
        "normalized_score": round(normalized_score, 2),
        "markers_analyzed": len(markers_found),
        "markers_found": markers_found,
        "caveats": [
            "This estimates genetic predisposition only, not actual telomere length",
            "These variants explain only 5-10% of telomere length variation",
            "Lifestyle factors (stress, diet, exercise, sleep) strongly influence telomeres",
            "Actual telomere length requires laboratory measurement",
            "Telomere length is just one factor in aging - don't overinterpret"
        ],
        "lifestyle_factors": [
            "Regular exercise is associated with longer telomeres",
            "Chronic stress may accelerate telomere shortening",
            "Mediterranean diet associated with telomere maintenance",
            "Adequate sleep supports telomere health",
            "Smoking strongly associated with shorter telomeres"
        ]
    }


def estimate_longevity_associations(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Identify longevity-associated variants.
    
    CAVEAT: Longevity is multifactorial. Genetics explains only ~25% of lifespan variation.
    """
    findings = []
    longevity_score = 0
    
    # Check FOXO3
    foxo3 = genotypes.get("rs2802292")
    if foxo3:
        foxo3_upper = foxo3.upper()
        effect = LONGEVITY_RELATED_MARKERS["rs2802292"]["effect"].get(foxo3_upper)
        if effect:
            findings.append({
                "gene": "FOXO3",
                "rsid": "rs2802292",
                "genotype": foxo3,
                "association": effect.get("longevity", "unknown"),
                "note": "One of the most replicated longevity genes"
            })
            longevity_score += effect.get("score", 0)
    
    # Check APOE
    rs429358 = genotypes.get("rs429358", "")
    rs7412 = genotypes.get("rs7412", "")
    
    if rs429358 and rs7412:
        # Determine APOE genotype
        alleles = []
        for i in range(min(len(rs429358), len(rs7412))):
            c1 = rs429358[i].upper()
            c2 = rs7412[i].upper()
            
            if c1 == 'T' and c2 == 'T':
                alleles.append('ε2')
            elif c1 == 'T' and c2 == 'C':
                alleles.append('ε3')
            elif c1 == 'C' and c2 == 'C':
                alleles.append('ε4')
        
        if len(alleles) >= 1:
            apoe_geno = '/'.join(sorted(alleles)) if len(alleles) == 2 else f"{alleles[0]}/{alleles[0]}"
            
            # Score APOE
            if 'ε4' in apoe_geno and alleles.count('ε4') == 2:
                apoe_effect = "unfavorable"
                longevity_score -= 1
            elif 'ε4' in apoe_geno:
                apoe_effect = "slightly_unfavorable"
                longevity_score -= 0.5
            elif 'ε2' in apoe_geno:
                apoe_effect = "favorable"
                longevity_score += 0.5
            else:
                apoe_effect = "neutral"
            
            findings.append({
                "gene": "APOE",
                "genotype": apoe_geno,
                "association": apoe_effect,
                "note": "Well-established longevity association, also affects disease risk"
            })
    
    # Interpret overall
    if longevity_score > 0.5:
        interpretation = "Some genetic variants associated with longevity"
    elif longevity_score > -0.5:
        interpretation = "Typical longevity-associated variant profile"
    else:
        interpretation = "Some variants associated with reduced longevity (lifestyle can offset)"
    
    return {
        "findings": findings,
        "score": round(longevity_score, 2),
        "interpretation": interpretation,
        "important_note": (
            "Longevity is only ~25% genetic. Lifestyle factors (diet, exercise, "
            "social connections, stress management, not smoking) are the major determinants "
            "of lifespan. Don't be discouraged or overconfident based on genetics alone."
        )
    }


def generate_telomere_report(genotypes: Dict[str, str]) -> str:
    """
    Generate plain-English telomere and longevity report.
    """
    telomere = estimate_telomere_length(genotypes)
    longevity = estimate_longevity_associations(genotypes)
    
    lines = []
    lines.append("🧬 TELOMERE & LONGEVITY PROFILE")
    lines.append("=" * 50)
    lines.append("")
    
    lines.append("📏 TELOMERE LENGTH ESTIMATE")
    lines.append(f"   {telomere['description']}")
    lines.append(f"   Estimate: {telomere['percentile_estimate']}")
    lines.append(f"   Markers analyzed: {telomere['markers_analyzed']}")
    lines.append("")
    
    lines.append("⚠️ IMPORTANT CAVEATS:")
    for caveat in telomere['caveats'][:3]:
        lines.append(f"   • {caveat}")
    lines.append("")
    
    lines.append("🌱 LONGEVITY ASSOCIATIONS")
    lines.append(f"   {longevity['interpretation']}")
    for finding in longevity['findings']:
        lines.append(f"   • {finding['gene']}: {finding['association']}")
    lines.append("")
    
    lines.append("💪 LIFESTYLE FACTORS (More important than genetics!):")
    for factor in telomere['lifestyle_factors'][:3]:
        lines.append(f"   • {factor}")
    
    lines.append("")
    lines.append("📝 " + longevity['important_note'][:100] + "...")
    
    return "\n".join(lines)
