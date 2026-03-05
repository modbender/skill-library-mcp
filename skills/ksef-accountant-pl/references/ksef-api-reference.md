# KSeF API 2.0 - Reference

**UWAGA:** Rzeczywiste punkty końcowe i formaty mogą ulec zmianie. Należy zawsze odwoływać się do oficjalnej dokumentacji API KSeF.

---

## Autentykacja

### 1. Inicjalizacja Sesji (Token)

**Endpoint:**
```http
POST /api/online/Session/InitToken
Content-Type: application/json
```

**Request:**
```json
{
  "context": {
    "token": "YOUR_KSEF_TOKEN_HERE"
  }
}
```

**Response (200 OK):**
```json
{
  "referenceNumber": "20260208-SE-1234567890AB-CD",
  "timestamp": "2026-02-08T23:40:00.000Z",
  "sessionToken": {
    "token": "SESSION_TOKEN_VALUE",
    "validity": "2026-02-09T00:10:00.000Z"
  }
}
```

**Ważność tokena:** Typowo 30 minut

---

### 2. Inicjalizacja Sesji (Certyfikat)

**Endpoint:**
```http
POST /api/online/Session/InitSigned
Content-Type: application/octet-stream
```

**Request:** Signed XML Session Request (CAdES)

---

### 3. Status Sesji

**Endpoint:**
```http
GET /api/online/Session/Status/{ReferenceNumber}
Authorization: SessionToken {token}
```

**Response (200 OK):**
```json
{
  "referenceNumber": "20260208-SE-1234567890AB-CD",
  "timestamp": "2026-02-08T23:45:00.000Z",
  "processingCode": 200,
  "processingDescription": "Sesja aktywna"
}
```

---

### 4. Zamknięcie Sesji

**Endpoint:**
```http
DELETE /api/online/Session/Terminate
Authorization: SessionToken {token}
```

**Response (200 OK):**
```json
{
  "referenceNumber": "20260208-ST-1234567890AB-CD",
  "timestamp": "2026-02-08T23:50:00.000Z",
  "processingCode": 200,
  "processingDescription": "Sesja zakończona"
}
```

---

## Wysyłanie Faktur

### 5. Wysłanie Faktury

**Endpoint:**
```http
POST /api/online/Invoice/Send
Authorization: SessionToken {token}
Content-Type: application/octet-stream
```

**Request Body:** FA(3) XML Content (raw bytes)

**Response (200 OK - Przyjęto do przetworzenia):**
```json
{
  "referenceNumber": "20260208-IV-1234567890AB-CD",
  "timestamp": "2026-02-08T23:41:00.000Z",
  "processingCode": 200,
  "processingDescription": "Faktura została przyjęta do przetworzenia"
}
```

---

### 6. Status Faktury

**Endpoint:**
```http
GET /api/online/Invoice/Status/{InvoiceElementReferenceNumber}
Authorization: SessionToken {token}
```

**Możliwe statusy:**
- `200` - Przetwarzanie w toku
- `202` - Faktura zaakceptowana
- `400` - Faktura odrzucona (błędy walidacji)

**Response (202 - Zaakceptowana):**
```json
{
  "referenceNumber": "20260208-IV-1234567890AB-CD",
  "timestamp": "2026-02-08T23:41:30.000Z",
  "processingCode": 202,
  "ksefReferenceNumber": "1234567890-20260208-ABCDEF1234567890-12",
  "invoiceNumber": "FV/2026/02/0008",
  "acquisitionTimestamp": "2026-02-08T23:41:25.000Z"
}
```

**Response (400 - Odrzucona):**
```json
{
  "referenceNumber": "20260208-IV-1234567890AB-CD",
  "timestamp": "2026-02-08T23:41:15.000Z",
  "processingCode": 400,
  "exception": {
    "exceptionDetailList": [
      {
        "exceptionCode": "101",
        "exceptionDescription": "Błąd walidacji schematu XSD"
      }
    ]
  }
}
```

---

### 7. Pobieranie UPO

**Endpoint:**
```http
GET /api/online/Invoice/Upo/{KsefReferenceNumber}
Authorization: SessionToken {token}
Accept: application/xml
```

**Response (200 OK):** XML z urzędowym poświadczeniem odbioru

---

## Pobieranie Faktur

### 8. Wyszukiwanie Faktur (Synchroniczne)

**Endpoint:**
```http
POST /api/online/Query/Invoice/Sync
Authorization: SessionToken {token}
Content-Type: application/json
```

**Request (faktury zakupowe, zakres dat):**
```json
{
  "queryCriteria": {
    "type": "range",
    "invoicingDateFrom": "2026-02-01",
    "invoicingDateTo": "2026-02-08",
    "subjectType": "subject2"
  },
  "pageSize": 100,
  "pageOffset": 0
}
```

**QueryCriteria - typy:**
- `subjectType: "subject1"` - faktury sprzedażowe (jako sprzedawca)
- `subjectType: "subject2"` - faktury zakupowe (jako nabywca)

