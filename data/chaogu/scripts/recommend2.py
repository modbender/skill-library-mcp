import pandas as pd

# Read CSV
df = pd.read_csv('C:/Users/chenyaoan/Desktop/stock_data.csv')

# Indexes: 1=代码, 2=名称, 3=最新价, 4=涨跌幅, 12=量比, 16=所属行业
col_name = 2
col_code = 1
col_price = 3
col_change = 4
col_volratio = 12
col_sector = 16

keywords = ['科技', '半导体', '芯片', '航天', '航空', '白酒']

print("=" * 70)
print(" RECOMMENDED STOCKS - RELAXED CRITERIA")
print("=" * 70)
print()

# Try multiple criteria sets
criteria_sets = [
    (1.2, 0, 10, "Vol Ratio > 1.2, Change 0-10%"),
    (1.0, 0, 10, "Vol Ratio > 1.0, Change 0-10%"),
]

for min_vol, min_change, max_change, desc in criteria_sets:
    print(f"Criteria: {desc}")
    print("-" * 70)

    recommendations = []
    for idx, row in df.iterrows():
        try:
            sector = str(row.iloc[col_sector])
            vol_ratio = float(row.iloc[col_volratio])
            change = float(row.iloc[col_change])
            price = float(row.iloc[col_price])
            code = str(row.iloc[col_code])
            name = str(row.iloc[col_name])

            if any(kw in sector for kw in keywords):
                if vol_ratio > min_vol and min_change < change < max_change:
                    recommendations.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'change': change,
                        'vol_ratio': vol_ratio,
                        'sector': sector
                    })
        except:
            pass

    recommendations.sort(key=lambda x: x['vol_ratio'], reverse=True)

    if len(recommendations) > 0:
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec['name']} ({rec['code']})")
            print(f"   Price: {rec['price']:.2f}  Change: {rec['change']:+.2f}%  Vol Ratio: {rec['vol_ratio']:.2f}")
            print(f"   Sector: {rec['sector']}")
            print()

        print(f"Total: {len(recommendations)} stocks found")
        print()
    else:
        print("No stocks found with these criteria")
        print()

print("=" * 70)
