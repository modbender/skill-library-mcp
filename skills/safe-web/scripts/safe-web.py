#!/usr/bin/env python3
"""
safe-web: Secure web fetch and search with PromptGuard scanning.

Protects against prompt injection attacks hidden in web content before 
returning it to the AI.

Usage:
    safe-web fetch <url> [--output file.txt]
    safe-web search "query" [--count 5]

Exit codes:
    0 - Success, content is clean
    1 - Error (network, parsing, etc.)
    2 - Threat detected - content blocked
"""

import sys
import os
import argparse
import json
import tempfile
import re
from urllib.parse import urlparse

def scan_with_promptguard(content: str):
    """Scan content using PromptGuard."""
    try:
        from prompt_guard import PromptGuard
        guard = PromptGuard()
        result = guard.analyze(content)
        return result
    except ImportError:
        print("Error: prompt_guard module not found. Install with:", file=sys.stderr)
        print("  cd /home/linuxbrew/.openclaw/workspace/skills/prompt-guard && pip3 install --break-system-packages -e .", file=sys.stderr)
        sys.exit(1)

def format_shield_report(result, source: str) -> str:
    """Format a SHIELD-style report for detected threats."""
    lines = [
        "=" * 60,
        "🛡️  SAFE-WEB SECURITY ALERT",
        "=" * 60,
        f"Source: {source}",
        f"Severity: {result.severity.name}",
        f"Action: {result.action.name}",
        f"Patterns Matched: {len(result.patterns_matched)}",
        "",
        "Detected Patterns:",
    ]
    for pattern in result.reasons:
        lines.append(f"  - {pattern}")
    lines.append("=" * 60)
    return "\n".join(lines)

def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch content from URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: requests and beautifulsoup4 required. Install with:", file=sys.stderr)
        print("  pip3 install --break-system-packages requests beautifulsoup4", file=sys.stderr)
        sys.exit(1)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract text content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def search_web(query: str, count: int = 5) -> list:
    """Search the web using Brave Search API."""
    try:
        import requests
    except ImportError:
        print("Error: requests required. Install with:", file=sys.stderr)
        print("  pip3 install --break-system-packages requests", file=sys.stderr)
        sys.exit(1)
    
    api_key = os.environ.get('BRAVE_API_KEY')
    if not api_key:
        # Fallback to web search without API if no key
        print("Warning: BRAVE_API_KEY not set. Using fallback search.", file=sys.stderr)
        return []
    
    headers = {
        'X-Subscription-Token': api_key,
        'Accept': 'application/json'
    }
    
    params = {
        'q': query,
        'count': count
    }
    
    try:
        response = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('web', {}).get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'description': item.get('description', '')
            })
        return results
    except requests.RequestException as e:
        print(f"Error searching: {e}", file=sys.stderr)
        sys.exit(1)

def scan_search_results(results: list, strict: bool = False) -> tuple:
    """Scan search results for threats. Return (clean_results, threats_found)."""
    clean_results = []
    threats_found = []
    
    severity_threshold = "MEDIUM" if strict else "HIGH"
    
    for result in results:
        # Scan title
        title_result = scan_with_promptguard(result['title'])
        if title_result.severity.value >= getattr(title_result.severity, severity_threshold).value:
            threats_found.append({
                'field': 'title',
                'url': result['url'],
                'severity': title_result.severity.name,
                'reasons': title_result.reasons
            })
            continue
        
        # Scan description
        desc_result = scan_with_promptguard(result['description'])
        if desc_result.severity.value >= getattr(desc_result.severity, severity_threshold).value:
            threats_found.append({
                'field': 'description',
                'url': result['url'],
                'severity': desc_result.severity.name,
                'reasons': desc_result.reasons
            })
            continue
        
        clean_results.append(result)
    
    return clean_results, threats_found

