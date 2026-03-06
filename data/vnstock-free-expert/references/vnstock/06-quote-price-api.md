# 06 - Quote & Price API - Giá Lịch Sử & Dữ Liệu Real-time

## 📖 Giới Thiệu

Quote API cung cấp các phương thức lấy dữ liệu giá chứng khoán, bao gồm:

- **Giá lịch sử (Historical Data)**: OHLCV data từ các khoảng thời gian khác nhau
- **Dữ liệu trong ngày (Intraday)**: Giá khớp lệnh thực tế theo từng tick
- **Bảng giá realtime (Price Board)**: Giá mua/bán, khối lượng hiện tại
- **Dư mua - Dư bán (Price Depth)**: Order book, mức bid/ask

### 🚀 Quick Start

```python
from vnstock import Quote

# Khởi tạo với VCI (khuyến nghị)
quote = Quote(symbol="VCI")

# Lấy giá lịch sử - đơn giản với length
df = quote.history(length="1M", interval="1D")  # 1 tháng gần nhất
print(df[['time', 'open', 'high', 'low', 'close', 'volume']].head())

# Lấy 100 ngày gần nhất
df_100d = quote.history(length=100, interval="1D")
print(f"100 ngày: {len(df_100d)} bars")

# Lấy 50 nến (bars) gần nhất  
df_50b = quote.history(length="50b", interval="1D")
print(f"50 nến: {len(df_50b)} bars")

# Lấy dữ liệu intraday
intraday_df = quote.intraday(page_size=100)
print(intraday_df[['time', 'price', 'volume', 'match_type']].head())
```

## 🔌 So Sánh Nguồn Dữ Liệu

| Method            | KBS | VCI | Ghi Chú                          |
| ----------------- | --- | --- | -------------------------------- |
| **history()**     | ✅  | ✅  | Cả hai đều hỗ trợ OHLCV          |
| **intraday()**    | ✅  | ✅  | KBS có get_all, VCI có last_time |
| **price_depth()** | ❌  | ✅  | **VCI độc quyền**                |

**Tổng số methods:**

- **KBS**: 2 methods
- **VCI**: 3 methods

**Khuyến nghị:**

- **KBS**: Dữ liệu ổn định, có thêm cột value với get_all
- **VCI**: Đầy đủ features, có price depth, linh hoạt hơn

## 🏗️ Khởi Tạo

```python
from vnstock import Quote

# Khởi tạo với VCI (khuyến nghị)
quote_vci = Quote(
    symbol="VCI",           # Mã chứng khoán (bắt buộc)
    random_agent=False,      # Sử dụng random user agent
    proxy_mode=None,         # Chế độ proxy: 'try', 'rotate', 'random', 'single'
    proxy_list=None          # Danh sách proxy URLs
)

# Khởi tạo với KBS
quote_kbs = Quote(
    symbol="VCI",           # Mã chứng khoán (bắt buộc)
    random_agent=False,      # Sử dụng random user agent
    proxy_mode=None,         # Chế độ proxy
    proxy_list=None          # Danh sách proxy URLs
)

# ⚠️ Lưu ý: Cần cung cấp symbol khi khởi tạo
# quote = Quote(symbol="")  # Sẽ gây lỗi nếu symbol rỗng
```

## 📊 Dữ Liệu OHLCV

OHLCV là viết tắt của:

- **O**pen (Giá mở): Giá đóng cửa hôm trước
- **H**igh (Giá cao): Giá cao nhất trong khoảng thời gian
- **L**ow (Giá thấp): Giá thấp nhất trong khoảng thời gian
- **C**lose (Giá đóng): Giá cuối cùng trong khoảng thời gian
- **V**olume (Khối lượng): Số lượng cổ phiếu giao dịch

```
Ví dụ:
         time   open   high    low  close     volume
0  2024-01-01  21.00  21.50  20.80  21.40   1234567
1  2024-01-02  21.40  21.80  21.10  21.50   2345678
2  2024-01-03  21.50  21.90  21.30  21.60   1567890
```

