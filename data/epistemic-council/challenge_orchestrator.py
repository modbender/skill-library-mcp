"""
epistemic_council/challenge_orchestrator.py

Orchestrates adversarial challenges on insights.
Runs all three adversarial agents and determines validation status.
"""

from typing import Dict, List, Any, Tuple
from adversarial import (
    BoundaryViolationAgent,
    NullHypothesisAgent,
    FalseAnalogyBreakerAgent,
    ChallengeResult
)
from substrate import Substrate


class ChallengeOrchestrator:
    """Runs insights through adversarial validation"""
    
    def __init__(self, substrate: Substrate, model_url: str = "http://localhost:11434"):
        self.substrate = substrate
        self.agents = {
            'boundary': BoundaryViolationAgent(substrate),
            'null_hypothesis': NullHypothesisAgent(substrate, model_url),
            'false_analogy': FalseAnalogyBreakerAgent(model_url)
        }
    
    def run_challenges(self, insight_event, query_text: str) -> Dict[str, Any]:
        """
        Run all challenges on an insight.
        
        Returns:
            {
                'passes': int,
                'results': dict,
                'final_confidence': float,
                'status': str  # 'validated', 'mostly_validated', 'challenged', 'rejected'
            }
        """
        results = {}
        passes = 0
        confidence_adjustments = []
        
        # Convert event to dict for agents
        insight_dict = {
            'content': insight_event.content,
            'confidence': insight_event.confidence
        }
        
        print(f"\n🔬 Challenging insight (conf={insight_event.confidence:.2f}):")
        print(f"   {insight_event.content.get('text', '')[:80]}...")
        
        # Challenge 1: Boundary Violation Check
        print(f"\n  [1/3] Boundary Violation Check...")
        try:
            boundary_result = self.agents['boundary'].challenge(insight_dict)
            results['boundary'] = boundary_result
            if boundary_result.passed:
                passes += 1
                print(f"    ✓ PASS")
            else:
                print(f"    ✗ FAIL: {boundary_result.reasoning}")
            confidence_adjustments.append(boundary_result.confidence_adjustment)
            
            # Write challenge result to substrate
            self.substrate.write_challenge_result(
                insight_id=insight_event.event_id,
                agent_id='boundary_agent',
                verdict={'type': 'boundary_violation', 'passed': boundary_result.passed, 'reasoning': boundary_result.reasoning},
                confidence_adjustment=boundary_result.confidence_adjustment
            )
        except Exception as e:
            print(f"    ⚠️  ERROR: {e}")
            boundary_result = ChallengeResult(True, 1.0, f"Error: {e}", {})
            results['boundary'] = boundary_result
            confidence_adjustments.append(1.0)
        
        # Challenge 2: Null Hypothesis Test
        print(f"\n  [2/3] Null Hypothesis Test...")
        try:
            null_result = self.agents['null_hypothesis'].challenge(insight_dict, query_text)
            results['null_hypothesis'] = null_result
            if null_result.passed:
                passes += 1
                print(f"    ✓ PASS: {null_result.reasoning}")
            else:
                print(f"    ✗ FAIL: {null_result.reasoning}")
            confidence_adjustments.append(null_result.confidence_adjustment)
            
            # Write challenge result to substrate
            self.substrate.write_challenge_result(
                insight_id=insight_event.event_id,
                agent_id='null_hypothesis_agent',
                verdict={'type': 'null_hypothesis', 'passed': null_result.passed, 'reasoning': null_result.reasoning},
                confidence_adjustment=null_result.confidence_adjustment
            )
        except Exception as e:
            print(f"    ⚠️  ERROR: {e}")
            null_result = ChallengeResult(True, 1.0, f"Error: {e}", {})
            results['null_hypothesis'] = null_result
            confidence_adjustments.append(1.0)
        
        # Challenge 3: False Analogy Test
        print(f"\n  [3/3] False Analogy Test...")
        try:
            # Get source claims for this challenge
            source_claim_ids = insight_event.content.get('source_claim_ids', [])
            source_claims = []
            for claim_id in source_claim_ids:
                event = self.substrate.get_event(claim_id)
                if event:
                    source_claims.append({
                        'domain': event.domain,
                        'content': event.content
                    })
            
            analogy_result = self.agents['false_analogy'].challenge(insight_dict, source_claims)
            results['false_analogy'] = analogy_result
            if analogy_result.passed:
                passes += 1
                print(f"    ✓ PASS: {analogy_result.reasoning}")
            else:
                print(f"    ✗ FAIL: {analogy_result.reasoning}")
            confidence_adjustments.append(analogy_result.confidence_adjustment)
            
            # Write challenge result to substrate
            self.substrate.write_challenge_result(
                insight_id=insight_event.event_id,
                agent_id='false_analogy_agent',
                verdict={'type': 'false_analogy', 'passed': analogy_result.passed, 'reasoning': analogy_result.reasoning},
                confidence_adjustment=analogy_result.confidence_adjustment
            )
        except Exception as e:
            print(f"    ⚠️  ERROR: {e}")
            analogy_result = ChallengeResult(True, 1.0, f"Error: {e}", {})
            results['false_analogy'] = analogy_result
            confidence_adjustments.append(1.0)
        
        # Calculate final confidence
        original_conf = insight_event.confidence
        adjustment_factor = sum(confidence_adjustments) / len(confidence_adjustments)
        final_confidence = original_conf * adjustment_factor
        
        # Determine status
        if passes == 3:
            status = 'validated'
        elif passes == 2:
            status = 'mostly_validated'
        elif passes == 1:
            status = 'challenged'
        else:
            status = 'rejected'
        
        print(f"\n  Result: {passes}/3 passed, status={status}")
        print(f"  Confidence: {original_conf:.2f} → {final_confidence:.2f}")
        
        # Write overall result to substrate
        self.substrate.write_challenge_result(
            insight_id=insight_event.event_id,
            agent_id='challenge_orchestrator',
            verdict={'passes': passes, 'total': 3, 'status': status},
            confidence_adjustment=final_confidence - original_conf
        )
        
        return {
            'passes': passes,
            'results': results,
            'final_confidence': final_confidence,
            'status': status,
            'original_confidence': original_conf
        }
    
    def validate_batch(self, insight_events: List, query_text: str) -> Tuple[List, List, List]:
        """
        Validate a batch of insights.
        
        Returns:
            (validated, challenged, rejected) - three lists of (insight, result) tuples
        """
        validated = []
        challenged = []
        rejected = []
        
        for insight in insight_events:
            result = self.run_challenges(insight, query_text)
            
            if result['status'] == 'validated':
                validated.append((insight, result))
            elif result['status'] in ['challenged', 'mostly_validated']:
                challenged.append((insight, result))
            else:
                rejected.append((insight, result))
        
        return validated, challenged, rejected
