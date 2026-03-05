"""
Export Modules for Genetic Analysis
Provides multiple output formats for integration and clinical use

Features:
- Genetic counselor clinical export (ACMG-style)
- Apple Health compatible format
- API-ready JSON structure
- Integration hooks for health trackers
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json

# =============================================================================
# VARIANT CLASSIFICATION (ACMG-like)
# =============================================================================

# Simplified ACMG-style classification criteria
CLASSIFICATION_CRITERIA = {
    "pathogenic": {
        "code": "P",
        "description": "Pathogenic - Disease-causing",
        "action_level": "clinical_action_required",
        "evidence_types": ["null_variant", "known_pathogenic", "functional_studies"]
    },
    "likely_pathogenic": {
        "code": "LP",
        "description": "Likely Pathogenic - Probably disease-causing",
        "action_level": "clinical_review_recommended",
        "evidence_types": ["strong_functional", "cosegregation", "case_control"]
    },
    "vus": {
        "code": "VUS",
        "description": "Variant of Uncertain Significance",
        "action_level": "no_clinical_action",
        "evidence_types": ["conflicting_data", "insufficient_data"]
    },
    "likely_benign": {
        "code": "LB",
        "description": "Likely Benign - Probably not disease-causing",
        "action_level": "no_clinical_action",
        "evidence_types": ["population_frequency", "functional_neutral"]
    },
    "benign": {
        "code": "B",
        "description": "Benign - Not disease-causing",
        "action_level": "no_clinical_action",
        "evidence_types": ["high_population_frequency", "no_phenotype"]
    },
    "risk_factor": {
        "code": "RF",
        "description": "Risk Factor - Associated with increased disease risk",
        "action_level": "lifestyle_modification",
        "evidence_types": ["gwas_association", "odds_ratio"]
    }
}


def generate_genetic_counselor_export(
    analysis_results: Dict[str, Any],
    output_path: str = None
) -> Dict[str, Any]:
    """
    Generate clinical-grade report for genetic counselors.
    
    Includes:
    - ACMG-style variant classification
    - Clinical actionability assessment
    - Inheritance patterns
    - Testing recommendations
    
    Args:
        analysis_results: Complete analysis results
        output_path: Optional path to save JSON
        
    Returns:
        Dict with clinical export data
    """
    export = {
        "report_type": "genetic_counselor_clinical_export",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "data_source": {
            "snps_analyzed": analysis_results.get("total_snps", 0),
            "platform": analysis_results.get("format", "Unknown"),
            "analysis_version": analysis_results.get("version", "Unknown")
        },
        "patient_info": {
            "note": "Patient identification should be added by ordering clinician"
        },
        "classification_summary": {
            "pathogenic": [],
            "likely_pathogenic": [],
            "vus_notable": [],
            "risk_factors": []
        },
        "clinical_actionability": {
            "immediate_action": [],
            "surveillance_recommended": [],
            "family_testing_indicated": [],
            "lifestyle_modification": []
        },
        "pharmacogenomics_summary": [],
        "hereditary_syndromes": [],
        "recommendations": [],
        "limitations": []
    }
    
    # Process critical alerts
    for alert in analysis_results.get("critical_alerts", []):
        classified_variant = _classify_variant(alert, "pathogenic")
        export["classification_summary"]["pathogenic"].append(classified_variant)
        export["clinical_actionability"]["immediate_action"].append({
            "gene": alert.get("gene"),
            "action": "Genetic counseling and clinical confirmation recommended",
            "recommendations": alert.get("recommendations", [])
        })
    
    # Process high priority
    for item in analysis_results.get("high_priority", []):
        classification = item.get("classification", "likely_pathogenic")
        classified_variant = _classify_variant(item, classification)
        
        if classification == "pathogenic":
            export["classification_summary"]["pathogenic"].append(classified_variant)
        elif classification == "likely_pathogenic":
            export["classification_summary"]["likely_pathogenic"].append(classified_variant)
        else:
            export["classification_summary"]["risk_factors"].append(classified_variant)
    
    # Pharmacogenomics
    for alert in analysis_results.get("pharmacogenomics_alerts", []):
        export["pharmacogenomics_summary"].append({
            "gene": alert.get("gene"),
            "rsid": alert.get("rsid"),
            "genotype": alert.get("genotype"),
            "phenotype": _determine_pharma_phenotype(alert),
            "affected_medications": alert.get("drugs", []),
            "clinical_recommendation": alert.get("action_type", "Review drug dosing")
        })
    
    # Carrier status
    for carrier in analysis_results.get("carrier_status", []):
        if carrier.get("is_carrier"):
            export["clinical_actionability"]["family_testing_indicated"].append({
                "condition": carrier.get("condition"),
                "gene": carrier.get("gene"),
                "inheritance": "autosomal_recessive",
                "partner_testing": "Recommended before pregnancy"
            })
    
    # APOE
    apoe = analysis_results.get("apoe", {})
    if apoe.get("risk_level") in ["elevated", "high"]:
        export["clinical_actionability"]["surveillance_recommended"].append({
            "gene": "APOE",
            "genotype": apoe.get("genotype"),
            "risk": apoe.get("risk_level"),
            "condition": "Alzheimer's disease",
            "recommendations": apoe.get("recommendations", [])
        })
    
    # Limitations
    export["limitations"] = [
        "Consumer genotyping arrays detect limited subset of genetic variants",
        "Negative results do not rule out hereditary conditions",
        "Clinical confirmation required for pathogenic findings",
        "Population-specific risk estimates may vary",
        "Penetrance and expressivity are incomplete for most conditions",
        "Environmental and lifestyle factors not accounted for",
        "This analysis is not a comprehensive clinical genetic test"
    ]
    
    # Recommendations
    if export["classification_summary"]["pathogenic"]:
        export["recommendations"].append(
            "URGENT: Pathogenic variant(s) detected. Refer for genetic counseling."
        )
    if export["pharmacogenomics_summary"]:
        export["recommendations"].append(
            "Update medical record with pharmacogenomic findings."
        )
    export["recommendations"].append(
        "Consider family history assessment for comprehensive risk evaluation."
    )
    
    # Save if path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2, default=str)
    
    return export


def _classify_variant(variant_info: Dict, default_class: str) -> Dict[str, Any]:
    """Create classified variant entry."""
    classification = variant_info.get("classification", default_class)
    criteria = CLASSIFICATION_CRITERIA.get(classification, CLASSIFICATION_CRITERIA["vus"])
    
    return {
        "rsid": variant_info.get("rsid"),
        "gene": variant_info.get("gene"),
        "variant": variant_info.get("variant", variant_info.get("name", "")),
        "genotype": variant_info.get("genotype"),
        "classification": {
            "category": classification,
            "code": criteria["code"],
            "description": criteria["description"]
        },
        "condition": variant_info.get("condition") or variant_info.get("syndrome"),
        "inheritance": variant_info.get("inheritance", "see_gene_specific"),
        "action_level": criteria["action_level"],
        "evidence": variant_info.get("evidence", "published_literature")
    }


def _determine_pharma_phenotype(alert: Dict) -> str:
    """Determine pharmacogenomic phenotype from alert data."""
    gene = alert.get("gene", "")
    
    if "poor" in str(alert).lower():
        return "Poor Metabolizer"
    elif "intermediate" in str(alert).lower():
        return "Intermediate Metabolizer"
    elif "ultrarapid" in str(alert).lower() or "ultra" in str(alert).lower():
        return "Ultrarapid Metabolizer"
    elif "normal" in str(alert).lower() or "extensive" in str(alert).lower():
        return "Normal/Extensive Metabolizer"
    else:
        return "See interpretation"


# =============================================================================
# APPLE HEALTH EXPORT
# =============================================================================

def generate_apple_health_export(
    analysis_results: Dict[str, Any],
    output_path: str = None
) -> Dict[str, Any]:
    """
    Generate Apple Health compatible export.
    
    Note: Direct Apple Health integration requires iOS app.
    This generates a structured format that could be imported.
    
    Apple Health categories for genetic data:
    - HKClinicalTypeIdentifierLabResultRecord (for variants)
    - HKCategoryTypeIdentifierAppleWalkingSteadinessEvent (not directly applicable)
    
    Since Apple Health doesn't have native genetic data types,
    we format as clinical records that could be imported via FHIR.
    
    Args:
        analysis_results: Complete analysis results
        output_path: Optional path to save
        
    Returns:
        Dict with Apple Health compatible structure
    """
    export = {
        "format": "apple_health_compatible",
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "source": {
            "name": "Personal Genomics Analysis",
            "bundle_id": "com.openclaw.genomics"
        },
        "records": []
    }
    
    # Add genetic findings as clinical records
    # These would be imported as HKClinicalRecord in a real iOS implementation
    
    # APOE
    apoe = analysis_results.get("apoe", {})
    if apoe.get("genotype") != "unknown":
        export["records"].append({
            "type": "genetic_variant",
            "identifier": "APOE_genotype",
            "display_name": "APOE Genotype",
            "value": apoe.get("genotype"),
            "interpretation": apoe.get("interpretation"),
            "risk_level": apoe.get("risk_level"),
            "date": datetime.now().isoformat(),
            "metadata": {
                "gene": "APOE",
                "rsids": ["rs429358", "rs7412"]
            }
        })
    
    # Pharmacogenomics
    for alert in analysis_results.get("pharmacogenomics_alerts", []):
        export["records"].append({
            "type": "pharmacogenomic_result",
            "identifier": f"pgx_{alert.get('gene', 'unknown')}",
            "display_name": f"{alert.get('gene')} Drug Response",
            "gene": alert.get("gene"),
            "genotype": alert.get("genotype"),
            "phenotype": _determine_pharma_phenotype(alert),
            "clinical_significance": alert.get("action_type", ""),
            "date": datetime.now().isoformat()
        })
    
    # PRS scores
    prs = analysis_results.get("prs", {})
    if prs and not prs.get("error"):
        for condition, scores in prs.items():
            if scores.get("percentile_estimate"):
                export["records"].append({
                    "type": "polygenic_risk_score",
                    "identifier": f"prs_{condition.lower().replace(' ', '_')}",
                    "display_name": f"Genetic Risk: {condition}",
                    "condition": condition,
                    "percentile": scores["percentile_estimate"],
                    "confidence": scores.get("confidence"),
                    "date": datetime.now().isoformat()
                })
    
    # Carrier status
    for carrier in analysis_results.get("carrier_status", []):
        if carrier.get("is_carrier"):
            export["records"].append({
                "type": "carrier_status",
                "identifier": f"carrier_{carrier.get('gene', 'unknown')}",
                "display_name": f"Carrier: {carrier.get('condition', 'Unknown')}",
                "gene": carrier.get("gene"),
                "condition": carrier.get("condition"),
                "status": "carrier",
                "date": datetime.now().isoformat()
            })
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2)
    
    return export


# =============================================================================
# API-READY JSON EXPORT
# =============================================================================

def generate_api_export(
    analysis_results: Dict[str, Any],
    include_raw: bool = False,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Generate API-ready JSON structure for integration.
    
    Designed for:
    - Health tracking app integration
    - Dashboard visualization
    - Webhook payloads
    - Database storage
    
    Args:
        analysis_results: Complete analysis results
        include_raw: Include raw marker data (increases size)
        output_path: Optional path to save
        
    Returns:
        Dict with structured API-ready data
    """
    export = {
        "api_version": "2.0",
        "schema": "openclaw.genomics.analysis",
        "generated_at": datetime.now().isoformat(),
        "metadata": {
            "snps_analyzed": analysis_results.get("total_snps", 0),
            "platform": analysis_results.get("format", "Unknown"),
            "analysis_version": analysis_results.get("version", "Unknown"),
            "categories_analyzed": []
        },
        "summary": {
            "critical_count": len(analysis_results.get("critical_alerts", [])),
            "high_priority_count": len(analysis_results.get("high_priority", [])),
            "pharmacogenomics_count": len(analysis_results.get("pharmacogenomics_alerts", [])),
            "carrier_findings": len(analysis_results.get("carrier_status", []))
        },
        "key_results": {
            "apoe": analysis_results.get("apoe"),
            "critical_alerts": analysis_results.get("critical_alerts", []),
            "high_priority": analysis_results.get("high_priority", [])[:10],
            "pharmacogenomics": analysis_results.get("pharmacogenomics_alerts", [])[:20]
        },
        "risk_scores": {},
        "ancestry": {},
        "recommendations": analysis_results.get("lifestyle_recommendations", {}),
        "integrations": {
            "webhook_ready": True,
            "supports_fhir": False,
            "supports_apple_health": True
        }
    }
    
    # Categories analyzed
    categories = []
    for key in analysis_results.keys():
        if key not in ["total_snps", "format", "version", "critical_alerts", 
                       "high_priority", "medium_priority", "low_priority"]:
            categories.append(key)
    export["metadata"]["categories_analyzed"] = categories
    
    # PRS
    prs = analysis_results.get("prs", {})
    if prs and not prs.get("error"):
        for condition, scores in prs.items():
            export["risk_scores"][condition] = {
                "percentile": scores.get("percentile_estimate"),
                "confidence": scores.get("confidence"),
                "snps_used": scores.get("snps_found")
            }
    
    # Ancestry
    if analysis_results.get("haplogroups"):
        export["ancestry"]["haplogroups"] = analysis_results["haplogroups"]
    if analysis_results.get("ancestry_composition"):
        export["ancestry"]["composition"] = analysis_results["ancestry_composition"]
    
    # Include raw data if requested
    if include_raw:
        export["raw_results"] = {
            cat: analysis_results.get(cat, {})
            for cat in categories
            if cat not in export["key_results"]
        }
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2, default=str)
    
    return export


