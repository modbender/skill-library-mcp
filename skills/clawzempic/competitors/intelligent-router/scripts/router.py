#!/usr/bin/env python3
"""
Intelligent Router CLI
A tool for classifying tasks and recommending appropriate LLM models.
Python 3.8+ compatible, no external dependencies.
"""

import json
import os
import sys
from pathlib import Path


class IntelligentRouter:
    """Main router class for task classification and model recommendation."""

    # Classification keywords for each tier
    TIER_KEYWORDS = {
        'SIMPLE': [
            'monitor', 'check', 'fetch', 'status', 'summarize', 'summary',
            'list', 'get', 'watch', 'poll', 'read', 'scan', 'find', 'search',
            'extract', 'filter', 'sort', 'count'
        ],
        'MEDIUM': [
            'fix', 'patch', 'update', 'modify', 'refactor', 'improve',
            'research', 'analyze', 'compare', 'review', 'document',
            'test', 'validate', 'lint', 'format', 'optimize'
        ],
        'COMPLEX': [
            'build', 'create', 'develop', 'design', 'architect', 'implement',
            'debug', 'troubleshoot', 'investigate', 'solve', 'integrate',
            'migrate', 'restructure', 'rewrite', 'engineer', 'system'
        ],
        'CRITICAL': [
            'security', 'production', 'deploy', 'release', 'financial',
            'payment', 'audit', 'compliance', 'sensitive', 'confidential',
            'vulnerability', 'exploit', 'breach', 'attack', 'protect'
        ]
    }

    # Token estimates for different task complexities
    TOKEN_ESTIMATES = {
        'SIMPLE': {'input': 500, 'output': 200},
        'MEDIUM': {'input': 2000, 'output': 1000},
        'COMPLEX': {'input': 5000, 'output': 3000},
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

    def classify_task(self, task_description):
        """
        Classify a task into a tier based on keyword matching.
        Returns the tier name (SIMPLE, MEDIUM, COMPLEX, or CRITICAL).
        """
        task_lower = task_description.lower()
        
        # Check each tier from highest to lowest priority
        for tier in ['CRITICAL', 'COMPLEX', 'MEDIUM', 'SIMPLE']:
            keywords = self.TIER_KEYWORDS[tier]
            if any(keyword in task_lower for keyword in keywords):
                return tier
        
        # Default to MEDIUM if no keywords match
        return 'MEDIUM'

    def get_models_by_tier(self, tier):
        """Get all models for a specific tier."""
        return [
            model for model in self.config['models']
            if model.get('tier') == tier
        ]

    def recommend_model(self, task_description):
        """
        Classify task and recommend the best model for it.
        Returns dict with tier, recommended model, and reasoning.
        """
        tier = self.classify_task(task_description)
        models = self.get_models_by_tier(tier)
        
        if not models:
            return {
                'tier': tier,
                'model': None,
                'reasoning': f"No models configured for {tier} tier"
            }
        
        # Recommend the first model in the tier (users can order by preference)
        recommended = models[0]
        
        return {
            'tier': tier,
            'model': recommended,
            'reasoning': self._explain_tier(tier)
        }

    def _explain_tier(self, tier):
        """Provide reasoning for tier classification."""
        explanations = {
            'SIMPLE': 'Routine monitoring, status checks, or simple data fetching',
            'MEDIUM': 'Moderate complexity tasks like code fixes or research',
            'COMPLEX': 'Multi-file development, debugging, or architectural work',
            'CRITICAL': 'Security-sensitive, production, or high-stakes operations'
        }
        return explanations.get(tier, 'General purpose task')

    def estimate_cost(self, task_description):
        """
        Estimate the cost of running a task based on its complexity.
        Returns dict with tier, token estimates, and cost breakdown.
        """
        tier = self.classify_task(task_description)
        models = self.get_models_by_tier(tier)
        
        if not models:
            return {
                'tier': tier,
                'error': f"No models configured for {tier} tier"
            }
        
        model = models[0]
        tokens = self.TOKEN_ESTIMATES[tier]
        
        # Calculate costs (per million tokens → actual tokens)
        input_cost = (tokens['input'] / 1_000_000) * model['input_cost_per_m']
        output_cost = (tokens['output'] / 1_000_000) * model['output_cost_per_m']
        total_cost = input_cost + output_cost
        
        return {
            'tier': tier,
            'model': model['alias'],
            'estimated_tokens': tokens,
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
            if tier not in ['SIMPLE', 'MEDIUM', 'COMPLEX', 'CRITICAL']:
                issues.append(f"Model {i} ({model.get('id')}): invalid tier '{tier}'")
        
        # Check tier coverage
        configured_tiers = set(m.get('tier') for m in self.config.get('models', []))
        all_tiers = set(['SIMPLE', 'MEDIUM', 'COMPLEX', 'CRITICAL'])
        missing_tiers = all_tiers - configured_tiers
        if missing_tiers:
            issues.append(f"Missing models for tiers: {', '.join(sorted(missing_tiers))}")
        
        return {
            'status': 'healthy' if not issues else 'unhealthy',
            'issues': issues,
            'model_count': len(self.config.get('models', [])),
            'config_path': str(self.config_path)
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Intelligent Router CLI")
        print("\nUsage:")
        print("  router.py classify <task>     Classify a task and recommend a model")
        print("  router.py models              List all configured models by tier")
        print("  router.py health              Check configuration health")
        print("  router.py cost-estimate <task>  Estimate cost for a task")
        print("\nExamples:")
        print('  router.py classify "fix lint errors in utils.js"')
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
            print(f"Reasoning: {result['reasoning']}")
            
            if result['model']:
                model = result['model']
                print(f"\nRecommended Model:")
                print(f"  ID: {model['id']}")
                print(f"  Alias: {model['alias']}")
                print(f"  Provider: {model['provider']}")
                print(f"  Cost: ${model['input_cost_per_m']:.2f}/${model['output_cost_per_m']:.2f} per M tokens")
                if 'notes' in model:
                    print(f"  Notes: {model['notes']}")
            else:
                print(f"\n⚠️  {result['reasoning']}")
        
        elif command == 'models':
            tiers = router.list_models()
            
            print("Configured Models by Tier:\n")
            for tier in ['SIMPLE', 'MEDIUM', 'COMPLEX', 'CRITICAL']:
                if tier in tiers:
                    print(f"{tier}:")
                    for model in tiers[tier]:
                        cost_str = f"${model['input_cost_per_m']:.2f}/${model['output_cost_per_m']:.2f}/M"
                        print(f"  • {model['alias']} ({model['id']}) - {cost_str}")
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
            print("Available commands: classify, models, health, cost-estimate")
            sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
