# 02 - Cài Đặt & Cấu Hình

## 📦 Yêu Cầu Hệ Thống

- **Python**: 3.8 hoặc cao hơn (khuyến nghị 3.10+)
- **OS**: Windows, macOS, hoặc Linux
- **Internet**: Kết nối internet ổn định

## 🚀 Cài Đặt Nhanh

### Option 1: Cài từ PyPI (Stable)

```bash
pip install vnstock
```

### Option 2: Cài từ GitHub (Latest Development)

```bash
pip install git+https://github.com/vnstock-lab/vnstock.git
```

### Option 3: Cài từ Local (Dev Version)

```bash
# Clone hoặc copy thư mục private_packages
pip install git+https://github.com/vnstock-lab/vnstock.git
```

## 📋 Dependencies

VNStock phụ thuộc vào các package sau:

```
pandas>=1.3.0          # Xử lý DataFrame
requests>=2.25.0       # HTTP requests
beautifulsoup4>=4.9.0  # Web scraping
lxml>=4.6.0            # XML parsing
pydantic>=1.8.0        # Data validation
tenacity>=8.0.0        # Retry logic
python-dateutil>=2.8.0 # Date utilities
aiohttp>=3.7.0         # Async HTTP
tqdm>=4.60.0           # Progress bars
packaging>=20.0        # Version parsing
python-dotenv>=0.19.0  # Env file support
```

### Cài đặt tự động (Recommended)

```bash
# Tất cả dependencies sẽ tự động được cài
pip install vnstock
```

### Cài đặt thủ công

```bash
pip install pandas requests beautifulsoup4 lxml pydantic tenacity \
    python-dateutil aiohttp tqdm packaging python-dotenv
```

## Xác Thực API Key

VNStock hỗ trợ các cấp độ sử dụng khác nhau với giới hạn requests tương ứng:

### Cấp Độ Sử Dụng

| Cấp độ | Giới hạn | Yêu cầu | Mô tả |
|--------|----------|---------|-------|
| **Khách (Guest)** | 20 requests/phút | Không cần đăng ký | Sử dụng miễn phí, giới hạn thấp |
| **Cộng đồng (Community)** | 60 requests/phút | Đăng ký miễn phí | Phù hợp cá nhân mới tìm hiểu |
| **Tài trợ (Sponsor)** | 180-600 requests/phút | Thành viên tài trợ| Dành cho nghiên cứu chuyên sâu |

### Đăng Ký API Key (Miễn Phí)

** 1. Đăng ký tương tác**

```python
from vnstock.core.utils.auth import register_user

# Chạy đăng ký tương tác
register_user()
```

Quá trình đăng ký sẽ:
1. Kiểm tra nếu đã có API key
2. Hướng dẫn đến trang đăng nhập: https://vnstocks.com/login
3. Nhập API key từ tài khoản Vnstock của người dùng
4. Lưu và xác thực API key

** 2. Đổi API key**

1. Truy cập https://vnstocks.com/login
2. Đăng nhập bằng tài khoản Google
3. Lấy API key từ trang quản lý tài khoản
4. Lưu API key bằng code:

```python
from vnstock.core.utils.auth import change_api_key

# Thay đổi API key
change_api_key("your_api_key_here")
```

### Kiểm Tra Trạng Thái

```python
from vnstock.core.utils.auth import check_status

# Kiểm tra trạng thái hiện tại
status = check_status()
# Output:
# ✓ API key: ab12***ef34
#   Tier: Community
#   Giới hạn: 60 requests/phút
```

### Sử Dụng Sau Khi Đăng Ký

Sau khi đăng ký API key, VNStock sẽ tự động sử dụng key cho tất cả requests:

```python
from vnstock import Quote, Listing

# Sẽ tự động sử dụng API key đã đăng ký
quote = Quote(source="KBS", symbol="VCI")
df = quote.history(start="2024-01-01", end="2024-12-31")

# Không cần cấu hình thêm gì!
```

### Lưu Ý Quan Trọng

- **API key được lưu trữ**: Không cần nhập lại. Nếu chạy trên môi trường Google Colab, sẽ phải lặp lại nhập API key mỗi lần sử dụng.
- **Miễn phí**: Sử dụng bậc miễn phí dành cho đào tạo cộng đồng với nhu cầu trải nghiệm thấp
- **Google OAuth**: Đăng nhập nhanh bằng tài khoản Google

## � Cấu Hình

### 1. Basic Configuration

VNStock có thể dùng ngay sau khi cài đặt mà không cần cấu hình:

