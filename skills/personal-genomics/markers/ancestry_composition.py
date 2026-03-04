"""
Ancestry Composition Analysis Module
Population admixture estimation from SNP data

This module provides:
- Reference population comparisons
- Admixture estimation using ancestry informative markers (AIMs)
- Major population cluster detection
- Sub-population resolution where data supports it

Sources:
- 1000 Genomes Project reference frequencies
- HGDP (Human Genome Diversity Project)
- Published ancestry informative marker studies

IMPORTANT LIMITATIONS:
- Consumer arrays capture only subset of ancestry-informative markers
- Admixture estimates are probabilistic approximations
- Sub-population resolution limited without full reference panels
- Recent admixture (<5 generations) better detected than ancient
"""

from typing import Dict, List, Optional, Any, Tuple
import math

# =============================================================================
# ANCESTRY INFORMATIVE MARKERS (AIMs)
# =============================================================================

# Population frequency data from 1000 Genomes and published studies
# Format: rsid -> {populations: {pop: allele_freq}, ancestry_info}

ANCESTRY_INFORMATIVE_MARKERS = {
    # =========================================================================
    # CONTINENTAL-LEVEL MARKERS (High differentiation)
    # =========================================================================
    
    # SLC24A5 - Major skin pigmentation gene (European selection)
    "rs1426654": {
        "gene": "SLC24A5",
        "trait": "skin_pigmentation",
        "ancestral": "G",
        "derived": "A",
        "frequencies": {
            "EUR": 0.98,  # European
            "AFR": 0.03,  # African
            "EAS": 0.03,  # East Asian
            "SAS": 0.85,  # South Asian
            "AMR": 0.55,  # Americas (admixed)
        },
        "delta": 0.95,  # Max population difference
        "informativeness": "continental"
    },
    
    # SLC45A2 - Skin/hair pigmentation
    "rs16891982": {
        "gene": "SLC45A2",
        "trait": "skin_pigmentation",
        "ancestral": "C",
        "derived": "G",
        "frequencies": {
            "EUR": 0.96,
            "AFR": 0.02,
            "EAS": 0.02,
            "SAS": 0.15,
            "AMR": 0.45,
        },
        "delta": 0.94,
        "informativeness": "continental"
    },
    
    # HERC2/OCA2 - Eye color (European)
    "rs12913832": {
        "gene": "HERC2",
        "trait": "eye_color",
        "ancestral": "A",
        "derived": "G",
        "frequencies": {
            "EUR": 0.75,
            "AFR": 0.01,
            "EAS": 0.01,
            "SAS": 0.10,
            "AMR": 0.35,
        },
        "delta": 0.74,
        "informativeness": "european_specific"
    },
    
    # LCT - Lactase persistence (European, some African)
    "rs4988235": {
        "gene": "LCT",
        "trait": "lactase_persistence",
        "ancestral": "G",
        "derived": "A",
        "frequencies": {
            "EUR": 0.75,
            "AFR": 0.10,
            "EAS": 0.02,
            "SAS": 0.25,
            "AMR": 0.40,
        },
        "delta": 0.73,
        "informativeness": "european_indicator"
    },
    
    # EDAR - Hair morphology (East Asian)
    "rs3827760": {
        "gene": "EDAR",
        "trait": "hair_morphology",
        "ancestral": "A",
        "derived": "G",
        "frequencies": {
            "EUR": 0.01,
            "AFR": 0.00,
            "EAS": 0.93,
            "SAS": 0.05,
            "AMR": 0.65,
        },
        "delta": 0.93,
        "informativeness": "east_asian_specific"
    },
    
    # ABCC11 - Earwax/body odor (East Asian)
    "rs17822931": {
        "gene": "ABCC11",
        "trait": "earwax_type",
        "ancestral": "G",
        "derived": "A",
        "frequencies": {
            "EUR": 0.12,
            "AFR": 0.02,
            "EAS": 0.95,
            "SAS": 0.15,
            "AMR": 0.55,
        },
        "delta": 0.93,
        "informativeness": "east_asian_specific"
    },
    
    # Duffy antigen - African malaria adaptation
    "rs2814778": {
        "gene": "DARC",
        "trait": "duffy_null",
        "ancestral": "T",
        "derived": "C",
        "frequencies": {
            "EUR": 0.00,
            "AFR": 0.97,
            "EAS": 0.00,
            "SAS": 0.00,
            "AMR": 0.15,
        },
        "delta": 0.97,
        "informativeness": "african_specific"
    },
    
    # =========================================================================
    # ADDITIONAL CONTINENTAL MARKERS
    # =========================================================================
    
    "rs1800414": {
        "gene": "OCA2",
        "trait": "pigmentation",
        "frequencies": {
            "EUR": 0.05,
            "AFR": 0.00,
            "EAS": 0.65,
            "SAS": 0.10,
            "AMR": 0.35,
        },
        "delta": 0.65,
        "informativeness": "east_asian_indicator"
    },
    
    "rs2228479": {
        "gene": "MC1R",
        "trait": "pigmentation",
        "frequencies": {
            "EUR": 0.12,
            "AFR": 0.00,
            "EAS": 0.00,
            "SAS": 0.02,
            "AMR": 0.05,
        },
        "delta": 0.12,
        "informativeness": "european_indicator"
    },
    
    "rs885479": {
        "gene": "MC1R",
        "trait": "pigmentation",
        "frequencies": {
            "EUR": 0.03,
            "AFR": 0.00,
            "EAS": 0.65,
            "SAS": 0.15,
            "AMR": 0.30,
        },
        "delta": 0.65,
        "informativeness": "east_asian_indicator"
    },
    
    # Native American informative
    "rs3811801": {
        "gene": "FUT2",
        "trait": "secretor_status",
        "frequencies": {
            "EUR": 0.45,
            "AFR": 0.35,
            "EAS": 0.40,
            "SAS": 0.40,
            "AMR": 0.10,  # Lower in Native Americans
        },
        "delta": 0.35,
        "informativeness": "native_american_indicator"
    },
    
    # South Asian informative markers
    "rs1042602": {
        "gene": "TYR",
        "trait": "pigmentation",
        "frequencies": {
            "EUR": 0.40,
            "AFR": 0.05,
            "EAS": 0.02,
            "SAS": 0.30,
            "AMR": 0.25,
        },
        "delta": 0.38,
        "informativeness": "subcontinental"
    },
    
    # =========================================================================
    # REGIONAL/SUBCONTINENTAL MARKERS
    # =========================================================================
    
    # European substructure
    "rs6548616": {
        "gene": "LCT",
        "trait": "lactase_regulation",
        "frequencies": {
            "EUR_North": 0.80,
            "EUR_South": 0.45,
            "EUR": 0.60,
            "AFR": 0.05,
            "EAS": 0.02,
        },
        "delta": 0.35,
        "informativeness": "european_substructure"
    },
    
    # Ashkenazi Jewish indicator
    "rs4532": {
        "gene": "DRD1",
        "frequencies": {
            "EUR": 0.60,
            "EUR_Ashkenazi": 0.85,
            "AFR": 0.40,
            "EAS": 0.55,
        },
        "informativeness": "ashkenazi_enriched"
    },
    
    # East African vs West African
    "rs1800404": {
        "gene": "OCA2",
        "frequencies": {
            "AFR_West": 0.15,
            "AFR_East": 0.30,
            "AFR": 0.20,
            "EUR": 0.75,
        },
        "informativeness": "african_substructure"
    },
    
    # =========================================================================
    # ADDITIONAL VALIDATED AIMs
    # =========================================================================
    
    "rs260690": {
        "gene": "TYRP1",
        "frequencies": {"EUR": 0.50, "AFR": 0.08, "EAS": 0.15, "SAS": 0.25, "AMR": 0.30},
        "delta": 0.42,
        "informativeness": "continental"
    },
    
    "rs1408799": {
        "gene": "TYRP1",
        "frequencies": {"EUR": 0.75, "AFR": 0.15, "EAS": 0.20, "SAS": 0.35, "AMR": 0.45},
        "delta": 0.60,
        "informativeness": "continental"
    },
    
    "rs7495174": {
        "gene": "OCA2",
        "frequencies": {"EUR": 0.85, "AFR": 0.02, "EAS": 0.65, "SAS": 0.50, "AMR": 0.55},
        "delta": 0.83,
        "informativeness": "continental"
    },
    
    "rs4778138": {
        "gene": "OCA2",
        "frequencies": {"EUR": 0.80, "AFR": 0.15, "EAS": 0.65, "SAS": 0.45, "AMR": 0.50},
        "delta": 0.65,
        "informativeness": "continental"
    },
    
    "rs1393350": {
        "gene": "TYR",
        "frequencies": {"EUR": 0.25, "AFR": 0.05, "EAS": 0.01, "SAS": 0.08, "AMR": 0.12},
        "delta": 0.24,
        "informativeness": "european_indicator"
    },
    
    "rs2305498": {
        "frequencies": {"EUR": 0.30, "AFR": 0.65, "EAS": 0.25, "SAS": 0.35, "AMR": 0.40},
        "delta": 0.40,
        "informativeness": "african_indicator"
    },
    
    "rs3827760": {
        "gene": "EDAR",
        "frequencies": {"EUR": 0.01, "AFR": 0.00, "EAS": 0.93, "SAS": 0.05, "AMR": 0.65},
        "delta": 0.93,
        "informativeness": "east_asian_specific"
    },
    
    "rs10843104": {
        "frequencies": {"EUR": 0.15, "AFR": 0.75, "EAS": 0.10, "SAS": 0.20, "AMR": 0.35},
        "delta": 0.65,
        "informativeness": "african_indicator"
    },
    
    "rs2789823": {
        "frequencies": {"EUR": 0.45, "AFR": 0.10, "EAS": 0.85, "SAS": 0.30, "AMR": 0.50},
        "delta": 0.75,
        "informativeness": "east_asian_indicator"
    },
    
    "rs2070959": {
        "gene": "UGT1A1",
        "frequencies": {"EUR": 0.35, "AFR": 0.45, "EAS": 0.12, "SAS": 0.25, "AMR": 0.30},
        "delta": 0.33,
        "informativeness": "subcontinental"
    },
}

