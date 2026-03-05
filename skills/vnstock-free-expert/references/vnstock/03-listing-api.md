# 03 - Listing API - Tìm Kiếm & Lọc Chứng Khoán

## 📖 Giới Thiệu

Listing API cung cấp các phương thức tìm kiếm, lọc và lấy thông tin về các chứng khoán có sẵn trên thị trường. Dữ liệu bao gồm:

- Danh sách tất cả mã chứng khoán
- Lọc theo sàn giao dịch (HOSE, HNX, UPCOM)
- Lọc theo ngành công nghiệp (ICB)
- Lọc theo chỉ số (VN30, VNMID, VNSML, etc.)
- Futures, Bonds, Warrants, Funds
- Industries & Sector classification

## 🔌 So Sánh Nguồn Dữ Liệu

| Method | KBS | VCI | Ghi Chú |
|--------|-----|-----|---------|
| **all_symbols()** | ✅ | ✅ | Cấu trúc giống nhau |
| **symbols_by_exchange()** | ✅ | ✅ | KBS 6 columns, VCI 7 columns |
| **symbols_by_industries()** | ✅ | ✅ | KBS 3 columns, VCI 10 columns |
| **symbols_by_group()** | ✅ | ✅ | Cả hai đều trả về Series |
| **industries_icb()** | ✅ | ✅ | KBS có thể rỗng, VCI đầy đủ |
| **all_future_indices()** | ✅ | ✅ | Cả hai đều Series |
| **all_government_bonds()** | ✅ | ✅ | Cả hai đều Series |
| **all_covered_warrant()** | ✅ | ✅ | Cả hai đều Series |
| **all_bonds()** | ✅ | ✅ | Cả hai đều Series |
| **all_etf()** | ✅ | ❌ | **KBS độc quyền** |
| **get_supported_groups()**  | ✅ | ❌ | **KBS độc quyền** |
| **all_indices()** | ✅ | ✅ | chung |
| **indices_by_group()** | ✅ | ✅ | chung |

**Tổng số methods:**
- **KBS**: 12 methods
- **VCI**: 13 methods

**Khuyến nghị:**
- **KBS**: Ổn định hơn cho Google Colab/Kaggle
- **VCI**: Dữ liệu đầy đủ hơn, có ICB classification và indices

## 🏗️ Khởi Tạo

```python
from vnstock import Listing

# Khởi tạo Listing adapter
# Hỗ trợ KBS, VCI, MSN
listing = Listing(
    source="vci",           # Nguồn dữ liệu (khuyến nghị)
    random_agent=False      # Sử dụng random user agent
)

# Hoặc với KBS (mới trong v3.4.0)
listing_kbs = Listing(source="kbs")

# ⚠️ TCBS đã deprecated, không nên sử dụng
# listing_tcbs = Listing(source="tcbs")  # DeprecatedWarning sẽ hiện ra
```

## 📋 Các Phương Thức

### 1. all_symbols() - Tất Cả Mã Chứng Khoán

Lấy danh sách tất cả mã chứng khoán.

**Parameters:**

```
- to_df (bool): Trả về DataFrame (default: True)
- lang (str): Ngôn ngữ ('vi' hoặc 'en')
```

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

# Trả về DataFrame
df = listing.all_symbols(to_df=True)
print(f"Shape: {df.shape}")  # (1565, 2)
print(f"Columns: {list(df.columns)}")
print(f"Dtypes:\n{df.dtypes}")
# Output:
# Shape: (1565, 2)
# Columns: ['symbol', 'organ_name']
# Dtypes:
# symbol        object
# organ_name    object
df.head()
# Output với KBS:
#   symbol          organ_name
# 0    DPP  CTCP Dược Đồng Nai
# 1    SDA  CTCP Simco Sông Đà

# Trả về list
symbols = listing.all_symbols(to_df=False)
print(f"Type: {type(symbols)}")  # <class 'list'>
print(f"Length: {len(symbols)}")  # 1565
print(symbols[:10])
# Output: ['DPP', 'SDA', 'SDC', 'SDH', 'SDS', 'SDT', 'SDV', 'SDW', 'SDY', 'SDZ']
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
listing = Listing(source="VCI")

