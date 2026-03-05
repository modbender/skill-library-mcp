#!/usr/bin/env python3
"""
JSON-LD Schema Generator
Generates schema.org structured data for common website elements.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

def generate_organization(name: str, url: str, logo: Optional[str] = None, same_as: list = None) -> Dict[str, Any]:
    """Generate Organization schema."""
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url
    }
    if logo:
        org["logo"] = logo
    if same_as:
        org["sameAs"] = same_as  # e.g., social media profiles
    return org

def generate_person(name: str, url: Optional[str] = None, job_title: Optional[str] = None, same_as: list = None) -> Dict[str, Any]:
    """Generate Person schema."""
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name
    }
    if url:
        person["url"] = url
    if job_title:
        person["jobTitle"] = job_title
    if same_as:
        person["sameAs"] = same_as
    return person

def generate_website(name: str, url: str, search_action_url: Optional[str] = None) -> Dict[str, Any]:
    """Generate WebSite schema (site-wide, includes potential search action)."""
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": url
    }
    if search_action_url:
        website["potentialAction"] = {
            "@type": "SearchAction",
            "target": f"{search_action_url}?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    return website

def generate_webpage(title: str, url: str, description: Optional[str] = None, date_published: Optional[str] = None, date_modified: Optional[str] = None) -> Dict[str, Any]:
    """Generate generic WebPage schema."""
    page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": url
    }
    if description:
        page["description"] = description
    if date_published:
        page["datePublished"] = date_published
    if date_modified:
        page["dateModified"] = date_modified
    return page

def generate_article(headline: str, url: str, author: Dict[str, Any], date_published: str, image: Optional[str] = None, publisher: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Generate Article or BlogPosting schema."""
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "author": author,
        "datePublished": date_published,
        "url": url
    }
    if image:
        article["image"] = image
    if publisher:
        article["publisher"] = publisher
    if description:
        article["description"] = description
    return article

def generate_blog_posting(headline: str, url: str, author_name: str, date_published: str, **kwargs) -> Dict[str, Any]:
    """Generate BlogPosting (specialized Article)."""
    bp = generate_article(headline, url, {"@type": "Person", "name": author_name}, date_published, **kwargs)
    bp["@type"] = "BlogPosting"
    return bp

def generate_product(name: str, description: str, brand: str, price: float, currency: str = "USD", availability: str = "https://schema.org/InStock", sku: Optional[str] = None, image: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """Generate Product schema."""
    product = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "description": description,
        "brand": {"@type": "Brand", "name": brand},
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": currency,
            "availability": availability
        }
    }
    if sku:
        product["sku"] = sku
    if image:
        product["image"] = image
    if url:
        product["url"] = url
    return product

def generate_event(name: str, start_date: str, end_date: Optional[str] = None, location: Optional[Dict[str, Any]] = None, organizer: Optional[Dict[str, Any]] = None, description: Optional[str] = None, event_status: Optional[str] = None, image: Optional[str] = None) -> Dict[str, Any]:
    """Generate Event schema."""
    event = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": name,
        "startDate": start_date
    }
    if end_date:
        event["endDate"] = end_date
    if location:
        event["location"] = location
    if organizer:
        event["organizer"] = organizer
    if description:
        event["description"] = description
    if event_status:
        event["eventStatus"] = event_status
    if image:
        event["image"] = image
    return event

def generate_faq(questions_answers: list) -> Dict[str, Any]:
    """Generate FAQPage schema from list of (question, answer) tuples."""
    main_entities = []
    for q, a in questions_answers:
        main_entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entities
    }

def generate_recipe(name: str, url: str, author: str, date_published: str, description: str, prep_time: Optional[str] = None, cook_time: Optional[str] = None, total_time: Optional[str] = None, ingredients: list = None, instructions: list = None, recipe_ingredient: list = None, recipe_instructions: list = None, image: Optional[str] = None) -> Dict[str, Any]:
    """Generate Recipe schema."""
    recipe = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": name,
        "url": url,
        "author": {"@type": "Person", "name": author},
        "datePublished": date_published,
        "description": description
    }
    if prep_time:
        recipe["prepTime"] = prep_time  # ISO 8601 duration e.g., "PT30M"
    if cook_time:
        recipe["cookTime"] = cook_time
    if total_time:
        recipe["totalTime"] = total_time
    if ingredients:
        recipe["recipeIngredient"] = ingredients  # list of ingredient strings
    if instructions:
        recipe["recipeInstructions"] = instructions  # list of step objects or strings
    if recipe_ingredient:
        recipe["recipeIngredient"] = recipe_ingredient
    if recipe_instructions:
        recipe["recipeInstructions"] = recipe_instructions
    if image:
        recipe["image"] = image
    return recipe

def generate_how_to(name: str, url: str, step_list: list, total_time: Optional[str] = None, estimated_cost: Optional[str] = None, supply: list = None, tool: list = None) -> Dict[str, Any]:
    """Generate HowTo schema."""
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "url": url,
        "step": step_list  # list of {"@type": "HowToStep", "name": "...", "text": "..."}
    }
    if total_time:
        howto["totalTime"] = total_time
    if estimated_cost:
        howto["estimatedCost"] = estimated_cost
    if supply:
        howto["supply"] = supply
    if tool:
        howto["tool"] = tool
    return howto

# Registry of available generators
SCHEMA_GENERATORS = {
    "Organization": generate_organization,
    "Person": generate_person,
    "WebSite": generate_website,
    "WebPage": generate_webpage,
    "Article": generate_article,
    "BlogPosting": generate_blog_posting,
    "Product": generate_product,
    "Event": generate_event,
    "FAQPage": generate_faq,
    "Recipe": generate_recipe,
    "HowTo": generate_how_to
}

def generate_schema(schema_type: str, **kwargs) -> Dict[str, Any]:
    """Entry point: generate schema.org JSON-LD for given type."""
    if schema_type not in SCHEMA_GENERATORS:
        raise ValueError(f"Unsupported schema type: {schema_type}. Supported: {list(SCHEMA_GENERATORS.keys())}")
    return SCHEMA_GENERATORS[schema_type](**kwargs)

def format_jsonld(data: Dict[str, Any]) -> str:
    """Return formatted JSON-LD string for HTML embedding."""
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    # Example usage
    example = generate_organization(
        name="Acme Corp",
        url="https://acme.example.com",
        logo="https://acme.example.com/logo.png",
        same_as=["https://twitter.com/acme"]
    )
    print(format_jsonld(example))