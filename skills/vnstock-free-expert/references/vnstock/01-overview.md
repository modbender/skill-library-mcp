# Vnstock 3.4.0 - Tổng Quan Kiến Trúc & Dữ Liệu

**Phiên bản:** 3.4.0+  

**Cập nhật:** Tháng 1, 2026  

**Trạng thái:** Hoạt động

---

## 📚 Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [Các Plan & Rate Limit](#các-plan--rate-limit)
3. [Kiến Trúc Tổng Thể](#kiến-trúc-tổng-thể)
4. [Phân Tầng Dữ Liệu (Data Layers)](#phân-tầng-dữ-liệu-data-layers)
5. [Các APIs & Dữ Liệu Hiện Có](#các-apis--dữ-liệu-hiện-có)
6. [Nguồn Dữ Liệu & Connectors](#nguồn-dữ-liệu--connectors)
7. [Core Utilities](#core-utilities)
8. [Cách Sử Dụng Cơ Bản](#cách-sử-dụng-cơ-bản)

---

## 📖 Giới Thiệu

**Vnstock** là thư viện Python mạnh mẽ để lấy dữ liệu chứng khoán Việt Nam từ nhiều nguồn uy tín. Thư viện được thiết kế với kiến trúc provider-based, cho phép dễ dàng chuyển đổi giữa các nguồn dữ liệu khác nhau mà không thay đổi code.

### 🎯 Đặc Điểm Chính

- **Nhiều nguồn dữ liệu**: VCI, KBS, MSN, và các connectors bên ngoài (FMP, DNSE)
- **API thống nhất**: Cùng một interface cho tất cả các nguồn dữ liệu
- **Dữ liệu lịch sử & Real-time**: Giá lịch sử, dữ liệu trong ngày, giá realtime
- **Dữ liệu công ty**: Hồ sơ công ty, cổ đông chính, nhân viên quản lý
- **Dữ liệu tài chính**: Báo cáo tài chính, chỉ số tài chính, các dòng tiền
- **Lọc & Phân loại**: Tìm kiếm theo ngành, sàn giao dịch, chỉ số
- **Xử lý lỗi thông minh**: Retry tự động với exponential backoff

⚠️ **TCBS**: Đã ngưng cập nhật từ v3.4.0, sẽ loại bỏ trong v3.5.0 (tháng 3/2026)

---

## 💳 So sánh các gói sử dụng & giới hạn

Vnstock cung cấp các gói sử dụng khác nhau phù hợp với từng nhu cầu cụ thể, xem thông tin chính xác được chia sẻ tại website Vnstock [Gói tài trợ Vnstock](https://vnstocks.com/insiders-program):

### So sánh gói sử dụng

| Tiêu Chí          | Khách | Cộng đồng (Tiêu chuẩn)  | Bronze    | Silver    | Golden    |
| ----------------- | ----- | ----- | --------- | --------- | --------- |
| **Giới Hạn/Phút** | 20    | 60    | 180 (3x)  | 300 (5x) | 500 (10x) |
| **Giới Hạn/Giờ**  | 1.2K  | 3.6K  | 10.8K     | 18K       | 36K       |
| **Giới Hạn/Ngày** | 5K    | 10K   | 50K       | 100K      | 150K      |
| **Đăng Nhập**     | ❌    | ✅    | ✅        | ✅        | ✅        |
| **API Key**       | ❌    | ✅    | ✅        | ✅        | ✅        |
| **vnstock_data**  | ❌    | ❌    | ✅        | ✅        | ✅        |
| **Hỗ Trợ**        | ❌    | ❌    | ✅        | ✅        | ✅        |
| **Cam Kết**       | Không | Không | Linh Hoạt | Quý       | 1 Năm     |

(*) **Lưu ý quan trọng về Rate Limit:**
- Khi chạm giới hạn API, chương trình sẽ tự động dừng để bảo vệ hệ thống
- Số lượng request trên mang tính tham khảo và có thể thay đổi
- Giới hạn thực tế phụ thuộc vào: giới hạn của Vnstock và giới hạn của server nguồn dữ liệu
- Khuyến nghị: Sử dụng cache dữ liệu để tối ưu hiệu suất

### 🎯 Chọn Plan Nào?

#### 1. **Guest** - Trải Nghiệm Nhanh

- **Ai nên dùng**: Người mới, thử nghiệm, không cam kết
- **Đặc điểm**: 
    - Không cần đăng nhập hay API key
    - Giới hạn 20 request/phút (1.2K/giờ, 5K/ngày)
    - Thích hợp cho khám phá nhanh
- **Ví dụ**: `quote = Quote(source="vci", symbol="VCB")`

#### 2. **Free** - Học Tập & Phát Triển

- **Ai nên dùng**: Sinh viên, developer mới, người học Python
- **Đặc điểm**:
    - Cần đăng nhập tài khoản vnstock & API key
    - Giới hạn 60 request/phút (3.6K/giờ, 10K/ngày) - **3x Guest**
    - Đủ cho phát triển & kiểm thử cơ bản
- **Cách bắt đầu**: Đăng ký miễn phí tại https://vnstocks.com/login
- **Ví dụ**: 

  ```python
  from vnstock import config
  config.set_api_key("your_api_key")
  quote = Quote(source="vci", symbol="VCB")
  ```

#### 3. **Bronze** - Dữ Liệu Cơ Bản

- **Ai nên dùng**: Nhà phân tích, trader cá nhân, startup
- **Đặc điểm**:
    - Giới hạn 180 request/phút (10.8K/giờ, 50K/ngày) - **9x Guest**
    - Truy cập **vnstock_data** với dữ liệu nâng cao
    - Plan linh hoạt (hàng tháng hoặc quý)
    - Hỗ trợ cơ bản
- **Tính năng nâng cao**: Xem [vnstock_data Overview](../vnstock-data/01-overview.md)
- **Tham gia**: https://vnstocks.com/insiders-program

#### 4. **Silver** - Chức Năng Mở Rộng

- **Ai nên dùng**: nhóm, quản lý quỹ đầu tư, dự án công khai
- **Đặc điểm**:
    - Giới hạn 300 request/phút (18K/giờ, 100K/ngày) - **15x Guest**
    - Truy cập hầu hết chức năng nâng cao của vnstock_data
    - Plan quý (3 tháng)
    - Hỗ trợ ưu tiên
- **Tính năng nâng cao**: Xem [vnstock_data Overview](../vnstock-data/01-overview.md)
- **Tham gia**: https://vnstocks.com/insiders-program

#### 5. **Golden** - Toàn Bộ Chức Năng

- **Ai nên dùng**: Dự án lâu dài, đồng hành bền vững cùng dự án
- **Đặc điểm**:
    - Giới hạn 600 request/phút (36K/giờ, 150K/ngày) - **30x Guest**
    - Truy cập **tất cả** chức năng của bộ thư viện tài trợ
    - Plan 1 năm (cam kết lâu dài)
    - Hỗ trợ tối ưu & ưu đãi chi phí tốt nhất
- **Tính năng nâng cao**: Xem [vnstock_data Overview](../vnstock-data/01-overview.md)
- **Tham gia**: https://vnstocks.com/insiders-program

### 📊 Rate Limit Chi Tiết

```python
TIER_LIMITS = {
    "guest": {"min": 20, "hour": 1200, "day": 5000},
    "free": {"min": 60, "hour": 3600, "day": 10000},
    "bronze": {"min": 180, "hour": 10800, "day": 50000},
    "silver": {"min": 300, "hour": 15000, "day": 100000},
    "golden": {"min": 500, "hour": 30000, "day": 150000}
}
```

### 🚀 Nâng Cấp

Khi bạn gặp rate limit:

```python
from vnstock.core.quota import RateLimitExceeded

try:
    quote = Quote(source="vci", symbol="VCB")
    df = quote.history(start="2024-01-01", end="2024-12-31")
except RateLimitExceeded as e:
    print(e)  # Sẽ hiển thị hướng dẫn nâng cấp phù hợp
```

---

## 🏗️ Kiến Trúc Tổng Thể

Vnstock được thiết kế theo **Adapter Pattern** với các tầng rõ ràng:

```
┌─────────────────────────────────────────┐
│         User Code (Your App)            │
├─────────────────────────────────────────┤
│  Quote | Listing | Company | Finance    │  ← Unified API Layer
│  Trading | Misc (Gold, FX)              │
├─────────────────────────────────────────┤
│  Provider Registry (Dynamic Discovery)  │
├─────────────────────────────────────────┤
│        Explorer (Web Scraping)          │
│  ┌──────────────────────────────────┐   │
│  │ VCI | KBS | MSN | FMarket        │   │
│  └──────────────────────────────────┘   │
│                                          │
│    Connector (Official APIs)             │
│  ┌──────────────────────────────────┐   │
│  │ FMP | DNSE | Binance             │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Cấu Trúc Thư Mục Hiện Tại

```
vnstock/
├── api/                          # Unified API Layer (Facade)
│   ├── __init__.py
│   ├── quote.py                  # Quote API
│   ├── company.py                # Company API
│   ├── financial.py              # Finance API
│   ├── trading.py                # Trading API
│   ├── listing.py                # Listing API
│   └── ...
│
├── explorer/                     # Data Explorers (Source-specific)
│   ├── kbs/                      # KB Securities
│   │   ├── quote.py
│   │   ├── company.py
│   │   ├── financial.py
│   │   ├── trading.py
│   │   ├── listing.py
│   │   └── const.py
│   │
│   ├── vci/                      # VCI
│   │   ├── quote.py
│   │   ├── company.py
│   │   ├── financial.py
│   │   ├── trading.py
│   │   ├── listing.py
│   │   └── const.py
│   │
│   ├── misc/                     # Miscellaneous (Utilities)
│   │   ├── gold_price.py         # Giá vàng
│   │   └── exchange_rate.py      # Tỷ giá ngoại tệ
│   │
│   └── ... (MAS, VND, CafeF, FMarket, MBK, SPL, MSN, TCBS, v.v.)
│
├── connector/                    # Low-level Connectors
│   ├── dnse/                     # DNSE Trading
│   ├── fmp/                      # FMP (Financial Modeling Prep)
│   ├── binance/                  # Binance (Crypto - sắp tới)
│   └── ...
│
├── core/                         # Core Utilities & Infrastructure
│   ├── utils/
│   │   ├── market.py             # Giờ giao dịch, trạng thái thị trường
│   │   ├── interval.py           # Xử lý timeframe (1D, 1H, 1m, v.v.)
│   │   ├── lookback.py           # Xử lý lookback period (1M, 3M, 100D, v.v.)
│   │   ├── transform.py          # Chuyển đổi dữ liệu (long/wide format)
│   │   ├── parser.py             # Parse dữ liệu từ các nguồn
│   │   ├── validation.py         # Kiểm tra dữ liệu
│   │   ├── auth.py               # Xác thực API key
│   │   ├── client.py             # HTTP client
│   │   ├── proxy_manager.py      # Quản lý proxy
│   │   ├── logger.py             # Logging
│   │   └── ... (19+ utilities)
│   │
│   ├── types.py                  # Type definitions
│   ├── models.py                 # Data models
│   ├── registry.py               # Provider registry
│   └── ...
│
├── base.py                       # Base classes (BaseAdapter, etc.)
├── config.py                     # Configuration
├── constants.py                  # Constants
└── __init__.py                   # Package initialization
```

### Cách Hoạt Động

1. **Adapter Layer**: Bạn sử dụng các class như `Quote`, `Listing`, `Company` v.v.
2. **Provider Registry**: Thư viện tìm kiếm provider phù hợp dựa trên `source` parameter
3. **Dynamic Method Detection**: Chỉ các phương thức mà provider hỗ trợ mới được gọi
4. **Parameter Filtering**: Tự động lọc tham số để phù hợp với provider signature

---

## 📊 Phân Tầng Dữ Liệu (Data Layers)

Vnstock tổ chức dữ liệu thành các tầng theo mô hình tham khảo từ các nguồn quốc tế như Bloomberg Terminal, FinancialModelingPrep, vv

### Tầng 1: Reference Data (Dữ Liệu Tham Chiếu)

**Mục đích:** Master data, identifiers, classifications

**Dữ Liệu Hiện Có:**

- **Listing API**: Danh sách chứng khoán, chỉ số, sàn giao dịch
- **Company API**: Thông tin công ty, cổ đông, ban lãnh đạo

**Methods:**

```python
from vnstock import Listing, Company

# Listing - Danh sách chứng khoán
listing = Listing(source="vci")
symbols = listing.all_symbols()           # Tất cả mã chứng khoán
indices = listing.indices()               # Danh sách chỉ số
bonds = listing.government_bonds()        # Trái phiếu (VCI only)

# Company - Thông tin công ty
company = Company(source="vci", symbol="VCB")
profile = company.overview()              # Thông tin tổng quan
shareholders = company.shareholders()     # Cổ đông lớn
officers = company.officers()             # Ban lãnh đạo
subsidiaries = company.subsidiaries()     # Công ty con
capital_history = company.capital_history()  # Lịch sử vốn (KBS only)
```

---

### Tầng 2: Market Data (Dữ Liệu Thị Trường)

**Mục đích:** Giá, khối lượng, sổ lệnh, dữ liệu tick

**Dữ Liệu Hiện Có:**

- **Quote API**: Giá lịch sử, intraday, sổ lệnh
- **Trading API**: Bảng giá, thống kê giao dịch

**Methods:**

```python
from vnstock import Quote, Trading

# Quote - Dữ liệu giá
quote = Quote(source="vci", symbol="VCB")
history = quote.history(
    start="2024-01-01",
    end="2024-12-31",
    interval="1D"  # 1D, 1H, 1m, 5m, 15m, 30m
)
intraday = quote.intraday()               # Dữ liệu trong ngày
depth = quote.price_depth()               # Sổ lệnh

# Trading - Dữ liệu giao dịch
trading = Trading(source="vci")
board = trading.price_board(["VCB", "VNM"])  # Bảng giá
price_history = trading.price_history()      # Lịch sử giá (VCI only)
trading_stats = trading.trading_stats()      # Thống kê giao dịch (VCI only)
```

**Hỗ trợ TimeFrame:**

- Intraday: `1m`, `5m`, `15m`, `30m`, `1H`, `4h`
- Daily+: `1D`, `1W`, `1M`

---

### Tầng 3: Fundamental Data (Dữ Liệu Cơ Bản)

**Mục đích:** Báo cáo tài chính, chỉ số, tỷ lệ

**Dữ Liệu Hiện Có:**

- **Finance API**: Báo cáo tài chính (Income, Balance Sheet, Cash Flow, Ratios)

**Methods:**

```python
from vnstock import Finance

finance = Finance(source="vci", symbol="VCB")

# Báo cáo tài chính
income = finance.income_statement(period="year")      # Báo cáo thu nhập
balance = finance.balance_sheet(period="quarter")     # Bảng cân đối
cashflow = finance.cash_flow(period="year")           # Dòng tiền
ratios = finance.ratio(period="year")                 # Chỉ số tài chính
```

**Hỗ trợ Periods:**

- `year` - Hàng năm
- `quarter` - Hàng quý

---

### Tầng 4: Alternative Data (Dữ Liệu Thay Thế)

**Mục đích:** Tin tức, sự kiện, dữ liệu tiện ích

**Dữ Liệu Hiện Có:**

- **Company.news()**: Tin tức công ty
- **Misc utilities**: Giá vàng, tỷ giá ngoại tệ

**Methods:**

```python
from vnstock import Company
from vnstock.explorer.misc import GoldPrice, ExchangeRate

# Tin tức
company = Company(source="vci", symbol="VCB")
news = company.news()

# Giá vàng
gold = GoldPrice()
gold_price = gold.get_latest()

# Tỷ giá ngoại tệ
fx = ExchangeRate()
usd_vnd = fx.get_rate("USD", "VND")
```

---

### Tầng 5-7: Analytics, Macro, Insights

**Trạng thái:** Chưa triển khai đầy đủ

- **Layer 5 (Analytics)**: Chỉ số kỹ thuật, mô hình định giá, vv (chưa đầy đủ) - có thư viện vnstock_ta cung cấp tính toán bộ chỉ báo kỹ thuật.​
- **Layer 6 (Macro)**: Chỉ số kinh tế, hàng hóa - chỉ có trong thư viện vnstock_data yêu cầu tham gia gói tài trợ Vnstock.
- **Layer 7 (Insights)**: Screener, rankings top stocks, vv - (Chưa đầy đủ) - chỉ có trong thư viện vnstock_data yêu cầu tham gia gói tài trợ Vnstock.

---

## 📋 Các APIs & Dữ Liệu Hiện Có

### 1. Quote API - Dữ Liệu Giá

| Method          | Mô Tả                        | Sources            |
| --------------- | ---------------------------- | ------------------ |
| `history()`     | Dữ liệu lịch sử OHLCV        | KBS, VCI, MSN, FMP |
| `intraday()`    | Dữ liệu giao dịch trong ngày | KBS, VCI           |
| `price_depth()` | Sổ lệnh (order book)         | KBS, VCI           |

**Ứng Dụng:** Phân tích kỹ thuật, backtest chiến lược, tính toán chỉ số

---

### 2. Company API - Thông Tin Công Ty

| Method              | Mô Tả               | Sources             |
| ------------------- | ------------------- | ------------------- |
| `overview()`        | Thông tin tổng quan | KBS, VCI, TCBS, FMP |
| `officers()`        | Ban lãnh đạo        | KBS, VCI, TCBS      |
| `shareholders()`    | Cổ đông lớn         | KBS, VCI, TCBS      |
| `subsidiaries()`    | Công ty con         | KBS, VCI, TCBS      |
| `news()`            | Tin tức             | KBS, VCI, TCBS      |
| `capital_history()` | Lịch sử vốn         | KBS only            |
| `ratio_summary()`   | Tóm tắt chỉ số      | VCI only            |

**Ứng Dụng:** Nghiên cứu công ty, phân tích quản trị, theo dõi thay đổi cấp quản lý

---

### 3. Finance API - Báo Cáo Tài Chính

| Method               | Mô Tả                | Sources             |
| -------------------- | -------------------- | ------------------- |
| `income_statement()` | Báo cáo thu nhập     | KBS, VCI, TCBS, FMP |
| `balance_sheet()`    | Bảng cân đối kế toán | KBS, VCI, TCBS, FMP |
| `cash_flow()`        | Báo cáo dòng tiền    | KBS, VCI, TCBS, FMP |
| `ratio()`            | Chỉ số tài chính     | KBS, VCI, TCBS, FMP |

**Ứng Dụng:** Phân tích cơ bản, định giá công ty, so sánh ngành

---

### 4. Trading API - Dữ Liệu Giao Dịch

| Method            | Mô Tả              | Sources        |
| ----------------- | ------------------ | -------------- |
| `price_board()`   | Bảng giá realtime  | KBS, VCI, TCBS |
| `price_history()` | Lịch sử giá        | VCI only       |
| `trading_stats()` | Thống kê giao dịch | VCI only       |
| `side_stats()`    | Thống kê mua/bán   | VCI only       |

**Ứng Dụng:** Theo dõi giá thị trường, phân tích dòng tiền

---

### 5. Listing API - Danh Sách Chứng Khoán

| Method                  | Mô Tả                 | Sources            |
| ----------------------- | --------------------- | ------------------ |
| `all_symbols()`         | Tất cả mã chứng khoán | KBS, VCI, MSN, FMP |
| `symbols_by_exchange()` | Mã theo sàn           | VCI only           |
| `government_bonds()`    | Trái phiếu chính phủ  | VCI only           |
| `indices()`             | Danh sách chỉ số      | VCI, MSN, FMP      |

**Ứng Dụng:** Xây dựng danh sách chứng khoán, lọc theo tiêu chí

---

### 6. Misc/Utils - Dữ Liệu Tiện Ích

| Module         | Mô Tả           | Source       |
| -------------- | --------------- | ------------ |
| `GoldPrice`    | Giá vàng        | Web scraping |
| `ExchangeRate` | Tỷ giá ngoại tệ | Web scraping |

**Ứng Dụng:** Theo dõi giá vàng, chuyển đổi tiền tệ

---

## 🔌 Nguồn Dữ Liệu & Connectors

### Explorer (Web Scraping)

| Nguồn       | Domain       | Hỗ Trợ                                    | Phương Pháp  | Trạng Thái      |
| ----------- | ------------ | ----------------------------------------- | ------------ | --------------- |
| **VCI**     | vci.com.vn   | Quote, Listing, Company, Finance, Trading | Web Scraping | ✅ Hoạt động    |
| **KBS**     | kbsec.com.vn | Quote, Listing, Company, Finance, Trading | Web Scraping | ✅ Mới (v3.4.0) |
| **MSN**     | msn.com      | Quote, Listing                            | Web Scraping | ✅ Hoạt động    |
| **FMarket** | fmarket.vn   | Listing (Fund)                            | Web Scraping | ✅ Hoạt động    |
| **TCBS**    | tcbs.com.vn  | Quote, Listing, Company, Finance, Trading | Web Scraping | ⚠️ Ngưng hỗ trợ  |

### Connector (Official APIs)

| API         | Domain                    | Đặc Điểm                   | Chi Phí  | Trạng Thái   |
| ----------- | ------------------------- | -------------------------- | -------- | ------------ |
| **FMP**     | financialmodelingprep.com | Dữ liệu tài chính toàn cầu | Freemium | ✅ Hoạt động |
| **DNSE**    | dnse.vn                   | API giao dịch  | Miễn phí   | ✅ Hoạt động |
| **Binance** | binance.com               | Dữ liệu crypto             | Miễn phí | 📋 Sắp tới  |

---

## 🛠️ Core Utilities

Vnstock cung cấp các utilities hỗ trợ:

### Market Utilities (`core/utils/market.py`)

- `trading_hours()` - Lấy giờ giao dịch
- `is_trading_hour()` - Kiểm tra giờ giao dịch
- `market_status()` - Trạng thái thị trường (preparing, real_time, settling, historical_only)

### Interval Utilities (`core/utils/interval.py`)

- Chuẩn hóa timeframe: `1D`, `1H`, `1m`, `5m`, `15m`, `30m`, `1W`, `1M`
- Hỗ trợ aliases: `d`, `h`, `m`, `w`, `M`

### Lookback Utilities (`core/utils/lookback.py`)

- Xử lý lookback periods: `1M`, `3M`, `6M`, `1Y`, `3Y`, `5Y`, `100D`, v.v.

### Transform Utilities (`core/utils/transform.py`)

- Chuyển đổi format: Long ↔ Wide, DataFrame ↔ JSON

### Validation & Auth

- `validation.py` - Kiểm tra dữ liệu

---

## 📈 Các Loại Dữ Liệu Chi Tiết

### 1. Dữ Liệu Giá (Quote Data)

```
- Giá lịch sử: Open, High, Low, Close, Volume
- Dữ liệu trong ngày (Intraday)
- Bảng giá realtime
- Độ sâu giá (Price Depth / Order Book)
```

### 2. Dữ Liệu Danh Sách (Listing Data)

```
- Tất cả mã chứng khoán
- Lọc theo sàn giao dịch (HOSE, HNX, UPCOM)
- Lọc theo ngành (ICB Industries)
- Lọc theo chỉ số (VN30, VNMID, VNSML, v.v.)
- Futures, Bonds, Warrants, Funds
```

### 3. Dữ Liệu Công Ty (Company Data)

```
- Hồ sơ công ty
- Thông tin cổ đông chính
- Danh sách nhân viên quản lý
- Công ty con & chi nhánh
- Tin tức & sự kiện
```

### 4. Dữ Liệu Tài Chính (Financial Data)

```
- Báo cáo tài chính:
  ├─ Bảng cân đối kế toán (Balance Sheet)
  ├─ Báo cáo kết quản kinh doanh (Income Statement)
  ├─ Lưu chuyển tiền tệ (Cash Flow)
  └─ Chỉ số tài chính (Ratios)
- Theo kỳ: Hàng quý (Quarter) hoặc hàng năm (Year)
```

### 5. Dữ Liệu Giao Dịch (Trading Data)

```
- Khối lượng giao dịch
- Giá trị giao dịch
- Giao dịch cổ đông lớn
- Lịch sử chia cổ tức
```

---

## 💱 Sàn Giao Dịch (Exchanges)

```
- HOSE: Sở giao dịch Hà Nội (HOSE) - Thị trường chính
- HNX: Sở giao dịch Hà Nội (HNX) - Thị trường phụ
- UPCOM: Thị trường chứng khoán chưa niêm yết (UPCOM)
```

---

## 📑 Chỉ Số Thị Trường (Indices)

### Chỉ Số HOSE (6 chỉ số)

- **VN30**: 30 cổ phiếu vốn hóa lớn nhất & thanh khoản tốt nhất
- **VN100**: 100 cổ phiếu có vốn hoá lớn nhất HOSE
- **VNMID**: Mid-Cap Index - nhóm cổ phiếu vốn hóa trung bình
- **VNSML**: Small-Cap Index - nhóm cổ phiếu vốn hóa nhỏ
- **VNALL**: Tất cả cổ phiếu trên HOSE và HNX
- **VNSI**: Vietnam Small-Cap Index

### Chỉ Số Ngành (10 chỉ số ICB)

- **VNIT**: Công nghệ thông tin
- **VNIND**: Công nghiệp
- **VNCONS**: Hàng tiêu dùng
- **VNCOND**: Hàng tiêu dùng thiết yếu
- **VNHEAL**: Chăm sóc sức khoẻ
- **VNENE**: Năng lượng
- **VNUTI**: Dịch vụ tiện ích
- **VNREAL**: Bất động sản
- **VNFIN**: Tài chính
- **VNMAT**: Nguyên vật liệu

### Chỉ Số Đầu Tư (3 chỉ số)

- **VNDIAMOND**: Chỉ số các cổ phiếu có triển vọng lớn
- **VNFINLEAD**: Chỉ số tài chính đầu ngành
- **VNFINSELECT**: Chỉ số tài chính được chọn lọc

---

## 🔄 Cách Sử Dụng Cơ Bản

### Khởi Tạo

```python
from vnstock import Quote, Listing, Company, Finance, Trading

# Quote - Giá chứng khoán
quote = Quote(source="vci", symbol="VCB")

# Listing - Danh sách chứng khoán
listing = Listing(source="vci")

# Company - Dữ liệu công ty
company = Company(source="vci", symbol="VCB")

# Finance - Dữ liệu tài chính
finance = Finance(source="vci", symbol="VCB")

# Trading - Dữ liệu giao dịch
trading = Trading(source="vci")
```

### Parameters Phổ Biến

```python
# Common parameters
Quote(
    source="vci",           # Nguồn dữ liệu: vci, kbs, msn, fmp, etc.
    symbol="VCB",           # Mã chứng khoán
    random_agent=False,     # Sử dụng random user agent
    show_log=False          # Hiển thị log chi tiết
)
```

### Chỉ Định Source

```python
from vnstock.core.types import DataSource

# Liệt kê tất cả available sources
print(DataSource.all_sources())
# Output: ['vci', 'kbs', 'msn', 'dnse', 'fmp', 'fmarket']

# Sử dụng enum
quote_vci = Quote(source=DataSource.VCI, symbol="VCB")
quote_kbs = Quote(source=DataSource.KBS, symbol="VCB")
quote_msn = Quote(source=DataSource.MSN, symbol="VCB")

# ⚠️ TCBS đã ngưng được hỗ trợ, không nên sử dụng
```

---

## 🛡️ Xử Lý Lỗi & Retry

Vnstock tự động xử lý lỗi tạm thời với:

- **Retry tự động**: Tối đa 5 lần (có thể cấu hình)
- **Exponential Backoff**: Tăng độ trễ giữa các lần thử
- **Timeout thông minh**: Tránh treo khi kết nối chậm

```python
from vnstock.config import Config

# Tuỳ chỉnh retry behavior
Config.RETRIES = 3  # Số lần retry
Config.BACKOFF_MULTIPLIER = 2  # Hệ số backoff
Config.BACKOFF_MIN = 1  # Độ trễ tối thiểu (giây)
Config.BACKOFF_MAX = 30  # Độ trễ tối đa (giây)
```

---

## 📚 Cấu Trúc Dữ Liệu Trả Về

### DataFrame (Pandas)

Hầu hết các phương thức trả về `pd.DataFrame`:

```python
df = quote.history(
    symbol="VCB",
    start="2024-01-01",
    end="2024-12-31"
)

# Output: DataFrame với các cột
# Columns: time, open, high, low, close, volume, value
```

### Dictionary

Một số phương thức trả về `dict`:

```python
profile = company.overview()

# Output: Dictionary với thông tin công ty
# {
#     'symbol': 'VCB',
#     'company_name': '...',
#     'exchange': 'HOSE',
#     ...
# }
```

### List

Danh sách:

```python
symbols = listing.all_symbols()

# Output: List of strings
# ['AAA', 'AAH', 'AAT', 'ABS', 'ABT', ...]
```

---

## ✅ Kiểm Tra Lỗi Thường Gặp

### 1. ValueError: Invalid Source

```python
# ❌ Sai
quote = Quote(source="invalid_source", symbol="VCB")

# ✅ Đúng
quote = Quote(source="vci", symbol="VCB")
```

### 2. NotImplementedError

```python
# ❌ Sai - MSN không hỗ trợ Finance
finance = Finance(source="msn", symbol="VCB")
df = finance.balance_sheet()  # NotImplementedError

# ✅ Đúng - Sử dụng KBS hoặc VCI
finance = Finance(source="kbs", symbol="VCB")
df = finance.balance_sheet()
```

### 3. TCBS Deprecated

```python
# ❌ Không nên sử dụng
quote = Quote(source="tcbs", symbol="VCB")

# ✅ Sử dụng KBS hoặc VCI thay thế
quote = Quote(source="vci", symbol="VCB")
```

---

## 🔗 Bước Tiếp Theo

1. **[02-Installation](02-installation.md)** - Cài đặt & cấu hình
2. **[03-Listing API](03-listing-api.md)** - Tìm kiếm chứng khoán
3. **[04-Quote & Price](04-quote-price-api.md)** - Giá lịch sử & realtime
4. **[05-Financial API](05-financial-api.md)** - Dữ liệu tài chính
5. **[06-Company API](06-company-api.md)** - Thông tin công ty
6. **[07-Trading API](07-trading-api.md)** - Dữ liệu giao dịch
7. **[08-Best Practices](08-best-practices.md)** - Mẹo & kinh nghiệm

---

**Last Updated**: Tháng 1, 2026  

**Version**: 3.4.0  

**Status**: Hoạt động  

**Important**: TCBS đã ngưng được hỗ trợ, sẽ bị loại bỏ vào khoảng tháng 3/2026.