# Trả về DataFrame
df = listing.all_symbols(to_df=True)
print(f"Shape: {df.shape}")  # (1733, 2)
print(f"Columns: {list(df.columns)}")
print(f"Dtypes:\n{df.dtypes}")
# Output:
# Shape: (1733, 2)
# Columns: ['symbol', 'organ_name']
# Dtypes:
# symbol        object
# organ_name    object
df.head()
# Output với VCI:
#   symbol                                         organ_name
# 0    YTC  Công ty Cổ phần Xuất nhập khẩu Y tế Thành phố ...
# 1    YEG                     Công ty Cổ phần Tập đoàn Yeah1

# Trả về list
symbols = listing.all_symbols(to_df=False)
print(f"Length: {len(symbols)}")  # 1733
print(symbols[:10])
# Output: ['YTC', 'YEG', 'YBM', 'YBC', 'XPH', 'XDC', 'XDC1', 'XDA', 'XDA1', 'XDG']
```

### 2. symbols_by_exchange() - Lọc Theo Sàn

Lấy danh sách mã chứng khoán theo sàn giao dịch.

**Parameters:**

```
- exchange (str): Sàn giao dịch
  ├─ 'HOSE': Sở giao dịch Hà Nội (HOSE) - Thị trường chính
  ├─ 'HNX': Sở giao dịch Hà Nội (HNX) - Thị trường phụ
  └─ 'UPCOM': Chứng khoán chưa niêm yết (UPCOM)
- lang (str): Ngôn ngữ ('vi' hoặc 'en')
```

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

# Lấy các mã HOSE
hose_symbols = listing.symbols_by_exchange(exchange="HOSE", to_df=True)
print(f"Shape: {hose_symbols.shape}")  # (1952, 6)
print(f"Columns: {list(hose_symbols.columns)}")
print(f"Dtypes:\n{hose_symbols.dtypes}")
# Output:
# Shape: (1952, 6)
# Columns: ['symbol', 'organ_name', 'en_organ_name', 'exchange', 'type', 'id']
# Dtypes:
# symbol           object
# organ_name       object
# en_organ_name    object
# exchange         object
# type             object
# id                int64
print(hose_symbols[['symbol', 'exchange', 'type']].head())
# Output với KBS:
#   symbol exchange   type  id
# 0    DPP    UPCOM  stock   1
# 1    SDA      HNX  stock   1

# Lấy các mã HNX
hnx_symbols = listing.symbols_by_exchange(exchange="HNX", to_df=True)
print(f"HNX symbols: {len(hnx_symbols)}")

# Lấy các mã UPCOM
upcom_symbols = listing.symbols_by_exchange(exchange="UPCOM", to_df=True)
print(f"UPCOM symbols: {len(upcom_symbols)}")

# Chỉ lấy list symbols
hose_list = listing.symbols_by_exchange(exchange="HOSE", to_df=False)
print(f"Type: {type(hose_list)}")  # <class 'list'>
print(f"First 10: {hose_list[:10]}")
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
listing = Listing(source="VCI")

# Lấy các mã HOSE
hose_symbols = listing.symbols_by_exchange(exchange="HOSE", to_df=True)
print(f"Shape: {hose_symbols.shape}")  # (3210, 7)
print(f"Columns: {list(hose_symbols.columns)}")
print(f"Dtypes:\n{hose_symbols.dtypes}")
# Output:
# Shape: (3210, 7)
# Columns: ['symbol', 'exchange', 'type', 'organ_short_name', 'organ_name', 'product_grp_id', 'icb_code2']
# Dtypes:
# symbol              object
# exchange            object
# type                object
# organ_short_name    object
# organ_name          object
# product_grp_id      object
# icb_code2           object
print(hose_symbols[['symbol', 'exchange', 'type']].head())
# Output với VCI:
#   symbol exchange   type organ_short_name                                         organ_name product_grp_id icb_code2
# 0    YTC    UPCOM  STOCK  XNK Y tế TP.HCM  Công ty Cổ phần Xuất nhập khẩu Y tế Thành phố ...            UPX      4500
# 1    YEG      HSX  STOCK   Tập đoàn Yeah1                     Công ty Cổ phần Tập đoàn Yeah1            STO      5500

# Chỉ lấy list symbols
hose_list = listing.symbols_by_exchange(exchange="HOSE", to_df=False)
print(f"Type: {type(hose_list)}")  # <class 'list'>
print(f"First 10: {hose_list[:10]}")
```

