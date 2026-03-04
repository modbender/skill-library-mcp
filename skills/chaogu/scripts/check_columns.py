import akshare as ak
df = ak.stock_zh_a_spot_em()
print("Columns:")
for i, col in enumerate(df.columns):
    print(f"{i}: {repr(col)}")
