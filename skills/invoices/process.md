# Invoice Processing Workflow

## Phase 1: Capture

**Sources:**
- Email attachment forwarded/sent to agent
- Photo/scan from mobile
- PDF uploaded directly
- URL to invoice portal (agent downloads)

**Actions:**
1. Copy file to `~/invoices/inbox/`
2. Generate temp name: `{timestamp}_{original_filename}`
3. Update `state.json` with new entry

**Agent capabilities:**
- Monitor email for invoices (if configured)
- Accept direct file uploads
- Download from URL if provided

---

## Phase 2: Extract

**OCR Pipeline:**
1. If PDF is text-based → extract text directly
2. If image/scanned PDF → use vision model for OCR
3. Parse structured data (see `extraction.md` for fields)

**Extraction approach:**
```
Send to vision model:
"Extract invoice data: provider name, provider tax ID, invoice number, 
date, due date, line items, subtotal, tax rate, tax amount, total, currency."
```

**Output:** JSON with extracted fields + confidence scores

---

## Phase 3: Validate

**Checks:**
- [ ] Provider tax ID format valid (if available)
- [ ] Date is parseable and reasonable (not future, not >1 year old)
- [ ] Math: sum(line_items) ≈ subtotal, subtotal + tax ≈ total
- [ ] No duplicate: same provider + invoice_number doesn't exist

**On validation failure:**
- Flag for human review
- Store in `inbox/` with `_REVIEW` suffix
- Ask user to confirm/correct

---

## Phase 4: Organize

**File naming:**
```
{date}_{provider}_{invoice_number}_{total}.pdf
Example: 2026-02-13_Hetzner_INV-12345_89.50.pdf
```

**Folder structure:**
```
archive/
└── 2026/
    └── 02/
        └── 2026-02-13_Hetzner_INV-12345_89.50.pdf
```

**Metadata update:**
1. Add entry to `entries.json`:
```json
{
  "id": "uuid",
  "file": "archive/2026/02/2026-02-13_Hetzner_INV-12345_89.50.pdf",
  "provider": "Hetzner",
  "provider_id": "DE812871812",
  "invoice_number": "INV-12345",
  "date": "2026-02-13",
  "due_date": "2026-03-13",
  "subtotal": 75.21,
  "tax_rate": 19,
  "tax_amount": 14.29,
  "total": 89.50,
  "currency": "EUR",
  "category": "hosting",
  "status": "pending",
  "paid_date": null,
  "captured_at": "2026-02-13T14:30:00Z"
}
```
2. Update `providers/index.json` if new provider
3. Remove from `inbox/`

---

## Phase 5: Confirm

**Show user:**
```
📥 Invoice captured:
• Provider: Hetzner
• Invoice #: INV-12345
• Date: 2026-02-13
• Total: €89.50 (€75.21 + 19% VAT)
• Category: hosting (auto-detected)

✓ Saved to: archive/2026/02/
```

**Allow corrections:**
- "Change category to 'infrastructure'"
- "Mark as paid"
- "This is a duplicate, delete it"

---

## State Management

`state.json` tracks:
```json
{
  "last_processed": "2026-02-13T14:30:00Z",
  "inbox_count": 2,
  "total_processed": 147,
  "providers_count": 23,
  "pending_review": ["inbox/1234567890_invoice.pdf"]
}
```

---

## Email Integration (Optional)

If user configures email access:
1. Scan inbox for invoices (common sender patterns, PDF attachments)
2. Auto-forward to processing queue
3. Mark as processed in email

Patterns to detect:
- Subject contains: "invoice", "factura", "rechnung", "bill"
- Sender is known provider
- PDF attachment named with invoice patterns