```python
from vnstock import Quote, Listing

# Khởi tạo với KBS (khuyến nghị)
quote = Quote(source="KBS", symbol="VCI")
listing = Listing(source="KBS")

# Hoặc VCI
quote_kbs = Quote(source="VCI", symbol="VCI")
listing_kbs = Listing(source="VCI")
```

### 2. Environment Variables

Tạo file `.env` trong project directory:

```bash
# .env file
VNSTOCK_TIMEOUT=30
VNSTOCK_RETRIES=5
VNSTOCK_BACKOFF_MULTIPLIER=2
```

Load trong code:

```python
from dotenv import load_dotenv
import os

load_dotenv()

timeout = os.getenv('VNSTOCK_TIMEOUT', '30')
retries = os.getenv('VNSTOCK_RETRIES', '5')
```

### 3. Configuration Object

```python
from vnstock.config import Config

# Thay đổi cấu hình
Config.RETRIES = 3
Config.BACKOFF_MULTIPLIER = 2
Config.BACKOFF_MIN = 1
Config.BACKOFF_MAX = 30
Config.TIMEOUT = 30
```

### 4. External API Keys

Nếu sử dụng external APIs như FMP, XNO, DNSE:

```bash
# .env file
FMP_API_KEY=your_fmp_api_key_here
XNO_API_KEY=your_xno_api_key_here
DNSE_API_KEY=your_dnse_api_key_here
BINANCE_API_KEY=your_binance_key_here
BINANCE_API_SECRET=your_binance_secret_here
```

Load trong code:

```python
from vnstock import Quote
import os
from dotenv import load_dotenv

load_dotenv()

# Sử dụng FMP API
quote = Quote(
    source="fmp",
    symbol="VCI",
    api_key=os.getenv('FMP_API_KEY')
)
```

## ✅ Kiểm Tra Cài Đặt

### 1. Kiểm Tra Import

```python
# test_installation.py
import sys

print("📦 Checking imports...")

try:
    from vnstock import Quote, Listing, Company, Finance, Trading, Screener
    print("✅ All main classes imported successfully")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

try:
    from vnstock.core.types import DataSource, TimeFrame
    print("✅ Core types imported successfully")
except ImportError as e:
    print(f"❌ Core types Error: {e}")
    sys.exit(1)

try:
    from vnstock.constants import INDICES_INFO, EXCHANGES, SECTOR_IDS
    print("✅ Constants imported successfully")
except ImportError as e:
    print(f"❌ Constants Error: {e}")
    sys.exit(1)

print("\n📊 Available Data Sources:", DataSource.all_sources())
print("⚠️  Note: TCBS is deprecated, use VCI or KBS instead")
print("🆕 KBS is now available in v3.4.0")
print("⏱️ Available TimeFrames:", [t.value for t in TimeFrame])
print("\n✅ All checks passed!")
```

Chạy test:

```bash
python test_installation.py
```

### 2. Quick Test

```python
# quick_test.py
from vnstock import Quote, Listing
from vnstock.core.types import TimeFrame

print("Testing Quote...")# Khởi tạo với KBS (khuyến nghị)
quote = Quote(source="KBS", symbol="VCI")
print(f"✅ Quote initialized: {quote}")

print("\nTesting Listing...")
listing = Listing(source="KBS")
print(f"✅ Listing initialized: {listing}")

print("\n✅ Installation successful!")
```

## 🐛 Troubleshooting

### Issue 1: `ModuleNotFoundError: No module named 'vnstock'`

**Giải pháp:**

```bash
# Cài đặt lại
pip uninstall vnstock -y
pip install vnstock
```

### Issue 2: `ModuleNotFoundError: No module named 'pandas'`

**Giải pháp:**

```bash
# Cài dependencies
pip install pandas requests beautifulsoup4 lxml pydantic tenacity

# Hoặc cài toàn bộ
pip install vnstock --upgrade
```

### Issue 3: `ImportError: cannot import name 'Quote'`

**Giải pháp:**

```python
# ✅ Đúng cách import
from vnstock import Quote, Listing, Company

# ❌ Sai cách
from vnstock.Quote import Quote  # Không cần như này
```

### Issue 4: Network/Connection Errors

**Lỗi:**
```
requests.exceptions.ConnectionError: 
Failed to establish a new connection
```

**Giải pháp:**

```python
from vnstock import Quote
from vnstock.config import Config

# Tăng timeout
Config.TIMEOUT = 60

# Hoặc sử dụng proxy
quote = Quote(
    source="vci",
    symbol="VCI",
    proxy="http://your-proxy:port"
)
```

### Issue 5: Rate Limit / 429 Error

