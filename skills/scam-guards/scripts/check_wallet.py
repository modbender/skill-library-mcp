import re
import sys
import json
from utils.patterns import BLACKLISTED_WALLETS

class WalletChecker:
    def __init__(self, address):
        self.address = address
        self.risks = []
        self.score = 0

    def check(self):
        # 1. Blacklist Check (Priority)
        # Check for direct match or prefix match (for short test IDs)
        is_blacklisted = False
        for blacklisted in BLACKLISTED_WALLETS:
            if self.address.lower() == blacklisted.lower() or (len(blacklisted) > 10 and self.address.lower().startswith(blacklisted.lower())):
                is_blacklisted = True
                break
        
        if is_blacklisted:
            self.risks.append("KNOWN_SCAM_ADDRESS")
            self.score += 100

        chain = self._identify_chain()
        
        # 2. Pattern-based Risky Indicators
        if self.address.startswith("0x000000"):
            self.risks.append("POTENTIAL_VANITY_DRAINER")
            self.score += 30

        threat_level = "DANGER" if self.score >= 70 else "WARNING" if self.score >= 40 else "SAFE"

        return {
            "address": self.address,
            "chain": chain or "Unknown/Custom",
            "threat_level": threat_level,
            "score": self.score,
            "risks": self.risks,
            "recommendation": "DO NOT INTERACT" if threat_level == "DANGER" else "VERIFY SOURCE" if threat_level == "WARNING" else "SAFE"
        }

    def _identify_chain(self):
        if re.match(r'^0x[a-fA-F0-9]{40}$', self.address):
            return "EVM (Ethereum/BSC/Polygon)"
        if re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', self.address):
            return "Solana"
        if re.match(r'^(1|3|bc1)[a-zA-HJ-NP-Za-km-z0-9]{25,62}$', self.address):
            return "Bitcoin"
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No wallet address provided"}, indent=2))
        sys.exit(1)
    
    checker = WalletChecker(sys.argv[1])
    print(json.dumps(checker.check(), indent=2))
