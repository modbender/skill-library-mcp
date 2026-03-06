"""
CounterClaw - Defensive Security Scanner
Open-source defensive interceptor for AI agents
"""

import re
from typing import Dict, Any


class Scanner:
    """Defensive scanner - snaps shut on malicious payloads"""
    
    # Malicious patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore previous instructions",
        r"(?i)disregard system",
        r"(?i)forget all rules",
        r"(?i)you are now",
        r"(?i)pretend to be",
        r"(?i)bypass",
    ]
    
    # PII patterns
    PII_PATTERNS = {
        "email": r"[\w.-]+@[\w.-]+\.\w+",
        "phone": r"0?7[\d\s]{9,}",
        "card": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    }
    
    def __init__(self):
        self._compile()
    
    def _compile(self):
        self._injection = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self._pii = {k: re.compile(v) for k, v in self.PII_PATTERNS.items()}
    
    def scan_input(self, text: str) -> Dict[str, Any]:
        """Scan input - snap shut on injections"""
        matches = []
        for pattern in self._injection:
            if pattern.search(text):
                matches.append(pattern.pattern)
        
        return {
            "safe": len(matches) == 0,
            "blocked": len(matches) > 0,
            "violations": matches,
        }
    
    def scan_output(self, text: str) -> Dict[str, Any]:
        """Scan output - detect PII leaks"""
        detected = {}
        for pii_type, pattern in self._pii.items():
            if pattern.search(text):
                detected[pii_type] = True
        
        return {
            "safe": len(detected) == 0,
            "pii_detected": detected,
        }
