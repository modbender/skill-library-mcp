"""
Tests for v4.1.0 features:
- Medication Interaction Checker
- Sleep Optimization Profile
- Dietary Interaction Matrix
- Athletic Profiling
- UV Sensitivity Calculator
- Natural Language Explanations
- Research Variant Flagging
- Telomere Length Estimation
- Runs of Homozygosity
"""

import pytest
import sys
import os
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def comprehensive_genotypes() -> Dict[str, str]:
    """Synthetic comprehensive genotype data for testing all v4.1 features."""
    return {
        # Pharmacogenomics
        "rs3892097": "GA",  # CYP2D6 *4 carrier
        "rs4244285": "GA",  # CYP2C19 *2 carrier
        "rs1799853": "CT",  # CYP2C9 *2 carrier
        "rs1057910": "AC",  # CYP2C9 *3 carrier
        "rs9923231": "GA",  # VKORC1
        "rs4149056": "CT",  # SLCO1B1
        "rs3918290": "GG",  # DPYD normal
        
        # Sleep/Chronotype
        "rs1801260": "CC",  # CLOCK evening
        "rs35333999": "AG",  # PER2 
        "rs228697": "GC",   # PER3
        "rs762551": "CC",   # CYP1A2 slow caffeine
        "rs5751876": "TT",  # ADORA2A high sensitivity
        
        # Dietary
        "rs671": "GG",      # ALDH2 normal
        "rs1229984": "CC",  # ADH1B normal
        "rs4988235": "GG",  # LCT lactose intolerant
        "rs2187668": "CT",  # HLA-DQ2 carrier
        "rs10246939": "TT", # TAS2R38 non-taster
        "rs5082": "CC",     # APOA2 sat fat sensitive
        "rs174547": "CC",   # FADS1 poor converter
        "rs1800562": "GG",  # HFE normal
        "rs1801133": "GA",  # MTHFR carrier
        
        # APOE
        "rs429358": "CT",   # E3/E4
        "rs7412": "CC",
        
        # Athletic
        "rs1815739": "CT",  # ACTN3 intermediate
        "rs1799752": "ID",  # ACE I/D
        "rs8192678": "GA",  # PPARGC1A
        "rs1800629": "GG",  # TNF fast recovery
        "rs1800795": "GC",  # IL6
        "rs12722": "CT",    # COL5A1 injury risk
        "rs143383": "CT",   # GDF5
        "rs6265": "CT",     # BDNF
        
        # Pigmentation/UV
        "rs1805007": "CT",  # MC1R R variant carrier
        "rs1426654": "AA",  # SLC24A5 light skin
        "rs16891982": "GG", # SLC45A2 light
        "rs12203592": "CT", # IRF4 freckling
        "rs12913832": "GG", # Blue eyes
        
        # Vitamin D
        "rs2282679": "TG",  # GC intermediate
        "rs12785878": "GT", # DHCR7
        
        # Telomere/Longevity
        "rs12696304": "CG", # TERC intermediate
        "rs2736100": "AC",  # TERT intermediate
        "rs9420907": "AC",  # OBFC1
        "rs2802292": "TG",  # FOXO3 favorable
    }


@pytest.fixture
def poor_metabolizer_genotypes() -> Dict[str, str]:
    """Genotypes for a poor metabolizer phenotype."""
    return {
        "rs3892097": "AA",  # CYP2D6 *4/*4 poor
        "rs4244285": "AA",  # CYP2C19 *2/*2 poor
        "rs1799853": "TT",  # CYP2C9 *2/*2
        "rs1057910": "CC",  # CYP2C9 *3/*3
    }


@pytest.fixture
def fair_skin_genotypes() -> Dict[str, str]:
    """Genotypes for fair skin phenotype."""
    return {
        "rs1805007": "TT",  # MC1R R151C homozygous
        "rs1805008": "CT",  # MC1R R160W carrier
        "rs1426654": "AA",  # SLC24A5 light
        "rs16891982": "GG", # SLC45A2 light
        "rs12203592": "TT", # IRF4 freckles
        "rs12913832": "GG", # Blue eyes
    }


