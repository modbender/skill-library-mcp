# 07 - Best Practices - Mẹo & Kinh Nghiệm

## 📖 Giới Thiệu

Tài liệu này cung cấp các mẹo, kinh nghiệm, và best practices khi sử dụng VNStock.

## 🚀 Performance & Optimization

### 1. Batch Processing - Xử Lý Hàng Loạt

Khi lấy dữ liệu cho nhiều cổ phiếu, khởi tạo một lần và thay đổi symbol:

```python
from vnstock import Quote

symbols = ['VCI', 'ACB', 'BID', 'CTG', 'SBT']
quote = Quote(source="vci", symbol="VCI")

results = {}
for symbol in symbols:
    quote.symbol = symbol
    df = quote.history(start="2024-01-01", end="2024-12-31", resolution="1D")
    results[symbol] = df
    print(f"✅ {symbol}: {len(df)} rows")

# Xử lý kết quả
for symbol, df in results.items():
    print(f"{symbol}: {len(df)} dòng dữ liệu")
```

### 2. Caching - Lưu Trữ Tạm

```python
import pickle
import os
from datetime import datetime, timedelta

class QuoteCache:
    def __init__(self, cache_dir='./cache', ttl_hours=24):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, source, symbol, start, end):
        return f"{self.cache_dir}/{source}_{symbol}_{start}_{end}.pkl"
    
    def _is_cache_valid(self, filepath):
        if not os.path.exists(filepath):
            return False
        age = datetime.now().timestamp() - os.path.getmtime(filepath)
        return age < self.ttl_seconds
    
    def get(self, source, symbol, start, end):
        from vnstock import Quote
        
        cache_path = self._get_cache_path(source, symbol, start, end)
        
        # Từ cache nếu còn hợp lệ
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        
        # Fetch từ API
        quote = Quote(source=source, symbol=symbol)
        df = quote.history(start=start, end=end)
        
        # Lưu cache
        with open(cache_path, 'wb') as f:
            pickle.dump(df, f)
        
        return df

# Sử dụng
cache = QuoteCache(ttl_hours=24)
df = cache.get("vci", "VCI", "2024-01-01", "2024-12-31")
print(f"✅ Loaded {len(df)} rows (from cache or API)")
```

### 3. Connection Pooling - Tái Sử Dụng Kết Nối

```python
from vnstock import Quote
import threading
from queue import Queue

class QuotePool:
    """Thư viện Quote Connection Pool"""
    
    def __init__(self, source="vci", pool_size=5):
        self.source = source
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(Quote(source=source))
    
    def get_quote(self, symbol):
        quote = self.pool.get()
        quote.symbol = symbol
        return quote
    
    def return_quote(self, quote):
        self.pool.put(quote)
    
    def fetch_history(self, symbol, start, end):
        quote = self.get_quote(symbol)
        try:
            df = quote.history(start=start, end=end)
            return df
        finally:
            self.return_quote(quote)

# Sử dụng
pool = QuotePool(source="vci", pool_size=3)
df = pool.fetch_history("VCI", "2024-01-01", "2024-12-31")
print(f"✅ Fetched {len(df)} rows")
```

## 🛡️ Error Handling & Resilience

### 1. Retry Logic - Xử Lý Lỗi Tạm Thời

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import requests

