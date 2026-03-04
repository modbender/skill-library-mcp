"""Basic tests for crabukit."""

import pytest
from pathlib import Path

from crabukit.scanner import SkillScanner
from crabukit.rules.patterns import Severity


class TestSkillScanner:
    """Test the SkillScanner class."""
    
    def test_scan_valid_skill(self, tmp_path):
        """Test scanning a valid skill structure."""
        # Create a minimal skill
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---

# Test Skill

This is a test skill.
""")
        
        scanner = SkillScanner(str(skill_dir))
        result = scanner.scan()
        
        assert result.skill_name == "test-skill"
        assert result.files_scanned >= 1
        assert isinstance(result.findings, list)
    
    def test_scan_empty_directory(self, tmp_path):
        """Test scanning an empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        scanner = SkillScanner(str(empty_dir))
        result = scanner.scan()
        
        assert len(result.errors) > 0
        assert "No SKILL.md found" in result.errors[0]
    
    def test_risk_level_clean(self):
        """Test risk level calculation for clean result."""
        from crabukit.scanner import ScanResult
        from pathlib import Path
        
        result = ScanResult(
            skill_path=Path("/tmp/test"),
            skill_name="test",
            findings=[],
            files_scanned=1,
            scripts_scanned=0,
            errors=[]
        )
        
        assert result.score == 0
        assert result.risk_level == "CLEAN"
    
    def test_risk_level_high(self):
        """Test risk level calculation for high result (single critical finding)."""
        from crabukit.scanner import ScanResult
        from crabukit.rules.patterns import Finding, Severity
        from pathlib import Path
        
        result = ScanResult(
            skill_path=Path("/tmp/test"),
            skill_name="test",
            findings=[
                Finding(
                    rule_id="TEST_CRITICAL",
                    title="Test critical",
                    description="Test",
                    severity=Severity.CRITICAL,
                    file_path="test",
                    line_number=1
                )
            ],
            files_scanned=1,
            scripts_scanned=0,
            errors=[]
        )
        
        assert result.score == 25  # CRITICAL = 25 points
        assert result.risk_level == "HIGH"  # 25 points = HIGH (>=25, <50)


class TestPatterns:
    """Test detection patterns."""
    
    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestFixtures:
    """Test with fixture skills."""
    
    def test_malicious_skill_detection(self):
        """Test that malicious skill is detected."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        malicious_skill = fixtures_dir / "malicious-skill"
        
        if not malicious_skill.exists():
            pytest.skip("Malicious skill fixture not found")
        
        scanner = SkillScanner(str(malicious_skill))
        result = scanner.scan()
        
        # Should have critical or high findings
        critical_high = [f for f in result.findings 
                        if f.severity in (Severity.CRITICAL, Severity.HIGH)]
        assert len(critical_high) > 0, "Should detect issues in malicious skill"
    
    def test_clean_skill(self):
        """Test that clean skill has low/no findings."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        clean_skill = fixtures_dir / "low-risk-skill"
        
        if not clean_skill.exists():
            pytest.skip("Clean skill fixture not found")
        
        scanner = SkillScanner(str(clean_skill))
        result = scanner.scan()
        
        # Should have minimal findings
        assert result.score < 10, "Clean skill should have low score"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
