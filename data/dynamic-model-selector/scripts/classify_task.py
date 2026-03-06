#!/usr/bin/env python3
"""
Dynamic Model Selector Script

Analyzes a user query and recommends the best GitHub Copilot model based on:
- Complexity (length, keywords)
- Task type (code, reasoning, chat)
- Cost considerations
"""

import sys
import re

def classify_query(query):
    """
    Classify the query and return recommended model.
    
    Returns: dict with 'model', 'reason', 'cost_tier'
    """
    query_lower = query.lower()
    length = len(query.split())
    
    # Keywords indicating complexity
    complex_keywords = ['explain', 'analyze', 'design', 'architecture', 'optimize', 'debug', 'troubleshoot', 'research', 'plan', 'strategy']
    code_keywords = ['code', 'function', 'class', 'script', 'api', 'database', 'algorithm', 'debug', 'fix']
    creative_keywords = ['write', 'story', 'poem', 'design', 'create', 'generate']
    
    # Simple heuristics
    is_very_complex = any(kw in query_lower for kw in complex_keywords) and length > 100
    is_complex = any(kw in query_lower for kw in complex_keywords) or length > 50
    is_code = any(kw in query_lower for kw in code_keywords) or '```' in query or re.search(r'\b(def|class|import|function|async|await)\b', query_lower)
    is_creative = any(kw in query_lower for kw in creative_keywords) and not is_code
    
    if is_very_complex:
        return {
            'model': 'github-copilot/claude-3-opus',
            'reason': 'Very complex task requiring top-tier reasoning',
            'cost_tier': 'paid'
        }
    elif is_complex and is_code:
        return {
            'model': 'github-copilot/gpt-4-turbo',
            'reason': 'Complex code task, needs advanced coding capabilities',
            'cost_tier': 'paid'
        }
    elif is_complex:
        return {
            'model': 'github-copilot/gpt-4o',
            'reason': 'Complex reasoning/analysis task, needs advanced capabilities',
            'cost_tier': 'paid'
        }
    elif is_code:
        return {
            'model': 'github-copilot/grok-code-fast-1',
            'reason': 'Code task, fast and free model suitable',
            'cost_tier': 'free'
        }
    elif is_creative:
        return {
            'model': 'github-copilot/claude-3.5-sonnet',
            'reason': 'Creative writing/design task',
            'cost_tier': 'paid'
        }
    elif length > 20:
        return {
            'model': 'github-copilot/grok-beta',
            'reason': 'Medium complexity, use enhanced free model',
            'cost_tier': 'free'
        }
    else:
        return {
            'model': 'github-copilot/grok-code-fast-1',
            'reason': 'Simple task, fast response sufficient',
            'cost_tier': 'free'
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 classify_task.py \"your query here\"")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    result = classify_query(query)
    
    print(f"Recommended Model: {result['model']}")
    print(f"Reason: {result['reason']}")
    print(f"Cost Tier: {result['cost_tier']}")

if __name__ == '__main__':
    main()