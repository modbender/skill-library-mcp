import re
import sys
import json
from urllib.parse import urlparse
from utils.patterns import PHISHING_KEYWORDS, MALICIOUS_IPS, TYPOSQUAT_TARGETS

class URLVerifier:
    def __init__(self, target):
        self.target = target
        self.risks = []
        self.score = 0

    def verify(self):
        # Normalize target
        url = self.target if "://" in self.target else "http://" + self.target
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain:
                domain = parsed.path.split('/')[0].lower()
        except:
            return {"error": "Invalid URL format", "threat_level": "UNKNOWN"}

        # 1. Typosquatting / Lookalike Check (Levenshtein based or Substring)
        for target in TYPOSQUAT_TARGETS:
            if target in domain and domain != target:
                # If target is a substring but not the whole domain (e.g. clawhub.ai.xyz)
                self.risks.append(f"TYPOSQUAT_TARGET_{target.upper()}")
                self.score += 50

        # 2. Suspicious TLD Check
        suspicious_tlds = ['.xyz', '.top', '.zip', '.click', '.monster', '.free']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            self.risks.append("SUSPICIOUS_TLD")
            self.score += 30

        # 3. Phishing Keyword in Domain
        for kw in PHISHING_KEYWORDS:
            if kw in domain:
                self.risks.append(f"PHISHING_KEYWORD_{kw.upper()}")
                self.score += 40

        # 4. Excessive Subdomains
        if domain.count('.') > 3:
            self.risks.append("EXCESSIVE_SUBDOMAINS")
            self.score += 20

        # 5. Malicious IP match
        if any(ip in domain for ip in MALICIOUS_IPS):
            self.risks.append("KNOWN_MALICIOUS_IP")
            self.score += 100

        threat_level = "DANGER" if self.score >= 70 else "WARNING" if self.score >= 40 else "SAFE"

        return {
            "target": self.target,
            "domain": domain,
            "threat_level": threat_level,
            "score": self.score,
            "risks": self.risks,
            "recommendation": "BLOCK ACCESS" if threat_level == "DANGER" else "PROCEED WITH CAUTION" if threat_level == "WARNING" else "SAFE"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided"}, indent=2))
        sys.exit(1)
    
    verifier = URLVerifier(sys.argv[1])
    print(json.dumps(verifier.verify(), indent=2))