# =============================================================================
# MEDICATION INTERACTION TESTS
# =============================================================================

class TestMedicationInteractions:
    """Tests for medication interaction checker."""
    
    def test_imports(self):
        """Test medication interaction imports."""
        from markers.medication_interactions import (
            DRUG_DATABASE, GENE_DRUG_INTERACTIONS,
            check_medication_interactions, normalize_drug_name,
            InteractionSeverity
        )
        assert len(DRUG_DATABASE) > 30
        assert len(GENE_DRUG_INTERACTIONS) > 5
    
    def test_normalize_drug_name(self):
        """Test drug name normalization."""
        from markers.medication_interactions import normalize_drug_name
        
        assert normalize_drug_name("Plavix") == "clopidogrel"
        assert normalize_drug_name("CLOPIDOGREL") == "clopidogrel"
        assert normalize_drug_name("Coumadin") == "warfarin"
        assert normalize_drug_name("Zocor") == "simvastatin"
        assert normalize_drug_name("tylenol #3") == "codeine"
        assert normalize_drug_name("unknown_drug_xyz") is None
    
    def test_check_no_interactions(self, comprehensive_genotypes):
        """Test medication check with no critical interactions."""
        from markers.medication_interactions import check_medication_interactions
        
        # Medications with no interaction for this genotype
        result = check_medication_interactions(
            medications=["ibuprofen", "acetaminophen"],
            genotypes=comprehensive_genotypes
        )
        
        assert "medications_checked" in result
        assert "summary" in result
        assert result["summary"]["critical_count"] == 0
    
    def test_check_critical_interaction(self, poor_metabolizer_genotypes):
        """Test detection of critical drug-gene interaction."""
        from markers.medication_interactions import check_medication_interactions
        
        result = check_medication_interactions(
            medications=["clopidogrel", "codeine"],
            genotypes=poor_metabolizer_genotypes
        )
        
        # Should flag clopidogrel for CYP2C19 poor metabolizer
        assert result["summary"]["critical_count"] >= 1 or result["summary"]["serious_count"] >= 1
        assert result["summary"]["requires_review"] is True
    
    def test_check_unknown_medication(self, comprehensive_genotypes):
        """Test handling of unknown medication."""
        from markers.medication_interactions import check_medication_interactions
        
        result = check_medication_interactions(
            medications=["fake_drug_xyz"],
            genotypes=comprehensive_genotypes
        )
        
        assert len(result["medications_not_found"]) == 1
        assert result["medications_not_found"][0]["input"] == "fake_drug_xyz"
    
    def test_drug_info_lookup(self):
        """Test drug info lookup."""
        from markers.medication_interactions import get_drug_info
        
        info = get_drug_info("warfarin")
        assert info is not None
        assert info["generic_name"] == "warfarin"
        assert "Coumadin" in info["brand_names"]
        
        assert get_drug_info("fake_drug") is None
    
    def test_list_all_drugs(self):
        """Test listing all drugs."""
        from markers.medication_interactions import list_all_drugs
        
        drugs = list_all_drugs()
        assert len(drugs) > 30
        assert "warfarin" in drugs
        assert "clopidogrel" in drugs
    
    def test_search_drugs(self):
        """Test drug search."""
        from markers.medication_interactions import search_drugs
        
        results = search_drugs("statin")
        assert len(results) >= 3  # simvastatin, atorvastatin, etc.
        
        results = search_drugs("coumadin")
        assert len(results) == 1
        assert results[0]["generic"] == "warfarin"


# =============================================================================
# SLEEP OPTIMIZATION TESTS
# =============================================================================

