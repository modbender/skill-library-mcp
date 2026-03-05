# Troubleshooting KSeF

Przewodnik rozwiązywania najczęstszych problemów z systemem KSeF.

---

## Problemy z Autentykacją

### Błąd 401: Unauthorized

**Objawy:**
```json
{
  "processingCode": 401,
  "processingDescription": "Brak autoryzacji"
}
```

**Przyczyny:**
- Sesja wygasła (token ważny tylko ~30 min)
- Nieprawidłowy token
- Token nie ma wymaganych uprawnień

**Rozwiązanie:**
```python
def handle_401_error():
    # 1. Sprawdź ważność tokena
    if session.is_expired():
        # Odśwież sesję
        session = ksef_client.init_session(token)
        retry_operation()

    # 2. Sprawdź uprawnienia tokena
    # Token musi mieć scope: invoice.read, invoice.write

    # 3. Wygeneruj nowy token w portalu KSeF
```

---

### Błąd 403: Forbidden

**Objawy:**
```json
{
  "processingCode": 403,
  "processingDescription": "Brak uprawnień"
}
```

**Przyczyny:**
- Token nie ma uprawnień do tej operacji
- NIP w tokenie nie zgadza się z NIP w fakturze

**Rozwiązanie:**
1. Sprawdź uprawnienia tokena w portalu KSeF
2. Upewnij się że token jest dla właściwego NIP
3. Sprawdź czy token ma scope dla danej operacji (read/write)

---

## Problemy z Walidacją Faktur

### Błąd 100: Nieprawidłowy format XML

**Objawy:**
```json
{
  "exceptionCode": "100",
  "exceptionDescription": "Nieprawidłowy format XML"
}
```

**Rozwiązanie:**
```python
# 1. Sprawdź encoding
assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')

# 2. Waliduj XML parser
try:
    ET.fromstring(xml_content)
except ET.ParseError as e:
    print(f"Błąd parsowania: {e}")
    # Sprawdź: unclosed tags, nieprawidłowe znaki

# 3. Usuń BOM (Byte Order Mark)
xml_content = xml_content.lstrip('\ufeff')
```

---

### Błąd 101: Błąd walidacji schematu

**Objawy:**
```json
{
  "exceptionCode": "101",
  "exceptionDescription": "Błąd walidacji schematu XSD"
}
```

**Przyczyny:**
- Używasz FA(2) zamiast FA(3)
- Nieprawidłowa struktura XML
- Brakujące wymagane pola
- Nieprawidłowy namespace

**Rozwiązanie:**
```python
# Checklist FA(3):
checks = {
    'Namespace': 'http://crd.gov.pl/wzor/2023/06/29/12648/',
    'KodFormularza kodSystemowy': 'FA(3)',
    'wersjaSchemy': '1-0E',
    'WariantFormularza': '3'
}

for field, expected in checks.items():
    if expected not in xml_content:
        print(f"BŁĄD: Brak {field} = {expected}")
```

**Częste błędy:**
- `kodSystemowy="FA(2)"` → Zmień na `FA(3)`
- `wersjaSchemy="1-0"` → Zmień na `1-0E`
- Stary namespace z 2021 → Użyj namespace z 2023

---

### Błąd 102: Nieprawidłowy NIP

**Objawy:**
```json
{
  "exceptionCode": "102",
  "exceptionDescription": "Nieprawidłowy NIP"
}
```

**Rozwiązanie:**
```python
def validate_nip(nip):
    # 1. Długość
    if len(nip) != 10:
        return False

    # 2. Cyfry
    if not nip.isdigit():
        return False

    # 3. Suma kontrolna
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    check_sum = sum(int(nip[i]) * weights[i] for i in range(9))
    check_digit = check_sum % 11

    if check_digit == 10:
        return False

    return check_digit == int(nip[9])

# 4. Sprawdź w białej liście VAT
response = requests.get(f"https://wl-api.mf.gov.pl/api/search/nip/{nip}")
if response.status_code != 200:
    print("NIP nie istnieje w bazie MF")
```

