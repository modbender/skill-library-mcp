#!/usr/bin/env python3
"""
LLM-Powered Tree Search for Tiered Memory

Reasons through the memory tree index to find relevant categories,
instead of simple keyword matching.

Modes:
  - keyword: Simple keyword overlap (fast, no LLM)
  - llm: LLM reasons about relevance (accurate, requires LLM)

Usage:
  tree_search.py --query "..." --tree-file path --mode keyword
  tree_search.py --query "..." --tree-file path --mode llm --llm-prompt-file prompt.txt
  tree_search.py --query "..." --tree-file path --mode llm --llm-endpoint http://...
"""

import argparse
import json
import re
import sys

# ─── Keyword Search (Fast, No LLM) ───

def search_keyword(tree, query, top_k=5):
    """
    Keyword-based search: find nodes by term overlap.
    
    Args:
        tree (dict): Memory tree index {path: {desc, warm_count, cold_count, ...}}
        query (str): Search query
        top_k (int): Max results to return
    
    Returns:
        list: [{path, relevance, reason}] sorted by relevance
    """
    query_words = set(query.lower().split())
    results = []
    
    for path, node in tree.items():
        if path == 'root':
            continue
        
        # Handle both dict nodes (warm memory) and string nodes (cold memory)
        if isinstance(node, dict):
            desc = node.get('desc', '')
        elif isinstance(node, str):
            desc = node
        else:
            continue
        
        # Extract words from path and description
        path_words = set(re.split(r'[/_\-\s]', path.lower()))
        desc_words = set(desc.lower().split())
        all_words = path_words | desc_words
        
        # Calculate overlap
        overlap = len(query_words & all_words)
        
        if overlap > 0:
            # Base score from overlap
            score = overlap / max(len(query_words), 1)
            
            # Boost by importance indicators
            warm_count = node.get('warm_count', 0)
            cold_count = node.get('cold_count', 0)
            
            # Nodes with more memories are more important
            importance_boost = min(1.0 + (warm_count * 0.1) + (cold_count * 0.01), 2.0)
            score *= importance_boost
            
            # Boost by recency (last_access)
            import time
            last_access = node.get('last_access', 0)
            if last_access > 0:
                age_days = (time.time() - last_access) / 86400
                recency_boost = 1.0 + (0.5 if age_days < 7 else 0.2 if age_days < 30 else 0)
                score *= recency_boost
            
            reason = f"Keywords: {', '.join(query_words & all_words)}"
            
            results.append({
                'path': path,
                'relevance': round(score, 3),
                'reason': reason,
                'warm_count': warm_count,
                'cold_count': cold_count
            })
    
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results[:top_k]


# ─── LLM Search (Accurate, Needs LLM) ───

def build_llm_prompt(tree, query):
    """
    Build prompt for LLM to reason about tree relevance.
    
    Returns:
        str: Prompt text ready to send to LLM
    """
    # Simplify tree for context efficiency
    tree_simple = []
    for path, node in tree.items():
        if path == 'root':
            continue
        tree_simple.append({
            'path': path,
            'desc': node.get('desc', ''),
            'warm': node.get('warm_count', 0),
            'cold': node.get('cold_count', 0)
        })
    
    # Sort by importance (warm + cold count)
    tree_simple.sort(key=lambda x: x['warm'] + x['cold'], reverse=True)
    
    # Build compact representation
    tree_lines = []
    for item in tree_simple[:50]:  # Max 50 nodes to keep prompt small
        tree_lines.append(
            f"  {item['path']} — {item['desc']} (warm:{item['warm']}, cold:{item['cold']})"
        )
    
    tree_text = '\n'.join(tree_lines)
    
    prompt = f"""You are a memory retrieval system. Given a memory tree index and a user query, identify which categories are relevant.

Memory Tree Index:
{tree_text}

User Query: {query}

Task: Which category paths are relevant to this query? Consider:
- Direct topic match (query mentions the category)
- Semantic relevance (query is about something the category covers)
- Multi-hop connections (query needs info from multiple categories)

Output Format (JSON array):
[
  {{"path": "category/path", "relevance": 0.9, "reason": "why relevant"}},
  {{"path": "another/path", "relevance": 0.6, "reason": "secondary relevance"}}
]

Rules:
- relevance: 0.0-1.0 (1.0 = perfect match, 0.5 = somewhat related)
- Return 1-5 categories, sorted by relevance
- If nothing is relevant, return empty array []
- Only return paths that exist in the tree above

Output (JSON only, no explanation):"""

    return prompt


