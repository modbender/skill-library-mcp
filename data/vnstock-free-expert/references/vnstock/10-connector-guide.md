# 06 - Connector Guide - API Bên Ngoài

## 📖 Giới Thiệu

VNStock hỗ trợ kết nối với các API dữ liệu tài chính bên ngoài, giúp bạn lấy dữ liệu từ nhiều nguồn:

- **FMP (Financial Modeling Prep)**: Dữ liệu tài chính toàn cầu.
- **XNO (XNO Data)**: Dữ liệu thị trường (market data) cho kiểm thử chiến lược định lượng.
- **DNSE (DNSE)**: API đặt lệnh.

## 🔌 Kiến Trúc Connector

```
┌────────────────────────────┐
│   Your Application Code    │
├────────────────────────────┤
│  Quote | Company | Finance │  ← API thống nhất
├────────────────────────────┤
│  Provider Registry         │
├────────────────────────────┤
│  Connector Implementations │
│  ┌──────────────────────┐  │
│  │  FMP | XNO | DNSE    │  │  ← Available sources
│  └──────────────────────┘  │
└────────────────────────────┘
```

## 📊 Các Nguồn Dữ Liệu Hỗ Trợ

vnstock hỗ trợ các connector API chính thức sau:

| Provider | Giá Lịch Sử | Tài Chính | Danh Sách | Ghi Chú |
|----------|:---:|:---:|:---:|---|
| **FMP** | ✅ | ✅ | ✅ | Cần API key, dữ liệu toàn cầu |
| **XNO** | ✅ | ❌ | ❌ | Cần API key, chứng khoán Việt Nam |
| **DNSE** | ✅ | ❌ | ❌ | Cần API key, API đặt lệnh |

## 🔑 FMP - Financial Modeling Prep

### Giới Thiệu

FMP cung cấp dữ liệu tài chính toàn cầu, bao gồm:

- Báo cáo tài chính (10K, 10Q)
- Giá lịch sử
- Chỉ số tài chính
- Dữ liệu macro kinh tế
- Dữ liệu crypto

**Website**: https://financialmodelingprep.com  
**API Key**: Có gói free và premium

### Cài Đặt

```bash
# FMP không cần thư viện bổ sung
# Chỉ cần API key
```

### Lấy API Key

1. Truy cập https://financialmodelingprep.com
2. Đăng ký tài khoản free
3. Lấy API key từ dashboard

### Cấu Hình

```python
import os
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv('FMP_API_KEY')

if not FMP_API_KEY:
    print("❌ Please set FMP_API_KEY in .env")
else:
    print("✅ FMP_API_KEY configured")
```

### Ví dụ Sử Dụng

```python
from vnstock import Quote
import os

# Đảm bảo FMP_API_KEY được set trong environment
if not os.getenv('FMP_API_KEY'):
    print("❌ Please set FMP_API_KEY environment variable")
    print("   export FMP_API_KEY='your_api_key'")
else:
    # Khởi tạo với FMP
    # Lưu ý: API key tự động đọc từ FMP_API_KEY environment variable
    quote = Quote(source="fmp", symbol="AAPL")
    
    # Lấy giá lịch sử
    df = quote.history(
        start="2024-01-01",
        end="2024-12-31",
        resolution="1D"
    )
    
    print(df.head())
```

## 🔑 XNO - XNO Data

### Giới Thiệu

XNO cung cấp dữ liệu chứng khoán Việt Nam:

- Giá lịch sử chi tiết
- Báo cáo tài chính công ty Việt Nam
- Dữ liệu thị trường
- Phân tích kỹ thuật

**Website**: https://xnoquant.vn  
**API Key**: Cần đăng ký (miễn phí)

### Cấu Hình

```python
import os
from dotenv import load_dotenv
from vnstock import Quote

load_dotenv()

XNO_API_KEY = os.getenv('XNO_API_KEY')

if not XNO_API_KEY:
    print("❌ Please set XNO_API_KEY in .env")
else:
    quote = Quote(source="xno", symbol="VCI")
    df = quote.history(
        start="2024-01-01",
        end="2024-12-31",
        resolution="1D"
    )
    print(df.head())
```

## 🔑 DNSE - DNSE API

