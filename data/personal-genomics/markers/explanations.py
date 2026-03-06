"""
Natural Language Explanations v4.1.0
Provides plain-English interpretations of genetic findings with:
- Jargon-free explanations
- Calibrated uncertainty language
- Practical implications
- Research variant flagging with PubMed links

This module transforms technical genetic data into accessible insights.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EvidenceLevel(Enum):
    """Evidence quality levels for genetic findings."""
    ESTABLISHED = "established"        # Clinical guidelines, FDA labels
    WELL_SUPPORTED = "well_supported"  # Multiple large studies, replicated
    MODERATE = "moderate"              # Some good studies, needs more replication
    EMERGING = "emerging"              # Recent research, preliminary findings
    EXPERIMENTAL = "experimental"      # Very early research, not clinical


class CertaintyLevel(Enum):
    """How certain we can be about the interpretation."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


# =============================================================================
# PUBMED REFERENCE DATABASE
# =============================================================================

PUBMED_REFERENCES: Dict[str, Dict[str, Any]] = {
    # Pharmacogenomics - Clinical Guidelines
    "rs3892097": {
        "gene": "CYP2D6",
        "pmids": ["22205192", "17622591", "25974703"],
        "primary_paper": "22205192",
        "title": "CPIC Guideline for CYP2D6 and Codeine Therapy",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Crews KR et al. Clin Pharmacol Ther. 2012"
    },
    "rs4244285": {
        "gene": "CYP2C19",
        "pmids": ["20801498", "22992668", "23698643"],
        "primary_paper": "20801498",
        "title": "CPIC Guideline for CYP2C19 and Clopidogrel",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Scott SA et al. Clin Pharmacol Ther. 2011"
    },
    "rs1799853": {
        "gene": "CYP2C9",
        "pmids": ["21900891", "28198005"],
        "primary_paper": "21900891",
        "title": "CPIC Guideline for Warfarin Dosing",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Johnson JA et al. Clin Pharmacol Ther. 2011"
    },
    "rs3918290": {
        "gene": "DPYD",
        "pmids": ["29152729", "28881920", "23988873"],
        "primary_paper": "29152729",
        "title": "CPIC Guideline for Fluoropyrimidines and DPYD",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Amstutz U et al. Clin Pharmacol Ther. 2018"
    },
    
    # APOE
    "rs429358": {
        "gene": "APOE",
        "pmids": ["9343467", "23489627", "25024455"],
        "primary_paper": "9343467",
        "title": "APOE and Alzheimer's Disease Meta-Analysis",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Farrer LA et al. JAMA. 1997"
    },
    
    # Fitness
    "rs1815739": {
        "gene": "ACTN3",
        "pmids": ["21448267", "12879365", "14593171"],
        "primary_paper": "12879365",
        "title": "ACTN3 Genotype and Athletic Performance",
        "evidence_level": EvidenceLevel.WELL_SUPPORTED,
        "citation": "Yang N et al. Am J Hum Genet. 2003"
    },
    
    # Nutrition
    "rs1801133": {
        "gene": "MTHFR",
        "pmids": ["25853894", "7647779", "12055160"],
        "primary_paper": "7647779",
        "title": "MTHFR Thermolabile Variant and Homocysteine",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Frosst P et al. Nat Genet. 1995"
    },
    "rs4988235": {
        "gene": "LCT",
        "pmids": ["12185609", "15114531"],
        "primary_paper": "12185609",
        "title": "Lactase Persistence in Europeans",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Enattah NS et al. Nat Genet. 2002"
    },
    
    # Sleep
    "rs762551": {
        "gene": "CYP1A2",
        "pmids": ["16522833", "26554680", "17962509"],
        "primary_paper": "16522833",
        "title": "Coffee, CYP1A2 Genotype, and Myocardial Infarction",
        "evidence_level": EvidenceLevel.WELL_SUPPORTED,
        "citation": "Cornelis MC et al. JAMA. 2006"
    },
    "rs5751876": {
        "gene": "ADORA2A",
        "pmids": ["16213838", "22080499"],
        "primary_paper": "16213838",
        "title": "ADORA2A and Caffeine-Induced Anxiety",
        "evidence_level": EvidenceLevel.WELL_SUPPORTED,
        "citation": "Retey JV et al. Eur J Neurosci. 2007"
    },
    
    # Pigmentation
    "rs1805007": {
        "gene": "MC1R",
        "pmids": ["11230166", "18488028", "10888885"],
        "primary_paper": "11230166",
        "title": "MC1R Variants and Skin Cancer Risk",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Palmer JS et al. Am J Hum Genet. 2000"
    },
    "rs1426654": {
        "gene": "SLC24A5",
        "pmids": ["15695382"],
        "primary_paper": "15695382",
        "title": "SLC24A5 and Skin Pigmentation",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Lamason RL et al. Science. 2005"
    },
    
    # Alcohol
    "rs671": {
        "gene": "ALDH2",
        "pmids": ["19624168", "16971766", "22897848"],
        "primary_paper": "16971766",
        "title": "ALDH2 and Esophageal Cancer Risk",
        "evidence_level": EvidenceLevel.ESTABLISHED,
        "citation": "Lewis SJ et al. PLoS Med. 2006"
    }
}


