import akshare as ak
import pandas as pd

# Fetch and save to CSV
df = ak.stock_zh_a_spot_em()
df.to_csv('C:/Users/chenyaoan/Desktop/stock_data.csv', index=False, encoding='utf-8-sig')
print(f"Saved {len(df)} stocks to CSV")

# Show top 10
print("\nTOP 10 GAINERS:")
top10 = df.sort_values('涨跌幅', ascending=False).head(10)
print(top10[['代码', '名称', '最新价', '涨跌幅', '量比']].to_string(index=False))

# Filter by user criteria
keywords = ['科技', '半导体', '芯片', '航天', '航空', '白酒']
print("\n=== PREFERRED SECTORS ===")
for kw in keywords:
    matching = df[df['所属行业'].str.contains(kw, na=False)]
    if len(matching) > 0:
        # Filter: vol > 1.5, change 0-7%
        filtered = matching[
            (matching['量比'] > 1.5) &
            (matching['涨跌幅'] > 0) &
            (matching['涨跌幅'] < 7)
        ].sort_values('量比', ascending=False)
        if len(filtered) > 0:
            print(f"\n{kw}:")
            print(filtered[['代码', '名称', '最新价', '涨跌幅', '量比', '所属行业']].head(3).to_string(index=False))
