#!/usr/bin/env python3
"""
Validate Schema.org JSON-LD markup.
"""

import argparse
import json
import sys
import re


class SchemaValidator:
    """Validate Schema.org JSON-LD."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self, schema):
        """Run all validations."""
        self._validate_structure(schema)
        self._validate_context(schema)
        self._validate_required_fields(schema)
        self._validate_best_practices(schema)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def _validate_structure(self, schema):
        """Validate basic JSON-LD structure."""
        if not isinstance(schema, dict):
            self.errors.append("Schema must be a JSON object")
            return
        
        if "@context" not in schema:
            self.errors.append("Missing @context field")
        
        if "@type" not in schema and "@graph" not in schema:
            self.errors.append("Missing @type or @graph field")
    
    def _validate_context(self, schema):
        """Validate @context value."""
        context = schema.get("@context", "")
        
        if isinstance(context, str):
            if context == "http://schema.org":
                self.warnings.append("@context uses HTTP (should be HTTPS)")
            elif context != "https://schema.org":
                self.warnings.append(f"Unexpected @context value: {context}")
        elif isinstance(context, dict):
            if "schema.org" not in str(context):
                self.warnings.append("@context may not include schema.org")
    
    def _validate_required_fields(self, schema):
        """Validate required fields for specific types."""
        schema_type = schema.get("@type", "")
        
        if schema_type == "Organization":
            self._check_required(schema, ["name", "url"], "Organization")
            if "logo" not in schema:
                self.warnings.append("Organization should include logo")
        
        elif schema_type == "WebSite":
            self._check_required(schema, ["name", "url"], "WebSite")
        
        elif schema_type in ["Article", "BlogPosting"]:
            self._check_required(schema, ["headline", "author", "datePublished"], schema_type)
            if "publisher" not in schema:
                self.warnings.append(f"{schema_type} should include publisher")
            if "image" not in schema:
                self.warnings.append(f"{schema_type} should include image for rich results")
        
        elif schema_type == "Product":
            self._check_required(schema, ["name"], "Product")
            if "offers" not in schema and "review" not in schema:
                self.errors.append("Product must have offers or review")
            if "offers" in schema:
                self._validate_offer(schema["offers"])
        
        elif schema_type == "FAQPage":
            self._check_required(schema, ["mainEntity"], "FAQPage")
            if "mainEntity" in schema:
                if not isinstance(schema["mainEntity"], list):
                    self.errors.append("FAQPage mainEntity must be an array")
                else:
                    for i, item in enumerate(schema["mainEntity"]):
                        if item.get("@type") != "Question":
                            self.errors.append(f"FAQ item {i+1} must be @type: Question")
                        if "acceptedAnswer" not in item:
                            self.errors.append(f"FAQ item {i+1} missing acceptedAnswer")
        
        elif schema_type == "HowTo":
            self._check_required(schema, ["name", "step"], "HowTo")
        
        elif schema_type == "BreadcrumbList":
            self._check_required(schema, ["itemListElement"], "BreadcrumbList")
            if "itemListElement" in schema:
                for i, item in enumerate(schema["itemListElement"]):
                    if "position" not in item:
                        self.errors.append(f"Breadcrumb item {i+1} missing position")
        
        elif schema_type == "LocalBusiness":
            self._check_required(schema, ["name", "address"], "LocalBusiness")
    
    def _check_required(self, schema, fields, schema_type):
        """Check that required fields are present."""
        for field in fields:
            if field not in schema or not schema[field]:
                self.errors.append(f"{schema_type} missing required field: {field}")
    
    def _validate_offer(self, offer):
        """Validate Offer object."""
        if not isinstance(offer, dict):
            self.errors.append("Product offers must be an object")
            return
        
        if "price" not in offer:
            self.errors.append("Offer missing price")
        elif isinstance(offer.get("price"), str) and not re.match(r'^\d+(\.\d{2})?$', offer["price"]):
            if "$" in offer["price"] or "€" in offer["price"] or "£" in offer["price"]:
                self.errors.append("Price should not include currency symbol")
        
        if "priceCurrency" not in offer:
            self.warnings.append("Offer should specify priceCurrency")
    
    def _validate_best_practices(self, schema):
        """Validate best practices."""
        schema_type = schema.get("@type", "")
        
        # Check for https in URLs
        for key, value in schema.items():
            if isinstance(value, str) and value.startswith("http://"):
                self.warnings.append(f"{key} uses HTTP (consider HTTPS)")
        
        # Check description length
        if "description" in schema:
            desc = schema["description"]
            if len(desc) < 50:
                self.warnings.append("Description is quite short (< 50 chars)")
            if len(desc) > 500:
                self.warnings.append("Description is quite long (> 500 chars)")
        
        # Check for promotional language
        promotional = ['best', 'revolutionary', 'amazing', 'incredible', 'unmatched']
        schema_str = json.dumps(schema).lower()
        found = [p for p in promotional if p in schema_str]
        if found:
            self.warnings.append(f"Promotional language detected: {', '.join(found)}")
        
        # Check for empty values
        self._check_empty_values(schema)
    
    def _check_empty_values(self, data, path=""):
        """Recursively check for empty values."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if value == "" or value == [] or value == {}:
                    self.warnings.append(f"Empty value for: {current_path}")
                elif isinstance(value, (dict, list)):
                    self._check_empty_values(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._check_empty_values(item, f"{path}[{i}]")


def main():
    parser = argparse.ArgumentParser(description="Validate Schema.org JSON-LD")
    parser.add_argument("file", help="JSON file to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    # Load schema
    try:
        with open(args.file, 'r') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    # Validate
    validator = SchemaValidator()
    results = validator.validate(schema)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Validation Results: {args.file}")
    print('='*60)
    
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
    
    print(f"\n{'='*60}")
    
    if results['valid'] and (not args.strict or not results['warnings']):
        print("✅ Schema is valid!")
        print('='*60)
        return 0
    else:
        error_count = len(results['errors'])
        warning_count = len(results['warnings'])
        if args.strict:
            print(f"❌ Found {error_count} error(s) and {warning_count} warning(s) (strict mode)")
        else:
            print(f"❌ Found {error_count} error(s)")
        print('='*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
