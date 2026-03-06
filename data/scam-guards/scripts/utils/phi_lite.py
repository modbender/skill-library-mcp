import re

class PHILite:
    """
    Lightweight PHI (Psychological Hazards Inventory) Scorer.
    Focuses on 3 key dimensions: Authority_Pressure, Urgency_Manufacturing, and Isolation_Tactic.
    """
    
    DIMENSIONS = {
        "Authority_Pressure": [
            r"official\s+support", r"admin(?:istrator)?", r"required\s+by\s+policy",
            r"compliance\s+officer", r"legal\s+department", r"must\s+comply"
        ],
        "Urgency_Manufacturing": [
            r"immediately", r"within\s+\d+\s+minutes", r"account\s+will\s+be\s+suspended",
            r"act\s+now", r"final\s+notice", r"last\s+chance", r"hurry"
        ],
        "Isolation_Tactic": [
            r"do\s+not\s+tell\s+anyone", r"keep\s+this\s+confidential",
            r"private\s+matter", r"don't\s+share\s+this", r"secret"
        ]
    }

    def analyze(self, text):
        results = {}
        total_score = 0
        
        for dimension, patterns in self.DIMENSIONS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            # Normalize to 0.0 - 1.0 range (0.0~1.0 점수 정규화)
            # 1 match = 0.5, 2+ matches = 1.0 (simplified for PHI Lite)
            score = min(len(matches) * 0.5, 1.0)
            results[dimension] = {
                "score": score,
                "matches": list(set(matches))
            }
            total_score += score
            
        overall_score = total_score / len(self.DIMENSIONS)
        
        return {
            "overall_score": round(overall_score, 2),
            "dimensions": results,
            "threat_label": self._get_label(overall_score)
        }

    def _get_label(self, score):
        if score > 0.7: return "CRITICAL"
        if score > 0.4: return "WARNING"
        return "SAFE"

if __name__ == "__main__":
    phi = PHILite()
    test_text = "Immediately contact official support. Keep this confidential or your account will be suspended."
    import json
    print(json.dumps(phi.analyze(test_text), indent=2))
