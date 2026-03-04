# 07 - Financial API - Dữ Liệu Tài Chính

## 📖 Giới Thiệu

Financial API cung cấp các phương thức lấy dữ liệu tài chính doanh nghiệp, bao gồm:

- **Báo cáo tài chính**: Bảng cân đối kế toán, Khoản lợi nhập, Lưu chuyển tiền tệ
- **Chỉ số tài chính**: ROE, ROA, EPS, P/E, Debt ratio, v.v.
- **Chu kỳ báo cáo**: Hàng quý (Quarter) hoặc hàng năm (Year)
- **Phân tích**: Xu hướng tài chính, so sánh ngành

## 🔌 So Sánh Nguồn Dữ Liệu

| Method                 | KBS | VCI | Ghi Chú                         |
| ---------------------- | --- | --- | ------------------------------- |
| **income_statement()** | ✅  | ✅  | KBS: 90 items, VCI: 25+ columns |
| **balance_sheet()**    | ✅  | ✅  | KBS: 162 items, VCI: 36 columns |
| **cash_flow()**        | ✅  | ✅  | KBS: 159 items, VCI: 39 columns |
| **ratio()**            | ✅  | ✅  | KBS: 27 ratios, VCI: 37+ ratios |

**Tổng số methods:**

- **KBS**: 4 methods
- **VCI**: 4 methods

**Khuyến nghị:**

- **KBS**: Dữ liệu chi tiết theo dòng (item-based), phù hợp phân tích chuyên sâu
- **VCI**: Dữ liệu theo cột (column-based), dễ sử dụng và tích hợp

## 🏗️ Khởi Tạo

### KBS Finance (Khuyến nghị)

```python
from vnstock import Finance

# Khởi tạo với KBS
finance_kbs = Finance(
    source="kbs",           # Nguồn dữ liệu
    symbol="VCI",            # Mã chứng khoán
    standardize_columns=True,  # Chuẩn hóa tên cột
    random_agent=False      # Sử dụng random user agent
)

# Khởi tạo với VCI
finance_vci = Finance(
    source="vci",            # Nguồn dữ liệu
    symbol="VCI",            # Mã chứng khoán
    period="quarter",        # Chu kỳ mặc định
    get_all=True,            # Lấy tất cả các trường
    show_log=False           # Hiển thị log
)
```

**Các tham số:**

- `symbol` (str): Mã chứng khoán (VD: 'VCI', 'ACB')
- `standardize_columns` (bool): Chuẩn hóa tên cột theo schema. Mặc định: True
- `random_agent` (bool): Sử dụng random user agent. Mặc định: False
- `show_log` (bool): Hiển thị log debug. Mặc định: False
- `proxy_mode` (str): Chế độ proxy. Mặc định: None
    - `'try'`: Thử proxy, nếu fail thì dùng direct
    - `'rotate'`: Xoay vòng proxy trong danh sách
    - `'random'`: Chọn proxy ngẫu nhiên
    - `'single'`: Dùng proxy đầu tiên
- `proxy_list` (list): Danh sách URL proxy. Mặc định: None

## 📊 Cấu Trúc Dữ Liệu So Sánh

### KBS Data Structure

**Format:** Item-based (dòng-based)

- **Shape**: (N items, 10 columns)
- **Index**: Không có index name
- **Columns tiêu chuẩn**:

  ```
  ['item', 'item_en', 'item_id', 'unit', 'levels', 'row_number', 
   '2025-Q3', '2025-Q2', '2025-Q1', '2024-Q4']
  ```
- **Đặc điểm**:
    - Mỗi dòng là một chỉ tiêu tài chính
    - Các cột thời gian là các quý/ năm
    - Có cả tên tiếng Việt và tiếng Anh
    - Có hierarchical levels

### VCI Data Structure

**Format:** Column-based (cột-based)

- **Shape**: (51 periods, N columns)
- **Index**: Không có index name
- **Columns tiêu chuẩn**:

  ```
  ['ticker', 'yearReport', 'lengthReport', ...financial_fields...]
  ```
