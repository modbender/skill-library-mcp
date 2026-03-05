#!/usr/bin/env python3
"""
Audit brand sentiment for AI search.
"""

import argparse

def audit_sentiment(content):
    """Simple sentiment audit."""
    positive_signals = [
        "Clear value proposition" in content,
        "customer" in content.lower(),
        "result" in content.lower(),
    ]
    
    negative_signals = [
        "leverage" in content.lower(),
        "delve" in content.lower(),
        "best" in content.lower() and "tool" in content.lower(),
    ]
    
    return {
        "positive": sum(positive_signals),
        "negative": sum(negative_signals),
        "score": 5 + positive_signals.count(True) - negative_signals.count(True)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    args = parser.parse_args()
    
    result = audit_sentiment(args.content)
    print(f"Sentiment Score: {result['score']}/10")
    print(f"Positive signals: {result['positive']}")
    print(f"Negative signals: {result['negative']}")

if __name__ == "__main__":
    main()
