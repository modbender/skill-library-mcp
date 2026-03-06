#!/usr/bin/env python3
"""
Intelligent Router CLI
A tool for classifying tasks and recommending appropriate LLM models.
Python 3.8+ compatible, no external dependencies.

Features:
- 15-dimension weighted scoring system
- REASONING tier for formal logic and proofs
- Automatic fallback chains (up to 3 attempts)
- Agentic task detection
- Confidence-based routing
"""

import json
import math
import os
import re
import sys
from pathlib import Path


class IntelligentRouter:
    """Main router class for task classification and model recommendation."""

    # Weighted scoring dimensions (15 total, sum = 1.0)
    SCORING_WEIGHTS = {
        'reasoning_markers': 0.18,
        'code_presence': 0.15,
        'multi_step_patterns': 0.12,
        'agentic_task': 0.10,
        'technical_terms': 0.10,
        'token_count': 0.08,
        'creative_markers': 0.05,
        'question_complexity': 0.05,
        'constraint_count': 0.04,
        'imperative_verbs': 0.03,
        'output_format': 0.03,
        'simple_indicators': 0.02,
        'domain_specificity': 0.02,
        'reference_complexity': 0.02,
        'negation_complexity': 0.01
    }

    # Keywords and patterns for each dimension
    REASONING_KEYWORDS = [
        'prove', 'theorem', 'proof', 'derive', 'derivation', 'formal',
        'verify', 'verification', 'logic', 'logical', 'induction', 'deduction',
        'lemma', 'corollary', 'axiom', 'postulate', 'qed', 'step by step',
        'show that', 'demonstrate that', 'mathematically', 'rigorously'
    ]

    CODE_KEYWORDS = ['lint', 'refactor', 'bug fix', 'code review', 'software', 'application', 'component', 'module', 'package', 'library']
    
    CODE_PATTERNS = [
        r'`[^`]+`',  # inline code
        r'```[\s\S]*?```',  # code blocks
        r'\bdef\b', r'\bclass\b', r'\bimport\b', r'\bfrom\b',
        r'\breturn\b', r'\bif\b.*:\s*$', r'\.py\b', r'\.js\b', r'\.java\b',
        r'\.cpp\b', r'\.rs\b', r'\.go\b', r'\bAPI\b', r'\bJSON\b', r'\bSQL\b',
        r'\b(python|javascript|java|rust|golang|c\+\+|typescript|ruby|php)\s+\w+',
        r'\bwrite\s+.*?(function|code|script|class|method|program)',
        r'\bcode\s+(for|to|that)',
        r'\bprogram(ming)?\b',
        r'\b(coding|development|implementation)\b'
    ]

    AGENTIC_KEYWORDS = [
        'run', 'test', 'fix', 'deploy', 'edit', 'build', 'create', 'implement',
        'execute', 'refactor', 'migrate', 'integrate', 'setup', 'configure',
        'install', 'compile', 'debug', 'troubleshoot'
    ]

    MULTI_STEP_PATTERNS = [
        r'\bfirst\b.*\bthen\b', r'\bstep\s+\d+', r'\d+\.\s+\w+',  # numbered lists
        r'\bnext\b', r'\bafter\s+that\b', r'\bfinally\b', r'\bsubsequently\b',
        r'\band then\b', r'\bfollowed by\b', r',\s*then\b', r'\bthen\s+\w+\s+it\b'
    ]

    SIMPLE_INDICATORS = [
        'check', 'get', 'fetch', 'list', 'show', 'display', 'status',
        'what is', 'how much', 'tell me', 'find', 'search', 'summarize'
    ]

    TECHNICAL_TERMS = [
        'algorithm', 'architecture', 'optimization', 'performance', 'scalability',
        'database', 'security', 'authentication', 'encryption', 'protocol',
        'framework', 'library', 'dependency', 'middleware', 'endpoint',
        'microservice', 'container', 'docker', 'kubernetes', 'pipeline'
    ]

    CREATIVE_MARKERS = [
        'creative', 'imaginative', 'story', 'poem', 'narrative', 'write a',
        'compose', 'brainstorm', 'innovative', 'original', 'artistic'
    ]

    IMPERATIVE_VERBS = [
        'analyze', 'evaluate', 'compare', 'assess', 'investigate', 'examine',
        'review', 'validate', 'verify', 'optimize', 'improve', 'enhance',
        'design', 'architect', 'plan', 'structure', 'model', 'prototype',
        'audit', 'inspect', 'assess'
    ]
    
    CRITICAL_KEYWORDS = [
        'security', 'production', 'deploy', 'release', 'financial', 'payment',
        'vulnerability', 'exploit', 'breach', 'audit', 'compliance', 'regulatory',
        'critical', 'urgent', 'emergency', 'live', 'mainnet'
    ]
    
    ARCHITECTURE_KEYWORDS = [
        'architecture', 'architect', 'design system', 'system design',
        'scalable', 'distributed', 'microservices', 'service mesh',
        'high availability', 'fault tolerant', 'load balancing',
        'api gateway', 'event driven', 'message queue', 'service oriented'
    ]

    CONSTRAINT_KEYWORDS = [
        'must', 'should', 'require', 'need', 'constraint', 'limit', 'restriction',
        'only', 'exactly', 'precisely', 'specifically', 'without', 'except'
    ]

    # Token estimates for different task complexities
    TOKEN_ESTIMATES = {
        'SIMPLE': {'input': 500, 'output': 200},
        'MEDIUM': {'input': 2000, 'output': 1000},
        'COMPLEX': {'input': 5000, 'output': 3000},
        'REASONING': {'input': 3000, 'output': 2000},
        'CRITICAL': {'input': 8000, 'output': 5000}
    }

    def __init__(self, config_path=None):
        """Initialize router with config file."""
        if config_path is None:
            # Default to config.json in the skill directory
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config.json'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self):
        """Load and parse configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create a config.json file with your model definitions."
            )
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            if 'models' not in config:
                raise ValueError("Configuration must contain a 'models' array")
            
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    @staticmethod
    def _full_id(model: dict) -> str:
        """Return provider/id string for a model record."""
        p = model.get("provider", "")
        i = model.get("id", "")
        return f"{p}/{i}" if p else i

    @staticmethod
    def _model_matches(model: dict, lookup_id: str) -> bool:
        """Match a model record by bare id OR full provider/id."""
        if model.get("id") == lookup_id:
            return True
        p = model.get("provider", "")
        i = model.get("id", "")
        return (f"{p}/{i}" == lookup_id) if p else False

    def _find_model(self, models: list, lookup_id: str, default=None):
        """Find a model by bare id or provider/id, return default if not found."""
        return next((m for m in models if self._model_matches(m, lookup_id)), default)

    def _count_matches(self, text, patterns, use_regex=False):
        """Count pattern matches in text (case-insensitive).
        
        Args:
            text: Text to search
            patterns: List of patterns (keywords or regex)
            use_regex: If True, treat all patterns as regex. If False, treat as keywords.
        """
        text_lower = text.lower()
        count = 0
        
        for pattern in patterns:
            if use_regex:
                # Regex pattern
                try:
                    count += len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
                except:
                    # If regex fails, try as keyword
                    count += text_lower.count(pattern.lower())
            else:
                # Simple keyword
                count += text_lower.count(pattern.lower())
        
        return count

    def _calculate_dimension_scores(self, task_description):
        """Calculate scores for all 15 dimensions."""
        text = task_description
        text_lower = text.lower()
        
        scores = {}
        
        # 1. Reasoning markers (0.18)
        reasoning_count = self._count_matches(text, self.REASONING_KEYWORDS)
        scores['reasoning_markers'] = min(reasoning_count / 3.0, 1.0)
        
        # 2. Code presence (0.15)
        code_count = self._count_matches(text, self.CODE_PATTERNS, use_regex=True) + self._count_matches(text, self.CODE_KEYWORDS)
        scores['code_presence'] = min(code_count / 3.0, 1.0)
        
        # 3. Multi-step patterns (0.12)
        multi_step_count = self._count_matches(text, self.MULTI_STEP_PATTERNS, use_regex=True)
        # Detect multi-component indicators ("with X, Y, and Z" or "across N services")
        multi_component_patterns = [r'with\s+\w+[,\s]+\w+\s+and', r'across\s+\d+\s+(services|components|systems)']
        multi_step_count += self._count_matches(text, multi_component_patterns, use_regex=True)
        scores['multi_step_patterns'] = min(multi_step_count / 2.0, 1.0)
        
        # 4. Agentic task (0.10)
        agentic_count = self._count_matches(text, self.AGENTIC_KEYWORDS)
        # Architecture design is inherently agentic (multi-step planning)
        arch_verbs = ['design', 'architect', 'plan', 'structure']
        arch_verb_count = self._count_matches(text, arch_verbs)
        if arch_verb_count > 0:
            agentic_count += arch_verb_count * 2  # Architecture verbs count double
        scores['agentic_task'] = min(agentic_count / 3.0, 1.0)
        
        # 5. Technical terms (0.10)
        tech_count = self._count_matches(text, self.TECHNICAL_TERMS)
        # Boost for architecture keywords (strong COMPLEX signal)
        arch_count = self._count_matches(text, self.ARCHITECTURE_KEYWORDS)
        if arch_count > 0:
            tech_count += arch_count * 2  # Architecture keywords count double
        scores['technical_terms'] = min(tech_count / 4.0, 1.0)
        
        # 6. Token count (0.08) - estimate based on word count
        word_count = len(text.split())
        token_estimate = word_count * 1.3  # rough estimate
        scores['token_count'] = min(token_estimate / 1000.0, 1.0)
        
        # 7. Creative markers (0.05)
        creative_count = self._count_matches(text, self.CREATIVE_MARKERS)
        scores['creative_markers'] = min(creative_count / 2.0, 1.0)
        
        # 8. Question complexity (0.05)
        question_marks = text.count('?')
        question_words = len(re.findall(r'\b(who|what|when|where|why|how)\b', text_lower))
        scores['question_complexity'] = min((question_marks + question_words) / 3.0, 1.0)
        
        # 9. Constraint count (0.04)
        constraint_count = self._count_matches(text, self.CONSTRAINT_KEYWORDS)
        scores['constraint_count'] = min(constraint_count / 3.0, 1.0)
        
        # 10. Imperative verbs (0.03)
        imperative_count = self._count_matches(text, self.IMPERATIVE_VERBS)
        scores['imperative_verbs'] = min(imperative_count / 2.0, 1.0)
        
        # 11. Output format (0.03) - structured output requests
        format_patterns = [r'\bjson\b', r'\btable\b', r'\blist\b', r'\bmarkdown\b', r'\bformat\b']
        format_count = self._count_matches(text, format_patterns)
        scores['output_format'] = min(format_count / 2.0, 1.0)
        
        # 12. Simple indicators (0.02) - inverted (high = simple)
        simple_count = self._count_matches(text, self.SIMPLE_INDICATORS)
        scores['simple_indicators'] = max(0, 1.0 - min(simple_count / 2.0, 1.0))
        
        # 13. Domain specificity (0.02)
        domain_patterns = [r'\b[A-Z]{2,}\b', r'\b\w+\.\w+\b']  # acronyms, dotted notation
        domain_count = self._count_matches(text, domain_patterns, use_regex=True)
        # Add architecture-specific domain terms
        arch_domain_terms = ['kubernetes', 'docker', 'redis', 'kafka', 'rabbitmq', 
                            'graphql', 'grpc', 'rest api', 'websocket', 'oauth']
        domain_count += self._count_matches(text, arch_domain_terms)
        scores['domain_specificity'] = min(domain_count / 3.0, 1.0)
        
        # 14. Reference complexity (0.02)
        ref_patterns = [r'\bthe\s+\w+\s+(?:above|below|mentioned|previous)\b', r'\bthis\s+\w+\b']
        ref_count = self._count_matches(text, ref_patterns)
        scores['reference_complexity'] = min(ref_count / 2.0, 1.0)
        
        # 15. Negation complexity (0.01)
        negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bexcept\b']
        negation_count = self._count_matches(text, negation_patterns)
        scores['negation_complexity'] = min(negation_count / 3.0, 1.0)
        
        return scores

    def _calculate_weighted_score(self, dimension_scores):
        """Calculate final weighted score from dimension scores."""
        weighted_sum = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.SCORING_WEIGHTS.get(dimension, 0.0)
            weighted_sum += weight * score
        
        return weighted_sum

    def _score_to_confidence(self, score):
        """Convert weighted score to confidence using sigmoid function.
        
        Formula: confidence = 1 / (1 + exp(-8 * (score - 0.5)))
        
        This creates a smooth S-curve:
        - score 0.0 → confidence ~0.02
        - score 0.25 → confidence ~0.12
        - score 0.5 → confidence ~0.50
        - score 0.75 → confidence ~0.88
        - score 1.0 → confidence ~0.98
        """
        return 1.0 / (1.0 + math.exp(-8.0 * (score - 0.5)))

    def _classify_by_score(self, score, confidence, is_agentic, dimension_scores=None, task_text=""):
        """Classify task tier based on weighted score and confidence."""
        # Check for CRITICAL keywords (security, production, financial)
        if task_text:
            critical_count = self._count_matches(task_text, self.CRITICAL_KEYWORDS)
            if critical_count >= 2:
                # Multiple critical keywords → force CRITICAL tier
                return 'CRITICAL'
            elif critical_count == 1:
                # Single critical keyword → boost to at least COMPLEX
                if score < 0.5:
                    score = 0.5
        
        # Check for REASONING tier first (special logic)
        # REASONING requires high reasoning_markers score specifically
        if dimension_scores and dimension_scores.get('reasoning_markers', 0) >= 0.6:
            # Strong reasoning markers detected (prove, theorem, derive, etc.)
            # Confidence threshold of ~0.7 (score ~0.6) for REASONING tier
            if score >= 0.10 or confidence >= 0.30:
                return 'REASONING'
        
        # Check for complex agentic tasks (multi-step + agentic + code)
        # Only apply bumps when the raw score shows genuine complexity (>= 0.15).
        # Low scores (< 0.15) indicate keyword noise, not real agentic work — leave as SIMPLE.
        if is_agentic and dimension_scores and score >= 0.15:
            code_score = dimension_scores.get('code_presence', 0)
            multi_step = dimension_scores.get('multi_step_patterns', 0)

            # Multi-step agentic tasks with code → COMPLEX tier
            if multi_step > 0.3 and code_score > 0:
                if score < 0.5:
                    score = 0.5  # Bump to COMPLEX tier
            # Genuine agentic tasks → at least MEDIUM (not triggered by substring matches)
            elif score < 0.4:
                score = 0.4  # Ensure minimum MEDIUM tier
        
        # Score-based classification
        if score < 0.3:
            return 'SIMPLE'
        elif score < 0.5:
            return 'MEDIUM'
        elif score < 0.75:
            return 'COMPLEX'
        else:
            return 'CRITICAL'

    def classify_task(self, task_description, return_details=False):
        """
        Classify a task into a tier using 15-dimension weighted scoring.
        
        Args:
            task_description: The task to classify
            return_details: If True, return detailed scoring breakdown
        
        Returns:
            If return_details=False: tier name (SIMPLE/MEDIUM/COMPLEX/REASONING/CRITICAL)
            If return_details=True: dict with tier, scores, confidence, and reasoning
        """
        # Calculate dimension scores
        dimension_scores = self._calculate_dimension_scores(task_description)
        
        # Calculate weighted score
        weighted_score = self._calculate_weighted_score(dimension_scores)
        
        # Convert to confidence
        confidence = self._score_to_confidence(weighted_score)
        
        # Check if task is agentic (lowered threshold from 0.5 to 0.3)
        is_agentic = dimension_scores['agentic_task'] > 0.3 or dimension_scores['multi_step_patterns'] > 0.5
        
        # Classify
        tier = self._classify_by_score(weighted_score, confidence, is_agentic, dimension_scores, task_description)
        
        if not return_details:
            return tier
        
        return {
            'tier': tier,
            'confidence': round(confidence, 4),
            'weighted_score': round(weighted_score, 4),
            'is_agentic': is_agentic,
            'dimension_scores': {k: round(v, 3) for k, v in dimension_scores.items()},
            'top_dimensions': self._get_top_dimensions(dimension_scores, n=5)
        }

    def _get_top_dimensions(self, dimension_scores, n=5):
        """Get top N contributing dimensions."""
        weighted_contributions = {}
        for dim, score in dimension_scores.items():
            weighted_contributions[dim] = score * self.SCORING_WEIGHTS[dim]
        
        sorted_dims = sorted(weighted_contributions.items(), key=lambda x: x[1], reverse=True)
        return [(dim, round(contrib, 4)) for dim, contrib in sorted_dims[:n]]

    def get_models_by_tier(self, tier):
        """Get all models for a specific tier."""
        return [
            model for model in self.config['models']
            if model.get('tier') == tier
        ]

    def recommend_model(self, task_description, use_fallback=False, fallback_index=0):
        """
        Classify task and recommend the best model for it.
        
        Args:
            task_description: The task to classify
            use_fallback: If True, use fallback chain instead of primary
            fallback_index: Which fallback in chain to use (0 = first fallback)
        
        Returns:
            Dict with tier, recommended model, fallback chain, and reasoning.
        """
        # Get detailed classification
        classification = self.classify_task(task_description, return_details=True)
        tier = classification['tier']
        
        models = self.get_models_by_tier(tier)
        
        if not models:
            return {
                'tier': tier,
                'model': None,
                'fallback_chain': [],
                'classification': classification,
                'reasoning': f"No models configured for {tier} tier"
            }
        
        # Get routing rules
        routing_rules = self.config.get('routing_rules', {}).get(tier, {})
        primary_id = routing_rules.get('primary')
        fallback_chain = routing_rules.get('fallback_chain', [])
        
        # Find primary model
        primary = None
        if primary_id:
            primary = self._find_model(models, primary_id, models[0] if models else None)
        else:
            primary = models[0]
        
        # Determine which model to return
        if use_fallback and fallback_chain:
            if fallback_index < len(fallback_chain):
                fallback_id = fallback_chain[fallback_index]
                recommended = self._find_model(self.config['models'], fallback_id, primary)
            else:
                recommended = primary  # Exhausted fallbacks
        else:
            recommended = primary
        
        return {
            'tier': tier,
            'model': recommended,
            'fallback_chain': fallback_chain,
            'classification': classification,
            'reasoning': self._explain_tier(tier, classification)
        }

    def _explain_tier(self, tier, classification):
        """Provide reasoning for tier classification."""
        base_explanations = {
            'SIMPLE': 'Routine monitoring, status checks, or simple data fetching',
            'MEDIUM': 'Moderate complexity tasks like code fixes or research',
            'COMPLEX': 'Multi-file development, debugging, or architectural work',
            'REASONING': 'Formal logic, mathematical proofs, or step-by-step derivations',
            'CRITICAL': 'Security-sensitive, production, or high-stakes operations'
        }
        
        explanation = base_explanations.get(tier, 'General purpose task')
        
        # Add top contributing dimensions
        if classification and 'top_dimensions' in classification:
            top_dims = classification['top_dimensions'][:3]
            dim_names = [dim.replace('_', ' ') for dim, _ in top_dims]
            explanation += f" (key factors: {', '.join(dim_names)})"
        
        if classification and classification.get('is_agentic'):
            explanation += " [Agentic task detected]"
        
        return explanation

    def estimate_cost(self, task_description):
        """
        Estimate the cost of running a task based on its complexity.
        Returns dict with tier, token estimates, and cost breakdown.
        """
        classification = self.classify_task(task_description, return_details=True)
        tier = classification['tier']
        models = self.get_models_by_tier(tier)
        
        if not models:
            return {
                'tier': tier,
                'classification': classification,
                'error': f"No models configured for {tier} tier"
            }
        
        model = models[0]
        tokens = self.TOKEN_ESTIMATES.get(tier, self.TOKEN_ESTIMATES['MEDIUM'])
        
        # Calculate costs (per million tokens → actual tokens)
        input_cost = (tokens['input'] / 1_000_000) * model['input_cost_per_m']
        output_cost = (tokens['output'] / 1_000_000) * model['output_cost_per_m']
        total_cost = input_cost + output_cost
        
        return {
            'tier': tier,
            'model': model['alias'],
            'estimated_tokens': tokens,
            'classification': classification,
            'costs': {
                'input': round(input_cost, 6),
                'output': round(output_cost, 6),
                'total': round(total_cost, 6)
            },
            'currency': 'USD'
        }

    def list_models(self):
        """List all configured models grouped by tier."""
        tiers = {}
        for model in self.config['models']:
            tier = model.get('tier', 'UNKNOWN')
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(model)
        
        return tiers

    def health_check(self):
        """Validate configuration file and report health status."""
        issues = []
        
        # Check if models exist
        if not self.config.get('models'):
            issues.append("No models defined in configuration")
        
        # Validate each model
        required_fields = ['id', 'alias', 'tier', 'input_cost_per_m', 'output_cost_per_m']
        for i, model in enumerate(self.config.get('models', [])):
            for field in required_fields:
                if field not in model:
                    issues.append(f"Model {i}: missing required field '{field}'")
            
            # Check tier validity
            tier = model.get('tier')
            if tier not in ['SIMPLE', 'MEDIUM', 'COMPLEX', 'REASONING', 'CRITICAL']:
                issues.append(f"Model {i} ({model.get('id')}): invalid tier '{tier}'")
        
        # Check tier coverage
        configured_tiers = set(m.get('tier') for m in self.config.get('models', []))
        all_tiers = set(['SIMPLE', 'MEDIUM', 'COMPLEX', 'REASONING', 'CRITICAL'])
        missing_tiers = all_tiers - configured_tiers
        if missing_tiers:
            issues.append(f"Missing models for tiers: {', '.join(sorted(missing_tiers))}")
        
        # Validate fallback chains
        routing_rules = self.config.get('routing_rules', {})
        for tier, rules in routing_rules.items():
            if 'fallback_chain' in rules:
                for fallback_id in rules['fallback_chain']:
                    if not any(self._model_matches(m, fallback_id) for m in self.config.get('models', [])):
                        issues.append(f"Tier {tier}: fallback model '{fallback_id}' not found in models")
        
        return {
            'status': 'healthy' if not issues else 'unhealthy',
            'issues': issues,
            'model_count': len(self.config.get('models', [])),
            'config_path': str(self.config_path)
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Intelligent Router CLI v2.0 (with weighted scoring & REASONING tier)")
        print("\nUsage:")
        print("  router.py classify <task>     Classify a task and recommend a model")
        print("  router.py models              List all configured models by tier")
        print("  router.py health              Check configuration health")
        print("  router.py cost-estimate <task>  Estimate cost for a task")
        print("  router.py score <task>        Show detailed scoring breakdown")
        print("\nExamples:")
        print('  router.py classify "fix lint errors in utils.js"')
        print('  router.py score "prove that sqrt(2) is irrational step by step"')
        print('  router.py cost-estimate "build authentication system"')
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        router = IntelligentRouter()
        
        if command == 'classify':
            if len(sys.argv) < 3:
                print("Error: Task description required")
                print('Usage: router.py classify "task description"')
                sys.exit(1)
            
            task = ' '.join(sys.argv[2:])
            result = router.recommend_model(task)
            
            print(f"Task: {task}")
            print(f"\nClassification: {result['tier']}")
            print(f"Confidence: {result['classification']['confidence']:.2%}")
            print(f"Weighted Score: {result['classification']['weighted_score']:.3f}")
            print(f"Reasoning: {result['reasoning']}")
            
            if result['model']:
                model = result['model']
                print(f"\nRecommended Model:")
                print(f"  ID: {model['id']}")
                print(f"  Alias: {model['alias']}")
                print(f"  Provider: {model['provider']}")
                print(f"  Cost: ${model['input_cost_per_m']:.2f}/${model['output_cost_per_m']:.2f} per M tokens")
                if model.get('agentic'):
                    print(f"  Agentic: Yes")
                if 'notes' in model:
                    print(f"  Notes: {model['notes']}")
                
                if result['fallback_chain']:
                    print(f"\nFallback Chain:")
                    for i, fb_id in enumerate(result['fallback_chain'], 1):
                        print(f"  {i}. {fb_id}")
            else:
                print(f"\n⚠️  {result['reasoning']}")
        
        elif command == 'score':
            if len(sys.argv) < 3:
                print("Error: Task description required")
                print('Usage: router.py score "task description"')
                sys.exit(1)
            
            task = ' '.join(sys.argv[2:])
            classification = router.classify_task(task, return_details=True)
            
            print(f"Task: {task}")
            print(f"\nClassification: {classification['tier']}")
            print(f"Confidence: {classification['confidence']:.2%}")
            print(f"Weighted Score: {classification['weighted_score']:.3f}")
            print(f"Agentic Task: {'Yes' if classification['is_agentic'] else 'No'}")
            
            print(f"\nTop Contributing Dimensions:")
            for dim, contrib in classification['top_dimensions']:
                dim_name = dim.replace('_', ' ').title()
                print(f"  {dim_name}: {contrib:.4f}")
            
            print(f"\nAll Dimension Scores:")
            for dim, score in sorted(classification['dimension_scores'].items(), key=lambda x: x[1], reverse=True):
                weight = router.SCORING_WEIGHTS[dim]
                dim_name = dim.replace('_', ' ').title()
                print(f"  {dim_name}: {score:.3f} (weight: {weight:.2f})")
        
        elif command == 'models':
            tiers = router.list_models()
            
            print("Configured Models by Tier:\n")
            for tier in ['SIMPLE', 'MEDIUM', 'COMPLEX', 'REASONING', 'CRITICAL']:
                if tier in tiers:
                    print(f"{tier}:")
                    for model in tiers[tier]:
                        cost_str = f"${model['input_cost_per_m']:.2f}/${model['output_cost_per_m']:.2f}/M"
                        agentic_flag = " [Agentic]" if model.get('agentic') else ""
                        print(f"  • {model['alias']} ({model['id']}) - {cost_str}{agentic_flag}")
                    print()
        
        elif command == 'health':
            result = router.health_check()
            
            print(f"Configuration Health Check")
            print(f"Config: {result['config_path']}")
            print(f"Status: {result['status'].upper()}")
            print(f"Models: {result['model_count']}")
            
            if result['issues']:
                print(f"\nIssues found:")
                for issue in result['issues']:
                    print(f"  ⚠️  {issue}")
            else:
                print("\n✅ Configuration is valid")
        
        elif command == 'cost-estimate':
            if len(sys.argv) < 3:
                print("Error: Task description required")
                print('Usage: router.py cost-estimate "task description"')
                sys.exit(1)
            
            task = ' '.join(sys.argv[2:])
            result = router.estimate_cost(task)
            
            print(f"Task: {task}")
            print(f"\nCost Estimate:")
            print(f"  Tier: {result['tier']}")
            print(f"  Confidence: {result['classification']['confidence']:.2%}")
            
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                print(f"  Model: {result['model']}")
                print(f"  Estimated Tokens: {result['estimated_tokens']['input']} in / {result['estimated_tokens']['output']} out")
                print(f"  Input Cost: ${result['costs']['input']:.6f}")
                print(f"  Output Cost: ${result['costs']['output']:.6f}")
                print(f"  Total Cost: ${result['costs']['total']:.6f} {result['currency']}")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: classify, score, models, health, cost-estimate")
            sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