- **Đặc điểm**:
    - Mỗi dòng là một kỳ báo cáo
    - Các cột là các chỉ tiêu tài chính
    - Tên cột theo tiếng Anh có đơn vị
    - MultiIndex cho ratios

## 📚 Phương Thức Chính

### Field Display Mode

Từ phiên bản v3.4.0+, tất cả các phương thức báo cáo tài chính hỗ trợ `display_mode` parameter để kiểm soát cách hiển thị các trường dữ liệu:

| Mode                    | Tên             | Mô Tả                                        | Columns                         |
| ----------------------- | --------------- | -------------------------------------------- | ------------------------------- |
| `FieldDisplayMode.STD`  | Standardized    | Chỉ hiển thị 'item' và 'item_id' (chuẩn hóa) | item, item_id, periods          |
| `FieldDisplayMode.ALL`  | All Fields      | Hiển thị tất cả: item (VN), item_en, item_id | item, item_en, item_id, periods |
| `FieldDisplayMode.AUTO` | Auto Convert    | Tự động chuyển đổi dựa trên loại dữ liệu     | item, item_en, item_id, periods |
| `'vi'`                  | Vietnamese Only | Chỉ tiếng Việt (backward compatible)         | item, item_id, periods          |
| `'en'`                  | English Only    | Chỉ tiếng Anh (backward compatible)          | item_en, item_id, periods       |

**Ví dụ sử dụng display_mode:**

```python
from vnstock import Finance
from vnstock.explorer.kbs.financial import FieldDisplayMode

finance = Finance(symbol="VCI")

# Mode 1: Standardized (mặc định) - Chỉ item tiếng Việt + item_id
df_std = finance.income_statement(
    period="quarter",
    display_mode=FieldDisplayMode.STD
)
print(df_std.columns)
# ['item', 'item_id', 'unit', 'levels', 'row_number', '2025-Q3', '2025-Q2', ...]

# Mode 2: All Fields - Hiển thị cả item (VN), item_en, item_id
df_all = finance.income_statement(
    period="quarter",
    display_mode=FieldDisplayMode.ALL
)
print(df_all.columns)
# ['item', 'item_en', 'item_id', 'unit', 'levels', 'row_number', '2025-Q3', '2025-Q2', ...]

# Mode 3: Auto Convert - Tự động chuyển đổi
df_auto = finance.income_statement(
    period="quarter",
    display_mode=FieldDisplayMode.AUTO
)

# Mode 4: chỉ Tiếng Việt chỉ (backward compatible)
df_vi = finance.income_statement(
    period="quarter",
    display_mode='vi'
)

# Mode 5: chỉ Tiếng Anh (backward compatible)
df_en = finance.income_statement(
    period="quarter",
    display_mode='en'
)
```

### 1. income_statement() - Báo Cáo Kết Quả Kinh Doanh

Lấy dữ liệu báo cáo kết quả hoạt động kinh doanh.

**KBS:**

```python
finance = Finance(source="kbs", symbol="VCI")
df = finance.income_statement(period="quarter")

print(f"Shape: {df.shape}")  # (90, 10)
print(f"Columns: {list(df.columns)}")
# ['item', 'item_id', 'unit', 'levels', 'row_number', 
#  '2025-Q3', '2025-Q2', '2025-Q1', '2024-Q4']

# Lấy dữ liệu năm
df_year = finance.income_statement(period="year")
print(f"Shape: {df_year.shape}")  # (90, years_available)

# Lấy với tất cả các trường (item VN, item_en, item_id)
df_all = finance.income_statement(
    period="quarter",
    display_mode="all"  # hoặc FieldDisplayMode.ALL
)

# Xem các chỉ tiêu chính
print(df[df['levels'] == 1][['item', 'item_id', '2025-Q3']].head())
```

**Output KBS:**

```
Shape: (90, 10)
     item item_id  2025-Q3
0  Doanh thu      revenue    1200.5
1  Lợi nhuận gộp  gross_profit   450.2
2  Lợi nhuận hoạt động  operating_profit   180.3
3  Lợi nhuận trước thuế  profit_before_tax   165.1
4  Lợi nhuận sau thuế  net_profit   132.4
```

### 2. balance_sheet() - Bảng Cân Đối Kế Toán

