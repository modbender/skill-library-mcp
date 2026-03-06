#!/usr/bin/env python3
"""
Validate llms.txt files against quality criteria.
"""

import argparse
import re
import sys
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: pip install requests")
    sys.exit(1)


class LLMsTxtValidator:
    """Validate llms.txt files."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.errors = []
        self.warnings = []
        self.info = []
        
        with open(filepath, 'r') as f:
            self.content = f.read()
    
    def validate(self):
        """Run all validations."""
        self._check_structure()
        self._check_brand_section()
        self._check_links()
        self._check_quality()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def _check_structure(self):
        """Check markdown structure."""
        # Must start with H1
        if not self.content.strip().startswith('# '):
            self.errors.append("File must start with '# Brand Name' (H1 heading)")
        
        # Should have sections (H2)
        h2_count = len(re.findall(r'^## ', self.content, re.MULTILINE))
        if h2_count < 2:
            self.warnings.append(f"Only {h2_count} section(s) found. Consider adding more sections for better organization.")
        else:
            self.info.append(f"Found {h2_count} sections")
        
        # Check for proper markdown
        lines = self.content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.startswith('-') and '[' in line and '](' not in line:
                self.warnings.append(f"Line {i}: Possible malformed link")
    
    def _check_brand_section(self):
        """Check brand description section."""
        # Look for tagline (blockquote)
        if '> ' not in self.content[:500]:
            self.warnings.append("No tagline found. Consider adding a one-sentence description after the brand name.")
        
        # Check for promotional language
        promotional = ['best', 'revolutionary', 'amazing', 'incredible', 'unmatched', 'ultimate']
        content_lower = self.content.lower()
        found_promo = [p for p in promotional if p in content_lower]
        if found_promo:
            self.warnings.append(f"Promotional language detected: {', '.join(found_promo)}. Consider more factual descriptions.")
        
        # Check overview length
        lines = self.content.split('\n')
        overview_lines = []
        in_overview = False
        for line in lines:
            if line.startswith('> '):
                in_overview = True
                continue
            if in_overview:
                if line.startswith('#') or line.startswith('- ['):
                    break
                if line.strip():
                    overview_lines.append(line)
        
        if len(overview_lines) < 2:
            self.warnings.append("Brand overview seems short. Consider adding 2-3 paragraphs.")
        elif len(overview_lines) > 10:
            self.warnings.append("Brand overview is quite long. Consider condensing to 2-3 paragraphs.")
    
    def _check_links(self):
        """Check link format and count."""
        # Extract all links
        link_pattern = r'- \[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, self.content)
        
        self.info.append(f"Found {len(links)} links")
        
        # Check link count
        if len(links) < 10:
            self.warnings.append(f"Only {len(links)} links. Consider adding more (15-40 recommended).")
        elif len(links) > 50:
            self.warnings.append(f"{len(links)} links is a lot. Consider curating to 15-40 most important pages.")
        
        # Check for duplicates
        urls = [url for _, url in links]
        duplicates = set([u for u in urls if urls.count(u) > 1])
        if duplicates:
            self.errors.append(f"Duplicate URLs found: {', '.join(duplicates)}")
        
        # Check URL format
        for title, url in links:
            if not url.startswith('http://') and not url.startswith('https://'):
                self.errors.append(f"URL must use http(s):// : {url}")
            
            if title == url:
                self.warnings.append(f"Link text is the URL. Use descriptive titles: {url}")
        
        # Check descriptions
        desc_pattern = r'- \[[^\]]+\]\([^)]+\): (.+)'
        descriptions = re.findall(desc_pattern, self.content)
        
        for desc in descriptions:
            words = desc.split()
            if len(words) < 3:
                self.warnings.append(f"Description too short: '{desc}'")
            if len(words) > 20:
                self.warnings.append(f"Description too long ({len(words)} words): '{desc[:50]}...'")
    
    def _check_quality(self):
        """Check content quality."""
        # Check for vague descriptions
        vague = ['click here', 'learn more', 'read more', 'our page', 'this page', 'information about']
        content_lower = self.content.lower()
        
        for v in vague:
            if v in content_lower:
                self.warnings.append(f"Vague phrase found: '{v}'. Use specific descriptions instead.")
    
    def check_live_urls(self, sample_size=5):
        """Check that URLs are accessible (sample)."""
        link_pattern = r'- \[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, self.content)
        
        if not links:
            return
        
        print(f"\nChecking {min(sample_size, len(links))} URLs...", file=sys.stderr)
        
        import random
        sample = random.sample(links, min(sample_size, len(links)))
        
        broken = []
        for title, url in sample:
            try:
                resp = requests.head(url, timeout=10, allow_redirects=True)
                if resp.status_code != 200:
                    broken.append((url, resp.status_code))
            except Exception as e:
                broken.append((url, str(e)))
        
        if broken:
            self.warnings.append(f"Some URLs may be broken (checked sample of {len(sample)}):")
            for url, status in broken:
                self.warnings.append(f"  - {url}: {status}")


def main():
    parser = argparse.ArgumentParser(description="Validate llms.txt files")
    parser.add_argument("filepath", help="Path to llms.txt file")
    parser.add_argument("--check-urls", action="store_true", help="Check if URLs are accessible")
    parser.add_argument("--sample-size", type=int, default=5, help="Number of URLs to check")
    
    args = parser.parse_args()
    
    validator = LLMsTxtValidator(args.filepath)
    results = validator.validate()
    
    if args.check_urls:
        validator.check_live_urls(args.sample_size)
    
    # Print results
    print(f"\n{'='*50}")
    print(f"Validation Results: {args.filepath}")
    print('='*50)
    
    if results['info']:
        print("\n📋 Info:")
        for info in results['info']:
            print(f"  • {info}")
    
    if results['warnings']:
        print("\n⚠️  Warnings:")
        for warning in results['warnings']:
            print(f"  • {warning}")
    
    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"  • {error}")
    
    print(f"\n{'='*50}")
    if results['valid']:
        print("✅ File is valid!")
    else:
        print(f"❌ Found {len(results['errors'])} error(s)")
    print('='*50)
    
    return 0 if results['valid'] else 1


if __name__ == "__main__":
    sys.exit(main())
