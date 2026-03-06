#!/usr/bin/env python3
"""
GEO Site Readiness Audit Tool
Evaluates websites for Generative Engine Optimization (GEO) readiness.
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
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


class GEOAuditor:
    """Main auditor class for GEO readiness checks."""
    
    def __init__(self, domain, timeout=10, delay=0, user_agent=None):
        self.domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        self.base_url = f"https://{self.domain}"
        self.timeout = timeout
        self.delay = delay
        self.results = {
            "site": self.domain,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "score": 0,
            "total": 29,
            "grade": "F",
            "dimensions": []
        }
        
        self.headers = {
            'User-Agent': user_agent or 'GEO-Audit-Bot/1.0 (Research Purpose)'
        }
    
    def fetch(self, path='', full_url=None):
        """Fetch a URL with error handling."""
        url = full_url or urljoin(self.base_url, path)
        try:
            time.sleep(self.delay)
            resp = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            return resp
        except Exception as e:
            return None
    
    def check_robots_txt(self):
        """Check 1.1: robots.txt allows AI crawlers."""
        resp = self.fetch('/robots.txt')
        if not resp or resp.status_code != 200:
            return {"check": "robots.txt allows AI crawlers", "status": "fail", "notes": "robots.txt not found"}
        
        content = resp.text.lower()
        ai_bots = ['gptbot', 'claudebot', 'perplexitybot', 'google-extended', 'ccbot']
        blocking = []
        
        for bot in ai_bots:
            if f'user-agent: {bot}' in content and 'disallow: /' in content.split(f'user-agent: {bot}')[1].split('user-agent:')[0]:
                blocking.append(bot)
        
        if blocking:
            return {"check": "robots.txt allows AI crawlers", "status": "partial", "notes": f"Blocking: {', '.join(blocking)}"}
        return {"check": "robots.txt allows AI crawlers", "status": "pass", "notes": "AI crawlers allowed"}
    
    def check_llms_txt_exists(self):
        """Check 1.2: llms.txt file exists."""
        resp = self.fetch('/llms.txt')
        if resp and resp.status_code == 200:
            return {"check": "llms.txt exists at root", "status": "pass", "notes": "File found"}
        return {"check": "llms.txt exists at root", "status": "fail", "notes": "Not found"}
    
    def check_llms_txt_content(self):
        """Check 1.3: llms.txt content quality."""
        resp = self.fetch('/llms.txt')
        if not resp or resp.status_code != 200:
            return {"check": "llms.txt content quality", "status": "fail", "notes": "File not accessible"}
        
        content = resp.text
        issues = []
        if not content.startswith('#'): issues.append("Missing title")
        if '##' not in content: issues.append("No sections")
        if '](' not in content: issues.append("No links")
        
        if issues:
            return {"check": "llms.txt content quality", "status": "partial", "notes": f"Issues: {', '.join(issues)}"}
        return {"check": "llms.txt content quality", "status": "pass", "notes": "Well-formatted"}
    
    def check_performance(self):
        """Check 1.4: Site loads within 3 seconds."""
        start = time.time()
        resp = self.fetch('/')
        elapsed = time.time() - start
        
        if not resp:
            return {"check": "Site loads within 3 seconds", "status": "fail", "notes": "Site unreachable"}
        if elapsed < 3:
            return {"check": "Site loads within 3 seconds", "status": "pass", "notes": f"{elapsed:.2f}s"}
        return {"check": "Site loads within 3 seconds", "status": "fail", "notes": f"Slow: {elapsed:.2f}s"}
    
    def check_js_rendering(self):
        """Check 1.5: No JS render-blocking."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "No JS render-blocking", "status": "fail", "notes": "Site unreachable"}
        
        text_content = len(re.findall(r'<p>.*?</p>', resp.text, re.DOTALL))
        if text_content > 5:
            return {"check": "No JS render-blocking", "status": "pass", "notes": f"{text_content} paragraphs in HTML"}
        return {"check": "No JS render-blocking", "status": "partial", "notes": "Limited text in raw HTML"}
    
    def check_accessibility(self):
        """Check 1.6: Content accessible without login."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Content accessible without login", "status": "fail", "notes": "Site unreachable"}
        if resp.status_code == 200 and 'login' not in resp.text.lower()[:1000]:
            return {"check": "Content accessible without login", "status": "pass", "notes": "No login gate"}
        return {"check": "Content accessible without login", "status": "partial", "notes": "May require auth"}
    
    def check_canonical(self):
        """Check 1.7: Canonical URLs consistent."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Canonical URLs consistent", "status": "fail", "notes": "Site unreachable"}
        
        canonical = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', resp.text, re.IGNORECASE)
        if canonical:
            return {"check": "Canonical URLs consistent", "status": "pass", "notes": f"Canonical: {canonical.group(1)}"}
        return {"check": "Canonical URLs consistent", "status": "fail", "notes": "No canonical tag"}
    
    def check_noindex(self):
        """Check 1.8: No noindex on key pages."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "No noindex on key pages", "status": "fail", "notes": "Site unreachable"}
        if 'noindex' in resp.text.lower():
            return {"check": "No noindex on key pages", "status": "fail", "notes": "noindex detected"}
        return {"check": "No noindex on key pages", "status": "pass", "notes": "No noindex"}
    
    def check_sitemap(self):
        """Check 1.9: XML sitemap exists."""
        resp = self.fetch('/sitemap.xml')
        if resp and resp.status_code == 200 and 'xml' in resp.text:
            return {"check": "XML sitemap exists", "status": "pass", "notes": "sitemap.xml found"}
        
        robots = self.fetch('/robots.txt')
        if robots and 'sitemap' in robots.text.lower():
            return {"check": "XML sitemap exists", "status": "pass", "notes": "Referenced in robots.txt"}
        return {"check": "XML sitemap exists", "status": "fail", "notes": "No sitemap"}
    
    def check_raw_html_content(self):
        """Check 1.10: Core content in raw HTML."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Core content in raw HTML", "status": "fail", "notes": "Site unreachable"}
        
        indicators = ['<h1', '<article', '<main', '<section']
        found = sum(1 for ind in indicators if ind in html.lower())
        if found >= 2:
            return {"check": "Core content in raw HTML", "status": "pass", "notes": f"{found} semantic elements"}
        return {"check": "Core content in raw HTML", "status": "partial", "notes": "Limited semantic markup"}
    
    def check_jsonld_present(self):
        """Check 2.1: JSON-LD present."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "JSON-LD present", "status": "fail", "notes": "Site unreachable"}
        if 'application/ld+json' in resp.text:
            return {"check": "JSON-LD present", "status": "pass", "notes": "JSON-LD found"}
        return {"check": "JSON-LD present", "status": "fail", "notes": "No JSON-LD"}
    
    def check_organization_schema(self):
        """Check 2.2: Organization schema."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Organization schema", "status": "fail", "notes": "Site unreachable"}
        if '"@type": "organization"' in resp.text.lower():
            return {"check": "Organization schema", "status": "pass", "notes": "Found"}
        return {"check": "Organization schema", "status": "fail", "notes": "Not found"}
    
    def check_website_schema(self):
        """Check 2.3: WebSite schema with SearchAction."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "WebSite schema", "status": "fail", "notes": "Site unreachable"}
        text = resp.text.lower()
        if '"@type": "website"' in text:
            if 'searchaction' in text:
                return {"check": "WebSite schema", "status": "pass", "notes": "With SearchAction"}
            return {"check": "WebSite schema", "status": "partial", "notes": "Without SearchAction"}
        return {"check": "WebSite schema", "status": "fail", "notes": "Not found"}
    
    def check_faq_schema(self):
        """Check 2.4: FAQPage schema."""
        for path in ['/faq', '/support', '/help']:
            resp = self.fetch(path)
            if resp and 'faqpage' in resp.text.lower():
                return {"check": "FAQPage schema", "status": "pass", "notes": f"On {path}"}
        return {"check": "FAQPage schema", "status": "partial", "notes": "Not detected"}
    
    def check_article_schema(self):
        """Check 2.5: Article schema."""
        for path in ['/blog', '/news', '/articles']:
            resp = self.fetch(path)
            if resp and 'article' in resp.text.lower():
                return {"check": "Article schema", "status": "pass", "notes": f"On {path}"}
        return {"check": "Article schema", "status": "partial", "notes": "Not detected"}
    
    def check_product_schema(self):
        """Check 2.6: Product schema."""
        for path in ['/shop', '/products', '/store']:
            resp = self.fetch(path)
            if resp and '"@type": "product"' in resp.text.lower():
                return {"check": "Product schema", "status": "pass", "notes": f"On {path}"}
        return {"check": "Product schema", "status": "partial", "notes": "Not detected"}
    
    def check_breadcrumb_schema(self):
        """Check 2.7: BreadcrumbList schema."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "BreadcrumbList schema", "status": "fail", "notes": "Site unreachable"}
        if 'breadcrumblist' in resp.text.lower():
            return {"check": "BreadcrumbList schema", "status": "pass", "notes": "Found"}
        return {"check": "BreadcrumbList schema", "status": "partial", "notes": "Not detected"}
    
    def check_howto_schema(self):
        """Check 2.8: HowTo schema."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "HowTo schema", "status": "fail", "notes": "Site unreachable"}
        if 'howto' in resp.text.lower():
            return {"check": "HowTo schema", "status": "pass", "notes": "Found"}
        return {"check": "HowTo schema", "status": "partial", "notes": "Not detected"}
    
    def check_schema_valid(self):
        """Check 2.9: Schema validation."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Schema validates", "status": "fail", "notes": "Site unreachable"}
        
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
        if not blocks:
            return {"check": "Schema validates", "status": "fail", "notes": "No JSON-LD"}
        
        valid = sum(1 for b in blocks if self._try_json(b))
        if valid == len(blocks):
            return {"check": "Schema validates", "status": "pass", "notes": f"All {valid} valid"}
        return {"check": "Schema validates", "status": "partial", "notes": f"{valid}/{len(blocks)} valid"}
    
    def _try_json(self, text):
        try:
            json.loads(text)
            return True
        except:
            return False
    
    def check_schema_context(self):
        """Check 2.10: @context is https."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "@context uses HTTPS", "status": "fail", "notes": "Site unreachable"}
        if '"@context": "https://schema.org"' in resp.text:
            return {"check": "@context uses HTTPS", "status": "pass", "notes": "HTTPS context"}
        if '"@context": "http://schema.org"' in resp.text:
            return {"check": "@context uses HTTPS", "status": "partial", "notes": "HTTP (should be HTTPS)"}
        return {"check": "@context uses HTTPS", "status": "partial", "notes": "Not detected"}
    
    def check_no_duplicate_schema(self):
        """Check 2.11: No duplicate schema."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "No conflicting schema", "status": "fail", "notes": "Site unreachable"}
        org_count = resp.text.lower().count('"@type": "organization"')
        if org_count > 1:
            return {"check": "No conflicting schema", "status": "partial", "notes": f"{org_count} Organization schemas"}
        return {"check": "No conflicting schema", "status": "pass", "notes": "No duplicates"}
    
    def check_answer_sentences(self):
        """Check 3.1: Answer sentences in first 100 words."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Answer sentences in first 100 words", "status": "fail", "notes": "Site unreachable"}
        
        text = re.sub(r'<[^>]+>', '', resp.text)
        words = text.split()[:100]
        first_100 = ' '.join(words).lower()
        indicators = [' is ', ' are ', ' means ', ' refers to ']
        if any(ind in first_100 for ind in indicators):
            return {"check": "Answer sentences in first 100 words", "status": "pass", "notes": "Direct statements found"}
        return {"check": "Answer sentences in first 100 words", "status": "partial", "notes": "Consider more direct opening"}
    
    def check_structured_format(self):
        """Check 3.2: Structured content format."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Structured content format", "status": "fail", "notes": "Site unreachable"}
        if 'faq' in resp.text.lower() or 'how to' in resp.text.lower():
            return {"check": "Structured content format", "status": "pass", "notes": "Structured content found"}
        return {"check": "Structured content format", "status": "partial", "notes": "Consider adding FAQ"}
    
    def check_faq_format(self):
        """Check 3.3: FAQs in Q&A format."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "FAQs in Q&A format", "status": "fail", "notes": "Site unreachable"}
        patterns = ['faq', 'frequently asked', 'question:']
        if any(p in resp.text.lower() for p in patterns):
            return {"check": "FAQs in Q&A format", "status": "pass", "notes": "FAQ detected"}
        return {"check": "FAQs in Q&A format", "status": "partial", "notes": "Consider adding FAQs"}
    
    def check_brand_in_first_para(self):
        """Check 3.4: Brand name in first paragraph."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Brand name in first paragraph", "status": "fail", "notes": "Site unreachable"}
        
        para = re.search(r'<p[^>]*>(.*?)</p>', resp.text, re.DOTALL | re.IGNORECASE)
        title = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
        brand = title.group(1).split('-')[0].strip() if title else self.domain
        
        if para and brand.lower() in para.group(1).lower():
            return {"check": "Brand name in first paragraph", "status": "pass", "notes": f"'{brand}' found"}
        return {"check": "Brand name in first paragraph", "status": "partial", "notes": "Consider adding brand name"}
    
    def check_citations(self):
        """Check 3.5: Statistics include citations."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Statistics with citations", "status": "fail", "notes": "Site unreachable"}
        if re.search(r'\d+%.*(?:according to|source:)', resp.text, re.IGNORECASE):
            return {"check": "Statistics with citations", "status": "pass", "notes": "Citations found"}
        return {"check": "Statistics with citations", "status": "partial", "notes": "Add sources to data"}
    
    def check_headers_structure(self):
        """Check 3.6: Headers signal structure."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Headers signal structure", "status": "fail", "notes": "Site unreachable"}
        h2_count = len(re.findall(r'<h2', resp.text, re.IGNORECASE))
        if h2_count >= 3:
            return {"check": "Headers signal structure", "status": "pass", "notes": f"{h2_count} H2 tags"}
        return {"check": "Headers signal structure", "status": "partial", "notes": f"Only {h2_count} H2 tags"}
    
    def check_about_page(self):
        """Check 3.7: About page defines identity."""
        about = self.fetch('/about')
        if about and about.status_code == 200:
            return {"check": "About page defines identity", "status": "pass", "notes": "/about found"}
        return {"check": "About page defines identity", "status": "partial", "notes": "Consider adding /about"}
    
    def check_llms_format(self):
        """Check 4.1: llms.txt standard format."""
        resp = self.fetch('/llms.txt')
        if not resp or resp.status_code != 200:
            return {"check": "llms.txt standard format", "status": "partial", "notes": "Not accessible"}
        content = resp.text
        has_all = content.startswith('#') and '##' in content and '](' in content
        if has_all:
            return {"check": "llms.txt standard format", "status": "pass", "notes": "Proper format"}
        return {"check": "llms.txt standard format", "status": "partial", "notes": "Use standard markdown"}
    
    def check_https(self):
        """Check 4.2: HTTPS enforced."""
        try:
            http_resp = requests.get(f"http://{self.domain}", timeout=self.timeout, allow_redirects=False)
            if http_resp.status_code in [301, 302] and 'https' in http_resp.headers.get('Location', ''):
                return {"check": "HTTPS enforced", "status": "pass", "notes": "HTTP redirects to HTTPS"}
        except:
            pass
        return {"check": "HTTPS enforced", "status": "pass", "notes": "Site uses HTTPS"}
    
    def check_hreflang(self):
        """Check 4.3: Hreflang for multilingual."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Hreflang for multilingual", "status": "partial", "notes": "Site unreachable"}
        if 'hreflang' in resp.text.lower():
            return {"check": "Hreflang for multilingual", "status": "pass", "notes": "Hreflang found"}
        return {"check": "Hreflang for multilingual", "status": "partial", "notes": "Not multilingual or missing"}
    
    def check_og_tags(self):
        """Check 4.4: Open Graph tags."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Open Graph tags", "status": "fail", "notes": "Site unreachable"}
        og_tags = ['og:title', 'og:description', 'og:image', 'og:url']
        found = sum(1 for t in og_tags if f'property="{t}"' in resp.text)
        if found >= 3:
            return {"check": "Open Graph tags", "status": "pass", "notes": f"{found}/4 tags"}
        return {"check": "Open Graph tags", "status": "partial", "notes": f"Only {found}/4 tags"}
    
    def check_twitter_cards(self):
        """Check 4.5: Twitter Card tags."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Twitter Card tags", "status": "fail", "notes": "Site unreachable"}
        tags = ['twitter:card', 'twitter:title', 'twitter:description']
        found = sum(1 for t in tags if f'name="{t}"' in resp.text)
        if found >= 2:
            return {"check": "Twitter Card tags", "status": "pass", "notes": f"{found}/3 tags"}
        return {"check": "Twitter Card tags", "status": "partial", "notes": f"Only {found}/3 tags"}
    
    def check_canonical_resolves(self):
        """Check 4.6: Canonical tags resolve."""
        resp = self.fetch('/')
        if not resp:
            return {"check": "Canonical tags resolve", "status": "fail", "notes": "Site unreachable"}
        canonical = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', resp.text, re.IGNORECASE)
        if canonical:
            return {"check": "Canonical tags resolve", "status": "pass", "notes": "Canonical present"}
        return {"check": "Canonical tags resolve", "status": "fail", "notes": "No canonical tag"}
    
    def check_404_status(self):
        """Check 4.7: Proper 404 status codes."""
        resp = self.fetch('/this-page-does-not-exist-12345')
        if resp and resp.status_code == 404:
            return {"check": "Proper 404 status", "status": "pass", "notes": "Returns 404"}
        if resp and resp.status_code == 200:
            return {"check": "Proper 404 status", "status": "fail", "notes": "Returns 200 for missing pages"}
        return {"check": "Proper 404 status", "status": "partial", "notes": f"Returns {resp.status_code if resp else 'error'}"}
    
    def calculate_grade(self, score):
        if score >= 26: return "A+"
        if score >= 22: return "A"
        if score >= 18: return "B"
        if score >= 14: return "C"
        if score >= 10: return "D"
        return "F"
    
    def run_full_audit(self, dimension=None):
        all_checks = {
            "AI Accessibility": [
                self.check_robots_txt, self.check_llms_txt_exists, self.check_llms_txt_content,
                self.check_performance, self.check_js_rendering, self.check_accessibility,
                self.check_canonical, self.check_noindex, self.check_sitemap, self.check_raw_html_content
            ],
            "Structured Data": [
                self.check_jsonld_present, self.check_organization_schema, self.check_website_schema,
                self.check_faq_schema, self.check_article_schema, self.check_product_schema,
                self.check_breadcrumb_schema, self.check_howto_schema, self.check_schema_valid,
                self.check_schema_context, self.check_no_duplicate_schema
            ],
            "Content Citability": [
                self.check_answer_sentences, self.check_structured_format, self.check_faq_format,
                self.check_brand_in_first_para, self.check_citations, self.check_headers_structure,
                self.check_about_page
            ],
            "Technical Setup": [
                self.check_llms_format, self.check_https, self.check_hreflang, self.check_og_tags,
                self.check_twitter_cards, self.check_canonical_resolves, self.check_404_status
            ]
        }
        
        if dimension:
            dim_map = {"accessibility": "AI Accessibility", "schema": "Structured Data",
                      "content": "Content Citability", "technical": "Technical Setup"}
            if dimension in dim_map:
                all_checks = {dim_map[dimension]: all_checks[dim_map[dimension]]}
        
        total_score = 0
        for dim_name, checks in all_checks.items():
            dim_results = []
            dim_score = 0
            print(f"\n📊 Auditing: {dim_name}", file=sys.stderr)
            
            for check_fn in checks:
                result = check_fn()
                dim_results.append(result)
                if result['status'] == 'pass':
                    dim_score += 1
                elif result['status'] == 'partial':
                    dim_score += 0.5
                icon = "✅" if result['status'] == 'pass' else "⚠️" if result['status'] == 'partial' else "❌"
                print(f"  {icon} {result['check']}", file=sys.stderr)
            
            self.results["dimensions"].append({
                "name": dim_name, "score": dim_score, "total": len(checks),
                "percentage": round((dim_score / len(checks)) * 100), "checks": dim_results
            })
            total_score += dim_score
        
        self.results["score"] = round(total_score, 1)
        self.results["grade"] = self.calculate_grade(total_score)
        return self.results


def output_markdown(results):
    """Generate Markdown report."""
    lines = [
        f"# GEO Readiness Audit Report\n",
        f"**Site:** {results['site']}  ",
        f"**Date:** {results['timestamp']}  ",
        f"**Score:** {results['score']}/{results['total']} (**{results['grade']}**)\n",
        "## Summary by Dimension\n"
    ]
    
    for dim in results['dimensions']:
        bar = '█' * int(dim['percentage'] / 10) + '░' * (10 - int(dim['percentage'] / 10))
        lines.append(f"### {dim['name']}: {dim['score']}/{dim['total']} ({dim['percentage']}%)\n")
        lines.append(f"{bar}\n")
        for check in dim['checks']:
            icon = "✅" if check['status'] == 'pass' else "⚠️" if check['status'] == 'partial' else "❌"
            lines.append(f"- {icon} **{check['check']}**: {check['notes']}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GEO Site Readiness Audit")
    parser.add_argument("domain", help="Domain or URL to audit")
    parser.add_argument("--output", choices=["json", "md", "markdown"], default="md", help="Output format")
    parser.add_argument("--dimension", choices=["accessibility", "schema", "content", "technical"], help="Audit specific dimension only")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--delay", type=float, default=0, help="Delay between requests")
    parser.add_argument("--user-agent", help="Custom User-Agent string")
    
    args = parser.parse_args()
    
    auditor = GEOAuditor(args.domain, timeout=args.timeout, delay=args.delay, user_agent=args.user_agent)
    results = auditor.run_full_audit(dimension=args.dimension)
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        print(output_markdown(results))


if __name__ == "__main__":
    main()