class TestSleepOptimization:
    """Tests for sleep optimization profile."""
    
    def test_imports(self):
        """Test sleep module imports."""
        from markers.sleep_optimization import (
            CHRONOTYPE_MARKERS, CAFFEINE_METABOLISM_MARKERS,
            SLEEP_MARKERS, generate_sleep_profile,
            Chronotype, CaffeineMetabolism
        )
        assert len(CHRONOTYPE_MARKERS) > 5
        assert len(CAFFEINE_METABOLISM_MARKERS) > 0
    
    def test_determine_chronotype(self, comprehensive_genotypes):
        """Test chronotype determination."""
        from markers.sleep_optimization import determine_chronotype
        
        result = determine_chronotype(comprehensive_genotypes)
        
        assert "chronotype" in result
        assert "ideal_wake_time" in result
        assert "ideal_sleep_time" in result
        assert "markers_analyzed" in result
        assert result["chronotype"] in ["definite_morning", "moderate_morning", 
                                        "intermediate", "moderate_evening", "definite_evening"]
    
    def test_determine_caffeine_metabolism(self, comprehensive_genotypes):
        """Test caffeine metabolism determination."""
        from markers.sleep_optimization import determine_caffeine_metabolism
        
        result = determine_caffeine_metabolism(comprehensive_genotypes)
        
        # CC at rs762551 = slow metabolizer
        assert result["metabolism_speed"] == "slow"
        assert result["max_daily_caffeine_mg"] <= 200
        assert result["cutoff_before_bed_hours"] >= 10
    
    def test_generate_sleep_profile(self, comprehensive_genotypes):
        """Test complete sleep profile generation."""
        from markers.sleep_optimization import generate_sleep_profile
        
        profile = generate_sleep_profile(comprehensive_genotypes)
        
        assert "profile_summary" in profile
        assert "optimal_timing" in profile
        assert "recommendations" in profile
        assert len(profile["recommendations"]) > 0
        
        assert "coffee_cutoff_time" in profile["optimal_timing"]
    
    def test_sleep_summary_text(self, comprehensive_genotypes):
        """Test plain-text sleep summary."""
        from markers.sleep_optimization import get_sleep_optimization_summary
        
        summary = get_sleep_optimization_summary(comprehensive_genotypes)
        
        assert "SLEEP OPTIMIZATION" in summary
        assert "Caffeine" in summary
        assert "Chronotype" in summary


# =============================================================================
# DIETARY INTERACTION TESTS
# =============================================================================

class TestDietaryInteractions:
    """Tests for dietary interaction matrix."""
    
    def test_imports(self):
        """Test dietary module imports."""
        from markers.dietary_interactions import (
            DIETARY_MARKERS, LACTOSE_MARKERS, GLUTEN_SENSITIVITY_MARKERS,
            analyze_dietary_interactions, ToleranceLevel
        )
        assert len(DIETARY_MARKERS) > 10
    
    def test_analyze_dietary_interactions(self, comprehensive_genotypes):
        """Test dietary interaction analysis."""
        from markers.dietary_interactions import analyze_dietary_interactions
        
        result = analyze_dietary_interactions(comprehensive_genotypes)
        
        assert "categories" in result
        assert "caffeine" in result["categories"]
        assert "lactose" in result["categories"]
        assert "gluten" in result["categories"]
        assert "saturated_fat" in result["categories"]
    
    def test_lactose_intolerance_detection(self, comprehensive_genotypes):
        """Test lactose intolerance detection."""
        from markers.dietary_interactions import analyze_dietary_interactions
        
        result = analyze_dietary_interactions(comprehensive_genotypes)
        
        # GG at rs4988235 = lactose intolerant
        lactose = result["categories"]["lactose"]
        assert lactose["markers_found"] > 0
    
    def test_apoe_diet_recommendations(self, comprehensive_genotypes):
        """Test APOE-based diet recommendations."""
        from markers.dietary_interactions import determine_apoe_diet_recommendations
        
        result = determine_apoe_diet_recommendations(comprehensive_genotypes)
        
        # E3/E4 carrier
        assert result["apoe_genotype"] in ["e3/e4", "ε3/ε4"]
        assert result["saturated_fat_sensitivity"] == "high"
        assert len(result["recommendations"]) > 0
    
    def test_dietary_report_text(self, comprehensive_genotypes):
        """Test dietary report text generation."""
        from markers.dietary_interactions import generate_dietary_matrix_report
        
        report = generate_dietary_matrix_report(comprehensive_genotypes)
        
        assert "DIETARY INTERACTION" in report
        assert "CAFFEINE" in report
        assert "LACTOSE" in report
    
    def test_food_specific_guidance(self, comprehensive_genotypes):
        """Test food-specific guidance lookup."""
        from markers.dietary_interactions import get_food_specific_guidance
        
        guidance = get_food_specific_guidance(comprehensive_genotypes, "coffee")
        
        assert guidance["food"] == "coffee"
        assert len(guidance["relevant_genes"]) > 0


