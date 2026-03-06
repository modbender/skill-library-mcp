import sys

def project_revenue(initial_revenue, growth_rate, years):
    projections = []
    current = initial_revenue
    for year in range(1, years + 1):
        projections.append((year, current))
        current *= (1 + growth_rate)
    return projections

def project_expenses(initial_expenses, inflation_rate, years):
    projections = []
    current = initial_expenses
    for year in range(1, years + 1):
        projections.append((year, current))
        current *= (1 + inflation_rate)
    return projections

def net_profit(revenue, expenses):
    return [(y, r - e) for (y1, r), (y2, e) in zip(revenue, expenses) if y1 == y2]

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python financial_projection.py <initial_revenue> <growth_rate> <initial_expenses> <inflation_rate> <years>")
        sys.exit(1)
    
    initial_revenue = float(sys.argv[1])
    growth_rate = float(sys.argv[2])
    initial_expenses = float(sys.argv[3])
    inflation_rate = float(sys.argv[4])
    years = int(sys.argv[5])
    
    revenue = project_revenue(initial_revenue, growth_rate, years)
    expenses = project_expenses(initial_expenses, inflation_rate, years)
    profit = net_profit(revenue, expenses)
    
    print("Year | Revenue | Expenses | Profit")
    for y, r in revenue:
        e = next(e for yr, e in expenses if yr == y)
        p = next(p for yp, p in profit if yp == y)
        print(f"{y} | {r:.2f} | {e:.2f} | {p:.2f}")