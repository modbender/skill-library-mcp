import pandas as pd

df = pd.read_csv('C:/Users/chenyaoan/Desktop/stock_data.csv')
sectors = df.iloc[:, 16].dropna().unique()

print("Sample Sectors (first 50):")
for i, s in enumerate(sorted(sectors)[:50], 1):
    print(f"{i}. {s}")

print("\n=== Sectors containing preferred keywords ===")
keywords = ['科技', '半导体', '芯片', '航天', '航空', '白酒']
for kw in keywords:
    matching = [s for s in sectors if kw in str(s)]
    if matching:
        print(f"\n{kw}:")
        for m in matching[:5]:
            print(f"  - {m}")
