import pandas as pd

# Read CSV
df = pd.read_csv('C:/Users/chenyaoan/Desktop/stock_data.csv')

# Get column index for "所属行业" - it's column 18 (index 17)
# Columns: 序号,代码,名称,最新价,涨跌幅,涨跌额,成交量,成交额,振幅,最高,最低,今开,昨收,量比,换手率,市盈率-动态,市净率,总市值,流通市值,涨速,5分钟涨跌,60日涨跌幅,年初至今涨跌幅

print("=" * 70)
print(" USER PREFERRED STOCK RECOMMENDATIONS")
print("=" * 70)
print()

# Keywords to search
keywords = ['科技', '半导体', '芯片', '航天', '航空', '白酒']

# Indexes: 1=代码, 2=名称, 3=最新价, 4=涨跌幅, 12=量比, 16=所属行业
col_name = 2
col_code = 1
col_price = 3
col_change = 4
col_volratio = 12
col_sector = 16

# Criteria: vol ratio > 1.5, change 0-7%
print("Criteria: Vol Ratio > 1.5, Change 0-7%")
print()

# Search and filter
recommendations = []
for idx, row in df.iterrows():
    try:
        sector = str(row.iloc[col_sector])
        vol_ratio = float(row.iloc[col_volratio])
        change = float(row.iloc[col_change])
        price = float(row.iloc[col_price])
        code = str(row.iloc[col_code])
        name = str(row.iloc[col_name])

        # Check if matches keywords
        if any(kw in sector for kw in keywords):
            # Check criteria
            if vol_ratio > 1.5 and 0 < change < 7:
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

# Sort by volume ratio
recommendations.sort(key=lambda x: x['vol_ratio'], reverse=True)

# Show top recommendations
print(f"Found {len(recommendations)} stocks matching criteria:")
print()

if len(recommendations) > 0:
    print("TOP 5 RECOMMENDATIONS:")
    print("-" * 70)
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['name']} ({rec['code']})")
        print(f"   Price: {rec['price']:.2f}  Change: {rec['change']:+.2f}%  Vol Ratio: {rec['vol_ratio']:.2f}")
        print(f"   Sector: {rec['sector']}")
        print()
else:
    print("No stocks match the criteria at this time.")
    print("Suggestion: Lower the volume ratio threshold or wait for market movement.")

print("=" * 70)
