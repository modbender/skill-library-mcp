# KSeF Troubleshooting

Guide for resolving the most common problems with the KSeF system.

---

## Authentication Problems

### Error 401: Unauthorized

**Symptoms:**
```json
{
  "processingCode": 401,
  "processingDescription": "Unauthorized"
}
```

**Causes:**
- Session expired (token valid only ~30 min)
- Invalid token
- Token does not have required permissions

**Solution:**
```python
def handle_401_error():
    # 1. Check token validity
    if session.is_expired():
        # Refresh session
        session = ksef_client.init_session(token)
        retry_operation()

    # 2. Check token permissions
    # Token must have scope: invoice.read, invoice.write

    # 3. Generate new token in KSeF portal
```

---

### Error 403: Forbidden

**Symptoms:**
```json
{
  "processingCode": 403,
  "processingDescription": "Forbidden"
}
```

**Causes:**
- Token does not have permissions for this operation
- NIP in token does not match NIP in invoice

**Solution:**
1. Check token permissions in KSeF portal
2. Make sure the token is for the correct NIP
3. Check if the token has scope for the given operation (read/write)

---

## Invoice Validation Problems

### Error 100: Invalid XML Format

**Symptoms:**
```json
{
  "exceptionCode": "100",
  "exceptionDescription": "Invalid XML format"
}
```

**Solution:**
```python
# 1. Check encoding
assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')

# 2. Validate XML parser
try:
    ET.fromstring(xml_content)
except ET.ParseError as e:
    print(f"Parse error: {e}")
    # Check: unclosed tags, invalid characters

# 3. Remove BOM (Byte Order Mark)
xml_content = xml_content.lstrip('\ufeff')
```

---

### Error 101: Schema Validation Error

**Symptoms:**
```json
{
  "exceptionCode": "101",
  "exceptionDescription": "XSD schema validation error"
}
```

**Causes:**
- Using FA(2) instead of FA(3)
- Invalid XML structure
- Missing required fields
- Invalid namespace

**Solution:**
```python
# FA(3) checklist:
checks = {
    'Namespace': 'http://crd.gov.pl/wzor/2023/06/29/12648/',
    'KodFormularza kodSystemowy': 'FA(3)',
    'wersjaSchemy': '1-0E',
    'WariantFormularza': '3'
}

for field, expected in checks.items():
    if expected not in xml_content:
        print(f"ERROR: Missing {field} = {expected}")
```

**Common errors:**
- `kodSystemowy="FA(2)"` -> Change to `FA(3)`
- `wersjaSchemy="1-0"` -> Change to `1-0E`
- Old namespace from 2021 -> Use 2023 namespace

---

### Error 102: Invalid NIP

**Symptoms:**
```json
{
  "exceptionCode": "102",
  "exceptionDescription": "Invalid NIP"
}
```

**Solution:**
```python
def validate_nip(nip):
    # 1. Length
    if len(nip) != 10:
        return False

    # 2. Digits
    if not nip.isdigit():
        return False

    # 3. Checksum
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    check_sum = sum(int(nip[i]) * weights[i] for i in range(9))
    check_digit = check_sum % 11

    if check_digit == 10:
        return False

    return check_digit == int(nip[9])

# 4. Check in VAT White List
response = requests.get(f"https://wl-api.mf.gov.pl/api/search/nip/{nip}")
if response.status_code != 200:
    print("NIP does not exist in MF database")
```

---

### Error 103: Future Date

**Symptoms:**
```json
{
  "exceptionCode": "103",
  "exceptionDescription": "Future date"
}
```

**Solution:**
```python
from datetime import datetime, timedelta

# DataWytworzeniaFa cannot be in the future
now = datetime.now()
data_wytworzenia = now.strftime('%Y-%m-%dT%H:%M:%S')

# ERROR: Tomorrow's date
tomorrow = now + timedelta(days=1)
data_wytworzenia = tomorrow.strftime(...)  # wrong

# Note on time zones
# KSeF uses Polish time (UTC+1/UTC+2)
```

---

### Error 104: Duplicate Invoice Number

**Symptoms:**
```json
{
  "exceptionCode": "104",
  "exceptionDescription": "Invoice with this number already exists"
}
```

**Solution:**
```python
def generate_unique_invoice_number():
    # Format: FV/YEAR/MONTH/NUMBER
    year = datetime.now().year
    month = datetime.now().month

    # Get last number from database
    last_number = db.get_last_invoice_number(year, month)

    next_number = (last_number or 0) + 1

    return f"FV/{year}/{month:02d}/{next_number:04d}"

# Check if number already exists in KSeF
existing = ksef_client.check_invoice_number(invoice_number)
if existing:
    print("Number already used - generate a new one")
```

---

## Performance Problems

### API Timeout / No Response

**Symptoms:**
- Request timeout (>30s)
- 503 Service Unavailable
- No response

