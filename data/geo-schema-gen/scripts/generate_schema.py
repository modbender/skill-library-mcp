#!/usr/bin/env python3
"""
Generate Schema.org JSON-LD markup.
"""

import argparse
import json
import sys
from datetime import datetime


SCHEMA_TEMPLATES = {
    "Organization": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "",
        "url": "",
        "logo": "",
        "description": "",
        "sameAs": []
    },
    "WebSite": {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "",
        "url": "",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "",
            "query-input": "required name=search_term_string"
        }
    },
    "Article": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "",
        "description": "",
        "author": {
            "@type": "Person",
            "name": ""
        },
        "publisher": {
            "@type": "Organization",
            "name": "",
            "logo": {
                "@type": "ImageObject",
                "url": ""
            }
        },
        "datePublished": "",
        "dateModified": "",
        "url": ""
    },
    "BlogPosting": {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": "",
        "description": "",
        "author": {
            "@type": "Person",
            "name": ""
        },
        "publisher": {
            "@type": "Organization",
            "name": "",
            "logo": {
                "@type": "ImageObject",
                "url": ""
            }
        },
        "datePublished": "",
        "dateModified": "",
        "url": ""
    },
    "FAQPage": {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    },
    "Product": {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "",
        "description": "",
        "brand": {
            "@type": "Brand",
            "name": ""
        },
        "offers": {
            "@type": "Offer",
            "price": "",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        }
    },
    "HowTo": {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "",
        "description": "",
        "totalTime": "",
        "step": []
    },
    "BreadcrumbList": {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    },
    "VideoObject": {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": "",
        "description": "",
        "thumbnailUrl": "",
        "uploadDate": "",
        "duration": ""
    },
    "LocalBusiness": {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "",
            "addressLocality": "",
            "addressRegion": "",
            "postalCode": "",
            "addressCountry": ""
        },
        "telephone": "",
        "openingHours": ""
    }
}


