#!/usr/bin/env python3
"""
Schema.org Validator
Basic validation for JSON-LD structured data.
Does not require external dependencies; checks structure, required fields, and common pitfalls.
"""

import json
from typing import Dict, Any, List

REQUIRED_FOR_TYPE = {
    "Organization": ["@type", "name"],
    "Person": ["@type", "name"],
    "WebSite": ["@type", "name", "url"],
    "WebPage": ["@type", "name", "url"],
    "Article": ["@type", "headline", "author", "datePublished", "url"],
    "BlogPosting": ["@type", "headline", "author", "datePublished", "url"],
    "Product": ["@type", "name", "description", "brand", "offers"],
    "Event": ["@type", "name", "startDate"],
    "FAQPage": ["@type", "mainEntity"],
    "Recipe": ["@type", "name", "author", "datePublished"],
    "HowTo": ["@type", "name", "url", "step"]
}

def load_jsonld(text: str) -> Dict[str, Any]:
    """Parse JSON-LD string into dict. Raise if invalid."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e.msg} at line {e.lineno}")
    return data

def validate_required_fields(data: Dict[str, Any]) -> List[str]:
    """Check that required fields for the declared @type are present."""
    errors = []
    schema_type = data.get("@type")
    if not schema_type:
        errors.append("Missing @type property")
        return errors
    required = REQUIRED_FOR_TYPE.get(schema_type, [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field '{field}' for @type '{schema_type}'")
    return errors

def validate_context(data: Dict[str, Any]) -> List[str]:
    """Ensure @context is schema.org."""
    errors = []
    context = data.get("@context")
    if not context:
        errors.append("Missing @context; should be 'https://schema.org'")
    elif context != "https://schema.org":
        errors.append(f"Invalid @context: {context}. Should be 'https://schema.org'")
    return errors

def validate_nested_objects(data: Dict[str, Any]) -> List[str]:
    """Basic checks for nested objects that should be dicts with @type."""
    warnings = []
    # Brand in Product
    if data.get("@type") == "Product":
        offers = data.get("offers", {})
        if not isinstance(offers, dict) or not offers.get("@type") == "Offer":
            warnings.append("Product.offers should be an Offer object")
        brand = data.get("brand", {})
        if not isinstance(brand, dict) or not brand.get("@type") == "Brand":
            warnings.append("Product.brand should be a Brand object")
    # author in Article/BlogPosting/Recipe
    if data.get("@type") in ("Article", "BlogPosting", "Recipe"):
        author = data.get("author")
        if isinstance(author, dict):
            if author.get("@type") not in ("Person", "Organization"):
                warnings.append(f"author should be a Person or Organization object, got @type={author.get('@type')}")
        else:
            warnings.append("author should be an object with @type (Person/Organization), not a string")
    return warnings

def validate_dates(data: Dict[str, Any]) -> List[str]:
    """Check that date fields are in ISO 8601 format (basic length check)."""
    warnings = []
    date_fields = ["datePublished", "dateModified", "startDate", "endDate", "prepTime", "cookTime", "totalTime"]
    for field in date_fields:
        if field in data:
            val = data[field]
            if not isinstance(val, str):
                warnings.append(f"{field} should be a string (ISO 8601 date/time)")
            elif not (val.endswith("Z") or ("T" in val and (":" in val or val.endswith("Z")))):
                warnings.append(f"{field} should be ISO 8601 format (e.g., '2025-02-20T10:00:00Z'), got: {val}")
    return warnings

def validate_jsonld(text: str, strict: bool = False) -> Dict[str, Any]:
    """
    Run all validations. Returns dict with 'valid' (bool), 'errors' (list), 'warnings' (list), and optionally 'data'.
    """
    try:
        data = load_jsonld(text)
    except ValueError as e:
        return {"valid": False, "errors": [str(e)], "warnings": [], "data": None}

    errors = []
    errors.extend(validate_context(data))
    errors.extend(validate_required_fields(data))
    warnings = []
    warnings.extend(validate_nested_objects(data))
    warnings.extend(validate_dates(data))

    # If strict mode, treat warnings as errors
    if strict and warnings:
        errors.extend([f"(strict) {w}" for w in warnings])
        warnings = []

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "data": data if len(errors) == 0 else None
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: validate_schema.py <json-file> [--strict]")
        sys.exit(1)
    path = sys.argv[1]
    strict = "--strict" in sys.argv
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    result = validate_jsonld(text, strict=strict)
    print("Validation:", "PASS" if result["valid"] else "FAIL")
    if result["errors"]:
        print("Errors:")
        for e in result["errors"]:
            print(f"  - {e}")
    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print(f"  - {w}")
    if not result["valid"]:
        sys.exit(1)