def cmd_fetch(args):
    """Handle fetch command."""
    if not args.url:
        print("Error: URL required for fetch command", file=sys.stderr)
        sys.exit(1)
    
    # Validate URL
    parsed = urlparse(args.url)
    if not parsed.scheme or not parsed.netloc:
        print(f"Error: Invalid URL: {args.url}", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"Fetching: {args.url}", file=sys.stderr)
    
    # Fetch content
    content = fetch_url(args.url, timeout=args.timeout)
    
    if not args.quiet:
        print(f"Fetched {len(content)} characters", file=sys.stderr)
        print("Scanning with PromptGuard...", file=sys.stderr)
    
    # Scan with PromptGuard
    result = scan_with_promptguard(content)
    
    severity_threshold = "MEDIUM" if args.strict else "HIGH"
    should_block = result.severity.value >= getattr(result.severity, severity_threshold).value
    
    if args.json:
        output = {
            "safe": not should_block,
            "url": args.url,
            "severity": result.severity.name,
            "action": result.action.name,
            "reasons": result.reasons,
            "patterns_matched": len(result.patterns_matched),
            "content": content if not should_block else None,
            "alert": format_shield_report(result, args.url) if should_block else None
        }
        print(json.dumps(output, indent=2))
    elif should_block:
        if not args.quiet:
            print(format_shield_report(result, args.url), file=sys.stderr)
            print(f"\nContent from {args.url} has been blocked.", file=sys.stderr)
            print("\nRecommendations:", file=sys.stderr)
            print("  1. Inspect the URL manually in a browser", file=sys.stderr)
            print("  2. Use --strict for stricter scanning", file=sys.stderr)
            print("  3. Report false positives if this is a trusted site", file=sys.stderr)
        sys.exit(2)
    else:
        # Content is clean, output it
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            if not args.quiet:
                print(f"Clean content written to: {args.output}")
        elif not args.quiet:
            print(content)
    
    sys.exit(0)

def cmd_search(args):
    """Handle search command."""
    if not args.query:
        print("Error: Query required for search command", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"Searching: {args.query}", file=sys.stderr)
    
    # Search the web
    results = search_web(args.query, count=args.count)
    
    if not results:
        if not args.quiet:
            print("No results found or search unavailable.", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"Found {len(results)} results, scanning...", file=sys.stderr)
    
    # Scan results
    clean_results, threats = scan_search_results(results, strict=args.strict)
    
    if args.json:
        output = {
            "query": args.query,
            "total_results": len(results),
            "clean_results": len(clean_results),
            "threats_filtered": len(threats),
            "results": clean_results,
            "threats": threats if threats else None
        }
        print(json.dumps(output, indent=2))
    else:
        if threats and not args.quiet:
            print(f"\n⚠️  Filtered {len(threats)} suspicious results", file=sys.stderr)
        
        if not args.quiet:
            print(f"\nShowing {len(clean_results)} clean results:\n")
            for i, result in enumerate(clean_results, 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   {result['description'][:200]}..." if len(result['description']) > 200 else f"   {result['description']}")
                print()
    
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Secure web fetch and search with PromptGuard scanning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  safe-web fetch https://example.com/article
  safe-web fetch https://example.com --output article.txt
  safe-web search "AI safety research" --count 10
  safe-web fetch https://site.com --json | jq '.safe'
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch and scan a URL')
    fetch_parser.add_argument('url', help='URL to fetch')
    fetch_parser.add_argument('--output', '-o', help='Write clean content to file')
    fetch_parser.add_argument('--timeout', '-t', type=int, default=30, help='Request timeout (seconds)')
    fetch_parser.add_argument('--json', action='store_true', help='Output JSON format')
    fetch_parser.add_argument('--strict', action='store_true', help='Block on MEDIUM severity')
    fetch_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output, only return exit code')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search and scan results')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--count', '-n', type=int, default=5, help='Number of results')
    search_parser.add_argument('--json', action='store_true', help='Output JSON format')
    search_parser.add_argument('--strict', action='store_true', help='Filter on MEDIUM severity')
    search_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output, only return exit code')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'fetch':
        cmd_fetch(args)
    elif args.command == 'search':
        cmd_search(args)

if __name__ == "__main__":
    main()