**Response (200 OK):**
```json
{
  "referenceNumber": "20260208-QS-1234567890AB-CD",
  "timestamp": "2026-02-08T23:42:00.000Z",
  "invoiceHeaderList": [
    {
      "ksefReferenceNumber": "9876543210-20260205-ZYXWVU9876543210-01",
      "invoiceNumber": "ZAKUP/123/2026",
      "acquisitionTimestamp": "2026-02-05T10:30:00.000Z",
      "netAmount": "5000.00",
      "vatAmount": "1150.00",
      "grossAmount": "6150.00",
      "currencyCode": "PLN"
    }
  ],
  "numberOfElements": 1,
  "pageSize": 100,
  "pageOffset": 0,
  "totalPages": 1,
  "totalElements": 1
}
```

---

### 9. Wyszukiwanie Faktur (Asynchroniczne)

**Endpoint:**
```http
POST /api/online/Query/Invoice/Async/Init
Authorization: SessionToken {token}
Content-Type: application/json
```

**Użycie:** Dla dużych zbiorów danych (>100 faktur)

**Workflow:**
1. `POST /api/online/Query/Invoice/Async/Init` - inicjalizacja
2. `GET /api/online/Query/Invoice/Async/Status/{QueryElementReferenceNumber}` - sprawdzenie statusu
3. `GET /api/online/Query/Invoice/Async/Fetch/{QueryElementReferenceNumber}` - pobranie wyników

---

### 10. Pobieranie Pełnej Faktury

**Endpoint:**
```http
GET /api/online/Invoice/Get/{KsefReferenceNumber}
Authorization: SessionToken {token}
Accept: application/xml
```

**Response (200 OK):** Pełny XML FA(3)

---

## Tryb Offline

### 11. Wysłanie Faktury Offline

**Endpoint:**
```http
POST /api/online/Invoice/Send
Authorization: SessionToken {token}
Content-Type: application/octet-stream
```

**FA(3) XML z oznaczeniem Offline24:**
```xml
<Faktura>
  <Naglowek>
    <SystemInfo>Offline24</SystemInfo>
  </Naglowek>
  <!-- ... -->
</Faktura>
```

**Termin wysyłki:** 24h od odzyskania łączności

---

## Kody Błędów

### Najczęstsze

| Kod | Opis | Rozwiązanie |
|-----|------|-------------|
| 100 | Nieprawidłowy format XML | Sprawdź encoding UTF-8 |
| 101 | Błąd walidacji schematu | Upewnij się że używasz FA(3) |
| 102 | Nieprawidłowy NIP | Sprawdź w białej liście VAT |
| 103 | Data w przyszłości | Skoryguj DataWytworzeniaFa |
| 104 | Duplikat numeru faktury | Sprawdź unikalność |
| 401 | Brak autoryzacji | Sesja wygasła, odśwież token |
| 403 | Brak uprawnień | Sprawdź uprawnienia tokena |
| 500 | Błąd serwera | Retry z exponential backoff |
| 503 | Serwis niedostępny | Sprawdź status KSeF (Latarnia) |

---

## Rate Limiting

**UWAGA:** Szczegóły mogą się różnić. Sprawdź aktualną dokumentację.

**Typowe limity (szacunkowe):**
- Sesje: ~100 sesji/godzinę na token
- Faktury: ~1000 faktur/godzinę na sesję
- Queries: ~100 zapytań/godzinę na sesję

**Best practices:**
- Używaj pojedynczej sesji dla wielu faktur
- Implementuj exponential backoff przy 429/503
- Cachuj wyniki queries (nie odpytuj co sekundę)

---

## Środowiska

### DEMO (testowe)
```
Base URL: https://ksef-demo.mf.gov.pl
Przeznaczenie: Testy integracji, development
Dane: Testowe (nie produkcyjne)
```

### PRODUKCJA
```
Base URL: https://ksef.mf.gov.pl
Przeznaczenie: Faktury produkcyjne
Dane: Prawne wiążące
```

**UWAGA:** NIE testuj na produkcji! Zawsze używaj DEMO do developmentu.

---

## Przykładowy Workflow

```python
# 1. Inicjalizacja sesji
session = ksef_client.init_session(token="YOUR_TOKEN")

# 2. Wysłanie faktury
invoice_xml = generate_fa3_xml(invoice_data)
ref = ksef_client.send_invoice(session, invoice_xml)

# 3. Sprawdzenie statusu (z retry)
for i in range(10):
    status = ksef_client.get_invoice_status(session, ref)
    if status.code == 202:
        ksef_number = status.ksefReferenceNumber
        break
    elif status.code == 400:
        handle_rejection(status.exception)
        break
    time.sleep(2)  # Czekaj 2s przed następnym sprawdzeniem

# 4. Pobranie UPO
upo_xml = ksef_client.get_upo(session, ksef_number)

# 5. Zamknięcie sesji
ksef_client.terminate_session(session)
```

---

**Oficjalna dokumentacja:** https://ksef.mf.gov.pl/api/docs
