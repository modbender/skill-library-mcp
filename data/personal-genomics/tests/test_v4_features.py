"""
Tests for v4.0 features:
- Haplogroup analysis
- Ancestry composition
- Cancer panel
- Autoimmune HLA
- Pain sensitivity
- Data quality
- PDF generation
- Export formats
"""

import pytest
import sys
import os
import json
from pathlib import Path
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def european_male_genotypes() -> Dict[str, str]:
    """Synthetic genotype data for European male."""
    return {
        # Haplogroup markers - mtDNA H
        "rs2853511": "CC",  # H+
        "rs2853512": "AA",  # H confirmation
        # Haplogroup markers - Y-DNA R1b
        "rs2032641": "AA",  # R+
        "rs9786076": "CC",  # R1b+
        # Ancestry markers - European
        "rs1426654": "AA",  # European pigmentation
        "rs16891982": "GG",  # European
        "rs12913832": "GG",  # Blue eyes
        "rs4988235": "AA",  # Lactase persistent
        "rs3827760": "AA",  # NOT East Asian
        "rs2814778": "TT",  # NOT Duffy null
        # APOE
        "rs429358": "TT",  # E3
        "rs7412": "CC",     # E3
        # BRCA - no pathogenic
        # Celiac HLA
        "rs2187668": "TT",  # DQ2 positive
        # Pain sensitivity
        "rs4680": "GA",     # COMT intermediate
        "rs1799971": "AA",  # OPRM1 normal
        "rs3892097": "GG",  # CYP2D6 normal
        "rs8065080": "CT",  # TRPV1 intermediate
        # Other
        "rs9939609": "TA",  # FTO heterozygous
    }


@pytest.fixture
def african_female_genotypes() -> Dict[str, str]:
    """Synthetic genotype data for African female."""
    return {
        # mtDNA L2 markers
        "rs3135028": "CC",  # L2+
        # No Y markers (female)
        # Ancestry markers - African
        "rs1426654": "GG",  # African pigmentation
        "rs16891982": "CC",  # African
        "rs12913832": "AA",  # Dark eyes
        "rs4988235": "GG",  # Lactose intolerant
        "rs2814778": "CC",  # Duffy null
        # APOE
        "rs429358": "CT",   # E3/E4
        "rs7412": "CC",
        # Celiac HLA - negative
        "rs2187668": "CC",
        # Pain sensitivity
        "rs4680": "AA",     # COMT Met/Met (pain sensitive)
        "rs1799971": "AG",  # OPRM1 reduced function
    }


@pytest.fixture
def mixed_ancestry_genotypes() -> Dict[str, str]:
    """Synthetic genotype data for admixed ancestry."""
    return {
        # Mixed markers
        "rs1426654": "GA",  # Heterozygous
        "rs16891982": "GC",
        "rs12913832": "GA",
        "rs4988235": "GA",
        "rs3827760": "GA",
        "rs2814778": "TC",
        # APOE E4/E4
        "rs429358": "CC",
        "rs7412": "CC",
    }


# =============================================================================
# HAPLOGROUP TESTS
# =============================================================================