## 🔄 Khung Thời Gian Lấy Mẫu

### Khung thời gian hỗ trợ

Cả KBS và VCI đều hỗ trợ các interval sau với nhiều định dạng khác nhau:

| Standard | Alias | Human Readable | Mô Tả   | KBS | VCI |
| -------- | ----- | -------------- | ------- | --- | --- |
| `"1m"`   | `"m"` | `"minute"`     | 1 phút  | ✅  | ✅  |
| `"5m"`   | -     | -              | 5 phút  | ✅  | ✅  |
| `"15m"`  | -     | -              | 15 phút | ✅  | ✅  |
| `"30m"`  | -     | -              | 30 phút | ✅  | ✅  |
| `"1H"`   | `"h"` | `"hour"`       | 1 giờ   | ✅  | ✅  |
| `"1D"`   | `"d"` | `"day"`        | 1 ngày  | ✅  | ✅  |
| `"1W"`   | `"w"` | `"week"`       | 1 tuần  | ✅  | ✅  |
| `"1M"`   | `"M"` | `"month"`      | 1 tháng | ✅  | ✅  |

**Lưu ý quan trọng:**

- **Case-sensitive**: `"M"` cho tháng (viết hoa), `"m"` cho phút (viết thường)
- KBS và VCI đều dùng string format (không dùng TimeFrame enum)
- Interval phải chính xác như trong bảng trên

### 🎯 Alias Ngắn Gọn (Quick Reference)

Các alias này giúp viết code nhanh hơn và tương thích với các trading platform khác:

| Alias | Tương Đương | Mô Tả   |
| ----- | ----------- | ------- |
| `"m"` | `"1m"`      | 1 phút  |
| `"h"` | `"1H"`      | 1 giờ   |
| `"d"` | `"1D"`      | 1 ngày  |
| `"w"` | `"1W"`      | 1 tuần  |
| `"M"` | `"1M"`      | 1 tháng |

**Ví dụ sử dụng:**

```python
# Các cách viết đều tương đương
quote.history(interval="1D")  # Standard format
quote.history(interval="d")   # Alias ngắn gọn
quote.history(interval="day") # Human readable

# Chú ý case sensitivity cho tháng/phút
quote.history(interval="M")   # ✅ Tháng (viết hoa)
quote.history(interval="m")   # ✅ Phút (viết thường)
```

## 📚 Phương Thức Chính

### 1. history() - Lịch Sử Giá OHLCV

Lấy dữ liệu giá lịch sử theo các khoảng thời gian khác nhau.

**Parameters:**

**Cả KBS và VCI:**

```
- start (str): Ngày bắt đầu (YYYY-MM-DD). Bắt buộc nếu không có length/count_back
- end (str): Ngày kết thúc (YYYY-MM-DD). Mặc định None (hiện tại)
- interval (str): Khung thời gian. Mặc định "1D"
- length (str/int): Khoảng thời gian lùi lại từ mốc thời gian hiện tại hoặc số nến
```

**KBS thêm:**

```
- get_all (bool): Lấy tất cả các cột. Mặc định False
```

### 🎯 Lookback với Parameter `length`

Parameter `length` hỗ trợ nhiều định dạng linh hoạt:

**1. Standard Periods (Chu kỳ tiêu chuẩn):**

```
'1W'  = 7 ngày    (1 tuần)
'2W'  = 14 ngày   (2 tuần)
'3W'  = 21 ngày   (3 tuần)
'1M'  = 30 ngày   (1 tháng)
'6W'  = 45 ngày   (6 tuần)
'2M'  = 60 ngày   (2 tháng)
'3M'  = 90 ngày   (1 quý)
'4M'  = 120 ngày  (4 tháng)
'5M'  = 150 ngày  (5 tháng)
'6M'  = 180 ngày  (6 tháng)
'9M'  = 270 ngày  (3 quý)
'1Y'  = 365 ngày  (1 năm)
'18M' = 540 ngày  (1.5 năm)
'2Y'  = 730 ngày  (2 năm)
'3Y'  = 1095 ngày (3 năm)
'5Y'  = 1825 ngày (5 năm)
```

