# 04 - Company API - Thông Tin Công Ty

## 📖 Giới Thiệu

**Company API** cung cấp thông tin chi tiết về các công ty cổ phần, bao gồm hồ sơ cơ bản, cấu trúc cổ đông, nhân viên quản lý, sự kiện công ty, và tin tức.

## 🔌 So Sánh Nguồn Dữ Liệu

| Method | KBS | VCI | Ghi Chú |
|--------|-----|-----|---------|
| **overview()** | ✅ | ✅ | KBS có 30 columns, VCI có 10 columns |
| **shareholders()** | ✅ | ✅ | KBS trả về 1 dòng, VCI trả về nhiều dòng |
| **officers()** | ✅ | ✅ | VCI có filter_by, KBS không |
| **subsidiaries()** | ✅ | ✅ | Cấu trúc khác nhau |
| **affiliate()** | ✅ | ✅ | Cả hai đều có |
| **news()** | ✅ | ✅ | KBS có pagination, VCI không |
| **events()** | ✅ | ✅ | KBS có thể rỗng, VCI đầy đủ |
| **ownership()** | ✅ | ❌ | Chỉ KBS hỗ trợ |
| **capital_history()** | ✅ | ❌ | Chỉ KBS hỗ trợ |
| **insider_trading()** | ✅ | ❌ | Chỉ KBS hỗ trợ |
| **reports()** | ❌ | ✅ | Chỉ VCI hỗ trợ |
| **trading_stats()** | ❌ | ✅ | Chỉ VCI hỗ trợ |
| **ratio_summary()** | ❌ | ✅ | Chỉ VCI hỗ trợ |

**Khuyến nghị:**
- **KBS**: Ổn định hơn cho Google Colab/Kaggle, có thêm dữ liệu insider trading
- **VCI**: Dữ liệu đầy đủ hơn cho events, có financial reports và trading stats

## 🔌 Nguồn Dữ Liệu

| Nguồn | Hỗ Trợ | Ghi Chú |
|-------|--------|--------|
| **KBS** | ✅ | Web scraping - Khuyến nghị, ổn định |
| VCI | ✅ | Web scraping - Nguồn truyền thống |
| TCBS | ⚠️ | Web scraping - Deprecated, sẽ loại bỏ v3.5.0 |

## 🚀 Bắt Đầu

```python
from vnstock import Company

# Khởi tạo với KBS (khuyến nghị)
company = Company(source="KBS", symbol="VCI")

# Xem thông tin cổ đông
shareholders = company.shareholders()
print(shareholders)

# Hoặc với VCI
company_vci = Company(source="VCI", symbol="VCI")

# ⚠️ TCBS đã deprecated, không nên sử dụng
# company_tcbs = Company(source="TCBS", symbol="VCI")
```

## 📚 Phương Thức Chính

### 1. overview() - Thông Tin Cơ Bản

Lấy thông tin tổng quan về công ty.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` (1 dòng) với các cột:
- `symbol` - Mã chứng khoán
- `issue_share` - Số cổ phiếu phát hành
- `company_profile` - Hồ sơ công ty (JSON)
- `icb_name2`, `icb_name3`, `icb_name4` - Phân loại ngành (ICB)
- `financial_ratio_issue_share` - Thông tin tài chính
- `charter_capital` - Vốn điều lệ

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
overview = company.overview()
print(f"Shape: {overview.shape}")  # (1, 30)
print(f"Columns: {list(overview.columns)}")
print(f"Dtypes:\n{overview.dtypes}")
# Output:
# Shape: (1, 30)
# Columns: ['business_model', 'symbol', 'founded_date', 'charter_capital', 
#           'number_of_employees', 'listing_date', 'par_value', 'exchange', ...]
# Dtypes:
# business_model           object
# symbol                   object
# founded_date             object
# charter_capital           int64
# number_of_employees       int64
# ...
print(overview[['symbol', 'charter_capital', 'exchange']].head())
```

**Output với KBS:**
```
                                      business_model symbol founded_date  charter_capital  exchange
0  \n- Môi giới chứng khoán và giao dịch cho vay ...    VCI   06/08/2007      8501000000000      HOSE
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
overview = company.overview()
print(f"Shape: {overview.shape}")  # (1, 10)
print(f"Columns: {list(overview.columns)}")
print(f"Dtypes:\n{overview.dtypes}")
# Output:
# Shape: (1, 10)
# Columns: ['symbol', 'id', 'issue_share', 'history', 'company_profile', 
#           'icb_name3', 'icb_name2', 'icb_name4', 'financial_ratio_issue_share', 'charter_capital']
# Dtypes:
# symbol                         object
# id                             object
# issue_share                     int64
# history                        object
# ...
print(overview[['symbol', 'charter_capital', 'icb_name4']].head())
```