# =============================================================================
# ATHLETIC PROFILE TESTS
# =============================================================================

class TestAthleticProfile:
    """Tests for athletic profiling."""
    
    def test_imports(self):
        """Test athletic module imports."""
        from markers.athletic_profile import (
            POWER_ENDURANCE_MARKERS, RECOVERY_MARKERS, INJURY_MARKERS,
            calculate_athletic_profile, AthleticType, RecoveryProfile
        )
        assert len(POWER_ENDURANCE_MARKERS) > 3
        assert len(RECOVERY_MARKERS) > 2
    
    def test_calculate_athletic_profile(self, comprehensive_genotypes):
        """Test athletic profile calculation."""
        from markers.athletic_profile import calculate_athletic_profile
        
        profile = calculate_athletic_profile(comprehensive_genotypes)
        
        assert "athletic_type" in profile
        assert "recovery_profile" in profile
        assert "injury_risk" in profile
        assert "vo2max_potential" in profile
        
        assert profile["athletic_type"]["type"] in ["power", "power_endurance", 
                                                     "balanced", "endurance_power", "endurance"]
    
    def test_training_recommendations(self, comprehensive_genotypes):
        """Test training recommendations generation."""
        from markers.athletic_profile import (
            calculate_athletic_profile, generate_training_recommendations
        )
        
        profile = calculate_athletic_profile(comprehensive_genotypes)
        recs = generate_training_recommendations(profile)
        
        assert len(recs) > 0
        assert all("category" in r for r in recs)
        assert all("recommendation" in r for r in recs)
    
    def test_athletic_report_text(self, comprehensive_genotypes):
        """Test athletic report text."""
        from markers.athletic_profile import generate_athletic_report
        
        report = generate_athletic_report(comprehensive_genotypes)
        
        assert "ATHLETIC" in report
        assert "POWER vs ENDURANCE" in report
        assert "RECOVERY" in report
    
    def test_sport_suitability(self, comprehensive_genotypes):
        """Test sport suitability scoring."""
        from markers.athletic_profile import get_sport_suitability
        
        result = get_sport_suitability(comprehensive_genotypes)
        
        assert "top_categories" in result
        assert len(result["top_categories"]) == 3
        assert all("score" in cat for cat in result["top_categories"])


# =============================================================================
# UV SENSITIVITY TESTS
# =============================================================================