# =============================================================================
# RESEARCH VARIANTS (Emerging)
# =============================================================================

RESEARCH_VARIANTS: Dict[str, Dict[str, Any]] = {
    "rs10830963": {
        "gene": "MTNR1B",
        "trait": "Melatonin receptor / Sleep timing",
        "status": "emerging",
        "research_context": "Linked to type 2 diabetes risk and melatonin signaling. Active research on meal timing interactions.",
        "pmids": ["19079262", "29566165"],
        "note": "Clinical implications still being established"
    },
    "rs6265": {
        "gene": "BDNF",
        "trait": "Brain plasticity / Exercise response",
        "status": "emerging",
        "research_context": "Met allele associated with altered hippocampal function. Exercise may compensate for genetic effects.",
        "pmids": ["14976042", "17151862"],
        "note": "Cognitive effects complex and context-dependent"
    },
    "rs53576": {
        "gene": "OXTR",
        "trait": "Oxytocin receptor / Social behavior",
        "status": "emerging",
        "research_context": "Association with empathy and social behavior studied but effects are small and context-dependent.",
        "pmids": ["21151117", "25769746"],
        "note": "Media often overstates findings. Effect sizes are modest."
    },
    "rs4680": {
        "gene": "COMT",
        "trait": "Dopamine metabolism / Stress response",
        "status": "moderate",
        "research_context": "Well-replicated for cognitive and pain outcomes, but 'warrior vs worrier' framing is oversimplified.",
        "pmids": ["18181169", "17194260"],
        "note": "Effects depend heavily on context and other genes"
    },
    "rs12934922": {
        "gene": "TERT",
        "trait": "Telomerase / Longevity",
        "status": "emerging",
        "research_context": "Associated with telomere length in some studies. Longevity implications still being researched.",
        "pmids": ["20018825"],
        "note": "Telomere-longevity relationship is complex"
    }
}


# =============================================================================
# EXPLANATION TEMPLATES
# =============================================================================

EXPLANATION_TEMPLATES = {
    "established": {
        "confidence": "This finding is based on well-established clinical guidelines.",
        "action": "This information may be medically relevant. Consider discussing with your healthcare provider.",
        "source": "Source: Clinical Pharmacogenetics Implementation Consortium (CPIC) guidelines"
    },
    "well_supported": {
        "confidence": "This finding is supported by multiple scientific studies.",
        "action": "While not yet clinical standard-of-care, this information is well-supported by research.",
        "source": "Source: Published genetic association studies"
    },
    "moderate": {
        "confidence": "This finding is supported by some research, though more studies are needed.",
        "action": "Consider this as one piece of information among many. Not diagnostic.",
        "source": "Source: Published research (replication ongoing)"
    },
    "emerging": {
        "confidence": "⚡ RESEARCH NOTE: This is an active area of scientific investigation.",
        "action": "These findings are preliminary. Do not make major decisions based solely on this.",
        "source": "Source: Early-stage research"
    },
    "experimental": {
        "confidence": "🔬 EXPERIMENTAL: Very early research. Findings may change.",
        "action": "For educational interest only. Not clinically validated.",
        "source": "Source: Preliminary studies"
    }
}


# =============================================================================
# NATURAL LANGUAGE GENERATION
# =============================================================================