**Output với VCI:**
```
  symbol     id  issue_share  ...             icb_name4 charter_capital
0    VCI  75885    850100000  ...  Môi giới chứng khoán   8501000000000
```

### 2. shareholders() - Cổ Đông Chính

Lấy danh sách các cổ đông lớn.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với các cột:
- `name` - Tên cổ đông (str)
- `update_date` - Ngày cập nhật (str, format: "YYYY-MM-DDTHH:MM:SS")
- `shares_owned` - Số cổ phiếu sở hữu (int64)
- `ownership_percentage` - Tỷ lệ sở hữu (float64, %)

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
shareholders = company.shareholders()
print(shareholders.shape)  # (1, 4)
print(shareholders[['name', 'shares_owned', 'ownership_percentage']].head())
```

**Output với KBS:**
```
      name          update_date  shares_owned  ownership_percentage
0  Tô Hải  2025-06-30T00:00:00     128889403                 17.95
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
shareholders = company.shareholders()
print(shareholders.shape)  # (33, 5)
print(shareholders[['share_holder', 'quantity', 'share_own_percent']].head(3))
```

**Output với VCI:**
```
         id           share_holder   quantity  share_own_percent update_date
0  96744105                 Tô Hải  129139403            0.17870  2025-10-31
1  96742707         PYN Elite Fund    8132100            0.04910  2025-01-24
2  96734076  Nguyễn Phan Minh Khôi    7483872            0.04591  2025-01-24
```

### 3. officers() - Ban lãnh đạo

Lấy danh sách ban lãnh đạo (Ban điều hành, Hội đồng quản trị).

**Tham số:**
- `filter_by` (str, tùy chọn): Loại lọc
  - `"all"` - Tất cả (mặc định)
  - `"ceo"` - Chỉ CEO
  - `"boc"` - Board of Directors

**Trả về:** `pd.DataFrame` với các cột:
- `from_date` - Năm bắt đầu (int)
- `position` - Vị trí công việc (str, VN)
- `name` - Tên nhân viên (str)
- `position_en` - Vị trí công việc (str, EN)
- `owner_code` - Mã sở hữu (str)

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
officers = company.officers()
print(officers.shape)  # (12, 5)
print(officers[['name', 'position', 'from_date']].head(3))
```

**Output với KBS:**
```
                   name        position  from_date
0  Bà Nguyễn Thanh Phượng          CTHĐQT       2007
1       Ông Đinh Quang Hoàn  TVHĐQT/Phó TGĐ       2007
2                Ông Tô Hải      TGĐ/TVHĐQT       2007
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
officers = company.officers()
print(officers.shape)  # (14, 7)
print(officers[['officer_name', 'officer_position', 'officer_own_percent']].head(3))
```

**Output với VCI:**
```
   id         officer_name                            officer_position  officer_own_percent   quantity
0  11               Tô Hải  Tổng Giám đốc/Thành viên Hội đồng Quản trị               0.1787  129139403
1  14  Nguyễn Thanh Phượng                  Chủ tịch Hội đồng Quản trị               0.0318   22815000
2   4     Nguyễn Quang Bảo                           Phó Tổng Giám đốc               0.0032    2324156
```

### 4. subsidiaries() - Công Ty Con

Lấy danh sách công ty con.

**Tham số:**
- `filter_by` (str, tùy chọn): 
  - `"subsidiary"` - Công ty con trực tiếp
  - `"all"` - Tất cả

**Trả về:** `pd.DataFrame` với các cột:
- `update_date` - Ngày cập nhật (str, format: "YYYY-MM-DDTHH:MM:SS")
- `name` - Tên công ty con (str)
- `charter_capital` - Vốn điều lệ (int64)
- `ownership_percent` - Tỷ lệ sở hữu (float64, %)
- `currency` - Loại tiền tệ (str)
- `type` - Loại quan hệ (str)

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
subsidiaries = company.subsidiaries()
print(subsidiaries.shape)  # (1, 6)
print(subsidiaries[['name', 'charter_capital', 'ownership_percent']])
```

**Output với KBS:**
```
                                          name  charter_capital  ownership_percent
