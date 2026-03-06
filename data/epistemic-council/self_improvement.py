"""
Self-Improvement Layer for Epistemic Council
Agent learns from adversarial validation feedback
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


class LearningSystem:
    """
    Tracks what works and what fails, adjusts agent behavior
    """
    
    def __init__(self, learning_file='agent_learning.json'):
        self.learning_file = learning_file
        self.data = self.load()
        
    def load(self) -> Dict:
        """Load learning data"""
        try:
            with open(self.learning_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._init_learning()
            
    def _init_learning(self) -> Dict:
        """Initialize learning structure"""
        return {
            'version': '1.0',
            'started': datetime.now().isoformat(),
            'claim_patterns': {
                'successful': [],  # Claims that led to validated insights
                'failed': []       # Claims that led to rejected insights
            },
            'insight_patterns': {
                'validated': [],   # Patterns in validated insights
                'rejected': []     # Patterns in rejected insights
            },
            'adversarial_feedback': {
                'boundary_violations': [],
                'null_hypothesis_fails': [],
                'false_analogies': []
            },
            'confidence_calibration': {
                'overconfident': [],  # High conf but rejected
                'underconfident': []  # Low conf but validated
            },
            'domain_performance': {
                'computer_science': {'success_rate': 0, 'total': 0},
                'biology': {'success_rate': 0, 'total': 0}
            },
            'improvement_metrics': {
                'validation_rate_over_time': [],
                'confidence_accuracy_over_time': []
            }
        }
        
    def save(self):
        """Save learning data"""
        with open(self.learning_file, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def record_result(self, insight: Dict, validation: Dict, claims: List[Dict]):
        """
        Learn from validation result
        
        Args:
            insight: The insight that was validated
            validation: Validation results (passes, status, details)
            claims: Source claims that generated this insight
        """
        status = validation['status']
        
        # Track claim patterns
        for claim in claims:
            pattern = self._extract_claim_pattern(claim)
            
            if status == 'validated':
                self.data['claim_patterns']['successful'].append(pattern)
            elif status == 'rejected':
                self.data['claim_patterns']['failed'].append(pattern)
                
        # Track insight patterns
        insight_pattern = self._extract_insight_pattern(insight)
        
        if status == 'validated':
            self.data['insight_patterns']['validated'].append(insight_pattern)
        else:
            self.data['insight_patterns']['rejected'].append(insight_pattern)
            
        # Learn from adversarial feedback
        self._learn_from_challenges(validation['results'])
        
        # Track confidence calibration
        self._track_confidence(insight, validation)
        
        # Update domain performance
        self._update_domain_stats(claims, status)
        
        self.save()
        
    def _extract_claim_pattern(self, claim: Dict) -> Dict:
        """Extract learnable pattern from claim"""
        return {
            'domain': claim.get('domain'),
            'confidence': claim.get('confidence'),
            'length': len(claim.get('text', '')),
            'has_specifics': any(word in claim.get('text', '').lower() 
                                for word in ['algorithm', 'mechanism', 'process', 'strategy']),
            'timestamp': datetime.now().isoformat()
        }
        
    def _extract_insight_pattern(self, insight: Dict) -> Dict:
        """Extract learnable pattern from insight"""
        return {
            'type': insight.get('insight_type'),
            'confidence': insight.get('confidence'),
            'source_count': len(insight.get('source_claim_ids', [])),
            'length': len(insight.get('text', '')),
            'has_both_domains': 'computer' in insight.get('text', '').lower() and 'biolog' in insight.get('text', '').lower(),
            'timestamp': datetime.now().isoformat()
        }
        
    def _learn_from_challenges(self, challenge_results: Dict):
        """Learn from adversarial validation"""
        # Guard: challenge_results may be empty (e.g. from rechallenge path)
        if not challenge_results:
            return

        boundary = challenge_results.get('boundary')
        if boundary and hasattr(boundary, 'passed') and not boundary.passed:
            for violation in boundary.details.get('violations', []):
                self.data['adversarial_feedback']['boundary_violations'].append({
                    'term': violation.get('found_terms', []),
                    'domain': violation.get('domain'),
                    'timestamp': datetime.now().isoformat()
                })

        null_hyp = challenge_results.get('null_hypothesis')
        if null_hyp and hasattr(null_hyp, 'passed') and not null_hyp.passed:
            self.data['adversarial_feedback']['null_hypothesis_fails'].append({
                'reason': null_hyp.reasoning,
                'timestamp': datetime.now().isoformat()
            })

        false_analogy = challenge_results.get('false_analogy')
        if false_analogy and hasattr(false_analogy, 'passed') and not false_analogy.passed:
            self.data['adversarial_feedback']['false_analogies'].append({
                'counter_example': false_analogy.details.get('counter_example', ''),
                'timestamp': datetime.now().isoformat()
            })
            
    def _track_confidence(self, insight: Dict, validation: Dict):
        """Track confidence calibration"""
        original = insight['confidence']
        final = validation['final_confidence']
        status = validation['status']
        
        # Overconfident: high initial conf but rejected
        if original > 0.7 and status == 'rejected':
            self.data['confidence_calibration']['overconfident'].append({
                'original': original,
                'final': final,
                'timestamp': datetime.now().isoformat()
            })
            
        # Underconfident: low initial conf but validated
        if original < 0.5 and status == 'validated':
            self.data['confidence_calibration']['underconfident'].append({
                'original': original,
                'final': final,
                'timestamp': datetime.now().isoformat()
            })
            
    def _update_domain_stats(self, claims: List[Dict], status: str):
        """Update per-domain success rates"""
        for claim in claims:
            domain = claim.get('domain')
            if domain in self.data['domain_performance']:
                self.data['domain_performance'][domain]['total'] += 1
                if status == 'validated':
                    self.data['domain_performance'][domain]['success_rate'] = \
                        (self.data['domain_performance'][domain]['success_rate'] * 
                         (self.data['domain_performance'][domain]['total'] - 1) + 1) / \
                        self.data['domain_performance'][domain]['total']
                        
    def get_prompt_improvements(self, domain: str) -> str:
        """
        Generate improved prompts based on learning
        
        Returns additional guidance to add to agent prompts
        """
        improvements = []
        
        # Boundary violation learning
        violations = self.data['adversarial_feedback']['boundary_violations']
        recent_violations = [v for v in violations[-10:] if v['domain'] == domain]
        
        if recent_violations:
            forbidden_terms = set()
            for v in recent_violations:
                forbidden_terms.update(v['term'])
                
            improvements.append(f"""
