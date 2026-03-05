"""
Raw Data Quality Metrics Module
Analysis of genotyping quality, coverage, and platform detection

This module provides:
- Call rate analysis
- No-call position tracking
- Chromosome coverage analysis
- Platform/chip detection
- Quality warnings
- Confidence scoring for variants
"""

from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import re


# =============================================================================
# PLATFORM DETECTION SIGNATURES
# =============================================================================

PLATFORM_SIGNATURES = {
    "23andme_v5": {
        "marker_count_range": (630000, 680000),
        "signature_snps": ["rs548049170", "rs9461509", "rs73211851"],
        "header_pattern": r"23andme",
        "expected_chromosomes": 25,  # 1-22, X, Y, MT
        "description": "23andMe v5 chip (2017+)"
    },
    "23andme_v4": {
        "marker_count_range": (570000, 620000),
        "signature_snps": ["rs12203592", "rs6548616"],
        "header_pattern": r"23andme",
        "expected_chromosomes": 25,
        "description": "23andMe v4 chip (2013-2017)"
    },
    "23andme_v3": {
        "marker_count_range": (950000, 1050000),
        "signature_snps": ["rs2032658", "rs12785878"],
        "header_pattern": r"23andme",
        "expected_chromosomes": 25,
        "description": "23andMe v3 chip (2010-2013) - larger panel"
    },
    "ancestrydna_v2": {
        "marker_count_range": (680000, 750000),
        "header_pattern": r"ancestrydna|ancestry\.com",
        "expected_chromosomes": 24,  # 1-22, X, Y
        "description": "AncestryDNA v2 chip"
    },
    "ancestrydna_v1": {
        "marker_count_range": (700000, 800000),
        "header_pattern": r"ancestrydna",
        "description": "AncestryDNA v1 chip"
    },
    "myheritage": {
        "marker_count_range": (680000, 750000),
        "header_pattern": r"myheritage",
        "description": "MyHeritage DNA"
    },
    "ftdna": {
        "marker_count_range": (680000, 750000),
        "header_pattern": r"family\s*tree\s*dna|ftdna",
        "description": "FamilyTreeDNA"
    },
    "living_dna": {
        "marker_count_range": (630000, 700000),
        "header_pattern": r"living\s*dna",
        "description": "LivingDNA"
    },
    "nebula": {
        "marker_count_range": (15000000, 3500000000),  # WGS range
        "header_pattern": r"nebula",
        "description": "Nebula Genomics (low-pass WGS)"
    },
    "vcf_wgs": {
        "marker_count_range": (3000000, 5000000000),
        "header_pattern": r"##fileformat=VCF",
        "description": "Whole Genome Sequencing VCF"
    },
    "vcf_exome": {
        "marker_count_range": (100000, 3000000),
        "header_pattern": r"##fileformat=VCF",
        "description": "Whole Exome Sequencing VCF"
    },
}

# Chromosome expected coverage (approximate, varies by chip)
CHROMOSOME_EXPECTED_SNPS = {
    "1": (45000, 75000),
    "2": (45000, 70000),
    "3": (35000, 55000),
    "4": (30000, 50000),
    "5": (30000, 50000),
    "6": (35000, 55000),
    "7": (30000, 45000),
    "8": (25000, 40000),
    "9": (25000, 40000),
    "10": (25000, 40000),
    "11": (25000, 40000),
    "12": (25000, 40000),
    "13": (18000, 30000),
    "14": (17000, 28000),
    "15": (16000, 26000),
    "16": (17000, 28000),
    "17": (16000, 26000),
    "18": (15000, 24000),
    "19": (12000, 22000),
    "20": (13000, 22000),
    "21": (7000, 14000),
    "22": (8000, 14000),
    "X": (20000, 40000),
    "Y": (500, 5000),
    "MT": (100, 1000),
}