**Diagnosis:**
```python
def diagnose_timeout():
    # 1. Check KSeF status
    try:
        response = requests.get('https://ksef.mf.gov.pl/api/health')
        print(f"KSeF status: {response.status_code}")
    except:
        print("KSeF unavailable")
        return "KSEF_DOWN"

    # 2. Check own network
    try:
        requests.get('https://google.com', timeout=5)
    except:
        print("Internet problem")
        return "NETWORK_ISSUE"

    # 3. Check load (peak hours)
    hour = datetime.now().hour
    if hour in [15, 16, 17]:  # 15:00-18:00
        print("Peak hours - heavy KSeF load")
        return "HIGH_LOAD"

    return "UNKNOWN"
```

**Solution:**
```python
import time

def send_with_retry(invoice_xml, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = ksef_client.send_invoice(invoice_xml, timeout=60)
            return response
        except Timeout:
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Timeout - retry {attempt+1}/{max_retries} in {wait_time}s")
                time.sleep(wait_time)
            else:
                raise

# Best practices:
# - Send outside peak hours (21:00-6:00)
# - Use queue + background worker
# - Implement circuit breaker
```

---

### Rate Limiting (429)

**Symptoms:**
```json
{
  "processingCode": 429,
  "processingDescription": "Too many requests"
}
```

**Solution:**
```python
import time
from functools import wraps

def rate_limit(max_per_hour=100):
    """Decorator limiting the number of requests"""
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls (from over an hour ago)
            calls[:] = [c for c in calls if c > now - 3600]

            if len(calls) >= max_per_hour:
                wait_time = 3600 - (now - calls[0])
                print(f"Rate limit - wait {wait_time:.0f}s")
                time.sleep(wait_time)

            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_per_hour=100)
def send_invoice(invoice):
    return ksef_client.send_invoice(invoice)
```

---

## Payment Problems

### Cannot Match Payment

**Causes:**
- Amount mismatch (error in transfer amount)
- Missing invoice number in title
- Split payment (MPP) - partial payment
- Batch payment (multiple invoices at once)

**Solution:**
```python
def handle_unmatched_payment(payment):
    # 1. Extended search (tolerance +/-2%)
    matches = search_invoices_extended(
        amount_min=payment.amount * 0.98,
        amount_max=payment.amount * 1.02,
        date_range_days=14  # +/-14 days instead of +/-7
    )

    if matches:
        return present_to_user_for_confirmation(matches)

    # 2. Check if it's a split payment (VAT portion)
    if is_likely_vat_payment(payment):
        net_payment = find_net_payment(payment)
        if net_payment:
            return match_mpp(net_payment, payment)

    # 3. Check batch payment
    invoice_numbers = extract_invoice_numbers_from_title(payment.title)
    if len(invoice_numbers) > 1:
        return split_payment_to_invoices(payment, invoice_numbers)

    # 4. Flag for manual review
    flag_for_review(payment)
```

---

## Environment Problems

### Test Invoices on Production

**Problem:** Test invoices were sent to the production environment

**WARNING:** Invoices on production are legally binding!

**What to do:**
1. DO NOT delete invoices (impossible in KSeF)
2. Issue corrective invoices to zero
3. Contact the counterparty
4. Report to the accounting department

**Prevention:**
```python
# Always check the environment
class KSefClient:
    def __init__(self, environment='demo'):
        if environment == 'production':
            # Force confirmation
            confirm = input("WARNING: PRODUCTION! Continue? (yes/no): ")
            if confirm != 'yes':
                raise Exception("Cancelled - use DEMO for testing")

        self.base_url = {
            'demo': 'https://ksef-demo.mf.gov.pl',
            'production': 'https://ksef.mf.gov.pl'
        }[environment]
```

---

## Monitoring and Alerts

### Alert Configuration

```python
def setup_monitoring():
    monitors = [
        # 1. Alert on high rejection rate
        {
            'name': 'High rejection rate',
            'condition': lambda: get_rejection_rate_last_hour() > 0.2,
            'action': send_alert_email
        },

        # 2. Alert on KSeF unavailability
        {
            'name': 'KSeF down',
            'condition': lambda: not check_ksef_health(),
            'action': send_sms_alert
        },

        # 3. Alert on payment matching problems
        {
            'name': 'Too many unmatched payments',
            'condition': lambda: count_unmatched_payments() > 10,
            'action': notify_accountant
        }
    ]

    # Run monitoring every 5 minutes
    schedule.every(5).minutes.do(run_monitors, monitors)
```

---

## Helpful Tools

### KSeF Latarnia (System Status)

```bash
# Check KSeF status in real time
git clone https://github.com/CIRFMF/ksef-latarnia
cd ksef-latarnia
python check_status.py
```

### XML Validator

```python
from lxml import etree

def validate_fa3_xsd(xml_content):
    """Validation against XSD schema"""
    xsd_url = "https://ksef.podatki.gov.pl/xsd/FA3_1-0E.xsd"

    # Download schema
    xsd_doc = etree.parse(xsd_url)
    schema = etree.XMLSchema(xsd_doc)

    # Validate XML
    xml_doc = etree.fromstring(xml_content.encode('utf-8'))

    try:
        schema.assertValid(xml_doc)
        return True, "OK"
    except etree.DocumentInvalid as e:
        return False, str(e)
```

---

**Need help?**
- KSeF Documentation: https://ksef.podatki.gov.pl
- Forum: https://github.com/CIRFMF/ksef-discussions
- MF Helpdesk: (check KSeF portal)
