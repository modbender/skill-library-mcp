"""
SenseGuard Layer 1: Rule Engine
Fast, local pattern matching against known malicious patterns.
Zero LLM cost, millisecond execution.
"""

import os
import re
import glob
import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class Finding:
    """A single detection finding."""
    rule_id: str
    category: str
    severity: str          # critical, high, medium, low
    description: str
    description_zh: str
    evidence: str          # the matched text
    file_path: str
    line_number: int
    layer: str = "layer1"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StructureFinding:
    """A file structure check finding."""
    check_name: str
    severity: str
    description: str
    details: str = ""
    layer: str = "layer1"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Layer1Result:
    """Complete result from Layer 1 scanning."""
    pattern_findings: List[Finding] = field(default_factory=list)
    structure_findings: List[StructureFinding] = field(default_factory=list)
    files_scanned: int = 0
    rules_loaded: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.pattern_findings if f.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.pattern_findings if f.severity == "high")

    @property
    def medium_count(self) -> int:
        pf = sum(1 for f in self.pattern_findings if f.severity == "medium")
        sf = sum(1 for f in self.structure_findings if f.severity == "medium")
        return pf + sf

    @property
    def low_count(self) -> int:
        pf = sum(1 for f in self.pattern_findings if f.severity == "low")
        sf = sum(1 for f in self.structure_findings if f.severity == "low")
        return pf + sf

    @property
    def has_suspicious(self) -> bool:
        """Returns True if any high or critical findings exist."""
        return self.critical_count > 0 or self.high_count > 0

    def to_dict(self) -> dict:
        return {
            "pattern_findings": [f.to_dict() for f in self.pattern_findings],
            "structure_findings": [f.to_dict() for f in self.structure_findings],
            "files_scanned": self.files_scanned,
            "rules_loaded": self.rules_loaded,
            "summary": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
            }
        }


