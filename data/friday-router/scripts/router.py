#!/usr/bin/env python3
"""
OpenRouterRouter | Codename: Centipede (friday-router skill)
Version 1.7.0

Fixed bugs from original intelligent-router:
- Simple indicators now properly invert (high match = SIMPLE, not complex)
- Agentic tasks properly bump to at least MEDIUM tier
- Code keywords actually detected
- Confidence scores vary appropriately

Features:
- Austin's preferred models (Flash, Haiku, GLM-5, Kimi, Grok, etc.)
- Keyword-based routing for obvious matches
- Weighted scoring for nuanced classification
- OpenClaw integration for spawning sub-agents
"""

import json
import math
import os
import re
import sys
from pathlib import Path

# OpenClaw imports (if available)
try:
    import openclaw
    HAS_OPENCLAW = True
except ImportError:
    HAS_OPENCLAW = False


# Removed get_openclaw_gateway_config() - gateway auth secrets should not be exposed in router output
# Use gateway-guard skill separately if gateway auth management is needed


class FridayRouter:
    """Austin's intelligent model router with fixed scoring."""
    
    # Simple indicators that suggest SIMPLE/Fast tasks (NOT inverted anymore)
    SIMPLE_KEYWORDS = [
        'check', 'get', 'fetch', 'list', 'show', 'display', 'status',
        'what is', 'how much', 'tell me', 'find', 'search', 'summarize',
        'monitor', 'watch', 'read', 'look', 'simple', 'quick', 'fast'
    ]
    
    # Complex indicators that suggest QUALITY/Code tasks
    COMPLEX_KEYWORDS = [
        'build', 'create', 'implement', 'architect', 'design', 'system',
        'comprehensive', 'thorough', 'complex', 'multi', 'full-stack',
        'authentication', 'authorization', 'database', 'api', 'service'
    ]
    
    # Code-related keywords
    CODE_KEYWORDS = [
        'code', 'function', 'class', 'method', 'debug', 'fix', 'bug',
        'refactor', 'lint', 'test', 'unit', 'integration', 'component',
        'module', 'package', 'library', 'framework', 'import', 'export',
        'react', 'vue', 'angular', 'node', 'python', 'javascript',
        'typescript', 'rust', 'go', 'java', 'api', 'endpoint'
    ]
    
    # Reasoning keywords
    REASONING_KEYWORDS = [
        'prove', 'theorem', 'proof', 'derive', 'logic', 'reason',
        'analyze', 'reasoning', 'step by step', 'why', 'how does',
        'explain', 'mathematical', 'induction', 'deduction'
    ]
    
    # Creative keywords
    CREATIVE_KEYWORDS = [
        'creative', 'write', 'story', 'poem', 'article', 'blog',
        'design', 'UI', 'UX', 'frontend', 'website', 'landing',
        'copy', 'narrative', 'brainstorm', 'idea', 'concept'
    ]
    
    # Research keywords
    RESEARCH_KEYWORDS = [
        'research', 'find', 'search', 'lookup', 'web', 'information',
        'fact', 'review', 'compare', 'vs', 'versus', 'difference',
        'summary of', 'what are', 'best', 'top', 'alternatives'
    ]
    
    # Agentic/action keywords (multi-step tasks)
    AGENTIC_KEYWORDS = [
        'run', 'test', 'fix', 'deploy', 'edit', 'build', 'create',
        'implement', 'execute', 'refactor', 'migrate', 'integrate',
        'setup', 'configure', 'install', 'compile', 'debug'
    ]
    
    def __init__(self, config_path=None):
        """Initialize router with config file."""
        if config_path is None:
            # Default to config.json in parent directory of script
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config.json'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Removed troubleshooting loop detection and FACEPALM integration
        # Use FACEPALM skill separately if troubleshooting is needed
    
    def _load_config(self):
        """Load and parse configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _keyword_match(self, text, keywords):
        """Count keyword matches (case-insensitive)."""
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw.lower() in text_lower)
    
    def classify_task(self, task_description, return_details=False):
        """
        Classify a task into a tier using keyword matching + scoring.
        
        Returns: FAST, REASONING, CREATIVE, RESEARCH, CODE, QUALITY, or VISION
        """
        text = task_description.lower()
        
        # First, check for exact keyword tier matches (highest priority)
        tier_scores = {}
        
        # Count matches for each tier
        tier_scores['FAST'] = self._keyword_match(task_description, self.SIMPLE_KEYWORDS)
        tier_scores['REASONING'] = self._keyword_match(task_description, self.REASONING_KEYWORDS)
        tier_scores['CREATIVE'] = self._keyword_match(task_description, self.CREATIVE_KEYWORDS)
        tier_scores['RESEARCH'] = self._keyword_match(task_description, self.RESEARCH_KEYWORDS)
        tier_scores['CODE'] = self._keyword_match(task_description, self.CODE_KEYWORDS)
        tier_scores['COMPLEX'] = self._keyword_match(task_description, self.COMPLEX_KEYWORDS)
        
        # Check for vision keywords (highest priority - if image/picture/photo/screenshot present, force VISION)
        vision_keywords = ['image', 'picture', 'photo', 'screenshot', 'visual', 'see', 'describe what']
        vision_matches = self._keyword_match(task_description, vision_keywords)
        tier_scores['VISION'] = vision_matches
        
        # If vision keywords present, this IS a vision task - override other classifications
        if vision_matches > 0:
            return {
                'tier': 'VISION',
                'confidence': min(vision_matches / 3.0, 1.0),
                'tier_scores': {'VISION': vision_matches},
                'is_agentic': False
            }
        
        # Agentic task detection - if multi-step, bump to at least CODE
        agentic_count = self._keyword_match(task_description, self.AGENTIC_KEYWORDS)
        multi_step_patterns = [
            r'\bfirst\b.*\bthen\b', r'\bstep\s+\d+', r'\d+\.\s+\w+',
            r'\bnext\b', r'\bafter\b', r'\bfinally\b', r',\s*then\b'
        ]
        is_multi_step = any(re.search(p, text) for p in multi_step_patterns)
        
        if agentic_count >= 2 or is_multi_step:
            # Multi-step task - ensure at least CODE tier
            tier_scores['CODE'] += 2
            if tier_scores['FAST'] > 0:
                tier_scores['FAST'] = 0  # Override FAST if agentic
        
        # Find best matching tier
        if max(tier_scores.values()) == 0:
            # No keywords matched - default to FAST
            best_tier = 'FAST'
        else:
            best_tier = max(tier_scores, key=tier_scores.get)
        
        # Website/frontend projects → CREATIVE (Kimi k2.5), never CODE
        website_project_keywords = [
            'website', 'web site', 'landing page', 'landing', 'frontend',
            'community site', 'online community', 'build a site', 'new site'
        ]
        if self._keyword_match(task_description, website_project_keywords) > 0:
            best_tier = 'CREATIVE'
        
        # Map COMPLEX to CODE for our tier system
        if best_tier == 'COMPLEX':
            # If also has code keywords, use CODE tier
            if tier_scores['CODE'] > 0:
                best_tier = 'CODE'
            else:
                best_tier = 'QUALITY'
        
        # Special handling: if both COMPLEX and FAST matched, prefer CODE/QUALITY
        if tier_scores['COMPLEX'] > 0 and tier_scores['FAST'] > 0:
            if tier_scores['COMPLEX'] >= tier_scores['FAST']:
                best_tier = 'QUALITY' if tier_scores['COMPLEX'] >= 2 else 'CODE'
        
        # Calculate confidence based on match strength
        max_score = max(tier_scores.values())
        confidence = min(max_score / 5.0, 1.0)  # Cap at 1.0, normalize around 5 matches = 100%
        
        result = {
            'tier': best_tier,
            'confidence': round(confidence, 3),
            'tier_scores': {k: v for k, v in tier_scores.items() if v > 0},
            'is_agentic': agentic_count >= 2 or is_multi_step
        }
        
        if not return_details:
            return result['tier']
        
        return result
    
    def get_default_model(self):
        """Return the default model (Gemini 2.5 Flash). Used for session default and orchestrator."""
        default_id = self.config.get('default_model')
        if not default_id:
            # Fallback: QUALITY tier primary
            tier_rules = self.config.get('routing_rules', {}).get('QUALITY', {})
            default_id = tier_rules.get('primary')
        for m in self.config.get('models', []):
            if m['id'] == default_id:
                return m
        return None
    
    def recommend_model(self, task_description):
        """Classify task and recommend the best model."""
        classification = self.classify_task(task_description, return_details=True)
        tier = classification['tier']
        
        # Get routing rules for this tier
        routing_rules = self.config.get('routing_rules', {})
        tier_rules = routing_rules.get(tier, {})
        
        # Get primary model
        primary_id = tier_rules.get('primary')
        
        # Find model in config
        model = None
        for m in self.config.get('models', []):
            if m['id'] == primary_id:
                model = m
                break
        
        # Fallback
        fallback = None
        fallback_ids = tier_rules.get('fallback', [])
        if fallback_ids:
            for fb_id in fallback_ids:
                for m in self.config.get('models', []):
                    if m['id'] == fb_id:
                        fallback = m
                        break
        
        return {
            'tier': tier,
            'model': model,
            'fallback': fallback,
            'classification': classification,
            'reasoning': self._explain(tier, classification)
        }
    
    def _explain(self, tier, classification):
        """Provide reasoning for tier selection."""
        explanations = {
            'FAST': 'Simple, quick task - monitoring, checks, summaries',
            'REASONING': 'Logical analysis, math, step-by-step reasoning',
            'CREATIVE': 'Creative writing, design, frontend work',
            'RESEARCH': 'Information lookup, web search, fact-finding',
            'CODE': 'Code generation, debugging, implementation',
            'COMPLEX': 'Code generation, debugging, implementation',  # Maps to CODE
            'QUALITY': 'Complex, comprehensive, architectural work',
            'VISION': 'Image analysis, visual understanding'
        }
        
        explanation = explanations.get(tier, 'General task')
        
        if classification.get('is_agentic'):
            explanation += ' [Multi-step agentic task detected]'
        
        return explanation
    
    def estimate_cost(self, task_description):
        """Estimate cost for a task."""
        result = self.recommend_model(task_description)
        model = result['model']
        
        if not model:
            return {'error': 'No model found for tier'}
        
        # Rough token estimates
        token_estimate = {
            'FAST': {'in': 500, 'out': 200},
            'REASONING': {'in': 2000, 'out': 1500},
            'CREATIVE': {'in': 1500, 'out': 2000},
            'RESEARCH': {'in': 1000, 'out': 500},
            'CODE': {'in': 2000, 'out': 1500},
            'QUALITY': {'in': 5000, 'out': 3000},
            'VISION': {'in': 500, 'out': 500}
        }
        
        tokens = token_estimate.get(result['tier'], {'in': 500, 'out': 200})
        
        input_cost = (tokens['in'] / 1_000_000) * model['input_cost_per_m']
        output_cost = (tokens['out'] / 1_000_000) * model['output_cost_per_m']
        
        return {
            'tier': result['tier'],
            'model': model['alias'],
            'cost': round(input_cost + output_cost, 4),
            'currency': 'USD'
        }
    
    def spawn_agent(self, task, session_target='isolated', label=None):
        """Spawn an OpenClaw sub-agent with the appropriate model."""
        recommendation = self.recommend_model(task)
        model = recommendation['model']
        
        if not model:
            raise ValueError(f"No model found for tier: {recommendation['tier']}")
        
        # Build the spawn params (no gateway auth secrets)
        params = {
            'task': task,
            'model': model['id'],
            'sessionTarget': session_target
        }
        
        if label:
            params['label'] = label
        
        return {
            'params': params,
            'recommendation': recommendation
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("OpenRouterRouter | Codename: Centipede v1.7.0")
        print("\nUsage:")
        print("  router.py default                Show session default model (capable by default)")
        print("  router.py classify <task>       Classify task and recommend model")
        print("  router.py score <task>          Show detailed scoring")
        print("  router.py cost <task>           Estimate cost")
        print("  router.py models               List all models")
        print("  router.py spawn [--json] <task>  Show spawn params for OpenClaw (--json for machine-readable)")
        sys.exit(1)
    
    command = sys.argv[1]
    router = FridayRouter()
    
    # Parse --json for spawn command
    output_json = False
    if command == 'spawn' and len(sys.argv) > 2 and sys.argv[2] == '--json':
        output_json = True
        sys.argv.pop(2)  # remove --json so task = ' '.join(sys.argv[2:])
    
    if command == 'default':
        m = router.get_default_model()
        if not m:
            print("❌ No default model configured (missing default_model or QUALITY primary in config)")
            sys.exit(1)
        print("🎯 Session default model (capable by default):\n")
        print(f"   {m['alias']} ({m['id']})")
        print(f"   Cost: ${m['input_cost_per_m']}/${m['output_cost_per_m']} per M")
        print(f"   Use for: {', '.join(m.get('use_for', []))}")
        print("\n   Simple tasks down-route to FAST tier (e.g. Gemini 2.5 Flash).")
    
    elif command == 'classify':
        task = ' '.join(sys.argv[2:])
        result = router.recommend_model(task)
        
        print(f"📋 Task: {task}")
        print(f"\n🎯 Classification: {result['tier']}")
        print(f"   Confidence: {result['classification']['confidence']:.1%}")
        print(f"   Reasoning: {result['reasoning']}")
        
        if result['model']:
            m = result['model']
            print(f"\n🤖 Recommended Model:")
            print(f"   {m['alias']} ({m['id']})")
            print(f"   Cost: ${m['input_cost_per_m']}/${m['output_cost_per_m']} per M")
            print(f"   Use for: {', '.join(m.get('use_for', []))}")
        
        if result['fallback']:
            fb = result['fallback']
            print(f"\n🔄 Fallback: {fb['alias']} ({fb['id']})")
    
    elif command == 'score':
        task = ' '.join(sys.argv[2:])
        result = router.classify_task(task, return_details=True)
        
        print(f"📋 Task: {task}")
        print(f"\n🎯 Tier: {result['tier']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Agentic: {'Yes' if result['is_agentic'] else 'No'}")
        
        print(f"\n📊 Tier Scores:")
        for tier, score in sorted(result['tier_scores'].items(), key=lambda x: x[1], reverse=True):
            bar = '█' * score
            print(f"   {tier:10} {bar} ({score})")
    
    elif command == 'cost':
        task = ' '.join(sys.argv[2:])
        result = router.estimate_cost(task)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📋 Task: {task}")
            print(f"\n💰 Cost Estimate:")
            print(f"   Tier: {result['tier']}")
            print(f"   Model: {result['model']}")
            print(f"   Est. Cost: ${result['cost']} {result['currency']}")
    
    elif command == 'models':
        print("📦 Configured Models:\n")
        for model in router.config.get('models', []):
            print(f"  {model['alias']:20} [{model['tier']:8}] {model['id']}")
            print(f"                         ${model['input_cost_per_m']}/${model['output_cost_per_m']}/M")
    
    elif command == 'spawn':
        task = ' '.join(sys.argv[2:])
        if not task:
            print("❌ Error: spawn requires a task string", file=sys.stderr)
            sys.exit(1)
        result = router.spawn_agent(task)
        
        if output_json:
            # Machine-readable: single JSON object for sessions_spawn
            # Note: Gateway auth secrets are NOT included - use gateway-guard skill separately if needed
            out = {k: v for k, v in result['params'].items()}
            print(json.dumps(out))
        else:
            print(f"📋 Task: {task}")
            print(f"\n🚀 OpenClaw Spawn Params:")
            print(f"   model: {result['params']['model']}")
            print(f"   sessionTarget: {result['params']['sessionTarget']}")
            print(f"\n📦 Full recommendation:")
            print(f"   Tier: {result['recommendation']['tier']}")
            print(f"   Model: {result['recommendation']['model']['alias']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