Lấy dữ liệu bảng cân đối kế toán.

**KBS:**

```python
from vnstock import Finance

finance = Finance(symbol="VCI")

# Lấy dữ liệu quý
df = finance.balance_sheet(period="quarter")
print(f"Shape: {df.shape}")  # (162, 10)

# Lấy các chỉ tiêu quan trọng
key_items = ['Tổng tài sản', 'Tài sản ngắn hạn', 'Vốn chủ sở hữu', 'Nợ phải trả']
print(df[df['item'].isin(key_items)][['item', 'item_id', '2025-Q3']])

# Lấy dữ liệu năm
df_year = finance.balance_sheet(period="year")
```

**KBS Output:**

```
                item        item_id  2025-Q3
0         Tổng tài sản      total_assets   50000
1      Tài sản ngắn hạn  current_assets   25000
2      Vốn chủ sở hữu    owner_equity   15000
3        Nợ phải trả        liabilities   35000
```

### 3. cash_flow() - Báo Cáo Lưu Chuyển Tiền Tệ

Lấy dữ liệu báo cáo lưu chuyển tiền tệ.

**KBS:**

```python
from vnstock import Finance

finance = Finance(symbol="VCI")

# Lấy dữ liệu quý
df = finance.cash_flow(period="quarter")
print(f"Shape: {df.shape}")  # (159, 10)

# Các dòng tiền quan trọng
cash_items = ['Lưu chuyển tiền từ hoạt động', 'Lưu chuyển tiền từ đầu tư', 
              'Lưu chuyển tiền từ tài chính', 'Thay đổi tiền mặt']
print(df[df['item'].isin(cash_items)][['item', 'item_id', '2025-Q3']])

# Lấy dữ liệu năm
df_year = finance.cash_flow(period="year")
```

**KBS Output:**

```
                  item          item_id  2025-Q3
0  Lưu chuyển từ hoạt động  cash_from_operations   8000
1  Lưu chuyển từ đầu tư    cash_from_investing   -2000
2  Lưu chuyển từ tài chính   cash_from_financing   1000
3  Thay đổi tiền mặt       net_cash_change       7000
```

### 4. ratio() - Chỉ Số Tài Chính

Lấy các chỉ số tài chính quan trọng.

**KBS:**

```python
from vnstock import Finance

finance = Finance(symbol="VCI")

# Lấy dữ liệu quý
df = finance.ratio(period="quarter")
print(f"Shape: {df.shape}")  # (27, 10)

# Các chỉ số quan trọng
ratio_items = ['PE', 'PB', 'ROE', 'ROA', 'Beta']
print(df[df['item'].isin(ratio_items)][['item', 'item_id', '2025-Q3']])

# Lấy dữ liệu năm
df_year = finance.ratio(period="year")
```

**KBS Output:**

```
Shape: (27, 10)
    item item_id  2025-Q3
0    PE     pe      12.5
1    PB     pb       1.8
2   ROE    roe      15.2
3   ROA    roa       8.7
4  Beta   beta       1.2
```

## 🎯 So Sánh Chi Tiết

### Data Format Comparison (v3.4.0+)

**Thay đổi chính từ phiên bản trước:**

- ✅ Giới thiệu FieldDisplayMode cho kiểm soát hiển thị trường linh hoạt
- ✅ Advanced field handling với Field ID generation tự động
- ✅ Hỗ trợ chuẩn hóa schema (schema standardization)
- ✅ Xử lý va chạm field ID với auto-resolution
- ✅ Proxy configuration trong khởi tạo
- ✅ Improved language support (Vi/En/Both)

| Feature                    | v3.3.x | v3.4.0+                       | Ưu Điểm                      |
| -------------------------- | ------ | ----------------------------- | ---------------------------- |
| **Field Display Mode**     | Không  | ✅ STD/ALL/AUTO               | Kiểm soát hiển thị linh hoạt |
| **Item ID Generation**     | Manual | ✅ Auto + collision detection | Tự động hóa & nhất quán      |
| **Proxy Support**          | Không  | ✅ Có (try/rotate/random)     | Vượt IP blocking             |
| **Schema Standardization** | Cơ bản | ✅ Advanced                   | Tối ưu hóa tên cột           |
| **Language Support**       | Vi/En  | ✅ Vi/En/Both flexible        | Linh hoạt hơn                |

