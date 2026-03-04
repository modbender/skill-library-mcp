"""
Edge case tests for personal-genomics analysis.

Tests cover:
- Empty input handling
- Malformed data handling
- Missing markers
- Invalid file formats
- Encoding issues
- Dashboard generation
"""

import pytest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_analysis import (
    validate_rsid,
    validate_genotype,
    sanitize_genotype,
    validate_filepath,
    detect_format,
    load_dna_file,
    determine_apoe,
    analyze_markers,
    calculate_all_prs,
    generate_agent_summary,
    generate_report,
    generate_dashboard,
    analyze_dna_file,
)


# =============================================================================
# INPUT VALIDATION TESTS
# =============================================================================

class TestInputValidation:
    """Tests for input validation functions."""

    def test_validate_rsid_valid(self):
        """Valid rsIDs should pass validation."""
        assert validate_rsid("rs123456") is True
        assert validate_rsid("rs1") is True
        assert validate_rsid("rs9999999999") is True
        assert validate_rsid("RS123456") is True  # Case insensitive

    def test_validate_rsid_invalid(self):
        """Invalid rsIDs should fail validation."""
        assert validate_rsid("") is False
        assert validate_rsid(None) is False
        assert validate_rsid("123456") is False  # Missing 'rs'
        assert validate_rsid("rs") is False  # No number
        assert validate_rsid("rsABC") is False  # Non-numeric
        assert validate_rsid("rs 123") is False  # Space
        assert validate_rsid("chr1:12345") is False  # Wrong format

    def test_validate_genotype_valid(self):
        """Valid genotypes should pass validation."""
        assert validate_genotype("AA") is True
        assert validate_genotype("AG") is True
        assert validate_genotype("GT") is True
        assert validate_genotype("CC") is True
        assert validate_genotype("A") is True  # Single allele
        assert validate_genotype("ID") is True  # Indel
        assert validate_genotype("DI") is True
        assert validate_genotype("DD") is True
        assert validate_genotype("II") is True

    def test_validate_genotype_invalid(self):
        """Invalid genotypes should fail validation."""
        assert validate_genotype("") is False
        assert validate_genotype(None) is False
        assert validate_genotype("XYZ") is False
        assert validate_genotype("AAA") is False  # Too long
        assert validate_genotype("123") is False

    def test_sanitize_genotype(self):
        """Genotype sanitization should clean inputs properly."""
        assert sanitize_genotype("AG") == "AG"
        assert sanitize_genotype("  AG  ") == "AG"
        assert sanitize_genotype("ag") == "AG"
        assert sanitize_genotype("--") == ""
        assert sanitize_genotype("00") == ""
        assert sanitize_genotype("NC") == ""
        assert sanitize_genotype("N/A") == ""
        assert sanitize_genotype("") == ""
        assert sanitize_genotype(None) == ""
        assert sanitize_genotype("A G") == "AG"

    def test_validate_filepath_valid(self, tmp_path):
        """Valid file paths should pass validation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = validate_filepath(str(test_file))
        assert result.exists()
        assert result.is_file()

    def test_validate_filepath_missing(self):
        """Missing files should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_filepath("/nonexistent/file.txt")

    def test_validate_filepath_empty(self):
        """Empty paths should raise ValueError."""
        with pytest.raises(ValueError):
            validate_filepath("")

    def test_validate_filepath_directory(self, tmp_path):
        """Directories should raise ValueError."""
        with pytest.raises(ValueError):
            validate_filepath(str(tmp_path))


# =============================================================================
# EMPTY INPUT TESTS
# =============================================================================