# =============================================================================
# POPULATION REFERENCE DATA
# =============================================================================

POPULATION_DESCRIPTIONS = {
    "EUR": {
        "name": "European",
        "description": "European ancestry, including Northern, Southern, Eastern, and Western European populations",
        "subpopulations": ["British", "Finnish", "Iberian", "Italian", "Ashkenazi Jewish"],
        "typical_haplogroups_mtdna": ["H", "U", "K", "J", "T", "V"],
        "typical_haplogroups_ydna": ["R1b", "R1a", "I", "J2", "E1b1b"],
    },
    "AFR": {
        "name": "African",
        "description": "Sub-Saharan African ancestry, including West, East, and Southern African populations",
        "subpopulations": ["West African", "East African", "Bantu", "Khoisan"],
        "typical_haplogroups_mtdna": ["L0", "L1", "L2", "L3"],
        "typical_haplogroups_ydna": ["E", "A", "B"],
    },
    "EAS": {
        "name": "East Asian",
        "description": "East Asian ancestry, including Chinese, Japanese, Korean, and Vietnamese populations",
        "subpopulations": ["Han Chinese", "Japanese", "Korean", "Vietnamese"],
        "typical_haplogroups_mtdna": ["D", "B", "F", "A", "C", "M"],
        "typical_haplogroups_ydna": ["O", "C", "D", "N"],
    },
    "SAS": {
        "name": "South Asian",
        "description": "South Asian ancestry, including Indian subcontinent populations",
        "subpopulations": ["North Indian", "South Indian", "Bengali", "Pakistani"],
        "typical_haplogroups_mtdna": ["M", "R", "U"],
        "typical_haplogroups_ydna": ["R1a", "H", "L", "J2"],
    },
    "AMR": {
        "name": "Americas (Indigenous + Admixed)",
        "description": "Indigenous American ancestry and Latin American admixed populations",
        "subpopulations": ["Native American", "Mexican", "Puerto Rican", "Colombian"],
        "typical_haplogroups_mtdna": ["A", "B", "C", "D", "X"],
        "typical_haplogroups_ydna": ["Q", "C"],
    },
    "MID": {
        "name": "Middle Eastern",
        "description": "Middle Eastern and North African ancestry",
        "subpopulations": ["Arab", "Persian", "Turkish", "Berber", "Jewish"],
        "typical_haplogroups_mtdna": ["U", "J", "T", "H", "K"],
        "typical_haplogroups_ydna": ["J1", "J2", "E1b1b", "G"],
    },
    "OCE": {
        "name": "Oceanian",
        "description": "Pacific Islander and Indigenous Australian ancestry",
        "subpopulations": ["Polynesian", "Melanesian", "Aboriginal Australian"],
        "typical_haplogroups_mtdna": ["B", "P", "Q"],
        "typical_haplogroups_ydna": ["C", "M", "S"],
    },
}