### Giới Thiệu

DNSE cung cấp API giao dịch và dữ liệu từ Sở Giao Dịch Chứng Khoán Hà Nội:

- API đặt lệnh giao dịch
- Dữ liệu realtime
- Dữ liệu giao dịch

**Website**: https://www.dnse.vn  
**API Key**: Cần liên hệ (có phí)

### Cấu Hình

```python
import os
from dotenv import load_dotenv
from vnstock import Quote

load_dotenv()

DNSE_API_KEY = os.getenv('DNSE_API_KEY')

if not DNSE_API_KEY:
    print("❌ Please set DNSE_API_KEY in .env")
else:
    quote = Quote(source="dnse", symbol="VCI")
    df = quote.history(
        start="2024-01-01",
        end="2024-12-31",
        resolution="1D"
    )
    print(df.head())
```

## ⚠️ Các Connector Không Được Hỗ Trợ

### Binance

Các nguồn sau **không được hỗ trợ** trong phiên bản hiện tại của vnstock:

- **Binance**: Không có connector implementation

**Ghi chú**:

- Để lấy dữ liệu tiền điện tử: sử dụng các thư viện chuyên dụng (ví dụ: `python-binance`)





## 🔄 Chuyển Đổi Giữa Connectors

### Ví dụ: So Sánh Dữ Liệu từ FMP và XNO

```python
import os
from dotenv import load_dotenv
from vnstock import Quote

load_dotenv()

FMP_API_KEY = os.getenv('FMP_API_KEY')
XNO_API_KEY = os.getenv('XNO_API_KEY')

# Lấy dữ liệu từ FMP (cổ phiếu quốc tế)
if FMP_API_KEY:
    quote_fmp = Quote(source="fmp", symbol="AAPL")
    df_fmp = quote_fmp.history(start="2024-01-01", end="2024-12-31", resolution="1D")
    print(f"FMP AAPL: {len(df_fmp)} records")

# Lấy dữ liệu từ XNO (cổ phiếu Việt Nam)
if XNO_API_KEY:
    quote_xno = Quote(source="xno", symbol="VCI")
    df_xno = quote_xno.history(start="2024-01-01", end="2024-12-31", resolution="1D")
    print(f"XNO VCI: {len(df_xno)} records")
```

## 🛡️ Error Handling

### Xử Lý API Key Missing

```python
import os
from dotenv import load_dotenv
from vnstock import Quote

load_dotenv()

def get_quote_with_fallback(symbol, symbol_type="international"):
    """Cố gắng kết nối đến connector với fallback strategy"""
    
    if symbol_type == "international":
        fmp_key = os.getenv('FMP_API_KEY')
        if fmp_key:
            try:
                quote = Quote(source="fmp", symbol=symbol)
                return quote, "fmp"
            except Exception as e:
                print(f"❌ FMP failed: {e}")
    else:
        xno_key = os.getenv('XNO_API_KEY')
        if xno_key:
            try:
                quote = Quote(source="xno", symbol=symbol)
                return quote, "xno"
            except Exception as e:
                print(f"❌ XNO failed: {e}")
    
    return None, None

quote, source = get_quote_with_fallback("AAPL", "international")
if quote:
    df = quote.history(start="2024-01-01", end="2024-12-31")
    print(f"✅ Data from {source}: {len(df)} records")
else:
    print("❌ Could not initialize quote from any connector")
```

### Xử Lý Rate Limiting

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from vnstock import Quote

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(quote, start, end):
    return quote.history(start=start, end=end, resolution="1D")

quote = Quote(source="fmp", symbol="AAPL")
df = fetch_with_retry(quote, "2024-01-01", "2024-12-31")
print(f"✅ Data fetched: {len(df)} rows")
```

## 📊 Multi-Source Data Collection

### Ví dụ: Thu Thập Dữ Liệu từ Nhiều Connector

```python
from vnstock import Quote
import os
from dotenv import load_dotenv

load_dotenv()

# Danh sách connector cần thử
CONNECTORS = {
    "fmp": {
        "api_key": os.getenv('FMP_API_KEY'),
        "symbols": ["AAPL", "MSFT"]
    },
    "xno": {
        "api_key": os.getenv('XNO_API_KEY'),
        "symbols": ["VCI", "ACB"]
    },
    "dnse": {
        "api_key": os.getenv('DNSE_API_KEY'),
        "symbols": ["VCI", "BID"]
    }
}