# =============================================================================
# INTEGRATION HOOKS
# =============================================================================

class IntegrationHooks:
    """
    Integration hooks for health tracker and third-party app integration.
    
    Provides callbacks and structured data for:
    - Real-time analysis streaming
    - Webhook delivery
    - Custom transformations
    """
    
    def __init__(self, analysis_results: Dict[str, Any]):
        self.results = analysis_results
        self.hooks = {}
    
    def register_hook(self, event_type: str, callback: callable):
        """Register a callback for an event type."""
        if event_type not in self.hooks:
            self.hooks[event_type] = []
        self.hooks[event_type].append(callback)
    
    def trigger_hooks(self, event_type: str, data: Dict):
        """Trigger all hooks for an event type."""
        for callback in self.hooks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Hook error for {event_type}: {e}")
    
    def get_webhook_payload(self, event_type: str = "analysis_complete") -> Dict:
        """Generate webhook payload for external services."""
        return {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "summary": {
                    "snps": self.results.get("total_snps"),
                    "critical_findings": len(self.results.get("critical_alerts", [])),
                    "pharmacogenomics_findings": len(self.results.get("pharmacogenomics_alerts", []))
                },
                "apoe": self.results.get("apoe", {}),
                "top_findings": self.results.get("high_priority", [])[:5]
            },
            "links": {
                "full_report": "/api/reports/latest",
                "pdf": "/api/reports/latest.pdf"
            }
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get data formatted for dashboard visualization."""
        return {
            "cards": [
                {
                    "type": "metric",
                    "title": "SNPs Analyzed",
                    "value": self.results.get("total_snps", 0),
                    "format": "number"
                },
                {
                    "type": "status",
                    "title": "Critical Findings",
                    "value": len(self.results.get("critical_alerts", [])),
                    "status": "warning" if self.results.get("critical_alerts") else "good"
                },
                {
                    "type": "info",
                    "title": "APOE Status",
                    "value": self.results.get("apoe", {}).get("genotype", "Unknown"),
                    "subtitle": self.results.get("apoe", {}).get("risk_level", "")
                }
            ],
            "charts": [
                {
                    "type": "bar",
                    "title": "Polygenic Risk Scores",
                    "data": {
                        condition: scores.get("percentile_estimate", 50)
                        for condition, scores in self.results.get("prs", {}).items()
                        if scores.get("percentile_estimate")
                    }
                }
            ],
            "lists": [
                {
                    "title": "Pharmacogenomics Alerts",
                    "items": [
                        f"{a.get('gene')}: {a.get('genotype')}"
                        for a in self.results.get("pharmacogenomics_alerts", [])[:5]
                    ]
                }
            ]
        }


def export_all_formats(
    analysis_results: Dict[str, Any],
    output_dir: str = None
) -> Dict[str, str]:
    """
    Export analysis results in all available formats.
    
    Args:
        analysis_results: Complete analysis results
        output_dir: Directory for output files
        
    Returns:
        Dict mapping format name to file path
    """
    if output_dir is None:
        output_dir = Path.home() / "dna-analysis" / "exports"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exports = {}
    
    # Genetic counselor export
    gc_path = output_dir / "clinical_export.json"
    generate_genetic_counselor_export(analysis_results, str(gc_path))
    exports["genetic_counselor"] = str(gc_path)
    
    # Apple Health export
    ah_path = output_dir / "apple_health_export.json"
    generate_apple_health_export(analysis_results, str(ah_path))
    exports["apple_health"] = str(ah_path)
    
    # API export
    api_path = output_dir / "api_export.json"
    generate_api_export(analysis_results, include_raw=False, output_path=str(api_path))
    exports["api"] = str(api_path)
    
    # Full API export with raw data
    api_full_path = output_dir / "api_export_full.json"
    generate_api_export(analysis_results, include_raw=True, output_path=str(api_full_path))
    exports["api_full"] = str(api_full_path)
    
    return exports