**2. Custom Periods (Tùy chỉnh):**

```
'10D' = 10 ngày
'3W'  = 21 ngày (3 × 7)
'6M'  = 180 ngày (6 × 30)
'2Y'  = 730 ngày (2 × 365)
'1Q'  = 90 ngày (1 quý)
```

**3. Number of Days (Số ngày cụ thể):**

```
150      = 150 ngày
'150'    = 150 ngày
```

**4. Number of Bars (Số nến):**

```
'100b'   = 100 nến (bars)
'50b'    = 50 nến
'200b'   = 200 nến
```

**Ví dụ:**

**Với KBS:**

```python
from vnstock import Quote

quote = Quote(symbol="VCI")

# 1. Standard periods - Chu kỳ tiêu chuẩn
df_1m = quote.history(length="1M", interval="1D")      # 1 tháng gần nhất
df_3m = quote.history(length="3M", interval="1D")      # 3 tháng (1 quý)
df_6m = quote.history(length="6M", interval="1D")      # 6 tháng
df_1y = quote.history(length="1Y", interval="1D")      # 1 năm
df_2y = quote.history(length="2Y", interval="1D")      # 2 năm

# 2. Custom periods - Tùy chỉnh
df_10d = quote.history(length="10D", interval="1D")     # 10 ngày
df_3w = quote.history(length="3W", interval="1D")       # 3 tuần
df_1q = quote.history(length="1Q", interval="1D")       # 1 quý

# 3. Number of days/bars - Số ngày/nến cụ thể
df_150 = quote.history(length=150, interval="1D")       # 150 ngày
df_100b = quote.history(length="100b", interval="1D")   # 100 nến

# 4. Kết hợp với end date
df_ytd = quote.history(end="2024-12-31", length="1Y", interval="1D")  # Cả năm 2024

# 5. Lấy tất cả các cột (bao gồm value)
df_all = quote.history(length="1M", interval="1D", get_all=True)
print(f"Shape: {df_all.shape}")
print(f"Columns: {list(df_all.columns)}")
# Output:
# Shape: (22, 7)
# Columns: ['time', 'open', 'high', 'low', 'close', 'volume', 'value']

print(df_all[['time', 'open', 'high', 'low', 'close', 'volume', 'value']].head())
```

**Với VCI:**

```python
quote = Quote(symbol="VCI")

# 1. Standard periods
df_1m = quote.history(length="1M", interval="1D")      # 1 tháng
df_3m = quote.history(length="3M", interval="1D")      # 3 tháng
df_6m = quote.history(length="6M", interval="1D")      # 6 tháng

# 2. Custom periods với các interval khác nhau
df_1w_hourly = quote.history(length="1W", interval="1H")   # 1 tuần data hourly
df_2w_15m = quote.history(length="2W", interval="15m")   # 2 tuần data 15 phút

# 3. Number of bars
df_100b = quote.history(length="100b", interval="1D")   # 100 nến ngày
df_200b_hourly = quote.history(length="200b", interval="1H")  # 200 nến giờ

# 4. Kết hợp với count_back
df_combined = quote.history(length="3M", interval="1D", count_back=50)  # 3 tháng nhưng chỉ 50 nến cuối

print(f"Shape: {df_combined.shape}")
print(f"Columns: {list(df_combined.columns)}")
# Output:
# Shape: (50, 6)
# Columns: ['time', 'open', 'high', 'low', 'close', 'volume']

print(df_combined[['time', 'open', 'high', 'low', 'close', 'volume']].head())
```

### 2. intraday() - Dữ Liệu Khớp Lệnh Trong Ngày

Lấy dữ liệu khớp lệnh thực tế theo từng tick trong ngày.

**Parameters:**

**KBS:**

