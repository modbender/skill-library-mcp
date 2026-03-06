#!/usr/bin/env python3
"""
Comprehensive Genetic Analysis - 1600+ Markers (v4.2.0)

Full health, pharmacogenomics, ancestry, traits, and actionable recommendations.
Works with ANY ancestry/ethnic background worldwide.

Supports:
    - 23andMe (v3, v4, v5)
    - AncestryDNA
    - MyHeritage
    - FamilyTreeDNA
    - Nebula Genomics
    - VCF files (whole genome/exome)

Privacy: All analysis runs locally. Zero network requests.

Output:
    - Human-readable reports
    - Agent-friendly JSON with actionable fields and priorities
    - Polygenic risk scores for major conditions
    - Evidence-based recommendations with citations
    - Lifestyle recommendation engine
    - Drug interaction matrix
    - Interactive HTML dashboard

Categories (21 total):
    1. Pharmacogenomics - Drug metabolism
    2. Polygenic Risk Scores - Disease risk
    3. Carrier Status - Recessive carriers
    4. Health Risks - Disease susceptibility
    5. Traits - Physical/behavioral
    6. Nutrition - Nutrigenomics
    7. Fitness - Athletic performance
    8. Neurogenetics - Cognition/behavior
    9. Longevity - Aging markers
    10. Immunity - HLA and immune
    11. Rare Diseases - Rare genetic conditions
    12. Mental Health - Psychiatric genetics
    13. Dermatology - Skin and hair
    14. Vision & Hearing - Sensory genetics
    15. Fertility - Reproductive health

Example:
    $ python comprehensive_analysis.py /path/to/dna_file.txt

    Or as a library:
    >>> from comprehensive_analysis import analyze_dna_file
    >>> results = analyze_dna_file('/path/to/dna_file.txt')
"""

from __future__ import annotations