class SchemaGenerator:
    """Generate Schema.org JSON-LD markup."""
    
    def __init__(self):
        self.data = {}
    
    def generate_interactive(self, schema_type):
        """Generate schema through interactive prompts."""
        print(f"\n=== Generating {schema_type} Schema ===\n", file=sys.stderr)
        
        template = SCHEMA_TEMPLATES.get(schema_type, {}).copy()
        if not template:
            print(f"Error: Unknown schema type '{schema_type}'", file=sys.stderr)
            return None
        
        # Common fields
        if schema_type in ["Organization", "WebSite"]:
            template["name"] = input("Organization/Site name: ").strip()
            template["url"] = input("Website URL (https://...): ").strip()
        
        if schema_type == "Organization":
            template["logo"] = input("Logo URL: ").strip()
            template["description"] = input("Description (1-2 sentences): ").strip()
            social = input("Social media URLs (comma-separated): ").strip()
            if social:
                template["sameAs"] = [s.strip() for s in social.split(",")]
        
        if schema_type == "WebSite":
            search_url = input("Site search URL pattern (use {search_term_string}): ").strip()
            if search_url:
                template["potentialAction"]["target"] = search_url
            else:
                del template["potentialAction"]
        
        if schema_type in ["Article", "BlogPosting"]:
            template["headline"] = input("Article headline: ").strip()
            template["description"] = input("Description (150 chars): ").strip()
            template["author"]["name"] = input("Author name: ").strip()
            template["publisher"]["name"] = input("Publisher name: ").strip()
            template["publisher"]["logo"]["url"] = input("Publisher logo URL: ").strip()
            template["url"] = input("Article URL: ").strip()
            template["datePublished"] = datetime.now().strftime("%Y-%m-%d")
            template["dateModified"] = template["datePublished"]
        
        if schema_type == "FAQPage":
            print("\nEnter FAQ pairs (blank question to finish):")
            while True:
                question = input("\nQuestion: ").strip()
                if not question:
                    break
                answer = input("Answer: ").strip()
                template["mainEntity"].append({
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": answer
                    }
                })
        
        if schema_type == "Product":
            template["name"] = input("Product name: ").strip()
            template["description"] = input("Description: ").strip()
            template["brand"]["name"] = input("Brand name: ").strip()
            template["offers"]["price"] = input("Price (numbers only): ").strip()
            currency = input("Currency (default USD): ").strip()
            if currency:
                template["offers"]["priceCurrency"] = currency
        
        if schema_type == "HowTo":
            template["name"] = input("HowTo title: ").strip()
            template["description"] = input("Description: ").strip()
            duration = input("Total time (e.g., PT30M): ").strip()
            if duration:
                template["totalTime"] = duration
            print("\nEnter steps (blank name to finish):")
            step_num = 1
            while True:
                name = input(f"Step {step_num} name: ").strip()
                if not name:
                    break
                text = input(f"Step {step_num} instructions: ").strip()
                template["step"].append({
                    "@type": "HowToStep",
                    "name": name,
                    "text": text
                })
                step_num += 1
        
        if schema_type == "BreadcrumbList":
            print("\nEnter breadcrumbs (blank name to finish):")
            position = 1
            while True:
                name = input(f"Level {position} name: ").strip()
                if not name:
                    break
                url = input(f"Level {position} URL: ").strip()
                template["itemListElement"].append({
                    "@type": "ListItem",
                    "position": position,
                    "name": name,
                    "item": url
                })
                position += 1
        
        if schema_type == "LocalBusiness":
            subtype = input("Business subtype (e.g., Restaurant, Store, Dentist): ").strip()
            if subtype:
                template["@type"] = subtype
            template["name"] = input("Business name: ").strip()
            template["address"]["streetAddress"] = input("Street address: ").strip()
            template["address"]["addressLocality"] = input("City: ").strip()
            template["address"]["addressRegion"] = input("State/Region: ").strip()
            template["address"]["postalCode"] = input("Postal code: ").strip()
            template["telephone"] = input("Phone number: ").strip()
            hours = input("Opening hours (e.g., Mo-Fr 09:00-17:00): ").strip()
            if hours:
                template["openingHours"] = hours
        
        return template
    
    def generate_from_file(self, filepath):
        """Generate schema from JSON input file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        schema_type = data.get("@type") or data.get("type")
        if not schema_type:
            print("Error: Input file must specify @type", file=sys.stderr)
            return None
        
        template = SCHEMA_TEMPLATES.get(schema_type, {}).copy()
        if not template:
            # Use input data as-is if type not in templates
            return data
        
        # Merge input data with template
        self._deep_merge(template, data)
        return template
    
    def _deep_merge(self, base, overlay):
        """Deep merge two dictionaries."""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def auto_generate(self, schema_type, url):
        """Auto-generate schema by extracting from URL."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            template = SCHEMA_TEMPLATES.get(schema_type, {}).copy()
            
            if schema_type in ["Article", "BlogPosting"]:
                # Extract title
                title = soup.find('h1') or soup.title
                if title:
                    template["headline"] = title.get_text(strip=True)
                
                # Extract description
                meta = soup.find('meta', attrs={'name': 'description'}) or \
                       soup.find('meta', attrs={'property': 'og:description'})
                if meta:
                    template["description"] = meta.get('content', '')
                
                # Extract author
                author = soup.find('meta', attrs={'name': 'author'})
                if author:
                    template["author"]["name"] = author.get('content', '')
                
                template["url"] = url
                template["datePublished"] = datetime.now().strftime("%Y-%m-%d")
            
            if schema_type == "Organization":
                title = soup.title.get_text(strip=True) if soup.title else ""
                template["name"] = title.split('-')[0].split('|')[0].strip()
                template["url"] = url
                
                meta = soup.find('meta', attrs={'name': 'description'})
                if meta:
                    template["description"] = meta.get('content', '')
            
            return template
            
        except Exception as e:
            print(f"Error extracting from URL: {e}", file=sys.stderr)
            return None


def output_html(schema):
    """Wrap schema in HTML script tag."""
    json_str = json.dumps(schema, indent=2)
    return f"""<script type="application/ld+json">
{json_str}
</script>"""


def main():
    parser = argparse.ArgumentParser(description="Generate Schema.org JSON-LD")
    parser.add_argument("--type", required=True, 
                       choices=["Organization", "WebSite", "Article", "BlogPosting", 
                               "FAQPage", "Product", "HowTo", "BreadcrumbList", 
                               "VideoObject", "LocalBusiness"],
                       help="Schema type to generate")
    parser.add_argument("--url", help="URL to auto-extract data from")
    parser.add_argument("--file", help="JSON file with input data")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--output", "-o", choices=["json", "html", "markdown"], default="json",
                       help="Output format")
    parser.add_argument("--pretty", "-p", action="store_true", default=True, help="Pretty print JSON")
    
    args = parser.parse_args()
    
    generator = SchemaGenerator()
    
    # Determine generation method
    if args.interactive:
        schema = generator.generate_interactive(args.type)
    elif args.file:
        schema = generator.generate_from_file(args.file)
    elif args.url:
        schema = generator.auto_generate(args.type, args.url)
    else:
        # Default to interactive
        schema = generator.generate_interactive(args.type)
    
    if not schema:
        sys.exit(1)
    
    # Output
    if args.output == "html":
        result = output_html(schema)
    elif args.output == "markdown":
        json_str = json.dumps(schema, indent=2)
        result = f"## {args.type} Schema\n\n```json\n{json_str}\n```\n\n**Implementation:** Paste inside `<head>` tag\n\n**Validation:** Test at https://validator.schema.org"
    else:
        result = json.dumps(schema, indent=2 if args.pretty else None)
    
    print(result)


if __name__ == "__main__":
    main()