0  CTCP Quản lý Quỹ Đầu tư Chứng khoán Bản Việt     130000000000                 51
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
try:
    subsidiaries = company.subsidiaries()
    print(subsidiaries.shape)
    print(subsidiaries.head())
except Exception as e:
    print(f"VCI subsidiaries error: {e}")
# Output: VCI subsidiaries error: RetryError[<Future...>]
```

### 5. affiliate() - Công Ty Liên Kết

Lấy danh sách công ty liên kết.

**Tham số:** Không có

**Trả về:** `pd.DataFrame`

⚠️ **Lưu ý:** Phương thức này có thể trả về lỗi nếu không có dữ liệu

### 6. news() - Tin Tức

Lấy tin tức gần đây về công ty.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với các cột:
- `head` - Tiêu đề tin (str)
- `article_id` - ID bài viết (int64)
- `publish_time` - Thời gian xuất bản (str, format: "YYYY-MM-DDTHH:MM:SS")
- `url` - Liên kết tin tức (str)

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
news = company.news()
print(news.shape)  # (1, 5)
print(news[['head', 'publish_time']].head())
```

**Output với KBS:**
```
                                           head  article_id           publish_time                                                url
0  VCI- Thông báo về ngày đăng ký cuối cùng...    1386720  2025-12-31T14:03:26  /2025/12/vci-thong-bao-ve-ngay-dang-ky-cuoi-cu...
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
news = company.news()
print(news.shape)  # (10, 18)
print(news[['news_title', 'public_date', 'price_change_pct']].head(3))
```

**Output với VCI:**
```
        id                                         news_title  ...  price_change_pct
0  9121667  VCI: Thông báo về việc giao dịch chứng khoán t...  ...        -0.013235
1  9108930  VCI: Giấy phép điều chỉnh giấy phép thành lập ...  ...         0.019118
2  9095781  VCI: Quyết định về việc thay đổi đăng ký niêm yết                 ...        -0.002825
```

### 7. events() - Sự Kiện Công Ty

Lấy danh sách sự kiện công ty (chia cổ tức, phát hành cổ phiếu, niêm yết, v.v.).

⚠️ **Lưu ý với KBS**: Có thể không có dữ liệu sự kiện cho một số công ty.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với các cột:
- `id` - ID sự kiện
- `event_title` - Tiêu đề sự kiện (str, VN)
- `en__event_title` - Tiêu đề sự kiện (str, EN)
- `public_date` - Ngày công bố (str)
- `issue_date` - Ngày phát hành (str)
- `source_url` - Liên kết tài liệu
- `event_list_code` - Mã loại sự kiện (str)
- `event_list_name` - Tên loại sự kiện (str, VN)
- `en__event_list_name` - Tên loại sự kiện (str, EN)
- `ratio` - Tỷ lệ (float64, VD: 0.35 = 35%)
- `value` - Giá trị (float64)
- `record_date` - Ngày ghi danh (str)
- `exright_date` - Ngày hết quyền (str)

**Ví dụ:**

**Với KBS (khuyến nghị):**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
events = company.events()
print(events.shape)  # (0, 0) - Có thể rỗng

# Nếu không có dữ liệu với KBS, thử VCI
if events.empty:
    company_vci = Company(source="VCI", symbol="VCI")
    events = company_vci.events()
    print(f"VCI events: {events.shape}")
```

**Với VCI (nguồn truyền thống):**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
events = company.events()
print(events.shape)  # (32, 13)
print(events[['event_title', 'event_list_name', 'public_date']].head(5))
```

**Output với VCI:**
```
         id                                        event_title  ...           event_list_name en__event_list_name
0   1868825  VCI - Trả cổ tức Đợt 1, 2021 bằng tiền 1200 VN...  ...  Trả cổ tức bằng tiền mặt       Cash Dividend
1  16582552  VCI - Trả cổ tức Đợt 1 năm 2022 bằng tiền 700 ...  ...  Trả cổ tức bằng tiền mặt       Cash Dividend
2  22322707  VCI - Trả cổ tức Đợt 2 năm 2022 bằng tiền 500 ...  ...  Trả cổ tức bằng tiền mặt       Cash Dividend
3  42249237  VCI - Trả cổ tức Đợt 1 năm 2024 bằng tiền 400 ...  ...  Trả cổ tức bằng tiền mặt       Cash Dividend
4  50556599  VCI - Trả cổ tức Đợt 2 năm 2024 bằng tiền 250 ...  ...  Trả cổ tức bằng tiền mặt       Cash Dividend
```

