# Endpoints

- Optional: email APIs or IMAP for read-only retrieval.
- Optional: OCR for scanned receipts.
- Do not use endpoints that initiate cancellation or payments.

## Generic parse template

```
{
  "vendor": "...",
  "amount": 0.0,
  "currency": "USD",
  "invoice_date": "YYYY-MM-DD",
  "descriptor": "..."
}
```
