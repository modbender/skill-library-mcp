import os
import re
import json
import sys
import datetime
from utils.patterns import PATTERNS, MALICIOUS_IPS, TYPOSQUAT_TARGETS

class SkillScanner:
    """
    ClawHub Skill Security Scanner
    [PATENT_CLAIM_3: Rhetorical Labeling]
    """
    def __init__(self, target_path):
        self.target_path = target_path
        self.findings = []
        self.score = 0
        self.version = "1.0.0"

    def scan(self):
        if not os.path.exists(self.target_path):
            return self._error_report(f"Path not found: {self.target_path}")

        files_to_scan = []
        if os.path.isfile(self.target_path):
            files_to_scan.append(self.target_path)
        else:
            for root, _, files in os.walk(self.target_path):
                for file in files:
                    if file.endswith(('.md', '.py', '.sh', '.js', '.json')):
                        files_to_scan.append(os.path.join(root, file))

        for file_path in files_to_scan:
            self._scan_file(file_path)

        self._check_typosquatting()
        
        threat_level = self._calculate_threat_level()
        
        now = datetime.datetime.now(datetime.timezone.utc)
        return {
            "skill_name": os.path.basename(self.target_path),
            "scan_timestamp": now.isoformat().split('.')[0] + "Z",
            "threat_level": threat_level,
            "score": self.score,
            "findings": self.findings,
            "recommendation": "DO NOT INSTALL" if threat_level == "DANGER" else "INSTALL WITH CAUTION" if threat_level == "WARNING" else "SAFE TO INSTALL",
            "scam_guards_version": self.version,
            "verified_badge": threat_level == "SAFE" and self.score == 0
        }

    def _scan_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for Malicious Patterns (악성 패턴 탐지)
                for rule, pattern in PATTERNS.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        self.findings.append({
                            "rule": rule,
                            "severity": "CRITICAL" if rule in ["BASE64_EXEC", "REVERSE_SHELL", "CREDENTIAL_ACCESS"] else "HIGH",
                            "location": f"{os.path.basename(file_path)}:L{content.count('\\n', 0, match.start()) + 1}",
                            "evidence": match.group(0)
                        })
                        self.score += 25

                # Check for Malicious IPs (악성 IP 탐지)
                for ip in MALICIOUS_IPS:
                    if ip in content:
                        self.findings.append({
                            "rule": "MALICIOUS_IP",
                            "severity": "CRITICAL",
                            "location": os.path.basename(file_path),
                            "evidence": ip
                        })
                        self.score += 50

        except Exception as e:
            self.findings.append({"rule": "SCAN_ERROR", "severity": "LOW", "evidence": str(e)})

    def _check_typosquatting(self):
        name = os.path.basename(self.target_path).lower()
        for target in TYPOSQUAT_TARGETS:
            if name != target and self._levenshtein(name, target) <= 2:
                self.findings.append({
                    "rule": "TYPOSQUAT_NAME",
                    "severity": "HIGH",
                    "evidence": f"Skill name '{name}' is very similar to legitimate skill '{target}'"
                })
                self.score += 30

    def _calculate_threat_level(self):
        if any(f["severity"] == "CRITICAL" for f in self.findings) or self.score >= 70:
            return "DANGER"
        if self.score > 20:
            return "WARNING"
        return "SAFE"

    def _levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def _error_report(self, message):
        return {"error": message, "threat_level": "UNKNOWN"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No target path provided"}, indent=2))
        sys.exit(1)
        
    scanner = SkillScanner(sys.argv[1])
    print(json.dumps(scanner.scan(), indent=2))
