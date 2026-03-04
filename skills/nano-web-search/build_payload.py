#!/usr/bin/env python3
"""Build JSON payload for search.sh with proper escaping."""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description='Build search payload')
    parser.add_argument('--query', required=True)
    parser.add_argument('--provider', default='linkup')
    parser.add_argument('--depth', default='standard')
    parser.add_argument('--output-type', dest='output_type', default='searchResults')
    parser.add_argument('--from-date', dest='from_date')
    parser.add_argument('--to-date', dest='to_date')
    parser.add_argument('--include-domains', dest='include_domains')
    parser.add_argument('--exclude-domains', dest='exclude_domains')
    parser.add_argument('--max-results', dest='max_results', type=int)
    
    args = parser.parse_args()
    
    payload = {
        "query": args.query,
        "provider": args.provider,
        "depth": args.depth,
        "outputType": args.output_type,
    }
    
    if args.from_date:
        payload["fromDate"] = args.from_date
    if args.to_date:
        payload["toDate"] = args.to_date
    if args.include_domains:
        payload["includeDomains"] = [d.strip() for d in args.include_domains.split(',')]
    if args.exclude_domains:
        payload["excludeDomains"] = [d.strip() for d in args.exclude_domains.split(',')]
    if args.max_results:
        payload["maxResults"] = args.max_results
    
    # json.dumps properly escapes all special characters
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