def search_llm(tree, query, llm_endpoint=None, prompt_file=None, top_k=5):
    """
    LLM-powered search: LLM reasons about relevance.
    
    Args:
        tree (dict): Memory tree index
        query (str): Search query
        llm_endpoint (str): HTTP endpoint for LLM completion
        prompt_file (str): Write prompt to file instead of calling LLM
        top_k (int): Max results
    
    Returns:
        list: [{path, relevance, reason}]
    """
    import urllib.request
    
    prompt = build_llm_prompt(tree, query)
    
    # If prompt_file, just write and exit (for piping to LLM externally)
    if prompt_file:
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        print(f"Prompt written to {prompt_file}", file=sys.stderr)
        print("Run with your LLM, then parse the JSON output", file=sys.stderr)
        sys.exit(0)
    
    # Call LLM endpoint
    if not llm_endpoint:
        print("Error: --llm-endpoint required for LLM mode (or use --llm-prompt-file)", file=sys.stderr)
        print("Falling back to keyword search", file=sys.stderr)
        return search_keyword(tree, query, top_k)
    
    payload = {
        'prompt': prompt,
        'max_tokens': 500,
        'temperature': 0.3,
        'stop': ['\n\n']
    }
    
    try:
        req = urllib.request.Request(
            llm_endpoint,
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.load(resp)
            response_text = result.get('text', result.get('response', result.get('content', '')))
            
            # Parse JSON from response
            # Handle markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            # Extract JSON array
            response_text = response_text.strip()
            if not response_text.startswith('['):
                # Find first [ and last ]
                start = response_text.find('[')
                end = response_text.rfind(']')
                if start >= 0 and end > start:
                    response_text = response_text[start:end+1]
            
            results = json.loads(response_text)
            
            # Validate results
            validated = []
            for item in results:
                if item.get('path') in tree:
                    validated.append(item)
            
            return validated[:top_k]
    
    except Exception as e:
        print(f"LLM search failed: {e}", file=sys.stderr)
        print("Falling back to keyword search", file=sys.stderr)
        return search_keyword(tree, query, top_k)


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description='Tree-based memory search with LLM reasoning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Keyword search (fast, no LLM)
  tree_search.py --query "garden project" --tree-file memory-tree.json --mode keyword

  # LLM search (accurate)
  tree_search.py --query "what did we decide about the hackathon?" \\
    --tree-file memory-tree.json --mode llm --llm-endpoint http://localhost:8080/complete

  # Generate prompt for external LLM
  tree_search.py --query "BSC integration" --tree-file memory-tree.json \\
    --mode llm --llm-prompt-file prompt.txt
  # Then: cat prompt.txt | llm-cli | jq .
        """
    )
    
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--tree-file', required=True, help='Path to memory-tree.json')
    parser.add_argument('--mode', choices=['keyword', 'llm'], default='keyword',
                        help='Search mode (default: keyword)')
    parser.add_argument('--llm-endpoint', help='LLM HTTP endpoint (for --mode llm)')
    parser.add_argument('--llm-prompt-file', help='Write LLM prompt to file instead of calling')
    parser.add_argument('--top-k', type=int, default=5, help='Max results (default: 5)')
    parser.add_argument('--output', help='Write results to file')
    
    args = parser.parse_args()
    
    # Load tree
    try:
        with open(args.tree_file) as f:
            tree = json.load(f)
    except Exception as e:
        print(f"Error loading tree: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Search
    if args.mode == 'keyword':
        results = search_keyword(tree, args.query, args.top_k)
    else:
        results = search_llm(tree, args.query, args.llm_endpoint, args.llm_prompt_file, args.top_k)
    
    # Output
    output = {
        'query': args.query,
        'mode': args.mode,
        'results': results,
        'count': len(results)
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
