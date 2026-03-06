import akshare as ak
df = ak.stock_zh_a_spot_em()
print(f"Stocks: {len(df)}")
print(df.head(3))