---

### Błąd 103: Data w przyszłości

**Objawy:**
```json
{
  "exceptionCode": "103",
  "exceptionDescription": "Data w przyszłości"
}
```

**Rozwiązanie:**
```python
from datetime import datetime, timedelta

# DataWytworzeniaFa nie może być w przyszłości
now = datetime.now()
data_wytworzenia = now.strftime('%Y-%m-%dT%H:%M:%S')

# BŁĄD: Data jutro
tomorrow = now + timedelta(days=1)
data_wytworzenia = tomorrow.strftime(...)  # ❌

# Uwaga na strefy czasowe
# KSeF używa czasu polskiego (UTC+1/UTC+2)
```

---

### Błąd 104: Duplikat numeru faktury

**Objawy:**
```json
{
  "exceptionCode": "104",
  "exceptionDescription": "Faktura o takim numerze już istnieje"
}
```

**Rozwiązanie:**
```python
def generate_unique_invoice_number():
    # Format: FV/ROK/MIESIĄC/NUMER
    year = datetime.now().year
    month = datetime.now().month

    # Pobierz ostatni numer z bazy
    last_number = db.get_last_invoice_number(year, month)

    next_number = (last_number or 0) + 1

    return f"FV/{year}/{month:02d}/{next_number:04d}"

# Sprawdź czy numer już istnieje w KSeF
existing = ksef_client.check_invoice_number(invoice_number)
if existing:
    print("Numer już użyty - wygeneruj nowy")
```

---

## Problemy z Wydajnością

### Timeout API / Brak Odpowiedzi

**Objawy:**
- Request timeout (>30s)
- 503 Service Unavailable
- Brak odpowiedzi

**Diagnoza:**
```python
def diagnose_timeout():
    # 1. Sprawdź status KSeF
    try:
        response = requests.get('https://ksef.mf.gov.pl/api/health')
        print(f"Status KSeF: {response.status_code}")
    except:
        print("KSeF niedostępny")
        return "KSEF_DOWN"

    # 2. Sprawdź własną sieć
    try:
        requests.get('https://google.com', timeout=5)
    except:
        print("Problem z internetem")
        return "NETWORK_ISSUE"

    # 3. Sprawdź obciążenie (godziny szczytu)
    hour = datetime.now().hour
    if hour in [15, 16, 17]:  # 15:00-18:00
        print("Godziny szczytu - duże obciążenie KSeF")
        return "HIGH_LOAD"

    return "UNKNOWN"
```

**Rozwiązanie:**
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
                print(f"Timeout - retry {attempt+1}/{max_retries} za {wait_time}s")
                time.sleep(wait_time)
            else:
                raise

# Best practices:
# - Wysyłaj poza godzinami szczytu (21:00-6:00)
# - Użyj queue + background worker
# - Implementuj circuit breaker
```

---

### Rate Limiting (429)

**Objawy:**
```json
{
  "processingCode": 429,
  "processingDescription": "Zbyt wiele żądań"
}
```

**Rozwiązanie:**
```python
import time
from functools import wraps

def rate_limit(max_per_hour=100):
    """Decorator ograniczający liczbę requestów"""
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Usuń stare calle (sprzed godziny)
            calls[:] = [c for c in calls if c > now - 3600]

            if len(calls) >= max_per_hour:
                wait_time = 3600 - (now - calls[0])
                print(f"Rate limit - czekaj {wait_time:.0f}s")
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

## Problemy z Płatnościami

### Nie Można Dopasować Płatności

**Przyczyny:**
- Niezgodna kwota (błąd w kwocie przelewu)
- Brak numeru faktury w tytule
- Split payment (MPP) - częściowa płatność
- Płatność zbiorcza (kilka faktur naraz)