**Kiến Thức Nâng Cao:**

```python
# Đếm mã theo sàn
from collections import Counter

all_df = listing.all_symbols(to_df=True)
exchange_counts = all_df['exchange'].value_counts()
print(exchange_counts)
# Output:
# HOSE     1020
# HNX      140
# UPCOM     80
# Name: exchange, dtype: int64

# So sánh giữa các sàn
hose_df = all_df[all_df['exchange'] == 'HOSE']
hnx_df = all_df[all_df['exchange'] == 'HNX']

print(f"HOSE industries: {hose_df['industry'].nunique()}")
print(f"HNX industries: {hnx_df['industry'].nunique()}")
```

### 3. symbols_by_industries() - Lọc Theo Ngành

Lấy danh sách mã chứng khoán theo ngành công nghiệp.

**Parameters:**

```
- to_df (bool): Trả về DataFrame
- lang (str): Ngôn ngữ
```

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

# Lọc theo ngành cụ thể
banking_df = listing.symbols_by_industries(industry_name='Ngân hàng', to_df=True)
print(f"Total Banking stocks: {len(banking_df)}")
print(banking_df.head())
# Output với KBS:
# Total Banking stocks: 697
#   symbol  industry_code           industry_name
# 0    ABR              6  Công nghệ và thông tin
# 1    ADC              6  Công nghệ và thông tin
# 2    BED              6  Công nghệ và thông tin
# 3    CKV              6  Công nghệ và thông tin
# 4    CMG              6  Công nghệ và thông tin

# Lấy tất cả các ngành (không lọc)
all_industries = listing.symbols_by_industries(to_df=True)
print(f"Total symbols with industry: {len(all_industries)}")
print(all_industries.head())
# Output:
#   symbol  industry_code           industry_name
# 0    MGC              1  Nông nghiệp - lâm nghiệp và thủy sản
# 1    GVT              1  Nông nghiệp - lâm nghiệp và thủy sản
# 2    SWC              1  Nông nghiệp - lâm nghiệp và thủy sản
# 3    SLD              1  Nông nghiệp - lâm nghiệp và thủy sản
# 4    VID              1  Nông nghiệp - lâm nghiệp và thủy sản

# Lấy danh sách các ngành duy nhất
unique_industries = all_industries['industry_name'].unique()
print(f"Total industries: {len(unique_industries)}")
print(f"First 10 industries: {list(unique_industries[:10])}")
# Output: Total industries: 28
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
listing = Listing(source="VCI")

# Lọc theo ngành cụ thể
banking_df = listing.symbols_by_industries(lang='vi', to_df=True)
print(f"Total Banking stocks: {len(banking_df)}")
print(banking_df.head())
# Output với VCI:
# Total Banking stocks: 35
#   symbol                                         organ_name                   icb_name3  ... icb_code2 icb_code3 icb_code4
# 0    STB                      Ngân hàng TMCP Sài Gòn                     Ngân hàng  ...      8000      8350      8353
# 1    TCB                      Ngân hàng TMCP Kỹ thương Việt Nam                 Ngân hàng  ...      8000      8350      8353
# 2    CTG                      Ngân hàng TMCP Công thương Việt Nam                 Ngân hàng  ...      8000      8350      8353

# Lấy tất cả các ngành (không lọc)
all_industries = listing.symbols_by_industries(lang='vi', to_df=True)
print(f"Total symbols with industry: {len(all_industries)}")
print(f"Total industries: {len(all_industries)}")
industries = listing.symbols_by_industries(to_df=True)
unique_industries = industries['industry_name'].unique()
print(f"Total industries: {len(unique_industries)}")
print(unique_industries)

# Top 5 ngành có nhiều mã nhất
industry_counts = industries['industry_name'].value_counts().head(5)
print(industry_counts)
# Output:
# Finance           200
# Technology        150
# Real Estate       120
# ...