### Field ID Generation & Collision Detection

**Tính năng mới:** Field ID tự động tạo từ item_en hoặc item (Việt) với xử lý va chạm tự động

```python
from vnstock import Finance

finance = Finance(symbol="VCI", show_log=True)

# Các item có tên tương tự sẽ tự động xử lý collision
df = finance.income_statement(
    period="quarter",
    display_mode="all"  # Hiển thị item_en để thấy ID generation
)

# Xem item_id được tạo (tự động từ item_en)
print(df[['item', 'item_en', 'item_id']].head(10))

# Output ví dụ:
# item                item_en              item_id
# Doanh thu           Revenue              revenue
# Giá vốn hàng bán   Cost of Sales        cost_of_sales
# Lợi nhuận gộp      Gross Profit         gross_profit
# ...
```

### KBS vs VCI (Chỉ tham khảo)

Từ v3.4.0, **KBS là data source mặc định** và được khuyến nghị:

| Feature          | KBS                        | VCI          | Khuyến nghị      |
| ---------------- | -------------------------- | ------------ | ---------------- |
| **Số items**     | 90 (income), 162 (balance) | 25+ columns  | KBS chi tiết hơn |
| **Language**     | Vi + En                    | En only      | KBS đa ngôn ngữ  |
| **Hierarchical** | Có (levels)                | Không        | KBS có cấu trúc  |
| **Format**       | Item-based (rows)          | Period-based | KBS linh hoạt    |
| **Field IDs**    | ✅ Auto generated          | -            | KBS chuẩn hóa    |

**Mapping từ KBS → Item IDs:**

```
Doanh thu → revenue
Lợi nhuận gộp → gross_profit
Lợi nhuận hoạt động → operating_profit
Lợi nhuận trước thuế → profit_before_tax
Lợi nhuận sau thuế → net_profit
Tổng tài sản → total_assets
Vốn chủ sở hữu → owner_equity
Nợ phải trả → liabilities
```

## 💡 Mẹo Sử Dụng

### 1. Proxy Support cho Cloud Environments

```python
from vnstock import Finance

# Tránh IP blocking trên Google Colab/Kaggle
finance = Finance(
    symbol="VCI",
    proxy_mode="rotate",  # Xoay vòng proxy
    proxy_list=[
        "http://proxy1.com:8080",
        "http://proxy2.com:8080",
        "http://proxy3.com:8080"
    ]
)

# Hoặc dùng single proxy
finance = Finance(
    symbol="VCI",
    proxy_mode="single",
    proxy_list=["http://proxy.com:8080"]
)

# Hoặc dùng try mode - tự động fallback nếu proxy fail
finance = Finance(
    symbol="VCI",
    proxy_mode="try",
    proxy_list=["http://proxy.com:8080"]
)

df = finance.income_statement(period="quarter")
```

### 2. Working with Field Display Modes

```python
from vnstock import Finance
from vnstock.explorer.kbs.financial import FieldDisplayMode

finance = Finance(symbol="VCI", show_log=False)

# 1. Standardized Mode (mặc định) - Tối ưu cho phân tích
df_std = finance.income_statement(period="quarter")
# Columns: ['item', 'item_id', 'unit', 'levels', 'row_number', 'periods...']

# 2. All Fields Mode - Cho nghiên cứu chi tiết
df_all = finance.income_statement(
    period="quarter",
    display_mode=FieldDisplayMode.ALL
)
# Columns: ['item', 'item_en', 'item_id', 'unit', 'levels', 'row_number', 'periods...']

# 3. Lọc theo mục đích sử dụng
# Để lấy chỉ tiêu chính (level 1)
key_items = df_std[df_std['levels'] == 1]

# Để lấy tất cả chi tiết (tất cả levels)
all_items = df_std[df_std['levels'] > 0]

# Để lọc theo item_id
revenue = df_std[df_std['item_id'] == 'revenue']
expenses = df_std[df_std['item_id'].str.contains('expense')]
```

