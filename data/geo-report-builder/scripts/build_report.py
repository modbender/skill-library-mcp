#!/usr/bin/env python3
"""
Build GEO performance report.
"""

import argparse
import json

def build_report(data):
    return f"""# GEO Performance Report

## Executive Summary

- AIGVR Score: {data.get('aigvr', 0)}/100
- AI Mentions: {data.get('mentions', 0)}
- Share of Model: {data.get('som', 0)}%
- Sentiment: {data.get('sentiment', 0)}/10

## Platform Breakdown

| Platform | AIGVR | Trend |
|----------|-------|-------|
| ChatGPT | {data.get('chatgpt', 0)} | ↑ |
| Perplexity | {data.get('perplexity', 0)} | → |

## Action Plan

1. [Priority action]
2. [Secondary action]
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="JSON file with metrics")
    args = parser.parse_args()
    
    with open(args.data) as f:
        data = json.load(f)
    
    report = build_report(data)
    print(report)

if __name__ == "__main__":
    main()