# Lấy thông tin chi tiết về các ngành ICB (Industry Classification Benchmark) - chỉ hỗ trợ với VCI.
# Parameters:
# - lang (str): Ngôn ngữ
# Ví dụ (với VCI):
# Top 5 ngành có nhiều mã nhất
top_5 = industry_counts.head(5)
print(top_5)
```

### 4. industries_icb() - Phân Loại ICB

⚠️ **Lưu ý với KBS**: KBS không cung cấp ICB classification. Sử dụng `symbols_by_industries()` để lấy mã theo ngành.

Lấy thông tin chi tiết về các ngành ICB (Industry Classification Benchmark) - chỉ hỗ trợ với VCI.

**Parameters:**

```
- lang (str): Ngôn ngữ
```

**Ví dụ (với VCI):**

```python
# Sử dụng VCI cho ICB
listing_vci = Listing(source="vci")

# Lấy danh sách ICB
icb_df = listing_vci.industries_icb()
print(icb_df.head())
# Output:
#   icb_id  icb_code  icb_name            super_group
# 0  6001    1000     Oil & Gas           Energy
# 1  6002    1001     Coal                Energy
# 2  6003    1010     Alternative Energy Energy
# ...

# Thong tin chi tiet
print(f"Total ICB categories: {len(icb_df)}")
print(f"Columns: {icb_df.columns.tolist()}")

# Tim theo super_group
energy = icb_df[icb_df['super_group'] == 'Energy']
print(f"Energy sectors: {energy['icb_name'].tolist()}")
```

**Lỗi với KBS:**

```python
# ❌ Sẽ gây lỗi với KBS
try:
    icb_df = listing.industries_icb()
except NotImplementedError as e:
    print(f"Lỗi: {e}")
# Output: Lỗi: KBS không cung cấp ICB classification. Sử dụng symbols_by_industries() để lấy mã theo ngành.
```

**Kiến Thức:**

```python
# Lấy danh sách các super_group
super_groups = icb_df['super_group'].unique()
print(f"Total super_groups: {len(super_groups)}")
for group in super_groups:
    sectors = icb_df[icb_df['super_group'] == group]
    print(f"{group}: {len(sectors)} sectors")
```

### 5. symbols_by_group() - Lọc Theo Chỉ Số

Lấy danh sách mã chứng khoán theo chỉ số (Index Group).

**Parameters:**

```
- group (str): Tên chỉ số
  ├─ VN30, VN100, VNMID, VNSML, VNALL, VNSI
  ├─ VNIT, VNIND, VNCONS, VNCOND, VNHEAL, VNENE
  ├─ VNUTI, VNREAL, VNFIN, VNMAT
  ├─ VNDIAMOND, VNFINLEAD, VNFINSELECT
  └─ VNX50, VNXALL
```

**Ví dụ:**

```python
# VN30 - 30 cổ phiếu vốn hóa lớn nhất
vn30 = listing.symbols_by_group(group_name="VN30", to_df=True)
print(f"VN30 symbols: {vn30['symbol'].tolist()}")
# Output với KBS:
# VN30 symbols: ['ACB', 'BCM', 'BID', 'CTG', 'DGC', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG', 
#                'LPB', 'MBB', 'MSN', 'MWG', 'PLX', 'SAB', 'SHB', 'SSB', 'SSI', 'STB', 
#                'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE']
print(f"Total VN30: {len(vn30)}")
# Output: Total VN30: 30

# HNX30 - 30 cổ phiếu trên HNX
hnx30 = listing.symbols_by_group(group_name="HNX30", to_df=True)
print(f"HNX30 symbols: {hnx30['symbol'].tolist()}")
# Output với KBS:
# HNX30 symbols: ['BVS', 'CAP', 'CEO', 'DHT', 'DP3', 'DTD', 'DVM', 'DXP', 'HGM', 'HUT', 
#                 'IDC', 'IDV', 'L14', 'L18', 'LAS', 'LHC', 'MBS', 'NTP', 'PLC', 'PSD', 
#                 'PVB', 'PVC', 'PVI', 'PVS', 'SHS', 'SLS', 'TMB', 'TNG', 'VC3', 'VCS']
print(f"Total HNX30: {len(hnx30)}")
# Output: Total HNX30: 30