results = {}

for connector, config in CONNECTORS.items():
    api_key = config.get('api_key')
    
    if not api_key:
        print(f"⚠️  {connector}: No API key found")
        continue
    
    results[connector] = {}
    
    for symbol in config['symbols']:
        try:
            quote = Quote(source=connector, symbol=symbol)
            df = quote.history(
                start="2024-01-01",
                end="2024-12-31",
                resolution="1D"
            )
            
            results[connector][symbol] = {
                'success': True,
                'rows': len(df)
            }
            print(f"✅ {connector:10} {symbol:10}: {len(df)} records")
        except Exception as e:
            results[connector][symbol] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ {connector:10} {symbol:10}: {str(e)[:40]}")
```

## 💡 Best Practices

### 1. Caching để Giảm API Calls

```python
import pickle
import os
import datetime
from vnstock import Quote

CACHE_DIR = 'cache'
CACHE_TTL = 3600  # 1 hour

def get_quote_data_cached(source, symbol, start, end):
    cache_file = f"{CACHE_DIR}/{source}_{symbol}_{start}_{end}.pkl"
    
    # Kiểm tra cache
    if os.path.exists(cache_file):
        file_age = datetime.datetime.now().timestamp() - os.path.getmtime(cache_file)
        if file_age < CACHE_TTL:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # Fetch từ connector API
    quote = Quote(source=source, symbol=symbol)
    df = quote.history(start=start, end=end, resolution="1D")
    
    # Save to cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(df, f)
    
    return df

df = get_quote_data_cached("fmp", "AAPL", "2024-01-01", "2024-12-31")
print(f"✅ Data loaded (from cache or API): {len(df)} rows")
```

### 2. Rate Limiting

```python
import time
from vnstock import Quote

def fetch_multiple_symbols(symbols, source="fmp"):
    """Fetch từ connector với rate limiting"""
    results = {}
    
    for i, symbol in enumerate(symbols):
        try:
            quote = Quote(source=source, symbol=symbol)
            df = quote.history(
                start="2024-01-01",
                end="2024-12-31",
                resolution="1D"
            )
            results[symbol] = df
            print(f"✅ {symbol}: {len(df)} records")
            
            # Rate limiting: chờ giữa các requests
            if i < len(symbols) - 1:
                time.sleep(1)
        except Exception as e:
            print(f"❌ {symbol}: {type(e).__name__}")
    
    return results

symbols = ["AAPL", "MSFT", "GOOGL"]
data = fetch_multiple_symbols(symbols, source="fmp")
print(f"✅ Fetched data for {len(data)} symbols")
```

## ❌ Troubleshooting

### Lỗi 1: Invalid API Key

```
Error: Invalid API Key
```

**Giải pháp:**
- Kiểm tra API key trong .env
- Kiểm tra quyền truy cập API
- Nếu free tier, có thể bị rate limit

### Lỗi 2: Source Not Supported

```
Error: Source 'invalid_source' is not supported
```

**Giải pháp:**
- Kiểm tra danh sách hỗ trợ: `DataSource.all_sources()`
- Đảm bảo source name chính xác

### Lỗi 3: No Data Available

```
Error: No data available for this symbol/date range
```

**Giải pháp:**
- Kiểm tra symbol có hợp lệ không
- Kiểm tra date range (không quá lâu)
- Thử symbol khác để test

## 📚 Bước Tiếp Theo

1. [02-Installation](02-installation.md) - Cài đặt
2. [01-Overview](01-overview.md) - Tổng quan
3. [03-Listing API](03-listing-api.md) - Danh sách chứng khoán
4. [04-Quote & Price](04-quote-price-api.md) - Giá lịch sử
5. [05-Financial API](05-financial-api.md) - Dữ liệu tài chính
6. ✅ **06-Connector Guide** - Bạn đã ở đây
7. [07-Best Practices](07-best-practices.md) - Mẹo & kinh nghiệm

---

**Last Updated**: 2024-12-03  
**Version**: 3.3.0  
**Status**: Actively Maintained