### 3. Field ID Collision Handling

```python
from vnstock import Finance

finance = Finance(symbol="VCI", show_log=True)

# Các item có tên tương tự sẽ được xử lý tự động
df = finance.income_statement(
    period="quarter",
    display_mode="all"
)

# Kiểm tra item_id có bị collision không
from collections import Counter
id_counts = Counter(df['item_id'])
duplicates = {k: v for k, v in id_counts.items() if v > 1}

if duplicates:
    print("Các item_id bị collision:", duplicates)
    # Các duplicate item sẽ được thêm counter tự động
    # VD: 'revenue', 'revenue_1', 'revenue_2', ...
else:
    print("✅ Không có collision")
```

### 4. Schema Standardization

```python
from vnstock import Finance

# Khởi tạo với chuẩn hóa (mặc định)
finance_std = Finance(symbol="VCI", standardize_columns=True)
df_std = finance_std.income_statement(period="quarter")

# Khởi tạo không chuẩn hóa (giữ tên gốc)
finance_raw = Finance(symbol="VCI", standardize_columns=False)
df_raw = finance_raw.income_statement(period="quarter")

# So sánh:
print("Standardized columns:", df_std.columns.tolist())
print("Raw columns:", df_raw.columns.tolist())
```

### 5. Lấy các chỉ tiêu quan trọng

```python
from vnstock import Finance

finance = Finance(symbol="VCI")

# Lấy dữ liệu quý
df = finance.income_statement(period="quarter")

# 1. Lọc theo levels (mặc định level 1 = chỉ tiêu chính)
key_items = df[df['levels'] == 1]

# 2. Lọc theo item_id
important_ids = ['revenue', 'cost_of_sales', 'net_profit', 'operating_profit']
important_data = df[df['item_id'].isin(important_ids)]

# 3. Xem xu hướng (so sánh quý)
columns_to_show = ['item', 'item_id'] + [col for col in df.columns if 'Q' in col or col.isdigit()]
trend = key_items[columns_to_show]
print(trend)

# 4. Tính tăng trưởng quý trên quý (QoQ)
revenue_row = df[df['item_id'] == 'revenue'].iloc[0]
periods = [col for col in df.columns if 'Q' in col or col.isdigit()]
qoq_growth = {}
for i in range(1, len(periods)):
    prev = revenue_row[periods[i]]
    curr = revenue_row[periods[i-1]]
    if prev != 0:
        qoq_growth[periods[i]] = ((curr - prev) / prev) * 100

print(f"Revenue QoQ Growth: {qoq_growth}")
```

### 6. Kết hợp dữ liệu từ nhiều báo cáo

```python
from vnstock import Finance
import pandas as pd

finance = Finance(symbol="VCI")

# Lấy dữ liệu từ các báo cáo khác nhau
income = finance.income_statement(period="year")
balance = finance.balance_sheet(period="year")
cash = finance.cash_flow(period="year")
ratios = finance.ratio(period="year")

# Lọc các chỉ tiêu cần thiết
net_profit = income[income['item_id'] == 'net_profit'].iloc[0]
total_assets = balance[balance['item_id'] == 'total_assets'].iloc[0]
roa = ratios[ratios['item_id'] == 'roa'].iloc[0]

# Tạo bảng tổng hợp
summary_data = {
    'Net Profit': net_profit[['2025', '2024', '2023']].to_dict(),
    'Total Assets': total_assets[['2025', '2024', '2023']].to_dict(),
    'ROA': roa[['2025', '2024', '2023']].to_dict()
}

summary_df = pd.DataFrame(summary_data)
print(summary_df)
```

## 🚨 Lưu Ý Quan Trọng

### 1. Phiên bản v3.4.0+ (Khuyến nghị)

✅ **Các tính năng mới & cải tiến:**

- Field Display Mode (STD/ALL/AUTO) để kiểm soát hiển thị
- Auto Field ID generation với collision detection
- Proxy support (try/rotate/random) cho cloud environments
- Advanced schema standardization
- Improved language support

### 2. Data Validation & Handling

