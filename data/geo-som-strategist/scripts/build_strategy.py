#!/usr/bin/env python3
"""
Build Share of Model strategy.
"""

import argparse

def build_strategy(brand, category, current_som, target_som):
    gap = target_som - current_som
    return {
        "brand": brand,
        "category": category,
        "current": current_som,
        "target": target_som,
        "gap": gap,
        "actions": [
            f"Create content for {category} prompts",
            f"Build comparison pages vs competitors",
            f"Add FAQ schema to top pages",
            f"Publish original research on {category}",
        ]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--current", type=int, required=True)
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args()
    
    strategy = build_strategy(args.brand, args.category, args.current, args.target)
    print(f"Strategy for {strategy['brand']}")
    print(f"Current SoM: {strategy['current']}% → Target: {strategy['target']}%")
    print(f"Gap to close: {strategy['gap']} percentage points")
    print("\n90-Day Actions:")
    for i, action in enumerate(strategy['actions'], 1):
        print(f"{i}. {action}")

if __name__ == "__main__":
    main()
