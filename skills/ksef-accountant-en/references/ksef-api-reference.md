# KSeF API 2.0 - Reference

**NOTE:** Actual endpoints and formats may change. Always refer to the official KSeF API documentation.

---

## Authentication

### 1. Session Initialization (Token)

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

**Token validity:** Typically 30 minutes

---

### 2. Session Initialization (Certificate)

**Endpoint:**
```http
POST /api/online/Session/InitSigned
Content-Type: application/octet-stream
```

**Request:** Signed XML Session Request (CAdES)

---

### 3. Session Status

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
  "processingDescription": "Session active"
}
```

---

### 4. Session Termination

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
  "processingDescription": "Session terminated"
}
```

---

## Sending Invoices

### 5. Send Invoice

**Endpoint:**
```http
POST /api/online/Invoice/Send
Authorization: SessionToken {token}
Content-Type: application/octet-stream
```

**Request Body:** FA(3) XML Content (raw bytes)

**Response (200 OK - Accepted for processing):**
```json
{
  "referenceNumber": "20260208-IV-1234567890AB-CD",
  "timestamp": "2026-02-08T23:41:00.000Z",
  "processingCode": 200,
  "processingDescription": "Invoice has been accepted for processing"
}
```

---

### 6. Invoice Status

**Endpoint:**
```http
GET /api/online/Invoice/Status/{InvoiceElementReferenceNumber}
Authorization: SessionToken {token}
```

**Possible statuses:**
- `200` - Processing in progress
- `202` - Invoice accepted
- `400` - Invoice rejected (validation errors)

**Response (202 - Accepted):**
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

**Response (400 - Rejected):**
```json
{
  "referenceNumber": "20260208-IV-1234567890AB-CD",
  "timestamp": "2026-02-08T23:41:15.000Z",
  "processingCode": 400,
  "exception": {
    "exceptionDetailList": [
      {
        "exceptionCode": "101",
        "exceptionDescription": "XSD schema validation error"
      }
    ]
  }
}
```

---

### 7. Downloading UPO

**Endpoint:**
```http
GET /api/online/Invoice/Upo/{KsefReferenceNumber}
Authorization: SessionToken {token}
Accept: application/xml
```

**Response (200 OK):** XML with Official Acknowledgement of Receipt

---

## Downloading Invoices

### 8. Invoice Search (Synchronous)

**Endpoint:**
```http
POST /api/online/Query/Invoice/Sync
Authorization: SessionToken {token}
Content-Type: application/json
```

**Request (purchase invoices, date range):**
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

**QueryCriteria - types:**
- `subjectType: "subject1"` - sales invoices (as seller)
- `subjectType: "subject2"` - purchase invoices (as buyer)

**Response (200 OK):**
```json
{
  "referenceNumber": "20260208-QS-1234567890AB-CD",
  "timestamp": "2026-02-08T23:42:00.000Z",
  "invoiceHeaderList": [
    {
      "ksefReferenceNumber": "9876543210-20260205-ZYXWVU9876543210-01",
      "invoiceNumber": "PURCHASE/123/2026",
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

### 9. Invoice Search (Asynchronous)

**Endpoint:**
```http
POST /api/online/Query/Invoice/Async/Init
Authorization: SessionToken {token}
Content-Type: application/json
```

**Usage:** For large datasets (>100 invoices)

**Workflow:**
1. `POST /api/online/Query/Invoice/Async/Init` - initialization
2. `GET /api/online/Query/Invoice/Async/Status/{QueryElementReferenceNumber}` - check status
3. `GET /api/online/Query/Invoice/Async/Fetch/{QueryElementReferenceNumber}` - fetch results

---

### 10. Downloading Full Invoice

**Endpoint:**
```http
GET /api/online/Invoice/Get/{KsefReferenceNumber}
Authorization: SessionToken {token}
Accept: application/xml
```

**Response (200 OK):** Full FA(3) XML

---

## Offline Mode

### 11. Sending Offline Invoice

**Endpoint:**
```http
POST /api/online/Invoice/Send
Authorization: SessionToken {token}
Content-Type: application/octet-stream
```

**FA(3) XML with Offline24 designation:**
```xml
<Faktura>
  <Naglowek>
    <SystemInfo>Offline24</SystemInfo>
  </Naglowek>
  <!-- ... -->
</Faktura>
```

**Submission deadline:** 24h after connectivity is restored

---

## Error Codes

### Most Common

| Code | Description | Solution |
|------|-------------|----------|
| 100 | Invalid XML format | Check UTF-8 encoding |
| 101 | Schema validation error | Make sure you are using FA(3) |
| 102 | Invalid NIP | Check in VAT White List |
| 103 | Future date | Correct DataWytworzeniaFa |
| 104 | Duplicate invoice number | Check uniqueness |
| 401 | Unauthorized | Session expired, refresh token |
| 403 | Forbidden | Check token permissions |
| 500 | Server error | Retry with exponential backoff |
| 503 | Service unavailable | Check KSeF status (Latarnia) |

---

## Rate Limiting

**NOTE:** Details may vary. Check the current documentation.

**Typical limits (estimated):**
- Sessions: ~100 sessions/hour per token
- Invoices: ~1000 invoices/hour per session
- Queries: ~100 queries/hour per session

**Best practices:**
- Use a single session for multiple invoices
- Implement exponential backoff on 429/503
- Cache query results (do not query every second)

---

## Environments

### DEMO (test)
```
Base URL: https://ksef-demo.mf.gov.pl
Purpose: Integration testing, development
Data: Test (non-production)
```

### PRODUCTION
```
Base URL: https://ksef.mf.gov.pl
Purpose: Production invoices
Data: Legally binding
```

**WARNING:** Do NOT test on production! Always use DEMO for development.

---

## Example Workflow

```python
# 1. Initialize session
session = ksef_client.init_session(token="YOUR_TOKEN")

# 2. Send invoice
invoice_xml = generate_fa3_xml(invoice_data)
ref = ksef_client.send_invoice(session, invoice_xml)

# 3. Check status (with retry)
for i in range(10):
    status = ksef_client.get_invoice_status(session, ref)
    if status.code == 202:
        ksef_number = status.ksefReferenceNumber
        break
    elif status.code == 400:
        handle_rejection(status.exception)
        break
    time.sleep(2)  # Wait 2s before next check

# 4. Download UPO
upo_xml = ksef_client.get_upo(session, ksef_number)

# 5. Terminate session
ksef_client.terminate_session(session)
```

---

**Official documentation:** https://ksef.mf.gov.pl/api/docs
