import pandas as pd

df = pd.read_csv('C:/Users/chenyaoan/Desktop/stock_data.csv')

print("=" * 70)
print(" STOCK RECOMMENDATIONS - BY NAME/KEYWORDS")
print("=" * 70)
print()

# Search by name instead of sector
keywords = ['科技', '半导体', '芯片', '航天', '航空', '白酒', '电子', '通信', '光电', '智能']

# Indexes: 1=代码, 2=名称, 3=最新价, 4=涨跌幅, 12=量比
col_code = 1
col_name = 2
col_price = 3
col_change = 4
col_volratio = 12

print("Searching by stock name/keywords...")
print()

# Find all stocks matching keywords
matching_stocks = []
for idx, row in df.iterrows():
    try:
        name = str(row.iloc[col_name])
        if any(kw in name for kw in keywords):
            matching_stocks.append(row)
    except:
        pass

print(f"Found {len(matching_stocks)} stocks matching keywords")
print()

# Filter by criteria
for min_vol, desc in [(1.5, "High Activity (Vol Ratio > 1.5)"), (1.2, "Moderate Activity (Vol Ratio > 1.2)")]:
    print(f"=== {desc}, Change 0-10% ===")
    print("-" * 70)

    recommendations = []
    for row in matching_stocks:
        try:
            vol_ratio = float(row.iloc[col_volratio])
            change = float(row.iloc[col_change])
            price = float(row.iloc[col_price])
            code = str(row.iloc[col_code])
            name = str(row.iloc[col_name])

            if 0 < change < 10 and vol_ratio > min_vol:
                recommendations.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'change': change,
                    'vol_ratio': vol_ratio
                })
        except:
            pass

    recommendations.sort(key=lambda x: x['vol_ratio'], reverse=True)

    if len(recommendations) > 0:
        for i, rec in enumerate(recommendations[:8], 1):
            print(f"{i}. {rec['name']} ({rec['code']})")
            print(f"   Price: {rec['price']:.2f}  Change: {rec['change']:+.2f}%  Vol Ratio: {rec['vol_ratio']:.2f}")
            print()
    else:
        print("No stocks found")
        print()

print("=" * 70)