**Lỗi:**
```
HTTPError: 429 Too Many Requests
```

**Giải pháp:**

**Cách 1: Đăng ký API key miễn phí**

```python
from vnstock.core.utils.auth import register_user

# Đăng ký để tăng từ 20 lên 60 requests/phút
register_user()
```

**Cách 2: Tăng retry và delay**

```python
from vnstock.config import Config
import time

# Tăng delay giữa requests
Config.RETRIES = 5
Config.BACKOFF_MULTIPLIER = 3

# Hoặc thêm delay thủ công
def safe_request(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if "429" in str(e):
            time.sleep(5)  # Chờ 5 giây rồi thử lại
            return func(*args, **kwargs)
        raise

result = safe_request(quote.history, symbol="VCI", start_date="2024-01-01")
```

## 📖 Project Structure

Thư mục tiêu chuẩn khi làm việc với vnstock:

```
my_project/
├── .env                      # Cấu hình & API keys
├── .gitignore               # Bỏ qua .env khi commit
├── requirements.txt         # Dependencies
├── main.py                  # Code chính
├── data/                    # Lưu dữ liệu
│   └── cache/              # Cache dữ liệu
├── logs/                    # Log files
└── tests/
    └── test_vnstock.py      # Unit tests
```

### Ví dụ requirements.txt

```
vnstock>=3.4.0
vnai>=2.3.9
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.3.0
python-dotenv>=0.19.0
```

### Ví dụ .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/
*.csv
*.xlsx
logs/

# Cache
.cache/
*.pyc
```

## 🚀 Getting Started - Ví dụ Đơn Giản

### Ví dụ 1: Lấy Danh Sách Cổ Phiếu

```python
# example1_list_symbols.py
from vnstock import Listing

# Khởi tạo với KBS (khuyến nghị)
listing = Listing(source="KBS")

# Lấy tất cả mã chứng khoán
all_symbols = listing.all_symbols(to_df=True)
print(f"Tổng số mã: {len(all_symbols)}")
print(all_symbols.head())

# Lấy theo sàn
hose_symbols = listing.symbols_by_exchange(exchange="HOSE")
print(f"\nTổng mã HOSE: {len(hose_symbols)}")
print(hose_symbols[:10])

# Lấy theo chỉ số
vn30_symbols = listing.symbols_by_group(group="VN30")
print(f"\nTổng mã VN30: {len(vn30_symbols)}")
print(vn30_symbols)
```

Chạy:

```bash
python example1_list_symbols.py
```

### Ví dụ 2: Lấy Giá Lịch Sử

```python
# example2_price_history.py
from vnstock import Quote
from vnstock.core.types import TimeFrame

# Khởi tạo với KBS (khuyến nghị)
quote = Quote(source="KBS", symbol="VCI")

# Lấy giá lịch sử
df = quote.history(
    start_date="2024-01-01",
    end_date="2024-12-31",
    resolution=TimeFrame.DAILY
)

print("Giá lịch sử:")
print(df.head())
print(f"\nTổng cộng: {len(df)} ngày")
print(f"Giá cao nhất: {df['high'].max()}")
print(f"Giá thấp nhất: {df['low'].min()}")
print(f"Khối lượng trung bình: {df['volume'].mean():,.0f}")
```

### Ví dụ 3: Lấy Thông Tin Công Ty

```python
# example3_company_info.py
from vnstock import Company

# Khởi tạo với KBS (khuyến nghị)
company = Company(source="KBS", symbol="VCI")

# Lấy thông tin công ty
overview = company.overview()
print("Thông tin công ty:")
print(overview)

# Lấy cổ đông chính
shareholders = company.shareholders()
print("\nCổ đông chính:")
print(shareholders)

# Lấy nhân viên quản lý
officers = company.officers()
print("\nNhân viên quản lý:")
print(officers)
```

## 📚 Các Bước Tiếp Theo

1. ✅ **Installation** - Bạn đã ở đây
2. [01-Overview](01-overview.md) - Tổng quan thư viện
3. [03-Listing API](03-listing-api.md) - Tìm kiếm chứng khoán
4. [04-Quote & Price](04-quote-price-api.md) - Giá lịch sử & realtime
5. [05-Financial API](05-financial-api.md) - Dữ liệu tài chính
6. [06-Connector Guide](06-connector-guide.md) - API bên ngoài
7. [07-Best Practices](07-best-practices.md) - Mẹo & kinh nghiệm

---

**Last Updated**: 2024-12-17  
**Version**: 3.4.0  
**Status**: Actively Maintained  
**Important**: TCBS deprecated, use VCI or KBS instead