# Chỉ lấy list symbols
vn30_list = listing.symbols_by_group(group_name="VN30", to_df=False)
print(f"First 10 VN30: {vn30_list[:10]}")
# Output: First 10 VN30: ['ACB', 'BCM', 'BID', 'CTG', 'DGC', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG']
```

**Kiến Thức Nâng Cao:**

```python
from vnstock.constants import INDEX_GROUPS

# Lấy tất cả chỉ số
all_groups = []
for group_category, indices in INDEX_GROUPS.items():
    print(f"{group_category}: {indices}")
    all_groups.extend(indices)

# Lấy tất cả mã từ VN30 đến VN100
vn30_symbols = set(listing.symbols_by_group(group="VN30"))
vn100_symbols = set(listing.symbols_by_group(group="VN100"))

# Mã ở VN100 nhưng không ở VN30
vn31_to_100 = vn100_symbols - vn30_symbols
print(f"VN31-100 symbols: {sorted(list(vn31_to_100))}")
```

### 6. all_future_indices() - Futures

Lấy danh sách tất cả hợp đồng tương lai.

**Ví dụ:**

```python
# Lấy danh sách futures
futures_df = listing.all_future_indices()
print(futures_df.head())
# Output:
#   symbol  contract_name  maturity_date
# 0   VNI   VN Index Futures  2024-12-31
# 1   VI1   VN30 Dec24        2024-12-31
# ...

print(f"Total futures: {len(futures_df)}")
```

### 7. all_government_bonds() - Trái Phiếu Chính Phủ

Lấy danh sách trái phiếu chính phủ.

**Ví dụ:**

```python
# Lấy danh sách trái phiếu
bonds_df = listing.all_government_bonds()
print(bonds_df.head())
# Output:
#   symbol  bond_name  maturity_date  coupon
# 0  GB01   10Y Bond   2030-01-01     5.5%
# ...
```

### 8. all_covered_warrant() - Warrant

Lấy danh sách warrant được phủ (Covered Warrant).

**Ví dụ:**

```python
# Lấy danh sách warrant
warrants_df = listing.all_covered_warrant()
print(warrants_df[['symbol', 'underlying', 'expiry_date']].head())
```

### 9. all_bonds() - Trái Phiếu Doanh Nghiệp

Lấy danh sách trái phiếu doanh nghiệp.

**Ví dụ:**

```python
# Lấy danh sách corporate bonds
bonds_df = listing.all_bonds()
print(bonds_df[['symbol', 'issuer', 'coupon', 'maturity']].head())
```

## 🔄 Kết Hợp & Lọc Nâng Cao

### Ví dụ 1: Cổ Phiếu Lớn ở Ngành Tài Chính

```python
import pandas as pd
from vnstock import Listing

listing = Listing(source="vci")

# Lấy dữ liệu
all_symbols = listing.all_symbols(to_df=True)
industries = listing.symbols_by_industries(to_df=True)

# Kết hợp dữ liệu
merged = all_symbols.merge(industries, on='symbol', how='left')

# Lọc theo ngành Finance và sàn HOSE
finance_hose = merged[
    (merged['industry'] == 'Finance') & 
    (merged['exchange'] == 'HOSE')
]

print(f"Finance stocks on HOSE: {len(finance_hose)}")
print(finance_hose[['symbol', 'company_name']].head())
```

### Ví dụ 2: So Sánh VN30 vs VN31-100

```python
# Lấy dữ liệu
vn30_set = set(listing.symbols_by_group(group="VN30"))
vn100_set = set(listing.symbols_by_group(group="VN100"))

# VN30
print("VN30 symbols:")
print(sorted(vn30_set))

# VN31-100 (ở VN100 nhưng không ở VN30)
vn31_100 = sorted(vn100_set - vn30_set)
print(f"\nVN31-100 symbols ({len(vn31_100)} stocks):")
print(vn31_100)

