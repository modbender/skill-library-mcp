"""
epistemic_council/adversarial.py

Adversarial validation agents that challenge insights to test robustness.

Three adversarial agent types:
1. Boundary Violation Agent - Checks if source claims respect domain boundaries
2. Null Hypothesis Agent - Tests if insight is emergent or already known
3. False Analogy Breaker - Generates counter-examples to test structural validity
"""

import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ChallengeResult:
    """Result of an adversarial challenge"""
    passed: bool
    confidence_adjustment: float
    reasoning: str
    details: Dict[str, Any]


class BoundaryViolationAgent:
    """Checks if source claims respect domain boundaries"""
    
    DOMAIN_BOUNDARIES = {
        'computer_science': {
            'forbidden_terms': [
                'evolve', 'evolution', 'evolutionary', 'natural selection',
                'organism', 'species', 'mutation', 'gene', 'biological',
                'ecology', 'predator', 'prey', 'fitness', 'offspring',
                'reproduce', 'reproduction', 'adapt', 'adaptation'
            ]
        },
        'biology': {
            'forbidden_terms': [
                'algorithm', 'algorithmic', 'complexity', 'computational',
                'O(n)', 'runtime', 'hash table', 'data structure',
                'memory allocation', 'compilation', 'syntax', 'debug',
                'code', 'program', 'software', 'hardware'
            ]
        }
    }
    
    def __init__(self, substrate):
        self.substrate = substrate
    
    def challenge(self, insight: Dict[str, Any]) -> ChallengeResult:
        """Check if source claims violate domain boundaries"""
        violations = []
        source_claim_ids = insight.get('content', {}).get('source_claim_ids', [])
        
        if not source_claim_ids:
            return ChallengeResult(
                passed=False, confidence_adjustment=0.0,
                reasoning="No source claims - cannot verify boundaries",
                details={'violations': []}
            )
        
        for claim_id in source_claim_ids:
            claim_event = self.substrate.get_event(claim_id)
            if not claim_event or claim_event.domain not in self.DOMAIN_BOUNDARIES:
                continue
            
            text = claim_event.content.get('text', '').lower()
            forbidden = self.DOMAIN_BOUNDARIES[claim_event.domain]['forbidden_terms']
            found_terms = [term for term in forbidden if term in text]
            
            if found_terms:
                violations.append({
                    'claim_id': claim_id,
                    'domain': claim_event.domain,
                    'text': claim_event.content.get('text', '')[:100],
                    'found_terms': found_terms[:3]
                })
        
        if len(violations) == 0:
            return ChallengeResult(
                passed=True, confidence_adjustment=1.0,
                reasoning="All source claims respect domain boundaries",
                details={'violations': []}
            )
        else:
            penalty = min(0.4 * len(violations), 0.8)
            return ChallengeResult(
                passed=False, confidence_adjustment=max(0.2, 1.0 - penalty),
                reasoning=f"Found {len(violations)} boundary violation(s)",
                details={'violations': violations}
            )


class NullHypothesisAgent:
    """Tests if insight adds value over single-domain reasoning"""
    
    def __init__(self, substrate, model_url: str = "http://localhost:11434"):
        self.substrate = substrate
        self.model_url = model_url
        self.model_name = "qwen2.5:14b"
    
    def challenge(self, insight: Dict[str, Any], query_text: str) -> ChallengeResult:
        """Ask each domain if they already know this insight"""
        insight_text = insight.get('content', {}).get('text', '')
        
        cs_knows = self._ask_domain('computer_science', insight_text, query_text)
        bio_knows = self._ask_domain('biology', insight_text, query_text)
        
        if cs_knows and bio_knows:
            return ChallengeResult(
                passed=False, confidence_adjustment=0.3,
                reasoning="Both domains already recognize this independently",
                details={'cs_knows': cs_knows, 'bio_knows': bio_knows, 'emergent': False}
            )
        elif cs_knows or bio_knows:
            return ChallengeResult(
                passed=True, confidence_adjustment=0.6,
                reasoning="Primarily known in one domain, but cross-domain adds value",
                details={'cs_knows': cs_knows, 'bio_knows': bio_knows, 'emergent': 'partial'}
            )
        else:
            return ChallengeResult(
                passed=True, confidence_adjustment=1.0,
                reasoning="Insight is emergent - not obvious from either domain alone",
                details={'cs_knows': False, 'bio_knows': False, 'emergent': True}
            )
    
    def _ask_domain(self, domain: str, insight_text: str, query_text: str) -> bool:
        """Ask if domain already knows this insight"""
        prompt = f"""You are a {domain} expert answering: "{query_text}"

Someone claims: "{insight_text}"

Within {domain} alone, is this obvious/well-known?

Answer YES only if: textbook knowledge, any expert would recognize it, requires NO cross-domain knowledge.
Answer NO if: requires cross-domain knowledge, novel connection, synthesizes multiple fields.

Your answer (YES or NO only):"""

        try:
            response = requests.post(
                f"{self.model_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.3, "num_predict": 50}},
                timeout=30
            )
            if response.status_code == 200:
                text = response.json().get('response', '').lower()
                return 'yes' in text and 'no' not in text
            return False
        except Exception as e:
            print(f"Warning: Model query failed: {e}")
            return False