class TestHaplogroups:
    """Tests for haplogroup analysis."""
    
    def test_haplogroup_imports(self):
        """Test haplogroup module imports."""
        from markers.haplogroups import (
            MTDNA_MARKERS, YCHROMOSOME_MARKERS, HAPLOGROUP_HISTORY,
            analyze_haplogroups
        )
        assert len(MTDNA_MARKERS) > 10
        assert len(YCHROMOSOME_MARKERS) > 10
        assert len(HAPLOGROUP_HISTORY) > 5
    
    def test_mtdna_marker_structure(self):
        """Test mtDNA marker structure."""
        from markers.haplogroups import MTDNA_MARKERS
        
        for rsid, info in list(MTDNA_MARKERS.items())[:5]:
            assert "haplogroup" in info
            assert "position" in info or "alleles" in info
    
    def test_ychrom_marker_structure(self):
        """Test Y-chromosome marker structure."""
        from markers.haplogroups import YCHROMOSOME_MARKERS
        
        for rsid, info in list(YCHROMOSOME_MARKERS.items())[:5]:
            assert "haplogroup" in info
            assert "gene" in info
            assert info["gene"] == "Y"
    
    def test_analyze_haplogroups_male(self, european_male_genotypes):
        """Test haplogroup analysis for male."""
        from markers.haplogroups import analyze_haplogroups
        
        result = analyze_haplogroups(european_male_genotypes)
        
        assert "mtDNA" in result
        assert "Y_DNA" in result
        assert "summary" in result
        assert result["mtDNA"]["lineage"] == "maternal"
        assert result["Y_DNA"]["lineage"] == "paternal"
    
    def test_analyze_haplogroups_female(self, african_female_genotypes):
        """Test haplogroup analysis for female (no Y-DNA)."""
        from markers.haplogroups import analyze_haplogroups
        
        result = analyze_haplogroups(african_female_genotypes)
        
        assert result["Y_DNA"]["sex"] in ["likely_female", "unknown"]
        assert "mtDNA" in result
    
    def test_haplogroup_history_data(self):
        """Test haplogroup history data completeness."""
        from markers.haplogroups import HAPLOGROUP_HISTORY
        
        for hg, history in HAPLOGROUP_HISTORY.items():
            assert "type" in history
            assert history["type"] in ["mtDNA", "Y-DNA"]
            assert "origin" in history
            assert "migration" in history


# =============================================================================
# ANCESTRY COMPOSITION TESTS
# =============================================================================

class TestAncestryComposition:
    """Tests for ancestry composition analysis."""
    
    def test_ancestry_imports(self):
        """Test ancestry module imports."""
        from markers.ancestry_composition import (
            ANCESTRY_INFORMATIVE_MARKERS, POPULATION_DESCRIPTIONS,
            estimate_ancestry, detect_admixture
        )
        assert len(ANCESTRY_INFORMATIVE_MARKERS) >= 15
        assert len(POPULATION_DESCRIPTIONS) >= 5
    
    def test_aims_structure(self):
        """Test ancestry informative marker structure."""
        from markers.ancestry_composition import ANCESTRY_INFORMATIVE_MARKERS
        
        for rsid, info in list(ANCESTRY_INFORMATIVE_MARKERS.items())[:5]:
            assert "frequencies" in info
            # Should have at least 3 population frequencies
            assert len(info["frequencies"]) >= 3
    
    def test_estimate_ancestry_european(self, european_male_genotypes):
        """Test ancestry estimation for European."""
        from markers.ancestry_composition import estimate_ancestry
        
        result = estimate_ancestry(european_male_genotypes)
        
        # Should have success or insufficient data
        if result.get("status") == "success":
            assert "ancestry_proportions" in result
            assert result["markers_used"] > 0
            # European should be detected
            proportions = result.get("ancestry_proportions_raw", {})
            assert "EUR" in proportions
    
    def test_estimate_ancestry_african(self, african_female_genotypes):
        """Test ancestry estimation for African."""
        from markers.ancestry_composition import estimate_ancestry
        
        result = estimate_ancestry(african_female_genotypes)
        
        if result.get("status") == "success":
            proportions = result.get("ancestry_proportions_raw", {})
            assert "AFR" in proportions
    
    def test_detect_admixture(self, mixed_ancestry_genotypes):
        """Test admixture detection."""
        from markers.ancestry_composition import detect_admixture
        
        result = detect_admixture(mixed_ancestry_genotypes)
        
        assert "is_admixed" in result
        assert "admixture_evidence" in result
    
    def test_population_descriptions(self):
        """Test population descriptions completeness."""
        from markers.ancestry_composition import POPULATION_DESCRIPTIONS
        
        required_pops = ["EUR", "AFR", "EAS"]
        for pop in required_pops:
            assert pop in POPULATION_DESCRIPTIONS
            assert "name" in POPULATION_DESCRIPTIONS[pop]
            assert "description" in POPULATION_DESCRIPTIONS[pop]