## 💡 Ví Dụ Thực Tế

### Phân Tích Cấu Trúc Cổ Đông

**Với KBS (khuyến nghị):**
```python
from vnstock import Company

# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
shareholders = company.shareholders()

# Top cổ đông lớn (KBS chỉ trả về 1 dòng)
top_shareholder = shareholders.nlargest(1, 'shares_owned')
print("Cổ đông lớn nhất:")
print(top_shareholder[['name', 'shares_owned', 'ownership_percentage']])

# Tính tỷ lệ sở hữu
total_ownership = shareholders['ownership_percentage'].sum()
print(f"\nTổng tỷ lệ sở hữu: {total_ownership:.2f}%")
```

**Với VCI (nguồn truyền thống):**
```python
from vnstock import Company

# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
shareholders = company.shareholders()

# Top 5 cổ đông lớn
top_5 = shareholders.nlargest(5, 'quantity')
print("Top 5 cổ đông:")
print(top_5[['share_holder', 'quantity', 'share_own_percent']])

# Tính tập trung cổ đông
top_10_pct = shareholders.nlargest(10, 'share_own_percent')['share_own_percent'].sum()
print(f"\nTrong lượng cổ đông top 10: {top_10_pct:.2f}%")
```

### Theo Dõi Ban Quản Trị

```python
from vnstock import Company

# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
officers = company.officers()

# Các vị trí lãnh đạo
positions = officers['position'].unique()
print(f"Số lượng vị trí quản lý: {len(positions)}")
print(f"Các vị trí: {list(positions)}")

# Cổ đông nội bộ (có sở hữu cổ phiếu)
insiders = officers[officers['position'].str.contains('TGĐ|CTHĐQT|TVHĐQT', na=False)]
print(f"\nBan lãnh đạo: {len(insiders)} người")
print(insiders[['name', 'position']])
```

### Theo Dõi Sự Kiện

```python
from vnstock import Company

# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
events = company.events()

# Kiểm tra nếu có sự kiện
if not events.empty:
    # Sự kiện chia cổ tức
    dividend_events = events[events['event_list_code'] == 'DIV']
    print(f"Số lần chia cổ tức: {len(dividend_events)}")
    
    # Sự kiện phát hành cổ phiếu
    issue_events = events[events['event_list_code'] == 'ISS']
    print(f"Số lần phát hành cổ phiếu: {len(issue_events)}")
else:
    print("Không có dữ liệu sự kiện với KBS, thử VCI:")
    company_vci = Company(source="VCI", symbol="VCI")
    events = company_vci.events()
    print(f"VCI events: {events.shape}")
```

### 8. ownership() - Cấu Trúc Cổ Đông (Chỉ KBS)

Lấy thông tin cơ cấu cổ đông theo tỷ lệ sở hữu - chỉ có ở KBS.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với các cột:
- `owner_type` - Loại cổ đông (str)
- `ownership_percentage` - Tỷ lệ sở hữu (float64, %)
- `shares_owned` - Số cổ phiếu sở hữu (int64)
- `update_date` - Ngày cập nhật (str, format: "YYYY-MM-DDTHH:MM:SS")

**Ví dụ:**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
ownership = company.ownership()
print(ownership.shape)  # (3, 4)
print(ownership)
```

**Output với KBS:**
```
                owner_type  ownership_percentage  shares_owned          update_date
0     CĐ nắm trên 5% số CP                 17.95     128889403  2024-12-31T00:00:00
1  CĐ nắm từ 1% - 5% số CP                 39.65     284754680  2024-12-31T00:00:00
2     CĐ nắm dưới 1% số CP                 42.40     304455397  2024-12-31T00:00:00
```

### 9. capital_history() - Lịch Sử Vốn Điều Lệ (Chỉ KBS)

Lấy lịch sử thay đổi vốn điều lệ của công ty - chỉ có ở KBS.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với các cột:
- `date` - Ngày thay đổi (str, format: "YYYY-MM-DD")
- `charter_capital` - Vốn điều lệ (int64)
- `currency` - Loại tiền tệ (str)

**Ví dụ:**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
capital_history = company.capital_history()
print(capital_history.shape)  # (19, 3)
print(capital_history.head())
```