**Rozwiązanie:**
```python
def handle_unmatched_payment(payment):
    # 1. Rozszerzone wyszukiwanie (tolerancja ±2%)
    matches = search_invoices_extended(
        amount_min=payment.amount * 0.98,
        amount_max=payment.amount * 1.02,
        date_range_days=14  # ±14 dni zamiast ±7
    )

    if matches:
        return present_to_user_for_confirmation(matches)

    # 2. Sprawdź czy to split payment (część VAT)
    if is_likely_vat_payment(payment):
        net_payment = find_net_payment(payment)
        if net_payment:
            return match_mpp(net_payment, payment)

    # 3. Sprawdź płatność zbiorczą
    invoice_numbers = extract_invoice_numbers_from_title(payment.title)
    if len(invoice_numbers) > 1:
        return split_payment_to_invoices(payment, invoice_numbers)

    # 4. Flaguj do manual review
    flag_for_review(payment)
```

---

## Problemy ze Środowiskiem

### Faktury Testowe na Produkcji

**Problem:** Wysłano faktury testowe na środowisko produkcyjne

**⚠️ UWAGA:** Faktury na produkcji są prawnie wiążące!

**Co zrobić:**
1. NIE usuwaj faktur (niemożliwe w KSeF)
2. Wystaw faktury korygujące do zera
3. Skontaktuj się z kontrahentem
4. Zgłoś do księgowości

**Zapobieganie:**
```python
# Zawsze sprawdzaj środowisko
class KSefClient:
    def __init__(self, environment='demo'):
        if environment == 'production':
            # Wymuś potwierdzenie
            confirm = input("⚠️  PRODUKCJA! Kontynuować? (yes/no): ")
            if confirm != 'yes':
                raise Exception("Anulowano - używaj DEMO do testów")

        self.base_url = {
            'demo': 'https://ksef-demo.mf.gov.pl',
            'production': 'https://ksef.mf.gov.pl'
        }[environment]
```

---

## Monitoring i Alerty

### Konfiguracja Alertów

```python
def setup_monitoring():
    monitors = [
        # 1. Alert przy wysokiej liczbie błędów
        {
            'name': 'High rejection rate',
            'condition': lambda: get_rejection_rate_last_hour() > 0.2,
            'action': send_alert_email
        },

        # 2. Alert przy niedostępności KSeF
        {
            'name': 'KSeF down',
            'condition': lambda: not check_ksef_health(),
            'action': send_sms_alert
        },

        # 3. Alert przy problemach z płatnościami
        {
            'name': 'Too many unmatched payments',
            'condition': lambda: count_unmatched_payments() > 10,
            'action': notify_accountant
        }
    ]

    # Uruchom monitoring co 5 minut
    schedule.every(5).minutes.do(run_monitors, monitors)
```

---

## Pomocne Narzędzia

### KSeF Latarnia (Status Systemu)

```bash
# Sprawdź status KSeF w czasie rzeczywistym
git clone https://github.com/CIRFMF/ksef-latarnia
cd ksef-latarnia
python check_status.py
```

### Walidator XML

```python
from lxml import etree

def validate_fa3_xsd(xml_content):
    """Walidacja względem schematu XSD"""
    xsd_url = "https://ksef.podatki.gov.pl/xsd/FA3_1-0E.xsd"

    # Pobierz schemat
    xsd_doc = etree.parse(xsd_url)
    schema = etree.XMLSchema(xsd_doc)

    # Waliduj XML
    xml_doc = etree.fromstring(xml_content.encode('utf-8'))

    try:
        schema.assertValid(xml_doc)
        return True, "OK"
    except etree.DocumentInvalid as e:
        return False, str(e)
```

---

**Potrzebujesz pomocy?**
- Dokumentacja KSeF: https://ksef.podatki.gov.pl
- Forum: https://github.com/CIRFMF/ksef-discussions
- Helpdesk MF: (sprawdź portal KSeF)
