#!/usr/bin/env python3
"""
URL Fetcher - Simple web content fetching without external dependencies
Uses only Python stdlib (urllib) - no API keys, no pip install needed

Usage: python3 url_fetcher.py fetch <url> [output_file]
       python3 url_fetcher.py fetch --markdown <url> [output_file]
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime
import re

# Safe file locations
SAFE_PATHS = [
    Path.home() / ".openclaw" / "workspace",
    Path.home(),
    Path("/tmp")
]

def is_safe_path(filepath):
    """Check if file path is in safe locations"""
    try:
        path = Path(filepath).expanduser().resolve()
        path_str = str(path)
        
        for safe in SAFE_PATHS:
            if path_str.startswith(str(safe.resolve())):
                blocked = ["/etc", "/usr", "/var", "/root", ".ssh", ".bashrc", ".zshrc"]
                if not any(b in path_str for b in blocked):
                    return True
        return False
    except:
        return False

def fetch_url(url, timeout=10):
    """Fetch URL content safely using urllib (stdlib only)"""
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or parsed.scheme not in ['http', 'https']:
            return {"error": "Invalid URL scheme (only http/https allowed)"}
        
        # Block localhost/internal networks
        blocked_hosts = ['localhost', '127.0.0.1', '::1', '0.0.0.0', '0.0.0.0']
        if parsed.hostname in blocked_hosts or parsed.hostname == '0.0.0.0':
            return {"error": "Internal/localhost URLs blocked"}
        
        # Create request with headers
        req = Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; URLFetcher/1.0)'
            }
        )
        
        # Fetch
        response = urlopen(req, timeout=timeout)
        
        # Get content type
        content_type = response.headers.get('Content-Type', 'text/plain')
        
        # Read content
        content = response.read().decode('utf-8', errors='ignore')
        
        return {
            "url": url,
            "status_code": response.status,
            "content_type": content_type,
            "content_length": len(content),
            "text": content,
            "fetched_at": datetime.now().isoformat()
        }
        
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"URL error: {e.reason}"}
    except TimeoutError:
        return {"error": f"Request timeout after {timeout}s"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def simple_markdown_extract(html_content, url):
    """Very basic HTML to markdown conversion"""
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert common HTML tags to markdown
    html = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<ul[^>]*>|</ul>|<ol[^>]*>|</ol>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<br[^>]*>', '\n', html, flags=re.IGNORECASE)
    
    # Remove remaining tags
    html = re.sub(r'<[^>]+>', ' ', html)
    
    # Clean up whitespace
    html = re.sub(r'\s+', ' ', html)
    html = html.strip()
    
    # Add header
    title = url.split('/')[-1] or 'Untitled'
    md = f"# {title}\n\n"
    md += f"**Source:** {url}\n"
    md += f"**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"**Note:** Basic markdown extraction. For better results, use a proper parser.\n\n"
    md += "---\n\n"
    md += html
    
    return md

def fetch_command(args):
    """Handle fetch command"""
    if len(args) < 1:
        print("Usage: url_fetcher.py fetch [--markdown] <url> [output_file]")
        return
    
    url = None
    output_file = None
    as_markdown = False
    
    for arg in args:
        if arg == '--markdown':
            as_markdown = True
        elif arg.startswith('http'):
            url = arg
        else:
            output_file = arg
    
    if not url:
        print("Error: URL is required")
        return
    
    print(f"🌐 Fetching: {url}")
    result = fetch_url(url)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"✅ Status: {result['status_code']}")
    print(f"   Content-Type: {result['content_type']}")
    print(f"   Size: {result['content_length']} bytes")
    
    content = result['text']
    
    if as_markdown:
        content = simple_markdown_extract(content, url)
        print("   Format: Markdown (basic extraction)")
    
    if output_file:
        if not is_safe_path(output_file):
            print(f"❌ Security error: Unsafe output path: {output_file}")
            return
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(content)
        print(f"   Saved to: {output_file}")
    else:
        preview = content[:500] + "..." if len(content) > 500 else content
        print(f"\n📄 Preview:\n{preview}")

def main():
    if len(sys.argv) < 2:
        print("URL Fetcher - Simple web content fetching (no API keys, no pip install)")
        print("\nCommands:")
        print("  fetch [--markdown] <url> [output_file]  - Fetch URL content")
        print("\nExamples:")
        print("  url_fetcher.py fetch https://example.com")
        print("  url_fetcher.py fetch --markdown https://example.com output.md")
        print("\nFeatures:")
        print("  • Uses Python stdlib (urllib) - no external dependencies")
        print("  • Validates URLs (blocks localhost/internal)")
        print("  • Path validation for file writes")
        print("  • Basic HTML to markdown conversion")
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "fetch":
        fetch_command(args)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