**Output với KBS:**
```
        date  charter_capital currency
0 2025-12-17    8501000000000      VND
1 2025-03-07    7226000000000      VND
2 2024-06-12    7180994800000      VND
3 2024-10-10    5744694800000      VND
4 2024-05-08    4419000000000      VND
```

### 10. insider_trading() - Giao Dịch Nội Bộ (Chỉ KBS)

Lấy thông tin giao dịch của người nội bộ - chỉ có ở KBS.

**Tham số:**
- `page` (int, tùy chọn): Số trang (mặc định: 1)
- `page_size` (int, tùy chọn): Kích thước trang (mặc định: 10)

**Trả về:** `pd.DataFrame` (có thể rỗng)

**Ví dụ:**
```python
# Khởi tạo với KBS
company = Company(source="KBS", symbol="VCI")
insider_trading = company.insider_trading()
print(f"Shape: {insider_trading.shape}")
# Output: Shape: (0, 0) - Có thể rỗng nếu không có dữ liệu
```

### 11. reports() - Báo Cáo Phân Tích (Chỉ VCI)

Lấy báo cáo phân tích về công ty - chỉ có ở VCI.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` (có thể rỗng)

**Ví dụ:**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
reports = company.reports()
print(f"Shape: {reports.shape}")
# Output: Shape: (0, 0) - Có thể rỗng nếu không có báo cáo
```

### 12. trading_stats() - Thống Kê Giao Dịch (Chỉ VCI)

Lấy thống kê giao dịch của công ty - chỉ có ở VCI.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với 24 columns bao gồm:
- `symbol`, `exchange`, `ev`, `ceiling`, `floor`
- `avg_match_volume_2w`, `foreign_holding_room`, `current_holding_ratio`
- `max_holding_ratio`, và nhiều thống kê khác

**Ví dụ:**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
trading_stats = company.trading_stats()
print(trading_stats.shape)  # (1, 24)
print(trading_stats[['symbol', 'exchange', 'ev', 'foreign_holding_room']].head())
```

**Output với VCI:**
```
  symbol exchange              ev  ceiling  foreign_holding_room
0    VCI     HOSE  29498470000000    37250             144233070
```

### 13. ratio_summary() - Tóm Tắt Tỷ Lệ Tài Chính (Chỉ VCI)

Lấy tóm tắt các tỷ lệ tài chính của công ty - chỉ có ở VCI.

**Tham số:** Không có

**Trả về:** `pd.DataFrame` với 46 columns tài chính

**Ví dụ:**
```python
# Khởi tạo với VCI
company = Company(source="VCI", symbol="VCI")
ratio_summary = company.ratio_summary()
print(ratio_summary.shape)  # (1, 46)
print(ratio_summary[['symbol', 'year_report', 'revenue', 'ebit']].head())
```

**Output với VCI:**
```
  symbol  year_report        revenue          ebit
0    VCI         2025  1443289075867  716139241499
```

```

## ⚠️ Ghi Chú Quan Trọng

1. **KBS là nguồn khuyến nghị**: Ổn định hơn VCI cho Google Colab/Kaggle
2. **Dữ liệu không đầy đủ**: Không phải công ty nào cũng có đầy đủ thông tin cho tất cả phương thức
3. **KBS hạn chế**: Events có thể rỗng, chỉ trả về 1 cổ đông lớn nhất
4. **Giá trị NaN**: Nếu không có dữ liệu, sẽ trả về `NaN` hoặc rỗng
5. **Phụ thuộc vào nguồn**: Thông tin khác nhau giữa KBS, VCI và TCBS
6. **TCBS deprecated**: Sẽ loại bỏ trong v3.5.0, không nên sử dụng
7. **Dữ liệu lịch sử**: Thông tin lịch sử được cập nhật định kỳ
8. **Methods độc quyền**: KBS có ownership/capital_history/insider_trading, VCI có reports/trading_stats/ratio_summary

## 🔗 Xem Thêm

- **[03-Listing API](03-listing-api.md)** - Tìm kiếm chứng khoán
- **[05-Trading API](05-trading-api.md)** - Dữ liệu giao dịch
- **[06-Financial API](06-financial-api.md)** - Dữ liệu tài chính
- **[08-Best Practices](08-best-practices.md)** - Mẹo tối ưu hóa

---

**Last Updated**: 2024-12-17  
**Version**: 3.4.0  
**Status**: Actively Maintained  
**Important**: KBS là nguồn dữ liệu mới được khuyến nghị, ổn định hơn VCI cho Google Colab/Kaggle