class RuleEngine:
    """Layer 1: Pattern-matching rule engine for fast local scanning."""

    # Common hidden files that are NOT suspicious
    SAFE_HIDDEN_FILES = {
        ".gitignore", ".gitkeep", ".gitattributes", ".editorconfig",
        ".npmrc", ".nvmrc", ".python-version", ".tool-versions",
        ".eslintrc", ".prettierrc", ".dockerignore",
    }

    SUSPICIOUS_BINARY_EXTS = {
        ".exe", ".dll", ".so", ".dylib", ".msi", ".dmg", ".pkg",
        ".bin", ".com", ".bat", ".cmd", ".scr", ".pif",
    }

    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir is None:
            rules_dir = os.path.join(os.path.dirname(__file__), "rules")
        self.rules_dir = rules_dir
        self.rules: Dict[str, dict] = {}
        self._load_rules()

    def _load_rules(self):
        """Load all YAML rule files from the rules directory."""
        pattern = os.path.join(self.rules_dir, "*.yaml")
        for rule_file in glob.glob(pattern):
            with open(rule_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "category" in data and "rules" in data:
                self.rules[data["category"]] = data

    @property
    def total_rules(self) -> int:
        count = 0
        for cat_data in self.rules.values():
            for severity_rules in cat_data.get("rules", {}).values():
                if isinstance(severity_rules, list):
                    count += len(severity_rules)
        return count

    def scan_skill(self, skill_dir: str, exclude_scanner_code: bool = True) -> Layer1Result:
        """Run full Layer 1 scan on a skill directory.
        
        Args:
            skill_dir: Root directory of the skill to scan.
            exclude_scanner_code: If True, skip 'rules' and 'scripts' directories.
                                 (automatically True when scanning senseguard itself)
        """
        result = Layer1Result()
        result.rules_loaded = self.total_rules

        # Collect all text files to scan
        files_to_scan = self._collect_files(skill_dir, exclude_scanner_code=exclude_scanner_code)
        result.files_scanned = len(files_to_scan)

        # Pattern matching on each file
        for file_path in files_to_scan:
            self._scan_file(file_path, result)

        # Structure checks
        self._check_structure(skill_dir, result)

        return result

    def _collect_files(self, skill_dir: str, exclude_scanner_code: bool = True) -> List[str]:
        """Collect all text files in the skill directory for scanning.
        
        Args:
            skill_dir: Root directory of the skill to scan.
            exclude_scanner_code: If True, skip 'rules' and 'scripts' directories
                                 (used when scanning the scanner tool itself).
        """
        text_extensions = {
            ".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh",
            ".bash", ".zsh", ".js", ".ts", ".rb", ".pl", ".lua",
            ".toml", ".ini", ".cfg", ".conf", ".xml", ".html",
            ".css", ".env", ".dockerfile",
        }
        
        # Directories to always skip
        skip_dirs = {".git", "__pycache__", "cache", ".DS_Store", "node_modules"}
        
        # If scanning the scanner itself, also skip rules and scripts
        if exclude_scanner_code:
            skip_dirs.update({"rules", "scripts"})
        
        files = []
        for root, dirs, filenames in os.walk(skill_dir):
            # Skip hidden directories and cache
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in skip_dirs]
            for fname in filenames:
                fpath = os.path.join(root, fname)
                ext = os.path.splitext(fname)[1].lower()
                # Include files with known text extensions or no extension
                if ext in text_extensions or ext == "":
                    files.append(fpath)
                # Also include SKILL.md explicitly (no ext check needed, but safety)
                elif fname == "SKILL.md":
                    files.append(fpath)
        return list(set(files))  # deduplicate

    def _is_in_example_context(self, lines: List[str], line_num: int) -> bool:
        """Check if a line is in an example/documentation context.
        
        Returns True if the line appears in a section describing examples of bad code,
        marked by keywords like "catches", "detect", "example", "bad", etc.
        """
        # Look back up to 5 lines for context
        context_start = max(0, line_num - 6)
        context_lines = "".join(lines[context_start:line_num]).lower()
        
        example_markers = {
            "catches what", "detects", "detects when", "detect:",
            "example", "example:", "bad example", "malicious example",
            "what not to do", "do not write", "avoid", "avoid:",
            "shows how", "demonstrates", "illustration", "anti-pattern",
        }
        
        return any(marker in context_lines for marker in example_markers)

    def _scan_file(self, file_path: str, result: Layer1Result):
        """Scan a single file against all loaded rules."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except (OSError, IOError):
            return

        # Also check for zero-width characters at the raw byte level
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
            self._check_zero_width(raw_bytes, file_path, result)
        except (OSError, IOError):
            pass

        full_text = "".join(lines)

        for category, cat_data in self.rules.items():
            rules_by_severity = cat_data.get("rules", {})
            for severity, rule_list in rules_by_severity.items():
                if not isinstance(rule_list, list):
                    continue
                for rule in rule_list:
                    pattern = rule.get("pattern", "")
                    if not pattern:
                        continue
                    try:
                        regex = re.compile(pattern, re.IGNORECASE)
                    except re.error:
                        continue

                    # Scan line by line for precise line numbers
                    for line_num, line in enumerate(lines, start=1):
                        match = regex.search(line)
                        if match:
                            # Skip if this is in an example/documentation context
                            if self._is_in_example_context(lines, line_num):
                                continue
                            
                            result.pattern_findings.append(Finding(
                                rule_id=rule.get("id", "UNKNOWN"),
                                category=category,
                                severity=severity,
                                description=rule.get("description", ""),
                                description_zh=rule.get("description_zh", ""),
                                evidence=match.group(0).strip()[:200],
                                file_path=file_path,
                                line_number=line_num,
                            ))

                    # Also check multi-line patterns against full text
                    if category == "obfuscation":
                        for match in regex.finditer(full_text):
                            # Find approximate line number
                            pos = match.start()
                            approx_line = full_text[:pos].count("\n") + 1
                            # Avoid duplicate if already found via line scan
                            already_found = any(
                                f.rule_id == rule.get("id") and f.file_path == file_path
                                for f in result.pattern_findings
                            )
                            if not already_found:
                                result.pattern_findings.append(Finding(
                                    rule_id=rule.get("id", "UNKNOWN"),
                                    category=category,
                                    severity=severity,
                                    description=rule.get("description", ""),
                                    description_zh=rule.get("description_zh", ""),
                                    evidence=match.group(0).strip()[:200],
                                    file_path=file_path,
                                    line_number=approx_line,
                                ))

    def _check_zero_width(self, raw_bytes: bytes, file_path: str, result: Layer1Result):
        """Detect zero-width characters in raw bytes."""
        zw_patterns = [
            (b"\xe2\x80\x8b", "U+200B ZERO WIDTH SPACE"),
            (b"\xe2\x80\x8c", "U+200C ZERO WIDTH NON-JOINER"),
            (b"\xe2\x80\x8d", "U+200D ZERO WIDTH JOINER"),
            (b"\xef\xbb\xbf", "U+FEFF BOM / ZERO WIDTH NO-BREAK SPACE"),
        ]
        for zw_bytes, zw_name in zw_patterns:
            idx = raw_bytes.find(zw_bytes)
            if idx != -1:
                approx_line = raw_bytes[:idx].count(b"\n") + 1
                result.pattern_findings.append(Finding(
                    rule_id="OB001",
                    category="obfuscation",
                    severity="high",
                    description="Zero-width character hidden text",
                    description_zh="零宽字符隐藏文本",
                    evidence=f"{zw_name} found at byte offset {idx}",
                    file_path=file_path,
                    line_number=approx_line,
                ))

    def _check_structure(self, skill_dir: str, result: Layer1Result):
        """Run file structure compliance checks."""
        skill_md = os.path.join(skill_dir, "SKILL.md")

        # Check SKILL.md exists
        if not os.path.isfile(skill_md):
            result.structure_findings.append(StructureFinding(
                check_name="missing_skill_md",
                severity="high",
                description="Missing SKILL.md file",
                details="The skill directory does not contain a SKILL.md file.",
            ))
            return  # Can't check frontmatter without SKILL.md

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(skill_md)

        if frontmatter is None:
            result.structure_findings.append(StructureFinding(
                check_name="missing_frontmatter",
                severity="medium",
                description="SKILL.md missing YAML frontmatter",
                details="SKILL.md does not contain valid YAML frontmatter between --- delimiters.",
            ))
        else:
            if "name" not in frontmatter:
                result.structure_findings.append(StructureFinding(
                    check_name="missing_name",
                    severity="medium",
                    description="Frontmatter missing 'name' field",
                    details="SKILL.md frontmatter should include a 'name' field.",
                ))
            if "description" not in frontmatter:
                result.structure_findings.append(StructureFinding(
                    check_name="missing_description",
                    severity="medium",
                    description="Frontmatter missing 'description' field",
                    details="SKILL.md frontmatter should include a 'description' field.",
                ))

        # Check for suspicious binary files
        for root, dirs, filenames in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in self.SUSPICIOUS_BINARY_EXTS:
                    result.structure_findings.append(StructureFinding(
                        check_name="suspicious_file_types",
                        severity="critical",
                        description=f"Suspicious binary file: {fname}",
                        details=f"Binary file '{fname}' with extension '{ext}' found in skill directory.",
                    ))

        # Check for suspicious hidden files
        for root, dirs, filenames in os.walk(skill_dir):
            for fname in filenames:
                if fname.startswith(".") and fname not in self.SAFE_HIDDEN_FILES:
                    result.structure_findings.append(StructureFinding(
                        check_name="hidden_files",
                        severity="medium",
                        description=f"Hidden file: {fname}",
                        details=f"Hidden file '{fname}' is not a commonly recognized config file.",
                    ))

        # Check for excessive files
        total_files = sum(len(files) for _, _, files in os.walk(skill_dir))
        if total_files > 20:
            result.structure_findings.append(StructureFinding(
                check_name="excessive_files",
                severity="low",
                description=f"Excessive file count: {total_files} files",
                details=f"Skill contains {total_files} files, which is unusually many.",
            ))

    def _parse_frontmatter(self, skill_md_path: str) -> Optional[dict]:
        """Parse YAML frontmatter from SKILL.md."""
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, IOError):
            return None

        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            return yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None


def get_frontmatter(skill_dir: str) -> Optional[dict]:
    """Utility: extract frontmatter from a skill's SKILL.md."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, IOError):
        return None
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def get_skill_content(skill_dir: str) -> str:
    """Utility: read full content of SKILL.md."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return ""
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            return f.read()
    except (OSError, IOError):
        return ""