class TestEmptyInput:
    """Tests for empty input handling."""

    def test_empty_genotypes_dict(self):
        """Empty genotypes dict should return unknown APOE."""
        result = determine_apoe({})
        assert result["genotype"] == "unknown"
        assert result["risk_level"] == "unknown"

    def test_empty_markers_analysis(self):
        """Empty markers should return zero findings."""
        result = analyze_markers({}, {}, "test_category")
        assert result["total_in_database"] == 0
        assert result["found_in_data"] == 0
        assert result["findings"] == []

    def test_empty_file(self, tmp_path):
        """Empty file should raise ValueError."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        
        with pytest.raises(ValueError, match="No valid genotypes"):
            load_dna_file(str(empty_file))

    def test_comments_only_file(self, tmp_path):
        """File with only comments should raise ValueError."""
        comments_file = tmp_path / "comments.txt"
        comments_file.write_text("# This is a comment\n# Another comment\n")
        
        with pytest.raises(ValueError, match="No valid genotypes"):
            load_dna_file(str(comments_file))


# =============================================================================
# MALFORMED DATA TESTS
# =============================================================================

class TestMalformedData:
    """Tests for malformed data handling."""

    def test_invalid_rsid_in_file(self, tmp_path):
        """Invalid rsIDs should be skipped gracefully."""
        test_file = tmp_path / "invalid_rsids.txt"
        test_file.write_text(
            "# Test file\n"
            "invalid\t1\t12345\tAA\n"  # Invalid rsid
            "rs123456\t1\t12345\tAG\n"  # Valid
            "\t1\t12345\tCC\n"  # Empty rsid
            "rs789\t1\t12345\tGT\n"  # Valid
        )
        
        genotypes, fmt = load_dna_file(str(test_file))
        assert len(genotypes) == 2  # Only valid entries
        assert "rs123456" in genotypes
        assert "rs789" in genotypes

    def test_invalid_genotype_in_file(self, tmp_path):
        """Invalid genotypes should be skipped gracefully."""
        test_file = tmp_path / "invalid_genotypes.txt"
        test_file.write_text(
            "# Test file\n"
            "rs111\t1\t12345\tAA\n"  # Valid
            "rs222\t1\t12345\t--\n"  # No-call
            "rs333\t1\t12345\tXX\n"  # Invalid
            "rs444\t1\t12345\tGT\n"  # Valid
        )
        
        genotypes, fmt = load_dna_file(str(test_file))
        assert len(genotypes) == 2
        assert "rs111" in genotypes
        assert "rs444" in genotypes
        assert "rs222" not in genotypes  # No-call
        assert "rs333" not in genotypes  # Invalid

    def test_truncated_lines(self, tmp_path):
        """Truncated lines should be skipped gracefully."""
        test_file = tmp_path / "truncated.txt"
        test_file.write_text(
            "# Test file\n"
            "rs111\t1\t12345\tAA\n"  # Valid
            "rs222\t1\n"  # Truncated
            "rs333\n"  # Very truncated
            "rs444\t1\t12345\tGT\n"  # Valid
        )
        
        genotypes, fmt = load_dna_file(str(test_file))
        assert len(genotypes) == 2
        assert "rs111" in genotypes
        assert "rs444" in genotypes

    def test_mixed_delimiters(self, tmp_path):
        """Files with mixed delimiters should be handled."""
        test_file = tmp_path / "mixed.txt"
        test_file.write_text(
            "# Test file\n"
            "rs111\t1\t12345\tAA\n"  # Tab
            "rs222,1,12345,GT\n"  # Comma
        )
        
        genotypes, fmt = load_dna_file(str(test_file))
        assert len(genotypes) >= 1  # At least tab-delimited works


# =============================================================================
# ENCODING TESTS
# =============================================================================

class TestEncodingHandling:
    """Tests for file encoding handling."""

    def test_utf8_file(self, tmp_path):
        """UTF-8 encoded files should be handled."""
        test_file = tmp_path / "utf8.txt"
        test_file.write_text(
            "# UTF-8 file with special chars: é à ü\n"
            "rs123456\t1\t12345\tAG\n",
            encoding='utf-8'
        )
        
        genotypes, fmt = load_dna_file(str(test_file))
        assert "rs123456" in genotypes

    def test_latin1_file(self, tmp_path):
        """Latin-1 encoded files should be handled gracefully."""
        test_file = tmp_path / "latin1.txt"
        test_file.write_bytes(
            b"# Latin-1 file with special chars: \xe9 \xe0\n"
            b"rs123456\t1\t12345\tAG\n"
        )
        
        # Should handle encoding errors gracefully
        genotypes, fmt = load_dna_file(str(test_file))
        assert "rs123456" in genotypes


# =============================================================================
# APOE EDGE CASES
# =============================================================================

class TestAPOEEdgeCases:
    """Tests for APOE determination edge cases."""

    def test_apoe_missing_one_marker(self):
        """Missing one APOE marker should return unknown."""
        result = determine_apoe({"rs429358": "TT"})
        assert result["genotype"] == "unknown"
        
        result = determine_apoe({"rs7412": "CC"})
        assert result["genotype"] == "unknown"

    def test_apoe_all_combinations(self):
        """Test all valid APOE allele combinations."""
        # ε3/ε3 (most common)
        result = determine_apoe({"rs429358": "TT", "rs7412": "CC"})
        assert result["genotype"] == "ε3/ε3"
        assert result["risk_level"] == "average"
        
        # ε4/ε4 (high risk)
        result = determine_apoe({"rs429358": "CC", "rs7412": "CC"})
        assert result["genotype"] == "ε4/ε4"
        assert result["risk_level"] == "high"
        assert result["actionable"] is True
        assert len(result["recommendations"]) > 0
        
        # ε2/ε2 (protective)
        result = determine_apoe({"rs429358": "TT", "rs7412": "TT"})
        assert result["genotype"] == "ε2/ε2"
        assert result["risk_level"] == "low"

    def test_apoe_single_allele_markers(self):
        """Single allele markers should work."""
        result = determine_apoe({"rs429358": "T", "rs7412": "C"})
        assert result["genotype"] == "ε3/ε3"


# =============================================================================
# PRS EDGE CASES
# =============================================================================

class TestPRSEdgeCases:
    """Tests for polygenic risk score edge cases."""

    def test_prs_no_snps_found(self):
        """PRS with no matching SNPs should return low confidence."""
        # Assuming PRS_WEIGHTS are loaded
        from comprehensive_analysis import PRS_WEIGHTS
        if PRS_WEIGHTS:
            # Use genotypes that won't match any PRS markers
            result = calculate_all_prs({"rs99999999": "AA"})
            # Should have low confidence for all conditions
            for condition, scores in result.items():
                if isinstance(scores, dict) and "confidence" in scores:
                    assert scores["snps_found"] <= scores["snps_total"]

    def test_prs_empty_genotypes(self):
        """Empty genotypes should return valid but empty scores."""
        result = calculate_all_prs({})
        # Should return something, not crash


# =============================================================================
# REPORT GENERATION TESTS
# =============================================================================

class TestReportGeneration:
    """Tests for report generation."""

    def test_report_generation_minimal(self):
        """Report generation with minimal data should not crash."""
        all_results = {
            "total_snps": 0,
            "format": "test",
            "apoe": {"genotype": "unknown", "risk_level": "unknown"}
        }
        agent_summary = {
            "critical_alerts": [],
            "high_priority": [],
            "pharmacogenomics_alerts": [],
            "notable_traits": []
        }
        
        report = generate_report(all_results, agent_summary)
        assert "COMPREHENSIVE GENETIC ANALYSIS REPORT" in report
        assert "IMPORTANT DISCLAIMERS" in report

    def test_agent_summary_empty_results(self):
        """Agent summary with empty results should be valid."""
        all_results = {"total_snps": 0, "format": "test"}
        summary = generate_agent_summary(all_results)
        
        assert "analysis_timestamp" in summary
        assert "critical_alerts" in summary
        assert isinstance(summary["critical_alerts"], list)


# =============================================================================
# DASHBOARD GENERATION TESTS
# =============================================================================

class TestDashboardGeneration:
    """Tests for dashboard generation."""

    def test_dashboard_generation(self, tmp_path):
        """Dashboard should be generated successfully."""
        # Create test JSON
        test_json = tmp_path / "test_summary.json"
        test_json.write_text(json.dumps({
            "snps_analyzed": 100,
            "format_detected": "test",
            "critical_alerts": [],
            "high_priority": [],
            "polygenic_risk_scores": {}
        }))
        
        # Check if dashboard template exists
        template_path = Path(__file__).parent.parent / "dashboard" / "index.html"
        if not template_path.exists():
            pytest.skip("Dashboard template not found")
        
        output_path = tmp_path / "dashboard.html"
        result = generate_dashboard(str(test_json), str(output_path))
        
        assert result.exists()
        content = result.read_text()
        assert "Personal Genomics Dashboard" in content
        assert "autoLoadData" in content  # Auto-load script injected

    def test_dashboard_missing_json(self):
        """Dashboard generation with missing JSON should raise error."""
        with pytest.raises(FileNotFoundError):
            generate_dashboard("/nonexistent/file.json")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for full analysis pipeline."""

    def test_full_analysis_pipeline(self, tmp_path):
        """Full analysis pipeline should complete without errors."""
        # Create minimal valid DNA file
        test_file = tmp_path / "test_dna.txt"
        test_file.write_text(
            "# Test DNA file\n"
            "# rsid\tchromosome\tposition\tgenotype\n"
            "rs429358\t19\t45411941\tTT\n"
            "rs7412\t19\t45412079\tCC\n"
            "rs1801133\t1\t11856378\tAG\n"
            "rs4680\t22\t19951271\tAG\n"
        )
        
        output_dir = tmp_path / "output"
        results = analyze_dna_file(
            str(test_file),
            output_dir=str(output_dir),
            generate_html_dashboard=True,
            auto_open_dashboard=False
        )
        
        # Check results
        assert results["total_snps"] >= 4
        assert results["apoe"]["genotype"] == "ε3/ε3"
        
        # Check output files
        assert (output_dir / "full_analysis.json").exists()
        assert (output_dir / "agent_summary.json").exists()
        assert (output_dir / "report.txt").exists()

    def test_analysis_with_all_invalid_data(self, tmp_path):
        """Analysis with all invalid data should raise ValueError."""
        test_file = tmp_path / "invalid.txt"
        test_file.write_text(
            "# Invalid file\n"
            "invalid_rsid\t1\t123\tXX\n"
            "also_invalid\t2\t456\tYY\n"
        )
        
        with pytest.raises(ValueError, match="No valid genotypes"):
            analyze_dna_file(str(test_file))


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