# Lấy chi tiết của VN31-100
all_df = listing.all_symbols(to_df=True)
vn31_100_df = all_df[all_df['symbol'].isin(vn31_100)]
print("\nVN31-100 details:")
print(vn31_100_df[['symbol', 'company_name', 'industry']].to_string())
```

### Ví dụ 3: Ngành Công Nghệ

```python
# Lấy tất cả cổ phiếu IT
vnit_symbols = listing.symbols_by_group(group="VNIT")
print(f"IT stocks ({len(vnit_symbols)}): {vnit_symbols}")

# Lấy chi tiết
industries_df = listing.symbols_by_industries(to_df=True)
it_stocks = industries_df[industries_df['symbol'].isin(vnit_symbols)]
print("\nIT stocks details:")
print(it_stocks[['symbol', 'industry_name']].to_string())
```

### Ví dụ 4: Export Danh Sách

```python
# Export VN30
vn30 = listing.symbols_by_group(group="VN30")
with open('vn30_symbols.txt', 'w') as f:
    for symbol in vn30:
        f.write(symbol + '\n')

# Export tất cả cổ phiếu theo ngành
industries = listing.symbols_by_industries(to_df=True)
industries.to_excel('all_stocks_by_industry.xlsx', index=False)

# Export VN100 chi tiết
all_df = listing.all_symbols(to_df=True)
vn100_symbols = listing.symbols_by_group(group="VN100")
vn100_df = all_df[all_df['symbol'].isin(vn100_symbols)]
vn100_df.to_csv('vn100_details.csv', index=False)

print("✅ Exported successfully!")
```

## � Methods Độc Quyền

### 1. get_supported_groups() - Danh Sách Nhóm Hỗ Trợ (Chỉ KBS)

Lấy danh sách tất cả các nhóm được hỗ trợ bởi KBS.

**Ví dụ:**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

# Lấy danh sách nhóm hỗ trợ
supported_groups = listing.get_supported_groups()
print(f"Shape: {supported_groups.shape}")  # (16, 4)
print(f"Columns: {list(supported_groups.columns)}")
print(f"Dtypes:\n{supported_groups.dtypes}")
# Output:
# Shape: (16, 4)
# Columns: ['group_name', 'group_code', 'category', 'description']
# Dtypes:
# group_name     object
# group_code     object
# category       object
# description    object
print(supported_groups[['group_name', 'category']].head())
```

**Output với KBS:**
```
  group_name       category
0       BOND     Trái phiếu
1         CW    Chứng quyền
2        ETF        ETF/Quỹ
3   FU_INDEX      Phái sinh
4        HNX  Sàn giao dịch
```

### 2. all_indices() - Tất Cả Chỉ Số (Hỗ trợ từ tất cả sources qua `Listing`)

Lấy danh sách tất cả các chỉ số tiêu chuẩn hóa với thông tin đầy đủ. Trước đây chỉ có trên VCI, từ phiên bản 3.4.1 hàm này đã được chuẩn hoá và có thể gọi từ bất kỳ adapter nào thông qua `Listing(source=...)`. Kết quả trả về là `pd.DataFrame` với các cột tiêu chuẩn: [`symbol`, `name`, `description`, `full_name`, `group`, `index_id`, `sector_id`] (nếu có).

**Ví dụ (VCI):**
```python
# Khởi tạo với VCI
listing = Listing(source="VCI")

all_indices_vci = listing.all_indices()
print(f"Shape: {all_indices_vci.shape}")
print(all_indices_vci[['symbol', 'name', 'group']].head())
```

**Ví dụ (KBS):**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

all_indices_kbs = listing.all_indices()
print(f"Shape: {all_indices_kbs.shape}")
print(all_indices_kbs[['symbol', 'name', 'group']].head())
```

**Lưu ý:**
- Một số provider có thể không có đầy đủ `sector_id` hoặc metadata giống VCI; hàm sẽ trả về những chỉ số sẵn có và giữ định dạng chuẩn để thuận tiện cho phân tích.

### 3. indices_by_group() - Chỉ Số Theo Nhóm (Hỗ trợ từ tất cả sources qua `Listing`)

Lấy danh sách chỉ số theo nhóm tiêu chuẩn hóa (ví dụ: các chỉ số HOSE, chỉ số ngành/sector). Hàm này hiện đã hỗ trợ gọi từ `Listing` với mọi `source` (ví dụ: `kbs`, `vci`, `msn`) và trả về dữ liệu đã được chuẩn hoá.

**Tham số:**
- `group` (str): Tên nhóm (VD: `'HOSE'`, `'Sector Indices'`, ...)

**Ví dụ (HOSE từ KBS):**
```python
# Khởi tạo với KBS
listing = Listing(source="KBS")

