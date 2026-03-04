"""Command-line interface for Airbnb Search."""

import argparse
import json
import sys
from .search import search_airbnb, parse_listings


def print_listings(result: dict, format: str = 'table'):
    """Print listings in specified format."""
    listings = result['listings']
    
    if format == 'json':
        print(json.dumps(result, indent=2))
        return
    
    print(f"\n📍 {result['location']}")
    print(f"📊 Found {result['total_count']} total listings\n")
    print("=" * 90)
    
    sorted_listings = sorted(
        [listing for listing in listings if listing['total_price_num']],
        key=lambda x: x['total_price_num']
    )
    
    for listing in sorted_listings:
        name = listing['name'][:50] + '...' if len(listing['name']) > 50 else listing['name']
        rating = f"⭐{listing['rating']}" if listing['rating'] else "No rating"
        superhost = "🏆" if listing['is_superhost'] else ""
        
        print(f"{name} {superhost}")
        print(f"  {listing['bedrooms']}BR/{listing['bathrooms']}BA | {rating} | {listing['reviews_count'] or 0} reviews")
        print(f"  💰 {listing['total_price']} {listing['price_qualifier']}")
        if listing['original_price']:
            print(f"     (was {listing['original_price']})")
        print(f"  🔗 {listing['url']}")
        print()


def main(argv=None):
    """Main entry point for the CLI.
    
    Args:
        argv: Command line arguments. If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(
        description='Search Airbnb listings from the command line',
        prog='airbnb-search'
    )
    parser.add_argument('query', help='Search location (e.g., "Steamboat Springs, CO")')
    parser.add_argument('--checkin', '-i', help='Check-in date (YYYY-MM-DD)')
    parser.add_argument('--checkout', '-o', help='Check-out date (YYYY-MM-DD)')
    parser.add_argument('--min-price', type=int, help='Minimum price')
    parser.add_argument('--max-price', type=int, help='Maximum price')
    parser.add_argument('--min-bedrooms', type=int, help='Minimum bedrooms')
    parser.add_argument('--limit', type=int, default=50, help='Max results (default: 50)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--format', '-f', choices=['table', 'json'], default='table',
                        help='Output format (default: table)')
    
    args = parser.parse_args(argv)
    
    # --json is shorthand for --format json
    if args.json:
        args.format = 'json'
    
    try:
        data = search_airbnb(
            query=args.query,
            checkin=args.checkin,
            checkout=args.checkout,
            min_price=args.min_price,
            max_price=args.max_price,
            min_bedrooms=args.min_bedrooms,
            items_per_page=args.limit,
        )
        result = parse_listings(data)
        print_listings(result, args.format)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