# =============================================================================
# CANCER PANEL TESTS
# =============================================================================

class TestCancerPanel:
    """Tests for hereditary cancer panel."""
    
    def test_cancer_imports(self):
        """Test cancer panel imports."""
        from markers.cancer_panel import (
            BRCA1_MARKERS, BRCA2_MARKERS, LYNCH_SYNDROME_MARKERS,
            HEREDITARY_CANCER_MARKERS, analyze_cancer_panel
        )
        assert len(BRCA1_MARKERS) >= 5
        assert len(BRCA2_MARKERS) >= 5
        assert len(LYNCH_SYNDROME_MARKERS) >= 5
    
    def test_brca_marker_structure(self):
        """Test BRCA marker structure."""
        from markers.cancer_panel import BRCA1_MARKERS
        
        for rsid, info in BRCA1_MARKERS.items():
            assert info["gene"] == "BRCA1"
            assert "variant" in info
            assert "classification" in info
    
    def test_lynch_marker_structure(self):
        """Test Lynch syndrome marker structure."""
        from markers.cancer_panel import LYNCH_SYNDROME_MARKERS
        
        for rsid, info in LYNCH_SYNDROME_MARKERS.items():
            assert info["gene"] in ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"]
            assert info.get("syndrome") == "Lynch syndrome" or "Lynch" in str(info.get("syndrome", ""))
    
    def test_analyze_cancer_panel(self, european_male_genotypes):
        """Test cancer panel analysis."""
        from markers.cancer_panel import analyze_cancer_panel
        
        result = analyze_cancer_panel(european_male_genotypes)
        
        assert "pathogenic_variants" in result
        assert "markers_analyzed" in result
        assert "genes_covered" in result
        assert "summary" in result
    
    def test_cancer_screening_panels(self):
        """Test cancer screening panel definitions."""
        from markers.cancer_panel import CANCER_SCREENING_PANELS
        
        assert "brca" in CANCER_SCREENING_PANELS
        assert "lynch" in CANCER_SCREENING_PANELS
        
        assert "BRCA1" in CANCER_SCREENING_PANELS["brca"]["genes"]
        assert "MLH1" in CANCER_SCREENING_PANELS["lynch"]["genes"]


# =============================================================================
# AUTOIMMUNE HLA TESTS
# =============================================================================

class TestAutoimmuneHLA:
    """Tests for autoimmune HLA associations."""
    
    def test_autoimmune_imports(self):
        """Test autoimmune module imports."""
        from markers.autoimmune_hla import (
            CELIAC_HLA_MARKERS, AUTOIMMUNE_HLA_MARKERS,
            AUTOIMMUNE_CONDITIONS, analyze_autoimmune_risk
        )
        assert len(CELIAC_HLA_MARKERS) >= 2
        assert len(AUTOIMMUNE_HLA_MARKERS) >= 20
    
    def test_celiac_markers(self):
        """Test celiac disease HLA markers."""
        from markers.autoimmune_hla import CELIAC_HLA_MARKERS
        
        # rs2187668 is key DQ2.5 marker
        assert "rs2187668" in CELIAC_HLA_MARKERS
        marker = CELIAC_HLA_MARKERS["rs2187668"]
        assert "DQ2" in marker.get("hla_type", "")
    
    def test_b27_marker(self):
        """Test HLA-B27 marker for ankylosing spondylitis."""
        from markers.autoimmune_hla import ANKYLOSING_SPONDYLITIS_MARKERS
        
        # rs4349859 tags HLA-B27
        assert "rs4349859" in ANKYLOSING_SPONDYLITIS_MARKERS
        marker = ANKYLOSING_SPONDYLITIS_MARKERS["rs4349859"]
        assert "B27" in marker.get("hla_type", "") or "B*27" in marker.get("hla_type", "")
    
    def test_analyze_autoimmune_risk(self, european_male_genotypes):
        """Test autoimmune risk analysis."""
        from markers.autoimmune_hla import analyze_autoimmune_risk
        
        result = analyze_autoimmune_risk(european_male_genotypes)
        
        assert "conditions_analyzed" in result
        assert "risk_profile" in result
        assert "summary" in result
    
    def test_autoimmune_conditions(self):
        """Test autoimmune condition definitions."""
        from markers.autoimmune_hla import AUTOIMMUNE_CONDITIONS
        
        required = ["celiac", "ankylosing_spondylitis", "rheumatoid_arthritis"]
        for cond in required:
            assert cond in AUTOIMMUNE_CONDITIONS
            assert "name" in AUTOIMMUNE_CONDITIONS[cond]


