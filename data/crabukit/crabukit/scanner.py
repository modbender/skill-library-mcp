"""Enhanced main scanner orchestrator with comprehensive security analysis."""

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from crabukit.parsers.skill_md import SkillMdParser
from crabukit.parsers.scripts import ScriptParser
from crabukit.analyzers.python_ast import PythonAnalyzer
from crabukit.analyzers.bash_static import BashAnalyzer
from crabukit.analyzers.permissions import PermissionAnalyzer
from crabukit.rules.patterns import Finding, Severity
from crabukit.external_scanners import (
    run_external_scanners,
    convert_external_to_findings,
    check_clawdex_installed,
)


@dataclass
class ScanResult:
    """Complete scan result for a skill."""
    skill_path: Path
    skill_name: str
    findings: List[Finding]
    files_scanned: int
    scripts_scanned: int
    errors: List[str]
    scan_duration_ms: float = 0
    
    @property
    def score(self) -> int:
        """Calculate a security score (0-100, higher is worse)."""
        score = 0
        for finding in self.findings:
            if finding.severity == Severity.CRITICAL:
                score += 25
            elif finding.severity == Severity.HIGH:
                score += 10
            elif finding.severity == Severity.MEDIUM:
                score += 3
            elif finding.severity == Severity.LOW:
                score += 1
        return min(score, 100)
    
    @property
    def risk_level(self) -> str:
        """Get risk level based on score."""
        score = self.score
        if score >= 50:
            return "CRITICAL"
        elif score >= 25:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "CLEAN"
    
    @property
    def critical_count(self) -> int:
        return len(self.findings_by_severity(Severity.CRITICAL))
    
    @property
    def high_count(self) -> int:
        return len(self.findings_by_severity(Severity.HIGH))
    
    @property
    def medium_count(self) -> int:
        return len(self.findings_by_severity(Severity.MEDIUM))
    
    @property
    def low_count(self) -> int:
        return len(self.findings_by_severity(Severity.LOW))
    
    @property
    def info_count(self) -> int:
        return len(self.findings_by_severity(Severity.INFO))
    
    def findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Get findings filtered by severity."""
        return [f for f in self.findings if f.severity == severity]
    
    def findings_by_category(self, category: str) -> List[Finding]:
        """Get findings filtered by category prefix."""
        return [f for f in self.findings if f.rule_id.startswith(category)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "skill_name": self.skill_name,
            "skill_path": str(self.skill_path),
            "score": self.score,
            "risk_level": self.risk_level,
            "files_scanned": self.files_scanned,
            "scripts_scanned": self.scripts_scanned,
            "scan_duration_ms": self.scan_duration_ms,
            "summary": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
                "total": len(self.findings),
            },
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "title": f.title,
                    "description": f.description,
                    "severity": f.severity.value,
                    "file": f.file_path,
                    "line": f.line_number,
                    "snippet": f.code_snippet,
                    "remediation": f.remediation,
                    "cwe": f.cwe_id,
                    "references": f.references,
                }
                for f in self.findings
            ],
            "errors": self.errors,
        }


class SkillScanner:
    """Main scanner for OpenClaw skills with comprehensive security analysis."""
    
    def __init__(self, skill_path: str | Path):
        self.skill_path = Path(skill_path).resolve()
        self.findings: List[Finding] = []
        self.errors: List[str] = []
        self.files_scanned = 0
        self.scripts_scanned = 0
        
    def scan(self) -> ScanResult:
        """Run complete security scan."""
        import time
        start_time = time.time()
        
        self.findings = []
        self.errors = []
        self.files_scanned = 0
        self.scripts_scanned = 0
        
        # Validate skill exists
        if not self.skill_path.exists():
            self.errors.append(f"Skill path does not exist: {self.skill_path}")
            return self._build_result()
        
        if not self.skill_path.is_dir():
            self.errors.append(f"Skill path is not a directory: {self.skill_path}")
            return self._build_result()
        
        # Run external scanners (Clawdex, etc.) if available
        skill_name = self.skill_path.name
        external_results = run_external_scanners(skill_name)
        if external_results:
            external_findings = convert_external_to_findings(external_results)
            self.findings.extend(external_findings)
            # If Clawdex reports malicious, we can skip further scanning
            if any(r.is_malicious for r in external_results):
                duration_ms = (time.time() - start_time) * 1000
                return self._build_result(skill_name, duration_ms)
        
        # Parse SKILL.md
        skill_parser = SkillMdParser(self.skill_path)
        metadata = skill_parser.parse()
        
        if metadata is None:
            self.errors.append(f"No SKILL.md found in {self.skill_path}")
            skill_name = self.skill_path.name
        else:
            skill_name = metadata.name
            self.files_scanned += 1
            
            # Analyze SKILL.md content for prompt injection
            content_findings = skill_parser.check_content_patterns()
            for finding_data in content_findings:
                self.findings.append(Finding(
                    rule_id=finding_data["rule_id"],
                    title=finding_data["title"],
                    description=finding_data["description"],
                    severity=finding_data["severity"],
                    file_path=str(metadata.file_path),
                    line_number=finding_data["line"],
                    code_snippet=finding_data.get("snippet"),
                    cwe_id=finding_data.get("cwe_id"),
                    references=finding_data.get("references"),
                ))
            
            # Analyze description quality
            desc_findings = skill_parser.analyze_description_quality()
            for finding_data in desc_findings:
                self.findings.append(Finding(
                    rule_id=finding_data["rule_id"],
                    title=finding_data["title"],
                    description=finding_data["description"],
                    severity=finding_data["severity"],
                    file_path=str(metadata.file_path),
                    line_number=finding_data["line"],
                ))
            
            # Analyze permissions
            perm_analyzer = PermissionAnalyzer(metadata, self.skill_path)
            self.findings.extend(perm_analyzer.analyze())
        
        # Scan scripts
        script_parser = ScriptParser(self.skill_path)
        scripts = script_parser.discover_scripts()
        
        for script in scripts:
            self.files_scanned += 1
            self.scripts_scanned += 1
            
            if script.language == 'python':
                analyzer = PythonAnalyzer(
                    content=script.content,
                    ast_tree=script.ast_tree,
                    file_path=script.path
                )
                self.findings.extend(analyzer.analyze())
            
            elif script.language == 'bash':
                analyzer = BashAnalyzer(
                    content=script.content,
                    file_path=script.path
                )
                self.findings.extend(analyzer.analyze())
        
        # Check for hidden files (potential steganography)
        self._check_hidden_files()
        
        # Check for unexpected file types
        self._check_file_types()
        
        duration_ms = (time.time() - start_time) * 1000
        return self._build_result(skill_name, duration_ms)
    
    def _check_hidden_files(self):
        """Check for hidden files that might contain malicious content."""
        for item in self.skill_path.rglob("*"):
            if item.is_file() and item.name.startswith('.'):
                self.findings.append(Finding(
                    rule_id="HIDDEN_FILE",
                    title=f"Hidden file: {item.name}",
                    description="Skill contains hidden file - may be used to hide malicious content",
                    severity=Severity.LOW,
                    file_path=str(item),
                    line_number=1,
                ))
    
    def _check_file_types(self):
        """Check for unexpected or dangerous file types."""
        dangerous_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin'}
        
        for item in self.skill_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in dangerous_extensions:
                self.findings.append(Finding(
                    rule_id="DANGEROUS_FILE_TYPE",
                    title=f"Binary executable: {item.name}",
                    description=f"Skill contains {item.suffix} file - binary executables are unusual in skills",
                    severity=Severity.HIGH,
                    file_path=str(item),
                    line_number=1,
                ))
    
    def _build_result(self, skill_name: str = "unknown", duration_ms: float = 0) -> ScanResult:
        """Build the final scan result."""
        # Sort findings by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        self.findings.sort(key=lambda f: severity_order.get(f.severity, 5))
        
        return ScanResult(
            skill_path=self.skill_path,
            skill_name=skill_name,
            findings=self.findings,
            files_scanned=self.files_scanned,
            scripts_scanned=self.scripts_scanned,
            errors=self.errors,
            scan_duration_ms=duration_ms,
        )