indices = listing.indices_by_group(group="HOSE")
if indices is not None:
    print(f"Shape: {indices.shape}")
    print(indices[['symbol', 'name']].head())
else:
    print("Không có dữ liệu cho nhóm này")
```

**Ví dụ (HOSE từ VCI):**
```python
# Khởi tạo với VCI
listing = Listing(source="VCI")

indices = listing.indices_by_group(group="HOSE")
print(indices[['symbol', 'name']].head())
```

**Lưu ý:**
- Một số source có thể cung cấp các nhóm khác nhau; nếu không có dữ liệu cho `group` truyền vào, hàm có thể trả về `None`.

## �📊 Performance & Caching

### Caching Dữ Liệu

```python
import pickle
import os
from vnstock import Listing

listing = Listing(source="vci")

CACHE_FILE = 'listing_cache.pkl'

# Lấy hoặc load từ cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        all_symbols = pickle.load(f)
    print("✅ Loaded from cache")
else:
    all_symbols = listing.all_symbols(to_df=True)
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(all_symbols, f)
    print("✅ Cached for next time")

print(all_symbols.head())
```

### Batch Operations

```python
# Lấy dữ liệu một lần, dùng nhiều lần
all_symbols = listing.all_symbols(to_df=True)
industries = listing.symbols_by_industries(to_df=True)
icb = listing.industries_icb()

# Lọc theo nhiều tiêu chí
hose_df = all_symbols[all_symbols['exchange'] == 'HOSE']
print(f"HOSE: {len(hose_df)}")

finance_df = hose_df[hose_df['industry'] == 'Finance']
print(f"HOSE Finance: {len(finance_df)}")
```

## ❌ Các Lỗi Thường Gặp

### Lỗi 1: ValueError - Invalid Source

```python
# ❌ Sai
listing = Listing(source="invalid")

# ✅ Đúng - KBS (khuyến nghị), VCI, MSN
listing = Listing(source="kbs")  # Nguồn mới, ổn định
listing = Listing(source="vci")  # Nguồn truyền thống
listing = Listing(source="msn")  # Nguồn dữ liệu quốc tế, crypto

# ⚠️ TCBS đã deprecated
# listing = Listing(source="tcbs")  # DeprecatedWarning
```

### Lỗi 2: NotImplementedError - ICB với KBS

```python
# ❌ KBS không hỗ trợ ICB
try:
    icb_df = listing.industries_icb()
except NotImplementedError as e:
    print(f"Lỗi: {e}")
    # Solution: Sử dụng symbols_by_industries() thay thế
    industries = listing.symbols_by_industries()
```

### Lỗi 3: Network/Timeout

```python
# Tăng timeout
from vnstock.config import Config
Config.TIMEOUT = 60

# Hoặc retry
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def get_symbols():
    return listing.all_symbols()
```

### Lỗi 4: Empty Result

```python
# Nếu không có dữ liệu
symbols = listing.symbols_by_group(group_name="INVALID_INDEX")
if not symbols or len(symbols) == 0:
    print("⚠️ No symbols found for this group")
```

## 📚 Bước Tiếp Theo

1. [02-Installation](02-installation.md) - Cài đặt
2. [01-Overview](01-overview.md) - Tổng quan
3. ✅ **03-Listing API** - Bạn đã ở đây
4. [04-Quote & Price](04-quote-price-api.md) - Giá lịch sử
5. [05-Financial API](05-financial-api.md) - Dữ liệu tài chính
6. [06-Connector Guide](06-connector-guide.md) - API bên ngoài
7. [07-Best Practices](07-best-practices.md) - Mẹo & kinh nghiệm

---

**Last Updated**: 2024-12-17  
**Version**: 3.4.0  
**Status**: Actively Maintained  
**Important**: KBS là nguồn dữ liệu mới được khuyến nghị, ổn định hơn VCI cho Google Colab/Kaggle