def estimate_ancestry(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Estimate ancestry composition from available AIMs.
    
    Uses a simplified likelihood-based approach:
    For each marker, calculate probability of genotype under each population's
    allele frequencies, then aggregate.
    
    Args:
        genotypes: Dict mapping rsid -> genotype
        
    Returns:
        Dict with ancestry estimates and confidence
    """
    # Initialize population scores
    populations = ["EUR", "AFR", "EAS", "SAS", "AMR"]
    log_likelihoods = {pop: 0.0 for pop in populations}
    markers_used = 0
    marker_details = []
    
    for rsid, info in ANCESTRY_INFORMATIVE_MARKERS.items():
        geno = genotypes.get(rsid)
        if not geno:
            continue
        
        freqs = info.get("frequencies", {})
        if not all(pop in freqs for pop in populations):
            continue
        
        markers_used += 1
        
        # Count derived allele
        derived = info.get("derived", info.get("ancestral", ""))
        ancestral = info.get("ancestral", "")
        
        # Determine allele count (0, 1, or 2 copies of derived)
        derived_count = sum(1 for a in geno if a.upper() == derived.upper())
        
        # Calculate genotype probability for each population
        # Using Hardy-Weinberg: P(AA) = p², P(Aa) = 2pq, P(aa) = q²
        for pop in populations:
            p = freqs.get(pop, 0.5)  # derived freq
            q = 1 - p
            
            # Avoid log(0)
            p = max(0.001, min(0.999, p))
            q = max(0.001, min(0.999, q))
            
            if derived_count == 2:
                prob = p * p
            elif derived_count == 1:
                prob = 2 * p * q
            else:
                prob = q * q
            
            log_likelihoods[pop] += math.log(prob)
        
        # Track informative markers
        if info.get("delta", 0) > 0.3:
            marker_details.append({
                "rsid": rsid,
                "gene": info.get("gene", ""),
                "genotype": geno,
                "informativeness": info.get("informativeness"),
            })
    
    # Convert log-likelihoods to proportions
    if markers_used < 3:
        return {
            "status": "insufficient_data",
            "markers_found": markers_used,
            "error": "Need at least 3 ancestry informative markers for estimation"
        }
    
    # Normalize to probabilities (softmax-like)
    max_ll = max(log_likelihoods.values())
    exp_lls = {pop: math.exp(ll - max_ll) for pop, ll in log_likelihoods.items()}
    total = sum(exp_lls.values())
    
    proportions = {pop: round(exp_ll / total * 100, 1) for pop, exp_ll in exp_lls.items()}
    
    # Determine confidence
    if markers_used >= 15:
        confidence = "high"
    elif markers_used >= 8:
        confidence = "moderate"
    else:
        confidence = "low"
    
    # Sort by proportion
    sorted_ancestry = sorted(proportions.items(), key=lambda x: x[1], reverse=True)
    
    # Build result
    result = {
        "status": "success",
        "markers_used": markers_used,
        "confidence": confidence,
        "ancestry_proportions": {
            POPULATION_DESCRIPTIONS[pop]["name"]: pct
            for pop, pct in sorted_ancestry
        },
        "ancestry_proportions_raw": proportions,
        "primary_ancestry": POPULATION_DESCRIPTIONS[sorted_ancestry[0][0]]["name"],
        "primary_percentage": sorted_ancestry[0][1],
        "detailed_breakdown": [],
        "methodology_notes": [
            "Estimates based on ancestry informative markers (AIMs)",
            "Consumer arrays have limited resolution vs research panels",
            "Recent admixture may show as mixed percentages",
            f"Analysis used {markers_used} informative markers"
        ]
    }
    
    # Add detailed breakdown for significant ancestries (>5%)
    for pop, pct in sorted_ancestry:
        if pct >= 5:
            pop_info = POPULATION_DESCRIPTIONS.get(pop, {})
            result["detailed_breakdown"].append({
                "population": pop_info.get("name", pop),
                "percentage": pct,
                "description": pop_info.get("description", ""),
                "typical_subpopulations": pop_info.get("subpopulations", []),
            })
    
    # Key informative markers
    result["informative_markers"] = marker_details[:10]
    
    return result


def detect_admixture(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Detect signs of recent admixture between populations.
    
    Recent admixture shows characteristic patterns:
    - High heterozygosity at AIMs
    - Mixed ancestry percentages in 20-80% range
    """
    ancestry = estimate_ancestry(genotypes)
    
    if ancestry.get("status") != "success":
        return {"status": "insufficient_data", "is_admixed": "unknown"}
    
    proportions = ancestry.get("ancestry_proportions_raw", {})
    
    # Count populations with significant contribution
    significant_pops = sum(1 for pct in proportions.values() if pct >= 15)
    
    # Check heterozygosity at high-delta AIMs
    het_count = 0
    aim_count = 0
    
    for rsid, info in ANCESTRY_INFORMATIVE_MARKERS.items():
        if info.get("delta", 0) < 0.5:
            continue
            
        geno = genotypes.get(rsid)
        if not geno or len(geno) < 2:
            continue
            
        aim_count += 1
        if geno[0] != geno[1]:
            het_count += 1
    
    het_rate = het_count / aim_count if aim_count > 0 else 0
    
    is_admixed = significant_pops >= 2 or het_rate > 0.6
    
    return {
        "status": "success",
        "is_admixed": is_admixed,
        "admixture_evidence": {
            "populations_with_15pct_plus": significant_pops,
            "heterozygosity_rate": round(het_rate, 2),
            "aims_checked": aim_count
        },
        "interpretation": _interpret_admixture(proportions, significant_pops, het_rate),
        "ancestry_summary": ancestry.get("ancestry_proportions", {})
    }


def _interpret_admixture(proportions: Dict, sig_pops: int, het_rate: float) -> str:
    """Generate human-readable admixture interpretation."""
    if sig_pops == 1:
        top_pop = max(proportions.items(), key=lambda x: x[1])
        return f"Ancestry appears primarily {POPULATION_DESCRIPTIONS.get(top_pop[0], {}).get('name', top_pop[0])} with minimal admixture"
    elif sig_pops == 2:
        top_two = sorted(proportions.items(), key=lambda x: x[1], reverse=True)[:2]
        pop1 = POPULATION_DESCRIPTIONS.get(top_two[0][0], {}).get('name', top_two[0][0])
        pop2 = POPULATION_DESCRIPTIONS.get(top_two[1][0], {}).get('name', top_two[1][0])
        return f"Evidence of admixture between {pop1} and {pop2} ancestry"
    else:
        return "Complex admixture pattern detected from multiple ancestral populations"


def get_ancestry_summary(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Complete ancestry analysis with composition and admixture detection.
    """
    composition = estimate_ancestry(genotypes)
    admixture = detect_admixture(genotypes)
    
    return {
        "composition": composition,
        "admixture": admixture,
        "summary": _generate_ancestry_text_summary(composition, admixture)
    }


def _generate_ancestry_text_summary(composition: Dict, admixture: Dict) -> str:
    """Generate text summary for reports."""
    lines = []
    
    if composition.get("status") != "success":
        return "Insufficient ancestry informative markers for reliable estimation."
    
    lines.append(f"Primary ancestry: {composition['primary_ancestry']} ({composition['primary_percentage']}%)")
    lines.append("")
    
    lines.append("Full breakdown:")
    for pop, pct in composition.get("ancestry_proportions", {}).items():
        if pct >= 1:
            lines.append(f"  {pop}: {pct}%")
    
    lines.append("")
    
    if admixture.get("is_admixed"):
        lines.append("Admixture: " + admixture.get("interpretation", "Detected"))
    else:
        lines.append("Admixture: No significant admixture detected")
    
    lines.append("")
    lines.append(f"Confidence: {composition.get('confidence', 'unknown')}")
    lines.append(f"Markers analyzed: {composition.get('markers_used', 0)}")
    
    return "\n".join(lines)
