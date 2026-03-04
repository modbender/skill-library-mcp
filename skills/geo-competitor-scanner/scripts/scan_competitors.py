#!/usr/bin/env python3
"""
Scan competitors for GEO signals.
"""

import argparse
import json
import sys
import time
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: pip install requests beautifulsoup4")
    sys.exit(1)


class GEOScanner:
    """Scan website for GEO signals."""
    
    def __init__(self, domain, timeout=10):
        self.domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        self.base_url = f"https://{self.domain}"
        self.timeout = timeout
        self.results = {
            'domain': self.domain,
            'technical': {},
            'content': {},
            'entity': {},
            'citation': {}
        }
    
    def fetch(self, path=''):
        """Fetch URL."""
        url = urljoin(self.base_url, path)
        try:
            resp = requests.get(url, timeout=self.timeout, allow_redirects=True)
            return resp
        except Exception as e:
            return None
    
    def scan_technical(self):
        """Scan technical GEO infrastructure."""
        print(f"  Scanning technical...", file=sys.stderr)
        
        # llms.txt
        llms = self.fetch('/llms.txt')
        self.results['technical']['llms_txt'] = {
            'exists': llms and llms.status_code == 200,
            'size': len(llms.text) if llms and llms.status_code == 200 else 0
        }
        
        # robots.txt
        robots = self.fetch('/robots.txt')
        robots_text = robots.text.lower() if robots and robots.status_code == 200 else ''
        ai_bots = ['gptbot', 'claudebot', 'perplexitybot', 'google-extended']
        blocking = []
        for bot in ai_bots:
            if f'user-agent: {bot}' in robots_text and 'disallow: /' in robots_text:
                blocking.append(bot)
        
        self.results['technical']['robots_txt'] = {
            'exists': robots and robots.status_code == 200,
            'blocks_ai': len(blocking) > 0,
            'blocked_bots': blocking
        }
        
        # Homepage for schema
        home = self.fetch('/')
        if home:
            schemas = self._extract_schemas(home.text)
            self.results['technical']['schema'] = {
                'types': schemas,
                'count': len(schemas)
            }
            
            # HTTPS check
            self.results['technical']['https'] = home.url.startswith('https://')
        
        # Calculate technical score
        score = 0
        if self.results['technical']['llms_txt']['exists']:
            score += 2
        if self.results['technical']['robots_txt']['exists'] and not self.results['technical']['robots_txt']['blocks_ai']:
            score += 2
        score += min(len(self.results['technical'].get('schema', {}).get('types', [])), 3)
        if self.results['technical'].get('https'):
            score += 1
        
        self.results['technical']['score'] = round(score / 8 * 10, 1)
    
    def _extract_schemas(self, html):
        """Extract schema types from HTML."""
        import re
        schemas = []
        jsonld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(jsonld_pattern, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    for item in data:
                        if '@type' in item:
                            schemas.append(item['@type'])
                elif '@type' in data:
                    schemas.append(data['@type'])
            except:
                pass
        return list(set(schemas))
    
    def scan_content(self):
        """Scan content structure."""
        print(f"  Scanning content...", file=sys.stderr)
        
        home = self.fetch('/')
        if not home:
            return
        
        soup = BeautifulSoup(home.text, 'html.parser')
        
        # Headers
        h2_count = len(soup.find_all('h2'))
        h3_count = len(soup.find_all('h3'))
        self.results['content']['headers'] = {'h2': h2_count, 'h3': h3_count}
        
        # FAQ check (simple keyword)
        faq_mentions = home.text.lower().count('faq') + home.text.lower().count('frequently asked')
        self.results['content']['faq'] = {'mentions': faq_mentions}
        
        # Estimate score
        score = 0
        if h2_count >= 2:
            score += 2
        elif h2_count >= 1:
            score += 1
        if faq_mentions > 0:
            score += 2
        
        self.results['content']['score'] = round(score / 10 * 10, 1)  # Simplified
    
    def scan_entity(self):
        """Scan entity signals."""
        print(f"  Scanning entity...", file=sys.stderr)
        
        home = self.fetch('/')
        if not home:
            return
        
        schemas = self._extract_schemas(home.text)
        has_org = 'Organization' in schemas
        has_website = 'WebSite' in schemas
        
        # About page
        about = self.fetch('/about')
        has_about = about and about.status_code == 200
        
        self.results['entity'] = {
            'organization_schema': has_org,
            'website_schema': has_website,
            'about_page': has_about
        }
        
        score = 0
        if has_org:
            score += 3
        if has_website:
            score += 1
        if has_about:
            score += 2
        
        self.results['entity']['score'] = round(score / 9 * 10, 1)
    
    def scan_citation(self):
        """Scan citation-optimized content."""
        print(f"  Scanning citation...", file=sys.stderr)
        
        # Check for comparison pages
        comp_paths = ['/compare', '/comparison', '/vs', '/alternatives']
        comp_pages = []
        for path in comp_paths:
            resp = self.fetch(path)
            if resp and resp.status_code == 200:
                comp_pages.append(path)
        
        # Check for about/what-is pages
        about = self.fetch('/about')
        whatis = self.fetch('/what-is')
        
        self.results['citation'] = {
            'comparison_pages': comp_pages,
            'about_content': about is not None,
            'definition_content': whatis is not None
        }
        
        score = 0
        if len(comp_pages) > 0:
            score += 2
        if about:
            score += 1
        if whatis:
            score += 1
        
        self.results['citation']['score'] = round(score / 9 * 10, 1)
    
    def run_full_scan(self):
        """Run all scans."""
        print(f"Scanning {self.domain}...", file=sys.stderr)
        self.scan_technical()
        time.sleep(0.5)
        self.scan_content()
        time.sleep(0.5)
        self.scan_entity()
        time.sleep(0.5)
        self.scan_citation()
        
        # Overall score
        scores = [
            self.results['technical'].get('score', 0),
            self.results['content'].get('score', 0),
            self.results['entity'].get('score', 0),
            self.results['citation'].get('score', 0)
        ]
        self.results['overall_score'] = round(sum(scores) / 4, 1)
        
        return self.results


def generate_comparison_report(results_list):
    """Generate comparison report."""
    lines = ["# GEO Competitor Scan Report\n"]
    
    # Matrix
    lines.append("## Competitive Matrix\n")
    lines.append("| Signal | " + " | ".join(r['domain'] for r in results_list) + " |")
    lines.append("|--------|" + "|".join("--------" for _ in results_list) + "|")
    
    signals = [
        ('llms.txt', lambda r: '✅' if r['technical'].get('llms_txt', {}).get('exists') else '❌'),
        ('robots.txt allows AI', lambda r: '✅' if not r['technical'].get('robots_txt', {}).get('blocks_ai') else '❌'),
        ('Organization schema', lambda r: '✅' if r['entity'].get('organization_schema') else '❌'),
        ('FAQ mentions', lambda r: str(r['content'].get('faq', {}).get('mentions', 0))),
        ('Comparison pages', lambda r: str(len(r['citation'].get('comparison_pages', [])))),
    ]
    
    for signal_name, getter in signals:
        values = [getter(r) for r in results_list]
        lines.append(f"| {signal_name} | " + " | ".join(values) + " |")
    
    # Scores
    lines.append("\n## Dimension Scores\n")
    lines.append("| Domain | Technical | Content | Entity | Citation | Overall |")
    lines.append("|--------|-----------|---------|--------|----------|---------|")
    for r in results_list:
        lines.append(f"| {r['domain']} | {r['technical'].get('score', 0)} | {r['content'].get('score', 0)} | {r['entity'].get('score', 0)} | {r['citation'].get('score', 0)} | **{r['overall_score']}** |")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan competitors for GEO")
    parser.add_argument("--brand", required=True, help="Your domain")
    parser.add_argument("--competitors", required=True, help="Comma-separated competitor domains")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    domains = [args.brand] + [c.strip() for c in args.competitors.split(",")]
    
    results = []
    for domain in domains:
        scanner = GEOScanner(domain)
        result = scanner.run_full_scan()
        results.append(result)
        time.sleep(1)
    
    report = generate_comparison_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