# =============================================================================
# PAIN SENSITIVITY TESTS
# =============================================================================

class TestPainSensitivity:
    """Tests for pain sensitivity module."""
    
    def test_pain_imports(self):
        """Test pain sensitivity imports."""
        from markers.pain_sensitivity import (
            COMT_MARKERS, OPRM1_MARKERS, PAIN_SENSITIVITY_MARKERS,
            analyze_pain_sensitivity
        )
        assert len(COMT_MARKERS) >= 2
        assert len(OPRM1_MARKERS) >= 1
        assert len(PAIN_SENSITIVITY_MARKERS) >= 15
    
    def test_comt_val158met(self):
        """Test COMT Val158Met marker."""
        from markers.pain_sensitivity import COMT_MARKERS
        
        assert "rs4680" in COMT_MARKERS
        marker = COMT_MARKERS["rs4680"]
        assert "genotype_effects" in marker
        assert "GG" in marker["genotype_effects"]
        assert "AA" in marker["genotype_effects"]
    
    def test_oprm1_a118g(self):
        """Test OPRM1 A118G marker."""
        from markers.pain_sensitivity import OPRM1_MARKERS
        
        assert "rs1799971" in OPRM1_MARKERS
        marker = OPRM1_MARKERS["rs1799971"]
        assert "genotype_effects" in marker
    
    def test_analyze_pain_sensitivity(self, european_male_genotypes):
        """Test pain sensitivity analysis."""
        from markers.pain_sensitivity import analyze_pain_sensitivity
        
        result = analyze_pain_sensitivity(european_male_genotypes)
        
        assert "pain_sensitivity_profile" in result
        assert "opioid_response" in result
        assert "migraine_risk" in result
        assert "key_findings" in result
    
    def test_cyp2d6_poor_metabolizer(self):
        """Test CYP2D6 poor metabolizer detection."""
        from markers.pain_sensitivity import analyze_pain_sensitivity
        
        genotypes = {"rs3892097": "AA"}  # Poor metabolizer
        result = analyze_pain_sensitivity(genotypes)
        
        assert result["opioid_response"]["cyp2d6_metabolism"] == "poor"
        assert len(result["actionable_items"]) > 0


# =============================================================================
# DATA QUALITY TESTS
# =============================================================================

class TestDataQuality:
    """Tests for data quality module."""
    
    def test_quality_imports(self):
        """Test data quality imports."""
        from data_quality import (
            detect_platform, analyze_call_rate, generate_quality_report
        )
    
    def test_analyze_call_rate(self, european_male_genotypes):
        """Test call rate analysis."""
        from data_quality import analyze_call_rate
        
        result = analyze_call_rate(european_male_genotypes)
        
        assert "call_rate" in result
        assert "quality_grade" in result
        assert "heterozygosity" in result
        assert 0 <= result["call_rate"] <= 1
    
    def test_detect_platform_by_count(self):
        """Test platform detection by SNP count."""
        from data_quality import detect_platform
        
        # Create mock genotypes of different sizes
        small_set = {f"rs{i}": "AA" for i in range(100000)}
        medium_set = {f"rs{i}": "AA" for i in range(650000)}
        large_set = {f"rs{i}": "AA" for i in range(4000000)}
        
        result_small = detect_platform(small_set)
        result_medium = detect_platform(medium_set)
        result_large = detect_platform(large_set)
        
        assert result_small["total_snps"] == 100000
        assert result_medium["total_snps"] == 650000
        # Large could be WGS or exome
    
    def test_quality_report(self, european_male_genotypes):
        """Test complete quality report."""
        from data_quality import generate_quality_report
        
        result = generate_quality_report(european_male_genotypes)
        
        assert "summary" in result
        assert "platform_detection" in result
        assert "call_rate_analysis" in result


