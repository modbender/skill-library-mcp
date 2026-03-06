#!/usr/bin/env python3
import sys
import json

def calculate_revenue(strategy, users, price, conv=0.8, churn=0.1, costs=0.2):
    monthly_gross = users * price * conv
    annual_gross = monthly_gross * 12
    annual_net = annual_gross * (1 - churn) * (1 - costs)
    return {
        'strategy': strategy,
        'monthly_gross': round(monthly_gross, 2),
        'annual_gross': round(annual_gross, 2),
        'annual_net': round(annual_net, 2),
        'break_even_users': round(price * conv * 12 * (1 - costs) / price, 0)  # Simplified
    }

if __name__ == '__main__':
    data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {'strategy':2, 'users':100, 'price':10}
    result = calculate_revenue(**data)
    print(json.dumps(result, indent=2))
