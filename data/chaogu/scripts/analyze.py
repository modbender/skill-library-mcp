import akshare as ak
import pandas as pd
from datetime import datetime

# Get current time
now = datetime.now()

print("=" * 70)
print(" STOCK ANALYSIS REPORT")
print("=" * 70)
print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Fetch A-share data
print("Fetching A-share market data...")
df = ak.stock_zh_a_spot_em()
print(f"Total stocks: {len(df)}")
print()

# Show first few rows to understand column names
print("Column names:")
print(df.columns.tolist())
print()

# Display top 10 gainers
print("Top 10 Gainers:")
print("=" * 70)
df_sorted = df.sort_values('涨跌幅', ascending=False).head(10)
print(df_sorted[['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '量比']].to_string(index=False))
print()

# Filter by volume ratio
print("Stocks with Volume Ratio > 2:")
print("=" * 70)
df_volume = df[df['量比'] > 2].sort_values('量比', ascending=False).head(10)
print(df_volume[['代码', '名称', '最新价', '涨跌幅', '量比']].to_string(index=False))
print()

# Filter by user preferences (Tech, Baijiu, Aerospace)
print("User Preferred Sectors:")
print("=" * 70)
keywords = ['科技', '白酒', '航天', '半导体', '芯片']
for keyword in keywords:
    matching = df[df['所属行业'].str.contains(keyword, na=False)]
    if len(matching) > 0:
        avg_change = matching['涨跌幅'].mean()
        top_stock = matching.nlargest(1, '涨跌幅')
        print(f"{keyword}: {len(matching)} stocks, Avg change: {avg_change:+.2f}%")
        print(f"  Top: {top_stock['名称'].values[0]} ({top_stock['代码'].values[0]}) {top_stock['涨跌幅'].values[0]:+.2f}%")
print()

# Sector analysis
print("Sector Average Returns (Top 10):")
print("=" * 70)
sector_avg = df.groupby('所属行业')['涨跌幅'].mean().sort_values(ascending=False).head(10)
for idx, (sector, avg) in enumerate(sector_avg.items(), 1):
    print(f"{idx:2d}. {sector:20s} {avg:+6.2f}%")

print()
print("=" * 70)
print("Analysis Complete")
print("=" * 70)