# =============================================================================
# PDF REPORT TESTS
# =============================================================================

class TestPDFReport:
    """Tests for PDF report generation."""
    
    def test_pdf_availability(self):
        """Test PDF generation availability."""
        from pdf_report import is_available
        
        # Should return True if reportlab is installed
        available = is_available()
        assert isinstance(available, bool)
    
    def test_create_styles(self):
        """Test style creation."""
        from pdf_report import is_available
        
        if is_available():
            from pdf_report import create_styles
            styles = create_styles()
            assert "Title" in styles
            assert "Body" in styles
            assert "Critical" in styles
    
    def test_pdf_generation_creates_file(self, european_male_genotypes, tmp_path):
        """Test PDF file is created."""
        from pdf_report import is_available, generate_pdf_report
        
        if not is_available():
            pytest.skip("reportlab not installed")
        
        # Create mock analysis results
        results = {
            "total_snps": 20,
            "format": "test",
            "version": "4.0",
            "apoe": {"genotype": "ε3/ε3", "risk_level": "average"},
            "critical_alerts": [],
            "high_priority": [],
            "pharmacogenomics_alerts": [],
            "prs": {},
            "lifestyle_recommendations": {"diet": [], "exercise": []},
        }
        
        output_path = str(tmp_path / "test_report.pdf")
        result = generate_pdf_report(results, output_path)
        
        if result:
            assert Path(result).exists()
            assert Path(result).stat().st_size > 1000  # Should be substantial


# =============================================================================
# EXPORT TESTS
# =============================================================================