```
- page_size (int): Số bản ghi mỗi trang. Mặc định 100
- page (int): Trang dữ liệu. Mặc định 1. Không cần thay đổi tham số này, chỉ thay đổi page_size để đảm bảo lấy về dữ liệu từ 9:15 đến 14:45.
- get_all (bool): Lấy tất cả các cột có sẵn trong API thay vì áp dụng chuẩn hoá. Mặc định False
```

**VCI:**

```
- page_size (int): Số bản ghi mỗi trang. Mặc định 100
- last_time (str/int/float): Thời gian cắt dữ liệu
- last_time_format (str): Định dạng của last_time
```

**Ví dụ:**

**Với KBS:**

```python
quote = Quote(symbol="VCI")

# Lấy 100 bản ghi khớp lệnh (cột chuẩn hóa)
df = quote.intraday(page_size=100)
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
# Output:
# Shape: (100, 5)
# Columns: ['time', 'price', 'volume', 'match_type', 'id']
print(df[['time', 'price', 'volume', 'match_type']].head())
```

**Output với KBS:**

```
                 time   price  volume match_type
0  2024-12-17 14:27:23  34700     150       sell
1  2024-12-17 14:27:22  34700     200        buy
2  2024-12-17 14:27:21  34700     100       sell
3  2024-12-17 14:27:20  34700     300        buy
4  2024-12-17 14:27:19  34700     150       sell
```

**Với VCI:**

```python
quote = Quote(symbol="VCI")

# Lấy dữ liệu intraday
df = quote.intraday(page_size=50)
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
# Output:
# Shape: (50, 5)
# Columns: ['time', 'price', 'volume', 'match_type', 'id']
print(df[['time', 'price', 'volume', 'match_type']].head())
```

**Output với VCI:**

```
                 time   price  volume match_type
0  2024-12-17 14:27:23  34700     150       sell
1  2024-12-17 14:27:22  34700     200        buy
2  2024-12-17 14:27:21  34700     100       sell
3  2024-12-17 14:27:20  34700     300        buy
4  2024-12-17 14:27:19  34700     150       sell
```

### 3. price_depth() - Thống kê Dư Mua, Dư Bán theo bước giá và khối lượng (Chỉ VCI)

Thống kê khối lượng khối lệnh theo từng mức giá.

**Parameters:**

```
- (Không có parameter bắt buộc)
```

**Ví dụ:**

```python
quote = Quote(symbol="VCI")

# Lấy dữ liệu độ sâu giá
df = quote.price_depth()
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
# Output:
# Shape: (50, 4)
# Columns: ['price', 'volume', 'buy_volume', 'sell_volume']
print(df[['price', 'volume', 'buy_volume', 'sell_volume']].head())
```

**Output với VCI:**

```
   price  volume  buy_volume  sell_volume
0  34700    1500        800         700
1  34650    2200       1200        1000
2  34600    1800        900         900
3  34550    2500       1500        1000
4  34500    3000       2000        1000
```

## 🚨 Lưu Ý Quan Trọng

1. **Rate Limits**: Cả hai nguồn đều có rate limits, tránh request quá nhanh
2. **Market Hours**: Dữ liệu intraday có trong ngày giao dịch đến trước 7:00 ngày tiếp theo
3. **Error Handling**: Luôn try-catch khi gọi API
4. **Memory Usage**: Intraday data có thể rất lớn, cẩn thận với page_size
5. **Time Zone**: Tất cả dữ liệu đều ở timezone Việt Nam (UTC+7)

## 🔗 Xem Thêm

- **[03-Listing API](03-listing-api.md)** - Tìm kiếm chứng khoán
- **[04-Company API](04-company-api.md)** - Thông tin công ty
- **[05-Trading API](05-trading-api.md)** - Bảng giá giao dịch
- **[08-Best Practices](08-best-practices.md)** - Mẹo tối ưu hóa

---

**Last Updated**: 2024-12-17  
**Version**: 3.4.0  
**Status**: Actively Maintained