class FalseAnalogyBreakerAgent:
    """Tests if analogy is structural via counter-examples"""
    
    def __init__(self, model_url: str = "http://localhost:11434"):
        self.model_url = model_url
        self.model_name = "qwen2.5:14b"
    
    def challenge(self, insight: Dict[str, Any], source_claims: List[Dict[str, Any]]) -> ChallengeResult:
        """Generate and test counter-example"""
        insight_text = insight.get('content', {}).get('text', '')
        claims_text = "\n".join([
            f"- [{c.get('domain', 'unknown')}] {c.get('content', {}).get('text', '')}"
            for c in source_claims
        ])
        
        counter_example = self._generate_counter_example(insight_text, claims_text)
        if not counter_example:
            return ChallengeResult(
                passed=True, confidence_adjustment=0.9,
                reasoning="No meaningful counter-example generated - analogy may be robust",
                details={'counter_example': None, 'judgment': None}
            )
        
        judgment = self._evaluate_counter_example(insight_text, counter_example)
        
        if 'survives' in judgment.lower() or 'holds' in judgment.lower():
            return ChallengeResult(
                passed=True, confidence_adjustment=1.0,
                reasoning="Analogy survived counter-example",
                details={'counter_example': counter_example, 'judgment': judgment, 'result': 'survived'}
            )
        elif 'breaks' in judgment.lower() or 'invalid' in judgment.lower():
            return ChallengeResult(
                passed=False, confidence_adjustment=0.5,
                reasoning="Counter-example revealed weakness",
                details={'counter_example': counter_example, 'judgment': judgment, 'result': 'broken'}
            )
        else:
            return ChallengeResult(
                passed=True, confidence_adjustment=0.8,
                reasoning="Counter-example test inconclusive",
                details={'counter_example': counter_example, 'judgment': judgment, 'result': 'inconclusive'}
            )
    
    def _generate_counter_example(self, insight_text: str, claims_text: str) -> Optional[str]:
        """Generate counter-example"""
        prompt = f"""Test this analogy:

ANALOGY: {insight_text}

EVIDENCE:
{claims_text}

Generate ONE counter-example that tests if analogy is structural or superficial.

Format:
COUNTER-EXAMPLE: [scenario in one domain]
PREDICTION: [what should happen in other domain if analogy holds]

Generate:"""

        try:
            response = requests.post(
                f"{self.model_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.7, "num_predict": 200}},
                timeout=45
            )
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return None
        except Exception as e:
            print(f"Warning: Counter-example generation failed: {e}")
            return None
    
    def _evaluate_counter_example(self, insight_text: str, counter_example: str) -> str:
        """Evaluate if counter-example breaks analogy"""
        prompt = f"""Evaluate counter-example:

ANALOGY: {insight_text}

COUNTER-EXAMPLE: {counter_example}

Does this show:
A) Analogy SURVIVES (structural similarity holds)
B) Analogy BREAKS (superficial, fails under scrutiny)  
C) INCONCLUSIVE

Your judgment (A, B, or C with brief explanation):"""

        try:
            response = requests.post(
                f"{self.model_url}/api/generate",
                json={"model": self.model_name, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.3, "num_predict": 150}},
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return "Inconclusive"
        except Exception as e:
            print(f"Warning: Evaluation failed: {e}")
            return "Inconclusive"