class TestExports:
    """Tests for export modules."""
    
    def test_export_imports(self):
        """Test export module imports."""
        from exports import (
            generate_genetic_counselor_export,
            generate_apple_health_export,
            generate_api_export,
            IntegrationHooks
        )
    
    def test_genetic_counselor_export(self, european_male_genotypes):
        """Test genetic counselor export generation."""
        from exports import generate_genetic_counselor_export
        
        results = {
            "total_snps": 20,
            "format": "test",
            "version": "4.0",
            "apoe": {"genotype": "ε3/ε4", "risk_level": "elevated"},
            "critical_alerts": [],
            "high_priority": [],
            "pharmacogenomics_alerts": [
                {"gene": "CYP2D6", "rsid": "rs3892097", "genotype": "GG"}
            ],
            "carrier_status": [],
        }
        
        export = generate_genetic_counselor_export(results)
        
        assert "classification_summary" in export
        assert "clinical_actionability" in export
        assert "pharmacogenomics_summary" in export
        assert "limitations" in export
    
    def test_apple_health_export(self):
        """Test Apple Health export generation."""
        from exports import generate_apple_health_export
        
        results = {
            "apoe": {"genotype": "ε3/ε3", "risk_level": "average"},
            "pharmacogenomics_alerts": [],
            "prs": {"CAD": {"percentile_estimate": 55, "confidence": "moderate"}},
            "carrier_status": [],
        }
        
        export = generate_apple_health_export(results)
        
        assert "format" in export
        assert export["format"] == "apple_health_compatible"
        assert "records" in export
    
    def test_api_export(self):
        """Test API export generation."""
        from exports import generate_api_export
        
        results = {
            "total_snps": 100,
            "format": "test",
            "version": "4.0",
            "apoe": {"genotype": "ε3/ε3"},
            "critical_alerts": [],
            "high_priority": [],
            "pharmacogenomics_alerts": [],
            "prs": {},
        }
        
        export = generate_api_export(results, include_raw=False)
        
        assert "api_version" in export
        assert "metadata" in export
        assert "summary" in export
        assert "integrations" in export
    
    def test_integration_hooks(self):
        """Test integration hooks."""
        from exports import IntegrationHooks
        
        results = {"total_snps": 100, "critical_alerts": [], "pharmacogenomics_alerts": []}
        hooks = IntegrationHooks(results)
        
        webhook = hooks.get_webhook_payload()
        assert "event" in webhook
        assert "timestamp" in webhook
        assert "data" in webhook
        
        dashboard = hooks.get_dashboard_data()
        assert "cards" in dashboard
        assert "charts" in dashboard


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestV4Integration:
    """Integration tests for v4.0 features."""
    
    def test_all_v4_modules_import(self):
        """Test all v4 modules import correctly."""
        from markers import (
            MTDNA_MARKERS, YCHROMOSOME_MARKERS,
            ANCESTRY_INFORMATIVE_MARKERS,
            HEREDITARY_CANCER_MARKERS,
            AUTOIMMUNE_HLA_MARKERS,
            PAIN_SENSITIVITY_MARKERS,
            get_marker_counts
        )
        
        counts = get_marker_counts()
        assert counts["haplogroups"] > 0
        assert counts["hereditary_cancer"] > 0
        assert counts["autoimmune_hla"] > 0
        assert counts["pain_sensitivity"] > 0
    
    def test_marker_counts_increased(self):
        """Test total marker count increased from v3."""
        from markers import get_marker_counts
        
        counts = get_marker_counts()
        # v3 had ~1300, v4 should have significantly more
        assert counts["total"] > 1400
    
    def test_analysis_functions_work(self, european_male_genotypes):
        """Test all analysis functions work together."""
        from markers import (
            analyze_haplogroups, analyze_cancer_panel,
            analyze_autoimmune_risk, analyze_pain_sensitivity
        )
        from markers.ancestry_composition import get_ancestry_summary
        
        haplogroups = analyze_haplogroups(european_male_genotypes)
        cancer = analyze_cancer_panel(european_male_genotypes)
        autoimmune = analyze_autoimmune_risk(european_male_genotypes)
        pain = analyze_pain_sensitivity(european_male_genotypes)
        ancestry = get_ancestry_summary(european_male_genotypes)
        
        assert haplogroups is not None
        assert cancer is not None
        assert autoimmune is not None
        assert pain is not None
        assert ancestry is not None


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Edge case and error handling tests."""
    
    def test_empty_genotypes(self):
        """Test handling of empty genotype data."""
        from markers.haplogroups import analyze_haplogroups
        from markers.ancestry_composition import estimate_ancestry
        from markers.pain_sensitivity import analyze_pain_sensitivity
        
        empty = {}
        
        haplogroups = analyze_haplogroups(empty)
        ancestry = estimate_ancestry(empty)
        pain = analyze_pain_sensitivity(empty)
        
        assert haplogroups["mtDNA"]["haplogroup"] == "Unknown"
        assert ancestry.get("status") == "insufficient_data"
        assert pain["markers_found"] == 0
    
    def test_partial_data(self):
        """Test handling of partial/incomplete data."""
        from markers.haplogroups import analyze_haplogroups
        
        # Only one marker
        partial = {"rs2853511": "CC"}
        
        result = analyze_haplogroups(partial)
        # Should still work, just with low confidence
        assert "mtDNA" in result
    
    def test_invalid_genotypes(self):
        """Test handling of invalid genotype formats."""
        from data_quality import analyze_call_rate
        
        invalid = {
            "rs123": "--",
            "rs456": "NC",
            "rs789": "00",
            "rs101": "AA",  # Valid
        }
        
        result = analyze_call_rate(invalid)
        assert result["no_calls"] == 3
        assert result["valid_calls"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
