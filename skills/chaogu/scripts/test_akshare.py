import akshare as ak
df = ak.stock_zh_a_spot_em()
print(f"Total stocks: {len(df)}")
print(df.head(3)[['代码', '名称', '最新价', '涨跌幅', '量比', '所属行业']].to_string())