def generate_plain_english_explanation(
    rsid: str,
    gene: str,
    genotype: str,
    trait: str,
    finding: str,
    evidence_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Generate a plain-English explanation of a genetic finding.
    """
    # Get evidence template
    evidence_enum = EvidenceLevel(evidence_level) if evidence_level in [e.value for e in EvidenceLevel] else EvidenceLevel.MODERATE
    template = EXPLANATION_TEMPLATES.get(evidence_enum.value, EXPLANATION_TEMPLATES["moderate"])
    
    # Build explanation
    explanation = {
        "summary": "",
        "what_it_means": "",
        "practical_implications": "",
        "confidence_note": template["confidence"],
        "action_suggestion": template["action"],
        "evidence_level": evidence_level,
        "is_research_variant": rsid in RESEARCH_VARIANTS,
        "pubmed_links": []
    }
    
    # Get PubMed references
    if rsid in PUBMED_REFERENCES:
        ref = PUBMED_REFERENCES[rsid]
        explanation["pubmed_links"] = [
            {
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            for pmid in ref.get("pmids", [])[:3]
        ]
        explanation["primary_citation"] = ref.get("citation", "")
    
    # Research variant flag
    if rsid in RESEARCH_VARIANTS:
        rv = RESEARCH_VARIANTS[rsid]
        explanation["research_context"] = rv.get("research_context", "")
        explanation["research_note"] = rv.get("note", "")
    
    # Generate natural language summary
    explanation["summary"] = _build_summary(gene, genotype, trait, finding)
    explanation["what_it_means"] = _build_meaning(gene, finding, evidence_level)
    explanation["practical_implications"] = _build_implications(gene, finding)
    
    return explanation


def _build_summary(gene: str, genotype: str, trait: str, finding: str) -> str:
    """Build a plain-English summary sentence."""
    # Clean up finding for natural language
    finding_clean = finding.replace("_", " ").lower()
    
    return f"Your {gene} gene variant ({genotype}) is associated with {finding_clean}."


def _build_meaning(gene: str, finding: str, evidence_level: str) -> str:
    """Explain what the finding means in practical terms."""
    certainty_phrases = {
        "established": "Research strongly supports that",
        "well_supported": "Studies suggest that",
        "moderate": "Some research indicates that",
        "emerging": "Preliminary research suggests that",
        "experimental": "Very early research hints that"
    }
    
    certainty = certainty_phrases.get(evidence_level, "Research suggests that")
    
    return f"{certainty} this variant may affect how your body handles {_make_readable(finding)}."


def _build_implications(gene: str, finding: str) -> str:
    """Generate practical implications."""
    # Gene-specific practical implications
    implications = {
        "CYP2D6": "This may affect how you metabolize certain medications, including some pain relievers and antidepressants.",
        "CYP2C19": "This may affect how you respond to certain medications, particularly blood thinners and acid reducers.",
        "CYP2C9": "This may affect how you metabolize warfarin and some other medications.",
        "CYP1A2": "This affects how quickly your body processes caffeine.",
        "APOE": "This is related to cholesterol metabolism and may be relevant for heart and brain health.",
        "ACTN3": "This relates to muscle fiber composition and athletic performance tendencies.",
        "MTHFR": "This affects folate metabolism, which may have implications for B vitamin needs.",
        "LCT": "This determines whether you can digest lactose (the sugar in milk) as an adult.",
        "ALDH2": "This affects how your body processes alcohol.",
        "MC1R": "This affects skin pigmentation and sun sensitivity."
    }
    
    return implications.get(gene, "The practical implications of this variant are still being studied.")


def _make_readable(text: str) -> str:
    """Convert technical text to readable form."""
    replacements = {
        "poor_metabolizer": "medication processing",
        "ultrarapid_metabolizer": "medication processing",
        "increased_risk": "certain conditions",
        "decreased_risk": "certain conditions",
        "caffeine_metabolism": "caffeine",
        "lactase_persistence": "dairy digestion",
        "alcohol_flush": "alcohol processing"
    }
    
    for tech, readable in replacements.items():
        text = text.replace(tech, readable)
    
    return text.lower().replace("_", " ")


def explain_risk_in_context(
    relative_risk: float,
    baseline_risk: float,
    condition: str
) -> str:
    """
    Explain relative risk in understandable terms.
    
    Example: "2x risk" for a 5% baseline = 10% absolute risk,
    which means 90% of people with this variant will NOT develop the condition.
    """
    absolute_risk = baseline_risk * relative_risk
    inverse_absolute = (1 - absolute_risk) * 100
    
    if relative_risk < 1.2:
        impact = "slightly"
    elif relative_risk < 1.5:
        impact = "modestly"
    elif relative_risk < 2.0:
        impact = "moderately"
    elif relative_risk < 3.0:
        impact = "substantially"
    else:
        impact = "significantly"
    
    explanation = (
        f"This variant {impact} affects risk for {condition}. "
        f"The relative risk is {relative_risk}x, which sounds dramatic but let's put it in context: "
        f"Even with this variant, approximately {inverse_absolute:.0f}% of people would NOT develop {condition}. "
        f"Genetics is just one factor—lifestyle, environment, and other genes also matter."
    )
    
    return explanation


def generate_uncertainty_statement(evidence_level: str, sample_size: str = "moderate") -> str:
    """Generate appropriate uncertainty language."""
    statements = {
        "established": (
            "This finding is based on clinical guidelines used in medical practice. "
            "While genetics doesn't guarantee outcomes, this information is considered clinically actionable."
        ),
        "well_supported": (
            "This finding is supported by multiple large studies. "
            "However, genetic associations are probabilistic, not deterministic—your actual outcome depends on many factors."
        ),
        "moderate": (
            "This finding has some scientific support but requires more research. "
            "Consider it informative but not definitive."
        ),
        "emerging": (
            "This is an active research area with preliminary findings. "
            "The science may evolve significantly. Do not make major decisions based on this alone."
        ),
        "experimental": (
            "This is very early research that may not replicate. "
            "Treat this as interesting but unconfirmed."
        )
    }
    
    return statements.get(evidence_level, statements["moderate"])


def flag_research_variants(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flag any findings that are research-grade vs clinically established.
    """
    flagged = []
    
    for finding in findings:
        rsid = finding.get("rsid", "")
        
        # Check if it's a known research variant
        if rsid in RESEARCH_VARIANTS:
            rv = RESEARCH_VARIANTS[rsid]
            finding["is_research_variant"] = True
            finding["research_status"] = rv.get("status", "emerging")
            finding["research_context"] = rv.get("research_context", "")
            finding["research_note"] = rv.get("note", "")
        elif rsid in PUBMED_REFERENCES:
            ref = PUBMED_REFERENCES[rsid]
            finding["is_research_variant"] = False
            finding["evidence_level"] = ref["evidence_level"].value
        else:
            finding["is_research_variant"] = True
            finding["research_status"] = "unknown"
            finding["research_note"] = "Limited information available for this variant."
        
        flagged.append(finding)
    
    return flagged


def get_pubmed_links(rsid: str) -> List[Dict[str, str]]:
    """Get PubMed links for a specific rsid."""
    if rsid in PUBMED_REFERENCES:
        ref = PUBMED_REFERENCES[rsid]
        return [
            {
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "is_primary": pmid == ref.get("primary_paper")
            }
            for pmid in ref.get("pmids", [])
        ]
    elif rsid in RESEARCH_VARIANTS:
        rv = RESEARCH_VARIANTS[rsid]
        return [
            {
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "is_primary": False
            }
            for pmid in rv.get("pmids", [])
        ]
    return []


def generate_full_explanation_report(
    findings: List[Dict[str, Any]],
    include_research: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive explanation report for all findings.
    """
    report = {
        "established_findings": [],
        "well_supported_findings": [],
        "emerging_research": [],
        "summary_statistics": {
            "total_findings": len(findings),
            "established": 0,
            "well_supported": 0,
            "emerging": 0,
            "experimental": 0
        },
        "disclaimer": (
            "This report is for informational purposes only and is not medical advice. "
            "Genetic associations are probabilistic—they describe tendencies, not certainties. "
            "Always consult healthcare professionals before making medical decisions."
        )
    }
    
    for finding in findings:
        rsid = finding.get("rsid", "")
        
        # Determine evidence level
        if rsid in PUBMED_REFERENCES:
            evidence = PUBMED_REFERENCES[rsid]["evidence_level"]
        elif rsid in RESEARCH_VARIANTS:
            status = RESEARCH_VARIANTS[rsid].get("status", "emerging")
            evidence = EvidenceLevel.EMERGING if status == "emerging" else EvidenceLevel.MODERATE
        else:
            evidence = EvidenceLevel.MODERATE
        
        # Generate explanation
        explanation = generate_plain_english_explanation(
            rsid=rsid,
            gene=finding.get("gene", "Unknown"),
            genotype=finding.get("genotype", ""),
            trait=finding.get("trait", ""),
            finding=finding.get("effect", finding.get("description", "")),
            evidence_level=evidence.value
        )
        
        finding_with_explanation = {**finding, "explanation": explanation}
        
        # Categorize
        if evidence == EvidenceLevel.ESTABLISHED:
            report["established_findings"].append(finding_with_explanation)
            report["summary_statistics"]["established"] += 1
        elif evidence == EvidenceLevel.WELL_SUPPORTED:
            report["well_supported_findings"].append(finding_with_explanation)
            report["summary_statistics"]["well_supported"] += 1
        elif include_research:
            report["emerging_research"].append(finding_with_explanation)
            if evidence == EvidenceLevel.EMERGING:
                report["summary_statistics"]["emerging"] += 1
            else:
                report["summary_statistics"]["experimental"] += 1
    
    return report
