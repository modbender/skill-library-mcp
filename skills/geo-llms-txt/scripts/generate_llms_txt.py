#!/usr/bin/env python3
"""
Generate llms.txt files for AI crawler accessibility.
"""

import argparse
import json
import sys
import re
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Install dependencies: pip install requests beautifulsoup4")
    sys.exit(1)


class LLMsTxtGenerator:
    """Generate llms.txt files from website analysis."""
    
    def __init__(self, domain, timeout=10):
        self.domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        self.base_url = f"https://{self.domain}"
        self.timeout = timeout
        self.visited = set()
        self.pages = []
    
    def fetch(self, path='', full_url=None):
        """Fetch a URL with error handling."""
        url = full_url or urljoin(self.base_url, path)
        try:
            resp = requests.get(url, timeout=self.timeout, allow_redirects=True)
            if resp.status_code == 200:
                return resp
        except:
            pass
        return None
    
    def extract_title(self, html):
        """Extract page title from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try title tag
        if soup.title:
            return soup.title.string.strip() if soup.title.string else "Untitled"
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return "Untitled"
    
    def extract_description(self, html, url):
        """Generate a description for a page."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try meta description
        meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta and meta.get('content'):
            desc = meta['content'].strip()
            if len(desc) > 20:
                # Truncate to ~15 words
                words = desc.split()[:15]
                return ' '.join(words) + ('...' if len(desc.split()) > 15 else '')
        
        # Try first paragraph
        p = soup.find('p')
        if p:
            text = p.get_text(strip=True)
            if len(text) > 30:
                words = text.split()[:12]
                return ' '.join(words) + '...'
        
        # Infer from URL path
        path = urlparse(url).path.strip('/')
        if path:
            parts = path.split('/')
            return f"Information about {parts[-1].replace('-', ' ').replace('_', ' ')}"
        
        return "Site page"
    
    def analyze_page(self, url):
        """Analyze a single page and extract info."""
        if url in self.visited:
            return None
        self.visited.add(url)
        
        resp = self.fetch(full_url=url)
        if not resp:
            return None
        
        return {
            'url': url,
            'title': self.extract_title(resp.text),
            'description': self.extract_description(resp.text, url)
        }
    
    def get_sitemap_urls(self):
        """Fetch URLs from sitemap.xml."""
        urls = []
        
        # Try common sitemap locations
        for path in ['/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml']:
            resp = self.fetch(path)
            if resp and resp.status_code == 200:
                # Parse XML
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(resp.text.encode('utf-8'))
                    # Handle both sitemap and urlset
                    for elem in root.iter():
                        if elem.tag.endswith('loc'):
                            urls.append(elem.text.strip())
                except:
                    pass
                if urls:
                    break
        
        # Filter to same domain
        return [u for u in urls if self.domain in u][:50]  # Limit to 50
    
    def categorize_url(self, url):
        """Categorize a URL into section type."""
        path = urlparse(url).path.lower()
        
        if any(x in path for x in ['/blog', '/article', '/post', '/news']):
            return 'blog'
        if any(x in path for x in ['/doc', '/api', '/reference', '/guide']):
            return 'docs'
        if any(x in path for x in ['/product', '/feature', '/solution']):
            return 'products'
        if any(x in path for x in ['/about', '/company', '/team']):
            return 'about'
        if any(x in path for x in ['/contact', '/support', '/help']):
            return 'support'
        if path in ['', '/', '/index']:
            return 'home'
        
        return 'other'
    
    def generate_from_sitemap(self):
        """Generate llms.txt by analyzing sitemap."""
        print("Fetching sitemap...", file=sys.stderr)
        urls = self.get_sitemap_urls()
        
        if not urls:
            print("No sitemap found. Try --interactive mode.", file=sys.stderr)
            return None
        
        print(f"Found {len(urls)} URLs in sitemap", file=sys.stderr)
        
        # Analyze each page
        for url in urls[:40]:  # Limit to 40 pages
            print(f"  Analyzing: {url}", file=sys.stderr)
            page = self.analyze_page(url)
            if page:
                self.pages.append(page)
            time.sleep(0.5)  # Be polite
        
        return self._generate_output()
    
    def generate_interactive(self):
        """Generate llms.txt through interactive prompts."""
        print("\n=== llms.txt Generator ===\n", file=sys.stderr)
        
        # Get brand info
        brand_name = input("Brand name: ").strip()
        tagline = input("One-sentence description: ").strip()
        
        print("\nEnter 2-3 paragraphs about your company (press Enter twice when done):")
        paragraphs = []
        while True:
            line = input()
            if not line and paragraphs and not paragraphs[-1]:
                break
            paragraphs.append(line)
        
        overview = '\n'.join(paragraphs).strip()
        
        # Get URLs
        print("\nEnter important URLs (one per line, blank line when done):")
        urls = []
        while True:
            url = input("URL: ").strip()
            if not url:
                break
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            urls.append(url)
        
        # Analyze pages
        for url in urls:
            print(f"\nAnalyzing: {url}", file=sys.stderr)
            page = self.analyze_page(url)
            if page:
                print(f"  Title: {page['title']}")
                print(f"  Description: {page['description']}")
                edit = input("  Edit description? (press Enter to keep, or type new): ").strip()
                if edit:
                    page['description'] = edit
                self.pages.append(page)
        
        return self._generate_output(brand_name, tagline, overview)
    
    def generate_from_file(self, filepath):
        """Generate llms.txt from a file of URLs."""
        with open(filepath, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for url in urls:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            print(f"Analyzing: {url}", file=sys.stderr)
            page = self.analyze_page(url)
            if page:
                self.pages.append(page)
            time.sleep(0.5)
        
        return self._generate_output()
    
    def _generate_output(self, brand_name=None, tagline=None, overview=None):
        """Generate the llms.txt content."""
        # Try to get brand info from homepage if not provided
        if not brand_name:
            home = self.fetch('/')
            if home:
                soup = BeautifulSoup(home.text, 'html.parser')
                brand_name = self.extract_title(home.text).split('-')[0].split('|')[0].strip()
                
                # Try to get tagline from meta
                meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                if meta:
                    tagline = meta.get('content', '')[:100]
                else:
                    tagline = f"Official website for {brand_name}"
                
                # Try to get overview from about page
                about = self.fetch('/about')
                if about:
                    soup = BeautifulSoup(about.text, 'html.parser')
                    # Get first few paragraphs
                    ps = soup.find_all('p', limit=3)
                    overview = '\n\n'.join(p.get_text(strip=True) for p in ps if len(p.get_text(strip=True)) > 50)
        
        # Default values
        brand_name = brand_name or self.domain
        tagline = tagline or f"Official website for {brand_name}"
        overview = overview or f"{brand_name} provides products and services. Visit the website for more information."
        
        # Categorize pages
        sections = {
            'home': [],
            'products': [],
            'docs': [],
            'blog': [],
            'about': [],
            'support': [],
            'other': []
        }
        
        for page in self.pages:
            cat = self.categorize_url(page['url'])
            sections[cat].append(page)
        
        # Build output
        lines = [
            f"# {brand_name}",
            "",
            f"> {tagline}",
            "",
            overview,
            ""
        ]
        
        # Add sections
        section_names = {
            'home': 'Home',
            'products': 'Products & Features',
            'docs': 'Documentation',
            'blog': 'Blog & Resources',
            'about': 'About',
            'support': 'Support & Contact',
            'other': 'Additional Pages'
        }
        
        for cat, pages in sections.items():
            if pages:
                lines.append(f"## {section_names[cat]}")
                lines.append("")
                for page in pages[:15]:  # Max 15 per section
                    lines.append(f"- [{page['title']}]({page['url']}): {page['description']}")
                lines.append("")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate llms.txt files")
    parser.add_argument("domain", help="Domain to analyze (e.g., example.com)")
    parser.add_argument("--output", "-o", default="llms.txt", help="Output file")
    parser.add_argument("--from-sitemap", action="store_true", help="Auto-generate from sitemap")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--urls", help="File with URLs (one per line)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    
    args = parser.parse_args()
    
    generator = LLMsTxtGenerator(args.domain, timeout=args.timeout)
    
    # Determine generation method
    if args.interactive:
        content = generator.generate_interactive()
    elif args.urls:
        content = generator.generate_from_file(args.urls)
    else:
        # Default to sitemap mode
        content = generator.generate_from_sitemap()
        if not content:
            print("\nFalling back to interactive mode...", file=sys.stderr)
            content = generator.generate_interactive()
    
    if not content:
        print("Error: Could not generate llms.txt", file=sys.stderr)
        sys.exit(1)
    
    # Output
    if args.format == "json":
        output = {
            "domain": args.domain,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "content": content
        }
        result = json.dumps(output, indent=2)
    else:
        result = content
    
    # Write to file
    with open(args.output, 'w') as f:
        f.write(result)
    
    print(f"\n✅ Generated llms.txt: {args.output}", file=sys.stderr)
    print(f"   Place this file at: https://{args.domain}/llms.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
