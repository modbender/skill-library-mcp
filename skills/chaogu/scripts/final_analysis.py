import akshare as ak
import pandas as pd
from datetime import datetime

# Fetch data
print("Fetching A-share data...")
df = ak.stock_zh_a_spot_em()
print(f"Total stocks: {len(df)}")

# Sort by change percentage
df_sorted = df.sort_values('涨跌幅', ascending=False)

# Top 10 gainers
print("\n=== TOP 10 GAINERS ===")
top10 = df_sorted.head(10)
print(top10[['代码', '名称', '最新价', '涨跌幅', '涨跌额', '量比']].to_string(index=False))

# Volume ratio > 2
print("\n=== STOCKS WITH VOLUME RATIO > 2 ===")
vol_high = df[df['量比'] > 2].sort_values('量比', ascending=False).head(10)
print(vol_high[['代码', '名称', '最新价', '涨跌幅', '量比']].to_string(index=False))

# User preferred sectors
print("\n=== USER PREFERRED SECTORS ===")
keywords = ['科技', '白酒', '航天', '半导体', '芯片', '航空']
for keyword in keywords:
    matching = df[df['所属行业'].str.contains(keyword, na=False)]
    if len(matching) > 0:
        top_in_sector = matching.nlargest(5, '涨跌幅')
        print(f"\n{keyword} ({len(matching)} stocks):")
        print(top_in_sector[['代码', '名称', '最新价', '涨跌幅', '量比']].to_string(index=False))

# Filter for user preferences
print("\n=== RECOMMENDATIONS ===")
print("Criteria: Preferred sector, Vol Ratio > 1.5, Change 0-7%")

recommended = []
for keyword in keywords:
    sector_stocks = df[df['所属行业'].str.contains(keyword, na=False)]
    if len(sector_stocks) > 0:
        # Filter by conditions
        filtered = sector_stocks[
            (sector_stocks['量比'] > 1.5) &
            (sector_stocks['涨跌幅'] > 0) &
            (sector_stocks['涨跌幅'] < 7)
        ].sort_values('量比', ascending=False).head(3)

        if len(filtered) > 0:
            for _, stock in filtered.iterrows():
                recommended.append(stock)

# Show top recommendations
if recommended:
    rec_df = pd.DataFrame(recommended)
    rec_df = rec_df.sort_values('量比', ascending=False).head(5)
    print(rec_df[['代码', '名称', '最新价', '涨跌幅', '量比', '所属行业']].to_string(index=False))
else:
    print("No stocks meet criteria at this time")

# Sector average
print("\n=== SECTOR AVERAGE RETURNS (Top 10) ===")
sector_avg = df.groupby('所属行业')['涨跌幅'].mean().sort_values(ascending=False).head(10)
print(sector_avg.to_string())

print("\n=== DONE ===")