```python
from vnstock import Finance

finance = Finance(symbol="VCI")

# Luôn kiểm tra shape và columns
df = finance.income_statement(period="quarter")

if df is None or len(df) == 0:
    print("❌ Không có dữ liệu")
else:
    print(f"✅ Dữ liệu: {df.shape[0]} items, {df.shape[1]} columns")
    
# Kiểm tra missing data
missing = df.isna().sum()
if missing.sum() > 0:
    print("⚠️ Có missing data:", missing[missing > 0])

# Validate period columns
period_cols = [col for col in df.columns if 'Q' in col or col.isdigit()]
print(f"Periods: {period_cols}")
```

### 3. Field ID & Item ID

- **Tự động tạo từ:** `item_en` (tiếng Anh) hoặc `item` (tiếng Việt)
- **Format:** snake_case (VD: `revenue`, `gross_profit`)
- **Collision handling:** Tự động thêm counter nếu trùng (VD: `revenue_1`, `revenue_2`)
- **Không thay đổi:** Luôn nhất quán trong cùng một phiên

### 4. Period Format

```python
# KBS periods format
'2025-Q3', '2025-Q2', '2025-Q1', '2024-Q4'  # Quý
'2025', '2024', '2023'                      # Năm

# Lọc periods
periods = [col for col in df.columns if 'Q' in col or col.isdigit()]
```

### 5. Proxy Configuration

```python
# ✅ Recommended cho cloud environments
finance = Finance(
    symbol="VCI",
    proxy_mode="rotate",  # Tốt nhất cho high-traffic
    proxy_list=["proxy1", "proxy2", "proxy3"]
)

# hoặc
finance = Finance(
    symbol="VCI",
    proxy_mode="try",  # Fallback to direct nếu fail
    proxy_list=["proxy.com:8080"]
)
```

### 6. Performance Tips

```python
# 1. Lấy dữ liệu một lần, tái sử dụng
df = finance.income_statement(period="year")
revenue = df[df['item_id'] == 'revenue']
profit = df[df['item_id'] == 'net_profit']

# 2. Lọc trước khi xử lý
important = df[df['levels'] == 1]  # Chỉ level 1
result = important[['item_id', '2025', '2024']]

# 3. Cache dữ liệu nếu sử dụng nhiều lần
import pickle
with open('financial_cache.pkl', 'wb') as f:
    pickle.dump(df, f)
```

## ❌ Các Lỗi Thường Gặp & Cách Khắc Phục

### Lỗi 1: Invalid Symbol

```python
# ❌ Sai - Symbol không hợp lệ
finance = Finance(symbol="INVALID123")
df = finance.income_statement()
# ValueError: Mã CK không hợp lệ hoặc không phải cổ phiếu

# ✅ Đúng
finance = Finance(symbol="VCI")  # hoặc "ACB", "VNM", v.v.
```

### Lỗi 2: Invalid Period

```python
# ❌ Sai
df = finance.income_statement(period="monthly")

# ✅ Đúng - Chỉ hỗ trợ 'quarter' hoặc 'year'
df = finance.income_statement(period="quarter")
df = finance.income_statement(period="year")
```

### Lỗi 3: Không Có Dữ Liệu

```python
# ❌ Lỗi thường gặp
finance = Finance(symbol="UNKNOWN")
df = finance.balance_sheet(period="year")
# Kết quả: DataFrame rỗng

# ✅ Xử lý đúng
from vnstock import Finance

try:
    finance = Finance(symbol="VCI")
    df = finance.balance_sheet(period="year")
    
    if df is None or len(df) == 0:
        print("❌ Không có dữ liệu tài chính cho cổ phiếu này")
    else:
        print(f"✅ Lấy {len(df)} items")
        print(df.head())
        
except ValueError as e:
    print(f"❌ Lỗi: {e}")
```

### Lỗi 4: Display Mode Invalid

```python
# ❌ Sai
df = finance.income_statement(display_mode="invalid_mode")

# ✅ Đúng
from vnstock.explorer.kbs.financial import FieldDisplayMode

df = finance.income_statement(display_mode=FieldDisplayMode.STD)
# hoặc
df = finance.income_statement(display_mode=FieldDisplayMode.ALL)
# hoặc backward compatible
df = finance.income_statement(display_mode='vi')
df = finance.income_statement(display_mode='en')
```

