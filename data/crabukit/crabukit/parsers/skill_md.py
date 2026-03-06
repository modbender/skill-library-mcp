"""Enhanced SKILL.md parser with prompt injection and typoglycemia detection."""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import yaml

from crabukit.rules.patterns import (
    Finding, Severity,
    SKILL_MD_PATTERNS,
    TYPOGLYCEMIA_KEYWORDS,
)


@dataclass
class SkillMetadata:
    """Parsed SKILL.md frontmatter and metadata."""
    name: str
    description: str
    raw_frontmatter: Dict[str, Any]
    content: str
    file_path: Path
    has_allowed_tools: bool
    allowed_tools: List[str]
    frontmatter_line_count: int


class SkillMdParser:
    """Parse SKILL.md files with security analysis."""
    
    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path)
        self.skill_md_path = self.skill_path / "SKILL.md"
        
    def parse(self) -> Optional[SkillMetadata]:
        """Parse SKILL.md and return metadata."""
        if not self.skill_md_path.exists():
            return None
            
        try:
            content = self.skill_md_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            return None
        
        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            # No frontmatter - still return basic info
            return SkillMetadata(
                name=self.skill_path.name,
                description="",
                raw_frontmatter={},
                content=content,
                file_path=self.skill_md_path,
                has_allowed_tools=False,
                allowed_tools=[],
                frontmatter_line_count=0,
            )
        
        frontmatter_text = frontmatter_match.group(1)
        body_content = content[frontmatter_match.end():]
        frontmatter_line_count = frontmatter_text.count('\n') + 2  # --- lines
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            frontmatter = {}
        
        # Extract allowed-tools if present
        allowed_tools = frontmatter.get("allowed-tools", [])
        if isinstance(allowed_tools, str):
            allowed_tools = [allowed_tools]
        
        return SkillMetadata(
            name=frontmatter.get("name", self.skill_path.name),
            description=frontmatter.get("description", ""),
            raw_frontmatter=frontmatter,
            content=body_content,
            file_path=self.skill_md_path,
            has_allowed_tools="allowed-tools" in frontmatter,
            allowed_tools=allowed_tools,
            frontmatter_line_count=frontmatter_line_count,
        )
    
    def check_content_patterns(self) -> List[Dict[str, Any]]:
        """Check SKILL.md content for suspicious patterns."""
        if not self.skill_md_path.exists():
            return []
        
        try:
            content = self.skill_md_path.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError):
            return []
        
        findings = []
        
        # Check standard patterns
        for rule_id, rule in SKILL_MD_PATTERNS.items():
            if rule.get("pattern") is None:
                continue
                
            matches = list(re.finditer(rule["pattern"], content, re.IGNORECASE))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                findings.append({
                    "rule_id": rule_id,
                    "title": rule["title"],
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "line": line_num,
                    "snippet": match.group(0)[:100],
                    "cwe_id": rule.get("cwe"),
                })
        
        # Check for excessive length (obfuscation)
        if len(content) > 10000:
            findings.append({
                "rule_id": "SKILL_EXCESSIVE_LENGTH",
                "title": "Very long SKILL.md",
                "description": f"SKILL.md is {len(content)} characters - possible content obfuscation",
                "severity": Severity.LOW,
                "line": 1,
                "snippet": content[:50] + "...",
            })
        
        # Check for encoded content
        findings.extend(self._check_encoded_content(content))
        
        # Check for typoglycemia attacks
        findings.extend(self._check_typoglycemia(content))
        
        # Check for HTML/Markdown injection
        findings.extend(self._check_html_injection(content))
        
        return findings
    
    def _check_encoded_content(self, content: str) -> List[Dict[str, Any]]:
        """Check for encoded/obfuscated content."""
        findings = []
        
        # Base64-like strings (long alphanumeric with +/=)
        base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        matches = list(re.finditer(base64_pattern, content))
        for match in matches[:3]:  # Limit to first 3
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_ENCODED_BASE64",
                "title": "Potential Base64 encoded content",
                "description": "Contains long Base64-like string that may hide malicious instructions",
                "severity": Severity.MEDIUM,
                "line": line_num,
                "snippet": match.group(0)[:50] + "...",
            })
        
        # Hex-encoded strings
        hex_pattern = r'[0-9a-fA-F]{40,}'
        matches = list(re.finditer(hex_pattern, content))
        for match in matches[:3]:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_ENCODED_HEX",
                "title": "Potential hex encoded content",
                "description": "Contains long hex string that may hide malicious instructions",
                "severity": Severity.MEDIUM,
                "line": line_num,
                "snippet": match.group(0)[:50] + "...",
            })
        
        # Unicode escapes
        unicode_pattern = r'\\u[0-9a-fA-F]{4}'
        if len(re.findall(unicode_pattern, content)) > 10:
            line_num = content.find('\\u')
            line_num = content[:line_num].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_UNICODE_ESCAPE",
                "title": "Unicode escape sequences",
                "description": "Contains multiple Unicode escape sequences - possible obfuscation",
                "severity": Severity.LOW,
                "line": line_num,
                "snippet": "Unicode escapes detected",
            })
        
        return findings
    
    def _check_typoglycemia(self, content: str) -> List[Dict[str, Any]]:
        """Check for typoglycemia (scrambled word) attacks."""
        findings = []
        content_lower = content.lower()
        
        for original, variants in TYPOGLYCEMIA_KEYWORDS:
            for variant in variants:
                if variant in content_lower:
                    line_num = content_lower.find(variant)
                    line_num = content[:line_num].count('\n') + 1
                    findings.append({
                        "rule_id": "SKILL_TYPOGLYCEMIA",
                        "title": f"Typoglycemia attack: '{variant}'",
                        "description": f"Scrambled word '{variant}' (intended: '{original}') - may bypass keyword filters",
                        "severity": Severity.MEDIUM,
                        "line": line_num,
                        "snippet": f"{variant}",
                        "references": ["https://arxiv.org/abs/2410.01677"],
                    })
        
        return findings
    
    def _check_html_injection(self, content: str) -> List[Dict[str, Any]]:
        """Check for HTML/Markdown injection attempts."""
        findings = []
        
        # Hidden HTML elements
        hidden_pattern = r'<[^>]+style\s*=\s*["\'][^"\']*(?:display\s*:\s*none|visibility\s*:\s*hidden)[^"\']*["\'][^>]*>'
        matches = list(re.finditer(hidden_pattern, content, re.IGNORECASE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_HIDDEN_HTML",
                "title": "Hidden HTML element",
                "description": "Contains hidden HTML element that may contain malicious instructions",
                "severity": Severity.HIGH,
                "line": line_num,
                "snippet": match.group(0)[:100],
            })
        
        # Image tags with external URLs (potential data exfiltration)
        img_pattern = r'<img[^>]+src\s*=\s*["\']https?://[^"\']+["\']'
        matches = list(re.finditer(img_pattern, content, re.IGNORECASE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_EXTERNAL_IMAGE",
                "title": "External image reference",
                "description": "Contains external image URL - may be used for tracking or data exfiltration",
                "severity": Severity.LOW,
                "line": line_num,
                "snippet": match.group(0)[:100],
            })
        
        # Iframes
        iframe_pattern = r'<iframe[^>]+src\s*=\s*["\'][^"\']+["\']'
        if re.search(iframe_pattern, content, re.IGNORECASE):
            match = re.search(iframe_pattern, content, re.IGNORECASE)
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_IFRAME",
                "title": "Iframe embedded",
                "description": "Contains iframe that loads external content",
                "severity": Severity.HIGH,
                "line": line_num,
                "snippet": match.group(0)[:100],
            })
        
        # JavaScript in markdown
        js_pattern = r'<script[^>]*>[^<]*</script>'
        if re.search(js_pattern, content, re.IGNORECASE):
            match = re.search(js_pattern, content, re.IGNORECASE)
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": "SKILL_JAVASCRIPT",
                "title": "JavaScript in markdown",
                "description": "Contains embedded JavaScript - unusual for skill documentation",
                "severity": Severity.CRITICAL,
                "line": line_num,
                "snippet": match.group(0)[:100],
            })
        
        return findings
    
    def analyze_description_quality(self) -> List[Dict[str, Any]]:
        """Analyze description for quality indicators."""
        findings = []
        metadata = self.parse()
        
        if not metadata:
            return findings
        
        desc = metadata.description
        
        # Check length
        if len(desc) < 30:
            findings.append({
                "rule_id": "META_SHORT_DESC",
                "title": "Very short description",
                "description": f"Description is only {len(desc)} characters - may lack important context",
                "severity": Severity.INFO,
                "line": 1,
            })
        
        if len(desc) > 1000:
            findings.append({
                "rule_id": "META_LONG_DESC",
                "title": "Very long description",
                "description": f"Description is {len(desc)} characters - unusually long, possible obfuscation",
                "severity": Severity.INFO,
                "line": 1,
            })
        
        # Check for trigger phrases quality
        trigger_words = ['when', 'use when', 'for', 'trigger']
        has_trigger = any(word in desc.lower() for word in trigger_words)
        if not has_trigger:
            findings.append({
                "rule_id": "META_NO_TRIGGER",
                "title": "No clear trigger phrases",
                "description": "Description lacks clear 'when to use' guidance",
                "severity": Severity.INFO,
                "line": 1,
            })
        
        return findings