@retry(
    retry=retry_if_exception_type((requests.RequestException, TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(quote, start, end):
    return quote.history(start=start, end=end)

from vnstock import Quote

quote = Quote(source="vci", symbol="VCI")
df = fetch_with_retry(quote, "2024-01-01", "2024-12-31")
print(f"✅ Data fetched: {len(df)} rows")
```

### 2. Circuit Breaker - Dừng Khi Lỗi Liên Tục

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_seconds=60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    def call(self, func, *args, **kwargs):
        if self.is_open:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.is_open = False
                self.failure_count = 0
            else:
                raise Exception("Circuit Breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                raise Exception(f"Circuit Breaker opened after {self.failure_count} failures")
            
            raise e

# Sử dụng
from vnstock import Quote

circuit = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
quote = Quote(source="vci", symbol="VCI")

try:
    df = circuit.call(
        quote.history,
        start="2024-01-01",
        end="2024-12-31"
    )
    print(f"✅ Data fetched: {len(df)} rows")
except Exception as e:
    print(f"❌ Error: {e}")
```

### 3. Fallback - Dự Phòng

```python
from vnstock import Quote

def get_price_data_with_fallback(symbol, start, end):
    """Thử các source theo thứ tự ưu tiên"""
    
    sources = ["vci", "tcbs"]  # Web scraping sources (fallback options)
    
    for source in sources:
        try:
            quote = Quote(source=source, symbol=symbol)
            df = quote.history(start=start, end=end)
            print(f"✅ Got data from {source}")
            return df
        except Exception as e:
            print(f"⚠️ {source} failed: {e}")
            continue
    
    raise Exception("All sources failed!")

# Sử dụng
try:
    df = get_price_data_with_fallback("VCI", "2024-01-01", "2024-12-31")
except Exception as e:
    print(f"❌ {e}")
```

## 📊 Data Quality & Validation

### 1. Data Validation - Kiểm Tra Chất Lượng Dữ Liệu

```python
import pandas as pd
from vnstock import Quote

def validate_quote_data(df):
    """Kiểm tra dữ liệu giá"""
    
    issues = []
    
    # 1. Kiểm tra cột bắt buộc
    required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")
    
    # 2. Kiểm tra dữ liệu trống
    if df.isnull().any().any():
        issues.append(f"Found {df.isnull().sum().sum()} null values")
    
    # 3. Kiểm tra logic OHLC (High >= Low >= Close >= Open)
    invalid = (df['high'] < df['low']).sum()
    if invalid > 0:
        issues.append(f"Found {invalid} rows where High < Low")
    
    # 4. Kiểm tra volume > 0
    zero_vol = (df['volume'] == 0).sum()
    if zero_vol > 0:
        issues.append(f"Found {zero_vol} rows with zero volume")
    
    # 5. Kiểm tra time series liên tục
    if 'time' in df.columns:
        df_sorted = df.sort_values('time')
        time_gaps = df_sorted['time'].diff()
        max_gap = time_gaps.max()
        issues.append(f"Max time gap: {max_gap}")
    
    if issues:
        print("⚠️ Data Quality Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Data quality check passed")
        return True

# Sử dụng
quote = Quote(source="vci", symbol="VCI")
df = quote.history(start="2024-01-01", end="2024-12-31")
validate_quote_data(df)
```

### 2. Outlier Detection - Phát Hiện Bất Thường

```python
import pandas as pd
import numpy as np

def detect_outliers(df, column='close', threshold=3):
    """Phát hiện giá trị bất thường sử dụng Z-score"""
    
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    outliers = df[z_scores > threshold]
    
    if len(outliers) > 0:
        print(f"⚠️ Found {len(outliers)} outliers:")
        print(outliers[['time', 'open', 'high', 'low', 'close']])
    else:
        print("✅ No outliers detected")
    
    return outliers

# Sử dụng
from vnstock import Quote

quote = Quote(source="vci", symbol="VCI")
df = quote.history(start="2024-01-01", end="2024-12-31")
detect_outliers(df, column='close', threshold=3)
```

## 🔐 Security & Privacy

### 1. API Key Management

```python
import os
from dotenv import load_dotenv

# ❌ Sai - API key hardcoded
api_key = "abc123def456"

# ✅ Đúng - Từ environment variable
load_dotenv()
api_key = os.getenv('API_KEY')

if not api_key:
    raise ValueError("API_KEY not set in environment")
```

### 2. Secure Configuration

```python
# .env file (gitignored)
FMP_API_KEY=your_key_here
XNO_API_KEY=your_key_here
DNSE_API_KEY=your_key_here

# .gitignore
.env
*.key
*.secret
```

### 3. Encrypted Storage

```python
from cryptography.fernet import Fernet
import json

class SecureConfig:
    def __init__(self, config_file=".secure_config"):
        self.config_file = config_file
    
    def save(self, data, password):
        cipher = Fernet(password.encode().ljust(32)[:32])
        encrypted = cipher.encrypt(json.dumps(data).encode())
        with open(self.config_file, 'wb') as f:
            f.write(encrypted)
    
    def load(self, password):
        cipher = Fernet(password.encode().ljust(32)[:32])
        with open(self.config_file, 'rb') as f:
            encrypted = f.read()
        return json.loads(cipher.decrypt(encrypted).decode())

# Sử dụng
config = SecureConfig()
config.save({
    'fmp_key': 'your_key',
    'xno_key': 'your_key'
}, password='secure_password')
```

## 📈 Logging & Monitoring

### 1. Setup Logging

```python
import logging
import sys

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vnstock.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Sử dụng
from vnstock import Quote

try:
    logger.info("Fetching VCI price data...")
    quote = Quote(source="vci", symbol="VCI")
    df = quote.history(start="2024-01-01", end="2024-12-31")
    logger.info(f"✅ Successfully fetched {len(df)} rows")
except Exception as e:
    logger.error(f"❌ Error: {e}", exc_info=True)
```

### 2. Performance Monitoring

```python
import time
import logging

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator để monitor performance"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        
        if elapsed > 5:  # Warning nếu > 5 giây
            logger.warning(f"{func.__name__} took too long: {elapsed:.2f}s")
        
        return result
    return wrapper

# Sử dụng
from vnstock import Quote

@monitor_performance
def fetch_vci_data():
    quote = Quote(source="vci", symbol="VCI")
    return quote.history(start="2024-01-01", end="2024-12-31")

df = fetch_vci_data()
```

## 📚 Testing

### 1. Unit Testing

```python
import unittest
from unittest.mock import Mock, patch
from vnstock import Quote
import pandas as pd

class TestQuoteAPI(unittest.TestCase):
    def setUp(self):
        self.quote = Quote(source="vci", symbol="VCI")
    
    def test_history_returns_dataframe(self):
        df = self.quote.history(start="2024-01-01", end="2024-01-31")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
    
    def test_history_columns_exist(self):
        df = self.quote.history(start="2024-01-01", end="2024-01-31")
        required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            self.assertIn(col, df.columns)
    
    @patch('vnstock.Quote.history')
    def test_history_with_mock(self, mock_history):
        mock_history.return_value = pd.DataFrame({
            'time': ['2024-01-01'],
            'open': [21.0],
            'high': [21.5],
            'low': [20.8],
            'close': [21.4],
            'volume': [1000000]
        })
        
        df = self.quote.history(start="2024-01-01", end="2024-01-01")
        self.assertEqual(len(df), 1)

if __name__ == '__main__':
    unittest.main()
```

Chạy test:

```bash
python -m unittest test_quote.py
```

## 🔗 Integration Examples

### Real-world: Stock Screener

```python
from vnstock import Quote, Listing, Finance
import pandas as pd

def screen_stocks(min_pe=15, max_pe=25):
    """Tìm cổ phiếu theo tiêu chí P/E"""
    
    listing = Listing(source="vci")
    all_stocks = listing.all_symbols(to_df=True)
    
    results = []
    for idx, row in all_stocks.iterrows():
        symbol = row['symbol']
        
        try:
            # Lấy giá hiện tại
            quote = Quote(source="vci", symbol=symbol)
            df = quote.history(start="2024-11-01", end="2024-12-03")
            current_price = df['close'].iloc[-1] if len(df) > 0 else None
            
            # Lấy dữ liệu tài chính
            finance = Finance(source="vci", symbol=symbol)
            ratios = finance.ratio()
            pe = ratios.iloc[0].get('pe_ratio') if len(ratios) > 0 else None
            
            # Kiểm tra tiêu chí
            if pe and min_pe <= pe <= max_pe:
                results.append({
                    'symbol': symbol,
                    'price': current_price,
                    'pe_ratio': pe
                })
        except:
            pass
    
    return pd.DataFrame(results)

# Sử dụng
screened = screen_stocks(min_pe=15, max_pe=25)
print(screened.sort_values('pe_ratio'))
```

## 📚 Bước Tiếp Theo

1. [02-Installation](02-installation.md) - Cài đặt
2. [01-Overview](01-overview.md) - Tổng quan
3. [03-Listing API](03-listing-api.md) - Danh sách chứng khoán
4. [04-Quote & Price](04-quote-price-api.md) - Giá lịch sử
5. [05-Financial API](05-financial-api.md) - Dữ liệu tài chính
6. [06-Connector Guide](06-connector-guide.md) - API bên ngoài
7. ✅ **07-Best Practices** - Bạn đã ở đây

---

**Last Updated**: 2024-12-03  
**Version**: 3.3.0  
**Status**: Actively Maintained
