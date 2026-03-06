#!/usr/bin/env python3
"""
Command-line interface for generate_jsonld.py

Usage:
  python generate_jsonld.py Organization --name "Acme" --url "https://acme.com" --logo "https://acme.com/logo.png"
  python generate_jsonld.py Product --name "Widget" --description "Great widget" --brand "Acme" --price 29.99
  python generate_jsonld.py FAQ --q "What is X?" --a "X is..."
"""

import argparse
from generate_jsonld import generate_schema, format_jsonld, SCHEMA_GENERATORS

def main():
    parser = argparse.ArgumentParser(description="Generate schema.org JSON-LD")
    parser.add_argument("type", choices=list(SCHEMA_GENERATORS.keys()), help="Schema type to generate")
    # Generic options; we'll pass all remaining args as kwargs
    parser.add_argument('--name', help='Name field (common)')
    parser.add_argument('--url', help='URL field (common)')
    parser.add_argument('--description', help='Description (common)')
    parser.add_argument('--author', help='Author name (for Article/BlogPosting/Recipe)')
    parser.add_argument('--date', help='datePublished (defaults to now if not provided)')
    parser.add_argument('--image', help='Image URL')
    parser.add_argument('--output', '-o', help='Output file (defaults to stdout)')

    # Type-specific shortcuts
    parser.add_argument('--headline', help='For Article/BlogPosting')
    parser.add_argument('--brand', help='For Product')
    parser.add_argument('--price', type=float, help='Product price')
    parser.add_argument('--currency', default='USD', help='Price currency')
    parser.add_argument('--availability', default='https://schema.org/InStock', help='Offer availability')
    parser.add_argument('--startDate', help='Event start date (ISO 8601)')
    parser.add_argument('--endDate', help='Event end date (optional)')
    parser.add_argument('--location-name', help='Event location name')
    parser.add_argument('--questions-answers', nargs='+', help='For FAQ: pairs of "question:answer"')
    parser.add_argument('--same-as', nargs='*', help='sameAs URLs (for Person/Organization)')

    args = parser.parse_args()

    # Build kwargs
    kwargs = {}
    if args.name: kwargs['name'] = args.name
    if args.url: kwargs['url'] = args.url
    if args.description: kwargs['description'] = args.description
    if args.author: kwargs['author_name'] = args.author
    if args.date: kwargs['date_published'] = args.date
    if args.image: kwargs['image'] = args.image
    if args.same_as: kwargs['same_as'] = args.same_as

    # Handle special cases
    if args.type in ('Article', 'BlogPosting') and args.headline:
        kwargs['headline'] = args.headline
    if args.type == 'Product':
        kwargs['brand'] = args.brand or ''
        kwargs['price'] = args.price
        kwargs['currency'] = args.currency
        kwargs['availability'] = args.availability
    if args.type == 'Event':
        kwargs['start_date'] = args.startDate
        if args.endDate: kwargs['end_date'] = args.endDate
        if args.location_name:
            kwargs['location'] = {'@type': 'Place', 'name': args.location_name}
    if args.type == 'FAQPage' and args.questions_answers:
        pairs = []
        for qa in args.questions_answers:
            if ':' in qa:
                q, a = qa.split(':', 1)
                pairs.append((q.strip(), a.strip()))
            else:
                raise ValueError("FAQ entries must be in 'question: answer' format")
        kwargs['questions_answers'] = pairs
    if args.type == 'Recipe' and args.author:
        kwargs['author'] = args.author
        kwargs['date_published'] = args.date or datetime.utcnow().strftime('%Y-%m-%d')

    # Default dates for article types if not provided
    if args.type in ('Article', 'BlogPosting', 'Recipe') and 'date_published' not in kwargs:
        kwargs['date_published'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        data = generate_schema(args.type, **kwargs)
        output = format_jsonld(data)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Generated {args.type} schema → {args.output}")
        else:
            print(output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        parser.exit(1)

if __name__ == "__main__":
    import sys
    main()