class TestUVSensitivity:
    """Tests for UV sensitivity calculator."""
    
    def test_imports(self):
        """Test UV module imports."""
        from markers.uv_sensitivity import (
            MC1R_MARKERS, PIGMENTATION_MARKERS,
            generate_uv_sensitivity_report, SkinType, MelanomaRisk
        )
        assert len(MC1R_MARKERS) > 3
        assert len(PIGMENTATION_MARKERS) > 10
    
    def test_calculate_pigmentation(self, fair_skin_genotypes):
        """Test pigmentation score calculation."""
        from markers.uv_sensitivity import calculate_pigmentation_score
        
        result = calculate_pigmentation_score(fair_skin_genotypes)
        
        assert "normalized_score" in result
        assert "melanoma_risk_factor" in result
        assert result["normalized_score"] < 0  # Fair skin = negative score
    
    def test_estimate_skin_type(self, fair_skin_genotypes):
        """Test skin type estimation."""
        from markers.uv_sensitivity import (
            calculate_pigmentation_score, estimate_skin_type
        )
        
        pigment = calculate_pigmentation_score(fair_skin_genotypes)
        skin_type = estimate_skin_type(pigment["normalized_score"])
        
        # Fair skin should be Type I or II
        assert skin_type["skin_type"] in ["type_i", "type_ii"]
        assert skin_type["burn_time_unprotected_min"] <= 15
    
    def test_spf_recommendation(self, fair_skin_genotypes):
        """Test SPF recommendation."""
        from markers.uv_sensitivity import (
            calculate_pigmentation_score, estimate_skin_type,
            calculate_spf_recommendation
        )
        
        pigment = calculate_pigmentation_score(fair_skin_genotypes)
        skin_type = estimate_skin_type(pigment["normalized_score"])
        spf = calculate_spf_recommendation(skin_type)
        
        # Fair skin should recommend high SPF
        assert spf["recommended_spf"] >= 50
        assert len(spf["tips"]) > 0
    
    def test_melanoma_risk(self, fair_skin_genotypes):
        """Test melanoma risk calculation."""
        from markers.uv_sensitivity import (
            calculate_pigmentation_score, calculate_melanoma_risk
        )
        
        pigment = calculate_pigmentation_score(fair_skin_genotypes)
        melanoma = calculate_melanoma_risk(fair_skin_genotypes, pigment)
        
        # MC1R variants should elevate risk
        assert melanoma["risk_factor"] > 1.5
        assert melanoma["risk_level"] in ["elevated", "high"]
    
    def test_vitamin_d_synthesis(self, fair_skin_genotypes):
        """Test vitamin D synthesis estimation."""
        from markers.uv_sensitivity import calculate_vitamin_d_synthesis
        
        result = calculate_vitamin_d_synthesis(fair_skin_genotypes, -3)
        
        assert "synthesis_capacity" in result
        assert "sun_exposure_needed" in result
    
    def test_uv_report(self, fair_skin_genotypes):
        """Test complete UV report."""
        from markers.uv_sensitivity import generate_uv_sensitivity_report
        
        report = generate_uv_sensitivity_report(fair_skin_genotypes)
        
        assert "summary" in report
        assert "spf_recommendation" in report
        assert "melanoma_risk" in report
    
    def test_uv_report_text(self, fair_skin_genotypes):
        """Test UV report text."""
        from markers.uv_sensitivity import generate_uv_report_text
        
        text = generate_uv_report_text(fair_skin_genotypes)
        
        assert "UV SENSITIVITY" in text
        assert "SPF" in text
        assert "MELANOMA" in text


# =============================================================================
# NATURAL LANGUAGE EXPLANATION TESTS
# =============================================================================

class TestExplanations:
    """Tests for natural language explanations."""
    
    def test_imports(self):
        """Test explanation module imports."""
        from markers.explanations import (
            PUBMED_REFERENCES, RESEARCH_VARIANTS,
            generate_plain_english_explanation,
            EvidenceLevel
        )
        assert len(PUBMED_REFERENCES) > 10
        assert len(RESEARCH_VARIANTS) > 3
    
    def test_generate_explanation(self):
        """Test plain-English explanation generation."""
        from markers.explanations import generate_plain_english_explanation
        
        explanation = generate_plain_english_explanation(
            rsid="rs3892097",
            gene="CYP2D6",
            genotype="GA",
            trait="Drug metabolism",
            finding="Poor metabolizer carrier",
            evidence_level="established"
        )
        
        assert "summary" in explanation
        assert "what_it_means" in explanation
        assert "confidence_note" in explanation
        assert "pubmed_links" in explanation
        assert len(explanation["pubmed_links"]) > 0
    
    def test_pubmed_links(self):
        """Test PubMed link retrieval."""
        from markers.explanations import get_pubmed_links
        
        links = get_pubmed_links("rs3892097")
        
        assert len(links) > 0
        assert all("pmid" in link for link in links)
        assert all("url" in link for link in links)
        assert "pubmed.ncbi.nlm.nih.gov" in links[0]["url"]
    
    def test_research_variant_flagging(self):
        """Test research variant flagging."""
        from markers.explanations import flag_research_variants
        
        findings = [
            {"rsid": "rs6265", "gene": "BDNF"},  # Research variant
            {"rsid": "rs3892097", "gene": "CYP2D6"},  # Established
        ]
        
        flagged = flag_research_variants(findings)
        
        # BDNF should be flagged as research
        bdnf = next(f for f in flagged if f["rsid"] == "rs6265")
        assert bdnf["is_research_variant"] is True
        
        # CYP2D6 should be established
        cyp2d6 = next(f for f in flagged if f["rsid"] == "rs3892097")
        assert cyp2d6["is_research_variant"] is False
    
    def test_explain_risk_in_context(self):
        """Test contextual risk explanation."""
        from markers.explanations import explain_risk_in_context
        
        explanation = explain_risk_in_context(
            relative_risk=2.0,
            baseline_risk=0.05,  # 5% baseline
            condition="condition X"
        )
        
        assert "90%" in explanation  # 90% won't develop
        assert "lifestyle" in explanation.lower()
    
    def test_uncertainty_statement(self):
        """Test uncertainty statement generation."""
        from markers.explanations import generate_uncertainty_statement
        
        established = generate_uncertainty_statement("established")
        emerging = generate_uncertainty_statement("emerging")
        
        assert "clinical" in established.lower()
        assert "preliminary" in emerging.lower() or "research" in emerging.lower()