def detect_platform(
    genotypes: Dict[str, str],
    header_content: str = "",
    chromosome_counts: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    Detect the genotyping platform/chip used.
    
    Args:
        genotypes: Dict of rsid -> genotype
        header_content: File header content for pattern matching
        chromosome_counts: Pre-computed chromosome SNP counts
        
    Returns:
        Dict with platform detection results
    """
    total_snps = len(genotypes)
    
    result = {
        "detected_platform": "unknown",
        "confidence": "low",
        "total_snps": total_snps,
        "platform_details": None,
        "alternative_matches": []
    }
    
    # Check header patterns first
    header_lower = header_content.lower()
    for platform, sig in PLATFORM_SIGNATURES.items():
        pattern = sig.get("header_pattern", "")
        if pattern and re.search(pattern, header_lower, re.IGNORECASE):
            min_snps, max_snps = sig.get("marker_count_range", (0, float('inf')))
            if min_snps <= total_snps <= max_snps:
                result["detected_platform"] = platform
                result["confidence"] = "high"
                result["platform_details"] = sig
                break
    
    # If no header match, use SNP count
    if result["detected_platform"] == "unknown":
        matches = []
        for platform, sig in PLATFORM_SIGNATURES.items():
            min_snps, max_snps = sig.get("marker_count_range", (0, float('inf')))
            if min_snps <= total_snps <= max_snps:
                matches.append((platform, sig))
        
        if len(matches) == 1:
            result["detected_platform"] = matches[0][0]
            result["confidence"] = "moderate"
            result["platform_details"] = matches[0][1]
        elif len(matches) > 1:
            result["detected_platform"] = matches[0][0]
            result["confidence"] = "low"
            result["platform_details"] = matches[0][1]
            result["alternative_matches"] = [m[0] for m in matches[1:]]
    
    # Check signature SNPs for confirmation
    if result["detected_platform"] != "unknown":
        sig_snps = PLATFORM_SIGNATURES.get(result["detected_platform"], {}).get("signature_snps", [])
        if sig_snps:
            found = sum(1 for snp in sig_snps if snp in genotypes)
            if found == len(sig_snps):
                result["confidence"] = "high"
            elif found > 0:
                result["confidence"] = "moderate"
    
    return result


def analyze_call_rate(genotypes: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze genotype call rate and quality.
    
    Returns:
        Dict with call rate metrics
    """
    total = len(genotypes)
    
    # Count various call types
    valid_calls = 0
    no_calls = 0
    heterozygous = 0
    homozygous = 0
    insertions_deletions = 0
    
    no_call_patterns = ['--', '00', 'NC', 'NO CALL', '??', 'II', 'DD']
    
    for rsid, geno in genotypes.items():
        geno_upper = geno.upper()
        
        # Check for no-call
        if geno_upper in no_call_patterns or not geno or geno == '.':
            no_calls += 1
        elif len(geno) >= 2:
            valid_calls += 1
            # Check heterozygosity
            if geno[0] != geno[1]:
                heterozygous += 1
            else:
                homozygous += 1
            # Check for indels
            if 'I' in geno_upper or 'D' in geno_upper:
                insertions_deletions += 1
        else:
            valid_calls += 1
            homozygous += 1
    
    call_rate = valid_calls / total if total > 0 else 0
    het_rate = heterozygous / valid_calls if valid_calls > 0 else 0
    
    # Quality assessment
    if call_rate >= 0.98:
        quality = "excellent"
    elif call_rate >= 0.95:
        quality = "good"
    elif call_rate >= 0.90:
        quality = "acceptable"
    else:
        quality = "poor"
    
    # Het rate should be ~0.30-0.35 for humans
    het_quality = "normal"
    if het_rate < 0.25:
        het_quality = "low (possible consanguinity or sample issue)"
    elif het_rate > 0.45:
        het_quality = "high (possible contamination or error)"
    
    return {
        "total_snps": total,
        "valid_calls": valid_calls,
        "no_calls": no_calls,
        "call_rate": round(call_rate, 4),
        "call_rate_percent": round(call_rate * 100, 2),
        "quality_grade": quality,
        "heterozygosity": {
            "heterozygous_count": heterozygous,
            "homozygous_count": homozygous,
            "het_rate": round(het_rate, 4),
            "het_rate_percent": round(het_rate * 100, 2),
            "assessment": het_quality
        },
        "indels_detected": insertions_deletions,
        "warnings": _generate_call_rate_warnings(call_rate, het_rate, no_calls)
    }


def _generate_call_rate_warnings(call_rate: float, het_rate: float, no_calls: int) -> List[str]:
    """Generate quality warnings based on metrics."""
    warnings = []
    
    if call_rate < 0.90:
        warnings.append(f"LOW CALL RATE ({call_rate:.1%}) - Data quality may be compromised")
    elif call_rate < 0.95:
        warnings.append(f"Below-average call rate ({call_rate:.1%}) - Some results may be less reliable")
    
    if het_rate < 0.25:
        warnings.append("Low heterozygosity - possible sample quality issue or consanguinity")
    elif het_rate > 0.45:
        warnings.append("High heterozygosity - possible sample contamination")
    
    if no_calls > 50000:
        warnings.append(f"{no_calls:,} no-call positions detected")
    
    return warnings


def analyze_chromosome_coverage(
    genotypes: Dict[str, str],
    rsid_positions: Dict[str, Tuple[str, int]] = None
) -> Dict[str, Any]:
    """
    Analyze SNP coverage by chromosome.
    
    Args:
        genotypes: Dict of rsid -> genotype
        rsid_positions: Optional dict of rsid -> (chromosome, position)
        
    Returns:
        Dict with chromosome coverage analysis
    """
    # Initialize chromosome counts
    chrom_counts = defaultdict(int)
    chrom_no_calls = defaultdict(int)
    
    # If we don't have position data, we can't do chromosome analysis
    if rsid_positions is None:
        return {
            "status": "position_data_unavailable",
            "note": "Chromosome coverage analysis requires position mapping"
        }
    
    no_call_patterns = ['--', '00', 'NC', 'NO CALL', '??']
    
    for rsid, geno in genotypes.items():
        if rsid in rsid_positions:
            chrom, pos = rsid_positions[rsid]
            # Normalize chromosome name
            chrom = str(chrom).replace("chr", "").upper()
            
            chrom_counts[chrom] += 1
            
            if geno.upper() in no_call_patterns:
                chrom_no_calls[chrom] += 1
    
    # Analyze coverage
    coverage_results = {}
    warnings = []
    
    for chrom, count in chrom_counts.items():
        expected = CHROMOSOME_EXPECTED_SNPS.get(chrom)
        no_calls = chrom_no_calls.get(chrom, 0)
        call_rate = (count - no_calls) / count if count > 0 else 0
        
        coverage_results[chrom] = {
            "snp_count": count,
            "no_calls": no_calls,
            "call_rate": round(call_rate, 4),
        }
        
        if expected:
            min_exp, max_exp = expected
            coverage_results[chrom]["expected_range"] = expected
            
            if count < min_exp * 0.5:
                coverage_results[chrom]["coverage_status"] = "poor"
                warnings.append(f"Chromosome {chrom}: Low coverage ({count} vs expected {min_exp}-{max_exp})")
            elif count < min_exp:
                coverage_results[chrom]["coverage_status"] = "below_average"
            elif count > max_exp:
                coverage_results[chrom]["coverage_status"] = "above_average"
            else:
                coverage_results[chrom]["coverage_status"] = "normal"
    
    # Check for missing chromosomes
    expected_chroms = set(CHROMOSOME_EXPECTED_SNPS.keys())
    found_chroms = set(chrom_counts.keys())
    missing = expected_chroms - found_chroms
    
    if missing:
        warnings.append(f"Missing chromosome data: {', '.join(sorted(missing))}")
    
    # Determine sex from chromosome coverage
    sex_determination = "unknown"
    y_count = chrom_counts.get("Y", 0)
    x_count = chrom_counts.get("X", 0)
    
    if y_count > 100 and x_count > 5000:
        sex_determination = "male"
    elif y_count < 50 and x_count > 10000:
        sex_determination = "female"
    elif y_count < 50:
        sex_determination = "likely_female"
    
    return {
        "status": "success",
        "chromosomes_found": len(chrom_counts),
        "total_mapped": sum(chrom_counts.values()),
        "coverage_by_chromosome": coverage_results,
        "sex_determination": sex_determination,
        "warnings": warnings
    }


def calculate_confidence_score(
    rsid: str,
    genotype: str,
    platform: str = None,
    call_rate: float = None
) -> Dict[str, Any]:
    """
    Calculate confidence score for a specific variant call.
    
    Consumer array limitations:
    - Cannot distinguish imputed vs directly genotyped without manifest
    - Call quality not provided in exported files
    - Some chips have better coverage of certain regions
    
    Returns:
        Dict with confidence assessment
    """
    confidence = {
        "rsid": rsid,
        "genotype": genotype,
        "confidence_level": "standard",
        "directly_genotyped": "unknown",
        "notes": []
    }
    
    # Basic quality checks
    if not genotype or genotype in ['--', '00', 'NC']:
        confidence["confidence_level"] = "no_call"
        confidence["notes"].append("No genotype data available for this position")
        return confidence
    
    # Common high-quality markers (directly genotyped on most chips)
    high_confidence_markers = {
        "rs429358", "rs7412",  # APOE
        "rs1426654",  # SLC24A5 pigmentation
        "rs4680",  # COMT
        "rs12913832",  # Eye color
        "rs1799971",  # OPRM1
        "rs2187668",  # Celiac HLA
    }
    
    if rsid in high_confidence_markers:
        confidence["confidence_level"] = "high"
        confidence["directly_genotyped"] = "likely"
        confidence["notes"].append("Common marker present on all major consumer arrays")
    
    # Platform-specific considerations
    if platform:
        if "wgs" in platform.lower():
            confidence["confidence_level"] = "high"
            confidence["directly_genotyped"] = "yes"
            confidence["notes"].append("Whole genome sequencing provides direct genotyping")
        elif "nebula" in platform.lower():
            confidence["confidence_level"] = "moderate"
            confidence["directly_genotyped"] = "imputed"
            confidence["notes"].append("Low-pass WGS with imputation")
    
    # Call rate impact
    if call_rate is not None and call_rate < 0.95:
        if confidence["confidence_level"] == "high":
            confidence["confidence_level"] = "moderate"
        confidence["notes"].append(f"Overall call rate below optimal ({call_rate:.1%})")
    
    return confidence


def generate_quality_report(
    genotypes: Dict[str, str],
    header_content: str = "",
    rsid_positions: Dict[str, Tuple[str, int]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive quality report for the genetic data.
    
    Returns:
        Dict with complete quality analysis
    """
    # Platform detection
    platform = detect_platform(genotypes, header_content)
    
    # Call rate analysis
    call_rate = analyze_call_rate(genotypes)
    
    # Chromosome coverage (if position data available)
    chromosome_coverage = analyze_chromosome_coverage(genotypes, rsid_positions)
    
    # Overall quality assessment
    all_warnings = []
    all_warnings.extend(call_rate.get("warnings", []))
    if chromosome_coverage.get("warnings"):
        all_warnings.extend(chromosome_coverage["warnings"])
    
    # Determine overall grade
    if call_rate["quality_grade"] == "excellent" and len(all_warnings) == 0:
        overall_grade = "A"
        overall_description = "Excellent quality data"
    elif call_rate["quality_grade"] in ["excellent", "good"] and len(all_warnings) <= 1:
        overall_grade = "B"
        overall_description = "Good quality data with minor notes"
    elif call_rate["quality_grade"] in ["good", "acceptable"]:
        overall_grade = "C"
        overall_description = "Acceptable quality - some results may have lower confidence"
    else:
        overall_grade = "D"
        overall_description = "Data quality concerns - interpret results with caution"
    
    return {
        "summary": {
            "overall_grade": overall_grade,
            "description": overall_description,
            "total_snps": len(genotypes),
            "call_rate_percent": call_rate["call_rate_percent"],
            "platform": platform["detected_platform"],
            "platform_confidence": platform["confidence"],
        },
        "platform_detection": platform,
        "call_rate_analysis": call_rate,
        "chromosome_coverage": chromosome_coverage,
        "all_warnings": all_warnings,
        "recommendations": _generate_quality_recommendations(all_warnings, call_rate)
    }


def _generate_quality_recommendations(warnings: List[str], call_rate: Dict) -> List[str]:
    """Generate recommendations based on quality issues."""
    recommendations = []
    
    if call_rate["quality_grade"] == "poor":
        recommendations.append("Consider re-testing with a fresh sample if results seem inconsistent")
    
    if call_rate["heterozygosity"]["het_rate"] < 0.25:
        recommendations.append("Low heterozygosity detected - results may have reduced accuracy for heterozygous variants")
    
    if len(warnings) > 3:
        recommendations.append("Multiple quality warnings - treat low-confidence results with caution")
    
    if not recommendations:
        recommendations.append("Data quality is acceptable for consumer genetic analysis")
    
    return recommendations