### Lỗi 5: Proxy Configuration

```python
# ❌ Sai - Proxy list không đúng format
finance = Finance(
    symbol="VCI",
    proxy_list="http://proxy.com:8080"  # String instead of list
)

# ✅ Đúng
finance = Finance(
    symbol="VCI",
    proxy_mode="rotate",
    proxy_list=["http://proxy1.com:8080", "http://proxy2.com:8080"]
)

# ✅ Hoặc không dùng proxy
finance = Finance(symbol="VCI")  # Direct connection
```

### Lỗi 6: Accessing Non-existent Columns

```python
# ❌ Sai
df = finance.income_statement(period="quarter")
print(df['item_en'])  # KeyError nếu dùng display_mode=STD

# ✅ Đúng - Kiểm tra columns trước
if 'item_en' in df.columns:
    print(df['item_en'])
else:
    print("item_en không có trong columns")
    print(f"Available columns: {df.columns.tolist()}")

# ✅ Hoặc lấy với display_mode=ALL
df_all = finance.income_statement(period="quarter", display_mode="all")
print(df_all['item_en'])
```

### Lỗi 7: IP Blocking (Cloud Environments)

```python
# ❌ Lỗi thường gặp trên Colab/Kaggle
finance = Finance(symbol="VCI")
df = finance.income_statement()
# HTTPError: 403 Forbidden (IP blocked)

# ✅ Khắc phục với Proxy
finance = Finance(
    symbol="VCI",
    proxy_mode="rotate",
    proxy_list=[
        "http://proxy1.com:8080",
        "http://proxy2.com:8080",
        "http://proxy3.com:8080"
    ]
)
df = finance.income_statement()

# hoặc try mode (fallback to direct)
finance = Finance(
    symbol="VCI",
    proxy_mode="try",
    proxy_list=["http://proxy.com:8080"]
)
```

### Lỗi 8: Field ID Collision

```python
# Thường không cần xử lý, nhưng nếu muốn debug
from vnstock import Finance
from collections import Counter

finance = Finance(symbol="VCI", show_log=True)
df = finance.income_statement(period="quarter", display_mode="all")

# Kiểm tra collision
id_counts = Counter(df['item_id'])
duplicates = {k: v for k, v in id_counts.items() if v > 1}

if duplicates:
    print(f"⚠️ Collision detected: {duplicates}")
    # Hệ thống tự động xử lý bằng cách thêm counter
    # VD: revenue, revenue_1, revenue_2, ...
else:
    print("✅ Không có collision")
```

## 📚 Bước Tiếp Theo

1. [02-Installation](02-installation.md) - Cài đặt
2. [01-Overview](01-overview.md) - Tổng quan
3. [03-Listing API](03-listing-api.md) - Danh sách chứng khoán
4. [04-Company API](04-company-api.md) - Thông tin công ty
5. [05-Trading API](05-trading-api.md) - Dữ liệu giao dịch
6. [06-Quote & Price API](06-quote-price-api.md) - Giá lịch sử
7. ✅ **07-Financial API** - Bạn đã ở đây
8. [08-Fund API](08-fund-api.md) - Dữ liệu quỹ
9. [09-Screener API](09-screener-api.md) - Lọc cổ phiếu
10. [10-Connector Guide](10-connector-guide.md) - API bên ngoài
11. [11-Best Practices](11-best-practices.md) - Mẹo & kinh nghiệm
12. [12-Migration Guide](12-migration-guide.md) - Nâng cấp vnstock_data

## 📋 Tóm Tắt Thay Đổi Phiên Bản

### v3.4.0+ (Hiện tại)

✅ Field Display Mode (STD/ALL/AUTO)

✅ Auto Field ID generation + collision detection

✅ Proxy support (try/rotate/random)

✅ Advanced schema standardization

✅ KBS là default source

✅ Improved error handling

---

**Last Updated**: 2026-01-23  

**Version**: 3.4.0+  

**Status**: Actively Maintained  

**Maintained By**: Thịnh Vũ & Vnstock Team