# =============================================================================
# ADVANCED GENETICS TESTS (ROH, TELOMERES)
# =============================================================================

class TestAdvancedGenetics:
    """Tests for advanced genetic analyses."""
    
    def test_imports(self):
        """Test advanced genetics imports."""
        from markers.advanced_genetics import (
            TELOMERE_MARKERS, LONGEVITY_RELATED_MARKERS,
            calculate_heterozygosity_rate, estimate_telomere_length,
            ROHLevel
        )
        assert len(TELOMERE_MARKERS) > 5
    
    def test_heterozygosity_calculation(self, comprehensive_genotypes):
        """Test heterozygosity rate calculation."""
        from markers.advanced_genetics import calculate_heterozygosity_rate
        
        result = calculate_heterozygosity_rate(comprehensive_genotypes)
        
        assert "heterozygosity_rate" in result
        assert "homozygosity_rate" in result
        assert "interpretation" in result
        assert 0 <= result["heterozygosity_rate"] <= 1
    
    def test_roh_detection(self, comprehensive_genotypes):
        """Test ROH detection."""
        from markers.advanced_genetics import detect_roh_regions
        
        result = detect_roh_regions(comprehensive_genotypes)
        
        # Without position data, should fall back to het rate
        assert "heterozygosity_analysis" in result or "roh_regions" in result
        assert "interpretation" in result
    
    def test_roh_report(self, comprehensive_genotypes):
        """Test ROH report generation."""
        from markers.advanced_genetics import generate_roh_report
        
        report = generate_roh_report(comprehensive_genotypes)
        
        assert "summary" in report
        assert "heterozygosity" in report
        assert "status" in report["summary"]
    
    def test_telomere_estimation(self, comprehensive_genotypes):
        """Test telomere length estimation."""
        from markers.advanced_genetics import estimate_telomere_length
        
        result = estimate_telomere_length(comprehensive_genotypes)
        
        assert "estimate" in result
        assert "percentile_estimate" in result
        assert "caveats" in result
        assert len(result["caveats"]) > 0
        assert "markers_analyzed" in result
    
    def test_longevity_associations(self, comprehensive_genotypes):
        """Test longevity association analysis."""
        from markers.advanced_genetics import estimate_longevity_associations
        
        result = estimate_longevity_associations(comprehensive_genotypes)
        
        assert "findings" in result
        assert "interpretation" in result
        assert "important_note" in result
        # Should find FOXO3 variant
        assert any(f["gene"] == "FOXO3" for f in result["findings"])
    
    def test_telomere_report_text(self, comprehensive_genotypes):
        """Test telomere report text generation."""
        from markers.advanced_genetics import generate_telomere_report
        
        text = generate_telomere_report(comprehensive_genotypes)
        
        assert "TELOMERE" in text
        assert "LONGEVITY" in text


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestV41Integration:
    """Integration tests for v4.1.0 features."""
    
    def test_all_modules_import(self):
        """Test all v4.1 modules import correctly."""
        from markers import (
            # Medication
            DRUG_DATABASE, check_medication_interactions,
            # Sleep
            SLEEP_MARKERS, generate_sleep_profile,
            # Dietary
            DIETARY_MARKERS, analyze_dietary_interactions,
            # Athletic
            POWER_ENDURANCE_MARKERS, calculate_athletic_profile,
            # UV
            PIGMENTATION_MARKERS, generate_uv_sensitivity_report,
            # Explanations
            PUBMED_REFERENCES, generate_plain_english_explanation,
            # Advanced
            TELOMERE_MARKERS, estimate_telomere_length,
            get_marker_counts
        )
        
        counts = get_marker_counts()
        assert "sleep_markers" in counts
        assert "athletic_markers" in counts
        assert "uv_sensitivity" in counts
    
    def test_marker_counts_v41(self):
        """Test v4.1 marker counts are reflected."""
        from markers import get_marker_counts
        
        counts = get_marker_counts()
        
        # v4.1 should add new markers
        assert counts["sleep_markers"] > 0
        assert counts["dietary_markers"] > 0
        assert counts["athletic_markers"] > 0
        assert counts["uv_sensitivity"] > 0
        assert counts["total"] > 1500  # Should have substantial total
    
    def test_combined_analysis(self, comprehensive_genotypes):
        """Test running all v4.1 analyses together."""
        from markers.medication_interactions import check_medication_interactions
        from markers.sleep_optimization import generate_sleep_profile
        from markers.dietary_interactions import analyze_dietary_interactions
        from markers.athletic_profile import calculate_athletic_profile
        from markers.uv_sensitivity import generate_uv_sensitivity_report
        from markers.advanced_genetics import estimate_telomere_length
        
        # Run all analyses - should not error
        med_result = check_medication_interactions(["warfarin"], comprehensive_genotypes)
        sleep_result = generate_sleep_profile(comprehensive_genotypes)
        diet_result = analyze_dietary_interactions(comprehensive_genotypes)
        athletic_result = calculate_athletic_profile(comprehensive_genotypes)
        uv_result = generate_uv_sensitivity_report(comprehensive_genotypes)
        telomere_result = estimate_telomere_length(comprehensive_genotypes)
        
        # All should have key fields
        assert "summary" in med_result
        assert "profile_summary" in sleep_result
        assert "categories" in diet_result
        assert "athletic_type" in athletic_result
        assert "summary" in uv_result
        assert "estimate" in telomere_result


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestV41EdgeCases:
    """Edge case tests for v4.1 features."""
    
    def test_empty_genotypes(self):
        """Test handling of empty genotype data."""
        from markers.medication_interactions import check_medication_interactions
        from markers.sleep_optimization import generate_sleep_profile
        from markers.dietary_interactions import analyze_dietary_interactions
        from markers.athletic_profile import calculate_athletic_profile
        from markers.uv_sensitivity import generate_uv_sensitivity_report
        
        empty = {}
        
        # Should not crash with empty data
        med = check_medication_interactions(["warfarin"], empty)
        sleep = generate_sleep_profile(empty)
        diet = analyze_dietary_interactions(empty)
        athletic = calculate_athletic_profile(empty)
        uv = generate_uv_sensitivity_report(empty)
        
        assert med is not None
        assert sleep is not None
        assert diet is not None
        assert athletic is not None
        assert uv is not None
    
    def test_empty_medication_list(self, comprehensive_genotypes):
        """Test medication check with empty list."""
        from markers.medication_interactions import check_medication_interactions
        
        result = check_medication_interactions([], comprehensive_genotypes)
        
        assert result["summary"]["total_medications"] == 0
    
    def test_case_insensitivity(self, comprehensive_genotypes):
        """Test case insensitivity of drug names."""
        from markers.medication_interactions import check_medication_interactions
        
        result1 = check_medication_interactions(["WARFARIN"], comprehensive_genotypes)
        result2 = check_medication_interactions(["warfarin"], comprehensive_genotypes)
        result3 = check_medication_interactions(["Warfarin"], comprehensive_genotypes)
        
        assert result1["summary"]["medications_checked"] == result2["summary"]["medications_checked"]
        assert result2["summary"]["medications_checked"] == result3["summary"]["medications_checked"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
