# Invoice Types

## 1. Factura Completa (Standard)

**When:** Default for B2B transactions.

**Requirements:**
- All fields from legal requirements
- Recipient tax ID mandatory
- Full address required

**Example:**
```
FACTURA F-2026-015
Fecha: 2026-02-13
...
```

---

## 2. Factura Simplificada (Ticket)

**When:**
- B2C transactions
- Amount ≤ 400€
- Recipient doesn't need VAT deduction

**Simplified fields:**
- Issuer data (full)
- Date and number
- Description
- Total with VAT included

**Can omit:**
- Recipient name/address/tax ID
- Separate VAT breakdown (can show "IVA incluido")

**Example:**
```
TICKET T-2026-089
Fecha: 2026-02-13
Cliente: [no requerido]

Servicio de diseño: 100€ (IVA inc.)
TOTAL: 100€
```

---

## 3. Factura Rectificativa (Credit Note)

**When:**
- Error in original invoice (amount, data, description)
- Full or partial return
- Discount applied after invoicing
- Cancellation of transaction

**Required fields:**
- Reference to original: "Rectifica factura F-2026-010 de fecha..."
- Reason for rectification
- Original amounts
- Corrected amounts
- Difference

**Two methods:**

### Method 1: By difference
Show only the difference (negative amounts).
```
Rectifica: F-2026-010 (2026-02-01)
Motivo: Error en cantidad

Base original: 500€
Base correcta: 400€
Diferencia: -100€

IVA 21%: -21€
TOTAL: -121€
```

### Method 2: By substitution
Show both original and corrected full invoice.

**Numbering:**
- Use separate series (R-2026-001) or same series
- Still correlative, no gaps

---

## 4. Proforma

**When:**
- Quote/estimate before agreement
- Budget for approval
- Import/export documentation

**NOT a tax document:**
- No legal value
- No correlative number required
- Can be modified freely

**Mark clearly:**
```
FACTURA PROFORMA
(Sin valor fiscal)
```

**Convert to invoice:**
When client approves, create real invoice copying data.

---

## 5. Factura Recurrente

**Structure:**
Same as standard invoice, but:
- Generated automatically on schedule
- Links to subscription definition
- May note: "Correspondiente a periodo: Febrero 2026"

---

## Decision Tree

```
Is recipient a business (B2B)?
├─ YES → Factura Completa
│        ├─ Error found → Factura Rectificativa
│        └─ Public entity → Facturae XML
│
└─ NO (B2C)
         ├─ Amount ≤ 400€ → Factura Simplificada
         └─ Amount > 400€ → Factura Completa
                            (can omit recipient tax ID if no VAT deduction needed)
```

---

## Series Recommendations

| Series | Use |
|--------|-----|
| F-YYYY | Standard invoices |
| T-YYYY | Simplified (tickets) |
| R-YYYY | Rectificativas |
| P-YYYY | Proformas (optional) |

Example: F-2026-001, F-2026-002, R-2026-001, F-2026-003...
