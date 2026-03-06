#!/usr/bin/env python3
"""ROI Calculator for CRO decision-making.
Evaluates proposed activities against revenue impact."""

import sys
import json

def calculate_roi(cost, reach, conversion_rate, avg_deal_size, timeframe_months=3):
    """Calculate ROI for a proposed activity."""
    expected_conversions = reach * conversion_rate
    expected_revenue = expected_conversions * avg_deal_size
    roi = ((expected_revenue - cost) / cost) * 100 if cost > 0 else 0
    monthly_revenue = expected_revenue / timeframe_months if timeframe_months > 0 else 0
    payback_months = cost / monthly_revenue if monthly_revenue > 0 else float('inf')
    
    return {
        "cost": cost,
        "reach": reach,
        "conversion_rate": f"{conversion_rate*100:.1f}%",
        "avg_deal_size": avg_deal_size,
        "expected_conversions": round(expected_conversions, 1),
        "expected_revenue": round(expected_revenue, 2),
        "roi_percent": round(roi, 1),
        "payback_months": round(payback_months, 1),
        "verdict": "GO" if roi >= 300 else "REVIEW" if roi >= 100 else "PASS",
        "reasoning": (
            "Strong ROI, execute immediately" if roi >= 300
            else "Moderate ROI, consider strategic value" if roi >= 100
            else "Weak ROI, deprioritize unless strategically critical"
        )
    }

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: roi_calculator.py <cost> <reach> <conversion_rate> <avg_deal_size> [timeframe_months]")
        print("Example: roi_calculator.py 500 10000 0.02 1500 3")
        sys.exit(1)
    
    cost = float(sys.argv[1])
    reach = float(sys.argv[2])
    conversion_rate = float(sys.argv[3])
    avg_deal_size = float(sys.argv[4])
    timeframe = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    
    result = calculate_roi(cost, reach, conversion_rate, avg_deal_size, timeframe)
    print(json.dumps(result, indent=2))