LEARNED BOUNDARY VIOLATIONS (avoid these terms):
{', '.join(forbidden_terms)}
""")
        
        # Successful patterns
        successful = self.data['claim_patterns']['successful']
        if len(successful) > 5:
            avg_conf = sum(s['confidence'] for s in successful[-10:]) / min(len(successful), 10)
            avg_length = sum(s['length'] for s in successful[-10:]) / min(len(successful), 10)
            
            improvements.append(f"""
SUCCESSFUL PATTERNS (emulate these):
- Target confidence: {avg_conf:.2f}
- Target length: ~{int(avg_length)} characters
- Include specific mechanisms/processes
""")
        
        # Failed patterns to avoid
        failed = self.data['claim_patterns']['failed']
        if len(failed) > 3:
            improvements.append("""
AVOID THESE PATTERNS:
- Vague or overly general statements
- Circular reasoning (CS concepts derived from bio)
- Claims without mechanistic detail
""")
        
        return '\n'.join(improvements)
        
    def get_confidence_adjustment(self, base_confidence: float, domain: str) -> float:
        """
        Adjust confidence based on calibration learning
        
        Returns: Adjusted confidence score
        """
        # Check if this domain tends to be overconfident
        overconfident_count = len([c for c in self.data['confidence_calibration']['overconfident'] 
                                   if c['original'] > base_confidence])
        underconfident_count = len([c for c in self.data['confidence_calibration']['underconfident']
                                     if c['original'] < base_confidence])
        
        # Adjust based on historical calibration
        if overconfident_count > underconfident_count:
            # This confidence range tends to be too high
            return base_confidence * 0.9
        elif underconfident_count > overconfident_count:
            # This confidence range tends to be too low
            return base_confidence * 1.1
        else:
            return base_confidence
            
    def get_learning_summary(self) -> str:
        """Human-readable learning summary"""
        total_validated = len(self.data['insight_patterns']['validated'])
        total_rejected = len(self.data['insight_patterns']['rejected'])
        total = total_validated + total_rejected
        
        validation_rate = total_validated / total if total > 0 else 0
        
        cs_stats = self.data['domain_performance']['computer_science']
        bio_stats = self.data['domain_performance']['biology']
        
        return f"""
📈 LEARNING SUMMARY

Performance:
  Validation Rate: {validation_rate*100:.1f}%
  Total Insights: {total}
  
Domain Performance:
  Computer Science: {cs_stats['success_rate']*100:.1f}% ({cs_stats['total']} claims)
  Biology: {bio_stats['success_rate']*100:.1f}% ({bio_stats['total']} claims)
  
Adversarial Feedback:
  Boundary Violations: {len(self.data['adversarial_feedback']['boundary_violations'])}
  Null Hypothesis Failures: {len(self.data['adversarial_feedback']['null_hypothesis_fails'])}
  False Analogies: {len(self.data['adversarial_feedback']['false_analogies'])}
  
Confidence Calibration:
  Overconfident: {len(self.data['confidence_calibration']['overconfident'])}
  Underconfident: {len(self.data['confidence_calibration']['underconfident'])}
"""


class ImprovedAgent:
    """
    Wrapper around DomainAgent that applies learning
    """
    
    def __init__(self, domain: str, substrate, model_client, learning_system: LearningSystem):
        from agent import DomainAgent
        
        self.domain = domain
        self.substrate = substrate
        self.model_client = model_client
        self.learning = learning_system
        
        # Create base agent
        self.agent = DomainAgent(domain, substrate, model_client)
        
    def reason(self, query: str):
        """
        Reason with learned improvements
        """
        # Get learned prompt improvements
        improvements = self.learning.get_prompt_improvements(self.domain)
        
        # Modify query with learning
        enhanced_query = f"{query}\n\n{improvements}" if improvements else query
        
        # Run base agent
        self.agent.reason(enhanced_query)
        
        # Adjust confidences based on calibration learning
        self._adjust_confidences()
        
    def _adjust_confidences(self):
        """Apply learned confidence calibration to recent claims"""
        recent_claims = self.substrate.get_claims_by_domain(self.domain)[-10:]
        
        for claim in recent_claims:
            original_conf = claim.get('confidence', 0.5)
            adjusted_conf = self.learning.get_confidence_adjustment(original_conf, self.domain)
            
            # Note: In production, you'd update the claim in substrate
            # For now, just track the adjustment
            pass


if __name__ == '__main__':
    # Test the learning system
    learning = LearningSystem()
    print(learning.get_learning_summary())