import sys
import json
import gzip
import math
import re
import logging
import shutil
import webbrowser
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import (
    Dict, List, Optional, Any, Tuple, Union,
    TypedDict, Sequence, Mapping
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class GenotypeData(TypedDict, total=False):
    """Type definition for genotype data."""
    rsid: str
    chromosome: str
    position: int
    genotype: str


class MarkerInfo(TypedDict, total=False):
    """Type definition for marker information."""
    gene: str
    risk_allele: str
    effect_allele: str
    variant: str
    name: str
    condition: str
    conditions: List[str]
    trait: str
    effect: Union[str, Dict[str, str]]
    note: str
    evidence: str
    actionable: Dict[str, Any]


class AnalysisResult(TypedDict, total=False):
    """Type definition for category analysis results."""
    category: str
    total_in_database: int
    found_in_data: int
    risk_variants: int
    findings: List[Dict[str, Any]]
    actionable_items: List[Dict[str, Any]]


class APOEResult(TypedDict):
    """Type definition for APOE analysis results."""
    genotype: str
    risk_level: str
    rs429358: str
    rs7412: str
    interpretation: str
    actionable: bool
    recommendations: List[str]


class PRSResult(TypedDict, total=False):
    """Type definition for polygenic risk score results."""
    raw_score: float
    snps_found: int
    snps_total: int
    coverage: float
    percentile_estimate: Optional[int]
    confidence: str


# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = "4.2.0"
OUTPUT_DIR = Path.home() / "dna-analysis" / "reports"

# Valid rsID pattern
RSID_PATTERN = re.compile(r'^rs\d+$', re.IGNORECASE)

# Valid genotype pattern (1-2 alleles)
GENOTYPE_PATTERN = re.compile(r'^[ACGT]{1,2}$|^[ACGTDI]{1,2}$|^--$|^00$|^\?$', re.IGNORECASE)

# =============================================================================
# MODULE IMPORTS (with graceful fallback)
# =============================================================================

MODULES_LOADED = False

try:
    from markers.pharmacogenomics import PHARMACOGENOMICS_MARKERS, DRUG_INTERACTIONS
    from markers.polygenic_scores import PRS_WEIGHTS, PRS_CONDITIONS, calculate_prs
    from markers.carrier_status import CARRIER_MARKERS, CARRIER_SCREENING_PANELS
    from markers.health_risks import HEALTH_RISK_MARKERS
    from markers.traits import TRAIT_MARKERS
    from markers.nutrition import NUTRITION_MARKERS
    from markers.fitness import FITNESS_MARKERS
    from markers.neurogenetics import NEURO_MARKERS
    from markers.longevity import LONGEVITY_MARKERS
    from markers.immunity import IMMUNITY_MARKERS, HLA_DRUG_ALERTS
    from markers.rare_diseases import RARE_DISEASE_MARKERS
    from markers.mental_health import MENTAL_HEALTH_MARKERS
    from markers.dermatology import DERMATOLOGY_MARKERS
    from markers.vision_hearing import VISION_HEARING_MARKERS
    from markers.fertility import FERTILITY_MARKERS
    from markers import get_marker_counts
    MODULES_LOADED = True
except ImportError as e:
    logger.warning(f"Could not load marker modules: {e}")
    logger.warning("Using inline markers only.")
    PHARMACOGENOMICS_MARKERS: Dict[str, MarkerInfo] = {}
    DRUG_INTERACTIONS: Dict[str, Any] = {}
    PRS_WEIGHTS: Dict[str, Any] = {}
    PRS_CONDITIONS: Dict[str, Any] = {}
    CARRIER_MARKERS: Dict[str, MarkerInfo] = {}
    HEALTH_RISK_MARKERS: Dict[str, MarkerInfo] = {}
    TRAIT_MARKERS: Dict[str, MarkerInfo] = {}
    NUTRITION_MARKERS: Dict[str, MarkerInfo] = {}
    FITNESS_MARKERS: Dict[str, MarkerInfo] = {}
    NEURO_MARKERS: Dict[str, MarkerInfo] = {}
    LONGEVITY_MARKERS: Dict[str, MarkerInfo] = {}
    IMMUNITY_MARKERS: Dict[str, MarkerInfo] = {}
    HLA_DRUG_ALERTS: Dict[str, Any] = {}
    RARE_DISEASE_MARKERS: Dict[str, MarkerInfo] = {}
    MENTAL_HEALTH_MARKERS: Dict[str, MarkerInfo] = {}
    DERMATOLOGY_MARKERS: Dict[str, MarkerInfo] = {}
    VISION_HEARING_MARKERS: Dict[str, MarkerInfo] = {}
    FERTILITY_MARKERS: Dict[str, MarkerInfo] = {}
    CARRIER_SCREENING_PANELS: Dict[str, Any] = {}

    def get_marker_counts() -> Dict[str, int]:
        return {"total": 0}


# =============================================================================
# INPUT VALIDATION
# =============================================================================

def validate_rsid(rsid: str) -> bool:
    """
    Validate rsID format.

    Args:
        rsid: The rsID string to validate.

    Returns:
        True if valid rsID format, False otherwise.

    Examples:
        >>> validate_rsid("rs123456")
        True
        >>> validate_rsid("invalid")
        False
    """
    if not rsid or not isinstance(rsid, str):
        return False
    return bool(RSID_PATTERN.match(rsid))


def validate_genotype(genotype: str) -> bool:
    """
    Validate genotype format.

    Args:
        genotype: The genotype string to validate.

    Returns:
        True if valid genotype format, False otherwise.

    Examples:
        >>> validate_genotype("AG")
        True
        >>> validate_genotype("XYZ")
        False
    """
    if not genotype or not isinstance(genotype, str):
        return False
    return bool(GENOTYPE_PATTERN.match(genotype))


def validate_filepath(filepath: Union[str, Path]) -> Path:
    """
    Validate and resolve filepath.

    Args:
        filepath: Path to the file.

    Returns:
        Resolved Path object.

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If path is invalid.
    """
    if not filepath:
        raise ValueError("Filepath cannot be empty")

    path = Path(filepath).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    return path


def sanitize_genotype(genotype: str) -> str:
    """
    Sanitize and normalize genotype string.

    Args:
        genotype: Raw genotype string.

    Returns:
        Cleaned genotype string, or empty string if invalid.

    Examples:
        >>> sanitize_genotype("  AG  ")
        'AG'
        >>> sanitize_genotype("--")
        ''
    """
    if not genotype:
        return ""

    cleaned = genotype.strip().upper().replace(' ', '')

    # Handle no-call values
    if cleaned in ('--', '00', 'NC', 'N/A', '.', '?'):
        return ""

    # Normalize indels
    if 'D' in cleaned or 'I' in cleaned:
        return cleaned

    # Filter to valid nucleotides only
    valid_chars = set('ACGT')
    filtered = ''.join(c for c in cleaned if c in valid_chars)

    return filtered if len(filtered) in (1, 2) else ""


# =============================================================================
# FILE FORMAT DETECTION AND LOADING
# =============================================================================

def detect_format(filepath: Union[str, Path]) -> str:
    """
    Detect DNA file format from file contents.

    Args:
        filepath: Path to the DNA data file.

    Returns:
        Format string: 'vcf', '23andme', 'ancestry', 'myheritage', 'ftdna', or 'generic'.

    Raises:
        IOError: If file cannot be read.
    """
    filepath = str(filepath)

    if filepath.endswith('.vcf') or filepath.endswith('.vcf.gz'):
        return 'vcf'

    # Determine opener based on compression
    opener = gzip.open if filepath.endswith('.gz') else open
    mode = 'rt' if filepath.endswith('.gz') else 'r'

    try:
        with opener(filepath, mode, encoding='utf-8', errors='replace') as f:
            header_lines = []
            for i, line in enumerate(f):
                if i >= 20:
                    break
                header_lines.append(line)
    except IOError as e:
        logger.error(f"Error reading file header: {e}")
        raise

    content = ''.join(header_lines).lower()

    if '23andme' in content:
        return '23andme'
    elif 'ancestrydna' in content:
        return 'ancestry'
    elif 'myheritage' in content:
        return 'myheritage'
    elif 'ftdna' in content or 'family tree dna' in content:
        return 'ftdna'
    elif '#rsid' in content or 'rsid\t' in content:
        return 'generic'
    else:
        return 'generic'


def load_vcf(filepath: Union[str, Path]) -> Dict[str, str]:
    """
    Load VCF file into rsid -> genotype dictionary.

    Args:
        filepath: Path to VCF file (.vcf or .vcf.gz).

    Returns:
        Dictionary mapping rsIDs to genotype strings.

    Raises:
        IOError: If file cannot be read.
        ValueError: If file format is invalid.
    """
    genotypes: Dict[str, str] = {}
    filepath_str = str(filepath)

    opener = gzip.open if filepath_str.endswith('.gz') else open
    mode = 'rt' if filepath_str.endswith('.gz') else 'r'

    line_count = 0
    error_count = 0

    try:
        with opener(filepath_str, mode, encoding='utf-8', errors='replace') as f:
            for line in f:
                line_count += 1

                if line.startswith('#'):
                    continue

                parts = line.strip().split('\t')
                if len(parts) < 10:
                    continue

                try:
                    chrom, pos, rsid, ref, alt, qual, filt, info, fmt, sample = parts[:10]

                    if not validate_rsid(rsid):
                        continue

                    # Parse genotype
                    fmt_fields = fmt.split(':')
                    sample_fields = sample.split(':')

                    gt_idx = fmt_fields.index('GT') if 'GT' in fmt_fields else 0
                    gt = sample_fields[gt_idx] if gt_idx < len(sample_fields) else './.'

                    # Convert GT to alleles
                    alleles = [ref] + alt.split(',')
                    gt_parts = gt.replace('|', '/').split('/')

                    a1 = alleles[int(gt_parts[0])] if gt_parts[0] not in ('.', '') else '?'
                    a2 = alleles[int(gt_parts[1])] if len(gt_parts) > 1 and gt_parts[1] not in ('.', '') else a1

                    geno = sanitize_genotype(a1 + a2)
                    if geno:
                        genotypes[rsid] = geno

                except (ValueError, IndexError) as e:
                    error_count += 1
                    if error_count <= 5:
                        logger.debug(f"Line {line_count}: Parse error - {e}")
                    continue

    except IOError as e:
        logger.error(f"Error reading VCF file: {e}")
        raise

    if error_count > 5:
        logger.warning(f"Skipped {error_count} lines with parse errors")

    logger.info(f"Loaded {len(genotypes):,} variants from VCF")
    return genotypes


def load_consumer_format(filepath: Union[str, Path]) -> Dict[str, str]:
    """
    Load consumer DNA format (23andMe, Ancestry, etc.) into dictionary.

    Args:
        filepath: Path to DNA data file.

    Returns:
        Dictionary mapping rsIDs to genotype strings.

    Raises:
        IOError: If file cannot be read.
    """
    genotypes: Dict[str, str] = {}
    filepath_str = str(filepath)

    opener = gzip.open if filepath_str.endswith('.gz') else open
    mode = 'rt' if filepath_str.endswith('.gz') else 'r'

    line_count = 0
    error_count = 0

    try:
        with opener(filepath_str, mode, encoding='utf-8', errors='replace') as f:
            for line in f:
                line_count += 1

                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue

                # Try tab-separated first, then comma
                parts = line.strip().split('\t')
                if len(parts) < 4:
                    parts = line.strip().split(',')

                if len(parts) >= 4:
                    rsid = parts[0].strip()

                    if not validate_rsid(rsid):
                        continue

                    # Format: rsid, chrom, pos, genotype
                    raw_genotype = parts[3].strip()
                    genotype = sanitize_genotype(raw_genotype)

                    if genotype:
                        genotypes[rsid] = genotype

                elif len(parts) >= 2:
                    # Alternative format: rsid, genotype
                    rsid = parts[0].strip()
                    if validate_rsid(rsid):
                        genotype = sanitize_genotype(parts[1])
                        if genotype:
                            genotypes[rsid] = genotype

    except IOError as e:
        logger.error(f"Error reading DNA file: {e}")
        raise

    if error_count > 0:
        logger.warning(f"Skipped {error_count} lines with parse errors")

    logger.info(f"Loaded {len(genotypes):,} SNPs from consumer format")
    return genotypes


def load_dna_file(filepath: Union[str, Path]) -> Tuple[Dict[str, str], str]:
    """
    Load DNA data from any supported format.

    Args:
        filepath: Path to DNA data file.

    Returns:
        Tuple of (genotypes dict, format string).

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file format is unsupported or data is empty.

    Examples:
        >>> genotypes, fmt = load_dna_file("~/dna_data.txt")
        >>> print(f"Loaded {len(genotypes)} SNPs in {fmt} format")
    """
    path = validate_filepath(filepath)
    fmt = detect_format(path)

    logger.info(f"Detected format: {fmt}")

    if fmt == 'vcf':
        genotypes = load_vcf(path)
    else:
        genotypes = load_consumer_format(path)

    if not genotypes:
        raise ValueError(
            f"No valid genotypes found in file. "
            f"Please check file format and content."
        )

    return genotypes, fmt


# =============================================================================
# APOE DETERMINATION
# =============================================================================

def determine_apoe(genotypes: Dict[str, str]) -> APOEResult:
    """
    Determine APOE genotype from rs429358 and rs7412.

    APOE alleles:
        - ε2: rs429358=T, rs7412=T
        - ε3: rs429358=T, rs7412=C
        - ε4: rs429358=C, rs7412=C

    Args:
        genotypes: Dictionary mapping rsIDs to genotype strings.

    Returns:
        APOEResult with genotype, risk level, interpretation, and recommendations.

    Examples:
        >>> result = determine_apoe({"rs429358": "TT", "rs7412": "CC"})
        >>> print(result["genotype"])  # "ε3/ε3"
    """
    rs429358 = genotypes.get('rs429358', '')
    rs7412 = genotypes.get('rs7412', '')

    # Default unknown result
    unknown_result: APOEResult = {
        "genotype": "unknown",
        "risk_level": "unknown",
        "rs429358": rs429358,
        "rs7412": rs7412,
        "interpretation": "Unable to determine APOE status - missing marker data",
        "actionable": False,
        "recommendations": []
    }

    if not rs429358 or not rs7412:
        return unknown_result

    # Determine alleles
    alleles: List[str] = []
    for i in range(min(len(rs429358), len(rs7412))):
        c1 = rs429358[i].upper()
        c2 = rs7412[i].upper()

        if c1 == 'T' and c2 == 'T':
            alleles.append('ε2')
        elif c1 == 'T' and c2 == 'C':
            alleles.append('ε3')
        elif c1 == 'C' and c2 == 'C':
            alleles.append('ε4')

    if len(alleles) == 2:
        genotype = '/'.join(sorted(alleles))
    elif len(alleles) == 1:
        genotype = alleles[0] + '/' + alleles[0]
    else:
        return unknown_result

    # Risk information
    risk_info: Dict[str, Tuple[str, str]] = {
        'ε2/ε2': ('low', 'Protective. Lower Alzheimer\'s risk, but higher triglycerides.'),
        'ε2/ε3': ('low', 'Below average Alzheimer\'s risk.'),
        'ε3/ε3': ('average', 'Most common genotype. Average risk.'),
        'ε2/ε4': ('moderate', 'Mixed effects. ε2 partially offsets ε4.'),
        'ε3/ε4': ('elevated', '~3x Alzheimer\'s risk vs ε3/ε3. Lifestyle modifications important.'),
        'ε4/ε4': ('high', '~12x Alzheimer\'s risk. Exercise, diet, sleep, and cognitive engagement are protective.')
    }

    risk_level, interpretation = risk_info.get(genotype, ('unknown', 'Unable to interpret'))
    is_actionable = risk_level in ('elevated', 'high')

    recommendations: List[str] = []
    if is_actionable:
        recommendations = [
            "Regular aerobic exercise (strongest protective factor)",
            "Mediterranean diet",
            "7-8 hours quality sleep",
            "Cognitive engagement and social connection",
            "Cardiovascular risk factor management"
        ]

    return {
        "genotype": genotype,
        "risk_level": risk_level,
        "rs429358": rs429358,
        "rs7412": rs7412,
        "interpretation": interpretation,
        "actionable": is_actionable,
        "recommendations": recommendations
    }


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_markers(
    genotypes: Dict[str, str],
    markers: Dict[str, MarkerInfo],
    category: str
) -> AnalysisResult:
    """
    Analyze a category of genetic markers.

    Args:
        genotypes: Dictionary mapping rsIDs to genotype strings.
        markers: Dictionary of marker definitions for this category.
        category: Name of the marker category.

    Returns:
        AnalysisResult with findings and actionable items.

    Examples:
        >>> result = analyze_markers(genotypes, TRAIT_MARKERS, "traits")
        >>> print(f"Found {result['found_in_data']} markers")
    """
    if not isinstance(genotypes, dict):
        logger.error(f"Invalid genotypes type: {type(genotypes)}")
        return {
            "category": category,
            "total_in_database": 0,
            "found_in_data": 0,
            "risk_variants": 0,
            "findings": [],
            "actionable_items": []
        }

    if not isinstance(markers, dict):
        logger.warning(f"Invalid markers dict for {category}")
        markers = {}

    results: AnalysisResult = {
        "category": category,
        "total_in_database": len(markers),
        "found_in_data": 0,
        "risk_variants": 0,
        "findings": [],
        "actionable_items": []
    }

    for rsid, info in markers.items():
        if not validate_rsid(rsid):
            continue

        geno = genotypes.get(rsid)
        if not geno:
            continue

        results["found_in_data"] += 1

        # Determine if risk allele present
        risk_allele = info.get('risk_allele') or info.get('effect_allele', '')
        risk_count = 0
        if risk_allele:
            risk_count = geno.upper().count(risk_allele.upper())

        finding: Dict[str, Any] = {
            "rsid": rsid,
            "gene": info.get('gene', 'Unknown'),
            "genotype": geno,
            "risk_allele": risk_allele,
            "risk_copies": risk_count,
            "is_risk": risk_count > 0
        }

        # Add variant-specific info
        for key in ['variant', 'name', 'condition', 'conditions', 'trait', 'effect', 'note', 'evidence']:
            if key in info:
                finding[key] = info[key]

        if risk_count > 0:
            results["risk_variants"] += 1

            # Check for actionable items
            if 'actionable' in info and isinstance(info['actionable'], dict):
                action = {
                    "rsid": rsid,
                    "gene": info.get('gene'),
                    "genotype": geno,
                    **info['actionable']
                }
                results["actionable_items"].append(action)

        results["findings"].append(finding)

    return results


def calculate_all_prs(genotypes: Dict[str, str]) -> Dict[str, PRSResult]:
    """
    Calculate polygenic risk scores for all conditions.

    Args:
        genotypes: Dictionary mapping rsIDs to genotype strings.

    Returns:
        Dictionary mapping condition names to PRSResult.

    Examples:
        >>> prs = calculate_all_prs(genotypes)
        >>> print(prs["type_2_diabetes"]["percentile_estimate"])
    """
    if not PRS_WEIGHTS:
        return {"error": {"raw_score": 0, "snps_found": 0, "snps_total": 0, "coverage": 0, "confidence": "none"}}

    scores: Dict[str, PRSResult] = {}
    conditions = set(v.get('condition', '') for v in PRS_WEIGHTS.values() if 'condition' in v)

    for condition in conditions:
        if not condition:
            continue

        condition_snps = {k: v for k, v in PRS_WEIGHTS.items() if v.get('condition') == condition}

        score = 0.0
        found = 0

        for rsid, info in condition_snps.items():
            geno = genotypes.get(rsid)
            if geno:
                found += 1
                effect_allele = info.get('effect', '')
                beta = info.get('beta', 0)
                if effect_allele:
                    effect_count = geno.upper().count(effect_allele.upper())
                    score += effect_count * beta

        percentile: Optional[int] = None
        if found > 5:
            # Rough percentile estimation using z-score approximation
            z = score / math.sqrt(found * 0.5) if found > 0 else 0
            percentile = min(99, max(1, int(50 + z * 15)))

        coverage = round(found / len(condition_snps), 2) if condition_snps else 0
        confidence = "moderate" if found > len(condition_snps) * 0.5 else "low"

        scores[condition] = {
            "raw_score": round(score, 3),
            "snps_found": found,
            "snps_total": len(condition_snps),
            "coverage": coverage,
            "percentile_estimate": percentile,
            "confidence": confidence
        }

    return scores


# =============================================================================
# AGENT-FRIENDLY OUTPUT
# =============================================================================

def generate_agent_summary(all_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate structured output optimized for AI agents.

    Args:
        all_results: Complete analysis results dictionary.

    Returns:
        Dictionary with priority-sorted actionable items and key findings.

    Examples:
        >>> summary = generate_agent_summary(all_results)
        >>> print(len(summary["critical_alerts"]))
    """
    summary: Dict[str, Any] = {
        "analysis_timestamp": datetime.now().isoformat(),
        "version": VERSION,
        "snps_analyzed": all_results.get("total_snps", 0),
        "format_detected": all_results.get("format", "unknown"),

        # Priority-sorted actionable items
        "critical_alerts": [],
        "high_priority": [],
        "medium_priority": [],
        "low_priority": [],
        "informational": [],

        # Key health markers
        "apoe_status": all_results.get("apoe", {}),
        "pharmacogenomics_alerts": [],
        "carrier_status": [],
        "polygenic_risk_scores": all_results.get("prs", {}),

        # Traits and lifestyle
        "notable_traits": [],
        "nutrition_insights": [],
        "fitness_insights": [],

        # Lifestyle recommendations
        "lifestyle_recommendations": all_results.get("lifestyle_recommendations", {}),
        "drug_interaction_matrix": all_results.get("drug_interaction_matrix", {}),

        # Metadata
        "confidence_notes": [
            "Consumer arrays capture ~0.1% of genome",
            "Polygenic scores are probabilistic, not deterministic",
            "Many conditions depend heavily on environment and lifestyle",
            "These results are not diagnostic - consult healthcare providers"
        ]
    }

    # Collect all actionable items and sort by priority
    for category, results in all_results.items():
        if isinstance(results, dict) and "actionable_items" in results:
            for item in results["actionable_items"]:
                priority = item.get("priority", "informational")

                if priority == "critical":
                    summary["critical_alerts"].append(item)
                elif priority == "high":
                    summary["high_priority"].append(item)
                elif priority == "medium":
                    summary["medium_priority"].append(item)
                elif priority == "low":
                    summary["low_priority"].append(item)
                else:
                    summary["informational"].append(item)

                # Also add to specific categories
                if category == "pharmacogenomics":
                    summary["pharmacogenomics_alerts"].append(item)
                elif category == "carrier_status":
                    summary["carrier_status"].append(item)

    # Add notable traits
    if "traits" in all_results and isinstance(all_results["traits"], dict):
        for finding in all_results["traits"].get("findings", [])[:20]:
            if finding.get("effect"):
                summary["notable_traits"].append({
                    "trait": finding.get("trait") or finding.get("name"),
                    "gene": finding.get("gene"),
                    "genotype": finding.get("genotype"),
                    "interpretation": finding.get("effect")
                })

    return summary


# =============================================================================
# HUMAN-READABLE REPORT
# =============================================================================

def generate_report(all_results: Dict[str, Any], agent_summary: Dict[str, Any]) -> str:
    """
    Generate human-readable text report.

    Args:
        all_results: Complete analysis results.
        agent_summary: Agent-optimized summary.

    Returns:
        Formatted text report string.
    """
    lines: List[str] = []

    lines.append("=" * 78)
    lines.append("COMPREHENSIVE GENETIC ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Version: {VERSION}")
    lines.append("=" * 78)
    lines.append("")
    lines.append("IMPORTANT DISCLAIMERS:")
    lines.append("  * This is NOT medical advice")
    lines.append("  * Consult healthcare providers before acting on results")
    lines.append("  * Genetic risk does not equal destiny - lifestyle matters enormously")
    lines.append("  * Consumer arrays miss rare variants and structural changes")
    lines.append("")

    # Summary stats
    lines.append("-" * 78)
    lines.append("SUMMARY")
    lines.append("-" * 78)
    lines.append(f"SNPs in file: {all_results.get('total_snps', 'N/A'):,}")
    lines.append(f"File format: {all_results.get('format', 'Unknown')}")
    lines.append(f"Critical alerts: {len(agent_summary.get('critical_alerts', []))}")
    lines.append(f"High priority items: {len(agent_summary.get('high_priority', []))}")
    lines.append("")

    # APOE
    apoe = all_results.get("apoe", {})
    if apoe.get("genotype") != "unknown":
        lines.append("-" * 78)
        lines.append("APOE STATUS (Alzheimer's / Cardiovascular)")
        lines.append("-" * 78)
        lines.append(f"Genotype: {apoe.get('genotype')}")
        lines.append(f"Risk level: {apoe.get('risk_level')}")
        lines.append(f"Interpretation: {apoe.get('interpretation')}")
        if apoe.get("recommendations"):
            lines.append("Recommendations:")
            for rec in apoe["recommendations"]:
                lines.append(f"  - {rec}")
        lines.append("")

    # Critical alerts
    if agent_summary.get("critical_alerts"):
        lines.append("-" * 78)
        lines.append("!!! CRITICAL ALERTS - SHARE WITH HEALTHCARE PROVIDERS !!!")
        lines.append("-" * 78)
        for alert in agent_summary["critical_alerts"]:
            lines.append(f"\n  {alert.get('gene', 'Unknown')} ({alert.get('rsid')})")
            lines.append(f"  Genotype: {alert.get('genotype')}")
            for rec in alert.get("recommendations", []):
                lines.append(f"    * {rec}")
        lines.append("")

    # High priority
    if agent_summary.get("high_priority"):
        lines.append("-" * 78)
        lines.append("HIGH PRIORITY FINDINGS")
        lines.append("-" * 78)
        for item in agent_summary["high_priority"][:10]:
            lines.append(f"\n  {item.get('gene', 'Unknown')} ({item.get('rsid')})")
            lines.append(f"  Genotype: {item.get('genotype')}")
            if item.get("recommendations"):
                for rec in item["recommendations"][:3]:
                    lines.append(f"    - {rec}")
        lines.append("")

    # Pharmacogenomics
    if agent_summary.get("pharmacogenomics_alerts"):
        lines.append("-" * 78)
        lines.append("PHARMACOGENOMICS (Drug Response)")
        lines.append("-" * 78)
        for item in agent_summary["pharmacogenomics_alerts"][:15]:
            lines.append(f"  {item.get('gene')}: {item.get('genotype')} - {item.get('action_type', '')}")
        lines.append("")

    # Polygenic Risk Scores
    prs = all_results.get("prs", {})
    if prs and not prs.get("error"):
        lines.append("-" * 78)
        lines.append("POLYGENIC RISK SCORES")
        lines.append("-" * 78)
        for condition, scores in prs.items():
            if isinstance(scores, dict) and scores.get("percentile_estimate"):
                lines.append(f"  {condition}: {scores['percentile_estimate']}th percentile "
                           f"(confidence: {scores.get('confidence', 'unknown')})")
        lines.append("")

    # Traits
    if agent_summary.get("notable_traits"):
        lines.append("-" * 78)
        lines.append("NOTABLE TRAITS")
        lines.append("-" * 78)
        for trait in agent_summary["notable_traits"][:15]:
            interp = trait.get("interpretation", "")
            if isinstance(interp, dict):
                interp = interp.get(trait.get("genotype"), str(interp))
            interp_str = str(interp)[:60]
            lines.append(f"  {trait.get('trait')}: {interp_str}...")
        lines.append("")

    lines.append("=" * 78)
    lines.append("END OF REPORT")
    lines.append("=" * 78)

    return "\n".join(lines)


# =============================================================================
# LIFESTYLE RECOMMENDATIONS
# =============================================================================

def generate_lifestyle_recommendations(all_results: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Generate personalized lifestyle recommendations based on genetic profile.

    Args:
        all_results: Complete analysis results.

    Returns:
        Dictionary with categorized recommendations.
    """
    recommendations: Dict[str, List[str]] = {
        "diet": [],
        "exercise": [],
        "supplements": [],
        "screening": [],
        "lifestyle": [],
        "avoid": []
    }

    # APOE-based recommendations
    apoe = all_results.get("apoe", {})
    if apoe.get("risk_level") in ("elevated", "high"):
        recommendations["diet"].extend([
            "Mediterranean diet - strongly protective for APOE4 carriers",
            "Limit saturated fat intake",
            "Include fatty fish 2-3x/week (omega-3s)"
        ])
        recommendations["exercise"].extend([
            "Regular aerobic exercise - strongest protective factor",
            "150+ minutes moderate exercise weekly"
        ])
        recommendations["lifestyle"].append("Prioritize 7-8 hours quality sleep")

    # Nutrition-based
    nutrition = all_results.get("nutrition", {})
    if isinstance(nutrition, dict):
        for finding in nutrition.get("findings", []):
            gene = finding.get("gene", "")
            if finding.get("risk_copies", 0) > 0:
                if gene == "MTHFR":
                    recommendations["supplements"].append("Consider methylfolate over folic acid")
                elif gene == "VDR":
                    recommendations["supplements"].append("Vitamin D supplementation may be beneficial")
                elif "caffeine" in str(finding.get("trait", "")).lower():
                    recommendations["avoid"].append("Limit caffeine if slow metabolizer")

    # Fitness-based
    fitness = all_results.get("fitness", {})
    if isinstance(fitness, dict):
        for finding in fitness.get("findings", []):
            gene = finding.get("gene", "")
            if gene == "ACTN3" and finding.get("genotype") == "TT":
                recommendations["exercise"].append("Favor endurance over power training (ACTN3 XX)")
            elif gene == "COL5A1" and finding.get("risk_copies", 0) > 0:
                recommendations["exercise"].append("Include tendon-strengthening exercises")

    # Dermatology-based
    dermatology = all_results.get("dermatology", {})
    if isinstance(dermatology, dict):
        for finding in dermatology.get("findings", []):
            gene = finding.get("gene", "")
            if gene == "MC1R" and finding.get("risk_copies", 0) > 0:
                recommendations["lifestyle"].append("Strict sun protection - elevated melanoma risk")
                recommendations["screening"].append("Annual dermatology screening recommended")

    # Vision-based
    vision = all_results.get("vision_hearing", {})
    if isinstance(vision, dict):
        for finding in vision.get("findings", []):
            gene = finding.get("gene", "")
            if gene == "CFH" and finding.get("risk_copies", 0) > 0:
                recommendations["screening"].append("Annual dilated eye exam after age 50 (AMD risk)")
                recommendations["supplements"].append("AREDS2 formula if AMD develops")
                recommendations["avoid"].append("CRITICAL: Do not smoke (dramatically increases AMD risk)")

    return recommendations


def generate_drug_interaction_matrix(all_results: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate drug interaction warnings based on pharmacogenomics.

    Args:
        all_results: Complete analysis results.

    Returns:
        Dictionary with categorized drug interactions.
    """
    matrix: Dict[str, List[Dict[str, Any]]] = {
        "critical_interactions": [],
        "warnings": [],
        "dosing_adjustments": [],
        "safe_alternatives": []
    }

    pharma = all_results.get("pharmacogenomics", {})
    if not isinstance(pharma, dict):
        return matrix

    for finding in pharma.get("findings", []):
        gene = finding.get("gene", "")
        geno = finding.get("genotype", "")
        risk = finding.get("risk_copies", 0)

        # DPYD - 5-FU toxicity
        if gene == "DPYD" and risk > 0:
            matrix["critical_interactions"].append({
                "drug_class": "Fluoropyrimidines",
                "drugs": ["5-FU", "capecitabine", "tegafur"],
                "risk": "FATAL TOXICITY - avoid or reduce dose significantly",
                "gene": gene,
                "genotype": geno
            })

        # CYP2C19 - clopidogrel
        if gene == "CYP2C19":
            if "AA" in geno:  # Poor metabolizer
                matrix["warnings"].append({
                    "drug": "Clopidogrel (Plavix)",
                    "issue": "Poor activation - reduced efficacy",
                    "recommendation": "Consider prasugrel or ticagrelor",
                    "gene": gene,
                    "genotype": geno
                })

        # CYP2D6 - opioids
        if gene == "CYP2D6":
            if risk == 0:  # Poor metabolizer
                matrix["dosing_adjustments"].append({
                    "drug_class": "Codeine, tramadol",
                    "issue": "No activation to active metabolite",
                    "recommendation": "Use alternative analgesics (morphine, oxycodone)",
                    "gene": gene,
                    "genotype": geno
                })

        # SLCO1B1 - statins
        if gene == "SLCO1B1" and risk > 0:
            matrix["warnings"].append({
                "drug": "Simvastatin",
                "issue": "Elevated myopathy risk",
                "recommendation": "Limit to 20mg/day or use alternative statin",
                "gene": gene,
                "genotype": geno
            })

        # Warfarin dosing
        if gene in ("CYP2C9", "VKORC1") and risk > 0:
            matrix["dosing_adjustments"].append({
                "drug": "Warfarin",
                "issue": "May require lower dose",
                "recommendation": "Use pharmacogenomic dosing algorithms",
                "gene": gene,
                "genotype": geno
            })

    return matrix


# =============================================================================
# DASHBOARD GENERATION
# =============================================================================

def generate_dashboard(
    json_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    auto_open: bool = False
) -> Path:
    """
    Generate interactive HTML dashboard from analysis results.

    Args:
        json_path: Path to agent_summary.json or full_analysis.json.
        output_path: Output path for dashboard HTML. Defaults to same directory.
        auto_open: Whether to open dashboard in browser after generation.

    Returns:
        Path to generated dashboard HTML file.

    Raises:
        FileNotFoundError: If JSON file or dashboard template not found.

    Examples:
        >>> path = generate_dashboard("~/dna-analysis/reports/agent_summary.json")
        >>> print(f"Dashboard generated at {path}")
    """
    json_path = validate_filepath(json_path)

    if output_path is None:
        output_path = json_path.parent / "dashboard.html"
    else:
        output_path = Path(output_path).expanduser().resolve()

    # Find dashboard template
    template_locations = [
        Path(__file__).parent / "dashboard" / "index.html",
        Path(__file__).parent / "dashboard.html",
    ]

    template_path: Optional[Path] = None
    for loc in template_locations:
        if loc.exists():
            template_path = loc
            break

    if template_path is None:
        raise FileNotFoundError(
            "Dashboard template not found. Expected at: "
            f"{template_locations[0]}"
        )

    # Read JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Inject data into template (auto-load feature)
    data_json = json.dumps(data, indent=2, default=str)
    inject_script = f"""
    <script>
        // Auto-loaded data from analysis
        window.autoLoadData = {data_json};

        // Auto-render on load
        document.addEventListener('DOMContentLoaded', function() {{
            if (window.autoLoadData) {{
                data = window.autoLoadData;
                document.getElementById('initial-state').classList.add('hidden');
                document.getElementById('dashboard-content').classList.remove('hidden');
                document.getElementById('main-nav').classList.remove('hidden');
                renderDashboard();
            }}
        }});
    </script>
    </body>
    """

    # Insert auto-load script before closing body tag
    dashboard_html = template.replace('</body>', inject_script)

    # Write dashboard
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

    logger.info(f"Dashboard generated: {output_path}")

    if auto_open:
        try:
            webbrowser.open(f'file://{output_path}')
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")

    return output_path


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_dna_file(
    filepath: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    generate_html_dashboard: bool = True,
    auto_open_dashboard: bool = False
) -> Dict[str, Any]:
    """
    Run complete genetic analysis on a DNA data file.

    This is the main entry point for programmatic usage.

    Args:
        filepath: Path to DNA data file (23andMe, AncestryDNA, VCF, etc.).
        output_dir: Directory for output files. Defaults to ~/dna-analysis/reports/.
        generate_html_dashboard: Whether to generate interactive HTML dashboard.
        auto_open_dashboard: Whether to open dashboard in browser.

    Returns:
        Complete analysis results dictionary.

    Raises:
        FileNotFoundError: If input file not found.
        ValueError: If file format is invalid or no data found.

    Examples:
        >>> results = analyze_dna_file("~/23andme_data.txt")
        >>> print(f"Found {results['total_snps']} SNPs")
        >>> print(f"APOE: {results['apoe']['genotype']}")
    """
    # Validate and set output directory
    if output_dir is None:
        output_dir = OUTPUT_DIR
    else:
        output_dir = Path(output_dir).expanduser().resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    logger.info(f"Loading {filepath}...")
    genotypes, fmt = load_dna_file(filepath)
    logger.info(f"Loaded {len(genotypes):,} SNPs")

    # Initialize results
    all_results: Dict[str, Any] = {
        "total_snps": len(genotypes),
        "format": fmt,
        "apoe": determine_apoe(genotypes),
        "version": VERSION
    }

    logger.info("Analyzing markers...")

    if MODULES_LOADED:
        # Core categories
        all_results["pharmacogenomics"] = analyze_markers(genotypes, PHARMACOGENOMICS_MARKERS, "pharmacogenomics")
        all_results["carrier_status"] = analyze_markers(genotypes, CARRIER_MARKERS, "carrier_status")
        all_results["health_risks"] = analyze_markers(genotypes, HEALTH_RISK_MARKERS, "health_risks")
        all_results["traits"] = analyze_markers(genotypes, TRAIT_MARKERS, "traits")
        all_results["nutrition"] = analyze_markers(genotypes, NUTRITION_MARKERS, "nutrition")
        all_results["fitness"] = analyze_markers(genotypes, FITNESS_MARKERS, "fitness")
        all_results["neurogenetics"] = analyze_markers(genotypes, NEURO_MARKERS, "neurogenetics")
        all_results["longevity"] = analyze_markers(genotypes, LONGEVITY_MARKERS, "longevity")
        all_results["immunity"] = analyze_markers(genotypes, IMMUNITY_MARKERS, "immunity")
        all_results["prs"] = calculate_all_prs(genotypes)

        # Extended categories
        all_results["rare_diseases"] = analyze_markers(genotypes, RARE_DISEASE_MARKERS, "rare_diseases")
        all_results["mental_health"] = analyze_markers(genotypes, MENTAL_HEALTH_MARKERS, "mental_health")
        all_results["dermatology"] = analyze_markers(genotypes, DERMATOLOGY_MARKERS, "dermatology")
        all_results["vision_hearing"] = analyze_markers(genotypes, VISION_HEARING_MARKERS, "vision_hearing")
        all_results["fertility"] = analyze_markers(genotypes, FERTILITY_MARKERS, "fertility")

        # Advanced features
        all_results["lifestyle_recommendations"] = generate_lifestyle_recommendations(all_results)
        all_results["drug_interaction_matrix"] = generate_drug_interaction_matrix(all_results)

    # Generate outputs
    logger.info("Generating reports...")

    agent_summary = generate_agent_summary(all_results)
    report = generate_report(all_results, agent_summary)

    # Save files
    full_json_path = output_dir / "full_analysis.json"
    summary_json_path = output_dir / "agent_summary.json"
    report_path = output_dir / "report.txt"

    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)

    with open(summary_json_path, 'w', encoding='utf-8') as f:
        json.dump(agent_summary, f, indent=2, default=str)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Output files saved to: {output_dir}/")

    # Generate dashboard
    if generate_html_dashboard:
        try:
            dashboard_path = generate_dashboard(
                summary_json_path,
                output_dir / "dashboard.html",
                auto_open=auto_open_dashboard
            )
            all_results["dashboard_path"] = str(dashboard_path)
        except Exception as e:
            logger.warning(f"Could not generate dashboard: {e}")

    return all_results


# =============================================================================
# CLI MAIN
# =============================================================================

def main() -> int:
    """
    Command-line interface entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    if len(sys.argv) < 2:
        print(f"Personal Genomics Analysis Tool v{VERSION}")
        print("=" * 40)
        print("\nUsage: python comprehensive_analysis.py <dna_file> [--no-dashboard] [--open]")
        print("\nSupported formats:")
        print("  - 23andMe (v3, v4, v5)")
        print("  - AncestryDNA")
        print("  - MyHeritage")
        print("  - FamilyTreeDNA")
        print("  - VCF (whole genome/exome)")
        print("  - Any tab-delimited rsid format")
        print("\nOptions:")
        print("  --no-dashboard  Skip HTML dashboard generation")
        print("  --open          Auto-open dashboard in browser")
        print(f"\nMarker modules loaded: {MODULES_LOADED}")
        if MODULES_LOADED:
            counts = get_marker_counts()
            print(f"Total markers in database: {counts.get('total', 0):,}")
            print("\nCategories:")
            for k, v in counts.items():
                if k != 'total':
                    print(f"  {k}: {v}")
        return 1

    filepath = sys.argv[1]
    generate_dashboard_flag = '--no-dashboard' not in sys.argv
    auto_open = '--open' in sys.argv

    try:
        all_results = analyze_dna_file(
            filepath,
            generate_html_dashboard=generate_dashboard_flag,
            auto_open_dashboard=auto_open
        )

        # Generate and print report
        agent_summary = generate_agent_summary(all_results)
        report = generate_report(all_results, agent_summary)
        print("\n" + report)

        print(f"\nOutput files saved to: {OUTPUT_DIR}/")
        print(f"  - full_analysis.json    (complete data)")
        print(f"  - agent_summary.json    (AI-optimized)")
        print(f"  - report.txt            (human-readable)")
        if generate_dashboard_flag:
            print(f"  - dashboard.html        (interactive visualization)")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\nError: {e}")
        print("Please check the file path and try again.")
        return 1

    except ValueError as e:
        logger.error(f"Invalid data: {e}")
        print(f"\nError: {e}")
        print("Please ensure the file contains valid DNA data.")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nUnexpected error: {e}")
        print("Please report this issue if it persists.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
